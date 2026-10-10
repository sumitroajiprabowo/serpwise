# Contributing

The most useful thing you can send is a correction. If a rule in `skills/serpwise/references/` is wrong, out of date, or not something Google actually says, open an issue or a pull request with a link to the Google page.

Google edits Search Central often. When a page we rely on changes, the "Google documentation changed" issue template asks for exactly what we need.

Auditor bugs are welcome too. Include the HTML or URL and the output of `npx serpwise audit`. So are reports from agents we haven't tested: tell us the agent, its version, and whether the skill loaded.

## Ground rules

1. Every rule must trace back to a page on [Google Search Central](https://developers.google.com/search/docs). Link it in your pull request. Popular SEO advice that Google doesn't support goes in the myths list in `SKILL.md`, not in the references.
2. Paraphrase. Don't paste Google's text.
3. Keep the skill host-neutral: no paths or tools that only one agent has.
4. The auditor stays on the Python standard library and runs on Python 3.8.

## Checks

```bash
npm test        # Node and Python tests
npm run lint    # ruff, Biome and shellcheck (needs uv and shellcheck)
npm run format  # fix formatting
```

[AGENTS.md](AGENTS.md) covers the repository layout, the full list of checks and the release steps. Coding agents read that file as well.

## Pull requests

- Keep one change per pull request.
- Add a test for any auditor or installer change (`tests/test_audit_page.py`, `tests/cli.test.mjs`).
- Add a line to `CHANGELOG.md` under an "Unreleased" heading.

By contributing, you agree that your work is released under the [MIT License](LICENSE).
