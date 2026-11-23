# hreflang: multilingual and multi-regional setup

**Input:** the locales and their URLs, or a page or sitemap to check. Rules: `references/international.md`.

## Steps
1. **Decide whether hreflang is needed** (§1, §5). If the site has a single language and region, don't add it.
2. **Choose a URL structure** for a new setup (§3): ccTLD, subdomain or subdirectory. Explain the trade-offs. Never use parameters or cookies to switch locale.
3. **Build a mapping table** of page × locale → absolute URL. Every target must be canonical, indexable and return 200. hreflang to redirected, noindexed or non-canonical URLs is ignored. Canonicals stay within each language.
4. **Codes** (§6):
   - language first (ISO 639-1), with an optional region (ISO 3166-1 alpha-2);
   - `en-GB`, not `uk` (Ukrainian) or `en-UK`;
   - no `es-419`;
   - add `x-default` for a selector page or the default page.
5. **Pick one method**: HTML `<link>`, HTTP header, or sitemap. Generate the full set. Every variant lists itself and all others (reciprocity).
6. **Verify:**
   - Run the bundled auditor on each variant. It flags bad codes, relative URLs and a missing self-reference.
   - Fetch each alternate to confirm the return links.
7. **Output:**
   - the mapping table;
   - the ready-to-paste tags, header or sitemap;
   - the mistakes found (§9).

## Don't
- Auto-redirect by IP or `Accept-Language`.
- Rely on the `lang` attribute or geo meta tags.
- Translate only the boilerplate.

## Done when
Every locale variant uses valid ISO codes and absolute canonical URLs, lists itself and all reciprocal alternates (plus `x-default` where appropriate), and passes the auditor's hreflang checks.
