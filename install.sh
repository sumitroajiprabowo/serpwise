#!/usr/bin/env bash
# Install the serpwise skill without Node.js. With Node, prefer `npx serpwise`.
#
#   ./install.sh                     install for every agent found on this machine (user-level)
#   ./install.sh claude antigravity  install only for the named targets
#   ./install.sh --project DIR       install into a project instead
#   ./install.sh --copy ...          copy the files instead of symlinking them
#
# Targets:
#   claude       ~/.claude/skills/serpwise          Claude Code
#   agents       ~/.agents/skills/serpwise          Codex, GitHub Copilot and other Agent Skills clients
#   antigravity  ~/.gemini/config/skills/serpwise   Antigravity
# In a project, Antigravity reads DIR/.agents/skills, so --project writes
# DIR/.claude/skills and DIR/.agents/skills only.
set -euo pipefail

# The skill folder sits next to this script.
SKILL_NAME="serpwise"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/$SKILL_NAME"
MODE="link"
PROJECT=""
TARGETS=()

# Parse options and target names.
while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE="copy" ;;
    --project) PROJECT="${2:?--project needs a directory}"; shift ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    claude|agents|antigravity) TARGETS+=("$1") ;;
    *) echo "Unknown option: $1 (see --help)" >&2; exit 1 ;;
  esac
  shift
done

[ -f "$SRC/SKILL.md" ] || { echo "SKILL.md not found at $SRC" >&2; exit 1; }

# No targets given: in a project use both folders, otherwise only the agents found here.
if [ ${#TARGETS[@]} -eq 0 ]; then
  if [ -n "$PROJECT" ]; then
    TARGETS=(claude agents)
  else
    TARGETS=(agents)
    if [ -d "$HOME/.claude" ]; then TARGETS+=(claude); else echo "- Claude Code not found (no ~/.claude), skipped"; fi
    if [ -d "$HOME/.gemini" ]; then TARGETS+=(antigravity); else echo "- Antigravity not found (no ~/.gemini), skipped"; fi
  fi
fi

# Print the install folder for one target.
dest_for() {
  local base="${PROJECT:-$HOME}"
  case "$1" in
    claude) echo "$base/.claude/skills/$SKILL_NAME" ;;
    agents) echo "$base/.agents/skills/$SKILL_NAME" ;;
    antigravity)
      if [ -n "$PROJECT" ]; then echo "$base/.agents/skills/$SKILL_NAME"
      else echo "$HOME/.gemini/config/skills/$SKILL_NAME"; fi ;;
  esac
}

# Install each folder once. An existing folder is moved aside as a backup, never deleted.
done_paths=" "
for t in "${TARGETS[@]}"; do
  dest="$(dest_for "$t")"
  case "$done_paths" in *" $dest "*) continue ;; esac
  done_paths="$done_paths$dest "
  mkdir -p "$(dirname "$dest")"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$MODE" = "link" ] && [ -L "$dest" ] && [ "$(readlink "$dest")" = "$SRC" ]; then
      echo "✓ $t: already linked ($dest)"; continue
    fi
    backup="$dest.bak.$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    echo "  moved the existing $dest to $backup"
  fi
  if [ "$MODE" = "copy" ]; then cp -R "$SRC" "$dest"; else ln -s "$SRC" "$dest"; fi
  echo "✓ $t: $MODE -> $dest"
done

echo "Done. Restart your agent to load $SKILL_NAME."
