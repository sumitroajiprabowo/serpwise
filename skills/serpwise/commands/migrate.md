# migrate: plan a site move

**Input:** the kind of move (new domain, HTTP→HTTPS, URL structure change, CMS or platform change, hosting or CDN only), the site size, and the target date. Rules: `references/crawling-indexing.md` §5 (redirects) and §16 (site moves).

## Steps
1. Classify the move.
   - **URL changes** (domain, HTTPS, paths, platform) need the full checklist.
   - **Hosting or CDN only** (same URLs) needs the short DNS checklist in §16.
2. Write a dated checklist with three phases.
   - **Before:**
     - Set up the new site with TLS and its live robots.txt, and remove any staging `noindex`.
     - Verify every property in Search Console.
     - Build the old → new **URL map** as a CSV, from sitemaps, analytics, logs, the CMS and the Links report. Include images, CSS and JS.
     - Set self-canonicals, and update hreflang and internal links.
     - Return 404/410 for dropped content.
     - Check that the server can handle heavier crawling.
   - **Launch:**
     - Add server-side **301/308** redirects, one hop each. Never mass-redirect to the home page.
     - Submit the new sitemap.
     - Use the **Change of Address** tool, but only for domain or subdomain moves.
     - Update external profiles, ads and important backlinks.
   - **After:**
     - Watch the Page Indexing, Sitemaps and Crawl Stats reports and the server logs.
     - Traffic should shift from the old site to the new one.
     - Keep the redirects for **at least a year**.
     - Expect weeks of fluctuation, longer on large sites.
3. If the repo holds the redirect config (nginx, `.htaccess`, `next.config` redirects, `vercel.json`, `netlify.toml`, a CMS plugin), write the rules. Test a sample with `curl -sI <old-url>`: expect a 301/308 with the right `Location` in a single hop.
4. **Output:**
   - the checklist (owners left blank);
   - the URL-map template;
   - the redirect rules;
   - the common mistakes to avoid: leftover `noindex` or robots blocks, redirects to 404s, stale sitemaps, an under-provisioned server.
