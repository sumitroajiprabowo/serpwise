<!-- Claude Code 2.1, same model, skills disabled. Prompt and input: skills/serpwise/evals/audit-broken-landing-page. Unedited output. -->

# SEO Audit: stridesupply.com homepage

**Date:** 2026-11-21
**Sources:** the local `index.html`, plus live HTTP and DNS checks of `stridesupply.com` run on the audit date.

## Summary

The page has two problems that each keep it out of Google on their own:

1. **The live domain doesn't serve this page.** Every version of `stridesupply.com` sends visitors with a temporary redirect (302) to a domain-for-sale listing on atom.com.
2. **The page tells Google not to index it.** `index.html` contains `<meta name="robots" content="noindex">`.

You need to fix both. Fixing either one alone won't get you indexed. Everything after that is about how well the page ranks once it is indexed.

---

## What the live checks found

| Request | Result |
|---|---|
| `https://www.stridesupply.com/` | `302` → `https://www.atom.com/name/StrideSupply` |
| `https://stridesupply.com/` | `302` → same atom.com listing |
| `http://www.stridesupply.com/` | `302` → same atom.com listing |
| `/robots.txt` | 404 page |
| `/sitemap.xml` | `404 Not Found` |
| `/en-gb/` (the hreflang target) | `404 Not Found` |
| Nameservers | `ns1.atom.com`, `ns2.atom.com` |
| A record | `52.20.84.62` |

The domain's DNS is still run by Atom, a domain marketplace, so Google has never seen your store. When Googlebot visits, it follows the redirect and finds a sale listing.

---

## Fix list, most important first

### P0: Blockers (the page can't be indexed until these are fixed)

#### 1. Point the domain at your store
- Check that you own the domain. If you bought it through Atom/Squadhelp, finish the transfer.
- At your registrar, change the nameservers (or the A/CNAME records) to your host or store platform (Shopify, Vercel, Netlify, your own server, and so on). Your host will tell you the exact records.
- Make sure `https://www.stridesupply.com/` returns **`200 OK`** with your HTML. Redirect the other versions (`http://`, the bare `stridesupply.com`) to it with a **301**, not a 302.
- Check with: `curl -I https://www.stridesupply.com/`

#### 2. Remove `noindex` (line 8)
```html
<!-- remove this -->
<meta name="robots" content="noindex, follow">
```
You don't need a robots tag at all, because indexing is the default. If you want to keep one, use `content="index, follow"`. Also make sure your host doesn't send an `X-Robots-Tag: noindex` HTTP header. Some staging setups add one.

#### 3. Move the `<img>` out of `<head>` (line 6)
An `<img>` is not allowed in `<head>`. When a browser or Google reaches it, the parser treats it as the end of `<head>`. Google says it stops reading head metadata at that point, so the description, canonical and hreflang tags after it may be ignored. Move the tracking pixel to just before `</body>`, or better, use your analytics tool's script.

---

### P1: High impact

#### 4. Add the mobile viewport tag and the `lang` attribute
Google indexes the mobile version of pages. Without a viewport tag, the page renders as a shrunk desktop page and fails mobile-friendliness checks.
```html
<html lang="en">
...
<meta name="viewport" content="width=device-width, initial-scale=1">
```

#### 5. Make the category link crawlable (line 19)
`<a onclick="go('/category/running')">` has no `href`, so Googlebot won't follow it and won't find your category page. Use:
```html
<a href="/category/running">Running Shoes</a>
```
Do the same for any product or category links created with JavaScript.

#### 6. Fix hreflang (lines 10–11)
- `hreflang="uk"` means **Ukrainian**, not the United Kingdom. Use `en-GB`.
- hreflang URLs must be absolute.
- `/en-gb/` currently returns 404. Remove that line until the page exists.
- Each version must link to every version, including itself, and the UK page must link back. Add `x-default`.
```html
<link rel="alternate" hreflang="en"        href="https://www.stridesupply.com/">
<link rel="alternate" hreflang="en-GB"     href="https://www.stridesupply.com/en-gb/">
<link rel="alternate" hreflang="x-default" href="https://www.stridesupply.com/">
```
If you only have one site version, delete all the hreflang tags.

#### 7. Write a real title tag (line 5)
"Home" gives Google nothing to rank you for and looks weak in results. Aim for 50–60 characters with your main keyword and brand:
```html
<title>Running Shoes for Men & Women | Stride Supply</title>
```

#### 8. Create robots.txt and an XML sitemap, then register with Google Search Console
- `/robots.txt`:
  ```
  User-agent: *
  Allow: /
  Sitemap: https://www.stridesupply.com/sitemap.xml
  ```
- `/sitemap.xml`: list the homepage, category pages and product pages. Most store platforms create this for you.
- In [Google Search Console](https://search.google.com/search-console), verify the domain, submit the sitemap and use **URL Inspection → Request indexing** on the homepage. URL Inspection also shows whether Google can now fetch the page and why it was excluded before. Do this right after fixes 1–3.

---

### P2: Medium impact

#### 9. Fix the JSON-LD structured data (lines 21–24)
JSON doesn't allow comments. The `// brand` comment makes the whole block invalid, so Google ignores it. Remove it and expand the block:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Stride Supply",
  "url": "https://www.stridesupply.com/",
  "logo": "https://www.stridesupply.com/img/logo.png",
  "sameAs": ["https://www.instagram.com/…", "https://www.facebook.com/…"]
}
</script>
```
Consider adding a `WebSite` block. Product pages should use `Product` markup with `Offer` (price, availability) for rich results and Google Shopping. Check the markup with Google's [Rich Results Test](https://search.google.com/test/rich-results).

#### 10. Write a useful meta description (line 7)
"Shoe store" is too short and generic. Write 140–160 characters that would make someone click:
```html
<meta name="description" content="Shop running shoes for men and women at Stride Supply. Top brands, free shipping over $50 and easy 30-day returns.">
```
(Replace the offers with your real ones.)

#### 11. Add real content to the page
Right now the page has one H1, two images and two links. Google has almost no text to judge what the page is about. Add:
- An intro paragraph on what you sell and who it's for.
- Featured categories and products with text names, prices and links.
- Trust signals: shipping, returns, reviews, contact details.
- H2 subheadings for each section.

Also make the H1 match what you actually sell. "The Best Running Shoes" is fine if running shoes are your main line. If you sell general footwear, broaden it.

#### 12. Add alt text and sizes to images (lines 17–18)
```html
<img src="/img/shoe-1.jpg" alt="Stride Supply men's lightweight road running shoe in blue" width="600" height="600" loading="lazy">
```
Alt text helps you show up in image search and helps accessibility. Setting `width`/`height` stops the layout jumping as images load (CLS).

#### 13. Make the hero image a real `<img>` (line 15)
Google doesn't index CSS background images, and they load late, which hurts LCP. Use an `<img>` with `alt`, `width`/`height` and `fetchpriority="high"`. Don't lazy-load this image, because it's at the top of the page.

---

### P3: Low impact / cleanup

#### 14. Use descriptive link text (line 20)
Replace "click here" with text that says where the link goes: `<a href="/sale">Shop the running shoe sale</a>`.

#### 15. Remove `meta keywords` (line 12)
Google ignores it, and it shows competitors which keywords you're targeting.

#### 16. Add social sharing tags
Add Open Graph and Twitter tags (`og:title`, `og:description`, `og:image`, `og:url`, `twitter:card`) so links shared on social media show a proper preview. This doesn't affect rankings directly.

#### 17. Keep the self-canonical (line 9)
The tag itself is correct. Once fix 3 is done, Google will actually read it.

---

## Corrected `<head>` for reference

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Running Shoes for Men & Women | Stride Supply</title>
  <meta name="description" content="Shop running shoes for men and women at Stride Supply. Top brands, free shipping over $50 and easy 30-day returns.">
  <link rel="canonical" href="https://www.stridesupply.com/">
  <!-- hreflang only once /en-gb/ exists and links back -->
  <meta property="og:title" content="Running Shoes for Men & Women | Stride Supply">
  <meta property="og:description" content="Shop running shoes at Stride Supply.">
  <meta property="og:image" content="https://www.stridesupply.com/img/og.jpg">
  <meta property="og:url" content="https://www.stridesupply.com/">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"Organization","name":"Stride Supply","url":"https://www.stridesupply.com/"}
  </script>
</head>
```

## After fixing: how to check it worked
1. `curl -I https://www.stridesupply.com/` returns `200` with no `X-Robots-Tag: noindex`.
2. View the page source: no `noindex`, and nothing but metadata inside `<head>`.
3. Search Console → URL Inspection → "Test live URL" says the page can be indexed. Then click "Request indexing".
4. Submit the sitemap. Indexing usually takes a few days to a couple of weeks.
5. Search Google for `site:stridesupply.com` to confirm the page is indexed.
