"""Integration tests use real local Git repositories and real subprocesses."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class KitIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fde-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Kit Test')
        self.git('config', 'user.email', 'kit@example.invalid')
        (self.root / 'README.md').write_text('Existing assignment\n')
        (self.root / 'AGENTS.md').write_text('Existing agent instructions\n')
        self.install()

    def run_cmd(self, argv, expected=0, env=None):
        actual_env = os.environ.copy()
        actual_env.update(env or {})
        p = subprocess.run(argv, cwd=self.root, env=actual_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        if expected is not None:
            self.assertEqual(p.returncode, expected, p.stdout)
        return p

    def git(self, *argv, expected=0):
        return self.run_cmd(['git', *argv], expected)

    def kit(self, *argv, expected=0, env=None):
        return self.run_cmd([PYTHON, 'kit.py', *argv], expected, env)

    def install(self, expected=0):
        return self.run_cmd([PYTHON, str(SOURCE / 'kit.py'), 'install', '--project', str(self.root)], expected)

    def fixture(self, broken=False):
        (self.root / 'app.py').write_text('import sys\n\ndef double(n):\n    return n * ' + ('3' if broken else '2') + '\n\nif __name__ == "__main__":\n    print(double(int(sys.argv[1])))\n')
        (self.root / 'verify.py').write_text('''import ast
import os
from pathlib import Path
import subprocess
import sys
mode = sys.argv[1]
if mode == 'doctor':
    assert Path('app.py').is_file()
elif mode == 'syntax':
    ast.parse(Path('app.py').read_text())
elif mode == 'business':
    from app import double
    assert double(7) == 14
elif mode == 'runtime':
    p = subprocess.run([sys.executable, 'app.py', '21'], capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout.strip() == '42', p.stdout
elif mode == 'cleanup':
    Path(os.environ['KIT_RUN_DIR'], 'cleanup-ran').write_text('yes')
elif mode == 'secret':
    print(os.environ['TEST_KIT_SECRET'])
elif mode == 'timeout':
    import time
    time.sleep(5)
elif mode == 'mutate':
    Path('app.py').write_text(Path('app.py').read_text() + '# mutation\\n')
elif mode == 'fail':
    sys.exit(9)
''')
        def cmd(mode, timeout=3):
            return {'argv': [PYTHON, 'verify.py', mode], 'timeout_seconds': timeout}
        self.cfg = {'schema_version': 1, 'doctor': cmd('doctor'), 'checks': [dict(id=name, kind=kind, **cmd(name)) for name, kind in [('syntax', 'static'), ('business', 'business'), ('runtime', 'runtime')]], 'cleanup': cmd('cleanup'), 'env': {}, 'required_env': [], 'run_timeout_seconds': 15}
        self.save_config()
        self.kit('map', 'add', '--id', 'F001', '--title', 'Double a number', '--source', 'app.py', '--entry', 'python3 app.py 21', '--action', 'Enter 21', '--expected', '42', '--invariant', 'double(n) equals 2*n', '--check', 'runtime', '--check', 'business')
        self.kit('map', 'sync')

    def save_config(self):
        (self.root / 'verification/project.json').write_text(json.dumps(self.cfg))

    def latest(self):
        return json.loads((self.root / '.kit/latest.json').read_text())

    def test_install_preserves_and_is_idempotent(self):
        self.assertEqual((self.root / 'README.md').read_text(), 'Existing assignment\n')
        agents = (self.root / 'AGENTS.md').read_text()
        self.assertTrue(agents.startswith('Existing agent instructions\n'))
        self.install()
        self.assertEqual((self.root / 'AGENTS.md').read_text(), agents)
        self.assertEqual(self.git('config', '--local', '--get', 'core.hooksPath').stdout.strip(), '.githooks')
        self.git('check-ignore', '.kit/test')
        self.run_cmd(['.githooks/pre-push'], expected=1)

    def test_install_conflict_preflight(self):
        (self.root / 'kit.py').write_text('# existing code\n')
        (self.root / 'scripts/check').unlink()
        self.install(expected=1)
        self.assertEqual((self.root / 'kit.py').read_text(), '# existing code\n')
        self.assertFalse((self.root / 'scripts/check').exists())

    def test_install_existing_hook_is_preserved(self):
        hook = self.root / '.githooks/pre-commit'
        hook.write_text('#!/bin/sh\necho user hook\n')
        self.install(expected=1)
        self.assertIn('user hook', hook.read_text())

    def test_install_preserves_vendor_executable_mode(self):
        relative = Path('vendor/pstack/skills/show-me-your-work/scripts/log.sh')
        source = SOURCE / relative
        installed = self.root / relative
        self.assertEqual(source.stat().st_mode & 0o777, 0o755)
        self.assertEqual(installed.read_bytes(), source.read_bytes())
        self.assertEqual(installed.stat().st_mode & 0o777, 0o755)
        self.assertEqual(installed.stat().st_mode & 0o7000, 0)
        self.install()
        self.assertEqual(installed.stat().st_mode & 0o777, 0o755)

    def test_unconfigured_fails(self):
        self.kit('doctor', expected=1)
        self.kit('check', expected=1)
        self.assertEqual(self.latest()['status'], 'FAIL')

    def test_real_commit_blocks_failure_then_accepts_fix(self):
        self.fixture(broken=True)
        self.kit('begin', '--unit', 'U001', '--goal', 'Fix doubling')
        self.git('add', '.')
        self.git('commit', '-m', 'broken should fail', expected=1)
        self.assertEqual(self.latest()['status'], 'FAIL')
        path = self.root / 'app.py'
        path.write_text(path.read_text().replace('n * 3', 'n * 2'))
        self.git('add', 'app.py')
        self.git('commit', '-m', 'correct doubling')
        self.assertEqual(self.latest()['status'], 'PASS')
        self.kit('status')  # HEAD changed; content evidence remains valid.
        self.assertTrue(self.latest()['staged_tree'])
        self.kit('begin', '--unit', 'U002', '--goal', 'Next task')

    def test_partial_stage_and_untracked_are_blocked(self):
        self.fixture()
        self.git('add', '.')
        app = self.root / 'app.py'
        app.write_text(app.read_text() + '# unstaged\n')
        self.kit('check', '--staged', expected=1)
        self.assertEqual(self.latest()['checks'], [])
        self.git('add', 'app.py')
        (self.root / 'new.txt').write_text('untracked')
        self.kit('check', '--staged', expected=1)
        self.git('add', 'new.txt')
        self.kit('check', '--staged')

    def test_stale_and_mutation_detection(self):
        self.fixture()
        self.kit('check')
        app = self.root / 'app.py'
        app.write_text(app.read_text() + '# edited\n')
        p = self.kit('status', expected=1)
        self.assertIn('STALE', p.stdout)
        self.cfg['checks'][0]['argv'][-1] = 'mutate'
        self.save_config()
        self.kit('check', expected=1)
        self.assertNotEqual(self.latest()['fingerprint'], self.latest()['fingerprint_after'])

    def test_map_is_readonly_and_requires_runtime(self):
        self.fixture()
        index = self.root / '.agents/skills/verify-app/features/README.md'
        index.write_text('corrupt index\n')
        self.kit('map', 'check', expected=1)
        self.assertEqual(index.read_text(), 'corrupt index\n')
        self.kit('map', 'sync')
        self.kit('map', 'check')
        (self.root / 'app.py').unlink()
        self.kit('map', 'check', expected=1)

    def test_cleanup_failure_timeout_and_total_deadline(self):
        self.fixture()
        self.cfg['cleanup']['argv'][-1] = 'fail'
        self.save_config()
        self.kit('check', expected=1)
        self.assertFalse(self.latest()['checks'][-1]['passed'])
        self.cfg['cleanup']['argv'][-1] = 'cleanup'
        self.cfg['checks'][0]['argv'][-1] = 'timeout'
        self.cfg['checks'][0]['timeout_seconds'] = 0.1
        self.save_config()
        self.kit('check', expected=1)
        report = self.latest()
        self.assertTrue(report['checks'][1]['timed_out'])
        self.assertTrue((self.root / '.kit/runs' / report['run_id'] / 'cleanup-ran').exists())
        self.cfg['checks'][0]['timeout_seconds'] = 5
        self.cfg['run_timeout_seconds'] = 0.8
        self.save_config()
        self.kit('check', expected=1)
        self.assertLess(self.latest()['duration_seconds'], 2)

    def test_attempt_limits_and_no_reset(self):
        self.fixture(broken=True)
        self.kit('iterate', expected=1)
        self.kit('begin', '--unit', 'U001', '--goal', 'Fix', '--max-attempts', '2')
        self.kit('iterate', expected=1)
        self.kit('begin', '--unit', 'U001', '--goal', 'Reset', expected=1)
        self.kit('iterate', expected=2)
        self.kit('iterate', expected=2)
        unit = json.loads((self.root / '.kit/unit.json').read_text())
        self.assertEqual(unit['attempts'], 2)
        self.assertEqual(len((self.root / '.kit/iteration.jsonl').read_text().splitlines()), 2)

    def test_secret_environment_is_masked(self):
        self.fixture()
        secret = 'test-' + 'sensitive-value-123456789'
        self.cfg['required_env'] = ['TEST_KIT_SECRET']
        self.cfg['checks'][0]['argv'][-1] = 'secret'
        self.save_config()
        p = self.kit('check', env={'TEST_KIT_SECRET': secret})
        self.assertNotIn(secret, p.stdout)
        for path in (self.root / '.kit').rglob('*'):
            if path.is_file():
                self.assertNotIn(secret.encode(), path.read_bytes(), str(path))
        report = self.latest()
        log = self.root / '.kit/runs' / report['run_id'] / 'check-syntax.log'
        self.assertIn('[REDACTED]', log.read_text())

    def test_reserved_environment_names_are_actionable(self):
        self.fixture()
        self.cfg['env'] = {'TZ': 'UTC', 'PYTHONHASHSEED': '0'}
        self.save_config()
        p = self.kit('check', expected=1)
        self.assertIn('TZ', p.stdout)
        self.assertIn('PYTHONHASHSEED', p.stdout)
        self.assertEqual(self.latest()['checks'], [])

    def test_real_secret_pattern_blocks_before_commands(self):
        self.fixture()
        (self.root / 'accidental.txt').write_text('AK' + 'IA' + 'Z' * 16)
        self.kit('check', expected=1)
        self.assertEqual(self.latest()['checks'], [])

    def test_map_requires_runtime_and_rejects_escape(self):
        self.fixture()
        self.kit('map', 'add', '--id', 'F002', '--title', 'Missing runtime', '--source', 'app.py', '--entry', 'python3 app.py', '--action', 'Run', '--expected', 'Result', '--invariant', 'Correct', '--check', 'business')
        self.kit('map', 'sync')
        self.kit('map', 'check', expected=1)
        external = Path(self.tmp.name) / 'outside.py'
        external.write_text('outside')
        (self.root / 'escape.py').symlink_to(external)
        self.kit('map', 'add', '--id', 'F003', '--title', 'Escape', '--source', 'escape.py', '--entry', 'x', '--action', 'x', '--expected', 'x', '--invariant', 'x', '--check', 'runtime', expected=1)

    def test_timeout_terminates_child_process_group(self):
        self.fixture()
        child = "import os,time;from pathlib import Path;time.sleep(0.7);Path(os.environ['KIT_RUN_DIR'],'orphan-survived').write_text('bad')"
        parent = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',sys.argv[1]]);time.sleep(5)"
        self.cfg['checks'][0]['argv'] = [PYTHON, '-c', parent, child]
        self.cfg['checks'][0]['timeout_seconds'] = 0.1
        self.save_config()
        self.kit('check', expected=1)
        time.sleep(0.8)
        self.assertFalse((self.root / '.kit/runs' / self.latest()['run_id'] / 'orphan-survived').exists())

    def test_minimal_environment_and_unit_deadline(self):
        self.fixture()
        self.cfg['checks'][0]['argv'] = [PYTHON, '-c', "import os;assert 'UNLISTED_SECRET' not in os.environ;assert os.environ['TZ']=='UTC';assert os.environ['TMPDIR'].startswith(os.environ['KIT_RUN_DIR'])"]
        self.save_config()
        self.kit('check', env={'UNLISTED_SECRET': 'must-not-inherit'})
        self.cfg['checks'][0]['argv'] = [PYTHON, 'verify.py', 'timeout']
        self.save_config()
        self.kit('begin', '--unit', 'U001', '--goal', 'Bound time', '--minutes', '0.02')
        self.kit('iterate', expected=2)
        self.assertLess(self.latest()['duration_seconds'], 2)


if __name__ == '__main__':
    unittest.main()
