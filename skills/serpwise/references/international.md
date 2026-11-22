# International & multilingual sites

Source: developers.google.com/search/docs/specialty/international/*

## Contents
1. Multilingual vs multi-regional
2. Language versions: rules
3. Locale URL structures
4. How Google determines the target locale
5. hreflang (HTML, HTTP header, sitemap)
6. Language/region codes & x-default
7. Duplicates across locales
8. Locale-adaptive pages
9. Don'ts & common mistakes

## 1. Multilingual vs multi-regional
- **Multilingual**: content in more than one language. Google matches the searcher's language.
- **Multi-regional**: targets different countries. Google picks the right locale page.
- A site can be both (e.g. Canada EN/FR plus US EN).

## 2. Language versions: rules
- **Separate URL per language.** Don't switch language with cookies, browser settings, or `Accept-Language` on one URL, because Googlebot may never see the variants. It usually crawls from the US without `Accept-Language`.
- One language per page for both content *and* navigation. Avoid side-by-side translations.
  - Translating only the template while user content stays in one language creates near-duplicates.
- Google detects language from **visible content**. It ignores `lang` attributes and URLs for detection (use them anyway for accessibility).
- **Don't auto-redirect by guessed language or IP.** Offer a visible language and region switcher (plain links) on every page.
- Localized words in URLs and IDNs are fine. Use UTF-8 and escape URLs properly in links.
- Link the versions with hreflang.

## 3. Locale URL structures
| Structure | Example | Pros | Cons |
|---|---|---|---|
| ccTLD | `example.de`, `example.fr` | Strongest geo signal, server location irrelevant, easy separation | Costly, availability limits, more infrastructure, some ccTLDs have strict requirements, one country each |
| Subdomain on gTLD | `id.example.com` | Easy, can host in different locations, easy separation | "id" is ambiguous (language or country?) |
| Subdirectory on gTLD | `example.com/de/` | Easy, low maintenance, one host | Weaker geo signal, single server location, harder to separate |
| URL parameter | `example.com?loc=de` | none | **Not recommended** |

Geotargeting a single country and language can boost that market at the expense of others. It is never exact, so always show region and language links.

## 4. How Google determines the target locale
- **ccTLD**: strong signal.
  - Vanity ccTLDs count as generic: `.ad .ai .as .bz .cc .cd .co .dj .fm .io .la .me .ms .nu .sc .sr .su .tv .tk .ws`. Regional `.eu` and `.asia` are generic too.
- **hreflang**: in HTML, headers, or sitemaps.
- **Server IP location**: weak, because CDNs blur it.
- **Other signals**: local addresses and phone numbers, local language and currency, links from local sites, Business Profile.
- **Ignored**: geo meta tags (`geo.position`, `ICBM`, `distribution`) and other geotargeting HTML attributes.
- Google does not vary crawler location to discover variants. Declare variants explicitly.

## 5. hreflang
hreflang tells Google that pages are localized variants of the same content, so the right one is served. It doesn't detect language and it isn't a canonical.

Use it for:
- Template-only translations (UGC sites).
- Same-language regional variants (en-US, en-GB, en-IE).
- Fully translated sites.

Rules for every method:
- Each version lists **itself and all other versions**.
- **Fully-qualified absolute URLs** (`https://example.com/de/`). No protocol-relative or relative URLs.
- Alternates can be on other domains.
- **Reciprocity required**: if page A points to B, B must point back to A, or the pair is ignored (this prevents hijacking).
- For partial sets that are hard to maintain, keep at least reciprocal pairs, and link new variants bidirectionally with the dominant version.
- Same-language regional variants should include a generic language fallback (`en`) and an `x-default`.
- Pick ONE method: HTML, header, or sitemap are equivalent, and using several adds no benefit.

**HTML** (in a valid `<head>`; don't combine hreflang with `media` in one tag):
```html
<link rel="alternate" hreflang="de" href="https://example.com/de/produkte" />
<link rel="alternate" hreflang="en" href="https://example.com/en/products" />
<link rel="alternate" hreflang="en-SG" href="https://example.com/sg/products" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

**HTTP header** (good for PDFs; identical on every variant):
```
Link: <https://example.com/file.pdf>; rel="alternate"; hreflang="en",
      <https://example.com/de/file.pdf>; rel="alternate"; hreflang="de",
      <https://example.com/de-ch/file.pdf>; rel="alternate"; hreflang="de-CH"
```

**Sitemap** (xhtml namespace; each `<url>` lists all variants including itself; sitemap scope rules apply):
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/de/produkte</loc>
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/produkte"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/en/products"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/"/>
  </url>
  <!-- repeat a <url> block for each variant with the same set of links -->
</urlset>
```

## 6. Language/region codes & x-default
- Format: language **ISO 639-1**, optionally followed by region **ISO 3166-1 alpha-2**: `de`, `de-AT`, `en-US`. Case-insensitive.
- **The first code is always the language.** A country alone is invalid. `be` means Belarusian, so for Belgium use `nl-BE`, `fr-BE`, or `de-BE`.
- Scripts use ISO 15924: `zh-Hans`, `zh-Hant`, `zh-Hant-TW`.
- Invalid or ignored: `es-419`, `EU`, `UN`, `UK` (use `GB`), and reserved codes.
- `x-default` is the fallback when no variant matches. Ideal for language or country selector pages or auto-redirecting home pages.

## 7. Duplicates across locales
- Same-language pages on different URLs (e.g. `example.de/` and `example.com/de/`): choose a preferred version and use `rel=canonical` plus hreflang.
- Canonical and hreflang must agree. The canonical stays within the same language.
- Regional variants with the same language but real differences (prices, currency, shipping) are fine. Annotate them with hreflang.

## 8. Locale-adaptive pages
- Pages that change content by perceived country (IP) or `Accept-Language` risk Google seeing only the US/default version. **Recommended instead: separate locale URLs plus hreflang.**
- Googlebot also crawls from some non-US IPs (geo-distributed crawling). Treat it like a user from that country: if you block US users, Googlebot-from-US is blocked too. It uses the same user-agent everywhere, so verify it via reverse DNS.
- Keep robots meta and robots.txt rules identical across locales.

## 9. Don'ts & common mistakes
- Auto-redirecting by IP or language.
- One URL that switches language by cookie.
- Translating only boilerplate.
- URL parameters for locale.
- Expecting geo meta tags or `lang` to work.
- Missing return links.
- Wrong codes (`uk`, `en-UK`, `es-419`, region-only).
- Relative hreflang URLs.
- hreflang pointing to non-canonical, redirected, or noindexed URLs.
- Inconsistent robots rules across locales.
- Debugging: third-party hreflang generators and testers exist (not Google-maintained). Search Console's old International Targeting report is retired, so audit hreflang with a crawler or the bundled audit script.
