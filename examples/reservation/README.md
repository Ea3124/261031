# HTTP 재고 예약 합성 예제

Python 3.9 이상 표준 라이브러리만 사용한다. 네트워크 설치는 없다. 최종 앱은 정상 취소 가드가 복구된 상태다.

## 키트 없이 재현

이 디렉터리에서 실행한다.

```sh
python3 verification/static.py
python3 verification/business.py
KIT_RUN_DIR="$PWD/.kit/manual-http" python3 verification/runtime.py
KIT_RUN_DIR="$PWD/.kit/manual-http" python3 verification/cleanup.py
```

runtime이 임시 상태와 서버를 만들고 실제 출력 포트에서 HTTP 흐름을 검사한 뒤 자기 서버만 종료한다. 결과는 .kit/manual-http에 남는다. 0.0.0.0 bind가 허용된 로컬 환경이 필요하다. 화면 자동조작이나 외부 HTTP 요청은 없다.

앱만 수동 실행하려면 `python3 app/server.py --port 0`이다. 첫 줄 JSON의 실제 port를 읽는다. GET /health와 /inventory, POST /reservations의 {"request_id":"r1","quantity":1}, POST /reservations/r1/cancel의 {}를 지원한다. 초기 재고는2이며 성공200, 잘못된 입력400, 미존재404, 충돌/초과409다. 종료는 그 터미널에서 Ctrl+C로 한다.

## 키트 커밋 검증 재현

새 빈 디렉터리에서 git init을 하고, 원본 키트 커밋 c1045e32308fd292a01696406973e5912a442a9c의 kit.py install --project .를 먼저 실행한다. 그 다음 이 예제의 app/, verification/, work/, .agents/skills/verify-app/을 같은 경로에 복사하여 설치된 앱 템플릿을 채운다. kit.py와 공통 문서/vendor는 이 내보내기에 포함하지 않는다.

```sh
python3 kit.py map sync
python3 kit.py map check
python3 kit.py check
python3 kit.py begin --unit EX001 --goal "HTTP 예약 정상 기준" --minutes 10 --max-attempts 3
git add -A
git diff --cached
git commit -m "HTTP 예약 정상 기준"
```

새 EX002 단위를 시작한 뒤 app/server.py의 `if not reservation["cancelled"]:` 한 줄을 `if True:`로 바꾸고 전체 stage/commit하면 business와 HTTP 검사 실패로 차단된다. HEAD가 그대로인지 확인한 뒤 같은 단위에서 해당 한 줄을 원복하고 판단 기록을 남겨 전체 stage/commit한다. 기대값을 바꾸거나 --no-verify를 쓰지 않는다. 이 설명만으로 회귀가 자동 도입되지는 않는다.

## 보존 증거와 한계

evidence/runs에는 실제 정상·회귀 실패·복구·최종 인계 보고서와 요청·서버 종료 증거를 보존했다. evidence/evaluation에는 명령 원장·diff·SHA·맵 오류·STALE·최종 프로세스 감사가 있다. 절대 경로는 평가 당시 합성 임시 프로젝트 위치를 나타내며 명령 실행에 하드코딩되어 있지 않다. work/handoff.md는 원래 평가 프로젝트의 상태를 설명한다.

영속 저장, 인증, UI, 부하 성능, 임의 URL 구분자 ID, 전수 동시성 검증은 포함하지 않는다. 실제 화면 확인을 했다고 주장하지 않는다. 전체 vendor, .git, 개인 설정, 비밀값은 포함하지 않았다.

## 이 저장소에서 재실행

공개 키트 원본의 루트에서 python3 scripts/replay_examples.py reservation를 실행하면 빈 Git 프로젝트에 현재 키트를 설치하고 실제 커밋 훅으로 다시 검증한다. evidence/는 준비 단계의 보존 기록이며 현재 프로젝트의 검증 상태로 사용하지 않는다. 원래 .kit/ 경로로 기록된 CSV 증거는 이 내보내기의 evidence/ 아래에 보존했다.
