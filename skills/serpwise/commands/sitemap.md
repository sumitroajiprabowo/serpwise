# sitemap: review or generate an XML sitemap

**Input:** a sitemap URL or file, or a site or repo to generate one for. Rules: `references/crawling-indexing.md` §7.

## Steps
1. **Decide whether it's needed.** Large, new, or media-heavy sites benefit. A well-linked site of about 500 pages or fewer may not.
2. **Get it.** Fetch it with `curl -s` (pipe through `gunzip` for `.gz`), or find it via the `Sitemap:` line in robots.txt.
3. **Check it:**
   - The XML is well-formed: `python3 -c "import sys,xml.etree.ElementTree as E; E.parse(sys.argv[1])" sitemap.xml`.
   - It uses the right namespace.
   - Each file stays within 50,000 URLs and 50 MB uncompressed. Otherwise use a sitemap index.
   - URLs are absolute and inside the sitemap's host and path scope.
   - It lists only canonical, indexable URLs that return 200. Sample 10–20 with `curl -s -o /dev/null -w "%{http_code}"`, and run the auditor on a few to check canonical and noindex.
   - `<lastmod>` is accurate. `<priority>` and `<changefreq>` are ignored by Google.
   - Image, video, news and hreflang extensions are valid.
4. **Check discovery:** there's a `Sitemap:` line in robots.txt and/or the sitemap is submitted in Search Console.
5. **Generate one:** prefer the framework's own generator (`app/sitemap.ts`, `next-sitemap`, `@nuxtjs/sitemap`, a WordPress core or plugin sitemap). Otherwise write a small script. Include only canonical URLs.
6. **Output:**
   - findings rated by severity;
   - a corrected sitemap or generator config.
   Tell the user to verify in the Search Console **Sitemaps report** (status and discovered URLs).

## Done when
The XML is well-formed, stays within Google's limits, lists only canonical indexable 200 URLs, and has a discovery path (`robots.txt` `Sitemap:` line and/or Search Console submission).
