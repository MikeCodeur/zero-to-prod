#!/usr/bin/env python3
"""Opt-in guards. Project paths/commands come only from AGENTS.local.md."""
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


class Blocked(Exception):
    pass


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise Blocked("cannot inspect git state")
    return result.stdout


def repo_root(cwd):
    return Path(os.fsdecode(git(cwd, "rev-parse", "--show-toplevel")).strip()).resolve()


def settings(root):
    path = root / "AGENTS.local.md"
    if not path.is_file():
        raise Blocked("AGENTS.local.md missing; configure the project before using --hooks")
    values = {}
    keys = {"Secret scan", "Protected paths", "Production commands", "Merge commands", "Merge resolve"}
    for line in path.read_text().splitlines():
        key, sep, value = line.partition(":")
        if sep and key in keys:
            if key in values:
                raise Blocked("duplicate setting: " + key)
            values[key] = value.strip()
    return values


def strings(values, key):
    try:
        result = json.loads(values[key])
    except (KeyError, ValueError):
        raise Blocked(key + " must be an explicit JSON array (use [] for none)")
    if not isinstance(result, list) or any(not isinstance(x, str) or not x for x in result):
        raise Blocked(key + " must contain nonempty strings")
    return result


def protected_patterns(values):
    patterns = strings(values, "Protected paths")
    for pattern in patterns:
        if pattern.startswith("/") or ".." in PurePosixPath(pattern).parts or "\\" in pattern:
            raise Blocked("Protected paths must be repo-relative glob patterns")
    return patterns


def protect(paths, patterns):
    for path in paths:
        for pattern in patterns:
            if (pattern.endswith("/") and (path == pattern[:-1] or path.startswith(pattern))) or fnmatch.fnmatchcase(path, pattern):
                raise Blocked("protected path: " + repr(path))


def declared_command(command, root, env, label):
    if not command or command == "—":
        raise Blocked(label + " is not declared")
    try:
        result = subprocess.run(command, shell=True, cwd=root, env={**os.environ, **env},
                                capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise Blocked(label + " timed out")
    if result.returncode:
        # Scanner output and command strings may contain credentials. Never echo them.
        raise Blocked(label + " failed (exit " + str(result.returncode) + "); output withheld")
    return result.stdout


def pre_commit(root, values):
    paths = [os.fsdecode(p) for p in git(root, "diff", "--cached", "--no-renames", "--name-only", "-z").split(b"\0") if p]
    protect(paths, protected_patterns(values))
    command = values.get("Secret scan")
    if not command or command == "—":
        raise Blocked("Secret scan is required with --hooks; declare a staged-snapshot scanner")
    blobs = {}
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        if stage != b"0":
            raise Blocked("unmerged index")
        blobs[os.fsdecode(path)] = (mode, oid.decode("ascii"))
    with tempfile.TemporaryDirectory(prefix="ztp-staged-") as directory:
        snapshot = Path(directory).resolve()
        for path in paths:
            if path not in blobs:  # A deletion contains nothing to scan.
                continue
            mode, oid = blobs[path]
            if mode == b"160000":  # Gitlink: the referenced repository is not a staged blob.
                continue
            dest = snapshot / path
            if not dest.resolve().is_relative_to(snapshot):
                raise Blocked("invalid index path")
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Symlinks are exported as their literal link text, never followed.
            dest.write_bytes(git(root, "cat-file", "blob", oid))
        declared_command(command, root, {"ZTP_SCAN_DIR": str(snapshot)}, "Secret scan")


def regexes(values, key):
    try:
        return [re.compile(value) for value in strings(values, key)]
    except re.error:
        raise Blocked(key + " contains an invalid regular expression")


def merge_gate(root, branch):
    if not re.fullmatch(r"(?:feature|chore)/[a-zA-Z0-9][a-zA-Z0-9_-]*", branch):
        raise Blocked("merge target unresolved; capture branch or configure Merge resolve")
    lane, identity = branch.split("/", 1)
    # Read the target branch's committed evidence, never the current unrelated worktree.
    if lane == "chore":
        content = git(root, "show", branch + ":docs/plans/" + identity + ".md").decode()
        if not re.search(r"^track:[ \t]*chore[ \t]*$", content, re.M) or not re.search(r"^validated:[ \t]*yes[ \t]*$", content, re.M):
            raise Blocked("chore merge requires its validated chore plan")
    else:
        content = git(root, "show", branch + ":docs/reviews/" + identity + ".md").decode()
        verdicts = re.findall(r"^Ship allowed:[ \t]*(.*?)[ \t]*$", content, re.M)
        if verdicts != ["yes"]:
            raise Blocked("merge requires exactly one Ship allowed: yes for " + identity)


def pre_tool_use(payload):
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PreToolUse":
        raise Blocked("invalid PreToolUse input")
    cwd = Path(payload.get("cwd", ""))
    if not cwd.is_absolute():
        raise Blocked("missing absolute hook cwd")
    root = repo_root(os.environ.get("CLAUDE_PROJECT_DIR") or cwd)
    values = settings(root)
    patterns = protected_patterns(values)
    tool = payload.get("tool_name")
    data = payload.get("tool_input")
    if not isinstance(data, dict):
        raise Blocked("missing tool input")
    if tool in {"Edit", "Write", "MultiEdit"}:
        filename = data.get("file_path")
        if not isinstance(filename, str) or not filename:
            raise Blocked("missing file path")
        path = Path(filename)
        path = path if path.is_absolute() else cwd / path
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise Blocked("edit outside the configured repository")
        protect([os.path.relpath(path, root), resolved.relative_to(root).as_posix()], patterns)
        return
    if tool != "Bash" or not isinstance(data.get("command"), str) or not data["command"].strip():
        raise Blocked("invalid Bash input")
    command = data["command"]
    production = regexes(values, "Production commands")
    merges = regexes(values, "Merge commands")
    if any(pattern.search(command) for pattern in production):
        raise Blocked("command matches a declared Production commands rule")
    for pattern in merges:
        matches = list(pattern.finditer(command))
        for match in matches:
            branch = match.groupdict().get("branch")
            if not branch:
                # A resolver must identify one target for this whole invocation. Do not
                # accidentally authorize several merges from one successful resolution.
                if len(matches) != 1:
                    raise Blocked("multiple merges need explicit branch captures")
                branch = declared_command(values.get("Merge resolve"), root,
                                          {"ZTP_GUARD_COMMAND": command}, "Merge resolve").decode().strip()
            merge_gate(root, branch)


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode == "pre-commit":
        root = repo_root(Path.cwd())
        pre_commit(root, settings(root))
    elif mode == "pre-tool-use":
        pre_tool_use(json.load(sys.stdin))
    else:
        raise Blocked("expected pre-commit or pre-tool-use")


if __name__ == "__main__":
    try:
        main()
    except (Blocked, OSError, ValueError, TypeError, KeyError) as error:
        print("ztp-guard: " + (str(error) if isinstance(error, Blocked) else "invalid input or unavailable control"), file=sys.stderr)
        sys.exit(1)
