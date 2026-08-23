"""Unit tests for skills/serpwise/scripts/audit_page.py (stdlib only, no network).

Run: python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from email.message import Message
from unittest import mock

sys.dont_write_bytecode = True  # keep __pycache__ out of the shipped skill folder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "serpwise", "scripts"))
import audit_page  # noqa: E402

FIXTURE = os.path.join(
    ROOT, "skills", "serpwise", "evals", "audit-broken-landing-page", "files", "index.html"
)


def fake_response(status=200, body=b"", url="https://example.com/robots.txt"):
    """Build a fetch() result without touching the network."""
    hdrs = Message()
    hdrs["Content-Type"] = "text/plain"
    return {"status": status, "headers": hdrs, "body": body, "final_url": url, "chain": [], "error": None}


def robots(txt, page="https://example.com/", status=200):
    """Run robots_check() against the given robots.txt text."""
    with mock.patch.object(audit_page, "fetch", return_value=fake_response(status, txt.encode())):
        return audit_page.robots_check(page, timeout=1)


GOOD_HEAD = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    "<title>Aero 2 Running Shoe: Light and Cushioned | Stride Supply</title>"
    '<meta name="description" content="The Aero 2 running shoe has a cushioned midsole, weighs 7.4 oz, '
    'and ships free with 30-day returns from Stride Supply.">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<link rel="canonical" href="https://example.com/product/aero-2">'
    '<meta name="robots" content="max-image-preview:large">'
    '<meta property="og:image" content="https://example.com/a.jpg">'
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"Aero 2"}</script>'
    "</head>"
)


def page(body="", head=GOOD_HEAD):
    """Build a page that passes every check, with `body` appended and `head` swappable."""
    filler = "<p>" + ("A comfortable running shoe for daily training. " * 12) + "</p>"
    return (
        head
        + "<body><h1>Aero 2 Running Shoe</h1>"
        + filler
        + '<a href="/category/running-shoes">All running shoes</a>'
        + body
        + "</body></html>"
    ).encode()


def run(html, url="https://example.com/product/aero-2"):
    """Audit HTML bytes offline as if served at `url`."""
    return audit_page.audit(url, local_html=html, offline=True)


def issues(d, prio=None):
    """List finding messages, optionally only those at one severity."""
    return [f["issue"] for f in d["findings"] if prio is None or f["severity"] == prio]


def has(d, needle, prio=None):
    """True if any finding (at `prio`, if given) contains `needle`."""
    return any(needle.lower() in i.lower() for i in issues(d, prio))


class RobotsTxtTests(unittest.TestCase):
    """robots.txt parsing and matching, following Google's rules."""

    def test_disallow_blocks(self):
        r = robots("User-agent: *\nDisallow: /private/", "https://example.com/private/x")
        self.assertTrue(r["googlebot_blocked"])
        self.assertEqual(r["matched_rule"], "disallow: /private/")

    def test_longest_match_wins(self):
        txt = "User-agent: *\nDisallow: /shop/\nAllow: /shop/public/"
        self.assertFalse(robots(txt, "https://example.com/shop/public/a")["googlebot_blocked"])
        self.assertTrue(robots(txt, "https://example.com/shop/secret")["googlebot_blocked"])

    def test_allow_wins_tie(self):
        txt = "User-agent: *\nDisallow: /page\nAllow: /page"
        self.assertFalse(robots(txt, "https://example.com/page")["googlebot_blocked"])

    def test_googlebot_group_overrides_star(self):
        txt = "User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /"
        self.assertFalse(robots(txt)["googlebot_blocked"])

    def test_other_bot_group_ignored(self):
        txt = "User-agent: Bingbot\nDisallow: /\n\nUser-agent: *\nAllow: /"
        self.assertFalse(robots(txt)["googlebot_blocked"])

    def test_googlebot_news_group_not_used_for_googlebot(self):
        txt = "User-agent: Googlebot-News\nDisallow: /\n"
        self.assertFalse(robots(txt)["googlebot_blocked"])

    def test_grouped_user_agents(self):
        txt = "User-agent: Bingbot\nUser-agent: Googlebot\nDisallow: /x"
        self.assertTrue(robots(txt, "https://example.com/x/1")["googlebot_blocked"])

    def test_wildcards(self):
        txt = "User-agent: *\nDisallow: /*.pdf$\nDisallow: /*?sort="
        self.assertTrue(robots(txt, "https://example.com/doc/a.pdf")["googlebot_blocked"])
        self.assertFalse(robots(txt, "https://example.com/doc/a.pdf.html")["googlebot_blocked"])
        self.assertTrue(robots(txt, "https://example.com/c?sort=price")["googlebot_blocked"])

    def test_empty_disallow_allows_all(self):
        self.assertFalse(robots("User-agent: *\nDisallow:")["googlebot_blocked"])

    def test_sitemaps_comments_and_unsupported(self):
        txt = (
            "# comment\nUser-agent: *\nCrawl-delay: 10\nNoindex: /a\nDisallow: /tmp # trailing\n"
            "Sitemap: https://example.com/sitemap.xml\n"
        )
        r = robots(txt, "https://example.com/tmp/1")
        self.assertEqual(r["sitemaps"], ["https://example.com/sitemap.xml"])
        self.assertEqual(sorted(r["unsupported"]), ["crawl-delay", "noindex"])
        self.assertTrue(r["googlebot_blocked"])

    def test_non_200_not_parsed(self):
        r = robots("User-agent: *\nDisallow: /", status=404)
        self.assertIsNone(r["googlebot_blocked"])


class PageAuditTests(unittest.TestCase):
    """Checks on the page itself: head, metadata, links, images, JSON-LD."""

    def test_clean_page_has_no_critical_or_high(self):
        d = run(page())
        self.assertEqual(issues(d, "critical") + issues(d, "high"), [], d["findings"])

    def test_findings_sorted_by_priority(self):
        d = run(page(head="<html><head><meta name='robots' content='noindex'></head>"))
        order = ["critical", "high", "medium", "low"]
        ranks = [order.index(f["severity"]) for f in d["findings"]]
        self.assertEqual(ranks, sorted(ranks))

    def test_noindex_is_critical(self):
        head = GOOD_HEAD.replace("max-image-preview:large", "noindex, nofollow")
        self.assertTrue(has(run(page(head=head)), "noindex", "critical"))

    def test_missing_title_and_viewport(self):
        d = run(page(head="<html><head></head>"))
        self.assertTrue(has(d, "Missing <title>", "high"))
        self.assertTrue(has(d, "viewport", "high"))

    def test_canonical_elsewhere_and_multiple(self):
        head = GOOD_HEAD.replace("/product/aero-2", "/product/lain")
        self.assertTrue(has(run(page(head=head)), "Canonical points elsewhere", "high"))
        head2 = GOOD_HEAD.replace("</head>", '<link rel="canonical" href="https://example.com/b"></head>')
        self.assertTrue(has(run(page(head=head2)), "canonical tags", "high"))

    def test_hreflang_codes(self):
        links = '<link rel="alternate" hreflang="{}" href="https://example.com/{}/">'
        head = GOOD_HEAD.replace(
            "</head>", "".join(links.format(c, c) for c in ("en-uk", "es-419", "id")) + "</head>"
        )
        d = run(page(head=head))
        msg = " ".join(issues(d, "high"))
        self.assertIn("en-uk", msg)
        self.assertIn("es-419", msg)
        self.assertNotIn("'id'", msg)

    def test_valid_hreflang_not_flagged(self):
        links = '<link rel="alternate" hreflang="{}" href="https://example.com/product/aero-2">'
        head = GOOD_HEAD.replace(
            "</head>",
            "".join(links.format(c) for c in ("id-ID", "en-GB", "zh-Hant-TW", "x-default")) + "</head>",
        )
        self.assertFalse(has(run(page(head=head)), "Suspicious hreflang"))

    def test_js_links_vs_placeholders(self):
        d = run(page(body='<a onclick="go(\'/x\')">Go to X</a><a href="javascript:void(0)">Y</a>'))
        self.assertTrue(has(d, "navigate via JS", "high"))
        d2 = run(page(body="<a name='top'>top</a>"))
        self.assertFalse(has(d2, "navigate via JS"))
        self.assertTrue(has(d2, "without href", "low"))

    def test_invalid_jsonld(self):
        head = GOOD_HEAD.replace('{"@context"', '{ // comment\n"@context"')
        self.assertTrue(has(run(page(head=head)), "fail to parse", "high"))

    def test_jsonld_types_extracted(self):
        self.assertIn("Product", run(page())["jsonld_types"])

    def test_img_in_head_ignores_following_meta(self):
        head = GOOD_HEAD.replace("<title>", '<img src="/px.gif"><title>')
        self.assertTrue(has(run(page(head=head)), "ignored", "critical"))

    def test_images_without_alt(self):
        self.assertTrue(has(run(page(body='<img src="/a.jpg">')), "missing alt", "medium"))

    def test_meta_keywords_is_myth(self):
        head = GOOD_HEAD.replace("</head>", '<meta name="keywords" content="shoes">' + "</head>")
        self.assertTrue(has(run(page(head=head)), "meta keywords", "low"))

    def test_thin_content(self):
        html = (GOOD_HEAD + "<body><h1>Hi</h1><a href='/a'>A</a></body></html>").encode()
        self.assertTrue(has(run(html), "chars of text", "high"))

    def test_http_url_flagged(self):
        self.assertTrue(has(run(page(), url="http://example.com/product/aero-2"), "HTTPS", "high"))

    def test_noscript_pixel_in_head_is_not_invalid(self):
        head = GOOD_HEAD.replace("<title>", '<noscript><img src="https://px.test/tr?id=1"></noscript><title>')
        self.assertFalse(has(run(page(head=head)), "Invalid element"))

    def test_no_fixed_length_rules(self):
        long_title = (
            "Aero 2 Running Shoe: Light, Cushioned and Built for Daily Training Miles | Stride Supply"
        )
        head = GOOD_HEAD.replace("Aero 2 Running Shoe: Light and Cushioned | Stride Supply", long_title)
        d = run(page(head=head))
        self.assertFalse(any("chars" in i for i in issues(d)), issues(d))

    def test_local_file_without_base_url_skips_url_comparisons(self):
        d = audit_page.audit("file:///tmp/index.html", local_html=page(), offline=True)
        self.assertFalse(has(d, "Canonical points elsewhere"))

    def test_unknown_charset_does_not_crash(self):
        hdrs = Message()
        hdrs["Content-Type"] = "text/html; charset=bogus-charset"
        resp = {
            "status": 200,
            "headers": hdrs,
            "body": page(),
            "final_url": "https://example.com/product/aero-2",
            "chain": [],
            "error": None,
        }
        with mock.patch.object(audit_page, "fetch", return_value=resp), mock.patch.object(
            audit_page,
            "robots_check",
            return_value={
                "status": 404,
                "sitemaps": [],
                "googlebot_blocked": None,
                "matched_rule": None,
                "unsupported": [],
            },
        ):
            d = audit_page.audit("https://example.com/product/aero-2", timeout=1)
        self.assertEqual(d["title"], "Aero 2 Running Shoe: Light and Cushioned | Stride Supply")

    def test_fail_on_threshold(self):
        f = [{"severity": "medium"}]
        self.assertFalse(audit_page.failed(f, None))
        self.assertFalse(audit_page.failed(f, "high"))
        self.assertTrue(audit_page.failed(f, "medium"))
        self.assertTrue(audit_page.failed(f, "low"))

    def test_offline_never_touches_network(self):
        with mock.patch.object(audit_page, "fetch", side_effect=AssertionError("network used")):
            run(page())

    def test_eval_fixture_catches_planted_bugs(self):
        with open(FIXTURE, "rb") as fh:
            d = audit_page.audit("https://example.com/", local_html=fh.read(), offline=True)
        for needle in ("noindex", "hreflang", "fail to parse", "navigate via JS", "meta keywords"):
            self.assertTrue(has(d, needle), f"fixture: expected finding containing {needle!r}")


class FetchTests(unittest.TestCase):
    """Behaviour when the server returns an error."""

    def test_http_errors_reported(self):
        d404 = {
            "status": 404,
            "headers": Message(),
            "body": b"",
            "final_url": "https://example.com/x",
            "chain": [],
            "error": None,
        }
        with mock.patch.object(audit_page, "fetch", return_value=d404):
            d = audit_page.audit("https://example.com/x", timeout=1)
        self.assertTrue(has(d, "HTTP 404", "critical"))


if __name__ == "__main__":
    unittest.main()
