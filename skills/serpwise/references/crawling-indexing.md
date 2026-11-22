# Crawling & indexing

Source: developers.google.com/search/docs/crawling-indexing/* and developers.google.com/crawling/docs/robots-txt/*

## Contents
1. Crawlers, limits, file types
2. robots.txt (create + full spec)
3. Robots meta / X-Robots-Tag / noindex
4. Canonicalization
5. Redirects
6. HTTP status codes
7. Sitemaps
8. URL structure & faceted navigation
9. Links (crawlable, rel qualifiers)
10. JavaScript SEO, lazy loading & fixes
11. Mobile-first indexing
12. Page metadata (valid head, supported meta tags)
13. Crawl budget (large sites)
14. Recrawl requests
15. Removals & redaction
16. Site moves, A/B tests, pausing a business
17. AMP
18. Verifying Googlebot

## 1. Crawlers, limits, file types
- Three crawler categories:
  - **Common crawlers** (Googlebot) always obey robots.txt.
  - **Special-case crawlers** (AdsBot) may ignore `*` rules.
  - **User-triggered fetchers** (Site Verifier, etc.) ignore robots.txt.
- Tokens worth knowing: `Googlebot` (Search, Discover; smartphone and desktop share it), `Googlebot-Image` (images, logos, favicons), `Googlebot-Video`, `Googlebot-News`, `Storebot-Google` (Shopping), `Google-InspectionTool` (testing tools, no Search effect), `GoogleOther` (no product effect).
- `Google-Extended` is a robots.txt token only. It controls Gemini training and grounding outside Search and has no effect on Search inclusion or ranking. Google has said it plans to support the shared AIPREF training signal (`user-agent: __usage_ai-training`) in early 2027.
- Verify Googlebot with reverse DNS or Google's published IP ranges, not the user-agent string alone.
- Crawling comes mostly from US IPs. Google may also crawl from other countries.
- Protocols: HTTP/1.1 and HTTP/2. Opt out of HTTP/2 by responding `421`. Encodings supported: gzip, deflate, br.
- **Size**: Google's crawlers fetch the first 15MB of a file by default, but Googlebot for Search fetches only the **first 2MB** of HTML and other supported text files (**64MB** for PDFs). Each CSS or JS file is fetched separately under the same 2MB limit. Uncompressed size counts, and anything past the limit is ignored. Keep critical content and links early.
- Caching: `ETag`/`If-None-Match` is preferred over `Last-Modified`. Set both. `Cache-Control: max-age` is honored.
- File type comes from `Content-Type`.
  - Indexable documents and text: HTML, PDF, DOC/DOCX, XLS/XLSX, PPT/PPTX, ODP/ODS/ODT, RTF, EPUB, HWP, PS, TXT and source code, CSV, KML/KMZ, GPX, SVG, TeX, WML, XML.
  - Images: BMP, GIF, JPEG, PNG, WebP, SVG, AVIF.
  - Video: common formats (MP4, WebM, MOV, M3U8, and so on).

## 2. robots.txt
Purpose: manage crawl load. It is **not** a way to keep pages out of Google. A disallowed URL can still be indexed (URL only, no snippet) if linked. Use `noindex` or a password for that.

Effects by type:
- **HTML/PDF**: don't use robots.txt to hide them.
- **Media**: disallow does keep images and video out.
- **Resources**: block only if the page renders fine without them. Never block CSS/JS needed for rendering.

Rules:
- Location and scope:
  - One file at the host root (`https://host/robots.txt`), UTF-8 plain text, **max 500 KiB** (the rest is ignored).
  - Applies per protocol + host + port. Subdomains need their own file. A file in a subdirectory is invalid.
  - CMS-hosted sites (Wix, Blogger) use the platform's visibility settings instead.
- Supported fields: `user-agent`, `allow`, `disallow`, `sitemap`. **`crawl-delay` and `noindex` are not supported.**
- Case rules: field names are case-insensitive, path values are case-sensitive, and user-agent values are case-insensitive.
- Groups:
  - Only the most specific matching user-agent group applies. Specific groups are not merged with `*`.
  - Multiple groups for the same agent are merged.
  - `*` does not cover AdsBot.
- Precedence: the longest matching path wins. On a tie, the least restrictive (allow) wins.
- Wildcards: `*` matches any sequence and `$` anchors the end. `/fish` matches `/fish.html` and `/fishheads` but not `/Fish`.
- Sitemap: `sitemap:` takes an absolute URL, can point to another host, and is independent of groups.
- HTTP status of robots.txt itself:
  - 2xx: parsed.
  - 3xx: up to 5 hops, then treated as 404.
  - 4xx except 429: treated as no restrictions.
  - 5xx or 429: crawling stops for 12h, then Google uses the last cached copy for up to 30 days, then treats it as unrestricted if the site is otherwise available.
  - Never serve 503 for robots.txt during maintenance.
- Cached up to 24h. Test with the robots.txt report in Search Console.

Faceted URL blocking example:
```
user-agent: Googlebot
disallow: /*?*color=
disallow: /*?*size=
allow: /*?products=all$
```

## 3. Robots meta / X-Robots-Tag / noindex
- Tag forms:
  - `<meta name="robots" content="noindex">` applies to all engines. `name="googlebot"` targets Google web only. `googlebot-news` targets News.
  - Header form: `X-Robots-Tag: noindex` works for PDFs, images, and video. It can be per-bot (`X-Robots-Tag: googlebot: nofollow`).
- Values:
  - `all` is the default.
  - Indexing and link control: `noindex`, `nofollow`, `none` (= noindex, nofollow).
  - Snippets: `nosnippet` (also blocks use as direct input in AI Overviews / AI Mode), `max-snippet:N` (0 = nosnippet, -1 = unlimited).
  - Previews: `max-image-preview:none|standard|large`, `max-video-preview:N`.
  - Other controls: `indexifembedded` (with noindex), `notranslate`, `noimageindex`, `unavailable_after:<date>`.
  - Ignored now: `noarchive`, `nocache`, `nositelinkssearchbox`.
- Conflicts resolve to the most restrictive value.
- `data-nosnippet` on `span`, `div`, or `section` excludes that text from snippets. Don't toggle it with JS.
- **Pitfall**: a page blocked by robots.txt can't have its noindex read. Allow crawling so the rule is seen. Removal takes until recrawl, which can be months for low-priority pages.
- Don't add noindex in initial HTML and remove it with JS: Google may skip rendering.

## 4. Canonicalization
- Google chooses one canonical among duplicates. Duplicates come from protocol, www, params, sort/filter, device, region, and accidental staging copies.
- Language versions are duplicates only if the main content is in the same language.
- Signals, strongest first: **redirect**, then **`rel=canonical`**, then **sitemap inclusion**. Also HTTPS is preferred over HTTP, and hreflang clusters matter. All are hints, and Google may pick another.
- Best practices:
  - Self-referencing canonical on canonical pages, with absolute URLs, in `<head>`, one per page.
  - Internal links point to the canonical.
  - Same canonical across all methods (no conflicting signals).
  - For hreflang, the canonical must be in the same language.
  - HTTP header canonical for PDFs. Use either HTML or the header, not both.
  - Mobile m-dot: desktop page gets `<link rel="alternate" media="only screen and (max-width: 640px)" href="m-url">`, and the mobile page gets a canonical pointing to desktop.
- Don't:
  - Use robots.txt or the URL removal tool for canonicalization.
  - Use noindex to pick a canonical.
  - Make a fragment URL the canonical.
  - Put the canonical on attributes like hreflang or media links.
- HTTPS preference can fail when certificates are invalid, pages have insecure dependencies, HTTPS redirects to HTTP, or HTTP URLs appear in the sitemap or hreflang.

## 5. Redirects
- **Permanent** (target shown in results): 301, 308, meta refresh 0s, JS `location` (last resort). Use them only when the move won't be reverted.
- **Temporary** (source stays in results): 302, 303, 307, delayed meta refresh.
- Prefer server-side redirects (Apache `Redirect permanent`, nginx `return 301`, PHP `header()`).
- Google follows up to 10 hops, but aim for direct redirects (fewer than 3).
- Redirecting many URLs to an irrelevant page such as the homepage is treated as a soft 404.
- Keep redirects at least 1 year after a move, ideally forever. 3xx redirects don't lose PageRank.

## 6. HTTP status codes
- **2xx**: content is considered for indexing (not guaranteed). An error page served with 200 is a **soft 404**. Fix it by returning 404/410 or noindex.
- **3xx**: 301/308 are strong signals, 302/303/307 are weak. 304 means unchanged.
- **4xx** (except 429): treated as "doesn't exist". Indexed URLs are dropped and crawl frequency drops. Use 410 for permanently gone. **Don't use 401/403 to slow crawling.**
- **5xx and 429**: crawling slows temporarily, and persistent errors drop URLs from the index. Recovery is gradual after 2xx returns.
- DNS or network errors are treated like 5xx.

## 7. Sitemaps
- **Needed when**:
  - The site is large.
  - The site is new with few external links.
  - There is lots of rich media, or the site is in Google News.
- **Probably not needed**: around 500 pages or fewer, well linked internally, with little media.
- Formats: XML (supports image, video, news, and hreflang extensions), RSS/mRSS/Atom, text (one URL per line).
- Limits: **50MB uncompressed or 50,000 URLs** per file. Use a sitemap index for more. UTF-8, absolute URLs, entity-escaped.
- Include only canonical URLs you want indexed.
- `<lastmod>` is used only if consistently accurate. Update it for significant changes, not a copyright year. **`<priority>` and `<changefreq>` are ignored.**
- Location: a sitemap affects only URLs under its directory unless submitted via Search Console. Put it at the root.
- Submit through the Search Console Sitemaps report, the API, a `Sitemap:` line in robots.txt, or WebSub for feeds.
- Cross-site sitemaps are allowed when all sites are verified.
- Extensions:
  - Image sitemap: helps with images loaded oddly or hosted on a CDN.
  - Video sitemap: `<video:thumbnail_loc>`, `<video:content_loc>` or `<video:player_loc>`, `<video:family_friendly>`, `<video:restriction>`, `<video:expiration_date>`.
  - News sitemap: title and publication date.

## 8. URL structure & faceted navigation
- Follow IETF STD 66 and percent-encode reserved and non-ASCII characters in `href`.
- **Hyphens, not underscores.** Use readable words, the audience's language, and few parameters.
- Parameters: `?key=value&key2=value2`. Multiple values as `color=red,blue`. Avoid `:`, `[]`, double commas, and repeated keys.
- **No fragments (`#`) for changing content.** Use the History API.
- URLs are case-sensitive. Normalize case if the server treats cases the same.
- URL explosions to watch for:
  - Additive filters.
  - Irrelevant params (session IDs, referral, sort). Prefer cookies over session IDs in URLs.
  - Infinite calendars: nofollow future-date links.
  - Broken relative links creating infinite paths: use root-relative URLs.
- Faceted navigation:
  - **If facets don't need indexing**: disallow them in robots.txt, or put filter state in `#`.
  - **If they do**: use `&` as separator, keep filter order consistent, prevent duplicate filters, and **return 404** for empty, nonsensical, or out-of-range combinations. Don't redirect those to a generic page.
  - Canonical or nofollow on facets are weaker long-term controls.

## 9. Links
- Crawlable links are `<a href="real-url">`. Relative and absolute URLs are fine, and extra attributes are fine.
- Not crawlable: `<a routerLink>`, `<span href>`, `<a onclick>` without href, `href="javascript:"`. JS-inserted `<a href>` is fine after rendering.
- Anchor text:
  - Descriptive, concise, relevant. Avoid "click here" and "read more", and avoid chaining adjacent links.
  - Image links use the image's alt text as anchor.
  - Empty anchors fall back to the `title` attribute.
- Every important page needs at least one internal link. There's no ideal number of links per page.
- Rel qualifiers:
  - `rel="sponsored"` for paid or affiliate links.
  - `rel="ugc"` for user-generated links.
  - `rel="nofollow"` for others you don't vouch for.
  - Combine as `"ugc nofollow"`.
  - For internal pages you don't want crawled, use robots.txt rather than nofollow.

## 10. JavaScript SEO
- Pipeline: crawl, then render (evergreen Chromium WRS), then index. Pages returning 200 are queued for rendering unless noindexed.
- Server-side rendering or pre-rendering is still recommended (faster, and works for all bots).
- Rules:
  - Unique titles and meta descriptions (JS may set them).
  - Canonical in the initial HTML, with the same value if JS sets it, and only one.
  - Links as `<a href>`.
  - History API routing, not `#/route`.
  - Meaningful status codes. SPA soft-404 fix: JS-redirect to a URL that returns 404, or inject `<meta name="robots" content="noindex">` on error views.
  - Feature-detect and polyfill.
  - Content fingerprinting (`main.2bb85551.js`), because WRS may ignore cache headers.
  - JSON-LD may be injected by JS. Test it.
  - Web components: shadow and light DOM are flattened. Use `<slot>` so light DOM renders.
- WRS **does not persist** localStorage, sessionStorage, or cookies across loads. It **declines permission prompts** (camera, geolocation). It doesn't support **WebGL, WebSockets, or WebRTC**, so provide fallbacks.
- JS paywalls: don't ship the full content and hide it with JS. Serve it only after the entitlement check, and use paywall structured data.
- **Lazy loading**:
  - Load on viewport entry (`loading="lazy"`, IntersectionObserver). Never require scroll, click, or typing.
  - Don't lazy-load above-the-fold content.
- **Infinite scroll**: each chunk gets a persistent unique URL (`?page=12`, not `?date=yesterday`), sequential `<a href>` links between pages, and History API URL updates.
- Debug with URL Inspection (rendered HTML, console, resources) or the Rich Results Test.

## 11. Mobile-first indexing
- Google indexes the **mobile** version with a smartphone crawler. **Responsive design is recommended.** Dynamic serving needs `Vary: User-Agent`.
- Parity between mobile and desktop:
  - Same primary content (accordions and tabs are fine), same headings.
  - Same structured data (with mobile URLs inside it), same title and meta description.
  - Same robots meta, same image alt text and captions, same video markup.
- Don't block mobile resources. Don't lazy-load primary content behind interaction.
- Ads follow the Better Ads Standard. Big top-of-page mobile ads hurt.
- Images and video:
  - Use stable URLs, not URLs that change on each load.
  - Images inside inline SVG `<image>` tags aren't indexed.
  - Videos must be easy to find on mobile.
- Separate m-dot sites:
  - Same error statuses on both versions, no fragment URLs.
  - Don't redirect all desktop pages to the mobile home.
  - hreflang links mobile-to-mobile and desktop-to-desktop.
  - Verify both versions in Search Console. Make sure the mobile host has capacity for crawling.

## 12. Page metadata
- Valid `<head>` elements: `title`, `meta`, `link`, `script`, `style`, `base`, `noscript`, `template`. **Any invalid element (e.g. `img`, `iframe`) ends the head for Google**, so metadata after it is ignored.
- Supported meta tags:
  - `description`, `robots`/`googlebot`.
  - `<meta name="googlebot" content="notranslate">`, `<meta name="google" content="nopagereadaloud">`.
  - `google-site-verification` (exact-case match).
  - Charset (UTF-8 recommended) and `viewport`.
  - `rating` (`adult` or the RTA label).
  - Meta refresh (avoid it, use 301).
- Ignored: `meta keywords`, `lang` attribute (language is detected from content), `rel=next/prev`.
- Avoid injecting or altering meta tags with JS. If you must, test.

## 13. Crawl budget (only for big sites)
- Relevant for 1M+ pages changing weekly, 10k+ pages changing daily, or many "Discovered – currently not indexed".
- Crawl budget is per hostname: crawl capacity (server health, speed, 5xx/429) plus crawl demand (inventory, popularity, staleness).
- Do:
  - Consolidate duplicates.
  - Block unimportant URL spaces with robots.txt.
  - Return 404/410 for removed pages and eliminate soft 404s.
  - Keep sitemaps fresh with `<lastmod>`.
  - Avoid redirect chains.
  - Speed up responses and support 304.
- Don't:
  - Use noindex to save budget (the URL is still fetched).
  - Toggle robots.txt to reallocate budget temporarily.
- "Hostload exceeded" in URL Inspection means add server capacity.

## 14. Recrawl requests
- **Few URLs**: URL Inspection, then Request indexing. There's a quota, and repeating doesn't speed it up.
- **Many URLs**: submit or update a sitemap.
- Crawling takes days to weeks and is never guaranteed.

## 15. Removals & redaction
- Ways to keep content out of Search:
  - Delete it (best).
  - Password-protect it.
  - `noindex`.
  - robots.txt (media only).
  - nosnippet / data-nosnippet.
  - The Search Console "Search generative AI" control (AI Overviews and AI Mode).
  - Property opt-outs (e.g. Shopping).
- **Removals tool**: hides within about a day but lasts **about 6 months**. Make it permanent by deleting, password-protecting, or noindexing. Don't rely on robots.txt for removal. Cover URL variants (case, params).
- Images:
  - Use robots.txt with `User-agent: Googlebot-Image` (`Disallow: /images/x.jpg`, `Disallow: /*.gif$`), **or** `X-Robots-Tag: noindex` on the image URL. Not both, because the header needs the URL crawlable.
  - `noimageindex` covers only that page's embeds.
- Redaction:
  - Black boxes, tiny or same-color text, and overlaying images don't redact. OCR and screen readers see through them.
  - Strip metadata and revision history, crop before embedding, flatten to PNG/WebP, and use real redaction tools.
  - Don't put names or emails in URLs.
  - If something leaks: delete, use the Removals tool (prefix), republish a redacted version at a new URL, and ask other hosts to remove copies.

## 16. Site moves, A/B tests, pausing
**Move with URL changes** (HTTPS migration, domain change, path change):
- Planning:
  - Change one thing at a time. Move a test section first on large sites. Pick a low-traffic period.
  - Expect weeks of fluctuation (longer for large sites).
- Preparation:
  - Set up the new site: TLS, robots.txt live version, remove dev noindex.
  - Return 404/410 for dropped content.
  - Verify all variants in Search Console. Re-upload the disavow file. Check a purchased domain for manual actions and old removals.
  - Make sure the server can handle heavier crawling.
- URL map, old to new:
  - Sources: sitemaps, analytics, logs, Links report, CMS.
  - Include images, JS, and CSS.
  - New pages get self-canonicals. Update hreflang and internal links.
- Launch:
  - 301/308 server-side, avoid chains, never mass-redirect to the homepage.
  - Test the redirects.
  - **Change of Address tool** only for domain or subdomain moves (not for HTTP→HTTPS or path changes).
  - Submit the new sitemap.
  - Update external links, profiles, and ads.
  - Keep redirects 1 year or more.
- Monitor:
  - Sitemaps and Page Indexing reports, crawl errors, logs.
  - Traffic should shift from old to new.
  - Common mistakes: leftover noindex or robots blocks, redirects to 404s, stale sitemaps, under-capacity servers.

**Move without URL changes** (hosting or CDN):
- Lower DNS TTL a week before.
- Test the new infrastructure (noindex on any temp hostname). Make sure the firewall or DoS protection doesn't block Googlebot.
- Remove temp blocks, then switch DNS.
- Crawl rate dips, then recovers. Shut down the old host when its logs show zero traffic.

**A/B tests**:
- No cloaking. Googlebot gets what users get. Cookie-based tests show Googlebot the no-cookie version.
- Variant URLs get `rel=canonical` to the original (not noindex). Use **302** redirects.
- End tests promptly.

**Pausing a business**:
- Keep the site up and limit functionality:
  - Disable the cart.
  - Show a banner with `data-nosnippet`.
  - Update structured data (availability, events cancelled, LocalBusiness hours) and Merchant Center.
- Full shutdown only for 1–2 days: **503 + Retry-After**. Never 503 robots.txt.
- Longer closures: a 200 placeholder home page.
- Don't use 403/404/410, noindex, robots.txt disallow-all, or the Removals tool for closures.

## 17. AMP
- AMP pages are indexed like any page. They must be valid AMP with content and actions equivalent to the canonical, and an understandable URL.
- AMP has no special desktop Search features. Responsive design is the recommendation.

## 18. Verifying Googlebot
- **Manual**: reverse DNS on the IP (`host 66.249.66.1`) must end in `googlebot.com`, `google.com`, or `googleusercontent.com`. A forward lookup must return the same IP.
- **Automated**: match against Google's published IP JSON lists (common-crawlers, special-crawlers, user-triggered-fetchers).
- Use this to whitelist Googlebot past age gates, firewalls, or paywalls safely.
