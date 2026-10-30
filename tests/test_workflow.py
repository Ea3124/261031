"""Exercise the workflow in disposable Git repositories, without an example app."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
TOOLS = (
    "scripts/check", "scripts/source-tree", "scripts/setup",
    ".githooks/pre-commit", ".githooks/pre-push", "verification/check",
)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="verification-test-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG_COUNT"):
            self.env.pop(key, None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("-c", "init.defaultBranch=main", "init", "-q")
        self.git("config", "user.name", "Workflow test")
        self.git("config", "user.email", "workflow@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        for name in TOOLS:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, target)
        (self.repo / "app.txt").write_text("original\n")
        (self.repo / ".gitignore").write_text(".evidence/tmp/\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "initial files")
        self.run_tool("scripts/setup")

    def command(self, *args, expected=0, env=None):
        result = subprocess.run(
            args, cwd=self.repo, env=self.env if env is None else env,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if expected is not None:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def git(self, *args, **kwargs):
        return self.command("git", *args, **kwargs)

    def run_tool(self, name, **kwargs):
        return self.command("./" + name, **kwargs)

    def adapter(self, body="printf 'native check passed\\n'\n"):
        path = self.repo / "verification/check"
        path.write_text("#!/usr/bin/env bash\nset -eu\n" + body)
        path.chmod(0o755)

    def add_submodule(self):
        origin = self.repo / ".git/local-submodule-source"
        origin.mkdir()
        self.git("-C", str(origin), "-c", "init.defaultBranch=main", "init", "-q")
        self.git("-C", str(origin), "config", "user.name", "Workflow test")
        self.git("-C", str(origin), "config", "user.email", "workflow@example.invalid")
        self.git("-C", str(origin), "config", "commit.gpgsign", "false")
        (origin / "module.txt").write_text("original module\n")
        (origin / ".gitignore").write_text("runtime.data\n")
        self.git("-C", str(origin), "add", "-A")
        self.git("-C", str(origin), "commit", "-qm", "module initial files")
        path = "deps/local module"
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), path)
        self.git("-C", path, "config", "user.name", "Workflow test")
        self.git("-C", path, "config", "user.email", "workflow@example.invalid")
        self.git("-C", path, "config", "commit.gpgsign", "false")
        return self.repo / path

    def evidence(self):
        run = (self.repo / ".evidence/latest").read_text().strip()
        return self.repo / ".evidence" / run

    def result(self):
        return dict(line.split("=", 1) for line in (self.evidence() / "result").read_text().splitlines())

    def stage(self):
        self.git("add", "-A")

    def blocked_commit(self):
        head = self.git("rev-parse", "HEAD").stdout
        result = self.git("commit", "-qm", "must be blocked", expected=None)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, head)
        return result

    def test_unconfigured_adapter_fails_and_blocks_commit(self):
        self.run_tool("scripts/check", expected=2)
        self.assertEqual(self.result()["status"], "FAIL")
        self.assertIn("not configured", (self.evidence() / "output.log").read_text())
        self.stage()
        self.blocked_commit()

    def test_verify_then_stage_and_real_commit(self):
        self.adapter('printf "detail\\n" > "$EVIDENCE_DIR/detail.txt"\nprintf "native check\\n"\n')
        self.run_tool("scripts/check")
        self.assertEqual(self.result()["status"], "PASS")
        self.assertEqual(self.result()["tree"], self.command("./scripts/source-tree", "working").stdout.strip())
        self.stage()
        self.git("commit", "-qm", "verified change")
        self.assertIn(".evidence/latest", self.git("ls-tree", "-r", "--name-only", "HEAD").stdout)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_false_adapter_fails_and_blocks_commit(self):
        self.adapter("false\n")
        self.run_tool("scripts/check", expected=1)
        self.assertEqual(self.result()["exit_code"], "1")
        self.stage()
        self.blocked_commit()

    def test_stale_evidence_after_source_or_document_change(self):
        for name in ("app.txt", "README.md"):
            with self.subTest(name=name):
                self.adapter()
                self.run_tool("scripts/check")
                (self.repo / name).write_text("changed after verification\n")
                self.stage()
                self.assertIn("verified tree", self.blocked_commit().stderr)

    def test_partial_stage_blocks_commit(self):
        self.adapter()
        self.run_tool("scripts/check")
        self.stage()
        (self.repo / "app.txt").write_text("unstaged change\n")
        self.assertIn("stage all", self.blocked_commit().stderr)

    def test_new_untracked_source_blocks_commit(self):
        self.adapter()
        self.run_tool("scripts/check")
        self.stage()
        (self.repo / "new source.txt").write_text("new input\n")
        self.assertIn("stage all", self.blocked_commit().stderr)

    def test_unstaged_evidence_blocks_commit(self):
        self.adapter()
        self.run_tool("scripts/check")
        self.git("add", "verification/check")
        self.assertIn("stage .evidence/latest", self.blocked_commit().stderr)
        self.stage()
        (self.evidence() / "output.log").write_text("changed output\n")
        self.assertIn("unstaged", self.blocked_commit().stderr)

    def test_untracked_current_evidence_blocks_commit_even_if_ignored(self):
        self.adapter()
        (self.repo / ".gitignore").write_text(".evidence/tmp/\n*.private\n")
        self.run_tool("scripts/check")
        self.stage()
        (self.evidence() / "extra.private").write_text("new evidence\n")
        self.assertIn("untracked", self.blocked_commit().stderr)

    def test_failure_with_same_source_invalidates_old_pass(self):
        self.adapter('test "${CHECK_FAIL:-0}" = 0\n')
        self.run_tool("scripts/check")
        original = self.evidence()
        self.stage()
        failure_env = dict(self.env, CHECK_FAIL="1")
        self.run_tool("scripts/check", expected=1, env=failure_env)
        self.assertEqual(self.git("show", ":.evidence/latest").stdout.strip(), original.name)
        self.assertNotEqual(self.evidence(), original)
        self.assertEqual(self.result()["tree"], dict(
            line.split("=", 1) for line in (original / "result").read_text().splitlines()
        )["tree"])
        self.assertIn("latest run is not staged", self.blocked_commit().stderr)
        self.stage()
        self.assertIn("latest verification failed", self.blocked_commit().stderr)

    def test_source_change_during_check_fails(self):
        self.adapter("printf 'changed\\n' >> app.txt\n")
        self.run_tool("scripts/check", expected=1)
        self.assertEqual(self.result()["status"], "FAIL")
        self.assertIn("Source tree changed", (self.evidence() / "output.log").read_text())
        self.stage()
        self.blocked_commit()

    def test_later_runs_preserve_prior_evidence(self):
        self.adapter()
        self.run_tool("scripts/check")
        previous = self.evidence()
        saved = {path.name: path.read_bytes() for path in previous.iterdir()}
        self.run_tool("scripts/check")
        self.assertNotEqual(previous, self.evidence())
        self.assertEqual(saved, {path.name: path.read_bytes() for path in previous.iterdir()})

    def test_check_and_hook_leave_real_index_unchanged(self):
        self.adapter()
        index = self.repo / ".git/index"
        saved = index.read_bytes()
        self.run_tool("scripts/check")
        self.assertEqual(saved, index.read_bytes())
        self.stage()
        saved = index.read_bytes()
        self.run_tool(".githooks/pre-commit")
        self.assertEqual(saved, index.read_bytes())

    def test_source_tree_supports_missing_index_without_creating_one(self):
        index = self.repo / ".git/index"
        index.unlink()
        staged = self.command("./scripts/source-tree", "staged").stdout.strip()
        working = self.command("./scripts/source-tree", "working").stdout.strip()
        self.assertNotEqual(staged, working)
        self.assertFalse(index.exists())

    def test_working_tree_sees_changes_hidden_by_index_flags(self):
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                before = self.command("./scripts/source-tree", "working").stdout
                self.git("update-index", "--" + flag, "app.txt")
                index = (self.repo / ".git/index").read_bytes()
                (self.repo / "app.txt").write_text("hidden change\n")
                after = self.command("./scripts/source-tree", "working").stdout
                self.assertNotEqual(before, after)
                self.assertEqual(index, (self.repo / ".git/index").read_bytes())
                self.git("update-index", "--no-" + flag, "app.txt")
                (self.repo / "app.txt").write_text("original\n")

    def test_evidence_index_flags_cannot_hide_unstaged_changes(self):
        self.adapter()
        self.run_tool("scripts/check")
        self.stage()
        output = self.evidence() / "output.log"
        relative = str(output.relative_to(self.repo))
        original = output.read_text()
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.git("update-index", "--" + flag, relative)
                index = (self.repo / ".git/index").read_bytes()
                output.write_text("hidden evidence change\n")
                blocked = self.run_tool(".githooks/pre-commit", expected=1)
                self.assertIn("unstaged", blocked.stderr)
                self.assertEqual(index, (self.repo / ".git/index").read_bytes())
                self.git("update-index", "--no-" + flag, relative)
                output.write_text(original)

    def test_clean_submodule_head_change_is_bound_by_gitlink(self):
        self.adapter()
        module = self.add_submodule()
        self.run_tool("scripts/check")
        previous = self.result()["tree"]
        (module / "module.txt").write_text("committed module change\n")
        self.git("-C", str(module), "commit", "-qam", "module source change")
        self.run_tool("scripts/check")
        self.assertNotEqual(previous, self.result()["tree"])
        self.stage()
        self.git("commit", "-qm", "verified submodule commit")

    def test_dirty_submodule_source_blocks_check_and_commit(self):
        self.adapter()
        module = self.add_submodule()
        self.run_tool("scripts/check")
        self.stage()
        for kind in ("modified", "staged", "staged-only", "untracked", "assume-unchanged", "skip-worktree"):
            with self.subTest(kind=kind):
                if kind in ("assume-unchanged", "skip-worktree"):
                    self.git("-C", str(module), "update-index", "--" + kind, "module.txt")
                path = module / ("new source.txt" if kind == "untracked" else "module.txt")
                path.write_text("uncommitted module change\n")
                if kind in ("staged", "staged-only"):
                    self.git("-C", str(module), "add", "module.txt")
                if kind == "staged-only":
                    path.write_text("original module\n")
                saved_index = (self.repo / ".git/modules/deps/local module/index").read_bytes()
                failed = self.run_tool("scripts/check", expected=None)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn("Dirty submodule", failed.stderr)
                self.assertEqual(self.result()["status"], "FAIL")
                self.assertEqual(saved_index, (self.repo / ".git/modules/deps/local module/index").read_bytes())
                self.stage()
                self.blocked_commit()
                if kind in ("assume-unchanged", "skip-worktree"):
                    self.git("-C", str(module), "update-index", "--no-" + kind, "module.txt")
                if kind == "untracked":
                    path.unlink()
                self.git("-C", str(module), "reset", "--hard", "-q", "HEAD")

    def test_submodule_change_during_check_fails(self):
        self.add_submodule()
        self.adapter("printf 'changed\\n' >> 'deps/local module/module.txt'\n")
        failed = self.run_tool("scripts/check", expected=None)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Dirty submodule", failed.stderr)
        self.assertEqual(self.result()["status"], "FAIL")

    def test_nested_submodule_changes_require_parent_commit(self):
        self.adapter()
        module = self.add_submodule()
        origin = self.repo / ".git/local-submodule-source"
        self.git("-C", str(module), "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                 str(origin), "nested module")
        self.git("-C", str(module), "commit", "-qm", "add nested module")
        self.run_tool("scripts/check")
        nested = module / "nested module"
        self.git("-C", str(nested), "config", "user.name", "Workflow test")
        self.git("-C", str(nested), "config", "user.email", "workflow@example.invalid")
        self.git("-C", str(nested), "config", "commit.gpgsign", "false")
        (nested / "module.txt").write_text("nested committed change\n")
        self.git("-C", str(nested), "commit", "-qam", "nested source change")
        failed = self.run_tool("scripts/check", expected=None)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Dirty submodule", failed.stderr)
        self.git("-C", str(module), "commit", "-qam", "bind nested commit")
        self.run_tool("scripts/check")
        (nested / "new source.txt").write_text("untracked nested source\n")
        failed = self.run_tool("scripts/check", expected=None)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Dirty submodule", failed.stderr)

    def test_uninitialized_submodule_fails_but_ignored_runtime_input_is_unbound(self):
        self.adapter()
        module = self.add_submodule()
        self.run_tool("scripts/check")
        previous = self.result()["tree"]
        (module / "runtime.data").write_text("ignored runtime input\n")
        self.run_tool("scripts/check")
        self.assertEqual(previous, self.result()["tree"])
        self.git("submodule", "deinit", "-f", "--", str(module.relative_to(self.repo)))
        failed = self.run_tool("scripts/check", expected=None)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Uninitialized submodule", failed.stderr)
        self.assertEqual(self.result()["status"], "FAIL")

    def test_missing_command_and_interruption_leave_fail_receipts(self):
        (self.repo / "verification/check").unlink()
        missing = self.run_tool("scripts/check", expected=None)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(self.result()["status"], "FAIL")
        self.assertEqual(self.result()["exit_code"], str(missing.returncode))
        self.adapter('kill -TERM "$PPID"\n')
        self.run_tool("scripts/check", expected=143)
        self.assertEqual(self.result()["status"], "FAIL")
        self.assertEqual(self.result()["exit_code"], "143")

    def test_setup_preserves_existing_user_hooks_and_hooks_path(self):
        self.git("config", "--local", "--unset", "core.hooksPath")
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 0\n")
        saved = hook.read_bytes()
        self.run_tool("scripts/setup", expected=1)
        self.assertEqual(saved, hook.read_bytes())
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath", expected=1).stdout, "")
        hook.unlink()
        global_config = self.repo / ".git/test-global-config"
        global_config.write_text("[core]\n\thooksPath = custom-hooks\n")
        inherited = dict(self.env, GIT_CONFIG_GLOBAL=str(global_config))
        self.run_tool("scripts/setup", expected=1, env=inherited)
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath", expected=1).stdout, "")
        self.git("config", "--local", "core.hooksPath", "")
        self.run_tool("scripts/setup", expected=1)
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath").stdout, "\n")

    def test_invalid_pointer_and_push_are_blocked(self):
        (self.repo / ".evidence").mkdir()
        (self.repo / ".evidence/latest").write_text("run-../../outside\n")
        self.assertIn("invalid evidence pointer", self.blocked_commit().stderr)
        self.run_tool(".githooks/pre-push", expected=1)


if __name__ == "__main__":
    unittest.main()
