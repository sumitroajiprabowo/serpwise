# Explicit content & SafeSearch

Source: developers.google.com/search/docs/specialty/explicit/guidelines, /troubleshooting

## What SafeSearch filters
- Sexual content of any kind (including pornography), nudity, photo-realistic sex toys, sex-oriented dating or escort services, violence or gore.
- Pages linking to, or showing pop-ups and ads for, such content.
- Educational, documentary, scientific, or artistic (EDSA) content may still be allowed.
- Detection is automated (ML on text, images, video, and links).
- Even with SafeSearch off or set to blur, ranking tries to avoid unexpected explicit results for non-explicit queries.

## Removals & demotion
- CSAM is always removed. Sites with a significant share of it are demoted entirely.
- Sites receiving many valid removals for non-consensual explicit imagery or explicit fakes get **all their pages demoted**.
- Content policy violations are removed regardless of SafeSearch.

## Best practices for sites with explicit content
1. **Prevent harmful UGC**: publisher verification, moderation, and proactive CSAM detection (hash matching for known content, classifiers for new content). See protectingchildren.google.
2. **Let Google fetch video files.** If it can't, automated protections can't run and pages may be demoted or filtered, especially in Video mode. Verify Googlebot to limit exposure.
3. **Let Googlebot past the age gate**: verify Googlebot (reverse DNS) and serve the content without the gate.
   - If Googlebot hits the gate, ranking suffers and image or video bytes can't be fetched.
   - Non-explicit content behind a gate Google can't see is more likely to be classified explicit.
4. **Separate explicit content onto its own domain or subdomain** (`adult.example.com` vs `www.example.com`). Otherwise the whole site may be filtered. The word "explicit" isn't needed in the name.
5. **Label pages** (optional, because detection is automatic):
   - `<meta name="rating" content="adult">` or the equivalent `content="RTA-5042-1996-1400-1577-RTA"`, or an HTTP header. Only on explicit pages.
   - In video sitemaps, `<video:family_friendly>no</video:family_friendly>` **only** for explicit or graphic videos.
6. **Shopping**: label adult products with the Merchant Center `adult` attribute or `hasAdultConsideration` markup. This doesn't affect organic search.

## Site wrongly flagged as explicit: troubleshooting
Diagnose:
- Page: search a query that finds the page with SafeSearch Off, then switch to Filter. If the page disappears, it's filtered.
- Site: run `site:example.com` with SafeSearch Off, then Filter.

Common mistakes:
- The adult `rating` meta tag on non-explicit pages (everything carrying it gets filtered).
- `family_friendly=no` on safe videos.
- Unmoderated UGC uploads or comments.
- An age gate blocking Googlebot (check with the URL Inspection live test).
- Explicit and non-explicit content mixed on one host.

After fixing:
- Wait **2–3 months** for classifiers to reprocess, then request a review. You can request immediately if the site always followed the guidelines.

Notes:
- Blurred images still count as explicit if they can be unblurred or link to the unblurred version.
- Explicit pages are ineligible for rich results, featured snippets, and video previews even with SafeSearch off.
- Sites with lots of nudity, sexual content (including computer-generated), or graphic violence may be classified as a whole.
