# CLI 잔액 장부 독립 E2E 평가

평가 모델은 gpt-6-astra이며 부모의 spawn_agent 호출 지정으로 확인했다. 소스 커밋은 `c1045e32308fd292a01696406973e5912a442a9c`이다. 요구사항과 공개 키트만 읽고 별도 clone과 빈 Git 프로젝트에서 앱·검사·맵을 직접 작성했다. 기존 키트 테스트를 읽거나 실행한 것만으로 앱 검증을 대신하지 않았다.

## 결과

요구한 정상 커밋 → 실제 회귀 → 커밋 차단 → 같은 단위 복구를 완료했다. 최종 상태는 PASS이고 작업트리는 깨끗하다. 원본 작업트리는 변경하지 않았다. 독립 소스 복사본도 해당 SHA와 깨끗한 상태를 유지한다. kit.py와 공통 지침은 수정하지 않았다. 설치기는 AGENTS.md에 BEGIN/END 구획만 자동 추가하므로 원본과의 바이트 비교 대신 구획과 최초 설치 커밋을 비교했다.

| 단계 | 종료 코드 | 실제 SHA/결과 |
|---|---:|---|
| 빈 프로젝트 install | 0 | 초기 doctor는 앱 미설정으로 1 |
| 정상 커밋 | 0 | `a2b0e2ac30584e681272061e2d929e7d1ac360ca` |
| 중복 반영 회귀 커밋 | 1 | 새 커밋 없음, HEAD `a2b0e2ac30584e681272061e2d929e7d1ac360ca` 유지 |
| 같은 U002의 복구 커밋 | 0 | `853d7043be26d00e392860c278166e830c861017` |
| 최종 인계 커밋 | 0 | `eee94facf6b0546ae5ba83775d1e2f85cd896a3b` |
| 깨진 맵 / 복구 | 1 / 0 | missing-runtime 참조 탐지 |
| 코드 변경 뒤 status | 1 | STALE 관측 |
| 최종 status | 0 | PASS |

U001은 25분·3회 중 1회, U002는 25분·3회 중 실패 1회와 복구 2회, U003은 15분·3회 중 1회를 사용했다. 실패 뒤 예산을 초기화하거나 --no-verify를 사용하지 않았다.

## 앱과 독립 기대값

`python3 app/ledger.py --file DATA deposit/withdraw REQUEST_ID AMOUNT`와 balance가 실제 진입점이다. 정상 출력은 JSON balance, 오류는 종료 2와 stderr다. 문법 검사는 AST 파싱, business 검사는 별도 9 입금/중복/충돌/전액 출금/잘못된 입력/손상 JSON 보존, runtime 검사는 요구사항의 100→70→70과 오류 후 70을 고정 기대값으로 사용한다. 런타임 인수 시나리오는 새로운 장부 두 개에서 반복했고 모든 CLI 호출이 새 프로세스였다. 내부 앱 함수를 호출한 단위 검사로 사용자 경로를 대신하지 않았다.

파일의 실제 바이트와 요청 기록, 오류 전후 불변, 임시 파일 잔류도 확인했다. 동일 출금의 조기 반환을 제거한 회귀에서는 별도 직접 실행 결과가 100→70→40→40이었다. 훅의 business는 기대 9에 실제 18, runtime은 기대 100에 실제 200으로 실패했다. 문법은 통과해 비즈니스 오류 탐지가 실제로 작동했음을 구분했다. 복구는 조기 반환을 되살리고 충돌 검사를 분리한 것이다. 검증 기대값은 유지했다.

F001 입금·F002 출금·F003 조회 맵과 앱별 verify-app, 의도·판단·인계를 작성했다. 정해지지 않은 CLI 문법, 오류 코드, 최초 조회, 금액 문자열 규칙, 중복 응답 의미, 순차 실행 범위는 work/decisions.tsv에 판단 근거를 남겼다.

## 증거와 정리

정상 `.kit/runs/20261030T174005-cbabc076e9/`, 실패 `.kit/runs/20261030T174026-0079768721/`, 복구 `.kit/runs/20261030T174057-7f5eab3b82/`, 최종 `.kit/runs/20261030T174144-9744725ba1/`에 report와 실제 로그가 있다. 각 실행의 scratch는 제거되었고 CLI 입출력/파일 내용과 보고서는 남았다. 설정 자체가 거절된 최초 실행은 앱을 시작하기 전이므로 cleanup/CLI 로그가 없고 실패 report만 남았다. 이 구분을 JSON에 기록했다.

깨진 맵을 처음 복구할 때 평가 보조 스크립트의 리스트 별칭 실수로 잘못된 ID가 다시 사용됐다. 키트는 계속 정확히 거절했다. 저장된 원본 명령을 다시 읽어 복구했고 두 실패를 지우지 않았다. 이것은 평가자 실수이며 키트 결함으로 세지 않았다.

예제 export에서 doctor·문법·business·runtime·cleanup을 별도 실행했고 모두 종료 0이었다. export에는 app/, verification/, 생성한 verify-app/, work/, 실행 README와 주요 증거만 있다. vendor·.git·개인 설정·비밀값은 포함하지 않는다. 공개용 증거는 프로젝트/인터프리터 절대 경로만 기호로 치환하고 stdout·잔액·종료 코드·SHA는 유지한다. 원시 증거는 평가 프로젝트 .kit에 보존한다.

## 발견 사항

**LEDGER-DOC-01 — 낮음: 예약 환경변수 안내 누락.** protocol은 시간대 고정을 요구하지만 이미 실행기가 고정한 TZ를 project.json env에 지정하면 검사 전 종료 1이다. 오류에는 충돌 변수 이름이 없다. 앱 env를 비워 진행했으며 키트는 변경하지 않았다. 문서에 기본값/예약 목록을 명시하고 오류에 실제 충돌 이름을 넣는 개선을 제안한다. LC_ALL은 예약 대상이 아니며 최초 설정의 TZ와 PYTHONDONTWRITEBYTECODE가 원인이다. 커밋 게이트의 기능상 차단 실패는 관측하지 않았다.

## 소스에서 이해한 계약

- **scope**: 공통 키트는 앱 구현물이 아니라 의도·기능 맵·검사 명령·증거·로컬 커밋 반복을 제공한다. 과제별 앱과 세 검사는 평가자가 직접 작성한다. vendor/pstack 58개는 비활성 참고 자료다.
- **entrypoint**: 실제 프로젝트에서 소스 kit.py install --project .를 실행한다. 활성 지침은 .agents/skills/fde-workflow/SKILL.md와 .agents/skills/verify-app/SKILL.md 두 개다. 검증 명령은 python3 kit.py check다.
- **read_order**: 과제 안내와 기존 README → RULE.md → AGENTS.md → FDE_GUIDE.md(키트 자체에서는 README) → docs/fde/protocol.md → skills.md와 verification.md. 이후 기존 work/intent.md·handoff.md와 git status/kit.py status, 두 활성 스킬을 확인한다. README의 먼저 읽기 목록과 AGENTS의 FDE_GUIDE 추가가 있으나 두 목록을 합치면 수행 가능했다.
- **map_location**: .agents/skills/verify-app/features/F001.md가 기능별 정본이고 features/README.md가 생성 인덱스다. 이 예제는 F001 입금, F002 출금, F003 조회다.
- **map_update_commands**: python3 kit.py map add --id F001 --title ... --source ... --entry ... --precondition ... --action ... --expected ... --invariant ... --check 실제-runtime-ID; 이어 map sync → map check. 같은 기능은 같은 ID로 갱신하고 본문만 직접 바꾸지 않는다.
- **commit_gate_command**: begin으로 단위와 예산 고정 → 전체 git add -A → diff 검토 → git commit. .githooks/pre-commit이 python3 kit.py iterate --staged를 호출한다. check는 단발 검사이며 커밋을 만들지 않는다.
- **loop_owner**: 에이전트가 목표·작업·실패 원인 분석·수정·재시도를 맡는다. kit.py iterate는 고정 예산에서 검사를 한 번 수행하고 상태를 기록할 뿐 AI 호출·자동 코드 수정·자동 커밋을 하지 않는다.
- **evidence_location**: .kit/runs/<run-id>/report.json, 검사 로그, 앱이 KIT_RUN_DIR에 저장한 입력/출력/파일 부수효과. .kit/latest.json, unit.json, iteration.jsonl이 현재 결과와 시도 이력을 기록한다. .kit은 Git 제외 대상이다.
- **partial_staging**: 부분 stage는 검증 내용과 커밋 내용이 달라지므로 금지되고 staged_guard가 차이를 거절한다. 전체 변경을 stage하고 --no-verify를 쓰지 않는다. 이번 평가는 부분 stage 음성 실험을 추가로 하지 않았다.
- **competition_models**: RULE의 실전은 제공 Codex와 허용 모델만 사용하며 권장 목록은 Sol 6.1/Terra 5.6/Luna 6/Sol 6.0이다. Astra·Claude Code·외부 AI 연결은 실전 제한이다. 이번 gpt-6-astra 평가는 사용자의 명시적 준비 평가 요청으로 별개다.
- **ui_verification**: Computer Use/Playwright/CDP 등 화면 자동조작은 금지이며 UI는 응시자가 내부 Browser에서 직접 확인한다. API 성공을 UI 성공으로 적지 않는다. 장부는 UI 없는 CLI여서 화면 확인은 해당하지 않는다.
- **handoff**: work/handoff.md에 목표·현재 브랜치/기존 SHA·변경·구조·명령·실제 검증과 증거·미확인 범위·다음 정확한 행동을 남긴다. 최종 인계도 정상 훅으로 커밋하고 자기 자신의 최종 SHA를 같은 파일에 넣지 않는다. 다음 세션은 실제 Git/검증 상태를 다시 확인한다.

## 현실적 누락과 재개

부분 staging 차단의 별도 음성 커밋 실험, 동시 쓰기, 전원 장애 복구, 부하 성능, 형식 증명은 하지 않았다. CLI 시나리오에 UI·서버는 없어 해당 검증을 했다고 주장하지 않는다. 외부 AI 호출·전송·push·화면 자동조작을 수행하지 않았다. 시작 시 public 키트를 로컬 clone한 것과 사용자가 명시 요청한 Astra 준비 평가를 실전 허가로 전이하지 않았다.

다음 행동은 프로젝트에서 `python3 kit.py status`로 현재성 확인이다. 새 변경이 없다면 추가 복구 작업은 없다. 앱에 의도적 회귀는 남아 있지 않다. 최종 SHA는 `eee94facf6b0546ae5ba83775d1e2f85cd896a3b`이다.
