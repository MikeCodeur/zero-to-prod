"""Exercise the real replay/CI runners with deterministic fixture agents, never paid calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

METHOD = Path(__file__).resolve().parents[2]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ztp-runtime-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "candidate"
        self.root.mkdir()
        self.cmd("git", "init", "-q", "-b", "main")
        self.cmd("git", "config", "user.name", "ZTP Test")
        self.cmd("git", "config", "user.email", "ztp-test@example.invalid")
        (self.root / "answer.txt").write_text("before")
        (self.root / "rules.md").write_text("old rules")
        self.commit()
        self.base = self.cmd("git", "rev-parse", "HEAD").stdout.strip()
        (self.root / "answer.txt").write_text("accepted")
        self.commit()
        self.accepted = self.cmd("git", "rev-parse", "HEAD").stdout.strip()

    def cmd(self, *args, expected=0, env=None):
        result = subprocess.run(args, cwd=self.root, text=True, capture_output=True,
                                env={**os.environ, **(env or {})})
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def commit(self):
        self.cmd("git", "add", ".")
        self.cmd("git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")

    def eval_setup(self, count=1):
        (self.root / "rules.md").write_text("current rules")
        (self.root / "replay.py").write_text(
            "from pathlib import Path\n"
            "assert Path('rules.md').read_text() == 'current rules'\n"
            "Path('answer.txt').write_text('accepted')\nprint('private agent output')\n")
        (self.root / "check.py").write_text(
            "from pathlib import Path\nassert Path('answer.txt').read_text() == 'accepted'\n")
        (self.root / "AGENTS.local.md").write_text(
            'Eval runner: python3 "$ZTP_EVAL_SOURCE/replay.py"\n'
            'Eval check: python3 "$ZTP_EVAL_SOURCE/check.py"\n'
            'Eval model: fixture-agent\nEval config paths: ["rules.md"]\nEval timeout: 5\n')
        directory = self.root / "docs/evals"
        directory.mkdir(parents=True)
        for n in range(count):
            identity = "case-" + str(n)
            (directory / (identity + ".md")).write_text(
                f"---\nid: {identity}\nbase: {self.base}\naccepted: {self.accepted}\n---\n"
                "## Task\nRestore accepted answer.\n## Expected result\naccepted\n"
                "## Checks\nRead the real output file.\n## Provenance\nFixture accepted commit.\n")

    def replay(self, *args, expected=0):
        return self.cmd("python3", "-B", str(METHOD / "src/tools/ztp-eval.py"), *args, expected=expected)

    def test_replay_uses_historical_base_current_rules_and_real_checker(self):
        self.eval_setup()
        before = (self.root / "answer.txt").read_bytes()
        self.replay("--case", "case-0")
        self.assertEqual((self.root / "answer.txt").read_bytes(), before)
        self.assertEqual(self.cmd("git", "worktree", "list", "--porcelain").stdout.count("worktree "), 1)
        report = next((self.root / "docs/evals/runs").glob("*.md")).read_text()
        self.assertIn("Eval status: passed", report)
        self.assertIn("single-case pilot", report)
        self.assertNotIn("private agent output", report)
        (self.root / "replay.py").write_text("print('done')\n")
        self.replay("--case", "case-0", expected=1)
        reports = sorted((self.root / "docs/evals/runs").glob("*.md"))
        self.assertIn("Eval status: failed", reports[-1].read_text())

    def test_full_suite_enforces_case_count_and_pinned_commits(self):
        self.eval_setup()
        self.replay(expected=1)
        task = self.root / "docs/evals/case-0.md"
        task.write_text(task.read_text().replace(self.base, "main"))
        self.replay("--case", "case-0", expected=1)

    def test_twenty_case_headless_suite(self):
        self.eval_setup(20)
        result = self.replay()
        self.assertIn("20/20 passed", result.stdout)

    def test_timeout_fails_and_cleans_disposable_worktree(self):
        self.eval_setup()
        settings = self.root / "AGENTS.local.md"
        settings.write_text(settings.read_text().replace("Eval timeout: 5", "Eval timeout: 1"))
        (self.root / "replay.py").write_text("import time\ntime.sleep(10)\n")
        self.replay("--case", "case-0", expected=1)
        report = next((self.root / "docs/evals/runs").glob("*.md")).read_text()
        self.assertIn("124", report)
        self.assertEqual(self.cmd("git", "worktree", "list", "--porcelain").stdout.count("worktree "), 1)

    def ci_setup(self):
        (self.root / "AGENTS.local.md").write_text("CI review: no\nCI evals: no\n")
        self.cmd("bash", str(METHOD / "install.sh"), "--target", "all", "--ci")
        self.policy = Path(self.temp.name) / "policy"
        self.policy.mkdir()
        for name in (".ztp-ci", ".ztp-tools", ".claude"):
            shutil.copytree(self.root / name, self.policy / name)
        shutil.copy2(self.root / "AGENTS.local.md", self.policy / "AGENTS.local.md")
        self.cmd("git", "checkout", "--detach", "-q")
        for folder in ("docs/plans", "docs/reviews"):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        (self.root / "docs/plans/s01-demo.md").write_text("---\nvalidated: yes\n---\n")
        (self.root / "docs/reviews/s01-demo.md").write_text("Max severity: none\nShip allowed: yes\n")
        self.commit()

    def ci(self, branch="feature/s01-demo", expected=0):
        return self.cmd("python3", "-B", str(self.policy / ".ztp-ci/ztp-ci.py"),
                        "--branch", branch, "--base", self.base, "--policy", str(self.policy),
                        expected=expected, env={"ZTP_SAME_REPO": "true"})

    def test_ci_uses_trusted_settings_and_preserves_workflow_customization(self):
        self.ci_setup()
        (self.root / "AGENTS.local.md").write_text("CI review: yes\nCI evals: yes\n")
        self.ci()
        (self.root / "docs/reviews/s01-demo.md").write_text("Ship allowed: no\n")
        self.ci(expected=1)
        workflow = self.root / ".github/workflows/ztp.yml"
        workflow.write_text("custom workflow\n")
        self.cmd("bash", str(METHOD / "install.sh"), "--target", "all", "--ci", "update")
        self.assertEqual(workflow.read_text(), "custom workflow\n")

    def test_ci_fresh_review_cannot_reuse_the_committed_verdict(self):
        self.ci_setup()
        (self.policy / "AGENTS.local.md").write_text(
            'CI review: yes\nCI evals: no\nCI review runner: python3 "$ZTP_CI_POLICY/review.py"\n')
        (self.policy / "review.py").write_text(
            "import os\nfrom pathlib import Path\n"
            "Path(os.environ['ZTP_REVIEW_REPORT']).write_text('Review status: complete\\nMax severity: critical\\nShip allowed: no\\n')\n")
        self.ci(expected=1)
        self.assertEqual(self.cmd("git", "worktree", "list", "--porcelain").stdout.count("worktree "), 1)

    def test_ci_review_passes_only_with_fresh_complete_report_and_restored_code(self):
        self.ci_setup()
        (self.policy / "AGENTS.local.md").write_text(
            'CI review: yes\nCI evals: no\nCI review runner: python3 "$ZTP_CI_POLICY/review.py"\n')
        script = ("import os\nfrom pathlib import Path\n"
                  "assert Path(os.environ['ZTP_REVIEW_PROMPT']).is_file()\n"
                  "Path(os.environ['ZTP_REVIEW_REPORT']).write_text('Review status: complete\\nMax severity: none\\nShip allowed: yes\\n')\n")
        (self.policy / "review.py").write_text(script)
        self.ci()
        (self.policy / "review.py").write_text(script + "Path('answer.txt').write_text('mutated')\n")
        self.ci(expected=1)
        self.assertIn("Review status: blocked", (self.root / "docs/reviews/ci/s01-demo.md").read_text())

    def test_init_and_ci_do_not_enable_git_hooks_or_agents(self):
        self.cmd("bash", str(METHOD / "install.sh"), "init", "--target", "codex", "--ci")
        self.assertTrue((self.root / ".ztp-ci/ztp-gate.sh").is_file())
        self.assertTrue((self.root / ".ztp-tools/ztp-eval.py").is_file())
        self.assertFalse((self.root / ".claude").exists())
        self.assertFalse((self.root / "AGENTS.local.md").exists())
        self.cmd("git", "config", "--get", "core.hooksPath", expected=1)


if __name__ == "__main__":
    unittest.main()
