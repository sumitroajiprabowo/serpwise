# Security policy

## Supported versions

Security fixes go into the latest release on npm. Update with `npx serpwise@latest update`.

## What is in scope

- `bin/serpwise.mjs`, the installer. It writes into `~/.claude/skills`, `~/.agents/skills`, `~/.gemini/config/skills` or a project folder, and must never touch anything outside a folder named `serpwise`.
- `skills/serpwise/scripts/audit_page.py`, the auditor. It fetches the URL you give it and that host's `robots.txt`, and it must not execute anything it downloads.
- `skills/serpwise/scripts/analyze_gsc.py`, the Search Console CSV analyzer. It reads only the local CSV file you pass to it and makes no network requests.
- Instructions in the skill that could lead an agent to take a harmful action.

## Reporting a vulnerability

Please don't open a public issue. Use GitHub's private reporting instead: **Security → Report a vulnerability** on [the repository](https://github.com/sumitroajiprabowo/serpwise/security/advisories/new).

Include the steps to reproduce and the version (`npx serpwise --version`). You'll get a reply within a week. Once a fix is released, the advisory is published with credit to you, unless you'd rather stay anonymous.
