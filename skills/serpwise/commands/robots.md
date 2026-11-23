# robots: review or write robots.txt

**Input:** a site URL or robots.txt content, plus what should and shouldn't be crawled. Rules: `references/crawling-indexing.md` §2.

## Steps
1. **Get the file.**
   - Live: `curl -s -o robots.txt -w "%{http_code}\n" https://host/robots.txt`.
   - Interpret the status code per §2: 4xx means no restrictions; 5xx or 429 stops crawling.
2. **Check it:**
   - it sits at the host root and covers this protocol, host and port;
   - it is under 500 KiB;
   - it uses supported fields only (`crawl-delay` and `noindex` are ignored);
   - which group Googlebot obeys: the most specific group only, never merged with `*`;
   - longest-match precedence and the `*` / `$` wildcards;
   - CSS and JS needed for rendering aren't blocked;
   - `Sitemap:` lines use absolute URLs.
3. **Test the important URLs.**
   - On a live site, run the bundled auditor per URL. It reports `googlebot_blocked` and the matched rule.
   - Otherwise apply the precedence rules by hand and show the matched rule for each URL.
4. **Correct a common misconception:** robots.txt doesn't remove pages from Google. To deindex, use `noindex`, and don't block the page in robots.txt, or Google can't see the `noindex`.
5. **Output:**
   - findings rated by severity;
   - the corrected file;
   - a table of URL → allowed or blocked → matching rule.
   Tell the user to verify in the Search Console **robots.txt report**.

## Done when
Every important URL and rendering resource (CSS/JS) has been tested against Googlebot's group and precedence rules, any Critical/High blocks are fixed, and the Search Console verification step is listed.
