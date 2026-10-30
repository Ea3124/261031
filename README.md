# 261031 — 작은 로컬 FDE 작업 키트

에이전트가 과제의 의도를 확인하고, 작은 변경을 구현하고, 같은 방법으로 검증한 뒤 코드와 증거를 함께 로컬 커밋하는 준비용 키트다.

실행은 Bash와 Git을 사용한다. 실제 과제의 검사 명령은 문제를 받은 뒤 verification/check에 작성한다. 기본 어댑터는 미설정으로 실패하며, 키트 자체 테스트 통과를 미래 과제의 검증으로 대신하지 않는다.

## 먼저 읽기
1. 실제 과제 안내와 기존 README, 원본 [RULE.md](RULE.md).
2. [AGENTS.md](AGENTS.md)와 [fde-workflow](.agents/skills/fde-workflow/SKILL.md).
3. 기존 [의도](docs/intent.md), [기능 맵](docs/features.md), [인계](docs/handoff.md).
4. 해당 단계에서만 필요한 [선별 스킬](docs/skills.md).

기대 동작·예외 처리·우선순위·성공 기준이 모호하면 반드시 사용자에게 질문한다. 관찰 가능한 코드와 실행 사실은 먼저 조사한다.

## 전체 흐름

~~~mermaid
flowchart TD
    A["목표·제약·기대 결과 확인<br/>모호한 기대는 사용자에게 질문"]
    B["작은 구현·필요한 문서 갱신"]
    C["같은 초기 상태·같은 방법으로 검증<br/>./scripts/check"]
    D{"실제 검증 통과?"}
    E["코드·증거 검토 후 함께 스테이징"]
    F["커밋 훅: 검증 대상 일치 확인"]
    G["로컬 커밋"]
    H["전환 전 인계 문서 작성<br/>증거는 .evidence/latest로 연결"]
    I["실제 결과·최종 SHA 전달"]

    A --> B --> C --> D
    D -->|실패| B
    D -->|통과| E --> F --> G
    G -->|다음 변경| B
    B -->|전환·완료 준비| H --> C
    G -->|인계 검증 완료| I
    B -->|기대 불명확| A
~~~

검증을 처음 만들거나 핵심 로직·검증 방법이 바뀌면 test-verifier를 사용한다. 모든 핵심 로직을 하나씩 의도적으로 손상하고, 같은 검증의 실제 실패와 정상 복구 후 성공을 증거로 남긴다. 문법 오류나 앱 시작 실패만으로 해당 비즈니스 로직을 검증했다고 하지 않는다.

## 구성

~~~text
.agents/skills/        필요한 부분만 편집한 7개 스킬
docs/intent.md        목표·제약·완료 조건·중요 판단
docs/features.md      실행 방법과 기능별 구체적인 기억
docs/handoff.md       현재 상태·한계·다음 행동
docs/skills.md        스킬별 용도와 선별 이유
docs/skill-selection.md 원본 61개 전체 검토·채택/제외표
scripts/check         공통 검증 입구
verification/check    과제별 실제 검사 명령
scripts/source-tree   증거를 제외한 Git 내용 식별
scripts/setup         로컬 훅 연결
.githooks/            검증 대상 일치 확인·push 차단
.evidence/            실제 검증 증거, 코드와 함께 Git 기록
tests/                공통 도구 자체의 계약 검사
vendor/pstack/        고정 원본과 라이선스, 비활성 비교 자료
~~~

예전 kit.py, 고정 JSON 기능 맵 생성기, begin/iterate 상태 관리, examples/, reports/는 제거했다. 기능 맵은 자유로운 Markdown이고, 작업 예산은 실제 종료 시각에 맞춰 에이전트가 관리한다.

## 과제 프로젝트에서 사용하기

제공 환경이 허용한 방식으로 공개 키트를 가져온다. 기존 과제 README·코드·규칙·사용자 훅을 덮어쓰지 않는다. 같은 이름의 파일이 있으면 먼저 읽고 충돌을 해결한다. 원본 vendor와 키트 자체 tests는 실제 과제 실행에 필요하지 않다. 전역 스킬·모델 설정을 변경하지 않으며 재귀 설치로 vendor 원본을 활성화하지 않는다.

1. .agents/skills와 지침·문서, scripts, verification/check, .githooks를 과제의 Git 루트에 충돌 없이 합친다. 기존 .gitignore에 .evidence/tmp/ 같은 폐기용 상태 제외를 병합하되 .evidence/ 전체는 제외하지 않는다.
2. 실제 과제에 맞게 docs/intent.md와 docs/features.md의 실행 절차, verification/check를 작성한다.
3. 핵심 로직별 정상·결함주입 실패·복구 성공을 실증한다.
4. 다음 고정 순서로 실행한다.

~~~sh
./scripts/setup
./scripts/check
git diff
git status --short
git add -A
git diff --cached
git commit -m "이번 변경의 목적과 결과"
~~~

scripts/setup은 기존의 다른 hooksPath나 사용자 훅이 있으면 중지한다. 기존 훅을 자동 덮어쓰지 않는다.

검증 실패 뒤에는 수정하고 ./scripts/check부터 다시 수행한다. 검사 이후 소스·문서·검사 코드가 바뀌면 새 검증이 필요하다. 커밋 훅은 앱 검사를 다시 실행하거나 증거를 자동 스테이징하지 않는다.

세션을 넘길 때는 docs/handoff.md를 마지막 검증 전에 먼저 작성하고 증거는 안정적인 .evidence/latest로 연결한다. 그 뒤 검증 → 함께 스테이징 → 커밋한다. 최종 SHA와 실제 통과 결과는 완료 응답에 남긴다. 커밋 뒤 인계를 다시 고치면 재검증·커밋이 필요하다.

## 증거와 커밋의 관계

- scripts/check는 verification/check를 실행하고 EVIDENCE_DIR로 고유 실행 폴더를 전달한다.
- .evidence/run-시각-고유값/output.log와 result를 남기며 .evidence/latest는 마지막 실행 ID를 가리킨다. 실패 실행도 별도로 보존한다.
- result에는 status, tree, exit_code, command를 기록한다. tree는 증거를 제외한 Git 내용 식별자다.
- 커밋 훅은 Git이 추적할 수 있는 작업 파일·스테이징 내용·스테이징된 통과 증거의 대상이 같은지 확인한다. 최신 결과가 실패하거나 증거가 빠졌거나 내용이 바뀌면 거절한다.
- .evidence/는 Git 관리 대상이다. 폐기할 임시 상태만 .evidence/tmp/에 격리한다. 앱 검사는 증거를 정리 과정에서 지우지 않는다.
- submodule은 초기화돼 있고 내부 미커밋 변경이 없어야 한다. 직접 자식의 깨끗한 HEAD 변경은 Git이 기록한 gitlink로 식별하며, 중첩 변경은 부모 submodule에도 커밋돼 있어야 한다.
- Git이 무시한 실행 입력·외부 DB·설치된 의존성·현재 환경은 이 트리 식별에 포함되지 않는다. 문제별 절차가 버전·체크섬·고정 데이터·재생성 방법으로 통제하고 증거를 남겨야 한다.
- 의미 있는 입력·기대값·실제 결과·부수효과·버전·결함주입 patch와 실패/복구 결과는 문제별 검사에서 함께 남긴다. 소스와 무관한 비밀 값이나 개인 데이터는 기록하지 않는다.
- 이 연결은 실수로 오래된 증거를 쓰는 일을 막는 장치다. 악성 검증 스크립트·허위 기대값·수정한 영수증을 신뢰할 수 있게 만드는 보안 샌드박스는 아니다.

## 확장 기준

문제를 만난 위치에 필요한 검사와 문서를 추가한다. 새 기능은 기능 맵과 회귀 검사에, 서버는 해당 실행·준비·요청·정리 코드에, 성능 요구는 고정 입력·기준값·반복 측정에 추가한다. 공통 루프에 예산 상태나 스키마를 먼저 늘리지 않는다.

사용자 기대는 사용자에게 확인하고, 실제 실행은 같은 절차로 반복하며, 모든 핵심 로직의 검증기는 개별 결함주입으로 확인한다. UI 확인과 형식 증명 등 수행하지 않은 범위는 명확히 남긴다.

## 키트 유지보수

이 공개 저장소 자체를 정비할 때는 아래 명령으로 공통 도구를 검증한다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
~~~

이것은 과제 앱 검증이 아니다. 미설정 verification/check는 그대로 실패해야 한다. 실제 과제 프로젝트에서만 앱 검사와 훅을 설정한다.

## 출처

pstack 원본은 [backnotprop/pstack](https://github.com/backnotprop/pstack)의 25abb38559ddbabec563646224d09eff9a250eca다. 루트 스킬 58개와 Benny의 3개를 전문 검토하고 필요한 개념만 7개 스킬로 편집했다. 원본 전체와 파일별 해시는 vendor/pstack에 비교용으로 보존하며 실제 실행 의존성으로 사용하지 않는다. 편집된 스킬에도 [원본 MIT 허가문](.agents/skills/LICENSE.pstack)을 포함한다.
