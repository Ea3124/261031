# pstack 선정 목록과 실전 대체 규칙

## 보존과 실행을 구분한다

원본은 backnotprop/pstack의 고정 SHA에서 가져왔고 파일별 해시와 실행 권한을 vendor/pstack/ORIGIN.json에 기록했다. 루트 SKILL.md 58개를 소스감사에서 전문 읽었다. README의 의존성 표와 실제 본문을 비교했으며, 원본 표에 없는 전이 의존성도 확인했다.

전이 참조가 끊기지 않고 원문과 비교할 수 있도록 원본 58개와 참조 자료를 모두 보존한다. 이것은 58개를 전부 활성화한다는 뜻이 아니다. 설치기는 명시적으로 .agents/skills/fde-workflow와 verify-app만 활성 경로로 복사한다. vendor 자료도 프로젝트에 보존하지만 npx skills add 같은 재귀 탐색 설치 명령은 사용하지 않는다.

다음 표가 실제 흐름에서 참고할 목록이다. 원본의 모델·위임·외부 도구 호출은 실행하지 않고 아래 대체 규칙을 사용한다. 단계마다 모든 스킬을 읽는 것은 아니며 필요한 원본만 조사한다.

## 단계별 선정

| 단계 | 원본 스킬 | 채택할 내용 | 로컬 실전 적용 |
|---|---|---|---|
| 문제·목표 | in-your-own-words | 사용자 문제와 목표를 자기 말로 확인 | work/intent.md의 문제·제약·완료 조건 |
| 문제 해결 | figure-it-out | 관찰 가능한 목표, 가설, 최소 실험, 종료 조건 | fde-workflow의 단위 반복. 원본 poteto-mode 전체 호출 제외 |
| 기존 코드 이해 | how | 실행 흐름·경계·저장 상태·함정 조사 | 같은 Codex가 소스와 로컬 실행으로 조사 |
| 설계 | architect | 호출자 사용례·자료형·모듈 경계와 설계 근거 | 복잡할 때만 두 대안을 순차 비교. 강제 다중 모델·arena 실행 제외 |
| 최소 구현 | principle-model-the-domain, principle-foundational-thinking, principle-laziness-protocol | 상태를 자료형에 모으고 작은 완결 흐름 선택 | 문제에 맞는 가장 작은 자료구조와 구현 |
| 사용자 결과 | principle-experience-first | 사용자 흐름이 실제로 완결되는지 확인 | 인수 조건을 사용자 입력·결과로 작성 |
| 경계와 타입 | principle-boundary-discipline, principle-type-system-discipline | 입력 경계 검증과 잘못된 상태 방지 | 실제 언어·기존 스키마에 맞춰 적용 |
| 검증 구축 | create-verification-skill | 실행·준비 확인·조작·증거·정리, 기능 맵 초기화 | verify-app과 project.json 작성. 화면 자동조작 경로 제외 |
| 실제 증명 | principle-prove-it-works | 실제 산출물과 값을 실행해 확인 | CLI·HTTP·파일·저장 부수효과까지 관찰 |
| 재실행 도구 | principle-build-the-lever | 검사를 재실행 가능한 도구로 제공 | scripts/check와 앱별 검사 코드 |
| 검사 품질 | principle-test-behavior-not-implementation | 요구사항에서 기대값을 정하고 사용자 동작 검증 | 실제 진입점·독립된 기대 결과·오류 입력 |
| 버그 수정 | tdd | 저렴한 회귀 검사로 수정 전 실패·수정 후 성공 | 기존 검사와 허용된 명령 사용. UI 자동화 fallback 제외 |
| 기능 맵 유지 | maintain-verification-skill | 소스 비교·전체 기능 실행·문서 드리프트 분류 | 기능별 순차 조사와 실행. PR 대신 로컬 커밋 |
| 작업 순서 | principle-sequence-verifiable-units | 작은 단위마다 검증하고 다음으로 진행 | 현재 SHA·변경 상태부터 기록. 원격 trunk rebase 요구 제외 |
| 재시도 | principle-make-operations-idempotent | 재실행·중단 뒤 같은 상태로 수렴 | 초기 데이터 격리와 중복 실행 검사 |
| 원인 수정 | principle-fix-root-causes, principle-attack-the-premise | 증상을 숨기지 않고 최초 오류와 잘못된 가설 수정 | 실제 실패 로그·동일 입력으로 재현 |
| 판단 기록 | show-me-your-work | 결정·이유·증거·결과의 단일 기록 | work/decisions.tsv. 다른 모델 계열 리뷰 요구 제외 |
| 반복 오류 예방 | correct, principle-encode-lessons-in-structure | 반복 실수를 검사·타입·스크립트로 옮김 | 실제 관측된 반복 문제에만 좁게 적용 |
| 영향·위험 | blast-radius, interrogate | 변경 밖의 계약을 읽고 재현된 위험만 보고 | 같은 Codex의 검토로 표기. 다중 모델 검토로 표현하지 않음 |
| 이유 조사 | why | 사실·추정·미확인을 구분하고 설계 이유 조사 | 로컬 Git·과제 문서 기본. MCP·조직 자료 자동 탐색 제외 |
| 인지·설명 | teach | 동작·구조·이유를 사용자가 이해하도록 설명 | 실제 코드·결정 기록·증거로 한국어 설명 |
| 문서·커밋 | technical-writing, unslop | 구체적인 문제·결과·근거·한계 | 한국어 요구 우선. 영어 문체 규칙 강제 제외 |
| 커밋 diff | no-comments의 제한적 검토 기준 | 외부 제약·법적 문구·공개 계약을 보존하며 불필요 설명 검토 | 무조건 주석 삭제·별도 agent 실행을 기본 절차로 넣지 않음 |
| 인계 | poteto-mode의 pause-safely, session-pickup | 현재 상태·증거·미완료·다음 행동을 남기고 실제 상태 재확인 | work/handoff.md와 status. PR·원격 브랜치 의존 제외 |

원본의 상호 호출을 그대로 실행하지 않으므로 위 스킬이 다른 스킬을 요구해도 외부 도구를 연결하지 않는다. 필요한 판단 기준은 공통 절차에 명시되어 있다. 원문을 더 조사할 때 필요한 전이 자료는 vendor에 전부 남아 있다.

## 조건부 자료

| 자료 | 적용 조건 | 기본 동작 |
|---|---|---|
| benchmark-checklist, principle-explain-the-number | 실제 성능·개선 수치를 주장할 때 | 기준·입력·환경·반복·수치를 함께 기록 |
| typescript-best-practices | TypeScript 과제일 때 | 기존 도구·스키마부터 사용 |
| create-formal-verification-skill, maintain-formal-verification-skill, statechart | 일반 실행 검사로 놓칠 고위험 불변식이 있고 시간·도구가 허용될 때 | 속성·가정·검증 범위·버전·반례를 먼저 정함. 자동 도구 설치 없음 |
| principle-separate-before-serializing-shared-state | 여러 작업자가 실제로 있을 때 | 기본 단독 작업에는 적용할 공유 상태가 없음 |
| principle-guard-the-context-window | 맥락 한도가 가까울 때 | 인계 파일을 갱신하고 다음 세션이 실제 상태를 재검증 |

## setup-pstack을 자동 실행하지 않는 이유

setup-pstack은 역할별 모델과 추론 예산을 개인 설정 파일에 기록한다. 커밋 훅, CI, 반복 실행기를 구성하지 않는다.

원본 기본값은 Claude·Grok이며 역할에 따라 서로 다른 모델 계열을 강제한다. 단순히 inherit-parent를 적어도 다른 계열 필수 요구가 전부 없어지지 않는다. 실전은 제공 Codex와 허용 모델만 사용하므로 이 키트는 전역 설정을 작성하거나 모델을 임의로 선택하지 않는다. 제공 환경의 현재 허용 모델을 그대로 사용한다.

## 활성 경로에서 제외한 내용

- 원격 PR·GitHub 상태 감시·CI 재시도·병합·배포·Benny 자동화.
- 원본 poteto-mode 전체 실행, arena·swarm의 강제 위임·외부 모델.
- Playwright·CDP·Computer Use·브라우저 자동조작.
- 외부 메신저·이슈 트래커에 자동 기록.
- 개인 대화·비공개 스킬·전역 모델 설정의 반입.
- make-bot-ui의 webhook·개인 키·터널.
- 과제와 무관한 무조건적 주석 삭제나 대형 구조 변경.

## 라이선스와 검토 범위

원본 MIT 저작권과 허가문을 vendor/pstack/LICENSE에 보존한다. ORIGIN.json의 파일 해시는 배포한 원본이 고정 SHA의 내용과 같은지 확인하는 용도다.

소스감사는 루트 SKILL.md 58개 전부와 도입에 관련된 README·LICENSE·setup·검증·맵 예제·설계·설명·인계·로그 참조를 전문 읽었다. statechart 전체 구현, 모든 성능 도구, 모든 원격 자동화를 실행하거나 전체 코드를 검토했다고 주장하지 않는다. 이 자료는 비활성이고 공통 실행기의 런타임 의존성이 아니다.
