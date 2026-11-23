# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/), and versions follow [Semantic Versioning](https://semver.org/).

Each release also records `docs-snapshot`, the date the reference material was last checked against Google Search Central.

## [1.1.1] - 2026-11-24

docs-snapshot: 2026-11-22

### Added

- `scripts/audit_page.py` checks `robots.txt` for HTTP 429 and the 500 KiB limit, flags `<meta http-equiv="refresh">` redirects by delay (Low for instant, Medium for delayed; plain reloads ignored), flags `FAQPage` and `HowTo` JSON-LD as no longer producing Google rich results (Low), validates `BreadcrumbList` item count and required `ListItem` fields, and checks required properties for `VideoObject`, `Recipe`, and `SoftwareApplication`.
- `Done when` sections in all command playbooks, and an explicit Output step in `commands/local.md`.
- `skills/serpwise/scripts/analyze_gsc.py` listed in the README repository layout.

### Fixed

- `scripts/audit_page.py` combines all `<meta name="robots">` and `<meta name="googlebot">` tags instead of reading only the first.
- `scripts/audit_page.py` no longer crashes on `<link rel="canonical">` without an `href` attribute, and flags empty canonical `href` values.
- `scripts/audit_page.py` scopes `X-Robots-Tag` checks to Googlebot/unscoped rules, matches `robots.txt` user-agent tokens exactly, checks `max-image-preview:large` case-insensitively across meta tags and `X-Robots-Tag`, ignores `<title>` inside `<body>` (such as inline SVG), counts image `alt` text inside `<a>` links as anchor text, flags zero-link pages for missing internal links, and rates `hreflang="uk"` High on English pages (Low otherwise).
- `scripts/analyze_gsc.py` omits meaningless totals for non-additive metrics (`ctr`, `position`), labels additive totals as "Total of exported rows" with a `rows_note` about Search Console's 1,000-row export cap, and formats floats cleanly.
- `install.sh --copy` excludes `evals/`, `__pycache__/`, and `.DS_Store`.
- Replaced remaining Indonesian words and locale examples in `references/appearance.md`, `references/international.md`, and `tests/test_audit_page.py`.
- Updated `references/appearance.md` Core Web Vitals thresholds to `≤ 200ms` (INP) and `≤ 0.1` (CLS), and updated the deprecated structured data list in `references/structured-data.md` (2025–2026 removals and FAQ retirement).

## [1.1.0] - 2026-11-23

docs-snapshot: 2026-11-22

### Added

- The auditor can audit every URL in a sitemap (`--sitemap`, `--limit`, default 20) or a list of URLs on stdin (`-`). Sitemap indexes and gzipped sitemaps are followed, and image or video `<loc>` entries aren't treated as pages.
- `--markdown` output for pull request comments and issues.
- Missing required properties are reported for Product, LocalBusiness, Event, JobPosting and BreadcrumbList markup (High, since the item can't get its rich result), and missing recommended properties for Article (Medium).
- `--pagespeed` reports Core Web Vitals (LCP, INP, CLS) from Chrome UX Report field data at the 75th percentile, using Google's thresholds. Lab data is shown for context but never raised as a finding. `--pagespeed-key` or `PAGESPEED_API_KEY` supplies an API key, because the keyless quota runs out quickly.
- `local` command for local business pages and LocalBusiness markup.
- `scripts/analyze_gsc.py` ranks the queries or pages that lost and gained the most in a Search Console Compare export, for clicks, impressions, CTR or position.
- `examples/serpwise-ci.yml`, a GitHub Actions workflow that audits a page on pull requests.

### Changed

- The `content` playbook says what Google recommends for AI search features and corrects the "AEO/GEO" myths.
- The installer help and README say that Cursor and Windsurf read `~/.agents/skills`, which the default install already covers.

## [1.0.1] - 2026-11-22

docs-snapshot: 2026-11-22

Rechecked every reference file against the current Google Search Central pages: SEO fundamentals, crawling and indexing, ranking and search appearance, site-specific guides and data analysis.

### Added

- Google's guide to generative AI search: query fan-out, the Search Console inclusion setting and report, and its myth list (llms.txt, chunking, rewriting for AI, one page per query variant, planted mentions).
- Search Essentials and its three technical requirements, the three stages of Search, and the main-content quality attributes (effort, originality, skill, accuracy).
- Google's guidance on AI-generated content, including reviewing titles, descriptions, structured data and alt text.
- Hiring an SEO: the questions to ask, red flags, and how to check third-party and "AEO/GEO" advice.
- Identifying Google Search traffic by referrer in analytics and server logs.
- Social and video platform accounts in Search Console.
- Google's crawler tokens, the 64MB PDF limit, and the planned AIPREF training signal.
- A release workflow that publishes to npm with trusted publishing (no npm token) whenever a GitHub Release is published.

### Changed

- FAQ and HowTo rich results are described as absent from Google's search gallery.
- Restructuring advice now matches the Starter Guide: don't reorganize a site right away.
- Replaced the remaining Indonesian examples in the references and tests with neutral ones.

## [1.0.0] - 2026-11-21

docs-snapshot: 2026-11-20

First release.

### Added

- Agent Skill with ten commands: `audit`, `fix`, `schema`, `meta`, `robots`, `sitemap`, `hreflang`, `migrate`, `drop` and `content`. Each command has its own playbook in `skills/serpwise/commands/`.
- Findings rated by severity (Critical, High, Medium, Low), each with the Google rule it is based on.
- Reference material condensed from Google Search Central, covering:
  - fundamentals;
  - crawling and indexing;
  - search appearance;
  - structured data;
  - monitoring and debugging;
  - ecommerce;
  - international sites;
  - explicit content;
  - spam policies.
- A page auditor (`scripts/audit_page.py`, Python 3.8+, standard library only) for live URLs and local HTML files.
- `npx serpwise` to install, update and uninstall the skill, and to run the auditor. A default install only targets agents found on the machine.
- Install options for skills.sh, the Claude Code plugin marketplace and `install.sh`.
- `--fail-on <severity>` in the auditor, so a CI job can fail when a page has findings at that level or worse.
- Linting and formatting with ruff, Biome and shellcheck, checked in CI.
- Tests for the installer, the auditor and the skill structure, run in CI, plus three end-to-end eval cases that run real model sessions.

### Tested with

- Claude Code 2.1.329
- Codex CLI 0.169.0
- Antigravity CLI 1.5.11
- GitHub Copilot CLI 1.0.65
