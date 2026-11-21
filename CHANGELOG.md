# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/), and versions follow [Semantic Versioning](https://semver.org/).

Each release also records `docs-snapshot`, the date the reference material was last checked against Google Search Central.

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
