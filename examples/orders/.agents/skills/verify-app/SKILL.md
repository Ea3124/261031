---
name: verify-app
description: CSV 주문 CLI의 독립 기대값과 실패 시 출력 보존을 실제 프로세스로 검증한다.
---
# 실행
프로젝트 루트에서 `python3 app/orders.py 입력.csv 결과.json`을 실행한다. UTF-8 CSV 헤더는 order_id,amount,status이고 출력 부모 디렉터리는 존재해야 한다. 서버·포트·화면이 없다.

# 준비 확인
`python3 kit.py doctor`로 Python 3.9 이상과 실제 CLI --help를 확인한다. `python3 app/orders.py --help`는 input, output을 표시한다. 검사는 매번 KIT_RUN_DIR/csv-scratch에 새 입력을 만들며 이전 결과를 사용하지 않는다.

# 조작
`python3 kit.py check`가 static, business, orders-cli를 순차 실행한다. orders-cli는 a=100 confirmed 두 행, b=40 cancelled, c=25 confirmed를 새 프로세스로 읽고 정확히 `{"confirmed_count":2,"total_amount":125}`+LF 바이트를 기대한다. 같은 입력을 다시 실행하고 바이트 일치를 확인한다. 충돌 금액·충돌 상태·음수·문자 금액·미지 상태·필수 컬럼 누락·여분 필드·필드 누락·빈 ID·깨진 따옴표는 실패해야 하고 기존 파일을 보존한다. 출력 없는 오류에는 부분 파일도 없어야 한다.

# 증거
`.kit/runs/<run-id>/report.json`, business.json, csv-evidence/의 입력 CSV·전후 JSON·stdout·stderr·observed.json을 읽는다. cleanup.json의 증거 목록과 실제 파일 존재를 비교한다. `python3 kit.py status`는 현재 소스와 같은 증거만 PASS로 표시해야 한다. 기능 맵 정본은 features/F001.md부터이며 `python3 kit.py map sync`와 `python3 kit.py map check`로 갱신한다.

# 정리
공통 check가 `python3 verification/cleanup.py`를 호출한다. 이 명령은 현재 KIT_RUN_DIR/csv-scratch만 제거하고 csv-evidence/와 로그는 보존한다. 수동 실행할 때도 KIT_RUN_DIR은 자기 실행 폴더로 명시한다. `test ! -d .kit/runs/<run-id>/csv-scratch`와 `test -f .kit/runs/<run-id>/csv-evidence/normal.after.json`으로 정리와 증거 보존을 확인한다.
