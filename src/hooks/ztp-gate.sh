#!/usr/bin/env bash
# ztp-gate — zero-to-prod repo-level guardrails, enforced by git (tool-independent).
# Works the same whether the harness is Claude Code or Codex:
# the gates live in the repo, not in a tool's per-command permissions.
#
# Subcommands:
#   ztp-gate design-validated <id>   exit 0 if docs/designs/<id>/design.md has `validated: yes`
#   ztp-gate plan-validated <id>     exit 0 if docs/plans/<id>.md has `validated: yes`
#   ztp-gate acceptance-tests <id>   exit 0 if the plan maps each story criterion to exactly one row, within `Test budget`
#   ztp-gate ship-allowed  <id>      exit 0 if docs/reviews/<id>.md has `Ship allowed: yes`
#   ztp-gate verif-current <id>      exit 0 if docs/verif/<id>.md proves the CURRENT code was verified
#   ztp-gate verif-clean             exit 0 if docs/verif/ holds only .md records at its root
#   ztp-gate tests-frozen  <id>      exit 0 if the validated acceptance tests are unchanged since their test(<id>) commit
#   ztp-gate pre-commit              block a code commit on feature/<id> or chore/<id> without a validated plan
#
# There is no push-time gate: /ztp-ship squash-merges, so a merged story leaves no merge
# commit to detect client-side. Enforce `ztp-gate ship-allowed <id>` in CI / branch protection.
set -euo pipefail

repo_root() { git rev-parse --show-toplevel 2>/dev/null || pwd; }

# Extract the story or chore id from a `feature/<id>` or `chore/<id>` branch name; empty otherwise.
story_id_from_branch() {
  local branch="$1"
  case "$branch" in
    feature/*) printf '%s' "${branch#feature/}" ;;
    chore/*)   printf '%s' "${branch#chore/}" ;;
    *) printf '' ;;
  esac
}

design_validated() {
  local id="$1" root; root="$(repo_root)"
  local f="$root/docs/designs/$id/design.md"
  [ -f "$f" ] || { echo "ztp-gate: no design for '$id' (docs/designs/$id/design.md missing). Run /ztp-design $id." >&2; return 1; }
  if grep -qE '^validated:[[:space:]]*yes[[:space:]]*$' "$f"; then
    return 0
  fi
  echo "ztp-gate: design '$id' not validated (docs/designs/$id/design.md lacks 'validated: yes'). Validate it via /ztp-design $id." >&2
  return 1
}

plan_validated() {
  local id="$1" root; root="$(repo_root)"
  local f="$root/docs/plans/$id.md"
  [ -f "$f" ] || { echo "ztp-gate: no plan for '$id' (docs/plans/$id.md missing). Run /ztp-plan $id — or /ztp-chore for a chore." >&2; return 1; }
  if grep -qE '^validated:[[:space:]]*yes[[:space:]]*$' "$f"; then
    return 0
  fi
  echo "ztp-gate: plan '$id' not validated (docs/plans/$id.md lacks 'validated: yes'). Validate it via /ztp-plan $id." >&2
  return 1
}

# The plan's "Acceptance tests" table: exactly one row per criterion of the story (docs/tickets/<id>.md
# when it exists, else the story's section of docs/stories.md), no row for a criterion the story does
# not have, and no more test rows than `Test budget` in AGENTS.local.md (25 when absent). The only
# budget is that setting: a plan cannot raise it. A purely visual criterion's row says `UI check` in
# its test column, and counts as its row but not as a test.
acceptance_tests() {
  local id="$1" root; root="$(repo_root)"
  local plan="$root/docs/plans/$id.md" source criteria rows budget
  [ -f "$plan" ] || { echo "ztp-gate: no plan for '$id' (docs/plans/$id.md missing). Run /ztp-plan $id." >&2; return 1; }
  if [ -f "$root/docs/tickets/$id.md" ]; then
    source="docs/tickets/$id.md"
    criteria="$(awk '/^## /{on=($0 ~ /^## Acceptance criteria/)} on && /^[[:space:]]*- / && match($0,/AC[0-9]+/){print substr($0,RSTART,RLENGTH)}' "$root/$source")"
  elif [ -f "$root/docs/stories.md" ]; then
    source="docs/stories.md"
    criteria="$(awk -v id="$id" '
      /^## /{ story=(index($0, "## Story " id " ")==1 || $0=="## Story " id); crit=0; next }
      story && /^### /{ crit=($0 ~ /^### Acceptance criteria/); next }
      story && crit && /^[[:space:]]*- / && match($0,/AC[0-9]+/){ print substr($0,RSTART,RLENGTH) }' "$root/$source")"
  else
    echo "ztp-gate: no work source for '$id' (neither docs/tickets/$id.md nor docs/stories.md)." >&2; return 1
  fi
  [ -n "$criteria" ] || { echo "ztp-gate: no acceptance criterion found for '$id' in $source." >&2; return 1; }
  # One line per table row: <criterion id or ?>\t<ui|test>
  rows="$(awk '
    /^## /{ on=($0 ~ /^## Acceptance tests/); next }
    on && /^[[:space:]]*\|/ {
      n=split($0, c, "|"); crit=c[2]; test=c[3]
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", crit); gsub(/[`*[:space:]]+/, " ", test); sub(/^ /, "", test)
      if (crit=="Criterion" || crit ~ /^:?-+:?$/) next
      kind=(tolower(test) ~ /^ui check/) ? "ui" : "test"
      if (match(crit, /AC[0-9]+/)) print substr(crit,RSTART,RLENGTH) "\t" kind; else print "?\t" kind
    }' "$plan")"
  budget="$(sed -n 's/^Test budget:[[:space:]]*\([0-9][0-9]*\)[[:space:]]*$/\1/p' "$root/AGENTS.local.md" 2>/dev/null | head -n1)"
  budget="${budget:-25}"
  local fail=0 ac count tests
  [ -n "$rows" ] || { echo "ztp-gate: docs/plans/$id.md has no \"Acceptance tests\" table rows." >&2; return 1; }
  if printf '%s\n' "$rows" | grep -q '^?'; then
    echo "ztp-gate: a row of the \"Acceptance tests\" table names no criterion id (ACn)." >&2; fail=1
  fi
  for ac in $criteria; do
    count="$(printf '%s\n' "$rows" | awk -F'\t' -v ac="$ac" '$1==ac' | wc -l | tr -d ' ')"
    if [ "$count" = 0 ]; then echo "ztp-gate: $ac of $source has no row in the plan's \"Acceptance tests\" table." >&2; fail=1
    elif [ "$count" -gt 1 ]; then echo "ztp-gate: $ac has $count rows — one criterion, one test (or one UI check)." >&2; fail=1; fi
  done
  for ac in $(printf '%s\n' "$rows" | cut -f1 | grep -v '^?' | sort -u); do
    printf '%s\n' "$criteria" | grep -qx "$ac" || { echo "ztp-gate: the table has a row for $ac, which $source does not list." >&2; fail=1; }
  done
  tests="$(printf '%s\n' "$rows" | awk -F'\t' '$2=="test"' | wc -l | tr -d ' ')"
  if [ "$tests" -gt "$budget" ]; then
    echo "ztp-gate: $tests acceptance tests, above Test budget $budget (AGENTS.local.md). A plan cannot raise it." >&2; fail=1
  fi
  return "$fail"
}

ship_allowed() {
  local id="$1" root; root="$(repo_root)"
  local f="$root/docs/reviews/$id.md"
  [ -f "$f" ] || { echo "ztp-gate: no review for '$id' (docs/reviews/$id.md missing). Run /ztp-review $id." >&2; return 1; }
  if grep -qE '^Ship allowed:[[:space:]]*yes[[:space:]]*$' "$f"; then
    return 0
  fi
  echo "ztp-gate: ship blocked for '$id' (docs/reviews/$id.md is not 'Ship allowed: yes')." >&2
  return 1
}

# The implementer records what it ran in docs/verif/<id>.md, with the tree it ran against.
# This says whether that record still describes the committed code: same tree outside docs/.
# docs/ is excluded because the plan's ticked checkboxes are written after the run — the same
# carve-out pre_commit() makes for docs-only commits. The record itself is gitignored: read
# from the worktree, never part of a tree, absent on a fresh clone or in CI.
# docs/verif/ holds the records and nothing else: one <id>.md per story or chore, at its root.
# Screenshots, logs, JSON, scripts belong in .ztp/evidence/<id>/. Called by verif_current, so a
# cluttered folder never yields a trusted record. .DS_Store, written by macOS, is tolerated.
verif_clean() {
  local root dir extra; root="$(repo_root)"; dir="$root/docs/verif"
  [ -d "$dir" ] || return 0
  extra="$(find "$dir" -mindepth 1 \( -type d -o ! -name '*.md' \) ! -name .DS_Store -print | sed "s|^$root/||" | sort)"
  [ -z "$extra" ] && return 0
  echo "ztp-gate: docs/verif/ holds only <id>.md records. Move these to .ztp/evidence/<id>/:" >&2
  printf '%s\n' "$extra" | sed 's/^/  /' >&2
  return 1
}

verif_current() {
  local id="$1" root; root="$(repo_root)"
  verif_clean || return 1
  local f="$root/docs/verif/$id.md"
  [ -f "$f" ] || { echo "ztp-gate: no verification record for '$id' (docs/verif/$id.md missing — it is local, never committed: absent on a fresh clone or in CI). Rerun the checks." >&2; return 1; }
  if ! grep -qE '^Verification status:[[:space:]]*complete[[:space:]]*$' "$f"; then
    echo "ztp-gate: verification record for '$id' is not complete (docs/verif/$id.md lacks 'Verification status: complete')." >&2
    return 1
  fi
  local tree
  tree="$(sed -n 's/^Tree:[[:space:]]*\([0-9a-f]\{40\}\).*/\1/p' "$f" | head -1)"
  [ -n "$tree" ] || { echo "ztp-gate: verification record for '$id' has no valid 'Tree:' line." >&2; return 1; }
  if ! git cat-file -e "$tree^{tree}" 2>/dev/null; then
    echo "ztp-gate: tree $tree recorded for '$id' is not in this repository." >&2
    return 1
  fi
  if ! git diff --quiet "$tree" HEAD -- . ':(exclude)docs' 2>/dev/null; then
    echo "ztp-gate: code changed after verification for '$id' — the record no longer describes HEAD. Rerun the checks." >&2
    return 1
  fi
  return 0
}

# The acceptance tests are committed alone as `test(<id>): acceptance tests`, then validated.
# The commit is found in the history rather than stored by hand: one source of error fewer.
# Its frozen files, listed in docs/tests/<id>.md, must be identical at HEAD.
tests_frozen() {
  local id="$1" root sha line; root="$(repo_root)"
  local f="$root/docs/tests/$id.md"
  [ -f "$f" ] || { echo "ztp-gate: no acceptance tests for '$id' (docs/tests/$id.md missing)." >&2; return 1; }
  if ! grep -qE '^validated:[[:space:]]*yes[[:space:]]*$' "$f"; then
    echo "ztp-gate: acceptance tests for '$id' are not validated (docs/tests/$id.md lacks 'validated: yes')." >&2
    return 1
  fi
  sha="$(git -C "$root" log -1 --format=%H --fixed-strings --grep="test($id): acceptance tests" HEAD 2>/dev/null || true)"
  [ -n "$sha" ] || { echo "ztp-gate: no 'test($id): acceptance tests' commit in the history." >&2; return 1; }
  set --
  while IFS= read -r line; do set -- "$@" "$line"; done < <(
    awk '/^## /{inside=($0=="## Frozen files")} inside && /^- /{sub(/^- /,""); sub(/[ \t]+$/,""); print}' "$f")
  [ "$#" -gt 0 ] || { echo "ztp-gate: docs/tests/$id.md lists no frozen files." >&2; return 1; }
  for line in "$@"; do
    git -C "$root" cat-file -e "$sha:$line" 2>/dev/null || {
      echo "ztp-gate: frozen file '$line' is not in the test($id) commit ${sha:0:12}." >&2; return 1; }
  done
  if ! git -C "$root" diff --quiet "$sha" HEAD -- "$@"; then
    echo "ztp-gate: frozen acceptance tests of '$id' changed since ${sha:0:12}:" >&2
    git -C "$root" diff --name-status "$sha" HEAD -- "$@" >&2
    return 1
  fi
  return 0
}

pre_commit() {
  local branch id; branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
  id="$(story_id_from_branch "$branch")"
  # Not on a story branch → nothing to enforce here.
  [ -n "$id" ] || return 0
  # Any staged path outside docs/ counts as code/config work.
  local code_staged=0 path
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    case "$path" in
      docs/*) : ;;
      *) code_staged=1 ;;
    esac
  done < <(git diff --cached --name-only)
  [ "$code_staged" = 1 ] || return 0
  if ! plan_validated "$id"; then
    echo "ztp-gate: refusing code commit on $branch — no validated plan. (docs-only commits are always allowed.)" >&2
    return 1
  fi
  return 0
}

cmd="${1:-}"
case "$cmd" in
  design-validated) design_validated "${2:?story id required}" ;;
  plan-validated)  plan_validated "${2:?story id required}" ;;
  acceptance-tests) acceptance_tests "${2:?story id required}" ;;
  ship-allowed)    ship_allowed   "${2:?story id required}" ;;
  verif-current)   verif_current  "${2:?story id required}" ;;
  verif-clean)     verif_clean ;;
  tests-frozen)    tests_frozen   "${2:?story id required}" ;;
  pre-commit)      pre_commit ;;
  *)
    echo "usage: ztp-gate {design-validated <id>|plan-validated <id>|acceptance-tests <id>|ship-allowed <id>|verif-current <id>|verif-clean|tests-frozen <id>|pre-commit}" >&2
    exit 2
    ;;
esac
