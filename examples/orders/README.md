# CSV 주문 집계 합성 예제
Python 3.9 이상, POSIX, Git만 사용한다. 프로젝트 루트에서 `python3 app/orders.py input.csv output.json`으로 실행한다. 입력은 UTF-8 CSV의 order_id,amount,status 3개 컬럼이다. amount는 음수 아닌 정수이며 status는 confirmed 또는 cancelled다.

정상 예: a,100,confirmed를 두 번, b,40,cancelled 한 번, c,25,confirmed 한 번 쓰면 출력은 `{"confirmed_count":2,"total_amount":125}` 뒤 LF다. 같은 주문은 한 번 집계하고 충돌·잘못된 행은 기존 출력을 보존한다.

키트를 설치한 프로젝트에서는 `python3 kit.py doctor`, `python3 kit.py map check`, `python3 kit.py check` 순서로 실행한다. 독립 실행은 `mkdir -p /private/tmp/csv-example-run`, `KIT_RUN_DIR=/private/tmp/csv-example-run PYTHONDONTWRITEBYTECODE=1 python3 verification/business.py`, `KIT_RUN_DIR=/private/tmp/csv-example-run python3 verification/runtime.py`, `KIT_RUN_DIR=/private/tmp/csv-example-run python3 verification/cleanup.py` 순서다. 같은 실행 폴더를 재사용하지 말고 새 폴더로 바꾼다. 정적 검사는 `python3 verification/static.py`다.

정책·한계는 work/decisions.tsv, 실제 인계는 work/handoff.md, 기능별 실행 경로는 .agents/skills/verify-app/features/를 확인한다. 보존한 evidence는 합성 데이터만 포함한다. 전체 vendor나 개인 환경, .git은 예제 내보내기에 포함하지 않는다.

## 공개 키트에 다시 설치하기

이 내보내기에는 공통 kit.py나 vendor를 포함하지 않는다. 새 빈 Git 프로젝트에서 공개 키트의 c1045e32308fd292a01696406973e5912a442a9c로 `python3 /키트/kit.py install --project .`를 실행한 뒤 이 예제의 app/, verification/, work/, .agents/skills/verify-app/을 복사한다. 앱별 초기 템플릿은 이 예제 파일로 교체한다. `python3 kit.py map sync`, `python3 kit.py map check`, `python3 kit.py check`로 재검증한다. 예제 단독 실행은 위의 KIT_RUN_DIR 명령을 따른다. 보존한 .kit/runs는 원래 독립 평가의 증거이며 새 실행의 PASS를 대신하지 않는다.

## 이 저장소에서 재실행

공개 키트 원본의 루트에서 python3 scripts/replay_examples.py orders를 실행하면 빈 Git 프로젝트에 현재 키트를 설치하고 실제 커밋 훅으로 다시 검증한다. evidence/는 준비 단계의 보존 기록이며 현재 프로젝트의 검증 상태로 사용하지 않는다. 원래 .kit/ 경로로 기록된 CSV 증거는 이 내보내기의 evidence/ 아래에 보존했다.
