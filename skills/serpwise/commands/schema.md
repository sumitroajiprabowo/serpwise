# schema: write or validate structured data (JSON-LD)

**Input:** a page (URL, file or description), or existing markup to validate.

## Steps
1. **Identify the page type** and what is visible on it. Pick the types Google supports for that page from `references/structured-data.md` §3.
   - On a store, a product you can buy on the page is a **merchant listing**. A review page is a **product snippet**.
   - Skip deprecated types (§4).
   - Types with no Search feature are fine for semantics, but say they won't produce a rich result.
2. **Use only facts that are on the page.** Ask for missing required values rather than inventing them: price, currency, availability, rating counts, dates with a timezone.
3. **Write the markup:**
   - one `<script type="application/ld+json">`;
   - `@graph` when there are several entities;
   - `@id` to link Organization, WebSite and the page entities.
   Start from the templates in §5.
4. **Self-check before handing it over**, then fix and re-check until clean:
   - It parses as strict JSON. Run `python3 -c "import json,sys; json.load(sys.stdin)"` on it, or `node -e` if Python isn't available.
   - Every required property for each type is present.
   - Values match the visible page, URLs are absolute, and dates are ISO 8601 with an offset.
   - Nothing hidden is marked up.
   - There are no self-serving reviews on LocalBusiness or Organization.
5. **Output:**
   - the ready-to-paste block;
   - a short table of required and recommended properties, marked present or missing;
   - a reminder to test in the **Rich Results Test** and watch the Search Console enhancement reports.

## Validate mode
For existing markup:
- Report parse errors and missing required properties as **High**.
- Report missing recommended properties as **Medium**.
- Then give the corrected block.
