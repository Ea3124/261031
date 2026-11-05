#!/usr/bin/env bash
# 사용: 실제 과제 폴더에서 bash /tmp/261031/setup.sh [과제 폴더]
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    printf '사용: bash setup.sh [기존 과제 폴더]\n'
    printf '인자 생략 시 현재 폴더에 안내서와 스킬 7개를 생성합니다.\n'
    printf '같은 내용은 보존하고 다른 내용의 기존 파일은 덮어쓰지 않습니다.\n'
    exit 0
fi
if [[ "$#" -gt 1 ]]; then
    printf '설치 중지: 과제 폴더 하나만 지정하세요.\n' >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    printf '설치 중지: Python 3.8 이상이 필요합니다.\n' >&2
    exit 1
fi

kit_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
target_dir="${1:-$PWD}"

python3 - "$kit_dir" "$target_dir" <<'PY'
import os
from pathlib import Path
import re
import sys
import tempfile


def fail(message):
    raise ValueError(message)


def install():
    if sys.version_info < (3, 8):
        fail("Python 3.8 이상이 필요합니다.")

    kit = Path(sys.argv[1]).resolve(strict=True)
    target = Path(sys.argv[2]).expanduser().resolve(strict=True)
    if not target.is_dir():
        fail("기존 과제 디렉터리를 지정하세요.")
    if target == kit or kit in target.parents:
        fail("키트 원본이나 그 하위 폴더가 아닌 실제 과제 폴더에서 실행하세요.")

    source = kit / "readme.kit.md"
    if source.is_symlink() or not source.is_file():
        fail("키트 원본 readme.kit.md가 일반 파일이어야 합니다.")
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    expected = (
        "cofa-workflow", "cofa-discovery", "cofa-prd", "cofa-architecture",
        "cofa-build", "cofa-verify", "cofa-understanding-coach",
    )
    pattern = r"^<!-- skill: ([a-z0-9-]+) -->\r?\n```markdown\r?\n(.*?)\r?\n```[ \t]*$"
    blocks = re.findall(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if tuple(name for name, _ in blocks) != expected:
        fail("스킬 원문의 누락·중복·순서를 확인하세요. 필요한 블록은 7개입니다.")

    outputs = {Path("readme.kit.md"): raw}
    for name, body in blocks:
        lines = body.splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            fail("YAML 머리말이 없습니다: " + name)
        end = lines.index("---", 1)
        metadata = {}
        for line in lines[1:end]:
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = value.strip()
        if metadata.get("name") != name or not metadata.get("description", "").strip("\"' "):
            fail("스킬 name 또는 description을 확인하세요: " + name)
        outputs[Path(".agents") / "skills" / name / "SKILL.md"] = (body + "\n").encode("utf-8")

    # 모든 대상 경로를 쓰기 전에 검사한다. 기존 하위 symlink는 따라가지 않는다.
    pending = []
    preserved = []
    for relative, content in outputs.items():
        parent = target
        for part in relative.parts[:-1]:
            parent = parent / part
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                fail("디렉터리 충돌 또는 symlink: " + str(parent))
        destination = target / relative
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            fail("일반 파일이 아닌 대상: " + str(destination))
        if destination.exists():
            if destination.read_bytes() != content:
                fail("기존 파일과 내용이 달라 보존했습니다. 먼저 비교하세요: " + str(destination))
            preserved.append(relative)
        else:
            pending.append((relative, content))

    # 완성된 임시 파일을 배타적으로 연결해 생성 중인 파일이나 기존 파일을 덮어쓰지 않는다.
    for relative, content in pending:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=str(destination.parent), prefix=".cofa-kit-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            temporary.chmod(0o644)
            try:
                os.link(str(temporary), str(destination))
            except FileExistsError:
                if destination.is_symlink() or not destination.is_file() or destination.read_bytes() != content:
                    fail("설치 중 대상이 변경됐습니다. 기존 경로를 보존했습니다: " + str(destination))
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        print("준비: " + str(relative))

    for relative in preserved:
        print("보존: " + str(relative))
    print("\n설치 완료: " + str(target))
    print("안내서와 스킬 7개를 준비했습니다. 실제 과제 규칙과 README를 먼저 확인하세요.")
    print("Codex에서 $cofa-workflow를 요청해 문답·PRD·설계·구현·검증을 시작하세요.")
    print("각 핵심 단계 뒤에 작은 검증과 사용자 역질문 한 개를 반복합니다.")
    print("앱 검증·제출·커밋은 실행하지 않았습니다.")


try:
    install()
except (OSError, ValueError, UnicodeError) as error:
    print("설치 중지: " + str(error), file=sys.stderr)
    sys.exit(1)
PY
