#!/usr/bin/env python3
"""PR gates and opt-in fresh review/evals. No publish, merge or build repair."""
import argparse
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile


def execute(args, cwd):
    subprocess.run(args, cwd=cwd, check=True)


def read_settings(path):
    result = {}
    if not path.is_file():
        return result
    for line in path.read_text().splitlines():
        key, sep, value = line.partition(":")
        if sep and key in {"CI review", "CI evals", "CI review runner"}:
            if key in result:
                raise ValueError("duplicate CI setting")
            result[key] = value.strip()
    return result


def enabled(values, key):
    value = values.get(key, "no")  # An absent opt-in never runs an agent.
    if value not in {"yes", "no"}:
        raise ValueError(key + " must be yes or no")
    return value == "yes"


def fresh_review(root, policy, identity, branch, base, command):
    if not command or command == "—":
        raise ValueError("CI review runner is not declared")
    contracts = [policy / ".claude/agents/reviewer.md", policy / ".codex/skills/reviewer/SKILL.md"]
    contract = next((path for path in contracts if path.is_file()), None)
    if contract is None:
        raise ValueError("no installed reviewer contract in CI policy")
    workspace = root / ".worktrees" / identity
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("CI review workspace already exists")
    reports = root / "docs/reviews/ci"
    reports.mkdir(parents=True, exist_ok=True)
    report = reports / (identity + ".md")
    if report.exists():
        report.unlink()  # Never accept a report supplied by the PR as the fresh result.
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    execute(["git", "worktree", "add", "-b", branch, str(workspace), "HEAD"], root)
    try:
        with tempfile.TemporaryDirectory(prefix="ztp-ci-review-") as directory:
            prompt = Path(directory) / "prompt.md"
            prompt.write_text(
                "Review " + identity + " in a fresh, non-resumed context. Read " + str(contract) +
                " and its preloaded skills from the trusted policy at " + str(policy) +
                ". Read approved review rules from that policy, not a PR-authored replacement.\n"
                "Working directory: " + str(workspace) + "; branch: " + branch +
                ". Diff: git diff " + base + "...HEAD. Apply the existing review procedure, "
                "including neutralization and restoration. This CI pass writes its full report "
                "only to " + str(report) + ". Never copy the PR's earlier verdict.\n"
                "End with Review status: complete, Max severity: <critical|major|minor|none>, "
                "and Ship allowed: <yes|no>. An incomplete review blocks. No merge or deploy.\n")
            env = {**os.environ, "ZTP_CI_POLICY": str(policy), "ZTP_REVIEW_ID": identity,
                   "ZTP_REVIEW_BASE": base, "ZTP_REVIEW_HEAD": head,
                   "ZTP_REVIEW_PROMPT": str(prompt), "ZTP_REVIEW_REPORT": str(report)}
            with (Path(directory) / "output").open("wb") as output:
                process = subprocess.Popen(command, shell=True, cwd=workspace, env=env,
                                           stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=900)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise ValueError("CI review timed out")
            if code:
                raise ValueError("CI review runner failed (exit " + str(code) + "); raw output withheld")
        execute(["git", "diff", "--exit-code"], workspace)
        execute(["git", "diff", "--cached", "--exit-code"], workspace)
        if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=workspace, text=True).strip() != head:
            raise ValueError("CI reviewer changed the reviewed commit")
        content = report.read_text()
        if re.findall(r"^Ship allowed:\s*(yes|no)\s*$", content, re.M) != ["yes"] or not re.search(r"^Review status: complete\s*$", content, re.M):
            raise ValueError("CI review missing, incomplete or negative")
        if re.findall(r"^Max severity:\s*(critical|major|minor|none)\s*$", content, re.M) not in [["major"], ["minor"], ["none"]]:
            raise ValueError("CI review has a critical or malformed severity")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        previous = report.read_text() if report.is_file() else ""
        if not ("Review status: complete" in previous and "Ship allowed: no" in previous):
            report.write_text("# CI review — " + identity + "\n\nReview status: blocked\n\n"
                              "## Failure cause\n" + str(error) + "\n\n"
                              "## Missing\nA complete independent review and restored checkout.\n\n"
                              "## Required adaptation\nRepair the declared CI runner/access and rerun this job.\n\n"
                              "Max severity: critical\nShip allowed: no\n")
        raise
    finally:
        execute(["git", "worktree", "remove", "--force", str(workspace)], root)
        execute(["git", "branch", "-D", branch], root)


def run(branch, base, policy):
    root = Path.cwd().resolve()
    policy = policy.resolve()
    gate = policy / ".ztp-ci/ztp-gate.sh"
    if not gate.is_file():
        raise ValueError("trusted base has no installed CI gate; complete the reviewed CI bootstrap first")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", base):
        raise ValueError("base must be a full commit SHA")
    match = re.fullmatch(r"(feature|chore)/([a-zA-Z0-9][a-zA-Z0-9_-]*)", branch)
    identity = None
    if match:
        lane, identity = match.groups()
        execute(["bash", str(gate), "plan-validated", identity], root)
        if lane == "feature":
            execute(["bash", str(gate), "ship-allowed", identity], root)
        else:
            plan = (root / "docs/plans" / (identity + ".md")).read_text()
            if not re.search(r"^track:\s*chore\s*$", plan, re.M):
                raise ValueError("a chore PR needs a chore plan")
    else:
        paths = subprocess.check_output(["git", "diff", "--name-only", "-z", base + "...HEAD"], cwd=root).split(b"\0")
        if any(path and not path.startswith(b"docs/") for path in paths):
            raise ValueError("non-docs PR needs a feature/<id> or chore/<id> branch")
        execute(["bash", str(gate), "pre-commit"], root)
    values = read_settings(policy / "AGENTS.local.md")
    review = enabled(values, "CI review")
    evals = enabled(values, "CI evals")
    if (review or evals) and os.environ.get("ZTP_SAME_REPO") != "true":
        raise ValueError("agent jobs require a trusted same-repository run; never expose keys to a fork")
    if review and match and match.group(1) == "feature":
        fresh_review(root, policy, identity, branch, base, values.get("CI review runner"))
    if evals:
        execute(["python3", str(policy / ".ztp-tools/ztp-eval.py")], root)
    print("ztp-ci: gates passed; review=" + str(review) + ", evals=" + str(evals))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--policy", required=True, type=Path)
    args = parser.parse_args()
    try:
        run(args.branch, args.base, args.policy)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("ztp-ci: blocked — " + str(error))
        raise SystemExit(1)
