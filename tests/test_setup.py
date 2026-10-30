"""Install the public kit into disposable task repositories, not its own checkout."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="kit-setup-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.kit = self.base / "public kit source"
        self.kit.mkdir()
        for name in ("setup.sh", "AGENTS.md", "RULE.md", "LICENSE"):
            shutil.copy2(SOURCE / name, self.kit / name)
        for name in (".agents", "docs", "scripts", ".githooks", "verification"):
            shutil.copytree(SOURCE / name, self.kit / name)
        # They must not be installed, even if present in the public source.
        for name in ("vendor", "tests", ".evidence"):
            (self.kit / name).mkdir()
            (self.kit / name / "never-copy.txt").write_text("source-only\n")
        (self.kit / "README.md").write_text("kit readme\n")
        self.repo = self.base / "task project"
        self.repo.mkdir()
        self.env = os.environ.copy()
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG_COUNT"):
            self.env.pop(name, None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.command("git", "-c", "init.defaultBranch=main", "init", "-q")
        (self.repo / "README.md").write_text("task readme\n")
        (self.repo / "LICENSE").write_text("native license\n")

    def command(self, *args, cwd=None, expected=0):
        result = subprocess.run(
            args, cwd=self.repo if cwd is None else cwd, env=self.env,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if expected is not None:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def setup(self, **kwargs):
        return self.command("bash", str(self.kit / "setup.sh"), **kwargs)

    def snapshot(self):
        return {
            str(p.relative_to(self.repo)): p.read_bytes()
            for p in self.repo.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(self.repo).parts
        }

    def test_fresh_install_from_absolute_path_with_spaces(self):
        index = self.repo / ".git/index"
        self.assertFalse(index.exists())
        self.setup()
        self.assertEqual((self.repo / "README.md").read_text(), "task readme\n")
        self.assertEqual((self.repo / "LICENSE").read_text(), "native license\n")
        self.assertEqual((self.repo / "LICENSE.261031").read_bytes(), (self.kit / "LICENSE").read_bytes())
        self.assertEqual(self.command("git", "config", "--local", "--get", "core.hooksPath").stdout.strip(), ".githooks")
        self.assertFalse(index.exists())
        self.assertFalse((self.repo / ".evidence").exists())
        for name in ("vendor", "tests", "setup.sh"):
            self.assertFalse((self.repo / name).exists())
        self.assertEqual(
            {p.name for p in (self.repo / "docs").iterdir()},
            {"intent.md", "features.md", "handoff.md", "skills.md"},
        )
        self.assertEqual(len(list((self.repo / ".agents/skills").glob("*/SKILL.md"))), 7)
        self.assertEqual(self.command("./verification/check", expected=2).returncode, 2)
        self.command("git", "check-ignore", "--quiet", ".evidence/tmp/state")
        self.command("git", "check-ignore", "--quiet", ".evidence/run-proof/output.log", expected=1)

    def test_reject_non_git_subdirectory_and_source_checkout(self):
        outside = self.base / "not git"
        outside.mkdir()
        self.setup(cwd=outside, expected=1)
        self.assertEqual(list(outside.iterdir()), [])
        child = self.repo / "child"
        child.mkdir()
        self.setup(cwd=child, expected=1)
        self.assertEqual(list(child.iterdir()), [])
        self.command("git", "init", "-q", cwd=self.kit)
        self.setup(cwd=self.kit, expected=1)
        self.assertFalse((self.kit / "AGENTS.kit.md").exists())

    def test_existing_documents_and_adapter_survive_idempotent_rerun(self):
        original_agents = b"# Existing task rules\nDo not remove me.\n"
        original_rules = b"Actual task restrictions\n"
        (self.repo / "AGENTS.md").write_bytes(original_agents)
        (self.repo / "RULE.md").write_bytes(original_rules)
        (self.repo / "docs").mkdir()
        (self.repo / "docs/intent.md").write_text("existing intent\n")
        (self.repo / ".gitignore").write_text("native-cache/\n")
        (self.repo / "verification").mkdir()
        adapter = self.repo / "verification/check"
        adapter.write_text("#!/bin/sh\nprintf 'native test\\n'\n")
        adapter.chmod(0o755)
        self.setup()
        self.assertTrue((self.repo / "AGENTS.md").read_bytes().startswith(original_agents))
        self.assertEqual((self.repo / "RULE.md").read_bytes(), original_rules)
        self.assertEqual((self.repo / "AGENTS.kit.md").read_bytes(), (self.kit / "AGENTS.md").read_bytes())
        self.assertEqual((self.repo / "RULE.kit.md").read_bytes(), (self.kit / "RULE.md").read_bytes())
        self.assertIn("AGENTS.kit.md", (self.repo / "AGENTS.md").read_text())
        self.assertEqual((self.repo / "docs/intent.md").read_text(), "existing intent\n")
        self.assertTrue((self.repo / ".gitignore").read_text().startswith("native-cache/\n"))
        first = self.snapshot()
        self.setup()
        self.assertEqual(self.snapshot(), first)
        self.assertEqual((self.repo / "AGENTS.md").read_text().count("<!-- 261031-kit -->"), 1)
        self.assertEqual(adapter.read_text(), "#!/bin/sh\nprintf 'native test\\n'\n")

    def test_runtime_conflict_stops_before_copying(self):
        (self.repo / "scripts").mkdir()
        script = self.repo / "scripts/check"
        script.write_text("#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        before = self.snapshot()
        result = self.setup(expected=1)
        self.assertIn("scripts/check", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.command("git", "config", "--get", "core.hooksPath", expected=1)

    def test_sidecar_conflict_stops_before_copying(self):
        (self.repo / "AGENTS.md").write_text("native rules\n")
        (self.repo / "AGENTS.kit.md").write_text("another kit\n")
        before = self.snapshot()
        self.setup(expected=1)
        self.assertEqual(self.snapshot(), before)

    def test_identical_runtime_without_execute_permission_stops_before_copying(self):
        (self.repo / "scripts").mkdir()
        script = self.repo / "scripts/check"
        shutil.copy2(self.kit / "scripts/check", script)
        script.chmod(0o644)
        before = self.snapshot()
        result = self.setup(expected=1)
        self.assertIn("scripts/check", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(script.stat().st_mode & 0o111)
        self.command("git", "config", "--get", "core.hooksPath", expected=1)

    def test_ignored_evidence_stops_before_copying(self):
        for pattern in (".evidence/\n", "*.log\n", ".evidence/latest\n", ".evidence/run-*/result\n"):
            with self.subTest(pattern=pattern):
                (self.repo / ".gitignore").write_text(pattern)
                before = self.snapshot()
                result = self.setup(expected=1)
                self.assertIn("ignore", result.stderr)
                self.assertEqual(self.snapshot(), before)
                self.command("git", "config", "--get", "core.hooksPath", expected=1)

    def test_existing_hooks_are_preserved_before_copying(self):
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 0\n")
        before = self.snapshot()
        original = hook.read_bytes()
        self.setup(expected=1)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(hook.read_bytes(), original)
        hook.unlink()
        self.command("git", "config", "--local", "core.hooksPath", "native-hooks")
        self.setup(expected=1)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.command("git", "config", "--get", "core.hooksPath").stdout.strip(), "native-hooks")

    def test_ignored_managed_files_stop_before_copying(self):
        for pattern in (".githooks/\n", "scripts/\n"):
            with self.subTest(pattern=pattern):
                (self.repo / ".gitignore").write_text(pattern)
                before = self.snapshot()
                result = self.setup(expected=1)
                self.assertIn("ignore", result.stderr)
                self.assertEqual(self.snapshot(), before)
                self.command("git", "config", "--get", "core.hooksPath", expected=1)

    def test_symlink_parent_is_rejected_without_external_writes(self):
        external = self.base / "external"
        external.mkdir()
        (self.repo / "scripts").symlink_to(external, target_is_directory=True)
        self.setup(expected=1)
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.repo / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
