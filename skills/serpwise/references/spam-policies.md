# Google spam policies (what NOT to do)

Source: developers.google.com/search/docs/essentials/spam-policies

Violations lead to lower rankings or removal. Detection is automated (SpamBrain) plus human review (manual actions in Search Console). Fix the problem, then file a reconsideration request. If a user asks for any of these tactics, decline the tactic, explain the risk, and offer the legitimate alternative.

| Policy | What it is | Legit alternative |
|---|---|---|
| **Cloaking** | Different content for Googlebot vs users | Serve the same content. Paywalls are OK with paywalled markup and flexible sampling |
| **Doorway abuse** | Many near-identical pages or domains funneling to one destination (e.g. "jasa SEO [kota]" × 500 cities) | Real location pages with unique local info, or one strong page |
| **Expired domain abuse** | Buying an expired domain for its reputation and hosting unrelated low-value content | Build your own brand. Redirect only genuinely related acquired domains |
| **Hacked content** | Injected code, pages, or links, malicious redirects | Security hygiene. Monitor the Security Issues report |
| **Hidden text & links** | White-on-white text, off-screen CSS, 0px font, text behind images | Visible content. Accordions, tabs, tooltips, and screen-reader text are fine |
| **Keyword stuffing** | Lists of keywords, cities, or phone numbers, unnatural repetition | Natural writing for people |
| **Link spam** | Buying or selling links for PageRank, excessive exchanges, automated links, keyword-anchor guest posts or advertorials, widget or footer links, low-quality directories, forum signatures, ToS-required links | Earn links with useful content and PR. Mark paid links `rel="sponsored"` or `nofollow` |
| **Machine-generated traffic** | Automated queries or rank scraping on Google | Search Console API |
| **Malware / malicious practices** | Malware, unwanted software, back-button hijacking | None |
| **Misleading functionality** | Fake tools or generators that don't work, deceptive ads | Tools that do what they say |
| **Scaled content abuse** | Many pages made primarily to manipulate rankings: mass generative-AI pages, scraped or spun feeds, stitched content, nonsense keyword pages, spreading across sites to hide scale | AI as an assistant for genuinely helpful, reviewed, people-first content. Noindex low-value hosted content |
| **Scraping** | Republishing others' content without added value, light rewrites, copied feeds, embed-only pages | Original work, or substantial added value with attribution |
| **Site reputation abuse** | Third-party pages hosted mainly to ride the host's ranking signals (e.g. a casino or payday-loan section on an education or news site) | Content integrated with the site's purpose and editorially controlled. Wire services, syndication, UGC, native ads, and proper affiliate links are fine |
| **Sneaky redirects** | Redirecting users or mobile visitors to different or spam content than shown to Google | Legit redirects only (moves, consolidation, login) |
| **Thin affiliation** | Affiliate pages with copied merchant descriptions and no added value | Original reviews, testing, comparisons, price information |
| **User-generated spam** | Spam accounts, posts, comments, files on your platform | Moderation, reCAPTCHA, `rel=ugc`, noindex for new users (monitoring-debugging.md §8) |

Other demotions:
- Many valid **legal removals** (copyright, defamation, counterfeit, court orders).
- **Personal information removals**, including exploitative removal practices and doxxing.
- **Policy circumvention**: moving violations to new subdomains, subdirectories, or sites. This can remove feature eligibility (Top Stories, Discover).
- **Scams and fraud**: impersonation, fake support, false business information.

Site reputation abuse notes:
- Outside the EEA it gets manual actions.
- Within the EEA, affected pages may be categorized separately instead.
- Review factors: presentation, quality, stated authorship, and duplication elsewhere.
