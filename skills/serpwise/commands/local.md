# local: local business pages and LocalBusiness markup

**Input:** a business website or page, the business type, and its address or addresses. Rules: `references/structured-data.md` §LocalBusiness, `references/appearance.md` §14 (business details), and the doorway policy in `references/spam-policies.md`.

## Steps
1. **Pick the type.** Use the most specific `LocalBusiness` subtype that fits (Restaurant, Dentist, Store...).
2. **Check or write the `LocalBusiness` JSON-LD** on the page for that location, following the required/recommended properties, hours formatting, and review rules in `references/structured-data.md` §LocalBusiness. Ensure name, address, and phone match the visible page.
3. **Business Profile.** Google says to claim a Google Business Profile for the address, hours and photos shown in Maps and the knowledge panel. That happens outside the codebase, so list it as a task for the user.
4. **Organization markup** on the home page with `logo`, plus breadcrumbs on location pages.
5. **Several locations:**
   - one page per real location, with its own URL, title, description and LocalBusiness markup;
   - each page needs information that is specific to that location;
   - no near-identical city pages with only the place name swapped. That is doorway abuse.
6. **Run the basics** from `commands/audit.md` on one location page (status, canonical, title, mobile).
7. **Output:**
   - findings rated by severity;
   - ready-to-paste `LocalBusiness` JSON-LD (and `Organization` / `BreadcrumbList` if missing);
   - the Business Profile checklist to complete outside the codebase.

## Don't
- Promise positions in Maps or the local pack.
- Add keywords to the business name in markup. It must be the real name.
- Create pages for places the business doesn't serve or have a presence in.

## Done when
Each location has a substantive page with valid LocalBusiness markup that matches the visible details, and the user has a list of Business Profile tasks to do outside the code.
