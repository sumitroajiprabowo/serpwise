# Ranking & search appearance

Source: developers.google.com/search/docs/appearance/*

## Contents
1. Anatomy of a result
2. Title links
3. Snippets & meta descriptions
4. Images
5. Video
6. Favicon
7. Site names
8. Sitelinks, featured snippets, byline dates
9. Discover
10. Page experience & Core Web Vitals
11. Interstitials
12. Ranking systems
13. AI features (AI Overviews / AI Mode) and generative AI search
14. Other features (business details, preferred sources, search profiles, translated results, top places, flexible sampling, Web Stories, regional features)

## 1. Anatomy of a result
- A text result has these parts:
  - Attribution: favicon, site name, visible URL and breadcrumb.
  - Title link.
  - Snippet.
  - Byline date.
  - Sitelinks.
  - Text-result image.
  - Rich attributes (stars, price), usually from structured data.
- Other result types: image result, video result (thumbnail, title, attribution, upload date), and exploration features ("People also ask", related searches). You can't control exploration features, but they're good topic ideas.

## 2. Title links
Sources Google uses:
- `<title>`
- The main visible title or `<h1>`
- Other headings and prominent text
- `og:title`
- Anchor text of links pointing to the page
- `WebSite` structured data (on the home page)

Best practices:
- Every page has a `<title>` that is descriptive and concise. Avoid "Home" or "Untitled". Long titles get truncated, and there's no hard limit.
- No keyword stuffing. No boilerplate repeated across pages (e.g. every page titled "Cheap products for sale"). Generate titles from page-specific data.
- Brand concisely: the site name on the home page, and on other pages at the start or end with a separator (`-`, `:`, `|`).
- Make the main title the most prominent element (a single clear `<h1>`).
- Match the content's language and script.
- robots.txt doesn't prevent a title from being shown. Use noindex to keep the page out.

Common issues Google rewrites:
- Half-empty titles ("| Site Name")
- Obsolete years
- Inaccurate titles
- Micro-boilerplate that differs only by a number
- No clear main title
- Language mismatch
- Duplicated site name

## 3. Snippets & meta descriptions
- Snippets come mostly from page content, tailored to each query. The meta description is used when it describes the page better.
- Controls: `nosnippet`, `max-snippet:N`, `data-nosnippet`.
- Meta description:
  - Unique per page. Site-level descriptions are fine for the home page and aggregation pages.
  - Include concrete facts (price, author, date, specs). Avoid keyword lists and one-word descriptions ("Mechanical pencil").
  - Describe the whole page.
  - Programmatic generation is fine for large database sites if the output is human-readable and varied.
- No length limit. Snippets are truncated to fit the device width, so put the most useful facts first. (Fixed character targets such as "150–160" are SEO folklore, not Google guidance.)
- "Read more" deep links work best when content is visible without tabs or accordions and the page doesn't force a scroll position.

## 4. Images
**Discovery**
- Use `<img src>`. **CSS background images aren't indexed.** `<picture>` and `srcset` need an `<img>` fallback.
- Image sitemap for images Google might miss. CDN URLs are allowed (verify the CDN domain).
- Formats: BMP, GIF, JPEG, PNG, WebP, SVG, AVIF. The extension should match the type.
- Use high-quality, fast images (check with PageSpeed Insights). Data URIs bloat HTML.

**Landing page**
- Preferred image: `primaryImageOfPage`, or `image` on the main entity, or `og:image`. It should be relevant, not a logo, not text-heavy, not an extreme aspect ratio, and high resolution.
- Descriptive filenames (`kucing-hitam-anggora.jpg`, not `IMG00023.JPG`), localized.
- **Alt text is the most important image attribute.** Describe the image in context, without stuffing. Bad → good: missing alt → `alt="puppy"` → `alt="Dalmatian puppy playing fetch"`. Inline SVG uses `<title>`.
- Place images near relevant text. Reuse the same URL for the same image across pages.
- Structured data with `image` enables badges in Google Images.
- Opt-outs:
  - Inline linking: when the referrer is a Google domain, return 200 or 204 with no body. This is not cloaking.
  - Full removal: see crawling-indexing.md §15.

## 5. Video
**Making videos findable**
- Embed with `<video>`, `<embed>`, `<iframe>`, or `<object>`.
- Don't load videos via fragments or after a user interaction.
- JS-injected players must appear in the rendered HTML.

**Indexing requirements**
- The watch page is indexed. The video is the main purpose of a dedicated **watch page**, not hidden.
- There is a valid thumbnail at a stable URL (min 60×30 px, at least 80% of pixels with alpha above 250). The thumbnail isn't blocked.

**Formats and URLs**
- Formats: 3GP, 3G2, ASF, AVI, DivX, M2V, M3U, M3U8, M4V, MKV, MOV, MP4, MPEG, OGV, QVT, RAM, RM, VOB, WebM, WMV, XAP. No data URLs.
- Use stable URLs for both the video file and the thumbnail.
- Thumbnail sources: `poster`, sitemap `thumbnail_loc`, `thumbnailUrl`, `og:video:image`. Use the same URL everywhere.

**Metadata**
- VideoObject structured data, a video sitemap, or OGP. Give each video a unique name and description.
- Third-party players (YouTube etc.) still benefit from markup on your page.

**Features**
- Previews and key moments require letting Google fetch the file: `contentUrl`, and don't block the bytes.
- Key moments: `Clip` (all languages), `SeekToAction`, or YouTube timestamps. Opt out with nosnippet.
- LIVE badge: `BroadcastEvent`.
- Preview length: `max-video-preview`.

**Removal and restriction**
- Removal: 404, noindex, or `expires` / `video:expiration_date`.
- Country restriction: `regionsAllowed` / `ineligibleRegion`, or sitemap `<video:restriction>`.

**Monitoring**: Video indexing report, Video rich results report, Performance report filtered by Videos.

## 6. Favicon
- Add `<link rel="icon" href="/favicon.ico">` (also `apple-touch-icon`) on the **home page**. One per hostname, and subdirectories can't have their own.
- Square, at least 8×8 (use **48×48 or larger**). Formats: ICO, PNG, SVG-capable formats, GIF, JPEG, BMP, TIFF, PPM. Use a stable URL.
- Googlebot and Googlebot-Image must be able to crawl the home page and the icon.
- It should visually represent the brand. Inappropriate icons are replaced.

## 7. Site names
- Signals:
  - `WebSite` structured data on the **home page** (strongest).
  - Also `og:site_name`, `<title>`, headings, and prominent home-page text, used consistently.
- Required: `name`, `url`. Recommended: `alternateName` (a list, in preference order).
- One name per domain or subdomain. Subdirectories aren't supported, and www and m count as the root.
- Duplicate home pages (http/https, www/non-www) must carry the same data.
- Nest the name inside existing WebSite markup rather than adding a second block.
- Name it concisely and recognizably ("Google", not "Google, Inc."). Avoid generic names ("Best Dentists In Iowa").
- If your preferred name isn't shown:
  1. Fix markup errors and make sure all home-page sources are consistent.
  2. Check redirects and crawlability.
  3. Add `alternateName`.
  4. Last resort: use the lowercase domain as `name` or as the last `alternateName`.
- Validate with the Schema Markup Validator. The Rich Results Test doesn't support site names.

```json
{"@context":"https://schema.org","@type":"WebSite","name":"Example Company","alternateName":["EC","example.com"],"url":"https://example.com/"}
```

## 8. Sitelinks, featured snippets, byline dates
- **Sitelinks**:
  - Fully automatic.
  - Help them with clear titles and headings, a logical structure, important pages linked from relevant pages, concise internal anchors, and no repetition.
  - To remove one, delete the page or noindex it.
- **Featured snippets**:
  - Can't be requested. Answer questions clearly in a well-structured way.
  - Opt out with `nosnippet` or `data-nosnippet` on specific text. Lowering `max-snippet` reduces the chance but doesn't guarantee it.
- **Byline dates**:
  - Show a visible, labeled date ("Diterbitkan", "Diperbarui").
  - Use `datePublished` / `dateModified` in Article, BlogPosting, or VideoObject. ISO 8601 with time and the correct timezone.
  - Visible and structured dates must match. No future dates, and no event dates as publish dates.
  - If Google picks the wrong date, remove other confusing dates from the page.

## 9. Google Discover
- Eligibility: indexed and meeting Discover content policies. No special markup is needed.
- Content: timely, strong storytelling, unique insights. Titles capture the essence. **No clickbait**, misleading previews, withheld key information, or sensationalism.
- Images: at least **1200px wide**, over 300k pixels, 16:9. Enable with `max-image-preview:large` (or AMP). Set via `og:image` or schema primary image. Avoid logos and text-heavy images.
- Filtered out: forms, job applications, petitions, code repositories, satire without context. SafeSearch applies.
- Traffic is volatile, so treat it as supplemental. Use the Discover performance report (16 months, impression threshold).

## 10. Page experience & Core Web Vitals
- **LCP ≤ 2.5s, INP < 200ms, CLS < 0.1** (75th percentile of field data). Measure with the Search Console CWV report, PageSpeed Insights, CrUX, and Lighthouse.
- CWV is used by ranking systems. Still, **don't chase perfect scores**: relevance wins, and a good experience helps mostly as a tiebreaker among similarly helpful pages.
- Other aspects that help user satisfaction (not direct rank boosts):
  - HTTPS
  - Mobile-friendly display
  - No excessive ads
  - No intrusive interstitials
  - Main content clearly distinguishable
- Page experience is evaluated mostly per page, with some site-wide assessment.

## 11. Intrusive interstitials
- Avoid full-page overlays and dialogs covering content, including app-install prompts. Use small banners (Smart App Banner, HTML banners).
- Don't redirect users to a separate consent page.
- Legal interstitials (cookie consent, age gates) are OK. Overlay the content (so some is indexable) and let verified Googlebot through age gates.

## 12. Ranking systems (what Google actually uses)
- **Language understanding**: BERT, RankBrain, neural matching, passage ranking. MUM is only for special applications.
- **Freshness**: "query deserves freshness" for timely queries.
- **Link analysis**: PageRank, one of many signals.
- **Dedup and originality**:
  - Deduplication: a featured snippet page isn't repeated on page 1.
  - Original content: canonical markup helps.
- **Quality and trust**:
  - Reviews system: rewards insightful, original, expert reviews.
  - Reliable information: advisories when confidence is low.
  - Spam detection: SpamBrain.
  - Removal-based demotion: many valid legal or personal-info removals demote a site.
- **Special situations**: crisis information, local news.
- **Result mix**:
  - Site diversity: usually at most 2 results per site in the top results, and subdomains count as the same site.
  - Exact-match domain: limited credit for keywords in the domain.
- **Retired** (folded into core): Helpful Content system (March 2024), Panda, Penguin, Hummingbird.
- Ranking is page-level with some site-wide signals.

## 13. AI features (AI Overviews, AI Mode) and generative AI search
Sources: /appearance/ai-features and /fundamentals/ai-optimization-guide.

How they work:
- AI features ground their answers in the regular Search index (retrieval-augmented generation). Optimizing for them is still SEO. "AEO" and "GEO" are other names for the same work.
- **Query fan-out**: the model runs several related searches at once (e.g. "lawn full of weeds" also searches herbicides, chemical-free removal, prevention), so a wider set of pages can be linked than in classic results.
- AI Overviews show only when Google judges them useful on top of classic results, so many queries don't trigger one. AI Mode is for complex, multi-step questions.

Eligibility:
- **No extra requirements or special optimization.** The page must be indexed and eligible to show a snippet. Indexing and display are never guaranteed.
- The site must be included in "Search generative AI features" in Search Console to be shown in them.

What helps (ordinary SEO):
- **Non-commodity content**: first-hand experience and a point of view that generic "7 tips" pages don't have. Google ranks this above everything else in the guide.
- Clear paragraphs, sections and headings, written for people.
- Images and video that support the text (follow §4 and §5).
- Crawlable, indexable pages (robots.txt and CDN allow Googlebot), internal links, JavaScript SEO, few duplicates, good page experience with main content clearly separated.
- Important content as text, and structured data that matches the visible text.
- Current Merchant Center feeds and Business Profile for products and local businesses.
- Semantic HTML helps accessibility but isn't required. Don't chase perfect code.

What not to do (Google's own myth list):
- **llms.txt, AI text files, Markdown copies or special markup**: Google Search doesn't use them. Making them for other services neither helps nor hurts.
- **Chunking** content into small pieces: not needed. One page can cover several topics, and there is no ideal length.
- **Rewriting for AI** or chasing every long-tail variant: AI systems understand synonyms and meaning.
- **One page per fan-out query or query variant**: that is scaled content abuse (spam-policies.md). More pages don't make a site better.
- **Inauthentic "mentions"** planted around the web: core ranking focuses on content quality, and other systems catch spam.
- **Over-focusing on structured data**: it isn't required for AI features and there is no special schema for them. It is still worth having for rich results.

Measurement:
- AI Overviews and AI Mode clicks are counted in the Performance report under the "Web" search type. Google says these clicks tend to be higher quality (more time on site).
- The Search Console generative AI performance report shows visibility in generative AI features and Discover.
- Be wary of third-party tools that claim to see Google's AI rankings. None has that access.

Controls:
- `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`. Changes can take days to months to apply after recrawl. Check with URL Inspection and request a recrawl.
- robots.txt for Googlebot is the access control for Search, including AI features.
- `Google-Extended` limits use for Gemini training and grounding in other Google AI products. It doesn't affect Search inclusion or ranking.

Agents:
- Browser agents may read screenshots, the DOM and the accessibility tree to complete tasks, so accessible, well-labelled pages help them too.
- Emerging protocols such as the Universal Commerce Protocol (UCP) and the Business Agent conversational experience are early. Watch Google's announcements instead of building for them speculatively.

## 14. Other features
- **Business details**:
  - Claim a Google Business Profile (address, hours, photos for Maps and the knowledge panel).
  - Use Organization markup with `logo`, plus Breadcrumb.
  - Allow about a week after crawl before using the knowledge panel feedback link.
- **Preferred sources**:
  - Users can mark your site as preferred, which gives more Top Stories presence and a badge (also in AI Mode/Overviews).
  - Domain or subdomain level only, not subdirectories.
  - Optional button: `publisher.js` script plus a `div[google-add-preferred-source-btn]`, or a deeplink to the source preferences tool.
- **Search profiles**:
  - A claimed profile helps linked content in Discover.
  - Badge links to `profile.google.com/@handle`, with `aria-label="Find us on Google Search"`.
  - Touch target at least 48dp (Android) or 44px (iOS/web). Don't alter the G logo.
- **Translated results**: Google may machine-translate titles and snippets (for a growing set of languages). Opt out with `notranslate`.
- **Top places list** (for physical businesses): third-party lists must be curated, genuine, independent, not sponsored, not templated, and not offensive.
- **Flexible sampling** (paywalls):
  - Prefer monthly metering, around 6–10 free articles per month (start at 10), or a lead-in of the first few sentences.
  - User satisfaction drops if the paywall shows on more than 10% of visits.
  - Use paywalled-content structured data so it isn't treated as cloaking.
- **Web Stories**:
  - Valid AMP.
  - Required metadata: `publisher-logo-src`, `poster-portrait-src`, `title`, `publisher`.
  - Self-canonical, linked or in the sitemap, not noindexed or blocked.
- **Regional features**: aggregator units and structured-data carousels in the EEA, Türkiye, and South Africa.
