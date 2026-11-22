# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/), and versions follow [Semantic Versioning](https://semver.org/).

Each release also records `docs-snapshot`, the date the reference material was last checked against Google Search Central.

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
