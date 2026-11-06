#!/usr/bin/env python3
"""Headless regression replay using only declared project commands (Python 3.9+)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode().strip()


def read_settings(path):
    values = {}
    for line in path.read_text().splitlines():
        key, sep, value = line.partition(":")
        if sep and key.startswith("Eval "):
            if key in values:
                raise ValueError("duplicate setting: " + key)
            values[key] = value.strip()
    for key in ("Eval runner", "Eval check", "Eval model", "Eval config paths", "Eval timeout"):
        if not values.get(key) or values[key] == "—":
            raise ValueError("missing " + key)
    if not values["Eval timeout"].isdigit() or int(values["Eval timeout"]) < 1:
        raise ValueError("Eval timeout must be positive seconds")
    return values


def configuration(root, values):
    paths = json.loads(values["Eval config paths"])
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) or not p for p in paths):
        raise ValueError("Eval config paths must be a nonempty JSON array")
    digest = hashlib.sha256(json.dumps(values, sort_keys=True).encode())
    for name in paths:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or relative == Path(".") or relative.parts[0] in {".git", ".worktrees"}:
            raise ValueError("invalid configuration path")
        source = root / relative
        if not source.exists() or source.is_symlink() or not source.resolve().is_relative_to(root):
            raise ValueError("configuration missing or outside repository: " + name)
        entries = sorted(source.rglob("*")) if source.is_dir() else [source]
        for entry in entries:
            if entry.is_symlink():
                raise ValueError("configuration symlinks are not replayable")
            if entry.is_file():
                digest.update(str(entry.relative_to(root)).encode())
                digest.update(entry.read_bytes())
    return paths, digest.hexdigest()


def task(root, path):
    text = path.read_text()
    front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not front:
        raise ValueError("missing task frontmatter: " + path.name)
    fields = {}
    for line in front.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            if key in fields:
                raise ValueError("duplicate task field")
            fields[key] = value.strip()
    identity = fields.get("id", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", identity) or path.stem != identity:
        raise ValueError("task id must match its filename")
    for key in ("base", "accepted"):
        sha = fields.get(key, "")
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", sha):
            raise ValueError("task needs full base/accepted commit hashes")
        git(root, "cat-file", "-e", sha + "^{commit}")
    for heading in ("## Task", "## Expected result", "## Checks", "## Provenance"):
        if heading not in text:
            raise ValueError("missing " + heading + " in " + path.name)
    return fields


def invoke(command, cwd, env, output, timeout):
    # A timeout kills this disposable command's process group, not only its parent shell.
    with output.open("wb") as out, output.with_suffix(".stderr").open("wb") as err:
        process = subprocess.Popen(command, shell=True, cwd=cwd, env=env,
                                   stdout=out, stderr=err, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124


def overlay(root, worktree, paths):
    for name in paths:
        source, destination = root / name, worktree / name
        if not destination.parent.resolve().is_relative_to(worktree):
            raise ValueError("historical configuration path escapes replay")
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        elif destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)


def run(case=None):
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
    values = read_settings(root / "AGENTS.local.md")
    paths, fingerprint = configuration(root, values)
    candidates = sorted((root / "docs/evals").glob("*.md"))
    if case:
        candidates = [p for p in candidates if p.stem == case]
        if len(candidates) != 1:
            raise ValueError("unknown eval case")
    elif not 20 <= len(candidates) <= 50:
        raise ValueError("a full suite needs 20–50 accepted tasks; use --case for a pilot")
    tasks = [(p, task(root, p)) for p in candidates]
    task_fingerprint = hashlib.sha256(b"".join(p.read_bytes() for p, _ in tasks)).hexdigest()
    rows = []
    with tempfile.TemporaryDirectory(prefix="ztp-evals-") as directory:
        scratch = Path(directory).resolve()
        for path, fields in tasks:
            identity = fields["id"]
            worktree = scratch / identity
            runner_exit = check_exit = "not run"
            status = "blocked"
            added = False
            try:
                git(root, "worktree", "add", "--detach", str(worktree), fields["base"])
                added = True
                overlay(root, worktree, paths)
                frozen_task = scratch / (identity + ".md")
                frozen_task.write_bytes(path.read_bytes())
                frozen_task.chmod(0o444)
                result = scratch / (identity + ".result")
                env = {**os.environ, "ZTP_EVAL_TASK": str(frozen_task),
                       "ZTP_EVAL_RESULT": str(result), "ZTP_EVAL_MODEL": values["Eval model"],
                       "ZTP_EVAL_WORKTREE": str(worktree), "ZTP_EVAL_SOURCE": str(root),
                       "ZTP_EVAL_ACCEPTED": fields["accepted"]}
                timeout = int(values["Eval timeout"])
                runner_exit = invoke(values["Eval runner"], worktree, env, result, timeout)
                if runner_exit == 0:
                    check_exit = invoke(values["Eval check"], worktree, env,
                                        scratch / (identity + ".check"), timeout)
                status = "passed" if runner_exit == 0 and check_exit == 0 else "failed"
            except (OSError, ValueError, subprocess.SubprocessError):
                status = "blocked"
            finally:
                if added:
                    try:
                        # Only our own registered disposable worktree is discarded.
                        git(root, "worktree", "remove", "--force", str(worktree))
                    except subprocess.SubprocessError:
                        status = "blocked"
            rows.append((identity, fields["base"], fields["accepted"], runner_exit, check_exit, status))
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    reports = root / "docs/evals/runs"
    reports.mkdir(parents=True, exist_ok=True)
    report = reports / (now + ".md")
    passed = all(row[-1] == "passed" for row in rows)
    text = ("# Agent evals — " + now + "\n\nEval status: " + ("passed" if passed else "failed") +
            "\nScope: " + ("single-case pilot" if case else "suite") +
            "\nModel: " + values["Eval model"] + "\nConfiguration: " + fingerprint +
            "\nTask set: " + task_fingerprint + "\nCases: " + str(len(rows)) +
            "\n\n| Case | Base / accepted | Runner exit | Check exit | Result |\n|---|---|---|---|---|\n")
    for identity, base, accepted, runner_exit, check_exit, status in rows:
        text += f"| {identity} | {base} / {accepted} | {runner_exit} | {check_exit} | {status} |\n"
    text += ("\n## Comparison\nEach case must still meet its accepted result. Compare prior reports only after\n"
             "checking identical task sets and checker code; a single-case pilot is not a suite pass.\n"
             "\n## Not verified\nNo production behavior or credential isolation is proven by a worktree.\n"
             "The declared runner owns the sandbox/model selection. Raw model output is not retained.\n")
    report.write_text(text)
    print(str(report))
    print(str(sum(row[-1] == "passed" for row in rows)) + "/" + str(len(rows)) + " passed")
    return 0 if passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="replay one known case as a pilot")
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.case))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("ztp-eval: blocked — " + str(error))
        raise SystemExit(1)
