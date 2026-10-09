// Tests for bin/serpwise.mjs. Run: node --test tests/cli.test.mjs

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CLI = path.join(ROOT, "bin", "serpwise.mjs");

// Run the CLI with a throwaway home directory, so tests never touch the real one.
function run(args, home, cwd = home) {
  const r = spawnSync(process.execPath, [CLI, ...args], {
    cwd,
    encoding: "utf8",
    env: { ...process.env, HOME: home, USERPROFILE: home },
  });
  return { code: r.status, out: r.stdout + r.stderr };
}
// Path helpers for temp folders and the install locations.
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), "serpwise-"));
const skill = (base, kind) => path.join(base, kind, "skills", "serpwise");
const antigravity = (home) => path.join(home, ".gemini", "config", "skills", "serpwise");

test("version matches package.json and SKILL.md metadata", () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8")).version;
  const md = fs.readFileSync(path.join(ROOT, "skills/serpwise/SKILL.md"), "utf8");
  assert.equal(run(["--version"], tmp()).out.trim(), pkg);
  assert.match(md, new RegExp(`version: "${pkg.replace(/\./g, "\\.")}"`));
});

// A home directory where Claude Code and Antigravity are installed.
const agentHome = () => {
  const home = tmp();
  fs.mkdirSync(path.join(home, ".claude"));
  fs.mkdirSync(path.join(home, ".gemini"));
  return home;
};

test("installs for Claude Code, .agents clients and Antigravity, without evals", () => {
  const home = agentHome();
  const r = run([], home);
  assert.equal(r.code, 0, r.out);
  for (const dir of [skill(home, ".agents"), skill(home, ".claude"), antigravity(home)]) {
    assert.ok(fs.existsSync(path.join(dir, "SKILL.md")), dir);
    assert.ok(fs.existsSync(path.join(dir, "commands", "audit.md")));
    assert.ok(fs.existsSync(path.join(dir, "scripts", "audit_page.py")));
    assert.ok(!fs.existsSync(path.join(dir, "evals")));
  }
});

test("skips agents that aren't installed unless asked", () => {
  const home = tmp();
  const r = run([], home);
  assert.equal(r.code, 0, r.out);
  assert.ok(fs.existsSync(path.join(skill(home, ".agents"), "SKILL.md")));
  assert.ok(!fs.existsSync(path.join(home, ".claude")), "must not create ~/.claude");
  assert.ok(!fs.existsSync(path.join(home, ".gemini")), "must not create ~/.gemini");
  assert.match(r.out, /--agents claude/);
  assert.equal(run(["--agents", "antigravity"], home).code, 0);
  assert.ok(fs.existsSync(path.join(antigravity(home), "SKILL.md")));
});

test("--project installs into the project only", () => {
  const home = tmp(),
    proj = tmp();
  assert.equal(run(["--project", proj], home).code, 0);
  assert.ok(fs.existsSync(path.join(skill(proj, ".agents"), "SKILL.md")));
  assert.ok(fs.existsSync(path.join(skill(proj, ".claude"), "SKILL.md")));
  assert.ok(!fs.existsSync(skill(home, ".agents")));
  assert.ok(!fs.existsSync(path.join(proj, ".gemini")), "Antigravity reads .agents/skills in projects");
});

test("--project --agents antigravity installs to the project's .agents/skills", () => {
  const home = tmp(),
    proj = tmp();
  assert.equal(run(["--project", proj, "--agents", "antigravity"], home).code, 0);
  assert.ok(fs.existsSync(path.join(skill(proj, ".agents"), "SKILL.md")));
  assert.ok(!fs.existsSync(skill(proj, ".claude")));
});

test("--agents limits targets", () => {
  const home = tmp();
  assert.equal(run(["--agents", "claude"], home).code, 0);
  assert.ok(fs.existsSync(skill(home, ".claude")));
  assert.ok(!fs.existsSync(skill(home, ".agents")));
  assert.ok(!fs.existsSync(antigravity(home)));
  assert.notEqual(run(["--agents", "nope"], home).code, 0);
});

test("update replaces an existing install, uninstall removes it", () => {
  const home = agentHome();
  run([], home);
  fs.writeFileSync(path.join(skill(home, ".agents"), "stale.txt"), "old");
  assert.equal(run(["update"], home).code, 0);
  assert.ok(!fs.existsSync(path.join(skill(home, ".agents"), "stale.txt")));
  assert.equal(run(["uninstall"], home).code, 0);
  assert.ok(!fs.existsSync(skill(home, ".agents")));
  assert.ok(!fs.existsSync(skill(home, ".claude")));
  assert.ok(!fs.existsSync(antigravity(home)));
});

test("never overwrites a foreign folder with the same name", () => {
  const home = tmp();
  const foreign = skill(home, ".agents");
  fs.mkdirSync(foreign, { recursive: true });
  fs.writeFileSync(path.join(foreign, "SKILL.md"), "---\nname: someone-else\n---\n");
  const r = run([], home);
  assert.match(r.out, /skipped/);
  assert.match(fs.readFileSync(path.join(foreign, "SKILL.md"), "utf8"), /someone-else/);
  run(["uninstall"], home);
  assert.ok(fs.existsSync(foreign));
});

test("--dry-run changes nothing", () => {
  const home = tmp();
  assert.match(run(["--dry-run"], home).out, /would create/);
  assert.ok(!fs.existsSync(skill(home, ".agents")));
});

test("audit passes arguments through to the Python auditor", () => {
  const fixture = path.join(ROOT, "skills/serpwise/evals/audit-broken-landing-page/files/index.html");
  const r = run(["audit", fixture, "--base-url", "https://example.com/", "--offline", "--json"], tmp());
  if (/needs Python/.test(r.out)) return; // no Python on this machine
  assert.equal(r.code, 0, r.out);
  assert.ok(JSON.parse(r.out).findings.some((f) => /noindex/.test(f.issue)));
});

test("unknown arguments fail with a hint", () => {
  const r = run(["--bogus"], tmp());
  assert.notEqual(r.code, 0);
  assert.match(r.out, /--help/);
});
