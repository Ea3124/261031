# 인계

목표는 초기 재고2의 실제 HTTP 예약·취소 서비스와 키트 커밋 검증의 정상/실패/복구를 확인하는 것이었다. 의도 변경은 없고 화면은 만들거나 확인하지 않았다.

현재 브랜치는 main이다. 최초 정상 SHA는 c1c7967e162bd222f501ceadbf542f7177f7dd63이며 회귀 차단 때도 HEAD가 같았다. 회귀 복구 SHA는 46596ff5473464ae3f8a9d34e36e4c6e86c91563다. 이 인계 문서 자체는 후속 정상 훅 커밋으로 기록한다. 최종 SHA는 외부 평가 result.json과 .kit/evaluation/final-sha.log에서 확인한다. 자기 최종 SHA를 자기 커밋 파일에 기록하는 순환은 만들지 않는다.

구현은 app/server.py의 Inventory(재고 정수, 요청 ID별 수량·취소 표식, 잠금)와 표준 라이브러리 HTTP 서버다. 영속 저장은 없고 새 서버마다 재고2다. GET /health, GET /inventory, POST /reservations, POST /reservations/{id}/cancel이 진입점이다. 독립 검사와 명령은 verification, 기능 정본은 .agents/skills/verify-app/features/F001.md~F003.md에 있다.

검증 명령은 `python3 kit.py check`다. 회귀는 취소 표식 가드를 제거한 실제 결함이며, 20261030T174037-71627276dc에서 비즈니스 검사와 HTTP 검사가 모두 실패했다. HTTP 두 번째 취소의 재고는 기대1 대신2였고, 독립 원장 검사에서는 기대2 대신3을 관측했다. 훅은 커밋을 차단했고 실패 SHA는 생성되지 않았다. 검사 기대값을 바꾸지 않고 가드를 복구하여 U002의 시도2/4에서 20261030T174038-b63d54c8e5 PASS를 얻었다. 시간·횟수 초기화는 하지 않았다.

F003을 does-not-exist 검사에 연결한 뒤 map check 및 전체 check가 종료코드1로 실패했다. 정상 reservation-http 참조와 인덱스를 복구했다. 앱 변경 뒤 status의 STALE/종료코드1을 관측하고 재검증 뒤 PASS/0을 확인했다. 각 서버는 0.0.0.0의 실제 출력 포트를 사용했고 harness finally가 자기 프로세스만 종료했다. 실패 실행에서도 server-cleanup.json은 alive=false, port_closed=true, trace_exists=true다.

증거는 .kit/runs의 각 report.json·http-trace.json·server-start.json·server-cleanup.json과 .kit/evaluation의 명령별 로그·commands.jsonl·regression-summary.json에 보존된다. 초기 제한 샌드박스에서는 bind가 PermissionError로 실패했다. 승인된 로컬 HTTP 실행 범위에서 통과했으며 실행기나 공통 문서는 바꾸지 않았다.

화면, 부하 성능, 영속 복구, 악의적 HTTP 입력 전수 검사, 형식 증명은 확인하지 않았다. 다중 동시 요청 경쟁을 별도로 시험하지 않았다. 요청 ID에 URL 경로 구분자가 들어가는 경우는 지원 계약이 명시되지 않은 한계이며 합성 ID r1/r2 등만 인수 경로로 확인했다. 실전 응시 모델과 후속 서술형 지원 종료 규칙은 RULE을 따른다.

다음 재개 행동은 `git status --short`와 `python3 kit.py status`를 확인하고, 변경이 있거나 새 환경이면 `python3 kit.py check`를 실행하는 것이다. 네트워크 설치·외부 AI·push·전송·화면 자동조작은 필요 없다.
