# CSV 주문 집계 인계
목표는 확정 주문을 ID별 한 번 집계하고 잘못된 CSV에서 기존 결과 파일을 보존하는 것이다. 의도 변경은 없었다. 현재 브랜치는 main이며 이 문서 작성 직전 복구 커밋은 2a77037bca44e6ceaf4549724d34d5ba84eeef45다. 이 문서와 판단 기록을 마지막 정상 훅 커밋에 포함하며, 그 최종 SHA는 외부 평가 보고서와 `git rev-parse HEAD`로 확인한다.

앱은 app/orders.py의 aggregate에서 ID→(정수 금액, 상태)를 검증·중복 제거한 뒤 최소 JSON 바이트를 만든다. main은 전체 입력 성공 후 같은 출력 디렉터리의 임시 파일을 os.replace로 교체한다. 실패하면 기존 출력이 유지되고 자신이 만든 임시 파일을 지운다. 표준 라이브러리만 사용하며 외부 서비스나 서버가 없다.

실행은 `python3 app/orders.py input.csv output.json`, 준비는 `python3 kit.py doctor`, 검증은 `python3 kit.py check`다. Python 문법 검사, 독립된 업무 기대값 8개, 실제 CLI 정상/재실행/오류 10종/출력 없는 실패가 통과했다. 요구사항의 2건·125 기대값을 앱으로 계산하지 않고 검사에 직접 고정했다.

정상 커밋 10f7b25d7bfe71f94260d5af674b51d7e08c35ee 후 중복 분기 continue를 pass로 바꿨다. CSV002 시도 1에서 업무 검사와 실제 CLI가 3건·225를 관측해 커밋이 차단됐고 HEAD는 그대로였다. 같은 단위 시도 2에서 continue 복구 후 성공했다. 실패 코드 자체는 최종 앱에 남지 않았다.

핵심 증거는 .kit/runs/20261030T173948-16798e8380(정상), 20261030T174004-e393dba558(회귀 실패), 20261030T174014-d3a9126d23(복구), 20261030T174034-161d96e7d3(맵 실패), 20261030T174035-44d1700d26(맵 복구)다. 각 실행의 report.json, business.json, csv-evidence/observed.json, 입력·전후 출력, cleanup.json을 읽는다. 전체 명령 종료 코드는 .kit/e2e/commands.json에 보존한다. .kit/iteration.jsonl은 같은 단위의 시도 1 실패→2 성공을 보여준다.

STALE은 앱 수정과 기능 맵 손상 각각에서 탐지했다. map add는 누락 소스 자체를 거절했으므로, 독립 실패 재현을 위해 맵 메타데이터·본문을 일관되게 손상시킨 뒤 map check와 check 실패를 관측하고 정식 map add/sync로 복구했다. 성공·업무 실패 모두 scratch가 정리되고 증거 파일이 남았다. 맵 사전 실패는 앱을 실행하지 않아서 cleanup도 호출하지 않으며 빈 report.checks를 남긴다.

UI는 없고 화면 자동조작은 하지 않았다. 대규모 성능, 동시 쓰기, 전원 장애의 디렉터리 내구성, 권한 경합, 모든 CSV 방언·빈 줄 정책, 모든 환경의 Python 버전은 검증하지 않았다. 단위 테스트는 형식 증명이 아니다. 다음 행동은 `git status --short`와 `python3 kit.py status`를 확인하고 STALE이면 `python3 kit.py check`를 실행하는 것이다.
