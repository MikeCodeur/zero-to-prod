#!/usr/bin/env bash
# Claude treats most nonzero exits as non-blocking: translate every failure to exit 2.
set -u
mode="${1:-}"
if command -v python3 >/dev/null 2>&1 && python3 "$(dirname "$0")/ztp-guard.py" "$@"; then
  exit 0
fi
echo "ztp-guard: control failed; action blocked. Check Python 3 and AGENTS.local.md." >&2
if [ "$mode" = pre-tool-use ]; then exit 2; fi
exit 1
