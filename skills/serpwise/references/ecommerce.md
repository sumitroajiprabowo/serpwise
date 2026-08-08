# Ecommerce SEO

Source: developers.google.com/search/docs/specialty/ecommerce/*

## Contents
1. Where products can appear
2. Product data: structured data + Merchant Center
3. Structured data set for stores
4. Launching a new store
5. Content that serves shoppers & high-quality reviews
6. URL design & variants
7. Site structure & internal linking
8. Pagination, load more, infinite scroll
9. Faceted navigation
10. Pausing sales / out of stock

## 1. Where products can appear
| Surface | What you need |
|---|---|
| Google Search (text and rich results) | SEO basics + Product structured data |
| Google Images | Image SEO + Product markup (badges) |
| Google Lens | Merchant Center products + good images |
| Shopping tab | **Merchant Center required** |
| Business Profile | Claim it and link it to Merchant Center |
| Google Maps (local inventory) | Merchant Center with local inventory data |

Results vary by country and device.

## 2. Product data: use both channels
**Product structured data on product pages**
- Not required for Search, but it gives rich-result eligibility (price, availability, rating, shipping, returns).
- Helps Google understand price, discounts, and shipping, and lets Merchant Center verify feeds.
- Put it in the initial HTML. `data-nosnippet` keeps specific elements out of snippets.

**Merchant Center feed**
- Required for the Shopping tab.
- Ensures every product is known, gives control over update frequency, and can carry data not on the site (store inventory).
- Small or static stores: automated feeds built from crawled pages (good markup helps).
- Large or fast-changing stores: scheduled feed uploads, or the Content API for near-instant stock and price updates.

**Fix lag mismatches**: enable Merchant Center **automatic item updates** so price and availability follow the website.

## 3. Structured data set for stores
- `Organization` / `OnlineStore` (logo, contacts, return and shipping policies, identifiers) on the home or About page.
- `Product`, `ProductGroup`, and variants on product pages (merchant listing). See structured-data.md.
- `BreadcrumbList` on category and product pages.
- `LocalBusiness` for physical stores: hours, location. Also use Business Profile and Merchant Center store codes.
- `Review` / `AggregateRating` (no self-serving or aggregated third-party ratings).
- `VideoObject` for product videos and livestreams.
- `MerchantReturnPolicy`, `ShippingService`, `MemberProgram` (nested under Organization).
- Many platforms (Shopify, WooCommerce) add markup via apps or plugins. Verify the output with the Rich Results Test.

## 4. Launching a new store
Steps:
1. Verify the site in Search Console.
2. Get it indexed: URL Inspection for a few URLs, a sitemap for many.
3. Watch the Page Indexing report.
4. Set up Business Profile if there's a physical store.
5. Sign up for Merchant Center.

Make sure the site is indexed and purchasable so Merchant Center verification doesn't warn.

Launch strategies:
| Strategy | How | Pro | Con |
|---|---|---|---|
| Grand reveal | Password-protect until launch day, then run all steps | Total secrecy | Slow to show up |
| Home page first | Public "coming soon" home page, verify early | Brand name searchable early, links accrue | Product details come later |
| Launch without availability | Full site live, products out of stock, feed with `excluded_destination` | Indexed at launch | Looks live but can't buy, so say so clearly |
| Soft launch | Go live quietly, marketing later | Simple, real testing at low traffic | Might leak early |

**Don't disable add-to-cart to block sales.** Google may use it to verify the final price (tax and shipping).

## 5. Content that serves shoppers & high-quality reviews
- Content types:
  - Brand story.
  - Seasonal offers.
  - Informative product descriptions in shoppers' words, plus category descriptions for broader queries.
  - Customer reviews.
  - Buying guides and merchant reviews (affiliate links qualified).
  - Workshops and classes (Event markup), livestreams.
  - Clear shipping and return policies, visible support contacts.
- Writing reviews (Google's best practices):
  - Evaluate from the user's perspective and show expertise.
  - Give **evidence of first-hand use** (original photos, audio, video, links).
  - Share quantitative measurements.
  - Explain what sets the product apart, compare with alternatives, and say which suits which use case.
  - Give benefits and drawbacks based on original research.
  - Cover how it evolved from earlier models, and focus on the key decision factors.
  - Explain design choices beyond the manufacturer's claims.
  - Link useful resources, and consider linking multiple sellers.
  - Back "best" claims with first-hand evidence. Ranked lists should stand on their own.
  - Quality beats length. Thin affiliate copy is spam.

## 6. URL design & variants
- Problems to avoid:
  - Fragments for variants (`/t-shirt#black`), which Google ignores.
  - Several URLs returning the same page (`/product/black-t-shirt` and `/product?sku=1234`).
  - Infinite URLs from changing values (`?now=12:34`).
- Rules:
  - Minimize alternate URLs for the same content. Normalize case.
  - Unique URL per paginated page.
  - Descriptive paths (`/product/black-tee-white-collar`, not `/product/3243`).
  - Parameters as `?key=value`. Don't repeat a key (`?type=a,b`).
  - Don't link to temporary params (session IDs, tracking codes, `location=nearby`, timestamps). Use persistent equivalents (`?location=ID`).
- Variants:
  - Each variant has its own URL: a path (`/tee/green`) or a param (`/tee?color=green`).
  - If an optional param selects the variant, the parameter-less URL is canonical.
  - Mark up ProductGroup with `hasVariant` and `variesBy` (structured-data.md). Merchant Center: `canonical_link`.
- Consistency:
  - Use the exact same URL form in internal links, sitemaps, and canonicals (e.g. always omit `?page=1`).
  - Self-canonical on indexable pages, and list them in the sitemap.
  - Use `<a href>` with meaningful anchors (product title).
- Empty categories: `noindex`, or 404 if the category was auto-removed.

## 7. Site structure & internal linking
- Make everything reachable by links: menu, then category, then subcategory, then **every** product.
- Googlebot doesn't use your on-site search box, so products reachable only through it may never be found.
- If you can't link everything, use a sitemap or Merchant Center feed.
- Link depth and count signal importance. Link bestsellers from the home page, blog posts, and newsletters. Google relies on link analysis more than URL hierarchy.
- Navigation uses `<a href>`, not JS click handlers.

## 8. Pagination, load more, infinite scroll
- UX patterns:
  - Pagination: shows size and position, needs more clicks.
  - Load more: single page, struggles with huge sets.
  - Infinite scroll: intuitive, but scroll fatigue and no sense of size.
- Google crawls only `<a href>`. It doesn't click "load more" or trigger scroll events.
- Implementation:
  - Link page *n* to page *n+1* with `<a href>`. Optionally link all pages back to page 1.
  - Unique URL per page (`?page=n`). **Each page canonicalizes to itself, not to page 1.**
  - No `#` page numbers.
  - Paginated pages don't need unique titles or descriptions.
  - `rel=next/prev` is not used by Google.
  - Consider preload, prefetch, or preconnect for the next page.
- For load more or infinite scroll, also provide paginated URLs (crawling-indexing.md §10) plus a sitemap or feed.
- Keep sort and filter variants (`?order=price`) out of the index: noindex or a robots.txt pattern.

## 9. Faceted navigation
See crawling-indexing.md §8:
- Block unneeded facet URLs with robots.txt, or keep filter state in `#`.
- If facets should rank:
  - Use `&` separators and a consistent filter order, with no duplicate filters.
  - Return 404 for empty or nonsense combinations.
- Index only facet pages that match real search demand (e.g. "black men's running shoes"), and give them unique content and an internal link.

## 10. Pausing sales / out of stock
- Out-of-stock product: keep the page live and mark `availability: OutOfStock`. Don't remove it with the Removals tool.
- Temporary pause:
  - Disable the cart and show a `data-nosnippet` banner.
  - Update structured data and Merchant Center availability.
  - Don't take the site down. Use 503 only for a day or two (crawling-indexing.md §16).
