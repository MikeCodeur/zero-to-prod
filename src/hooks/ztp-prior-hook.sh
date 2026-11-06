#!/usr/bin/env bash
# Preserve the project's previous hooks without editing their directory.
set -euo pipefail
hook_dir="$(cd "$(dirname "$0")" && pwd)"
hook_name="$(basename "$0")"
if [ "$hook_name" = ztp-prior-hook.sh ]; then hook_name="$1"; shift; fi
[ -f "$hook_dir/.previous-hooks-path" ] || exit 0
IFS= read -r previous < "$hook_dir/.previous-hooks-path"
case "$previous" in
  /*) ;;
  *) previous="$(git rev-parse --show-toplevel)/$previous" ;;
esac
if [ -x "$previous/$hook_name" ]; then exec "$previous/$hook_name" "$@"; fi
