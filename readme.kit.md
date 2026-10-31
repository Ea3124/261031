# 261031 — 로컬 FDE 작업 키트

과제의 뜻을 확인하고, 작은 기능을 구현하고, 같은 방법으로 검증한 뒤 코드와 증거를 함께 로컬 커밋하는 키트다. **과제 README.md는 그대로 두고 키트 설명은 이 readme.kit.md에서 읽는다.**

## 먼저 읽기

1. 실제 과제 안내·과제 README.md·[RULE.md](RULE.md).
2. [AGENTS.md](AGENTS.md)와 [01-fde-workflow](.agents/skills/01-fde-workflow/SKILL.md).
3. [의도](docs/intent.md)·[기능 맵](docs/features.md)·[인계](docs/handoff.md)의 실제 현재 내용.
4. 필요한 단계의 역할과 사용 예시는 [readme.skill.md](readme.skill.md).

기대 동작이나 성공 기준이 정해지지 않았으면 먼저 질문한다. 코드·파일·실행 결과에서 확인할 수 있는 사실은 조사한다. 업무 메신저에는 질문 초안을 준비하고, 실제 전달과 화면 조작은 RULE.md가 정한 사람이 수행한다.

## 번호로 보는 흐름

번호는 역할을 찾기 위한 표시다. 매 작업마다 7개를 전부 호출하는 순서는 아니다. 구현은 과제 코드에서 하고, 스킬은 해당 단계의 판단을 돕는다.

~~~mermaid
flowchart TD
    Z["최초 1회 설치<br/>과제 Git 루트에서 bash /tmp/261031/setup.sh"]
    A["01-fde-workflow<br/>문제·요구·업무 질문·기대 결과 정리"]
    B["02-design-change: 설계·작은 구현<br/>03-feature-map: 기능·접근법 갱신"]
    C["04-verify-app: 같은 방법으로 검증<br/>처음·핵심 변경 때 05-test-verifier로 검증기 실증"]
    D{"실제 검사 통과?"}
    J["06-debug-root-cause<br/>재현·원인 확인·수정"]
    E["코드·문서·증거 검토 후 함께 스테이징"]
    F["커밋 훅: 검증 대상 일치 확인"]
    G["로컬 커밋"]
    H["07-handoff<br/>최종 검증 전에 인계 작성"]
    I["실제 결과·한계·최종 SHA 전달"]

    Z --> A --> B --> C --> D
    D -->|실패| J --> B
    D -->|통과| E --> F --> G
    G -->|다음 변경| B
    B -->|전환·완료 준비| H --> C
    G -->|인계 검증 완료| I
    B -->|기대 불명확| A
~~~

04는 실제 검사를 준비·실행하는 역할이고, 05는 그 검사가 잘못된 로직도 잡는지 확인하는 역할이다. 05에서는 모든 핵심 규칙을 하나씩 실제로 손상해 같은 검사로 실패를 관측하고, 복구 후 성공까지 보존한다. 문법 오류나 시작 실패만으로 업무 규칙을 검증했다고 하지 않는다.

## 최초 설치

실제 과제 Git 루트에서 공개 키트를 별도 경로에 내려받고 실행한다. /tmp/261031이 이미 있으면 삭제하지 말고 출처·버전을 확인한다.

~~~sh
# 현재 위치: 실제 과제의 Git 루트
git clone https://github.com/Ea3124/261031.git /tmp/261031
bash /tmp/261031/setup.sh
~~~

설치기는 자신의 위치에서 원본을 찾고, 현재 과제 Git 루트에 필요한 파일만 추가한다. 키트 원본 자체·하위 폴더·Git 저장소가 아닌 곳에서는 중지한다.

- readme.kit.md·readme.skill.md, 번호가 붙은 스킬 7개와 출처 허가문, 의도·기능 맵·인계 문서, 공통 도구·훅·검사 어댑터·지침을 설치한다.
- 과제 README.md·코드·기존 문서·실행 가능한 verification/check는 보존한다. 재실행해도 과제용 내용을 초기 틀로 되돌리지 않는다.
- 기존 AGENTS.md가 다르면 AGENTS.kit.md와 읽기 참조를 추가한다. 기존 RULE.md가 다르면 RULE.kit.md를 비교용으로 둔다. 실제 과제 규칙이 우선한다.
- 번호 없는 구버전 스킬이 설치된 과제에서는 자동으로 섞지 않고 중지한다. 기존 수정 내용을 비교해 정리한 뒤 재실행한다. 설치기가 구버전 파일을 임의 삭제하지 않는다.
- 다른 내용의 공통 도구·스킬·키트 안내서·허가문, symlink, 실행 권한 누락, ignore로 가려진 필수 파일·증거, 기존 사용자 훅은 복사 전에 확인하고 중지한다.
- 기존 .gitignore에 폐기용 .evidence/tmp/ 제외만 추가하고, 로컬 core.hooksPath를 .githooks로 연결한다. scripts/setup --check는 훅 충돌 확인만 한다.
- 네트워크·패키지 설치·전역 설정 변경·Git 초기화·앱 검사·스테이징·커밋은 설치기가 하지 않는다. 디스크·권한 오류로 복사 중 멈추면 추가된 파일이 남을 수 있으며, 비파괴 재실행으로 이어간다.

원본 아카이브 vendor/는 제거했다. 이미 편집한 스킬과 필요한 허가문만 유지한다. 키트 자체 tests·과거 .evidence·선정 감사표는 과제 프로젝트에 설치하지 않는다.

## 매 변경의 실행 순서

설치 뒤 docs/intent.md·docs/features.md와 verification/check를 실제 문제에 맞게 채운다. 기본 verification/check는 미설정으로 종료 코드 2를 반환한다. 설치 성공을 앱 검증 성공으로 취급하지 않는다.

~~~sh
./scripts/check
git diff
git status --short
git add -A
git diff --cached
git commit -m "이번 변경의 목적과 결과"
~~~

실패하면 원인을 수정하고 ./scripts/check부터 다시 실행한다. 검사 뒤 소스·문서·검사 코드가 바뀌면 새 검증이 필요하다. 훅은 앱 검사 재실행·파일 수정·자동 스테이징을 하지 않는다.

세션 전환·완료 때는 07-handoff로 docs/handoff.md를 **마지막 검증 전에** 작성한다. 증거는 .evidence/latest로 연결하고 검증 → 함께 스테이징 → 커밋한다. 최종 SHA와 실제 결과는 완료 응답에 남긴다. 검증할 수 없으면 미검증·미커밋 상태를 그대로 인계한다.

## 증거가 연결되는 방식

- scripts/check는 verification/check를 실행하고 EVIDENCE_DIR로 고유 실행 폴더를 전달한다.
- .evidence/run-시각-고유값/output.log와 result를 남긴다. .evidence/latest는 실패도 포함한 마지막 실행을 가리킨다.
- result의 status·tree·exit_code·command를 기록하고, 훅은 작업 내용 = 스테이징 내용 = 통과 영수증의 tree인지 확인한다. 최신 증거나 파일이 빠지면 커밋을 막는다.
- .evidence/는 Git 관리 대상이다. 폐기 상태만 .evidence/tmp/에 두고, 입력·독립 기대값·실제 결과·부수효과·결함주입 patch·실패/복구 결과는 보존한다. 비밀 값과 개인 데이터는 기록하지 않는다.
- submodule은 초기화돼 있고 내부 미커밋 변경이 없어야 한다. 깨끗한 직접 HEAD 변경은 gitlink로 식별하고, 중첩 변경은 부모에도 커밋돼 있어야 한다.
- ignored 입력·외부 DB·설치된 의존성·환경 값은 Git 트리에 포함되지 않는다. 문제별 절차에서 버전·체크섬·고정 데이터·초기화 방법으로 통제한다.
- 이 연결은 오래된 증거와 부분 stage를 막는 장치다. 잘못된 기대값·허위 검사·위조 영수증을 판별하는 보안 샌드박스는 아니다.

## 파일을 찾을 때

~~~text
readme.kit.md          설치·전체 흐름·검증과 커밋
readme.skill.md        01–07 역할 설명·상황별 사용 흐름
.agents/skills/        번호별 판단 지침과 출처 허가문
docs/intent.md        목표·요구·질문·합의·핵심 규칙
docs/features.md      기능별 목적·접근법·기대 결과·검사
docs/handoff.md       실제 상태·한계·다음 행동
setup.sh              별도 과제에 최초 설치
scripts/setup         훅 충돌 확인·로컬 연결
scripts/check         공통 검증 입구
verification/check    과제별 실제 명령
scripts/source-tree   증거를 제외한 Git 내용 식별
.githooks/            커밋 대상 일치 확인·push 차단
.evidence/            코드와 함께 기록하는 실증 증거
~~~

## 키트 자체를 수정할 때

키트 원본에는 과제용 설치기를 실행하지 않는다. 아래 검사는 설치·공통 도구를 임시 Git 저장소에서 확인하며, 실제 과제 앱의 기능 검증을 대신하지 않는다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
~~~

## 출처와 추가 설명

pstack의 필요한 판단만 선별·편집했으며 [원본 MIT 고지](.agents/skills/LICENSE.pstack)를 유지한다. 시작 단계에는 cofa-ready-kit의 요구 파악·질문 정리 관점을 새 문장으로 작성했고 [해당 MIT 고지](.agents/skills/LICENSE.cofa-ready-kit)도 포함한다. 실제 메시지를 보내거나 원본 자동화를 활성화하지 않는다.

선정 이력은 [공개 저장소의 감사표](https://github.com/Ea3124/261031/blob/main/docs/skill-selection.md), README를 받은 순간부터 제출까지의 상세 흐름은 [180분 작업 시나리오](readme.skill.md#180분-작업-시나리오)에서 확인한다.

최초 설치 방식은 [cofa-kit/setup.sh](https://github.com/JinwooKim-git/cofa-kit/blob/main/setup.sh)의 현재 폴더 복사·기존 파일 보존 개념을 우리 구조에 맞게 독립 구현했다.
