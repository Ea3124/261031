#!/usr/bin/env python3
"""Local-only, standard-library verification and bounded iteration kit."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

VERSION = 1
FEATURES = Path('.agents/skills/verify-app/features')
BEGIN = '<!-- FDE KIT: BEGIN -->'
END = '<!-- FDE KIT: END -->'
IGN_BEGIN = '# FDE KIT: BEGIN'
IGN_END = '# FDE KIT: END'
PRE_COMMIT = '#!/bin/sh\ncd "$(git rev-parse --show-toplevel)" || exit 1\nexec python3 kit.py iterate --staged\n'
PRE_PUSH = '#!/bin/sh\nprintf "%s\\n" "이 키트는 로컬 커밋 전용입니다. push를 차단합니다." >&2\nexit 1\n'


class KitError(Exception):
    pass


def git(root, *args, check=True):
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if check and p.returncode:
        raise KitError('Git 명령 실패: ' + p.stderr.decode(errors='replace').strip())
    return p.stdout.decode(errors='surrogateescape').strip() if check else p


def project():
    return Path(git(Path.cwd(), 'rev-parse', '--show-toplevel')).resolve()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise KitError(f'JSON 읽기 실패: {path}: {exc}') from exc


def rel_files(root):
    raw = subprocess.run(['git', '-C', str(root), 'ls-files', '-c', '-o', '--exclude-standard', '-z'], capture_output=True, check=True).stdout
    names = sorted(set(os.fsdecode(v) for v in raw.split(b'\0') if v))
    return [n for n in names if not any(p in ('.git', '.kit', '__pycache__', '.pytest_cache') for p in Path(n).parts) and not n.endswith(('.pyc', '.pyo'))]


def fingerprint(root):
    digest = hashlib.sha256()
    names = set(rel_files(root))
    # Explicitly mapped source/configuration remains evidence even if ignored by Git.
    names.add('verification/project.json')
    for feature in (root / FEATURES).glob('*.md'):
        names.add(str(feature.relative_to(root)))
        try:
            meta = json.loads(feature.read_text(encoding='utf-8').splitlines()[1])
            for source in meta.get('sources', []):
                safe_file(root, source)
                names.add(source)
        except (KitError, OSError, ValueError, IndexError, AttributeError, TypeError):
            pass  # The dedicated map validator reports malformed metadata.
    for name in sorted(names):
        path = root / name
        digest.update(os.fsencode(name) + b'\0')
        if path.is_symlink():
            value = b'link:' + os.fsencode(os.readlink(path))
            if path.is_file() and path.resolve().is_relative_to(root.resolve()):
                value += b'\0content:' + path.read_bytes()
        elif path.is_file():
            value = (b'x:' if path.stat().st_mode & 0o111 else b'f:') + path.read_bytes()
        else:
            value = b'missing'
        digest.update(hashlib.sha256(value).digest())
    return digest.hexdigest()


def safe_file(root, source):
    if not isinstance(source, str) or not source or Path(source).is_absolute() or '..' in Path(source).parts:
        raise KitError(f'프로젝트 내부 상대 파일 경로가 필요합니다: {source}')
    path = root / source
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise KitError(f'소스가 없거나 프로젝트 밖을 가리킵니다: {source}')
    return path


def command_config(value, label):
    if not isinstance(value, dict):
        raise KitError(f'{label} 미설정: argv와 timeout_seconds를 설정하세요.')
    argv = value.get('argv')
    if not isinstance(argv, list) or not argv or any(not isinstance(s, str) or not s or '\0' in s for s in argv):
        raise KitError(f'{label}.argv는 비어 있지 않은 문자열 배열이어야 합니다. shell 문자열은 허용하지 않습니다.')
    timeout = value.get('timeout_seconds')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 86400:
        raise KitError(f'{label}.timeout_seconds는 양수여야 합니다.')


def config(root):
    cfg = read_json(root / 'verification/project.json')
    if not isinstance(cfg, dict) or cfg.get('schema_version') != VERSION:
        raise KitError('verification/project.json의 schema_version은 1이어야 합니다.')
    command_config(cfg.get('doctor'), 'doctor')
    command_config(cfg.get('cleanup'), 'cleanup')
    checks = cfg.get('checks')
    if not isinstance(checks, list) or not checks:
        raise KitError('checks 미설정: static, business, runtime 검사를 각각 등록하세요.')
    ids, kinds = set(), set()
    for item in checks:
        command_config(item, 'check')
        cid = item.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', cid) or cid in ids:
            raise KitError('검사 ID는 고유한 영숫자/밑줄/하이픈이어야 합니다.')
        ids.add(cid)
        if item.get('kind') not in ('static', 'business', 'runtime'):
            raise KitError(f'검사 종류 오류: {cid}')
        kinds.add(item['kind'])
    if kinds != {'static', 'business', 'runtime'}:
        raise KitError('static, business, runtime 검사가 각각 하나 이상 필요합니다.')
    env = cfg.get('env', {})
    if not isinstance(env, dict) or any(not isinstance(k, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', k) or not isinstance(v, str) or '\0' in v for k, v in env.items()):
        raise KitError('env는 문자열 환경변수 사전이어야 합니다.')
    required = cfg.get('required_env', [])
    if not isinstance(required, list) or any(not isinstance(k, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', k) for k in required):
        raise KitError('required_env는 환경변수 이름 배열이어야 합니다.')
    protected = {'KIT_RUN_DIR', 'TMPDIR', 'TZ', 'PYTHONHASHSEED', 'PYTHONDONTWRITEBYTECODE'}
    collisions = sorted(protected.intersection(env) | protected.intersection(required))
    if collisions:
        raise KitError('실행기가 관리하는 환경변수는 재정의할 수 없습니다: ' + ', '.join(collisions))
    missing = [key for key in required if key not in os.environ]
    if missing:
        raise KitError('필수 환경변수 미설정: ' + ', '.join(missing))
    limit = cfg.get('run_timeout_seconds', 120)
    if isinstance(limit, bool) or not isinstance(limit, (float, int)) or not math.isfinite(limit) or not 0 < limit <= 86400:
        raise KitError('run_timeout_seconds는 양수여야 합니다.')
    return cfg


def render_feature(meta):
    lines = ['---', json.dumps(meta, ensure_ascii=False, sort_keys=True), '---', '', '# ' + meta['id'] + ': ' + meta['title'], '', '이 파일은 메타데이터와 본문을 함께 검증합니다. 변경은 kit.py map add로 수행하세요.', '', '- 사전 조건: ' + meta['precondition'], '- 사용자 진입 경로: ' + meta['entry'], '- 조작/입력: ' + meta['action'], '- 관측할 결과: ' + meta['expected'], '', '## 소스', *['- ' + x for x in meta['sources']], '', '## 불변식', *['- ' + x for x in meta['invariants']], '', '## 검사', *['- ' + x for x in meta['checks']], '']
    return '\n'.join(lines)


def feature_metadata(root):
    result = []
    folder = root / FEATURES
    for path in sorted(folder.glob('*.md')):
        if path.name == 'README.md':
            continue
        try:
            content = path.read_text(encoding='utf-8')
            lines = content.splitlines()
            if len(lines) < 3 or lines[0] != '---' or lines[2] != '---':
                raise ValueError('JSON 한 줄 frontmatter가 필요합니다.')
            meta = json.loads(lines[1])
            if not isinstance(meta, dict):
                raise ValueError('메타데이터는 객체여야 합니다.')
            for key in ('id', 'title', 'entry', 'action', 'expected', 'precondition'):
                if not isinstance(meta.get(key), str) or not meta[key].strip():
                    raise ValueError(f'{key} 누락')
            if not re.fullmatch(r'F[0-9]+', meta['id']) or path.name != meta['id'] + '.md':
                raise ValueError('ID와 파일명이 일치해야 합니다.')
            for key in ('sources', 'invariants', 'checks'):
                if not isinstance(meta.get(key), list) or not meta[key] or any(not isinstance(v, str) or not v.strip() for v in meta[key]):
                    raise ValueError(f'{key}는 비어 있지 않은 문자열 배열이어야 합니다.')
            if content != render_feature(meta):
                raise ValueError('메타데이터/본문 불일치: map add로 갱신하세요.')
            result.append(meta)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise KitError(f'기능맵 오류 {path.name}: {exc}') from exc
    return result


def render_index(features):
    return '# 사용자 기능 인덱스\n\nkit.py map sync로 생성합니다. 각 기능은 실행 가능한 runtime 검사에 연결되어야 합니다.\n\n' + ''.join(f'- [{m["id"]}: {m["title"]}]({m["id"]}.md)\n' for m in sorted(features, key=lambda m: m['id']))


def map_check(root, cfg):
    features = feature_metadata(root)
    if not features:
        raise KitError('기능맵이 비어 있습니다. map add 후 map sync를 실행하세요.')
    checks = {c['id']: c for c in cfg['checks']}
    for meta in features:
        for source in meta['sources']:
            safe_file(root, source)
        unknown = set(meta['checks']) - set(checks)
        if unknown:
            raise KitError(f'{meta["id"]}: 존재하지 않는 검사 ID: {sorted(unknown)}')
        if not any(checks[c]['kind'] == 'runtime' for c in meta['checks']):
            raise KitError(f'{meta["id"]}: runtime 검사 연결이 필요합니다.')
    index = root / FEATURES / 'README.md'
    if not index.exists() or index.read_text(encoding='utf-8') != render_index(features):
        raise KitError('기능 인덱스 불일치: map sync를 실행하세요.')
    return features


def map_command(root, args):
    if args.map_command == 'add':
        if not re.fullmatch(r'F[0-9]+', args.id):
            raise KitError('기능 ID는 F001과 같은 형식이어야 합니다.')
        for source in args.source:
            safe_file(root, source)
        meta = dict(id=args.id, title=args.title, sources=args.source, entry=args.entry, action=args.action, expected=args.expected, invariants=args.invariant, checks=args.check, precondition=args.precondition)
        for key in ('title', 'entry', 'action', 'expected', 'precondition'):
            if not meta[key].strip() or '\n' in meta[key]:
                raise KitError(f'{key}는 비어 있지 않은 한 줄이어야 합니다.')
        folder = root / FEATURES
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (args.id + '.md')).write_text(render_feature(meta), encoding='utf-8')
        print('기능 저장 완료. 인덱스는 map sync로 갱신하세요.')
    elif args.map_command == 'sync':
        features = feature_metadata(root)
        (root / FEATURES).mkdir(parents=True, exist_ok=True)
        (root / FEATURES / 'README.md').write_text(render_index(features), encoding='utf-8')
        print('기능 인덱스 갱신 완료.')
    else:
        map_check(root, config(root))
        print('기능맵 검사 통과.')
    return 0


def staged_guard(root):
    diff = git(root, 'diff', '--name-only')
    untracked = git(root, 'ls-files', '--others', '--exclude-standard')
    if diff or untracked:
        raise KitError('부분 stage 금지: 추적 파일의 unstaged 변경 또는 미추적 파일이 있습니다. 모든 작업 파일을 stage하세요.')


def secret_scan(root):
    patterns = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), re.compile(rb'AKIA[0-9A-Z]{16}'), re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'), re.compile(rb'sk-' + rb'(?:proj-)?[A-Za-z0-9_-]{32,}')]
    for name in rel_files(root):
        path = root / name
        if not path.is_file() or path.is_symlink():
            continue
        data = path.read_bytes()
        if any(p.search(data) for p in patterns):
            raise KitError(f'실제 비밀 형식과 일치하는 내용 발견: {name} (값은 출력하지 않습니다). 이 검사는 제한적인 패턴 검사입니다.')


def mask(text, secrets):
    for value in sorted(set(secrets), key=len, reverse=True):
        if value:
            text = text.replace(value, '[REDACTED]')
    return text


def run_command(root, label, command, env, run_dir, deadline, secrets):
    started = time.monotonic()
    timeout = min(command['timeout_seconds'], max(0.001, deadline - started))
    result = {'id': label, 'passed': False, 'returncode': None, 'timed_out': False, 'log': label + '.log'}
    output = ''
    proc = None
    try:
        proc = subprocess.Popen(command['argv'], cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            data, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['timed_out'] = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                data, _ = proc.communicate(timeout=min(0.2, max(0.001, deadline - time.monotonic())))
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                data, _ = proc.communicate()
        output = data.decode(errors='replace')
        result['returncode'] = proc.returncode
        result['passed'] = proc.returncode == 0 and not result['timed_out'] and time.monotonic() <= deadline
    except OSError as exc:
        output = str(exc)
    finally:
        if proc is not None:
            # Synchronous checks must not leave children running after completion.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        (run_dir / result['log']).write_text(mask(output, secrets), encoding='utf-8')
    result['duration_seconds'] = round(time.monotonic() - started, 4)
    print(f'{label}: ' + ('통과' if result['passed'] else '실패') + (' (시간초과)' if result['timed_out'] else ''))
    return result


def check(root, staged=False, unit_deadline=None):
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:10]
    run_dir = root / '.kit/runs' / run_id
    run_dir.mkdir(parents=True)
    (run_dir / 'tmp').mkdir()
    report = {'schema_version': VERSION, 'run_id': run_id, 'status': 'FAIL', 'staged': staged, 'staged_tree': None, 'fingerprint': None, 'checks': [], 'errors': [], 'started_at': dt.datetime.now(dt.timezone.utc).isoformat()}
    cfg, secrets, before = None, [], None
    start = time.monotonic()
    try:
        if staged:
            staged_guard(root)
            report['staged_tree'] = git(root, 'write-tree')
        before = fingerprint(root)
        report['fingerprint'] = before
        cfg = config(root)
        secrets = [os.environ[k] for k in cfg.get('required_env', [])]
        map_check(root, cfg)
        secret_scan(root)
        env = {'PATH': os.environ.get('PATH', os.defpath), 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'}
        env.update(cfg.get('env', {}))
        env.update({k: os.environ[k] for k in cfg.get('required_env', [])})
        env.update(KIT_RUN_DIR=str(run_dir), TMPDIR=str(run_dir / 'tmp'))
        budget = cfg.get('run_timeout_seconds', 120)
        if unit_deadline is not None:
            budget = min(budget, max(0.001, unit_deadline - time.time()))
        deadline = start + budget
        # Reserve cleanup's configured time within the overall execution budget.
        main_deadline = deadline - min(cfg['cleanup']['timeout_seconds'], budget / 4)
        try:
            result = run_command(root, 'doctor', cfg['doctor'], env, run_dir, main_deadline, secrets)
            report['checks'].append(result)
            if result['passed']:
                for command in cfg['checks']:
                    if time.monotonic() >= main_deadline:
                        raise KitError('전체 실행 시간 제한에 도달했습니다.')
                    report['checks'].append(run_command(root, 'check-' + command['id'], command, env, run_dir, main_deadline, secrets))
        finally:
            report['unit_limit_reached'] = bool(unit_deadline is not None and budget < cfg.get('run_timeout_seconds', 120) and time.monotonic() >= main_deadline)
            report['checks'].append(run_command(root, 'cleanup', cfg['cleanup'], env, run_dir, deadline, secrets))
        if not all(c['passed'] for c in report['checks']) or len(report['checks']) != len(cfg['checks']) + 2:
            raise KitError('검증 또는 cleanup 실패. 로그를 확인하세요.')
        if time.monotonic() > deadline:
            raise KitError('전체 실행 시간 제한에 도달했습니다.')
        report['status'] = 'PASS'
    except (KitError, OSError, subprocess.SubprocessError) as exc:
        report['errors'].append(mask(str(exc), secrets))
    finally:
        after = fingerprint(root)
        report['fingerprint_after'] = after
        if before is not None and before != after:
            report['status'] = 'FAIL'
            report['errors'].append('검사 전후 소스/문서 지문이 변경되었습니다. 검사는 프로젝트 파일을 수정하면 안 됩니다.')
        if staged and report['staged_tree'] is not None:
            try:
                staged_guard(root)
                if git(root, 'write-tree') != report['staged_tree']:
                    raise KitError('검사 도중 Git 인덱스가 변경되었습니다.')
            except KitError as exc:
                report['status'] = 'FAIL'
                report['errors'].append(str(exc))
        report['duration_seconds'] = round(time.monotonic() - start, 4)
        def redact(value):
            if isinstance(value, str):
                return mask(value, secrets)
            if isinstance(value, list):
                return [redact(v) for v in value]
            if isinstance(value, dict):
                return {k: redact(v) for k, v in value.items()}
            return value
        report = redact(report)
        atomic_json(run_dir / 'report.json', report)
        atomic_json(root / '.kit/latest.json', report)
    for error in report['errors']:
        print(error)
    print(f'검증 결과: {report["status"]}; 증거: .kit/runs/{run_id}/report.json')
    return 0 if report['status'] == 'PASS' else 1


def managed(original, content, begin=BEGIN, end=END):
    block = begin + '\n' + content.rstrip() + '\n' + end
    if begin in original or end in original:
        if original.count(begin) != 1 or original.count(end) != 1 or original.index(end) < original.index(begin):
            raise KitError('관리 블록이 손상되었습니다.')
        a, tail = original.split(begin, 1)
        _, b = tail.split(end, 1)
        return a + block + b
    return original.rstrip('\n') + ('\n\n' if original else '') + block + '\n'


def install(target):
    source = Path(__file__).resolve().parent
    root = Path(target).expanduser().resolve()
    if not root.is_dir() or Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise KitError('--project는 기존 Git 저장소 루트여야 합니다.')
    hook_path = git(root, 'config', '--get', 'core.hooksPath', check=False)
    configured = hook_path.stdout.decode().strip()
    if configured and configured != '.githooks':
        raise KitError('기존 core.hooksPath를 덮어쓰지 않습니다: ' + configured)
    native_hooks = Path(git(root, 'rev-parse', '--git-common-dir')) / 'hooks'
    if not native_hooks.is_absolute():
        native_hooks = root / native_hooks
    if native_hooks.exists() and any(p.is_file() and not p.name.endswith('.sample') for p in native_hooks.iterdir()):
        raise KitError('기존 사용자 Git hook이 있습니다. 설치를 중지합니다.')
    expected_hooks = {'pre-commit': PRE_COMMIT.encode(), 'pre-push': PRE_PUSH.encode()}
    hooks = root / '.githooks'
    if hooks.exists():
        for path in hooks.iterdir():
            if not path.is_file() or path.name not in expected_hooks or path.read_bytes() != expected_hooks[path.name]:
                raise KitError('기존 사용자 .githooks를 덮어쓰지 않습니다: ' + path.name)
    copies = {}
    copy_modes = {}
    for relative in ('kit.py', 'scripts/check', 'RULE.md'):
        if not (source / relative).is_file():
            raise KitError('설치 원본 누락: ' + relative)
        copies[relative] = (source / relative).read_bytes()
        copy_modes[relative] = (source / relative).stat().st_mode & 0o777
    for relative in ('docs/fde', '.agents/skills', 'vendor/pstack'):
        folder = source / relative
        if not folder.is_dir():
            raise KitError('설치 원본 누락: ' + relative)
        for path in sorted(folder.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                copies[str(path.relative_to(source))] = path.read_bytes()
                copy_modes[str(path.relative_to(source))] = path.stat().st_mode & 0o777
    copies['FDE_GUIDE.md'] = (source / 'README.md').read_bytes()
    copy_modes['FDE_GUIDE.md'] = (source / 'README.md').stat().st_mode & 0o777
    conflicts = []
    for name, data in copies.items():
        dest = root / name
        if dest.is_symlink() or (dest.exists() and (not dest.is_file() or dest.read_bytes() != data)):
            conflicts.append(name)
        if any(p.exists() and (not p.is_dir() or p.is_symlink()) for p in dest.parents if p != root and root in p.parents):
            conflicts.append(name + ' (상위 경로 충돌)')
    if conflicts:
        raise KitError('설치 충돌; 변경하지 않았습니다: ' + ', '.join(conflicts))
    updates = {}
    for name, content, begin, end in [('AGENTS.md', (source / 'AGENTS.md').read_text(encoding='utf-8'), BEGIN, END), ('.gitignore', '.kit/\n__pycache__/\n*.pyc\n*.pyo\n.pytest_cache/', IGN_BEGIN, IGN_END)]:
        dest = root / name
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            raise KitError('관리 파일 경로 충돌: ' + name)
        updates[name] = managed(dest.read_text(encoding='utf-8') if dest.exists() else '', content, begin, end)
    defaults = {'work/intent.md': '# 작업 의도\n\n- 작업 단위:\n- 사용자 목표:\n- 완료 조건:\n', 'work/handoff.md': '# 인수인계\n\n- 현재 상태:\n- 검증 증거:\n- 다음 행동:\n', 'work/decisions.tsv': 'unit\tdecision\treason\tevidence\n', 'verification/project.json': json.dumps({'schema_version': 1, 'doctor': None, 'checks': [], 'cleanup': None, 'env': {}, 'required_env': [], 'run_timeout_seconds': 120}, ensure_ascii=False, indent=2) + '\n'}
    for name in [*updates, *defaults, '.githooks/pre-commit', '.githooks/pre-push']:
        dest = root / name
        if dest.is_symlink() or any(p.exists() and (not p.is_dir() or p.is_symlink()) for p in dest.parents if p != root and root in p.parents) or (dest.exists() and not dest.is_file()):
            raise KitError('설치 경로 충돌: ' + name)
    for name, data in copies.items():
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(copy_modes[name])
    for name, text in updates.items():
        (root / name).write_text(text, encoding='utf-8')
    for name, text in defaults.items():
        dest = root / name
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding='utf-8')
    hooks.mkdir(exist_ok=True)
    for name, data in expected_hooks.items():
        path = hooks / name
        path.write_bytes(data)
        path.chmod(0o755)
    (root / 'scripts/check').chmod(0o755)
    git(root, 'config', '--local', 'core.hooksPath', '.githooks')
    print('키트 설치 완료. 기존 README와 과제 파일은 보존했습니다.')
    doctor(root)
    return 0


def doctor(root):
    errors = []
    if sys.version_info < (3, 9):
        errors.append('Python 3.9 이상이 필요합니다.')
    if git(root, 'config', '--local', '--get', 'core.hooksPath', check=False).stdout.decode().strip() != '.githooks':
        errors.append('로컬 core.hooksPath가 .githooks로 설정되지 않았습니다.')
    for name, content in (('pre-commit', PRE_COMMIT), ('pre-push', PRE_PUSH)):
        path = root / '.githooks' / name
        if not path.is_file() or path.read_text() != content or not os.access(path, os.X_OK):
            errors.append('키트 hook 누락 또는 변경: ' + name)
    ignored = git(root, 'check-ignore', '--no-index', '.kit/probe', check=False)
    if ignored.returncode:
        errors.append('.kit/ Git 제외 설정이 필요합니다.')
    if git(root, 'ls-files', '--', '.kit'):
        errors.append('.kit/가 이미 Git 인덱스에 포함되어 있습니다. 인덱스에서 제외하세요.')
    try:
        cfg = config(root)
        map_check(root, cfg)
    except KitError as exc:
        errors.append('앱 검증 준비 미완료: ' + str(exc))
    for error in errors:
        print(error)
    print('구조·설정 검사: ' + ('미완료' if errors else '통과') + ' (앱 doctor 명령은 미실행; 실제 환경은 kit.py check로 확인)')
    return 1 if errors else 0


def begin(root, args):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.unit) or not args.goal.strip() or not math.isfinite(args.minutes) or args.minutes <= 0 or args.max_attempts < 1:
        raise KitError('작업 단위/목표/양수 제한을 확인하세요.')
    path = root / '.kit/unit.json'
    if path.exists():
        old = read_json(path)
        if old.get('unit') == args.unit:
            raise KitError('같은 작업 단위의 시도 횟수는 초기화할 수 없습니다. status를 확인하세요.')
        head = git(root, 'rev-parse', '--verify', 'HEAD', check=False).stdout.decode().strip()
        if old.get('result') != 'PASS' or not head or head == old.get('head_at_begin'):
            raise KitError('기존 단위가 검증 통과 후 커밋되지 않았습니다. 현재 단위를 계속 진행하세요.')
    now = time.time()
    value = {'unit': args.unit, 'goal': args.goal, 'started_at': now, 'deadline': now + args.minutes * 60, 'max_attempts': args.max_attempts, 'attempts': 0, 'result': None, 'head_at_begin': git(root, 'rev-parse', '--verify', 'HEAD', check=False).stdout.decode().strip()}
    atomic_json(path, value)
    print(f'작업 단위 시작: {args.unit}; 최대 {args.max_attempts}회, {args.minutes:g}분')
    return 0


def iterate(root, staged):
    path = root / '.kit/unit.json'
    if not path.exists():
        raise KitError('begin으로 작업 단위를 먼저 시작하세요.')
    unit = read_json(path)
    if unit.get('result') == 'LIMIT' or time.time() >= unit['deadline'] or unit['attempts'] >= unit['max_attempts']:
        print('중지: 작업 단위의 시간 또는 시도 한도에 도달했습니다.')
        return 2
    unit['attempts'] += 1
    unit['result'] = 'RUNNING'
    atomic_json(path, unit)
    result = check(root, staged, unit_deadline=unit['deadline'])
    latest = read_json(root / '.kit/latest.json')
    exceeded = time.time() >= unit['deadline'] or latest.get('unit_limit_reached', False) or (result != 0 and unit['attempts'] >= unit['max_attempts'])
    code = 2 if exceeded else result
    unit['result'] = 'PASS' if code == 0 else ('LIMIT' if code == 2 else 'FAIL')
    atomic_json(path, unit)
    entry = {'unit': unit['unit'], 'attempt': unit['attempts'], 'result': unit['result'], 'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(), 'run_id': read_json(root / '.kit/latest.json')['run_id']}
    with (root / '.kit/iteration.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f'반복 결과: {unit["result"]}; 시도 {unit["attempts"]}/{unit["max_attempts"]}')
    return code


def status(root):
    latest = root / '.kit/latest.json'
    if not latest.exists():
        raise KitError('검증 증거가 없습니다.')
    report = read_json(latest)
    state = report['status']
    if fingerprint(root) != report.get('fingerprint'):
        state = 'STALE'
    if report.get('staged'):
        try:
            staged_guard(root)
            if git(root, 'write-tree') != report.get('staged_tree'):
                state = 'STALE'
        except KitError:
            state = 'STALE'
    print(f'증거 상태: {state}; 실행: {report["run_id"]}')
    unit = root / '.kit/unit.json'
    if unit.exists():
        u = read_json(unit)
        print(f'작업 단위: {u["unit"]}; 시도 {u["attempts"]}/{u["max_attempts"]}; 결과 {u["result"]}')
    return 0 if state == 'PASS' else 1


def main():
    parser = argparse.ArgumentParser(description='로컬 커밋 전용 FDE 실행기')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('install', help='기존 Git 저장소에 설치')
    p.add_argument('--project', required=True)
    sub.add_parser('doctor', help='구조·설정 확인; 앱 doctor 명령은 check에서 실행')
    p = sub.add_parser('begin', help='제한된 작업 단위 시작')
    p.add_argument('--unit', required=True)
    p.add_argument('--goal', required=True)
    p.add_argument('--minutes', type=float, default=10)
    p.add_argument('--max-attempts', type=int, default=3)
    for name in ('check', 'iterate'):
        p = sub.add_parser(name)
        p.add_argument('--staged', action='store_true')
    sub.add_parser('status')
    p = sub.add_parser('map')
    ms = p.add_subparsers(dest='map_command', required=True)
    add = ms.add_parser('add')
    for field in ('id', 'title', 'entry', 'action', 'expected'):
        add.add_argument('--' + field, required=True)
    for field in ('source', 'invariant', 'check'):
        add.add_argument('--' + field, action='append', required=True)
    add.add_argument('--precondition', default='없음')
    ms.add_parser('sync')
    ms.add_parser('check')
    args = parser.parse_args()
    try:
        if args.command == 'install':
            return install(args.project)
        root = project()
        if args.command == 'doctor':
            return doctor(root)
        if args.command == 'begin':
            return begin(root, args)
        if args.command == 'check':
            return check(root, args.staged)
        if args.command == 'iterate':
            return iterate(root, args.staged)
        if args.command == 'status':
            return status(root)
        if args.command == 'map':
            return map_command(root, args)
    except (KitError, OSError, ValueError) as exc:
        print('오류: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
