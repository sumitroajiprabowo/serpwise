# meta: title and meta description

**Input:** a page (URL, file or content), or a page template for a large site. Rules: `references/appearance.md` §2–3.

## Steps
1. Read the page's main content and work out its intent. Name the primary query in the user's language.
2. **Title:**
   - descriptive and specific, on the same topic as the visible `<h1>`;
   - brand at the start or end with a separator (`-`, `:`, `|`);
   - no stuffing and no boilerplate.
   There is no fixed character limit, but long titles get truncated, so put the distinguishing words first.
3. **Meta description:** a unique, readable 1–2 sentence summary with concrete facts from the page (price, specs, location, date, author). No keyword lists.
4. **Large sites:** write a template that fills in page fields. Make sure the output varies, and avoid "micro-boilerplate" that differs only by a number.
5. **Output:**
   - 2–3 options, ready to paste as HTML or in the project's framework syntax (e.g. Next.js `metadata`);
   - one line on why each works.
   Note that Google may still rewrite titles and snippets per query.

## Don't
- Give fixed character targets as Google rules.
- Add meta keywords.
- Repeat the same description across pages, except the home page and aggregation pages.
