---
name: verify-app
description: 합성 HTTP 재고 예약 서비스의 독립 상태·실제 요청·서버 정리를 검증한다.
---

# HTTP 재고 예약 검증

## 실행
프로젝트 루트에서 `python3 kit.py check`를 실행한다. 구성은 verification/project.json이다. 개별 재현은 `KIT_RUN_DIR="$PWD/.kit/manual-http" python3 verification/runtime.py`다. harness는 임시 상태 디렉터리에서 `python3 -B app/server.py --port 0`의 절대 경로를 실행한다. 새 프로세스의 초기 재고는 2이고 바인딩은 0.0.0.0이다. 사람이 수동 실행할 때는 루트에서 `python3 app/server.py --port 0`를 실행하고 첫 JSON 줄의 실제 port를 읽는다.

## 준비 확인
`python3 verification/doctor.py`로 Python 3.9+, 임시 파일 쓰기, 0.0.0.0 소켓 바인딩을 확인한다. runtime.py는 서버 첫 출력에서 서비스명·버전·바인딩·실제 포트를 확인하고 해당 포트의 GET /health 응답이 ready=true인지 검사한다. GET /inventory는 stock=2여야 한다.

## 조작
`python3 kit.py check`는 Python 구문, 1,296개 원장 시퀀스의 5,184개 전이, 실제 HTTP 인수 흐름을 실행한다. runtime.py의 POST /reservations 요청 r1/1 → r1/1 반복 → r1/2 충돌 → r2/1 → r3/1 초과 후 r1 취소를 두 번 보낸다. 기대 재고는 각각 1,1,1,0,0,1,1이다. 잘못된 JSON·값·없는 예약도 보낸 뒤 조회하여 재고1을 확인한다. 마지막 r2 취소 두 번의 재고는2다. 기능별 정본은 features/F001.md~F003.md이다. 화면은 없으며 HTTP 성공을 UI 확인으로 표시하지 않는다.

## 증거
`.kit/runs/<run_id>/report.json`에 검사별 종료 코드가 있다. 같은 폴더의 http-trace.json은 입력·상태코드·JSON 결과, server-start.json은 실제 port·host·PID, server.stderr.log는 요청 로그, server-cleanup.json은 종료 코드·포트 폐쇄·증거 존재를 기록한다. `python3 kit.py status`로 현재 파일과 검증 지문을 비교한다.

## 정리
runtime.py의 finally는 자신이 생성한 Popen 프로세스만 terminate/wait하고 필요시 kill/wait한다. 소켓으로 실제 포트 폐쇄도 확인한다. 임시 디렉터리만 삭제하고 KIT_RUN_DIR 증거는 보존한다. cleanup.py는 종료 증거와 HTTP 기록을 확인한다. 실패한 실행도 같은 finally와 정리를 거친다. 독립 실행 후 `cat .kit/manual-http/server-cleanup.json`으로 alive=false, port_closed=true를 확인한다.
