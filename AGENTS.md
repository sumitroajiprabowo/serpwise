# Contributing to serpwise

This guide is for people and AI agents working on this repository.

## How the repository is organized

The product is a single Agent Skill in `skills/serpwise/`. Everything else is packaging around it:

| Path | Purpose |
|---|---|
| `skills/serpwise/SKILL.md` | Instructions the agent loads first: commands, severity levels, myths, report format |
| `skills/serpwise/commands/` | One playbook per command |
| `skills/serpwise/references/` | Condensed Google Search Central guidance, read on demand |
| `skills/serpwise/scripts/audit_page.py` | The page auditor |
| `skills/serpwise/agents/openai.yaml` | Optional display metadata for Codex |
| `skills/serpwise/evals/` | End-to-end test cases (not shipped to users) |
| `bin/serpwise.mjs`, `package.json` | The `npx serpwise` installer |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests |
| `install.sh` | Installer for machines without Node.js |
| `examples/` | Unedited audit reports from a with/without-skill comparison, linked from the README |
| `assets/` | README animations, their generator (`make_demos.py`) and the GitHub social preview image. Not shipped to npm |
| `.github/` | CI, the npm release workflow, issue templates and the pull request template |

## Rules for the skill

The skill has to work in every agent that supports the [Agent Skills specification](https://agentskills.io/specification), so it follows that specification strictly.

**Frontmatter**
- `name` must match the folder name.
- `description` must stay under 1,024 characters.
- The only other allowed fields are `license`, `compatibility`, `metadata` and `allowed-tools`.
- Agent-specific fields such as `argument-hint` fail validation, so leave them out.

**Commands**
- Every row in the Commands table in `SKILL.md` needs a matching playbook in `commands/`.
- A playbook describes the workflow, the output and when the job is done. For the SEO rules themselves, it points to `references/` instead of repeating them.
- `tests/test_skill_structure.py` checks that the table and the files agree.

**Size**
- Keep `SKILL.md` well under 500 lines.
- Detail belongs in `references/`, linked directly from `SKILL.md` with paths relative to the skill folder.

**Host neutrality**
- Don't hard-code paths like `~/.claude/` or tools that only one agent has.

**Auditor**
- `scripts/audit_page.py` must run on Python 3.8 or later with only the standard library.

**Sources**
- Every rule in `references/` must come from Google Search Central documentation.
- Paraphrase, don't copy.
- If a claim can't be traced to Google, leave it out. Popular SEO advice that Google doesn't support belongs in the myths list instead.

**Severity levels**
- Findings use Critical, High, Medium and Low. Keep these labels consistent across `SKILL.md`, the playbooks and the auditor.

## Checks

Run these before opening a pull request:

```bash
npm test                     # installer tests (Node) plus auditor and structure tests (Python)
npm run lint                 # ruff, Biome and shellcheck
npm pack --dry-run           # confirm evals/ is not in the package
uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" skills-ref validate skills/serpwise
claude plugin validate .
bash -n install.sh
```

CI runs the same checks on more platforms:
- Python 3.8, 3.10 and 3.13;
- Node 18, 20 and 22 on Linux, plus Node 22 on Windows and macOS.

It also:
- installs the packed tarball with `npx`;
- confirms that every manifest carries the same version number.

Code comments are in English. Every function gets a one-line comment or docstring saying what it does; add more only where the reason isn't obvious from the code.

When you add a check to the auditor, add a test to `tests/test_audit_page.py`. Changes to the installer need a test in `tests/cli.test.mjs`.

The cases in `skills/serpwise/evals/` run real model sessions and cost money, so they aren't part of CI. Run them with:

```bash
claude plugin eval skills/serpwise --allow-tools Write,Edit,Bash --scaffold
```

## Updating for Google documentation changes

1. Update the affected file in `references/`.
2. Set `metadata.docs-snapshot` in `SKILL.md` to the date you checked the documentation.
3. Bump the version, then add an entry to `CHANGELOG.md`.

## Releasing

The version number appears in four places, and CI fails if they don't match:
- `package.json`;
- `.claude-plugin/plugin.json`;
- `.claude-plugin/marketplace.json`;
- `metadata.version` in `SKILL.md`.

To release:

1. Update all four version numbers and add a `CHANGELOG.md` entry.
2. Run `npm test`, commit and push.
3. Create a GitHub release with the tag `v<version>`, for example `gh release create v1.2.0 --generate-notes`.

Publishing the release starts `.github/workflows/release.yml`. It checks that the tag matches all four version numbers, runs the tests and publishes to npm. A pre-release goes to the `next` dist-tag.

The workflow uses npm trusted publishing (OIDC), so the repository holds no npm token. The trusted publisher is set up once on npmjs.com under the package's Settings: GitHub Actions, `sumitroajiprabowo/serpwise`, workflow `release.yml`, with direct publish allowed.
