#!/usr/bin/env bash
# 과제 Git 루트에서 실행: bash /tmp/261031/setup.sh
# 설치 방식 참고: https://github.com/JinwooKim-git/cofa-kit/blob/main/setup.sh
set -euo pipefail

fail() { printf '설치 중지: %s\n' "$1" >&2; exit 1; }
exists() { [ -e "$1" ] || [ -L "$1" ]; }
kit=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
target=$(pwd -P)
top=$(git rev-parse --show-toplevel 2>/dev/null) || fail '과제 Git 루트에서 실행하세요. Git 저장소를 자동 생성하지 않습니다.'
top=$(cd "$top" && pwd -P)
[ "$target" = "$top" ] || fail '하위 폴더가 아닌 과제 Git 루트에서 실행하세요.'
[ "$target" != "$kit" ] || fail '키트 원본이 아닌 별도 과제 Git 루트에서 실행하세요.'
[ "$#" -eq 0 ] || fail '인자 없이 과제 Git 루트에서 실행하세요.'

# 모든 충돌을 먼저 확인한다. 외부 경로로 연결되는 symlink는 따라가지 않는다.
check_path() {
    local path=$1 parent=$1
    while [[ "$parent" = */* ]]; do
        parent=${parent%/*}
        if exists "$parent" && { [ ! -d "$parent" ] || [ -L "$parent" ]; }; then
            fail "디렉터리 충돌 또는 symlink: $parent"
        fi
    done
    if exists "$path" && { [ ! -f "$path" ] || [ -L "$path" ]; }; then
        fail "일반 파일이 아닌 경로: $path"
    fi
}
runtime=(
    readme.kit.md readme.skill.md
    .agents/skills/LICENSE.pstack .agents/skills/LICENSE.cofa-ready-kit
    scripts/check scripts/source-tree scripts/setup
    .githooks/pre-commit .githooks/pre-push
)
for skill in 01-fde-workflow 02-design-change 03-feature-map 04-verify-app 05-test-verifier 06-debug-root-cause 07-handoff; do
    legacy=".agents/skills/${skill#??-}/SKILL.md"
    if exists "$legacy"; then
        fail "번호 없는 이전 스킬을 보존했습니다: $legacy. 새 스킬과 중복되지 않도록 내용을 비교해 이전 경로를 정리한 뒤 다시 실행하세요."
    fi
    runtime+=(".agents/skills/$skill/SKILL.md")
done
preserved=(docs/intent.md docs/features.md docs/handoff.md verification/check)
for path in "${runtime[@]}" "${preserved[@]}" AGENTS.md RULE.md; do
    [ -f "$kit/$path" ] && [ ! -L "$kit/$path" ] || fail "키트 원본 누락: $path"
    check_path "$path"
done
for path in "${runtime[@]}"; do
    if exists "$path" && ! cmp -s "$kit/$path" "$path"; then
        fail "기존 공통 도구·스킬을 덮어쓰지 않습니다: $path. 내용을 비교해 먼저 해결하세요."
    fi
    case "$path" in
        scripts/*|.githooks/*)
            [ -x "$kit/$path" ] || fail "키트 실행 권한 누락: $path"
            if [ -f "$path" ] && [ ! -x "$path" ]; then
                fail "기존 실행 파일의 권한을 보존했습니다: $path. 실행 권한을 확인한 뒤 다시 실행하세요."
            fi ;;
    esac
done
[ -x "$kit/verification/check" ] || fail '키트 실행 권한 누락: verification/check'
if [ -f verification/check ] && [ ! -x verification/check ]; then
    fail '기존 verification/check를 보존했습니다. 실행 권한을 확인한 뒤 다시 실행하세요.'
fi

agents=AGENTS.md
if [ -f AGENTS.md ] && ! cmp -s "$kit/AGENTS.md" AGENTS.md; then agents=AGENTS.kit.md; fi
rules=RULE.md
if [ -f RULE.md ] && ! cmp -s "$kit/RULE.md" RULE.md; then rules=RULE.kit.md; fi
for pair in "AGENTS.md:$agents" "RULE.md:$rules"; do
    source=${pair%%:*}; destination=${pair#*:}
    check_path "$destination"
    if [ "$source" != "$destination" ] && exists "$destination" && ! cmp -s "$kit/$source" "$destination"; then
        fail "기존 참고 문서 충돌: $destination. 내용을 비교해 먼저 해결하세요."
    fi
done
check_path LICENSE.261031
[ -f "$kit/LICENSE" ] && [ ! -L "$kit/LICENSE" ] || fail '키트 원본 누락: LICENSE'
if exists LICENSE.261031 && ! cmp -s "$kit/LICENSE" LICENSE.261031; then
    fail '기존 LICENSE.261031을 덮어쓰지 않습니다. 내용을 비교해 먼저 해결하세요.'
fi
check_path .gitignore
check_not_ignored() {
    local reason=$1 ignored
    shift
    if git check-ignore --no-index -- "$@" > /dev/null; then
        fail "$reason 기존 추적 여부와 관계없이 ignore 충돌을 먼저 해결하세요."
    else
        ignored=$?
        [ "$ignored" -eq 1 ] || fail '기존 ignore 규칙을 확인하지 못했습니다.'
    fi
}
check_not_ignored '.evidence 실행 증거가 ignore 규칙에 가려집니다. 증거는 추적하고 .evidence/tmp/만 제외해야 합니다.' \
    .evidence/latest .evidence/run-kit-probe/result .evidence/run-kit-probe/output.log
check_not_ignored '필수 키트 설치 파일이 ignore 규칙에 가려집니다.' \
    "${runtime[@]}" "${preserved[@]}" AGENTS.md "$agents" RULE.md "$rules" LICENSE.261031 .gitignore
bash "$kit/scripts/setup" --check

copy_missing() {
    local source=$1 destination=$2
    if [ -f "$destination" ]; then
        printf '보존: %s\n' "$destination"
    else
        mkdir -p "$(dirname "$destination")"
        cp -p -n "$kit/$source" "$destination"
        printf '추가: %s\n' "$destination"
    fi
}
for path in "${runtime[@]}" "${preserved[@]}"; do copy_missing "$path" "$path"; done
copy_missing LICENSE LICENSE.261031
copy_missing AGENTS.md "$agents"
copy_missing RULE.md "$rules"
if [ "$agents" = AGENTS.kit.md ] && ! grep -Fqx '<!-- 261031-kit -->' AGENTS.md; then
    cat >> AGENTS.md <<'POINTER'

<!-- 261031-kit -->
작업을 시작할 때 AGENTS.kit.md도 읽는다. 실제 과제 안내와 기존 규칙을 우선하고, RULE.kit.md가 있으면 차이도 확인한다.
<!-- /261031-kit -->
POINTER
fi
if [ ! -f .gitignore ] || ! grep -Fqx '.evidence/tmp/' .gitignore; then
    printf '\n# 261031: 폐기용 상태만 제외하고 실행 증거는 추적한다.\n.evidence/tmp/\n' >> .gitignore
fi
bash ./scripts/setup
printf '\n설치 완료. 실제 과제 안내·RULE.md·AGENTS.md를 먼저 읽으세요.\n'
if [ "$rules" = RULE.kit.md ]; then
    printf '기존 RULE.md를 보존하고 키트 규칙을 RULE.kit.md에 두었습니다. 실제 과제 규칙이 우선합니다.\n'
fi
printf '키트 안내는 readme.kit.md, 단계별 스킬과 시나리오는 readme.skill.md에서 확인하세요.\n'
printf 'docs/intent.md·docs/features.md와 verification/check를 과제에 맞게 작성하세요.\n'
printf '그 뒤 ./scripts/check → 코드·증거 함께 스테이징 → 커밋 순서로 진행하세요.\n'
printf '앱 검증·스테이징·커밋은 실행하지 않았습니다. 재실행은 기존 과제 문서와 검사 어댑터를 보존합니다.\n'
