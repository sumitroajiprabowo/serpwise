#!/usr/bin/env node
// serpwise CLI: installs the serpwise Agent Skill for coding agents, and runs the bundled auditor.
// Zero dependencies. Node 18+.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Paths inside the installed npm package.
const NAME = "serpwise";
const PKG_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SRC = path.join(PKG_ROOT, "skills", NAME);
const VERSION = JSON.parse(fs.readFileSync(path.join(PKG_ROOT, "package.json"), "utf8")).version;
// Never copied to users: test cases and local build leftovers.
const SKIP = new Set(["evals", "__pycache__", ".DS_Store"]);

// Where each agent reads skills from. `home` is relative to the user's home
// directory, `project` to a project root. Duplicate paths are installed once.
const TARGETS = {
  // `detect` is the folder that shows the agent is installed; without it, a
  // default install skips that agent instead of creating its config folder.
  claude: {
    home: [".claude", "skills"],
    project: [".claude", "skills"],
    detect: ".claude",
    label: "Claude Code",
  },
  agents: {
    home: [".agents", "skills"],
    project: [".agents", "skills"],
    detect: null,
    label: "Codex, GitHub Copilot and other Agent Skills clients",
  },
  antigravity: {
    home: [".gemini", "config", "skills"],
    project: [".agents", "skills"],
    detect: ".gemini",
    label: "Antigravity",
  },
};

const HELP = `serpwise ${VERSION}: SEO for AI coding agents, based on Google's documentation

Usage
  npx serpwise                      Install for the agents found on this machine
  npx serpwise --project [dir]      Install into a project only (default: current dir)
  npx serpwise@latest update        Reinstall the latest version over an existing install
  npx serpwise uninstall [--project [dir]]
  npx serpwise audit <url|file|-> [--json|--markdown] [--base-url URL] [--offline] [--fail-on SEVERITY]
  npx serpwise audit --sitemap URL [--limit N] [--pagespeed] ...
                                    Run the bundled page auditor (needs Python 3.8+)

Options
  --agents claude,agents,antigravity
                                    Choose targets (default: the agents found)
                                      claude      = ~/.claude/skills (Claude Code)
                                      agents      = ~/.agents/skills (Codex, Copilot, Cursor, Windsurf, ...)
                                      antigravity = ~/.gemini/config/skills (Antigravity)
                                    In a project, Antigravity reads .agents/skills.
  --dry-run                         Show what would change
  -h, --help                        Show this help
  -v, --version                     Show version

Then, in your agent:
  /serpwise audit https://example.com    (Claude Code, Copilot, Cursor, Windsurf)
  $serpwise audit https://example.com    (Codex)
`;

// Print an error and exit with status 1.
function fail(msg) {
  console.error(`serpwise: ${msg}`);
  process.exit(1);
}

// Turn argv into options. Everything after `audit` goes to the Python auditor unchanged.
function parse(argv) {
  const o = {
    cmd: "install",
    project: null,
    agents: Object.keys(TARGETS),
    explicitAgents: false,
    dryRun: false,
    rest: [],
  };
  const args = [...argv];
  if (args[0] && !args[0].startsWith("-")) o.cmd = args.shift();
  if (o.cmd === "audit") {
    o.rest = args;
    return o;
  }
  while (args.length) {
    const a = args.shift();
    if (a === "-h" || a === "--help") o.cmd = "help";
    else if (a === "-v" || a === "--version") o.cmd = "version";
    else if (a === "--dry-run") o.dryRun = true;
    else if (a === "--project") o.project = args[0] && !args[0].startsWith("-") ? args.shift() : ".";
    else if (a === "--agents") {
      const v = (args.shift() || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const bad = v.filter((x) => !TARGETS[x]);
      if (!v.length || bad.length)
        fail(`--agents takes ${Object.keys(TARGETS).join(",")}; got '${bad.join(",") || ""}'`);
      o.agents = v;
      o.explicitAgents = true;
    } else fail(`unknown argument '${a}'. Run 'npx serpwise --help'.`);
  }
  return o;
}

// The folders to install into for the chosen agents, at user or project level.
function destinations(o) {
  const base = o.project ? path.resolve(o.project) : os.homedir();
  const out = [];
  for (const k of o.agents) {
    const dir = o.project ? TARGETS[k].project : TARGETS[k].home;
    if (!dir) continue;
    const p = path.join(base, ...dir, NAME);
    if (!out.some((t) => t.path === p)) out.push({ key: k, label: TARGETS[k].label, path: p });
  }
  return out;
}

// Only replace what is clearly ours: a symlink, or a folder whose SKILL.md is named serpwise.
function isOurs(p) {
  try {
    if (fs.lstatSync(p).isSymbolicLink()) return true;
    const md = fs.readFileSync(path.join(p, "SKILL.md"), "utf8");
    return /^name:\s*serpwise\s*$/m.test(md);
  } catch {
    return false;
  }
}

// Copy the skill folder, keeping file modes so the auditor stays executable.
function copyTree(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const s = path.join(src, e.name),
      d = path.join(dst, e.name);
    if (e.isDirectory()) copyTree(s, d);
    else {
      fs.copyFileSync(s, d);
      fs.chmodSync(d, fs.statSync(s).mode);
    }
  }
}

// A default user-level install only targets agents that are present, or that
// already have serpwise installed. --agents and --project install as asked.
function wanted(o, t) {
  if (o.project || o.explicitAgents) return true;
  const detect = TARGETS[t.key].detect;
  return (
    !detect || fs.existsSync(path.join(os.homedir(), detect)) || fs.existsSync(t.path) || isSymlink(t.path)
  );
}

// Install or update. A folder that isn't ours is left alone with a warning.
function install(o) {
  if (!fs.existsSync(path.join(SRC, "SKILL.md"))) fail(`skill source not found at ${SRC}`);
  for (const t of destinations(o)) {
    if (!wanted(o, t)) {
      console.log(
        `- ${t.label}: not found (no ~/${TARGETS[t.key].detect}), skipped. Use --agents ${t.key} to install anyway.`,
      );
      continue;
    }
    const exists = fs.existsSync(t.path) || isSymlink(t.path);
    if (exists && !isOurs(t.path)) {
      console.warn(
        `! skipped ${t.path}: it exists and isn't a serpwise install. Remove it yourself if you want to replace it.`,
      );
      continue;
    }
    if (o.dryRun) {
      console.log(`would ${exists ? "replace" : "create"} ${t.path}`);
      continue;
    }
    if (exists) fs.rmSync(t.path, { recursive: true, force: true });
    copyTree(SRC, t.path);
    console.log(`✓ ${t.path}  (${t.label})`);
  }
  if (!o.dryRun) {
    console.log(`\nserpwise ${VERSION} installed. Restart your agent, then try:`);
    console.log("  /serpwise audit https://example.com   (Claude Code, Copilot, Cursor, Windsurf)");
    console.log("  $serpwise audit https://example.com   (Codex)");
    if (o.project)
      console.log("\nTip: commit .agents/ and .claude/skills/ to share serpwise with your team.");
  }
}

// lstat-based check, so a broken symlink still counts as present.
function isSymlink(p) {
  try {
    return fs.lstatSync(p).isSymbolicLink();
  } catch {
    return false;
  }
}

// Remove serpwise from every target. Folders that aren't ours are left alone.
function uninstall(o) {
  let n = 0;
  for (const t of destinations(o)) {
    if (!fs.existsSync(t.path) && !isSymlink(t.path)) continue;
    if (!isOurs(t.path)) {
      console.warn(`! left ${t.path} alone: not a serpwise install`);
      continue;
    }
    if (o.dryRun) {
      console.log(`would remove ${t.path}`);
      continue;
    }
    fs.rmSync(t.path, { recursive: true, force: true });
    console.log(`✓ removed ${t.path}`);
    n++;
  }
  if (!n && !o.dryRun) console.log("Nothing to remove.");
}

// Run the bundled auditor with the first Python 3.8+ found on PATH, passing its exit status through.
function audit(rest) {
  const script = path.join(SRC, "scripts", "audit_page.py");
  const candidates =
    process.platform === "win32" ? [["py", "-3"], ["python"], ["python3"]] : [["python3"], ["python"]];
  for (const [bin, ...pre] of candidates) {
    const probe = spawnSync(
      bin,
      [...pre, "-c", "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"],
      { stdio: "ignore" },
    );
    if (probe.status !== 0) continue;
    const r = spawnSync(bin, [...pre, script, ...rest], { stdio: "inherit" });
    process.exit(r.status ?? 1);
  }
  fail(
    "the auditor needs Python 3.8+ on PATH (python3, python or py). Your agent can still use the skill without it.",
  );
}

// Entry point. Filesystem errors become one-line messages instead of stack traces.
const o = parse(process.argv.slice(2));
process.on("uncaughtException", (e) => {
  fail(e.code === "EACCES" || e.code === "EPERM" ? `no permission to write ${e.path}` : e.message);
});
switch (o.cmd) {
  case "help":
    console.log(HELP);
    break;
  case "version":
    console.log(VERSION);
    break;
  case "install":
  case "update":
    install(o);
    break;
  case "uninstall":
  case "remove":
    uninstall(o);
    break;
  case "audit":
    audit(o.rest);
    break;
  default:
    fail(`unknown command '${o.cmd}'. Run 'npx serpwise --help'.`);
}
