#!/usr/bin/env python3
"""serpwise page auditor: checks one URL against Google Search Central rules.

Stdlib only. Usage:
    python3 audit_page.py https://example.com/page [--json] [--timeout 20]
    python3 audit_page.py ./index.html [--base-url https://example.com/] [--json]
    python3 audit_page.py https://example.com/ --fail-on high    # exit 1 for CI

A local file is audited as if served with HTTP 200 at --base-url. robots.txt
is fetched from the live host only when --base-url is given; add --offline to
skip every network request.

It inspects raw HTML (no JavaScript rendering). For JS-heavy sites, confirm
with Search Console URL Inspection or the Rich Results Test.
"""

import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser

# Honest UA: a mobile browser string (Google indexes mobile-first) plus our own
# token. Never impersonate Googlebot; many sites block fake Googlebot requests.
UA = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0 Mobile Safari/537.36 "
    "(compatible; serpwise-audit/1.0; +https://github.com/sumitroajiprabowo/serpwise)"
)
HEAD_ALLOWED = {"title", "meta", "link", "script", "style", "base", "noscript", "template"}
GOOGLEBOT_HTML_LIMIT = 2 * 1024 * 1024
VAGUE_TITLES = {
    "home",
    "home page",
    "homepage",
    "untitled",
    "untitled document",
    "index",
    "page",
    "welcome",
    "new page",
}
VAGUE_ANCHORS = {"click here", "here", "read more", "more", "learn more", "this link", "link"}
SEVERITIES = ("critical", "high", "medium", "low")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop urllib from following redirects, so fetch() can record every hop."""

    def redirect_request(self, *a, **k):
        """Return None to hand the 3xx response back to the caller."""
        return None


def fetch(url, timeout, follow=True, max_hops=10):
    """Return dict(status, headers, body, final_url, chain, error)."""
    opener = urllib.request.build_opener(NoRedirect)
    chain = []
    current = url
    for _ in range(max_hops + 1):
        req = urllib.request.Request(
            current,
            headers={
                "User-Agent": UA,
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            },
        )
        try:
            resp = opener.open(req, timeout=timeout)
            status, headers, raw = resp.status, resp.headers, resp.read()
        except urllib.error.HTTPError as e:
            status, headers, raw = e.code, e.headers, e.read() if e.fp else b""
        except Exception as e:  # network / DNS / TLS
            return {
                "status": None,
                "headers": {},
                "body": b"",
                "final_url": current,
                "chain": chain,
                "error": f"{type(e).__name__}: {e}",
            }
        if status in (301, 302, 303, 307, 308) and follow:
            loc = headers.get("Location")
            chain.append((status, current))
            if not loc:
                break
            current = urllib.parse.urljoin(current, loc)
            continue
        enc = (headers.get("Content-Encoding") or "").lower()
        try:
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc == "deflate":
                raw = zlib.decompress(raw)
        except Exception:
            pass
        return {
            "status": status,
            "headers": headers,
            "body": raw,
            "final_url": current,
            "chain": chain,
            "error": None,
        }
    return {
        "status": None,
        "headers": {},
        "body": b"",
        "final_url": current,
        "chain": chain,
        "error": "Too many redirects (>10)",
    }


class PageParser(HTMLParser):
    """Collect the parts of a page that the audit checks, in one pass over the HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        # Where <head> ends, and what ended it.
        self.in_head = False
        self.head_closed_by = None
        self.head_done = False
        self.title = None
        self._in_title = False
        self.metas = []
        self.links = []
        self.html_lang = None
        self.h1 = []
        self._in_h1 = False
        self._h1_buf = ""
        self.imgs = []
        self.anchors = []
        self._in_a = None
        self.jsonld = []
        self._in_jsonld = False
        self._jsonld_buf = ""
        self.meta_after_invalid = []
        self._raw_depth = 0  # inside <noscript>/<template> in <head>: treated as text by Google

    def handle_starttag(self, tag, attrs):
        """Record metadata, links, images and JSON-LD, and notice where <head> ends."""
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
            self.head_done = True
        in_raw = self._raw_depth > 0
        if self.in_head and not self.head_done and tag in ("noscript", "template"):
            self._raw_depth += 1
        # Google stops reading <head> at the first element that doesn't belong there.
        if (
            self.in_head
            and not self.head_done
            and not in_raw
            and tag not in HEAD_ALLOWED
            and tag not in ("head", "html")
            and self.head_closed_by is None
        ):
            self.head_closed_by = tag
        if tag == "title" and self.title is None:
            self._in_title = True
            self.title = ""
        elif tag == "meta":
            self.metas.append(a)
            if self.head_closed_by and not self.head_done:
                self.meta_after_invalid.append(a)
        elif tag == "link":
            self.links.append(a)
            if self.head_closed_by and not self.head_done:
                self.meta_after_invalid.append(a)
        elif tag == "h1":
            self._in_h1 = True
            self._h1_buf = ""
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a":
            self._in_a = {"attrs": a, "text": ""}
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = ""

    def handle_endtag(self, tag):
        """Close whatever element was being collected."""
        if tag in ("noscript", "template") and self._raw_depth:
            self._raw_depth -= 1
        if tag == "title":
            self._in_title = False
        elif tag == "head":
            self.in_head = False
            self.head_done = True
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            self.h1.append(self._h1_buf.strip())
        elif tag == "a" and self._in_a is not None:
            self.anchors.append(self._in_a)
            self._in_a = None
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append(self._jsonld_buf)

    def handle_data(self, data):
        """Append text to the element currently being collected."""
        if self._in_title:
            self.title += data
        if self._in_h1:
            self._h1_buf += data
        if self._in_a is not None:
            self._in_a["text"] += data
        if self._in_jsonld:
            self._jsonld_buf += data


def _normalize(url):
    """Compare URLs without the fragment or a trailing slash."""
    return url.split("#")[0].rstrip("/")


def meta_content(metas, name):
    """Return the content of the first <meta> whose name or property is `name`."""
    for m in metas:
        if m.get("name", "").lower() == name or m.get("property", "").lower() == name:
            return m.get("content")
    return None


def jsonld_types(obj, out):
    """Append every @type found anywhere in a parsed JSON-LD value to `out`."""
    if isinstance(obj, dict):
        t = obj.get("@type")
        if t:
            out.extend(t if isinstance(t, list) else [t])
        for v in obj.values():
            jsonld_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            jsonld_types(v, out)


def robots_check(page_url, timeout):
    """Fetch the host's robots.txt and decide whether Googlebot may crawl page_url.

    Follows Google's rules: the most specific user-agent group wins, the longest
    matching rule wins, and Allow wins a tie. Non-200 responses aren't parsed."""
    p = urllib.parse.urlsplit(page_url)
    robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
    r = fetch(robots_url, timeout)
    info = {
        "url": robots_url,
        "status": r["status"],
        "error": r["error"],
        "sitemaps": [],
        "googlebot_blocked": None,
        "matched_rule": None,
        "unsupported": [],
    }
    if r["status"] != 200:
        return info
    text = r["body"].decode("utf-8", "replace")
    groups, cur, last_was_ua = [], None, False
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, val = [x.strip() for x in line.split(":", 1)]
        field = field.lower()
        if field == "sitemap":
            info["sitemaps"].append(val)
            continue
        if field == "user-agent":
            if not last_was_ua or cur is None:
                cur = {"agents": [], "rules": []}
                groups.append(cur)
            cur["agents"].append(val.lower())
            last_was_ua = True
            continue
        last_was_ua = False
        if field in ("allow", "disallow") and cur is not None:
            cur["rules"].append((field, val))
        elif field in ("crawl-delay", "noindex", "host"):
            info["unsupported"].append(field)

    def pick(agent):
        """Return the rules from the group(s) that apply to `agent`, else from `*`."""
        best, best_len = [], -1
        for g in groups:
            for a in g["agents"]:
                if a != "*" and agent.startswith(a) and len(a) > best_len:
                    best, best_len = [g], len(a)
                elif a != "*" and agent.startswith(a) and len(a) == best_len:
                    best.append(g)
        if best:
            return [r for g in best for r in g["rules"]]
        return [r for g in groups if "*" in g["agents"] for r in g["rules"]]

    def to_re(path):
        """Turn a robots.txt path pattern (`*` and a trailing `$`) into a regex."""
        anchored = path.endswith("$")
        core = path[:-1] if anchored else path
        rx = "".join(".*" if c == "*" else re.escape(c) for c in core)
        return re.compile("^" + rx + ("$" if anchored else ""))

    path = p.path or "/"
    if p.query:
        path += "?" + p.query
    rules = pick("googlebot")
    match = None
    for kind, val in rules:
        if not val:
            continue
        if to_re(val).match(path):
            ln = len(val)
            if match is None or ln > match[2] or (ln == match[2] and kind == "allow"):
                match = (kind, val, ln)
    info["googlebot_blocked"] = bool(match and match[0] == "disallow")
    info["matched_rule"] = f"{match[0]}: {match[1]}" if match else None
    return info


def audit(url, timeout=20, local_html=None, offline=False):
    """Audit one page and return a dict of page data plus a sorted `findings` list.

    With `local_html`, the bytes are audited as if served at `url` with HTTP 200.
    With `offline`, nothing is fetched, not even robots.txt."""
    findings = []

    def add(severity, area, msg, fix=""):
        """Record one finding."""
        findings.append({"severity": severity, "area": area, "issue": msg, "fix": fix})

    # Fetch the page, or wrap a local file in a fake 200 response.
    if local_html is not None:
        from email.message import Message

        hdrs = Message()
        hdrs["Content-Type"] = "text/html; charset=utf-8"
        r = {"status": 200, "headers": hdrs, "body": local_html, "final_url": url, "chain": [], "error": None}
    else:
        r = fetch(url, timeout)
    data = {
        "url": url,
        "final_url": r["final_url"],
        "status": r["status"],
        "redirect_chain": [f"{s} {u}" for s, u in r["chain"]],
    }
    if r["error"]:
        add(
            "critical",
            "crawl",
            f"Fetch failed: {r['error']}",
            "Make the server reachable (DNS, TLS, firewall must allow Googlebot).",
        )
        data["findings"] = findings
        return data
    # HTTP status, redirects and HTTPS.
    st = r["status"]
    if st >= 500:
        add(
            "critical",
            "crawl",
            f"HTTP {st} server error",
            "Fix the server; persistent 5xx drops URLs from the index.",
        )
    elif st >= 400:
        add(
            "critical",
            "crawl",
            f"HTTP {st}",
            "4xx means 'does not exist' to Google. Return 200 for real content, or redirect.",
        )
    if len(r["chain"]) > 0:
        temp = [s for s, _ in r["chain"] if s in (302, 303, 307)]
        if len(r["chain"]) >= 3:
            add(
                "high",
                "crawl",
                f"Redirect chain of {len(r['chain'])} hops",
                "Redirect directly to the final URL.",
            )
        if temp:
            add(
                "medium",
                "crawl",
                "Temporary redirect (302/303/307) in chain",
                "Use 301/308 if the move is permanent.",
            )
    if r["chain"] and r["chain"][0][1].startswith("http://") and not r["final_url"].startswith("https://"):
        add("high", "security", "Not served over HTTPS", "Serve HTTPS and redirect HTTP to HTTPS.")
    elif r["final_url"].startswith("http://"):
        add("high", "security", "Final URL is HTTP, not HTTPS", "Serve HTTPS and redirect HTTP to HTTPS.")

    # Response headers and Googlebot's HTML size limit.
    headers = r["headers"]
    xrt = ", ".join(headers.get_all("X-Robots-Tag") or []) if hasattr(headers, "get_all") else ""
    data["x_robots_tag"] = xrt or None
    if re.search(r"\b(noindex|none)\b", xrt, re.I):
        add(
            "critical",
            "indexing",
            f"X-Robots-Tag header blocks indexing: '{xrt}'",
            "Remove noindex from the header if the page should rank.",
        )
    ctype = headers.get("Content-Type", "")
    data["content_type"] = ctype
    body = r["body"]
    data["html_bytes"] = len(body)
    if len(body) > GOOGLEBOT_HTML_LIMIT:
        add(
            "high",
            "crawl",
            f"HTML is {len(body) // 1024} KB, over Googlebot's 2MB fetch limit",
            "Shrink the HTML; content past 2MB is ignored.",
        )

    # Decode with the declared charset, falling back to UTF-8, then parse.
    charset = "utf-8"
    m = re.search(r"charset=([\w-]+)", ctype, re.I)
    if m:
        charset = m.group(1)
    try:
        html = body.decode(charset, "replace")
    except LookupError:
        html = body.decode("utf-8", "replace")
    pp = PageParser()
    try:
        pp.feed(html)
    except Exception as e:
        add("medium", "html", f"HTML parse problem: {e}")

    # Title. Google sets no length limit, so only vague titles are flagged.
    title = (pp.title or "").strip()
    data["title"] = title
    if not title:
        add("high", "appearance", "Missing <title>", "Add a unique, descriptive title.")
    else:
        if title.lower() in VAGUE_TITLES:
            add(
                "high",
                "appearance",
                f"Title too vague: '{title}'",
                "Describe the page specifically; brand at start/end.",
            )
        elif len(title.split()) < 2:
            add(
                "medium",
                "appearance",
                f"Title is a single word: '{title}'",
                "Check it describes this page, not just the site.",
            )

    # Meta description.
    desc = meta_content(pp.metas, "description")
    data["meta_description"] = desc
    if not desc:
        add(
            "medium",
            "appearance",
            "Missing meta description",
            "Write a unique 1-2 sentence summary with concrete facts.",
        )
    elif len(desc.split()) < 6:
        add(
            "medium",
            "appearance",
            f"Meta description is very thin: '{desc}'",
            "Summarize this page with concrete, page-specific facts.",
        )

    # Robots and googlebot meta tags, meta keywords, SafeSearch rating.
    robots_meta = " ".join(
        filter(None, [meta_content(pp.metas, "robots"), meta_content(pp.metas, "googlebot")])
    )
    data["robots_meta"] = robots_meta or None
    if re.search(r"\b(noindex|none)\b", robots_meta, re.I):
        add(
            "critical",
            "indexing",
            f"Robots meta blocks indexing: '{robots_meta}'",
            "Remove noindex if the page should appear in Google.",
        )
    if re.search(r"\bnosnippet\b", robots_meta, re.I):
        add(
            "medium",
            "appearance",
            "nosnippet set: no snippet and no direct use in AI Overviews",
            "Remove it unless intentional.",
        )
    if re.search(r"\bnofollow\b", robots_meta, re.I):
        add("medium", "crawl", "Page-level nofollow: links on this page won't be followed")
    if meta_content(pp.metas, "keywords"):
        add(
            "low",
            "myth",
            "meta keywords present (Google ignores it)",
            "Harmless, but don't spend effort on it.",
        )
    if (meta_content(pp.metas, "rating") or "").lower() in ("adult", "rta-5042-1996-1400-1577-rta"):
        add(
            "high",
            "safesearch",
            "Adult rating meta: page will be filtered by SafeSearch",
            "Keep only on genuinely explicit pages.",
        )

    # Canonical. Comparisons only make sense when the page has a real http(s) URL.
    canon = [link.get("href") for link in pp.links if "canonical" in link.get("rel", "").lower().split()]
    data["canonical"] = canon
    final = r["final_url"]
    if not canon:
        add("medium", "indexing", "No rel=canonical", "Add a self-referencing absolute canonical.")
    elif len(canon) > 1:
        add("high", "indexing", f"{len(canon)} canonical tags", "Keep exactly one.")
    else:
        c = urllib.parse.urljoin(final, canon[0])
        if not canon[0].startswith("http"):
            add("low", "indexing", "Canonical is relative", "Use an absolute URL.")
        if final.startswith("http") and _normalize(c) != _normalize(final):
            add(
                "high",
                "indexing",
                f"Canonical points elsewhere: {c}",
                "Fine if this page is a duplicate; otherwise make it self-referencing.",
            )

    # Mobile viewport, html lang and headings.
    vp = meta_content(pp.metas, "viewport")
    data["viewport"] = vp
    if not vp:
        add(
            "high",
            "mobile",
            "No viewport meta (likely not mobile-friendly)",
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
        )

    data["html_lang"] = pp.html_lang
    h1s = [h for h in pp.h1 if h]
    data["h1"] = h1s
    if not h1s:
        add("medium", "content", "No <h1> (in raw HTML)", "Give the page one clear, prominent main heading.")
    elif len(h1s) > 1:
        add(
            "low",
            "content",
            f"{len(h1s)} <h1> elements",
            "Fine for Google; ensure the main title is the most prominent.",
        )

    # An invalid element in <head> makes Google ignore the metadata after it.
    if pp.head_closed_by:
        msg = f"Invalid element <{pp.head_closed_by}> inside <head> ends the head for Google"
        if pp.meta_after_invalid:
            add(
                "critical",
                "html",
                msg
                + f"; {len(pp.meta_after_invalid)} meta/link tags after it are ignored (robots, canonical, hreflang included)",
                "Move it to <body> or after all metadata.",
            )
        else:
            add("low", "html", msg, "Move it to <body>.")

    # hreflang: valid codes, absolute URLs, a self-reference and x-default.
    hreflangs = [
        (link.get("hreflang"), link.get("href"))
        for link in pp.links
        if "alternate" in link.get("rel", "").lower() and link.get("hreflang")
    ]
    data["hreflang"] = hreflangs
    if hreflangs:
        codes = [h for h, _ in hreflangs]
        bad = [
            h
            for h in codes
            if h.lower() != "x-default" and not re.fullmatch(r"[a-z]{2,3}(-[A-Za-z]{4})?(-[A-Za-z]{2})?", h)
        ]
        bad += [
            h
            for h in codes
            if h.lower().endswith("-uk") or h.lower() in ("uk", "eu") or h.lower().endswith("-eu")
        ]
        if bad:
            add(
                "high",
                "international",
                f"Suspicious hreflang codes: {sorted(set(bad))}",
                "Language first (ISO 639-1), region ISO 3166-1 alpha-2 (GB not UK; es-419 unsupported).",
            )
        rel = [u for _, u in hreflangs if u and not u.startswith("http")]
        if rel:
            add("high", "international", "Relative hreflang URLs", "Use fully-qualified absolute URLs.")
        if final.startswith("http") and not any(
            urllib.parse.urljoin(final, u or "").rstrip("/") == final.rstrip("/") for _, u in hreflangs
        ):
            add(
                "high",
                "international",
                "hreflang set doesn't include this page itself",
                "Each version must list itself and all others.",
            )
        if "x-default" not in [c.lower() for c in codes]:
            add(
                "low",
                "international",
                "No x-default hreflang",
                "Add x-default pointing to a selector or default page.",
            )

    # Images: alt text, a crawlable src, and CSS background images.
    imgs = pp.imgs
    no_alt = [i.get("src") or i.get("data-src") for i in imgs if "alt" not in i]
    no_src = [i for i in imgs if not i.get("src") and not i.get("srcset")]
    data["images"] = {"total": len(imgs), "missing_alt": len(no_alt), "missing_src": len(no_src)}
    if imgs and no_alt:
        add(
            "medium",
            "images",
            f"{len(no_alt)}/{len(imgs)} images missing alt attribute (e.g. {no_alt[:3]})",
            "Describe each meaningful image in context.",
        )
    if no_src:
        add(
            "medium",
            "images",
            f"{len(no_src)} <img> without src/srcset in raw HTML (JS lazy-load?)",
            'Ensure src appears in rendered HTML; prefer loading="lazy".',
        )

    bg = re.findall(r"background(?:-image)?\s*:\s*url\(", html, re.I)
    if bg:
        add(
            "low",
            "images",
            f"{len(bg)} inline CSS background image(s)",
            "CSS background images aren't indexed; use <img src> with alt for meaningful images.",
        )

    # Links: Google only follows <a href>. Also check anchor text and internal links.
    bad_links = [
        a
        for a in pp.anchors
        if a["attrs"].get("href", "").strip().lower().startswith("javascript:")
        or (
            not a["attrs"].get("href")
            and (a["attrs"].get("onclick") or a["attrs"].get("routerlink") or a["attrs"].get("ng-click"))
        )
    ]
    placeholder = [a for a in pp.anchors if not a["attrs"].get("href") and a not in bad_links]
    empty_anchor = [
        a
        for a in pp.anchors
        if a["attrs"].get("href")
        and not a["text"].strip()
        and not a["attrs"].get("aria-label")
        and not a["attrs"].get("title")
    ]
    host = urllib.parse.urlsplit(final).netloc
    internal = [
        a
        for a in pp.anchors
        if a["attrs"].get("href")
        and urllib.parse.urlsplit(urllib.parse.urljoin(final, a["attrs"]["href"])).netloc == host
    ]
    vague = [a for a in pp.anchors if a["text"].strip().lower() in VAGUE_ANCHORS]
    data["links"] = {
        "total": len(pp.anchors),
        "internal": len(internal),
        "uncrawlable": len(bad_links),
        "empty_text": len(empty_anchor),
        "vague_text": len(vague),
    }
    data["links"]["no_href_placeholders"] = len(placeholder)
    if bad_links:
        add(
            "high",
            "links",
            f"{len(bad_links)} link(s) navigate via JS (onclick/routerLink/javascript:) without a real href",
            'Use <a href="/real-url">; Google only follows href.',
        )
    if placeholder:
        add(
            "low",
            "links",
            f"{len(placeholder)} <a> elements without href (not crawlable)",
            "Fine if they are not navigation; otherwise add href.",
        )
    if pp.anchors and not internal:
        add(
            "high",
            "links",
            "No internal links found in raw HTML",
            "Link to related pages with <a href>. JS-only nav may hide links.",
        )
    if vague:
        add(
            "low",
            "links",
            f"{len(vague)} vague anchors (e.g. 'click here', 'read more')",
            "Use descriptive anchor text.",
        )
    if empty_anchor:
        add(
            "low",
            "links",
            f"{len(empty_anchor)} links with no anchor text (icons/images without alt?)",
            "Add alt text on linked images or aria-label.",
        )

    # JSON-LD: every block must parse, and the page should have some.
    types, errors = [], []
    for block in pp.jsonld:
        try:
            jsonld_types(json.loads(block), types)
        except Exception as e:
            errors.append(str(e)[:80])
    data["jsonld_types"] = sorted(set(types))
    if errors:
        add(
            "high",
            "structured-data",
            f"{len(errors)} JSON-LD block(s) fail to parse: {errors[:2]}",
            "Fix the JSON (no comments, trailing commas).",
        )
    if not types and not errors:
        add(
            "medium",
            "structured-data",
            "No JSON-LD structured data in raw HTML",
            "Add types that fit the page (Organization/WebSite on home, Article, Product, BreadcrumbList...).",
        )

    # Discover and social: og:image, max-image-preview, favicon.
    og = meta_content(pp.metas, "og:image")
    data["og_image"] = og
    if not og:
        add(
            "low",
            "appearance",
            "No og:image",
            "Set a large (>=1200px wide) representative image for Discover/social.",
        )
    mip = re.search(r"max-image-preview:(\w+)", robots_meta or "")
    if not mip or mip.group(1) != "large":
        add(
            "low",
            "appearance",
            "max-image-preview:large not set",
            "Add to robots meta to allow large images in Discover.",
        )

    icons = [link for link in pp.links if "icon" in link.get("rel", "").lower()]
    if urllib.parse.urlsplit(final).path in ("", "/") and not icons:
        add("medium", "appearance", "No <link rel=icon> on home page", "Add a square favicon >=48x48.")

    # robots.txt, fetched from the live host unless offline.
    rb = (
        robots_check(final, timeout)
        if final.startswith("http") and not offline
        else {
            "status": None,
            "sitemaps": [],
            "googlebot_blocked": None,
            "matched_rule": None,
            "unsupported": [],
        }
    )
    data["robots_txt"] = rb
    if rb["status"] and rb["status"] >= 500:
        add(
            "critical",
            "crawl",
            f"robots.txt returns {rb['status']}: Google stops crawling",
            "Serve robots.txt with 200 (or 404).",
        )
    if rb["googlebot_blocked"]:
        add(
            "critical",
            "crawl",
            f"robots.txt blocks Googlebot for this URL ({rb['matched_rule']})",
            "Allow crawling; robots.txt is not a way to deindex.",
        )
    if rb.get("status") is None and not final.startswith("http") or offline:
        data["robots_txt_note"] = "robots.txt not checked (offline/local file)"
    if rb["status"] == 200 and not rb["sitemaps"]:
        add("low", "crawl", "No Sitemap: line in robots.txt", "Add 'Sitemap: https://.../sitemap.xml'.")
    if rb["unsupported"]:
        add(
            "low",
            "myth",
            f"Unsupported robots.txt fields: {sorted(set(rb['unsupported']))}",
            "Google ignores crawl-delay/noindex/host.",
        )

    # Very little text in the raw HTML usually means thin or client-rendered content.
    text_len = len(
        re.sub(
            r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", html))
        ).strip()
    )
    data["visible_text_chars"] = text_len
    if text_len < 300 and st == 200:
        add(
            "high",
            "content",
            f"Only ~{text_len} chars of text in raw HTML (thin or client-rendered)",
            "Check rendered HTML in URL Inspection; consider SSR.",
        )

    findings.sort(key=lambda f: SEVERITIES.index(f["severity"]))
    data["findings"] = findings
    return data


def print_report(d):
    """Print the audit result as a plain-text report."""
    print(f"# serpwise audit: {d['url']}")
    print(f"Final URL: {d.get('final_url')}  |  HTTP {d.get('status')}")
    if d.get("redirect_chain"):
        print("Redirects: " + " -> ".join(d["redirect_chain"]))
    for k in (
        "title",
        "meta_description",
        "canonical",
        "robots_meta",
        "x_robots_tag",
        "viewport",
        "html_lang",
        "h1",
        "hreflang",
        "jsonld_types",
        "og_image",
        "images",
        "links",
        "html_bytes",
        "visible_text_chars",
    ):
        if k in d:
            print(f"- {k}: {d[k]}")
    rb = d.get("robots_txt")
    if rb:
        print(
            f"- robots.txt: HTTP {rb['status']}, googlebot_blocked={rb['googlebot_blocked']}, "
            f"rule={rb['matched_rule']}, sitemaps={rb['sitemaps']}"
        )
    print("\n## Findings")
    if not d["findings"]:
        print("No mechanical issues found. Now review content quality and intent manually.")
    for f in d["findings"]:
        fix = f" → {f['fix']}" if f["fix"] else ""
        print(f"[{f['severity'].upper()}] ({f['area']}) {f['issue']}{fix}")
    print("\nNote: raw HTML only; JS-rendered content is not executed.")


def main():
    """Parse the command line, run the audit and set the exit status."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--base-url", help="URL the local HTML file is served at")
    ap.add_argument(
        "--offline", action="store_true", help="local file mode: don't fetch robots.txt or anything else"
    )
    ap.add_argument(
        "--fail-on",
        choices=SEVERITIES,
        metavar="SEVERITY",
        help="exit with status 1 if any finding is at this severity or worse (for CI)",
    )
    a = ap.parse_args()
    import os

    if os.path.isfile(a.url):
        with open(a.url, "rb") as fh:
            body = fh.read()
        base = a.base_url or ("file://" + os.path.abspath(a.url))
        d = audit(base, a.timeout, local_html=body, offline=a.offline)
        d["source_file"] = a.url
    else:
        url = a.url if re.match(r"https?://", a.url) else "https://" + a.url
        d = audit(url, a.timeout)
    if a.json:
        print(json.dumps(d, indent=2, ensure_ascii=False, default=str))
    else:
        print_report(d)
    sys.exit(1 if failed(d["findings"], a.fail_on) else 0)


def failed(findings, threshold):
    """Return True if any finding is at `threshold` severity or worse."""
    if not threshold:
        return False
    limit = SEVERITIES.index(threshold)
    return any(SEVERITIES.index(f["severity"]) <= limit for f in findings)


if __name__ == "__main__":
    main()
