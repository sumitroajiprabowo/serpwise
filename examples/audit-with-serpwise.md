<!-- Claude Code 2.1, same model, serpwise installed. Prompt and input: skills/serpwise/evals/audit-broken-landing-page. Unedited output. -->

# SEO Audit: https://www.stridesupply.com/ (homepage, `index.html`)

*Audited 2026-11-21. I ran two checks: the bundled `serpwise` auditor on the local `index.html`, and a live check of the domain (HTTP, robots.txt, DNS).*

## Summary

**Your store isn't what's being served at www.stridesupply.com.** Every version of the domain (`https`/`http`, `www`/no-`www`) returns a **302 redirect to `https://www.atom.com/name/StrideSupply`**, which is a domain-marketplace listing. The domain's nameservers are `ns1.atom.com` / `ns2.atom.com`. When Googlebot visits, it never sees the `index.html` below. That alone explains why nothing shows up on Google.

Fixing DNS will expose a second blocker that was going to stop indexing anyway: the page contains `<meta name="robots" content="noindex">`. On top of that, an `<img>` placed inside `<head>` makes Google stop reading the head early, so the canonical, hreflang and robots tags are unreliable.

Fix the domain first, then the `<head>`. Then request indexing in Search Console. After that, the homepage can usually be indexed within days to a few weeks.

## Findings

| # | Severity | Issue | Evidence | Fix | Google rule |
|---|---|---|---|---|---|
| 1 | **Critical** | Domain doesn't serve your site. It 302-redirects to a domain-sale page | `curl -I https://www.stridesupply.com/` → `302 Location: https://www.atom.com/name/StrideSupply`. The same happens for `stridesupply.com` and both `http://` versions. NS = `ns1/ns2.atom.com`, A = `52.20.84.62` | Point the domain at your store host (see Details §1). Afterwards, every variant should return **200** at `https://www.stridesupply.com/` or **301** to it | Google indexes what it fetches. A redirect to another site isn't your page (Search Central: HTTP status codes & redirects) |
| 2 | **Critical** | `noindex` on the homepage | `index.html:8` `<meta name="robots" content="noindex, follow">` | Delete the line, or use `<meta name="robots" content="max-image-preview:large">` | `noindex` removes the page from Search results (Search Central: Block indexing with noindex) |
| 3 | **Critical** | Invalid `<img>` inside `<head>` | `index.html:6` `<img src="/tracking-pixel.gif">` comes before the description, robots, canonical and hreflang tags | Move the pixel into `<body>` (or load it via script) | Google stops parsing `<head>` at the first invalid element, so the robots, canonical and hreflang tags after it are ignored (Search Central: valid page metadata) |
| 4 | **Critical** | robots.txt returns a 404 HTML page | `https://www.stridesupply.com/robots.txt` → `HTTP 404`. Right now this comes from the domain parking host, not yours | Once DNS is fixed, serve a real `robots.txt` (sample below). A 404 is technically OK (it means "crawl everything"), but you want the `Sitemap:` line | robots.txt 4xx = no restrictions. Sitemaps can be declared in robots.txt (Search Central: robots.txt spec) |
| 5 | High | Main nav link is not crawlable | `index.html:19` `<a onclick="go('/category/running')">` has no `href` | `<a href="/category/running">Running shoes</a>` | Google only follows `<a href>` links (Search Central: Make links crawlable) |
| 6 | High | JSON-LD is invalid, so the Organization markup is ignored | `index.html:22` has a `// brand` comment. JSON doesn't allow comments, so the block fails to parse | Remove the comment (corrected block below) | Structured data must be valid to be used (Search Central: structured data general guidelines) |
| 7 | High | Title is "Home" | `index.html:5` | Use a descriptive title with the brand, e.g. `Stride Supply – Running Shoes for Men & Women` | Titles should be unique and describe the page (Search Central: title links) |
| 8 | High | Very thin content: about 52 characters of text in the raw HTML | One `<h1>`, two images, two links | Add real content: featured categories and products with names and prices, what makes the store different, shipping/returns info, and a link to the About page. If products load via JS, render them server-side | People-first, helpful content (Search Central: Creating helpful content). Content must be in the HTML Google renders (JavaScript SEO basics) |
| 9 | High | No viewport meta tag | Missing from `<head>` | `<meta name="viewport" content="width=device-width, initial-scale=1">` | Google uses mobile-first indexing (Search Central: mobile-first indexing) |
| 10 | High | Broken hreflang | `index.html:10` `hreflang="uk"` (`uk` = Ukrainian, not the United Kingdom) uses a relative URL `/en-gb/`. There's no `x-default`, and the `/en-gb/` page must link back | `en-GB` + absolute URL + `x-default` (below). If there is no real UK version, **remove the hreflang tags entirely** | hreflang uses an ISO 639-1 language code plus an optional ISO 3166-1 region, fully-qualified URLs, and reciprocal links (Search Central: localized versions) |
| 11 | Medium | Meta description is "Shoe store" | `index.html:7` | Write something specific, e.g. *"Shop running, trail and everyday shoes from top brands at Stride Supply. Free shipping over $X and 30-day returns."* (use your real terms) | Descriptions should summarize the page (Search Central: snippets) |
| 12 | Medium | Images have no alt text | `index.html:17-18` | `alt="Stride Supply Tempo 3 men's road running shoe, blue"` etc. | Alt text helps Google Images and accessibility (Search Central: image SEO) |
| 13 | Medium | No favicon | No `<link rel="icon">` | Add a square favicon of at least 48×48 px | Search Central: favicon in Search |
| 14 | Medium | No `WebSite` markup for the site name | Only Organization (currently invalid) | Add `WebSite` JSON-LD with `name` (below) | Search Central: site names |
| 15 | Low | Hero image is a CSS background | `index.html:15` | Use `<img src alt>` if the image matters | CSS background images aren't indexed (image SEO) |
| 16 | Low | "click here" anchor text | `index.html:20` | `<a href="/sale">Shop the sale</a>` | Descriptive anchor text (Search Central: link best practices) |
| 17 | Low | No `og:image` | Missing | Add a ≥1200 px wide representative image | Discover / social previews |
| 18 | Low | Meta keywords tag | `index.html:12` | Harmless, but Google ignores it, so don't spend time on it | Google doesn't use meta keywords |
| 19 | Low | No `lang` attribute | `<html>` | Add `<html lang="en">` for accessibility. Google itself detects language from visible content | — |

## Details by area

### 1. Crawling & indexing

**Root cause: the domain isn't connected to your store.** The nameservers belong to Atom (a domain marketplace), and the server responds with a redirect to `atom.com/name/StrideSupply`. Here are the likely situations and what to do in each:

- **You bought the domain through Atom/Squadhelp and the transfer or DNS setup never finished.** In your Atom account, finish the transfer to your registrar, or change the nameservers / DNS records to the ones your store host gives you. Shopify, for example, uses an A record to their IP plus a `www` CNAME. Use your host's exact values.
- **You never actually completed the purchase, or a lease/payment plan lapsed.** The domain is still listed for sale. Contact Atom to sort out ownership first.
- **Your store is live on a different domain, and this one was supposed to point to it.** Then it needs a **301** (not a 302) to the real URL, and that URL should be the one you audit and submit.

After the DNS change, check that `curl -I https://www.stridesupply.com/` returns `HTTP 200` and shows your store's HTML. Also check that `stridesupply.com` and `http://` versions return **301** to `https://www.stridesupply.com/`.

**`noindex` + invalid head.** These two interact. Because the `<img>` on line 6 ends the head for Google, the `noindex` on line 8 may be ignored right now, and so may the canonical and hreflang. If you only moved the pixel, you would suddenly *activate* the `noindex`. Fix both together.

**robots.txt / sitemap.** Once DNS is fixed, publish these at the root of the domain:

```
# https://www.stridesupply.com/robots.txt
User-agent: *
Disallow: /cart
Disallow: /checkout
Disallow: /account

Sitemap: https://www.stridesupply.com/sitemap.xml
```

Make sure `/sitemap.xml` exists and lists your canonical homepage, category and product URLs. Don't block CSS/JS.

**Links.** Google can't discover `/category/running`, because the only link to it uses `onclick`. Every category and product page needs a real `<a href>` from somewhere.

### 2. Content & relevance

As served, the homepage has almost no text and doesn't say who you are, what you sell or why someone should buy from you. Add:
- a short intro paragraph about the store;
- linked category tiles (Running, Trail, Men's, Women's, Sale);
- a featured-products grid with names, prices and links;
- trust info (shipping, returns, contact, About).

Avoid stuffing the page with "cheap shoes"-style keywords. Write for shoppers.

### 3. Search appearance: corrected `<head>` (ready to paste)

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Stride Supply – Running Shoes for Men &amp; Women</title>
  <meta name="description" content="Shop running, trail and everyday shoes at Stride Supply. Free shipping over $X and easy 30-day returns.">
  <meta name="robots" content="max-image-preview:large">
  <link rel="canonical" href="https://www.stridesupply.com/">
  <link rel="icon" href="/favicon.png" sizes="48x48" type="image/png">
  <meta property="og:title" content="Stride Supply – Running Shoes for Men &amp; Women">
  <meta property="og:image" content="https://www.stridesupply.com/img/og-home.jpg">

  <!-- Only if a real UK version exists at /en-gb/ that links back here: -->
  <link rel="alternate" hreflang="en-US" href="https://www.stridesupply.com/">
  <link rel="alternate" hreflang="en-GB" href="https://www.stridesupply.com/en-gb/">
  <link rel="alternate" hreflang="x-default" href="https://www.stridesupply.com/">

  <script type="application/ld+json">
  [
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "Stride Supply",
      "url": "https://www.stridesupply.com/",
      "logo": "https://www.stridesupply.com/img/logo.png"
    },
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "Stride Supply",
      "url": "https://www.stridesupply.com/"
    }
  ]
  </script>
</head>
<body>
  <img src="/tracking-pixel.gif" alt="" width="1" height="1">
  ...
  <a href="/category/running">Running shoes</a>
  <a href="/sale">Shop the sale</a>
```

Replace `$X`, the logo and the OG image path with real values. Use `en-US` or plain `en` depending on your main market.

### 4. Performance & page experience

I couldn't measure this, because the live URL doesn't serve your page. After launch, run PageSpeed Insights. Add `width`/`height` to images, and serve the hero image as an optimized `<img>` (this also helps LCP).

### 5. Ecommerce

- On product pages, add `Product` JSON-LD with `offers` (price, currency, availability). This is required for price and stock rich results.
- Connect **Google Merchant Center** for free product listings. That is often the fastest way for a new store to show up in Google Shopping results.

## Action plan

1. **Today:** fix the domain so `https://www.stridesupply.com/` serves your store with HTTP 200 (#1).
2. **Same deploy:** remove `noindex`, move the pixel out of `<head>`, and fix the JSON-LD, title, viewport, nav `href` and hreflang (#2, #3, #5–#10). Publish robots.txt and sitemap.xml (#4).
3. **Then:** verify the domain in Google Search Console, submit the sitemap, and use **URL Inspection → Request indexing** on the homepage.
4. **This month:** expand homepage content, add alt text, a meta description, a favicon and WebSite markup (#8, #11–#14). Set up Merchant Center and Product markup.
5. **Ongoing:** descriptive anchors, OG images, content for each category, and real promotion (social, partners, reviews) to earn links naturally.

## How to verify

- **Domain:** `curl -I https://www.stridesupply.com/` → `200` with your HTML. The non-www and http variants → `301` to it.
- **Search Console → URL Inspection** (live test): "URL is available to Google", indexing allowed (no `noindex` detected), user-declared canonical = `https://www.stridesupply.com/`. Under *View crawled page*, your products and links should appear in the rendered HTML.
- **Rich Results Test / Schema Markup Validator:** the Organization and WebSite blocks parse with no errors.
- **Page Indexing report:** the homepage moves to "Indexed" and the sitemap shows as "Success".
- **PageSpeed Insights:** mobile Core Web Vitals in the "Good" range.

**Not verified:** your store host's real response once DNS is fixed (status, `X-Robots-Tag` headers, robots.txt, sitemap), and any JavaScript-rendered content. Re-run this audit after the DNS change.

**Expectations:** once the site is reachable and indexable, Google can index the homepage within days. Rankings for competitive terms like "running shoes" take months and depend on content, products and reputation. Judge progress after a few weeks, not hours.
