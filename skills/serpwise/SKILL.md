---
name: serpwise
description: Google Search SEO playbook based on the official Google Search Central docs, with commands audit, fix, schema, meta, robots, sitemap, hreflang, migrate, drop, content and local (e.g. "/serpwise audit https://example.com"). Use it whenever the user wants to audit a site or page for SEO, rank better or get indexed on Google, fix robots.txt/sitemap/canonical/noindex/redirect/JavaScript-rendering problems, add or validate schema.org JSON-LD and rich results, write titles and meta descriptions, plan a site migration or hreflang, optimize product pages, review content quality, set up local SEO, or debug a Google traffic drop or Search Console error, even without the word "SEO" (e.g. "why isn't my site showing up on Google?") and in any language. Also use it when reviewing website code (Next.js, Nuxt, WordPress, Laravel, HTML) for search-friendliness.
license: MIT
compatibility: Optional bundled auditor needs Python 3.8+ and network access to fetch the URL being audited. Works with any Agent Skills client (Claude Code, Codex, Copilot, Antigravity, etc.).
metadata:
  version: "1.1.2"
  source: "https://developers.google.com/search/docs"
  docs-snapshot: "2026-11-22"
---

# Serpwise: Google Search SEO for coding agents

This skill turns Google's own Search Central documentation into a working method. Google says plainly that **there is no secret trick that ranks a site #1**. Sites win by:
1. being technically easy for Google to crawl, render and index;
2. having genuinely helpful, people-first content;
3. presenting that content well in results.

Work in that order, because the later steps are wasted if an earlier one is broken. A beautiful title on a `noindex` page earns nothing.

Answer in the user's language. Cite the Google rule behind each recommendation so the user can trust it isn't folklore.

## Commands

Users invoke a command as `/serpwise <command> [target]` (Claude Code, Copilot), `$serpwise <command> [target]` (Codex), or in plain words.

| Command | Use it to | Playbook | Also read |
|---|---|---|---|
| `audit <url\|file>` | Audit a page and get findings ranked by severity | `commands/audit.md` | `references/fundamentals.md`, `references/crawling-indexing.md`, `references/appearance.md` |
| `fix [path]` | Find and fix SEO issues in the codebase, then re-check | `commands/fix.md` | `references/crawling-indexing.md`, `references/appearance.md` |
| `schema <page>` | Write or validate JSON-LD for rich results | `commands/schema.md` | `references/structured-data.md` |
| `meta <page>` | Write title and meta description | `commands/meta.md` | `references/appearance.md` |
| `robots [url\|file]` | Review or write robots.txt | `commands/robots.md` | `references/crawling-indexing.md` |
| `sitemap [url\|file]` | Review or generate an XML sitemap | `commands/sitemap.md` | `references/crawling-indexing.md` |
| `hreflang [url]` | Set up or check multilingual/multi-regional sites | `commands/hreflang.md` | `references/international.md` |
| `migrate` | Plan a domain, HTTPS, URL, platform or hosting move | `commands/migrate.md` | `references/crawling-indexing.md` |
| `drop` | Diagnose a Google traffic drop | `commands/drop.md` | `references/monitoring-debugging.md` |
| `content <page>` | Review helpful content and E-E-A-T | `commands/content.md` | `references/fundamentals.md`, `references/spam-policies.md` |
| `local <page>` | Set up or audit local business pages and LocalBusiness markup | `commands/local.md` | `references/structured-data.md`, `references/appearance.md`, `references/spam-policies.md` |

Routing:
- **No command and no clear task:** show this table as a short menu in the user's language and ask what to run. Don't start work on your own.
- **Explicit command, or a request that clearly matches one:** read its playbook and the "Also read" files, then follow the playbook. If two commands fit, ask once.
- **Any other SEO question:** answer from the reference files below.
- **Site-specific extras:**
  - Online store: also read `references/ecommerce.md`.
  - Adult or sensitive content: `references/explicit-content.md`.
  - Shortcut or link-buying requests, or a manual action: `references/spam-policies.md`.
- **Chaining:** commands chain naturally (`audit` → `fix` → `audit` again to confirm).

## Reference files: read only what the task needs

| File | Covers |
|---|---|
| `references/fundamentals.md` | How Search works, Search Essentials, helpful content, E-E-A-T, generative AI content, myths, promotion, hiring an SEO |
| `references/crawling-indexing.md` | robots.txt, sitemaps, canonical, noindex, redirects, status codes, JS SEO, crawl budget, URL structure, mobile-first, site moves, removals |
| `references/appearance.md` | Titles, snippets, images, video, favicon, site name, Discover, Core Web Vitals, ranking systems, AI features and generative AI search (AEO/GEO) |
| `references/structured-data.md` | General policies, required/recommended properties per type, JSON-LD templates |
| `references/monitoring-debugging.md` | Traffic-drop tree, Search Console workflow, debugging tools, GA vs GSC, Google traffic in logs, social and video accounts, Trends, UGC spam |
| `references/ecommerce.md` | Product data, Merchant Center, variants, pagination, faceted navigation, launch |
| `references/international.md` | hreflang, locale URL structures, locale-adaptive pages |
| `references/explicit-content.md` | SafeSearch and misclassification |
| `references/spam-policies.md` | Spam tactics to refuse and their legitimate alternatives |

## Bundled auditor

`scripts/audit_page.py` lives in this skill's folder (`<skill-dir>` is the directory that contains this SKILL.md). It is Python 3.8+ with the standard library only. Use `python` instead of `python3` if that's what the system has (common on Windows).

```bash
python3 <skill-dir>/scripts/audit_page.py https://example.com/page [--json]
python3 <skill-dir>/scripts/audit_page.py page.html --base-url https://the-live-url/ [--offline]
python3 <skill-dir>/scripts/audit_page.py --sitemap https://example.com/sitemap.xml --limit 20 [--markdown]
python3 <skill-dir>/scripts/audit_page.py https://example.com/ --pagespeed   # Core Web Vitals field data
```

What it checks:
- HTTP status, redirect chain, `<meta http-equiv="refresh">` redirects and X-Robots-Tag;
- robots.txt rules for Googlebot, HTTP 429/5xx errors, the 500 KiB limit and sitemap lines;
- title, meta description, robots meta, canonical, viewport, `<h1>`, hreflang;
- image alt text, `<a href>` crawlability;
- JSON-LD parse errors, types, missing required properties for Product, LocalBusiness, Event, JobPosting, BreadcrumbList, VideoObject, Recipe and SoftwareApplication (recommended ones for Article), warnings for retired FAQPage and HowTo rich results, and og:image;
- with `--pagespeed`, Core Web Vitals from real-user (Chrome UX Report) data via the PageSpeed Insights API. The keyless quota runs out fast, so pass `--pagespeed-key` or set `PAGESPEED_API_KEY`;
- invalid elements in `<head>`;
- HTML size against Googlebot's 2 MB limit.

`scripts/analyze_gsc.py` ranks the queries or pages that lost and gained the most in a Search Console Performance export made in Compare mode: `python3 <skill-dir>/scripts/analyze_gsc.py Queries.csv --metric clicks`.

The auditor reads raw HTML only and doesn't run JavaScript. If Python or network access isn't available, get the HTML another way (curl, a browser tool, or pasted source) and check the same items by hand.

## Severity levels

Rate every finding with one of four severity levels so the user fixes what matters first. Use these English labels, or their equivalent in the user's language:

- **Critical:** the page can't be indexed or served. Examples:
  - a 4xx/5xx status;
  - a `noindex` added by mistake;
  - robots.txt disallowing important paths or the CSS/JS they need;
  - a canonical pointing elsewhere by mistake;
  - a soft 404;
  - a security issue or manual action;
  - content that only appears after user interaction;
  - an invalid element (`<img>`, `<iframe>`, `<div>`) in `<head>` before the metadata. Google stops reading `<head>` there, so the robots, canonical and hreflang tags after it are ignored.
- **High:** the page is indexed but held back. Examples:
  - missing or duplicate titles;
  - no internal links to the page;
  - duplicate URLs without canonicalization;
  - mobile content smaller than desktop;
  - invalid structured data on key templates;
  - poor Core Web Vitals;
  - thin or copied content;
  - intrusive interstitials.
- **Medium:** presentation and rich-result eligibility. Examples:
  - weak meta descriptions;
  - missing alt text;
  - non-descriptive URLs;
  - missing recommended schema properties;
  - a missing favicon or site-name markup.
- **Low:** polish and long-term work. Examples: breadcrumbs, `alternateName`, Trends-driven content ideas, promotion.

## Myths: don't recommend these

Google says these don't matter. If the user asks about one, explain kindly with the source rule.
- The meta keywords tag.
- Keyword stuffing.
- Keywords in the domain or URL as a ranking boost.
- A "magic" word count.
- **Fixed character limits for titles or meta descriptions.** Google sets none; it truncates to fit the display.
- Worrying that the TLD matters (except for country targeting).
- A "duplicate content penalty". Duplicates are an inefficiency, not a penalty.
- Heading count or order.
- E-E-A-T as a direct ranking factor.
- `rel=next/prev` (no longer used).
- Sitemap `<priority>` and `<changefreq>` (ignored).
- `crawl-delay` or `noindex` in robots.txt (unsupported).
- llms.txt or special "AI files" to appear in AI Overviews (not needed).
- "Chunking" content, rewriting it for AI, or one page per query variant for AI search (not needed; the last is scaled content abuse).
- Geo meta tags (ignored).
- The `lang` attribute for language detection (Google reads the visible content instead).

Never suggest tactics that violate spam policies:
- buying links or using PBNs;
- mass AI or programmatic pages made to game rankings;
- doorway city pages;
- cloaking or hidden text;
- repurposing expired domains;
- parasite pages on a high-authority site.

These can wipe out a site, and Google's systems (SpamBrain plus manual review) catch them. Refuse, name the policy from `references/spam-policies.md`, and offer the legitimate alternative.

## Report format

Use this structure for `audit`, with the headings in the user's language. Other commands define their own output in their playbook.

```
# SEO Audit: <URL or site>
## Summary
<3-5 sentences: overall health, the single most important fix, expected impact>
## Findings
| # | Severity | Issue | Evidence | Fix | Google rule |
|---|---|---|---|---|---|
## Details by area
### Crawling & indexing
### Content & relevance
### Search appearance (titles, snippets, structured data, images)
### Performance & page experience
### (Ecommerce / International / etc. when relevant)
## Action plan
1. This week: Critical and High ...
2. This month: Medium ...
3. Ongoing: Low, content, promotion ...
## How to verify
<URL Inspection, Rich Results Test, Page Indexing report, PageSpeed Insights... and what "fixed" looks like>
```

Close with realistic expectations. Google says changes can take from hours to several months to show, so judge results after a few weeks, and not every change produces a visible ranking jump.
