"""Unit tests for skills/serpwise/scripts/audit_page.py (stdlib only, no network).

Run: python3 -m unittest discover -s tests -v
"""

import gzip
import json
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
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"Aero 2","offers":{"@type":"Offer","price":"120","priceCurrency":"USD"}}</script>'
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

    def test_arbitrary_prefix_ua_does_not_match_googlebot(self):
        txt = "User-agent: g\nDisallow: /\n\nUser-agent: *\nAllow: /"
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
        head = GOOD_HEAD.replace("/product/aero-2", "/product/other")
        self.assertTrue(has(run(page(head=head)), "Canonical points elsewhere", "high"))
        head2 = GOOD_HEAD.replace("</head>", '<link rel="canonical" href="https://example.com/b"></head>')
        self.assertTrue(has(run(page(head=head2)), "canonical tags", "high"))

    def test_canonical_missing_or_empty_href(self):
        head = GOOD_HEAD.replace(
            '<link rel="canonical" href="https://example.com/product/aero-2">', '<link rel="canonical">'
        )
        self.assertTrue(has(run(page(head=head)), "Empty or missing href on rel=canonical", "high"))
        head2 = GOOD_HEAD.replace('href="https://example.com/product/aero-2"', 'href=""')
        self.assertTrue(has(run(page(head=head2)), "Empty or missing href on rel=canonical", "high"))

    def test_multiple_robots_meta_tags_combined(self):
        head = GOOD_HEAD.replace("</head>", '<meta name="robots" content="noindex"></head>')
        self.assertTrue(has(run(page(head=head)), "noindex", "critical"))

    def test_meta_refresh_reload_instant_and_delayed(self):
        # Plain reload (no URL) and self-URL refresh are not redirects.
        head_reload = GOOD_HEAD.replace("</head>", '<meta http-equiv="refresh" content="300"></head>')
        self.assertFalse(has(run(page(head=head_reload)), "meta refresh"))
        head_self = GOOD_HEAD.replace(
            "</head>",
            '<meta http-equiv="refresh" content="30;url=https://example.com/product/aero-2"></head>',
        )
        self.assertFalse(has(run(page(head=head_self)), "meta refresh"))
        # Instant redirect (delay 0) is Low; delayed redirect (delay > 0) is Medium.
        head_instant = GOOD_HEAD.replace("</head>", '<meta http-equiv="refresh" content="0;url=/new"></head>')
        self.assertTrue(has(run(page(head=head_instant)), "Instant meta refresh", "low"))
        head_delayed = GOOD_HEAD.replace("</head>", '<meta http-equiv="refresh" content="5;url=/new"></head>')
        self.assertTrue(has(run(page(head=head_delayed)), "Delayed meta refresh", "medium"))

    def test_svg_title_in_body_not_used_as_page_title(self):
        head = GOOD_HEAD.replace(
            "<title>Aero 2 Running Shoe: Light and Cushioned | Stride Supply</title>", ""
        )
        d = run(page(head=head, body="<svg><title>Icon</title></svg>"))
        self.assertEqual(d["title"], "")
        self.assertTrue(has(d, "Missing <title>", "high"))

    def test_image_link_with_alt_not_empty_anchor(self):
        d = run(page(body='<a href="/sale"><img src="/b.jpg" alt="Summer sale"></a>'))
        self.assertEqual(d["links"]["empty_text"], 0)
        self.assertFalse(has(d, "links with no anchor text"))

    def test_zero_links_page_flagged_no_internal_links(self):
        html = (GOOD_HEAD + "<body><h1>Title</h1><p>" + ("word " * 80) + "</p></body></html>").encode()
        self.assertTrue(has(run(html), "No internal links", "high"))

    def test_ukrainian_hreflang_severity_depends_on_english_context(self):
        # On an English page (html lang="en" or en hreflang), "uk" is High.
        head_en = GOOD_HEAD.replace(
            "</head>",
            '<link rel="alternate" hreflang="uk" href="https://example.com/product/aero-2"></head>',
        )
        self.assertTrue(has(run(page(head=head_en)), "for the UK use en-GB", "high"))
        # On a non-English page (e.g. html lang="uk"), "uk" is Low only.
        head_uk = head_en.replace('lang="en"', 'lang="uk"')
        d_uk = run(page(head=head_uk))
        self.assertFalse(has(d_uk, "hreflang 'uk'", "high"))
        self.assertTrue(has(d_uk, "hreflang 'uk' is Ukrainian", "low"))

    def test_x_robots_tag_bot_scoping_and_case_insensitive_mip(self):
        hdrs = Message()
        hdrs["Content-Type"] = "text/html; charset=utf-8"
        hdrs.add_header("X-Robots-Tag", "bingbot: noindex")
        hdrs.add_header("X-Robots-Tag", "MAX-IMAGE-PREVIEW:LARGE")
        resp = {
            "status": 200,
            "headers": hdrs,
            "body": page(
                head=GOOD_HEAD.replace('<meta name="robots" content="max-image-preview:large">', "")
            ),
            "final_url": "https://example.com/product/aero-2",
            "chain": [],
            "error": None,
        }
        with mock.patch.object(audit_page, "fetch", return_value=resp):
            d = audit_page.audit("https://example.com/product/aero-2", offline=True)
        self.assertFalse(has(d, "X-Robots-Tag", "critical"))
        self.assertFalse(has(d, "max-image-preview:large"))

    def test_robots_txt_429_and_size_limit(self):
        with mock.patch.object(
            audit_page,
            "robots_check",
            return_value={
                "status": 429,
                "bytes": 0,
                "sitemaps": [],
                "googlebot_blocked": None,
                "matched_rule": None,
                "unsupported": [],
            },
        ):
            d = audit_page.audit("https://example.com/product/aero-2", local_html=page(), offline=False)
        self.assertTrue(has(d, "robots.txt returns 429", "critical"))
        with mock.patch.object(
            audit_page,
            "robots_check",
            return_value={
                "status": 200,
                "bytes": 501 * 1024,
                "sitemaps": ["https://example.com/sitemap.xml"],
                "googlebot_blocked": False,
                "matched_rule": None,
                "unsupported": [],
            },
        ):
            d2 = audit_page.audit("https://example.com/product/aero-2", local_html=page(), offline=False)
        self.assertTrue(has(d2, "500 KiB", "high"))

    def test_hreflang_codes(self):
        links = '<link rel="alternate" hreflang="{}" href="https://example.com/{}/">'
        head = GOOD_HEAD.replace(
            "</head>", "".join(links.format(c, c) for c in ("en-uk", "es-419", "de")) + "</head>"
        )
        d = run(page(head=head))
        msg = " ".join(issues(d, "high"))
        self.assertIn("en-uk", msg)
        self.assertIn("es-419", msg)
        self.assertNotIn("'de'", msg)

    def test_valid_hreflang_not_flagged(self):
        links = '<link rel="alternate" hreflang="{}" href="https://example.com/product/aero-2">'
        head = GOOD_HEAD.replace(
            "</head>",
            "".join(links.format(c) for c in ("de-AT", "en-GB", "zh-Hant-TW", "x-default")) + "</head>",
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
            d = audit_page.audit("https://www.stridesupply.com/", local_html=fh.read(), offline=True)
        for needle in ("noindex", "hreflang", "fail to parse", "navigate via JS", "meta keywords"):
            self.assertTrue(has(d, needle), f"fixture: expected finding containing {needle!r}")
        self.assertTrue(has(d, "hreflang 'uk'", "high"))


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


class SitemapTests(unittest.TestCase):
    """Sitemap XML parsing."""

    def test_parse_urlset_sitemap(self):
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/page1</loc></url>
            <url><loc>https://example.com/page2</loc></url>
        </urlset>"""
        pages, children = audit_page.parse_sitemap(xml)
        self.assertEqual(pages, ["https://example.com/page1", "https://example.com/page2"])
        self.assertEqual(children, [])

    def test_parse_sitemapindex(self):
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap><loc>https://example.com/sitemap1.xml</loc></sitemap>
            <sitemap><loc>https://example.com/sitemap2.xml</loc></sitemap>
        </sitemapindex>"""
        pages, children = audit_page.parse_sitemap(xml)
        self.assertEqual(pages, [])
        self.assertEqual(children, ["https://example.com/sitemap1.xml", "https://example.com/sitemap2.xml"])

    def test_image_locs_are_not_pages(self):
        xml = b"""<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
            <url><loc>https://example.com/p</loc>
              <image:image><image:loc>https://cdn.example.com/a.jpg</image:loc></image:image></url>
        </urlset>"""
        self.assertEqual(audit_page.parse_sitemap(xml), (["https://example.com/p"], []))

    def test_gzipped_sitemap(self):
        xml = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://e.com/</loc></url></urlset>'
        self.assertEqual(audit_page.parse_sitemap(gzip.compress(xml)), (["https://e.com/"], []))

    def test_sitemap_index_is_followed(self):
        index = b'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://e.com/a.xml</loc></sitemap></sitemapindex>'
        child = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://e.com/1</loc></url><url><loc>https://e.com/2</loc></url></urlset>'
        bodies = {"https://e.com/sitemap.xml": index, "https://e.com/a.xml": child}

        def fake_fetch(url, timeout):
            """Serve the two sitemap files from memory."""
            return {"error": None, "body": bodies[url]}

        with mock.patch.object(audit_page, "fetch", fake_fetch):
            self.assertEqual(
                audit_page.sitemap_urls("https://e.com/sitemap.xml", 5, 1), (["https://e.com/1"], None)
            )

    def test_doctype_is_refused(self):
        xml = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><urlset><url><loc>&a;</loc></url></urlset>'
        self.assertEqual(audit_page.parse_sitemap(xml), ([], []))

    def test_inflate_is_capped(self):
        bomb = gzip.compress(b"0" * (audit_page.MAX_BYTES + 1024))
        self.assertEqual(len(audit_page.inflate(bomb, 16 + 15)), audit_page.MAX_BYTES)

    def test_parse_malformed_xml_returns_empty(self):
        self.assertEqual(audit_page.parse_sitemap(b"not xml"), ([], []))


class SchemaValidationTests(unittest.TestCase):
    """Validation of Google-required schema.org properties."""

    def test_product_missing_offers_and_reviews(self):
        issues = []
        audit_page.check_jsonld_properties({"@type": "Product", "name": "Shoe"}, issues)
        self.assertTrue(any("offers" in msg for _, _, msg, _ in issues))

    def test_product_complete_has_no_issues(self):
        issues = []
        obj = {"@type": "Product", "name": "Shoe", "offers": {"@type": "Offer", "price": "10"}}
        audit_page.check_jsonld_properties(obj, issues)
        self.assertEqual(issues, [])

    def test_local_business_missing_address(self):
        issues = []
        audit_page.check_jsonld_properties({"@type": "Restaurant", "name": "Cafe"}, issues)
        self.assertTrue(any("address" in msg for _, _, msg, _ in issues))

    def test_product_as_item_reviewed_is_not_a_product_snippet(self):
        issues = []
        review = {"@type": "Review", "itemReviewed": {"@type": "Product", "name": "Shoe"}, "author": "A"}
        audit_page.check_jsonld_properties(review, issues)
        self.assertEqual(issues, [])

    def test_job_posting_needs_location_unless_remote(self):
        job = {
            "@type": "JobPosting",
            "title": "Dev",
            "description": "x",
            "datePosted": "2026-01-01",
            "hiringOrganization": {"@type": "Organization", "name": "Co"},
        }
        issues = []
        audit_page.check_jsonld_properties(job, issues)
        self.assertTrue(any("jobLocation" in msg for _, _, msg, _ in issues))
        issues = []
        audit_page.check_jsonld_properties(dict(job, jobLocationType="TELECOMMUTE"), issues)
        self.assertEqual(issues, [])

    def test_missing_required_is_high(self):
        issues = []
        audit_page.check_jsonld_properties({"@type": "Event", "name": "Gig"}, issues)
        self.assertEqual({sev for sev, *_ in issues}, {"high"})

    def test_breadcrumb_missing_items(self):
        issues = []
        audit_page.check_jsonld_properties({"@type": "BreadcrumbList"}, issues)
        self.assertTrue(any("itemListElement" in msg for _, _, msg, _ in issues))
        issues2 = []
        audit_page.check_jsonld_properties(
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1}]}, issues2
        )
        self.assertTrue(any("at least 2" in msg for _, _, msg, _ in issues2))
        self.assertTrue(any("position" in msg for _, _, msg, _ in issues2))

    def test_video_recipe_and_software_app_required_props(self):
        issues = []
        audit_page.check_jsonld_properties({"@type": "VideoObject", "name": "Demo"}, issues)
        self.assertTrue(any("thumbnailUrl" in msg for _, _, msg, _ in issues))
        self.assertTrue(any("uploadDate" in msg for _, _, msg, _ in issues))
        issues2 = []
        audit_page.check_jsonld_properties({"@type": "Recipe", "name": "Soup"}, issues2)
        self.assertTrue(any("image" in msg for _, _, msg, _ in issues2))
        issues3 = []
        audit_page.check_jsonld_properties(
            {"@type": "SoftwareApplication", "name": "App", "offers": {"@type": "Offer", "price": 0}},
            issues3,
        )
        self.assertTrue(any("aggregateRating" in msg for _, _, msg, _ in issues3))

    def test_faqpage_and_howto_flagged_low(self):
        for kind in ("FAQPage", "HowTo"):
            issues = []
            audit_page.check_jsonld_properties({"@type": kind}, issues)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0][0], "low")
            self.assertIn("no longer produces a Google rich result", issues[0][2])


class PageSpeedTests(unittest.TestCase):
    """Core Web Vitals from the PageSpeed Insights API."""

    def psi(self, payload):
        """Run pagespeed_check against a canned API response."""
        resp = mock.MagicMock()
        resp.read.return_value = json.dumps(payload).encode()
        resp.__enter__.return_value = resp
        with mock.patch("urllib.request.urlopen", return_value=resp):
            return audit_page.pagespeed_check("https://e.com/", 5)

    def test_field_data_is_read_and_cls_is_scaled(self):
        payload = {
            "loadingExperience": {
                "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 4300},
                    "INTERACTION_TO_NEXT_PAINT": {"percentile": 180},
                    "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 15},
                }
            },
            "lighthouseResult": {"audits": {"largest-contentful-paint": {"numericValue": 1200.4}}},
        }
        ps = self.psi(payload)
        self.assertEqual(ps["field"], {"LCP": 4300, "INP": 180, "CLS": 0.15})
        self.assertEqual(ps["field_scope"], "url")
        self.assertEqual(ps["lab"], {"LCP": 1200})

    def test_origin_fallback_is_labelled(self):
        payload = {
            "loadingExperience": {
                "origin_fallback": True,
                "metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 1}},
            },
            "originLoadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000}}},
        }
        ps = self.psi(payload)
        self.assertEqual((ps["field"], ps["field_scope"]), ({"LCP": 2000}, "origin"))

    def test_findings_use_field_data_only(self):
        field = {
            "field": {"LCP": 4300, "INP": 180, "CLS": 0.15},
            "field_scope": "url",
            "lab": {},
            "error": None,
        }
        with mock.patch.object(audit_page, "pagespeed_check", return_value=field):
            d = audit_page.audit("https://e.com/", local_html=page(), offline=False, pagespeed=True)
        perf = [f for f in d["findings"] if f["area"] == "performance"]
        self.assertEqual(sorted(f["severity"] for f in perf), ["high", "medium"])
        self.assertTrue(any("Poor LCP" in f["issue"] for f in perf))

    def test_no_field_data_is_low_only(self):
        lab = {"field": {}, "field_scope": None, "lab": {"LCP": 9000}, "error": None}
        with mock.patch.object(audit_page, "pagespeed_check", return_value=lab):
            d = audit_page.audit("https://e.com/", local_html=page(), offline=False, pagespeed=True)
        perf = [f for f in d["findings"] if f["area"] == "performance"]
        self.assertEqual([f["severity"] for f in perf], ["low"])


class MarkdownOutputTests(unittest.TestCase):
    """Markdown report generation."""

    def test_print_markdown_contains_table(self):
        import io

        d = {
            "url": "https://example.com",
            "final_url": "https://example.com",
            "status": 200,
            "findings": [
                {"severity": "critical", "area": "indexing", "issue": "noindex tag", "fix": "Remove it"}
            ],
        }
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            audit_page.print_markdown(d)
        out = buf.getvalue()
        self.assertIn("# SEO Audit: https://example.com", out)
        self.assertIn("| Severity | Area | Issue | Fix |", out)
        self.assertIn("**CRITICAL**", out)


class GSCTests(unittest.TestCase):
    """Google Search Console CSV analyzer."""

    def test_analyze_gsc_csv(self):
        import tempfile

        import analyze_gsc

        csv_content = (
            "Top queries,Clicks (Last 3 months),Clicks (Previous 3 months)\nshoes,100,500\nrunning,300,100\n"
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
            fh.write(csv_content)
            tmp_path = fh.name
        try:
            import io

            res = analyze_gsc.analyze(tmp_path, metric="clicks")
            self.assertEqual(len(res["top_drops"]), 2)
            self.assertEqual(res["top_drops"][0]["dimension"], "shoes")
            self.assertEqual(res["top_drops"][0]["change"], -400)
            self.assertEqual(res["top_gains"][0]["dimension"], "running")
            self.assertEqual(res["top_gains"][0]["change"], 200)
            self.assertIn("1,000 rows", res["rows_note"])
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                analyze_gsc.print_report(res)
            self.assertIn("Total of exported rows:", buf.getvalue())
        finally:
            os.unlink(tmp_path)

    def test_ctr_percent_and_position_direction(self):
        import tempfile

        import analyze_gsc

        csv_content = (
            "Top queries,Last 3 months CTR,Previous 3 months CTR,Last 3 months Position,Previous 3 months Position\n"
            "a,2.5%,5%,9.0,3.0\nb,6%,4%,2.0,4.0\n"
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
            fh.write(csv_content)
            tmp_path = fh.name
        try:
            ctr = analyze_gsc.analyze(tmp_path, metric="ctr")
            self.assertEqual(ctr["top_drops"][0]["dimension"], "a")
            self.assertEqual(ctr["top_drops"][0]["change"], -2.5)
            self.assertEqual(ctr["summary"], {})
            pos = analyze_gsc.analyze(tmp_path, metric="position")
            self.assertEqual(pos["top_drops"][0]["dimension"], "a")
            self.assertEqual(pos["top_gains"][0]["dimension"], "b")
            self.assertEqual(pos["summary"], {})
        finally:
            os.unlink(tmp_path)


class CliTests(unittest.TestCase):
    """Command-line behaviour of the auditor."""

    script = os.path.join(ROOT, "skills", "serpwise", "scripts", "audit_page.py")

    def cli(self, *args, stdin=""):
        """Run the auditor as a subprocess and return (exit code, stdout, stderr)."""
        import subprocess

        p = subprocess.run(
            [sys.executable, self.script, *args], input=stdin, capture_output=True, text=True, timeout=60
        )
        return p.returncode, p.stdout, p.stderr

    def test_limit_must_be_positive(self):
        code, _out, err = self.cli("--limit", "0", "x.html")
        self.assertEqual(code, 2)
        self.assertIn("--limit", err)

    def test_stdin_list_accepts_local_files(self):
        import tempfile

        with tempfile.NamedTemporaryFile("wb", suffix=".html", delete=False) as fh:
            fh.write(page())
            path = fh.name
        try:
            code, out, _err = self.cli("-", "--offline", "--json", stdin="# comment\n" + path + "\n")
            results = json.loads(out)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["source_file"], path)
            self.assertEqual(code, 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
