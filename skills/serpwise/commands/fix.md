# fix: find and fix SEO issues in the codebase

**Input:** a repo path (default: the current directory), or a specific file or route. If the user asked only for a list, report and don't edit.

## 1. Find where SEO lives in this stack
- **Next.js**: `metadata` / `generateMetadata`, `app/sitemap.ts`, `app/robots.ts`, `next.config` redirects and headers, `next-sitemap`, `pages/_document`.
- **Nuxt**: `useHead` / `useSeoMeta`, `nuxt.config`, `@nuxtjs/sitemap`.
- **Astro / SvelteKit / Remix**: layout `<head>`, `<svelte:head>`, `meta` exports.
- **WordPress**: theme `header.php`, SEO plugin settings, *Settings → Reading → Discourage search engines*.
- **Laravel / Rails / Django**: base layout templates, routes for 404s, middleware headers.
- **Server config**: nginx/Apache redirects and `X-Robots-Tag`, Vercel/Netlify config files.

## 2. Check, in priority order
1. **Indexing**:
   - `noindex` that ships to production (staging flags, env checks);
   - robots.txt or its generator blocking `/` or CSS/JS;
   - `X-Robots-Tag` set in headers or middleware.
2. **Status codes**:
   - unknown routes return a real 404, not a 200 "not found" page (soft 404);
   - moved URLs use 301/308 in a single hop.
3. **Canonical**:
   - one absolute, self-referencing canonical per page, built from the production host;
   - consistent with the sitemap, internal links and trailing-slash policy.
4. **Valid `<head>`**: no `<img>`, `<iframe>` or other body elements rendered before the metadata (tracking pixels are the usual culprit). A viewport meta is present.
5. **Titles and descriptions**: generated per page from page data, not one site-wide constant.
6. **Links**: link components render `<a href>`, navigation doesn't rely on `onClick`, and there's no `#` routing.
7. **Rendering**: the main content and links are in the server HTML (SSR/SSG), or at least render without user interaction.
8. **Images**: meaningful images have `alt` and a real `src` in the rendered HTML.
9. **Structured data**: JSON-LD is built as an object and serialized (`JSON.stringify`), not as a hand-written string template, and it matches the visible content.
10. **Sitemap and hreflang**: only canonical absolute URLs. Locale variants are reciprocal.

## 3. Fix
- Make the smallest change at the source: the layout, template or config, not per-page copies.
- Keep all other behavior unchanged.
- Never add myths such as meta keywords.

## 4. Verify
- Build or run the app if you can, then run the bundled auditor on one rendered URL per template. Otherwise inspect the generated HTML.
- Run the project's existing tests and lint.

## 5. Report
- A table of changes: `file:line`, the problem, the fix, and the Google rule.
- Anything that can only be confirmed after deploy, such as URL Inspection or the Page Indexing report.

## Done when
Every Critical and High issue found in the codebase is fixed at its template or config source, existing tests and lint pass, and any remaining post-deploy checks are listed.
