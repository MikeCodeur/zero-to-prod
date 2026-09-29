#!/usr/bin/env bash
set -euo pipefail

# zero-to-prod installer
#
# Usage:
#   ./install.sh                       Project (default), Claude Code target
#   ./install.sh --target codex        Project, Codex target (.codex/skills + AGENTS.md)
#   ./install.sh --target all          Project, Claude + Codex
#   ./install.sh --global              Global Claude (~/.claude) — commands in every repo
#   ./install.sh --global --target codex   Global Codex (~/.codex/skills)
#   ./install.sh --global --target all      Global Claude + Codex
#   ./install.sh init [--target …]     Drops templates + rules in the project (after a global install)
#   ./install.sh update [--target …]   Updates tooling + templates (keeps your local edits)
#   ./install.sh --check               Lists installed files modified locally (writes nothing)
#   --hooks                            Installs the enforcement git hooks (opt-in, reversible)
#   --force                            Also overwrites locally modified templates
#
# Two scopes for each target: project (current repo) or global (--global).
#
# curl -fsSL https://raw.githubusercontent.com/MikeCodeur/zero-to-prod/main/install.sh | bash

REPO="https://github.com/MikeCodeur/zero-to-prod.git"

# --- Payload resolution (src/): local files, else a clone (curl|bash case) ---
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "${SELF_DIR:-}" ] && [ -f "$SELF_DIR/src/commands/ztp-prd.md" ]; then
  SRC="$SELF_DIR/src"
  PAYLOAD_ROOT="$SELF_DIR"
else
  TMP="$(mktemp -d)"
  echo "→ Fetching zero-to-prod…"
  git clone --depth 1 "$REPO" "$TMP" >/dev/null 2>&1
  SRC="$TMP/src"
  PAYLOAD_ROOT="$TMP"
fi

VERSION="$(git -C "$PAYLOAD_ROOT" rev-parse --short HEAD 2>/dev/null || date +%Y-%m-%d)"
CACHE="$HOME/.claude/zero-to-prod"
ORIG="./.zero-to-prod/templates.orig"   # baseline templates (tool-neutral), for local-edit detection

# --- Arguments: mode + --target + --hooks + --force ---
FORCE=0; HOOKS=0; TARGET="claude"; MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force)   FORCE=1 ;;
    --hooks)      HOOKS=1 ;;
    --check)      MODE="check" ;;
    --target)     TARGET="${2:-}"; shift ;;
    --target=*)   TARGET="${1#--target=}" ;;
    *)            MODE="$1" ;;
  esac
  shift
done

# Removes the files a previous install laid down (listed in .ztp-manifest) — never anything else.
clean_tooling() {
  local dest="$1" line
  [ -f "$dest/.ztp-manifest" ] || return 0
  while IFS= read -r line; do
    case "$line" in
      commands/*|skills/*|agents/*|prompts/*) rm -rf "$dest/$line" ;;
    esac
  done < "$dest/.ztp-manifest"
}

# Claude: verbatim copy (no build, no Node — the everyday path).
copy_tooling_claude() {
  local dest="$1" f
  clean_tooling "$dest"
  mkdir -p "$dest/commands" "$dest/skills" "$dest/agents"
  cp -R "$SRC/commands/." "$dest/commands/"
  cp -R "$SRC/skills/."   "$dest/skills/"
  cp -R "$SRC/agents/."   "$dest/agents/"
  : > "$dest/.ztp-manifest"
  for f in "$SRC/commands/"*.md; do echo "commands/$(basename "$f")" >> "$dest/.ztp-manifest"; done
  for f in "$SRC/skills/"*/;     do echo "skills/$(basename "$f")"   >> "$dest/.ztp-manifest"; done
  for f in "$SRC/agents/"*.md;   do echo "agents/$(basename "$f")"   >> "$dest/.ztp-manifest"; done
  echo "$VERSION" > "$dest/.ztp-version"
}

# Codex: transformed by the Node build → .codex/skills.
copy_tooling_codex() {
  local dest="$1" stg d
  command -v node >/dev/null 2>&1 || { echo "✗ Node is required for the codex target (md→skills build)." >&2; return 1; }
  stg="$(mktemp -d)"
  node "$PAYLOAD_ROOT/bin/ztp-build.mjs" --target codex --src "$SRC" --out "$stg" >/dev/null
  clean_tooling "$dest"
  mkdir -p "$dest"
  cp -R "$stg/." "$dest/"
  : > "$dest/.ztp-manifest"
  for d in "$dest/skills/"*/; do echo "skills/$(basename "$d")" >> "$dest/.ztp-manifest"; done
  echo "$VERSION" > "$dest/.ztp-version"
  rm -rf "$stg"
}

# Copies a template only if it is absent or not modified locally (baseline: $ORIG).
sync_templates() {
  local payload="$1" f name
  mkdir -p ./templates "$ORIG"
  for f in "$payload/templates/"*; do
    name="$(basename "$f")"
    if [ ! -f "./templates/$name" ]; then
      cp "$f" "./templates/$name"; cp "$f" "$ORIG/$name"
    elif [ -f "$ORIG/$name" ] && cmp -s "./templates/$name" "$ORIG/$name"; then
      cp "$f" "./templates/$name"; cp "$f" "$ORIG/$name"
    elif cmp -s "./templates/$name" "$f"; then
      cp "$f" "$ORIG/$name"
    elif [ "$FORCE" = 1 ]; then
      cp "$f" "./templates/$name"; cp "$f" "$ORIG/$name"
      echo "↻  templates/$name overwritten (--force)."
    else
      echo "⚠  templates/$name modified locally — not overwritten (rerun with --force to overwrite it)."
    fi
  done
}

# The zero-to-prod repository itself is not a project: its root AGENTS.md carries the method's
# maintenance rules, not the pipeline's. Never overwrite it when self-installing.
is_method_repo() { [ -f ./src/commands/ztp-prd.md ] && [ -f ./install.sh ]; }

# AGENTS.local.md belongs to the project, and /ztp-setup is its ONLY creator: the installer does
# not write it. A file laid down here with default values would make /ztp-setup look "already
# configured", and the project would inherit settings nobody chose.
warn_agents_local() {
  is_method_repo && return 0
  [ -f ./AGENTS.local.md ] && return 0
  echo "→ No settings yet — run /ztp-setup to create ./AGENTS.local.md."
}

# AGENTS.md belongs to the method: rewritten on every install, with AGENTS.local.md appended.
# Concatenation rather than import: Codex does not resolve `@file` (openai/codex#17401), it stacks
# one AGENTS.md per directory. One mechanism for both targets.
assemble_agents_md() {
  local payload="$1"
  if is_method_repo; then
    echo "· method repository: root AGENTS.md left intact (maintenance rules, not an install)."
    return 0
  fi
  cat "$payload/AGENTS.md" > ./AGENTS.md
  if [ -f ./AGENTS.local.md ]; then
    printf '\n---\n\n' >> ./AGENTS.md
    cat ./AGENTS.local.md >> ./AGENTS.md
  fi
}
wire_claude_md() {
  if [ -f ./CLAUDE.md ]; then
    grep -qxF '@AGENTS.md' ./CLAUDE.md || printf '\n@AGENTS.md\n' >> ./CLAUDE.md
  else
    printf '@AGENTS.md\n' > ./CLAUDE.md
  fi
}

# Repo-level enforcement: git hooks (opt-in, reversible). Tool-independent.
install_hooks() {
  command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1 || {
    echo "⚠  Not a git repository — hooks not installed. (git init, then ./install.sh --hooks)"; return 0; }
  mkdir -p ./.ztp-hooks
  cp "$SRC/hooks/ztp-gate.sh" "$SRC/hooks/pre-commit" ./.ztp-hooks/
  chmod +x ./.ztp-hooks/ztp-gate.sh ./.ztp-hooks/pre-commit
  git config core.hooksPath .ztp-hooks
  echo "✅ Git hooks installed (core.hooksPath=.ztp-hooks). Gate: no code without a validated plan."
  echo "   The ship gate (ztp-gate ship-allowed <id>) belongs in CI / branch protection."
  echo "   Disable: git config --unset core.hooksPath"
}

# --check: compares the install to the payload, through .ztp-manifest. Writes nothing.
# A command edited locally is lost on the next install — better to know beforehand.
check_drift() {
  local dest="$1" payload="$2" label="$3" line drifted=0 src_path
  [ -d "$dest" ] || return 0
  if [ ! -f "$dest/.ztp-manifest" ]; then
    echo "· $label: no manifest (installed by an earlier version)."; return 0
  fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    src_path="$payload/$line"
    if [ ! -e "$src_path" ]; then
      echo "  + $line — no longer in the method (removed on the next install)"; drifted=1
    elif [ ! -e "$dest/$line" ]; then
      echo "  ✗ $line — deleted locally"; drifted=1
    elif ! diff -rq "$src_path" "$dest/$line" >/dev/null 2>&1; then
      echo "  ✎ $line — modified locally (will be overwritten on the next install)"; drifted=1
    fi
  done < "$dest/.ztp-manifest"
  if [ "$drifted" = 0 ]; then
    echo "✅ $label: matches the method."
  else
    echo "⚠  $label: move these changes upstream into zero-to-prod's src/, or you will lose them."
  fi
}

install_target() {
  case "$1" in
    claude)
      copy_tooling_claude "./.claude"
      sync_templates "$SRC"; assemble_agents_md "$SRC"; warn_agents_local; wire_claude_md
      echo "✅ zero-to-prod installed (Claude, project, version $VERSION). Commands: /ztp-setup … /ztp-ship" ;;
    codex)
      copy_tooling_codex "./.codex"
      sync_templates "$SRC"; assemble_agents_md "$SRC"; warn_agents_local   # AGENTS.md is native to Codex, no CLAUDE.md
      echo "✅ zero-to-prod installed (Codex, project, version $VERSION). Skills: ztp-setup … ztp-ship in .codex/skills." ;;
    all)
      install_target claude
      install_target codex ;;
    *)
      echo "Unknown target: $1 (claude|codex|all)" >&2; exit 1 ;;
  esac
}

case "$MODE" in
  ""|--project)
    install_target "$TARGET"
    if [ "$HOOKS" = 1 ]; then install_hooks; fi
    ;;

  -g|--global)
    # Shared cache (templates + AGENTS.md + installer) for per-project `init`.
    seed_cache() {
      mkdir -p "$CACHE"
      cp -R "$SRC/templates" "$CACHE/"
      cp "$SRC/AGENTS.md" "$CACHE/"
      cp "$PAYLOAD_ROOT/install.sh" "$CACHE/install.sh" 2>/dev/null \
        || cp "${BASH_SOURCE[0]:-$0}" "$CACHE/install.sh" 2>/dev/null || true
    }
    case "$TARGET" in
      claude)
        copy_tooling_claude "$HOME/.claude"; seed_cache
        echo "✅ Tooling installed (global Claude, version $VERSION). Commands available in every repo." ;;
      codex)
        copy_tooling_codex "$HOME/.codex"; seed_cache
        echo "✅ Tooling installed (global Codex, version $VERSION). Skills in ~/.codex/skills." ;;
      all)
        copy_tooling_claude "$HOME/.claude"; copy_tooling_codex "$HOME/.codex"; seed_cache
        echo "✅ Tooling installed (global Claude + Codex, version $VERSION)." ;;
      *) echo "Unknown target: $TARGET (claude|codex|all)" >&2; exit 1 ;;
    esac
    echo "→ In each project: ~/.claude/zero-to-prod/install.sh init [--target codex] [--hooks]"
    ;;

  init)
    # After a --global: lays down the PROJECT files (templates + rules) without touching the
    # tooling already installed globally. That is the only difference with project mode.
    local_src="$SRC"; [ -d "$local_src/templates" ] || local_src="$CACHE"
    sync_templates "$local_src"; assemble_agents_md "$local_src"; warn_agents_local
    case "$TARGET" in claude|all) wire_claude_md ;; esac   # CLAUDE.md only when Claude is a target
    echo "✅ templates + rules added to $(pwd) (target $TARGET)"
    if [ "$HOOKS" = 1 ]; then install_hooks; fi
    ;;

  update)
    install_target "$TARGET"
    echo "✅ zero-to-prod updated ($TARGET, version $VERSION). AGENTS.md rebuilt from the method's rules + your AGENTS.local.md."
    if [ "$HOOKS" = 1 ]; then install_hooks; fi
    ;;

  check)
    check_drift "./.claude" "$SRC" "Claude (.claude)"
    # Codex: the install is transformed at build time, so it cannot be compared to the raw payload.
    # Regenerate the expected output and compare against that.
    if [ -d ./.codex ]; then
      if command -v node >/dev/null 2>&1 && [ -f "$PAYLOAD_ROOT/bin/ztp-build.mjs" ]; then
        stg="$(mktemp -d)"
        node "$PAYLOAD_ROOT/bin/ztp-build.mjs" --target codex --src "$SRC" --out "$stg" >/dev/null
        check_drift "./.codex" "$stg" "Codex (.codex)"
        rm -rf "$stg"
      else
        echo "· Codex (.codex): cannot be checked here (node or bin/ztp-build.mjs missing)."
      fi
    fi
    ;;

  *)
    echo "Unknown option: $MODE" >&2
    echo "Usage: ./install.sh [--target claude|codex|all] [--hooks] [--global | init | update] [--force]" >&2
    exit 1
    ;;
esac
