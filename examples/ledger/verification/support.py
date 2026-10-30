import json
import os
from pathlib import Path
import subprocess
import sys

RUN = Path(os.environ['KIT_RUN_DIR']).resolve()
RUN.mkdir(parents=True, exist_ok=True)


def sandbox(name):
    path = RUN / 'scratch' / name
    path.mkdir(parents=True, exist_ok=False)
    return path / 'ledger.json'


def call(path, *args):
    command = [sys.executable, 'app/ledger.py', '--file', str(path), *args]
    before = path.read_text() if path.exists() else None
    result = subprocess.run(command, capture_output=True, text=True, timeout=5)
    after = path.read_text() if path.exists() else None
    record = {'argv': command, 'exit_code': result.returncode,
              'stdout': result.stdout, 'stderr': result.stderr,
              'before': before, 'after': after}
    with (RUN / 'cli-transcript.jsonl').open('a') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    return result


def success(path, expected, *args):
    result = call(path, *args)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {'balance': expected}, result.stdout


def rejected(path, *args):
    before = path.read_bytes() if path.exists() else None
    result = call(path, *args)
    assert result.returncode == 2, result
    assert result.stderr.strip() and not result.stdout
    after = path.read_bytes() if path.exists() else None
    assert after == before, 'rejected operation changed ledger'
