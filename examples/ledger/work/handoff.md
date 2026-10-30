# 인수인계

## 현재 상태

목표는 로컬 JSON 장부와 커밋 전 검증 흐름의 독립 준비 평가다. main 브랜치에서 정상 커밋은 a2b0e2ac30584e681272061e2d929e7d1ac360ca, 회귀 복구 커밋은 853d7043be26d00e392860c278166e830c861017이다. 이 문서 작성 시 그 뒤의 미커밋 변경은 인계 문서뿐이다. 인계 문서 자체도 U003 정상 훅을 거쳐 커밋하며 자기 자신의 SHA는 넣지 않는다. 최종 SHA는 외부 평가 결과와 `git rev-parse HEAD`에서 확인한다.

## 구조와 실행

app/ledger.py는 --file 경로와 deposit/withdraw/balance를 처리한다. 저장 구조는 정수 balance와 ID별 kind/amount 사전이다. 기존 요청의 내용이 다르면 거절하고 같으면 저장 이전에 반환한다. 성공 쓰기는 같은 폴더의 임시 파일을 replace한다. `python3 kit.py doctor`, `python3 kit.py map check`, `python3 kit.py check`, `python3 kit.py status`로 재개한다. 실제 앱 doctor는 check 내부에서 실행된다. 세 기능의 정본은 .agents/skills/verify-app/features/이다.

## 검증과 증거

정상 훅은 `.kit/runs/20261030T174005-cbabc076e9/`에서 세 검사 통과 후 커밋되었다. U002에서 동일 요청 조기 반환을 제거하자 실제 CLI의 100 입금→30 출금→같은 출금이 100→70→40이 됐다. `.kit/runs/20261030T174026-0079768721/`에서 문법은 통과했지만 business/runtime은 실패하고 커밋 종료 1, HEAD는 정상 SHA 그대로였다. 실패 후 검사와 기대값을 바꾸지 않고 원인을 고쳤다. 같은 U002의 2/3번째 시도 `.kit/runs/20261030T174057-7f5eab3b82/`가 통과해 복구 커밋이 생성됐다.

깨진 검사 참조 missing-runtime은 map check 종료 1, 원본 명령으로 복구 후 종료 0이었다. 평가 보조 스크립트의 리스트 별칭 실수로 첫 복구도 깨진 ID를 사용한 사실을 .kit/assessment에 그대로 보존했다. 키트의 결함으로 세지 않는다. 코드 변경 후 status의 STALE 종료 1도 관측했다. 성공/실패 실행 모두 cleanup 종료 0이며 scratch가 없고 report/CLI 로그가 남았다. `.kit/assessment/integrity-and-cleanup.json`에 직접 확인 결과가 있다.

## 한계와 판단

CLI의 순차 입출력과 파일 부수효과만 확인했다. UI·서버·동시 쓰기·전원 장애 복구·성능·모든 입력의 형식 증명은 미확인이다. 부분 staging 차단은 문서/코드로 이해했으며 추가 커밋 실험은 하지 않았다. 키트 공통 코드와 공통 문서는 수정하지 않았다. 시간/횟수 초기화나 --no-verify를 사용하지 않았다.

문서의 시간대 고정 안내를 따라 TZ를 설정했다가 예약 변수 오류를 받았다. 예약 목록은 kit.py를 읽고 파악했으며 앱 설정 env를 비워 복구했다. 정확한 CLI 형식, 오류 코드, 초기 조회, 금액 문자열 표현과 동시성 범위 등 요구사항에 없는 선택은 work/decisions.tsv에 기록했다.

## 다음 행동

`python3 kit.py status`로 현재 파일과 마지막 증거가 일치하는지 확인한다. 새 변경이 있으면 새 단위를 시작하고 앱과 맵 및 검사를 함께 갱신한다. 공개 예제 사본은 별도 export 디렉터리에 app/verification/verify-app/work/README 및 경로를 정리한 주요 증거만 담는다. 과제에 없는 기능 추가나 외부 전송은 요청받기 전 수행하지 않는다.
