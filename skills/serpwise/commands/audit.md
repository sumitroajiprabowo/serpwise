# audit: one-page SEO audit

**Input:** a URL, a local HTML file, or pasted source. If none is given, ask for one.

## Steps
1. Run the bundled auditor (see "Bundled auditor" in SKILL.md).
   - For a live URL, run it as is.
   - For a local file, pass `--base-url` with the URL the page will live at.
   - If you must not touch the network, add `--offline`, and list robots.txt, HTTP status and headers as unverified.
2. Read the raw HTML yourself for what the script can't judge:
   - the page type (home, category, product, article, local business);
   - whether the main content and links are in the HTML or only appear after JavaScript runs;
   - content quality against `references/fundamentals.md` §4;
   - internal linking;
   - which structured data types fit this page type.
3. Connect the findings, and explain causal chains the user would miss. Examples:
   - An invalid element in `<head>` hides every robots, canonical and hreflang tag after it, so fixing it can suddenly activate a `noindex`.
   - A canonical that points to another host competes with this page's own indexing.
   - hreflang that points to non-canonical URLs is ignored.
4. Give one finding per root cause. Rate its severity (Critical, High, Medium, Low) and cite the Google rule behind each.
5. Write the report in the "Report format" from SKILL.md. Include ready-to-paste fixes for the Critical and High findings, such as a corrected `<head>` or JSON-LD block.
6. JavaScript-heavy pages: ask the user to confirm in Search Console via **URL Inspection → View crawled page**. If a browser tool is available, compare the rendered DOM with the raw HTML.

## Several pages or a whole site
Audit the home page plus one URL per template (category, product, article, location). Report per template, and say that it is a sample. For site-wide crawl questions, also run `sitemap` and `robots`.

## Done when
Every Critical and High finding has evidence (a line number, header or rule) and a concrete fix, and everything that wasn't verified is listed under "How to verify".
