# Monitoring & debugging

Source: developers.google.com/search/docs/monitor-debug/* and /guides/debug

## Contents
1. Search Console workflow
2. Debugging tools
3. Traffic-drop diagnostic tree
4. Analysis steps in the Performance report
5. Google Trends
6. Search Console vs Google Analytics
7. Search operators
8. Preventing user-generated spam
9. JavaScript problem checklist
10. Identifying Google Search traffic in analytics and server logs
11. Social and video platform accounts in Search Console

## 1. Search Console workflow
1. Verify ownership of every variant you care about: a Domain property, or URL-prefix properties for http/https and www/non-www.
2. Check the Page Indexing (Index Coverage) report for errors.
3. Optionally submit a sitemap. It speeds discovery and enables the Sitemaps report.
4. Watch the Performance report: queries, pages, countries, devices, search appearance.
- Google emails you about new issues, so no daily login is needed. Check monthly or after changes.
- Tools:
  - SEO and owner side: Manual Actions, Removals (temporary, about 6 months), Change of Address, rich result reports.
  - Developer side: URL Inspection, Core Web Vitals, Security Issues, Crawl Stats, robots.txt report.

## 2. Debugging tools
- **URL Inspection** (owners only): index status, the canonical Google chose, a live test, rendered HTML and screenshot, loaded resources, JS console errors, Request indexing.
- **Rich Results Test** (anyone, URL or code input): rendered DOM and structured data eligibility.
- **Schema Markup Validator**: generic schema.org validation.
- **robots.txt report**: fetch status, and can request a recrawl of robots.txt.
- **PageSpeed Insights / CrUX / Lighthouse**: Core Web Vitals.
- **Local or firewalled pages**: expose them with a tunnel (`python3 -m http.server 5326` then `ngrok http 5326 --request-header-add ngrok-skip-browser-warning:1`). Some tunnels add a robots.txt block, and Google's tools respect it.
- Fixes don't show until recrawl, which usually takes a few days. Search Console may keep showing old errors until then.

## 3. Traffic-drop diagnostic tree
Read the shape of the drop first:
- **Sudden site-wide drop to near zero**: security issue, manual action, site down, robots.txt or noindex accident.
- **Gradual decline**: algorithmic update, changing interest, competition.
- **Recurring yearly pattern**: seasonality.
- **Drop that also shows in other sites' data, or appears overnight then reverts**: reporting glitch.

Check in this order:
1. **Reporting glitch**: the Search Console "Data anomalies" page.
2. **Google update**: the Search Status Dashboard ranking-updates list and core-update dates.
   - Small position drop (e.g. 2 → 4): normal fluctuation. Don't make radical changes to good pages.
   - Large drop across many queries (top 10 → 29): self-assess the whole site against helpful-content questions (fundamentals.md §4). Improvements take days to months, and recovery isn't guaranteed.
3. **Technical issues**: Crawl Stats (spikes in errors, host availability, robots.txt fetch failures) and Page Indexing (new noindex, 404, 5xx, soft 404, redirect errors). Site-wide problems drop traffic fast. A misplaced noindex drops it gradually as pages are recrawled.
4. **Security**: Security Issues report (malware, phishing, hacked content). Browsers show warnings.
5. **Spam**: Manual Actions report. Review spam-policies.md, fix, and file a reconsideration request.
6. **Seasonality or changing interest**: check top queries in Google Trends to see whether the whole market dropped.
7. **Site move or migration**: fluctuation lasts weeks (medium sites) or longer. Use the site-move troubleshooting checklist (crawling-indexing.md §16).

## 4. Analysis steps in the Performance report
- **Clicks and impressions both down**: visibility problem (causes above).
- **Impressions flat, clicks down**:
  - Your title or snippet is less compelling, or competitors gained rich results.
  - Improve title links and meta descriptions, and add eligible structured data.
- **Date range**: set it to the **last 16 months** to spot yearly patterns. Keep longer history via the Search Analytics API or bulk data export (BigQuery).
- **Compare views**: last 3 months vs the previous period, and year over year. Click through Queries, Pages, Countries, Devices, and Search appearance to isolate the drop.
- **Search type filter**: check Web, Image, Video, and News separately.
- **Average position**: turn it on. Don't obsess over it, since clicks and impressions matter more. A persistent large decline calls for a content self-assessment.
- **Pages table**: sort by click difference.
  - Site-wide drop: Page Indexing report.
  - Only a group of pages: URL Inspection on samples, plus a template-level check.
- **Industry trends**:
  - Compare your queries with Trends' top regional queries. Create content for missing or rising topics.
  - Check whether those pages are crawled and indexed.

## 5. Google Trends
- Trends shows sampled, normalized interest (not absolute volume). Explore compares up to 5 terms by region, related topics and queries (Top and Rising). Trending now shows what's trending right now.
- Uses:
  - Keyword vocabulary research, including other languages.
  - A content calendar: publish ahead of seasonal peaks, market by market.
  - Benchmarking a traffic drop against the market.
  - Brand monitoring over 30 or 90 days.
- Don't write about something only because it's trending. It must fit your audience and expertise.
- Topics merge languages and misspellings, and some related queries will be irrelevant.

## 6. Search Console vs Google Analytics
- Search Console measures performance *before* the click (impressions, clicks, CTR, position). GA measures behavior *after* (sessions, engagement, conversions).
- The most comparable pair is GSC **Clicks** vs GA **Sessions** (source google / medium organic). They will differ.
- Why they differ:
  - Missing or misfiring GA tags, consent opt-outs.
  - Timezone: GSC uses Pacific Time, fixed.
  - Attribution models.
  - Canonical URL aggregation in GSC.
  - Search types (Discover, News).
  - Non-HTML files like PDFs count in GSC but aren't measured in GA unless you track them (e.g. enhanced measurement events).
  - Bot filtering: GA drops known bots, GSC doesn't necessarily.
- Small differences are normal. The trends should match even when totals don't.
- Setup: the Looker Studio template (GSC URL Impression table plus GA4). Use the same country and device filters on both sources.
- Advanced: GSC bulk export plus GA4 BigQuery export, joined on landing page, country, or device.
- Interpreting changes:
  - Organic clicks drop: investigate in GSC.
  - Engagement drops: check that the content matches the query intent.
  - Organic share moves but sessions and engagement don't: another channel changed. Check GA's Traffic acquisition report.
- Other routes: connect Search Console to GA, or Site Kit on WordPress.

## 7. Search operators (debugging aid only, results are incomplete)
- `site:example.com` covers the domain and subdomains. `site:https://example.com/blog/` limits to a prefix. `site:example.com widget` finds pages with that term.
- Use `site:` to spot spam injection (e.g. `site:example.com casino`).
- `filetype:pdf`, `imagesize:1200x800` (Images), `src:` (Images, pages that reference an image URL).
- A missing URL in `site:` results doesn't prove it isn't indexed. **URL Inspection is authoritative.**

## 8. Preventing user-generated spam (comments, forums, hosting platforms)
- Publish a clear abuse policy, and let trusted users report spam.
- Gate new users:
  - reCAPTCHA, manual approval or moderation, IP blocklists or a firewall.
  - Log signup signals: form-fill speed, IP ranges, user agents, odd usernames.
- **Reputation system**: `noindex` content from new or low-reputation users and allow indexing once they're trusted.
- Add `rel="ugc"` or `nofollow` to user links. Noindex utility and sharing pages by default.
- Monitor:
  - Search Console alerts, Page Indexing and Performance spikes.
  - `site:` searches and Google Alerts for spammy terms, server-log spikes.
  - Safe Browsing API checks, language detection for unexpected locales.
- Tools: Akismet (CMS comments), reCAPTCHA.

## 9. JavaScript problem checklist (fix-search-javascript)
1. Test with URL Inspection or the Rich Results Test. Read the console errors and the resource-loading list. Optionally log errors with `window.addEventListener('error', ...)`.
2. Fix SPA soft 404s: redirect to a real 404 URL, or add noindex on error views.
3. Don't require permission prompts (camera, geolocation, notifications). Googlebot declines them.
4. Use no `#` fragment routing. The AJAX crawling scheme died in 2015. Use the History API.
5. Don't depend on localStorage, sessionStorage, or cookies persisting.
6. Fingerprint asset filenames, because WRS may use stale cached JS or CSS.
7. Feature-detect and provide fallbacks. No WebGL, WebSockets, or WebRTC in Googlebot.
8. Web components must use `<slot>` for light-DOM content.
9. JS paywalls: don't send the full text and hide it client-side.
10. Re-test. Expect days for recrawl.

## 10. Identifying Google Search traffic in analytics and server logs
- Google Search sends the `origin` referrer policy, so `Referer` has only the scheme and host, never the path or the query. Use the Performance report for queries.
- Referer values:
  - Web: `https://www.google.com/` or a local Google domain (`https://www.google.co.uk/`, `https://www.google.co.jp/`).
  - Google app on Android: `android-app://com.google.android.googlequicksearchbox/https/www.google.com`, or the web values when the link opens in a browser.
  - Google app on iOS: the web values.
- Discover and Google Images send the same values as the surface they were seen on, so they can't be separated from web Search by referrer alone.
- In server logs, count landing-page requests only. Images, CSS and JS requests carry your own page as the referrer.
- Search traffic showing as direct or referral: check custom channel rules, referral exclusions and filters in the analytics tool.
- Why logs or analytics undercount compared with Search Console:
  - blank referrers from private browsing, privacy settings, extensions, ad blockers, some new-tab opens, native search widgets;
  - consent choices;
  - client-side redirects (JavaScript or `meta refresh`) or a strict `Referrer-Policy` that replace or strip the referrer, and redirects that drop parameters such as `gclid`;
  - a GSC click becomes a session only after the page loads and the tag runs;
  - analytics may include paid clicks, while GSC counts organic only.

## 11. Social and video platform accounts in Search Console
- TikTok, Instagram, X and YouTube accounts can be added as platform properties in Search Console, one by one. Claiming a Search profile adds verified accounts automatically.
- Their content shows in Search as short-video carousels, latest-post carousels and "what people are saying".
- Insights report: 28-day clicks, top content, the queries people used, audience countries, and query groups (top, trending up, trending down).
- Performance report: filter by country, date, device or query. Use the 24-hour view to catch a new post trending, then cross-promote it.
- Compare formats with page filters and comparison mode: YouTube `/watch` vs `/shorts/`, Instagram `/p/` vs `/reels/`. A `playlist` filter reports the playlist page only, not its videos.
- Export each platform property to compare across platforms.
- Revive older posts that suddenly gain impressions (pin, reference, follow up). Add a Search Console annotation when you change a caption or title, then compare before and after.
