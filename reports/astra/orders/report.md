# CSV 주문 집계 독립 E2E 평가

실제 모델은 gpt-6-astra(high)이며 부모 에이전트의 spawn 설정으로 확인했다. 소스 c1045e32308fd292a01696406973e5912a442a9c를 `git clone --no-hardlinks`로 독립 복사하고 빈 Git 프로젝트에 실제 install했다. 원본 작업트리·공통 실행기·공통 문서를 수정하지 않았다. 기존 대화와 의도된 답 없이 소스 안내에서 절차를 이해했다. 최초 파일명 탐색 범위를 /private/tmp 전체로 잘못 잡아 다른 평가 폴더 이름이 출력됐으나 해당 파일 내용은 읽지 않았다.

## 실제 결과

- 정상 커밋: `10f7b25d7bfe71f94260d5af674b51d7e08c35ee`. 훅 종료 0, 정적·업무·실제 CLI 검사 모두 PASS.
- 회귀: 중복 분기의 continue를 pass로 바꾸자 실제 CLI는 3건·225를 출력했다. 독립 기대값은 2건·125여서 업무와 runtime 검사가 동시에 실패했다. git commit 종료 1, 새 실패 커밋 없음, HEAD `10f7b25d7bfe71f94260d5af674b51d7e08c35ee`로 유지.
- 복구: 동일 CSV002 작업 단위 시도 2/3에서 continue를 복구했다. 검사를 삭제·완화하지 않았고 제한을 초기화하지 않았다. 정상 훅 종료 0, 복구 SHA `2a77037bca44e6ceaf4549724d34d5ba84eeef45`.
- 최종 인계 커밋: `fb7018a19e46baf59603369f889a887b62038ead`. status PASS, git status --short 빈 출력.
- 정상 출력은 UTF-8 `{"confirmed_count":2,"total_amount":125}`와 마지막 LF. 새 프로세스 반복 실행에서 동일 바이트를 확인했다.
- 금액·상태 충돌, 음수, 비수치, 미지 상태, 필수 컬럼 누락, 여분/누락 필드, 빈 ID, 깨진 따옴표 모두 실패하며 기존 출력 바이트를 보존했다. 출력 없는 오류도 부분 출력과 임시 파일이 없었다.
- 기능 맵 3개는 가져오기·중복 처리·결과 저장으로 작성하고 runtime 검사에 연결했다. map add는 없는 소스 자체를 거절했다. 저장 맵을 직접 손상한 독립 실험에서 map check와 check는 종료 1, status는 STALE을 보였다. 정식 map add/sync 후 복구했다.
- 앱 변경 때도 status가 STALE을 보였다. 부분 stage에서 check --staged는 종료 1이었고 전체 stage 후 훅 커밋은 성공했다.
- 정상·업무 실패·복구 실행 모두 자체 scratch 제거와 모든 evidence_files의 실제 존재를 확인했다. 실패 증거를 다음 실행이 덮어쓰지 않았다.

## 소스로 이해한 절차

- **scope**: 문제 정의·구현·앱별 검증·기능 맵·로컬 커밋 훅·실패 수정·인계를 통일하는 준비용 키트다. 앱은 제공하지 않으며 원격 CI·자동 AI 수정·보안 샌드박스가 아니다.
- **entrypoint**: .agents/skills/fde-workflow/SKILL.md가 공통 진입점, .agents/skills/verify-app/SKILL.md가 앱 실행·검증 진입점이다. vendor/pstack은 비활성 참고 자료다.
- **read_order**: 실제 과제 안내/기존 README → RULE.md → AGENTS.md → FDE_GUIDE.md(없으면 키트 README) → docs/fde/protocol.md → 기존 work/intent.md·handoff.md 및 실제 Git/status. README는 추가로 docs/fde/skills.md와 verification.md를 안내한다.
- **map_location**: .agents/skills/verify-app/features/F001.md 형태가 정본이고 map sync가 기능 인덱스를 만든다.
- **map_update_commands**: python3 kit.py map add --id Fxxx ... → python3 kit.py map sync → python3 kit.py map check. 변경은 같은 ID, 삭제는 해당 파일 제거 후 sync이며 의미 일치는 소스·실제 실행으로 별도 확인한다.
- **commit_gate_command**: python3 kit.py begin --unit ... --goal ... --minutes ... --max-attempts ... 후 git add -A, diff 확인, git commit. 설치된 pre-commit이 python3 kit.py iterate --staged를 호출한다.
- **loop_owner**: 코드 수정·가설 변경·다음 커밋 시도는 에이전트가 수행한다. iterate는 제한된 한 차례 검사와 상태 저장만 하며 AI 호출·자동 수정·자동 커밋·데몬이 없다.
- **evidence_location**: .kit/runs/<run-id>/report.json과 명령 로그. 앱 검사는 KIT_RUN_DIR에 입력·출력·부수효과를 남긴다. .kit/latest.json, iteration.jsonl, unit.json이 최신 결과와 반복 이력을 보조한다.
- **partial_staging**: 부분 stage를 금지한다. 추적 파일 unstaged 변경 또는 미추적 작업 파일이 있으면 --staged 검사/커밋을 막는다. --no-verify로 우회하지 않는다.
- **competition_models**: 실전은 제공 Codex와 허용 모델만 사용한다. RULE의 권장 모델은 Sol 6.1, Terra 5.6, Luna 6, Sol 6.0이며 Astra·외부 모델 연결은 제한된다. 이번 Astra는 소유자가 명시한 준비평가 예외이며 실전 허가로 전이되지 않는다.
- **ui_verification**: Computer Use·Playwright/CDP·자동 화면 조작은 금지다. 화면은 응시자가 플랫폼 내부 Browser에서 직접 확인하며 API/CLI 통과를 화면 확인으로 표기하지 않는다. 이번 앱은 UI 없는 CLI다.
- **handoff**: work/handoff.md에 목표·브랜치·직전 SHA·변경·구조·검증 명령과 결과·증거·한계·다음 행동을 남긴다. 마지막 인계 문서도 정상 훅으로 커밋하고 최종 SHA는 응답/외부 보고서에 둔다. 다음 세션은 Git/status를 재확인하고 STALE이면 재검증한다.

## 발견과 제안

### CSV-KIT-01 — cleanup 호출 범위의 문서와 실행 차이

재현: F001의 metadata와 본문 소스를 존재하지 않는 app/nonexistent.py로 바꾼 뒤 map sync, map check, kit.py check 실행. map check와 check 모두 종료 1. .kit/runs/20261030T174034-161d96e7d3/report.json의 checks는 []이며 cleanup.json도 없다.

영향: protocol 1절과 앱 스킬 템플릿은 성공·실패 모두 cleanup을 호출한다고 읽히지만 맵·stage 등 사전 검사 실패에는 호출하지 않는다. 이번에는 앱을 시작하지 않아 앱 임시 데이터 누수는 없었다. 공통 run 폴더와 빈 tmp는 증거와 함께 남는다. 모든 실패에서 앱 cleanup이 실행됐다고 보고하면 사실과 다르다.

제안: 사전조건 검사 실패에는 앱 실행·cleanup을 생략하고 그 이유를 report에 명시한다고 문서를 좁히거나, 안전한 구성·환경 준비 후의 실패에서만 cleanup을 보장하는 계약을 분명히 한다. 이 평가는 kit.py/공통 문서를 수정하지 않았다.

### CSV-SPEC-01 — 시나리오의 비지정 인터페이스·입력 정책을 앱별 결정으로 고정

재현: orders.md는 JSON 파일과 건수/합계만 요구하며 CLI 인수 이름·JSON 키·직렬화·빈 ID·여분 컬럼·숫자 표기·같은 입력/출력 경로의 정책을 정하지 않는다.

영향: 새 에이전트가 기능을 완성하려면 합리적 정책을 선택해야 한다. 앱·검사·맵의 계약 일치로 처리했고 work/decisions.tsv D001–D005에 이유를 기록했다. 합계 125 등 고정 인수 조건은 변경하지 않았다.

제안: 공통 키트 결함은 아니다. 여러 독립 구현의 바이트나 인터페이스를 동일하게 비교하려면 시나리오에 출력 스키마·CLI 계약과 경계 정책을 추가한다.


## 보존한 자료와 현실적 한계

세 종류 검사는 verification/static.py, business.py, runtime.py다. runtime의 기대 JSON 바이트와 업무 기대 125는 시나리오에서 직접 고정했으며 앱의 집계 함수로 기대값을 계산하지 않았다. 앱별 verify-app의 실행·준비·조작·증거·정리를 실제 명령으로 작성하고 실행했다. 의도·판단·인계도 독립 작성했다.

실험별 명령 argv/종료 코드는 `.kit/e2e/commands.json`, 출력은 같은 디렉터리의 stdout/stderr, 정상·실패·복구의 실제 입력/출력은 `.kit/runs/<run-id>/csv-evidence/`, 정리·파일존재 검사는 `.kit/e2e/evidence-audit.json`에 있다. 이 보고서와 JSON도 `.kit/e2e/`에 복사했다. 구조화된 observed에는 모든 핵심 실행의 실제 종료 코드, SHA, 결과 바이트와 정리 결과를 넣었다.

정상 앱과 앱별 검사·3개 맵·work 문서·실행 README·핵심 증거만 `/private/tmp/fde-e2e-csv-export`에 내보냈다. vendor 전체·.git·개인 환경·비밀값은 포함하지 않았다. 의도적 실패 코드는 최종 앱에 남지 않으며 실패 입력/출력과 diff는 증거로만 보존했다.

화면은 없는 CLI 과제이며 외부 AI 명령·전송·push·UI 자동조작은 실행하지 않았다. 형식 증명, 대규모 성능, 동시 파일 쓰기, 전원 장애 내구성, 모든 CSV 방언과 모든 Python 버전은 확인하지 않았다. 맵 사전 실패에는 앱을 시작하지 않고 cleanup도 생략된다는 예외를 발견 사항으로 남겼다. 최초 clone/install/읽기와 앱 생성 명령은 세션 도구 로그에 있고, `.kit/e2e/commands.json`의 연속 수집은 정상 커밋 준비부터 시작했다.

내보낸 예제에서도 doctor/static/business/runtime/cleanup을 별도로 실행해 모두 종료 0을 확인했다. .kit/e2e/export-validation.json에 결과가 있으며 출력 2건·125, scratch 정리, 실제 증거 보존을 다시 확인했다.
