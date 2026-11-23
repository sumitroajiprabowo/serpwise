# drop: diagnose a Google traffic drop

**Input:** what dropped (clicks and/or impressions), since when, how much, and where (pages, queries, countries, devices, search type). Also any recent changes: deploys, migrations, CMS or plugin updates, redesigns. Rules: `references/monitoring-debugging.md` §3–4.

## Steps
1. **If key data is missing, ask once, specifically.** Ask for a Performance report comparison (last 3 months vs the previous period, plus a 16-month view) and the Pages and Queries tables sorted by click difference. If the user has the exported CSVs, rank them with `python3 <skill-dir>/scripts/analyze_gsc.py Queries.csv --metric clicks` (also `impressions`, `ctr`, `position`, and `Pages.csv`).
2. **Classify the shape:**
   - sudden and site-wide;
   - gradual;
   - seasonal or yearly;
   - a reporting glitch.
3. **Walk the checklist in order**, saying for each step what to check and what a positive result looks like:
   1. reporting glitch;
   2. Google update;
   3. technical issues;
   4. security;
   5. manual action or spam;
   6. seasonality or changing interest;
   7. a migration.
4. **Check the pages directly.** If URLs are known, run the bundled auditor on the biggest losers to catch `noindex`, robots blocks, canonical changes and status codes.
5. **Read the click/impression pattern:**
   - Both down means a visibility problem.
   - Impressions flat with clicks down means a title, snippet or SERP-feature problem. Run `meta` and `schema` on those pages.
6. **Output:**
   - the likely causes, ranked by evidence;
   - what was ruled out and why;
   - the next checks;
   - the fixes.
   Don't promise recovery. After a core update, recommend a content self-assessment (`content`), not quick tweaks.
