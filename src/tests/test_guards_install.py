"""Integration checks on disposable repositories, no external service or real credential."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

METHOD = Path(__file__).resolve().parents[2]
GUARD = METHOD / "src/hooks/ztp-guard.sh"


class Repository(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ztp-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_command("git", "init", "-q", "-b", "main")
        self.run_command("git", "config", "user.name", "ZTP Test")
        self.run_command("git", "config", "user.email", "ztp-test@example.invalid")
        self.values = {
            "Secret scan": 'python3 scan.py',
            "Protected paths": '[]',
            "Production commands": json.dumps([r"prod-db\b"]),
            "Merge commands": json.dumps([r"merge-tool (?P<branch>(?:feature|chore)/[\w-]+)"]),
            "Merge resolve": "—",
        }
        self.write_settings()
        (self.root / "scan.py").write_text(
            "import os,pathlib,sys\n"
            "assert 'ZTP_SCAN_DIR' in os.environ\n"
            "sys.exit(any(b'ZTP_TEST_SECRET' in p.read_bytes() for p in "
            "pathlib.Path(os.environ['ZTP_SCAN_DIR']).rglob('*') if p.is_file()))\n")
        (self.root / "file.txt").write_text("clean")
        self.commit()

    def run_command(self, *args, input=None, expected=0, env=None):
        result = subprocess.run(args, cwd=self.root, input=input, text=True,
                                capture_output=True, env={**os.environ, **(env or {})})
        if expected is not None:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def write_settings(self):
        (self.root / "AGENTS.local.md").write_text(
            "\n".join(k + ": " + v for k, v in self.values.items()) + "\n")

    def commit(self):
        self.run_command("git", "add", ".")
        self.run_command("git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")

    def hook(self, command="harmless", *, expected=0, tool="Bash", path=None):
        data = {"command": command} if tool == "Bash" else {"file_path": str(path)}
        return self.run_command("bash", str(GUARD), "pre-tool-use", expected=expected,
                                input=json.dumps({"hook_event_name": "PreToolUse", "cwd": str(self.root),
                                                  "tool_name": tool, "tool_input": data}),
                                env={"CLAUDE_PROJECT_DIR": str(self.root)})

    def precommit(self, expected=0):
        return self.run_command("bash", str(GUARD), "pre-commit", expected=expected)

    def install(self, target="all", *flags, expected=0):
        return self.run_command("bash", str(METHOD / "install.sh"), "--target", target,
                                *flags, expected=expected)

    def test_index_not_working_copy_is_scanned_and_output_is_redacted(self):
        file = self.root / "file.txt"
        file.write_text("ZTP_TEST_SECRET")
        self.run_command("git", "add", "file.txt")
        file.write_text("clean again")
        result = self.precommit(expected=1)
        self.assertIn("Secret scan failed", result.stderr)
        self.assertNotIn("ZTP_TEST_SECRET", result.stdout + result.stderr)
        self.run_command("git", "add", "file.txt")
        file.write_text("ZTP_TEST_SECRET")
        self.precommit()

    def test_missing_failed_scanner_and_invalid_config_block(self):
        for value in ("—", "", "nonexistent-ztp-scanner", "exit 9"):
            with self.subTest(value=value):
                self.values["Secret scan"] = value
                self.write_settings()
                self.precommit(expected=1)
        self.values["Protected paths"] = "not json"
        self.write_settings()
        self.precommit(expected=1)
        self.hook(expected=2)
        (self.root / "AGENTS.local.md").unlink()
        self.hook(expected=2)

    def test_protected_rename_and_deletion(self):
        self.values["Protected paths"] = '["file.txt"]'
        self.write_settings()
        self.run_command("git", "mv", "file.txt", "renamed.txt")
        self.precommit(expected=1)
        self.hook(tool="Write", path=self.root / "file.txt", expected=2)

    def test_symlink_edits_cannot_bypass_protected_target(self):
        self.values["Protected paths"] = '["file.txt"]'
        self.write_settings()
        (self.root / "alias.txt").symlink_to("file.txt")
        self.hook(tool="Edit", path=self.root / "alias.txt", expected=2)

    def test_staged_names_with_spaces_newlines_and_symlinks(self):
        (self.root / "space and\nnewline").write_text("ZTP_TEST_SECRET")
        self.run_command("git", "add", ".")
        self.precommit(expected=1)
        (self.root / "space and\nnewline").write_text("safe")
        (self.root / "outside-link").symlink_to("/outside/never-read")
        self.run_command("git", "add", ".")
        self.precommit()

    def test_production_patterns_and_malformed_hook_fail_closed(self):
        self.hook("echo before && prod-db --connect", expected=2)
        self.hook("test-runner")
        self.run_command("bash", str(GUARD), "pre-tool-use", input="{broken", expected=2)
        self.values["Production commands"] = '["["]'
        self.write_settings()
        self.hook(expected=2)

    def test_merge_reads_target_branch_evidence(self):
        self.run_command("git", "checkout", "-qb", "feature/s01-demo")
        reviews = self.root / "docs/reviews"
        reviews.mkdir(parents=True)
        (reviews / "s01-demo.md").write_text("Ship allowed: yes\n")
        self.commit()
        self.run_command("git", "checkout", "-q", "main")
        self.hook("merge-tool feature/s01-demo")
        self.hook("merge-tool feature/s02-missing", expected=2)
        # An uncommitted positive report on the caller's branch cannot authorize another target.
        reviews.mkdir(parents=True, exist_ok=True)
        (reviews / "s02-missing.md").write_text("Ship allowed: yes\n")
        self.hook("merge-tool feature/s02-missing", expected=2)

    def test_chore_gate_preserves_validated_plan_exception(self):
        self.run_command("git", "checkout", "-qb", "chore/doc-fix")
        plans = self.root / "docs/plans"
        plans.mkdir(parents=True)
        (plans / "doc-fix.md").write_text("---\ntrack: chore\nvalidated: yes\n---\n")
        self.commit()
        self.hook("merge-tool chore/doc-fix")

    def test_unresolved_merge_does_not_fall_back_to_current_branch(self):
        self.values["Merge commands"] = '["merge-tool"]'
        self.write_settings()
        self.hook("merge-tool https://example.invalid/pr/42", expected=2)

    def test_installs_all_targets_and_reinstall_preserves_project_files(self):
        settings = (self.root / "AGENTS.local.md").read_bytes()
        for target in ("claude", "codex", "all"):
            with self.subTest(target=target):
                self.install(target)
                self.assertEqual((self.root / "AGENTS.local.md").read_bytes(), settings)
        for name in ("ztp-intent", "ztp-ops"):
            self.assertTrue((self.root / ".claude/commands" / (name + ".md")).is_file())
            emitted = self.root / ".codex/skills" / name / "SKILL.md"
            self.assertTrue(emitted.is_file())
            self.assertNotIn("@templates/", emitted.read_text())
        template = self.root / "templates/intent.md"
        template.write_text("project customization\n")
        self.install("all", "update")
        self.assertEqual(template.read_text(), "project customization\n")
        result = self.install("all", "--check")
        self.assertNotIn("modified locally (will be overwritten", result.stdout)

    def test_zone_rules_survive_every_install_and_are_not_drift(self):
        rules = self.root / ".claude/rules"
        rules.mkdir(parents=True)
        rule = rules / "services.md"
        rule.write_text('---\npaths:\n  - "**/src/services/**"\n---\n- One file per domain.\n')
        self.values["Zone rules"] = "| services | `**/src/services/**` | .claude/rules/services.md | domain |"
        self.write_settings()
        content = rule.read_bytes()
        for args in (("claude",), ("codex",), ("all",), ("all", "update")):
            with self.subTest(args=args):
                self.install(*args)
                self.assertEqual(rule.read_bytes(), content)
        self.assertIn(".claude/rules/services.md", (self.root / "AGENTS.md").read_text())
        result = self.install("all", "--check")
        self.assertNotIn("rules/services.md", result.stdout)
        self.assertNotIn("Zone rules:", result.stdout)

    def test_check_reports_unindexed_rule_and_orphan_index_row(self):
        rules = self.root / ".claude/rules"
        rules.mkdir(parents=True)
        (rules / "data.md").write_text('---\npaths:\n  - "**/src/data/**"\n---\n- Only layer that imports db.\n')
        self.values["Zone rules"] = "| services | `**/src/services/**` | .claude/rules/services.md | domain |"
        self.write_settings()
        self.install("claude")
        result = self.install("claude", "--check")
        self.assertIn(".claude/rules/data.md — not in", result.stdout)
        self.assertIn(".claude/rules/services.md — indexed in AGENTS.local.md, file missing", result.stdout)
        self.assertIn("Zone rules: index and .claude/rules/ disagree", result.stdout)
        self.assertFalse((rules / "services.md").exists())

    def frozen_tests_fixture(self, validated="yes", commit_message="test(s01-book): acceptance tests"):
        tests = self.root / "tests"
        tests.mkdir(exist_ok=True)
        (tests / "booking.test.ts").write_text("test('AC1 — refuses a past date', () => {})\n")
        record = self.root / "docs/tests/s01-book.md"
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("---\nvalidated: no\n---\n## Frozen files\n- tests/booking.test.ts\n\n## Findings\n")
        self.run_command("git", "add", ".")
        self.run_command("git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", commit_message)
        record.write_text(record.read_text().replace("validated: no", "validated: " + validated))
        (self.root / "src.ts").write_text("export const ok = true\n")
        self.commit()
        return tests / "booking.test.ts"

    def gate(self, *args, expected=0):
        return self.run_command("bash", str(METHOD / "src/hooks/ztp-gate.sh"), *args, expected=expected)

    def test_acceptance_tests_gate_one_row_per_criterion_within_budget(self):
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "docs/stories.md").write_text(
            "## Story s01-book — Book a slot\n### Acceptance criteria\n"
            "- [ ] AC1 — books an open slot\n- [ ] AC2 — refuses a closed slot\n- [ ] AC3 — shows the slot in brand colours\n"
            "### Dependencies\nNone\n## Story s02-other — Other\n### Acceptance criteria\n- [ ] AC9 — elsewhere\n")
        plans = self.root / "docs/plans"
        plans.mkdir(parents=True, exist_ok=True)
        header = "---\nvalidated: no\n---\n## Acceptance tests\n| Criterion | Test (file › name) | Layer |\n|---|---|---|\n"
        ac1 = "| AC1 | booking.test.ts › AC1 — books | service |\n"
        ac2 = "| AC2 | booking.test.ts › AC2 — refuses | service |\n"
        ac3 = "| AC3 | `UI check` — slot colours | visual |\n"
        plan = plans / "s01-book.md"

        def check(rows, expected, budget=None):
            plan.write_text(header + rows + "\n## Test strategy\n| AC1 | not a row of the table | x |\n")
            (self.root / "AGENTS.local.md").write_text(f"Test budget:       {budget}\n" if budget else "")
            return self.gate("acceptance-tests", "s01-book", expected=expected).stderr

        check(ac1 + ac2 + ac3, 0)
        self.assertIn("AC1 has 2 rows", check(ac1 + ac1.replace("books", "books twice") + ac2 + ac3, 1))
        self.assertIn("AC2 of docs/stories.md has no row", check(ac1 + ac3, 1))
        self.assertIn("AC9, which docs/stories.md does not list", check(ac1 + ac2 + ac3 + "| AC9 | x.test.ts › AC9 | service |\n", 1))
        self.assertIn("above Test budget 1", check(ac1 + ac2 + ac3, 1, budget=1))
        check(ac1 + ac2 + ac3, 0, budget=2)
        self.assertIn("3 acceptance tests, above Test budget 2", check(ac1 + ac2 + ac3.replace("`UI check` — slot colours", "colours.test.ts › AC3"), 1, budget=2))

        (self.root / "docs/tickets").mkdir()
        (self.root / "docs/tickets/s01-book.md").write_text("## Acceptance criteria\n- [ ] AC1 — restored\n## Complexity\n1\n")
        self.assertIn("the table has a row for AC2", check(ac1 + ac2, 1))
        check(ac1, 0)

    def test_design_validated_requires_validated_yes_in_design_md(self):
        self.assertIn("no design", self.gate("design-validated", "s01-book", expected=1).stderr)
        design = self.root / "docs/designs/s01-book/design.md"
        design.parent.mkdir(parents=True)
        design.write_text("---\nvalidated: no\n---\n# Design\nvalidated: yes is written by the gate\n")
        self.assertIn("not validated", self.gate("design-validated", "s01-book", expected=1).stderr)
        design.write_text("---\nvalidated: yes\n---\n# Design\n")
        self.gate("design-validated", "s01-book")
        self.assertIn("no design", self.gate("design-validated", "s02-other", expected=1).stderr)

    def test_install_ignores_verification_records_once_and_warns_if_tracked(self):
        record = self.root / "docs/verif/s00-old.md"
        record.parent.mkdir(parents=True)
        record.write_text("old\n")
        self.commit()
        result = self.install("all")
        self.install("all", "update")
        lines = (self.root / ".gitignore").read_text().splitlines()
        self.assertEqual(lines.count("/docs/verif/"), 1)
        self.assertEqual(lines.count("/.ztp/evidence/"), 1)
        self.assertIn("git rm -r --cached docs/verif", result.stdout)

    def test_verif_current_holds_with_a_gitignored_record(self):
        (self.root / ".gitignore").write_text("/docs/verif/\n")
        (self.root / "app.py").write_text("print('v1')\n")
        self.run_command("git", "add", "-A")
        tree = self.run_command("git", "write-tree").stdout.strip()
        record = self.root / "docs/verif/s01-book.md"
        record.parent.mkdir(parents=True)
        record.write_text(f"Tree: {tree}\n\nVerification status: complete\n")
        self.commit()
        self.assertEqual(self.run_command("git", "ls-files", "docs/verif").stdout, "")
        self.assertEqual(self.run_command("git", "rev-parse", "HEAD^{tree}").stdout.strip(), tree)
        self.gate("verif-current", "s01-book")
        (self.root / "app.py").write_text("print('v2')\n")
        self.commit()
        self.gate("verif-current", "s01-book", expected=1)
        record.unlink()
        result = self.gate("verif-current", "s01-book", expected=1)
        self.assertIn("never committed", result.stderr)

    def test_verif_clean_accepts_only_root_md_records(self):
        verif = self.root / "docs/verif"
        self.gate("verif-clean")
        verif.mkdir(parents=True)
        tree = self.run_command("git", "rev-parse", "HEAD^{tree}").stdout.strip()
        (verif / "s01-book.md").write_text(f"Tree: {tree}\n\nVerification status: complete\n")
        (verif / "c01-docs.md").write_text("record\n")
        (verif / ".DS_Store").write_text("")
        self.gate("verif-clean")
        self.gate("verif-current", "s01-book")
        for intruder in ("shot.png", "run.log", "result.json", "check.sh", "s01-book/notes.md"):
            with self.subTest(intruder=intruder):
                path = verif / intruder
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x\n")
                result = self.gate("verif-clean", expected=1)
                self.assertIn("docs/verif/" + intruder.split("/")[0], result.stderr)
                self.assertIn(".ztp/evidence/", result.stderr)
                self.gate("verif-current", "s01-book", expected=1)
                path.unlink()
                if path.parent != verif:
                    path.parent.rmdir()
        self.gate("verif-clean")

    def test_tests_frozen_passes_when_code_lands_after_untouched_tests(self):
        self.frozen_tests_fixture()
        self.gate("tests-frozen", "s01-book")

    def test_tests_frozen_blocks_a_test_edited_or_deleted_after_validation(self):
        frozen = self.frozen_tests_fixture()
        frozen.write_text("test.skip('AC1 — refuses a past date', () => {})\n")
        self.commit()
        result = self.gate("tests-frozen", "s01-book", expected=1)
        self.assertIn("tests/booking.test.ts", result.stderr)
        frozen.unlink()
        self.commit()
        self.gate("tests-frozen", "s01-book", expected=1)

    def test_tests_frozen_requires_validation_and_the_test_commit(self):
        self.frozen_tests_fixture(validated="no")
        self.assertIn("not validated", self.gate("tests-frozen", "s01-book", expected=1).stderr)
        record = self.root / "docs/tests/s01-book.md"
        record.write_text(record.read_text().replace("validated: no", "validated: yes"))
        self.commit()
        self.gate("tests-frozen", "s01-book")
        (self.root / "docs/tests/s02-x.md").write_text("---\nvalidated: yes\n---\n## Frozen files\n- tests/booking.test.ts\n")
        self.commit()
        self.assertIn("no 'test(s02-x): acceptance tests' commit", self.gate("tests-frozen", "s02-x", expected=1).stderr)

    def test_hooks_preserve_settings_and_prior_hooks_idempotently(self):
        old = self.root / "custom-hooks"
        old.mkdir()
        for name in ("pre-commit", "pre-push"):
            hook = old / name
            hook.write_text("#!/bin/sh\nprintf 'old-" + name + "\\n'\n")
            hook.chmod(0o755)
        self.run_command("git", "config", "core.hooksPath", "custom-hooks")
        config = self.root / ".claude/settings.json"
        config.parent.mkdir()
        original = {"permissions": {"deny": ["Read(private)"]}, "hooks": {"Stop": []}}
        config.write_text(json.dumps(original))
        self.install("all", "--hooks")
        self.install("all", "--hooks")
        actual = json.loads(config.read_text())
        self.assertEqual(actual["permissions"], original["permissions"])
        self.assertEqual(len(actual["hooks"]["PreToolUse"]), 1)
        self.assertIn("old-pre-commit", self.run_command("bash", ".ztp-hooks/pre-commit").stdout)
        self.assertIn("old-pre-push", self.run_command("bash", ".ztp-hooks/pre-push").stdout)

    def test_codex_hooks_do_not_create_claude_settings(self):
        self.install("codex", "--hooks")
        self.assertFalse((self.root / ".claude").exists())

    def test_invalid_claude_settings_are_preserved(self):
        config = self.root / ".claude/settings.json"
        config.parent.mkdir()
        config.write_text("{broken")
        self.install("claude", "--hooks", expected=1)
        self.assertEqual(config.read_text(), "{broken")
        self.assertEqual(self.run_command("git", "config", "--get", "core.hooksPath", expected=None).returncode, 1)

    def test_original_plan_gate_still_blocks_code_and_allows_docs(self):
        self.install("codex", "--hooks")
        self.run_command("git", "checkout", "-qb", "feature/s01-test")
        (self.root / "file.txt").write_text("new code")
        self.run_command("git", "add", "file.txt")
        self.run_command("bash", ".ztp-hooks/pre-commit", expected=1)
        self.run_command("git", "restore", "--staged", "file.txt")
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "notes.md").write_text("notes")
        self.run_command("git", "add", "docs")
        self.run_command("bash", ".ztp-hooks/pre-commit")

    def test_global_payload_supports_offline_init_for_both_targets(self):
        payload = self.root / "payload"
        payload.mkdir()
        shutil.copytree(METHOD / "src", payload / "src")
        shutil.copytree(METHOD / "bin", payload / "bin")
        fake_user = self.root / "fixture-user"
        # Substitute only destination literals in the fixture; never change the user's HOME.
        script = (METHOD / "install.sh").read_text()
        for name in (".claude", ".codex"):
            script = script.replace("$HOME/" + name, str(fake_user / name))
        installer = payload / "install.sh"
        installer.write_text(script)
        self.run_command("bash", str(installer), "--global", "--target", "all")
        self.assertTrue((fake_user / ".codex/skills/ztp-ops/SKILL.md").is_file())
        self.assertTrue((fake_user / ".claude/commands/ztp-intent.md").is_file())
        cached = fake_user / ".claude/zero-to-prod/install.sh"
        self.run_command("bash", str(cached), "init", "--target", "all", "--ci")
        self.assertTrue((self.root / ".ztp-ci/ztp-ci.py").is_file())
        self.assertTrue((self.root / "templates/ops-report.md").is_file())


class DesignTools(unittest.TestCase):
    def test_design_tools_are_named_only_in_their_template(self):
        catalogue = METHOD / "src/templates/design-tools.md"
        rows = [line for line in catalogue.read_text().splitlines() if line.startswith("| ")]
        names = [row.split("|")[1].strip() for row in rows[1:]]
        self.assertTrue(names)
        offenders = []
        for path in (METHOD / "src").rglob("*.md"):
            if path == catalogue:
                continue
            text = path.read_text().lower()
            offenders += [f"{path.relative_to(METHOD)}: {name}" for name in names
                          if name.lower() in text]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
