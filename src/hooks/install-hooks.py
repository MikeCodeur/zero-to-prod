#!/usr/bin/env python3
"""Install project guardrails; preserve existing Git hooks and Claude settings."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def install(source, target):
    root = Path.cwd().resolve()
    destination = root / ".ztp-hooks"
    config_path = root / ".claude/settings.json"
    config = None
    hook_command = 'bash "$CLAUDE_PROJECT_DIR/.ztp-hooks/ztp-guard.sh" pre-tool-use'
    if target in {"claude", "all"}:
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        if not isinstance(config, dict) or config.get("disableAllHooks"):
            raise ValueError("Claude settings must be an object with hooks enabled")
        hooks = config.setdefault("hooks", {})
        if not isinstance(hooks, dict):
            raise ValueError("Claude hooks must be an object")
        entries = hooks.setdefault("PreToolUse", [])
        if not isinstance(entries, list):
            raise ValueError("Claude PreToolUse must be an array")
        existing = [h for entry in entries if isinstance(entry, dict)
                    for h in entry.get("hooks", []) if isinstance(h, dict)]
        if not any(h.get("command") == hook_command for h in existing):
            entries.append({"matcher": "Bash|Edit|Write|MultiEdit", "hooks": [
                {"type": "command", "command": hook_command, "timeout": 70}]})
    current = subprocess.run(["git", "config", "--get", "core.hooksPath"], capture_output=True, text=True)
    if current.returncode not in {0, 1}:
        raise ValueError("cannot read core.hooksPath")
    previous = current.stdout.strip()
    marker = destination / ".previous-hooks-path"
    if previous == ".ztp-hooks":
        previous = marker.read_text().strip() if marker.exists() else ""
    elif not previous:
        previous = str(Path(subprocess.check_output(["git", "rev-parse", "--git-path", "hooks"], text=True).strip()).resolve())
    if "\n" in previous:
        raise ValueError("multiline hooks path unsupported")
    previous_dir = Path(previous) if previous else None
    if previous_dir and not previous_dir.is_absolute():
        previous_dir = root / previous_dir
    if previous_dir and previous_dir.resolve() == destination:
        raise ValueError("previous hooks path loops back into .ztp-hooks")
    destination.mkdir(exist_ok=True)
    if previous:
        marker.write_text(previous + "\n")
    for name in ("ztp-gate.sh", "ztp-guard.sh", "ztp-guard.py", "ztp-prior-hook.sh", "pre-commit"):
        shutil.copyfile(source / name, destination / name)
        (destination / name).chmod(0o755)
    if previous_dir and previous_dir.is_dir():
        for hook in previous_dir.iterdir():
            if hook.name == "pre-commit" or hook.name.endswith(".sample") or not hook.is_file() or not os.access(hook, os.X_OK):
                continue
            link = destination / hook.name
            if not link.exists() and not link.is_symlink():
                link.symlink_to("ztp-prior-hook.sh")
    if config is not None:
        config_path.parent.mkdir(exist_ok=True)
        temporary = config_path.with_suffix(".ztp-tmp")
        temporary.write_text(json.dumps(config, indent=2) + "\n")
        temporary.replace(config_path)
    subprocess.run(["git", "config", "core.hooksPath", ".ztp-hooks"], check=True)
    print("✅ Git guards installed: staged secrets, declared protected paths, existing plan gate.")
    if config is not None:
        print("✅ Claude PreToolUse guard installed; existing settings preserved.")
    print("   Configure Secret scan and guard arrays in AGENTS.local.md before committing.")
    print("   Command rules cover only declared patterns, not arbitrary shell equivalents.")
    print("   Previous Git hooks retained; path recorded in .ztp-hooks/.previous-hooks-path.")


if __name__ == "__main__":
    try:
        install(Path(sys.argv[1]), sys.argv[2])
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
        print("ztp-hooks: installation failed: " + str(error), file=sys.stderr)
        sys.exit(1)
