---
name: verify-app
description: 로컬 JSON 장부의 실제 CLI, 요청 중복과 오류 입력, 파일 부수효과를 검사하고 증거를 보존한다.
---

# 장부 앱 검증

## 실행

프로젝트 루트와 Python 3.9 이상이 필요하다. 서버·포트·설치 의존성은 없다. `python3 kit.py check`는 새 `.kit/runs/<run-id>/scratch/` 아래 독립 장부를 만든다. 개별 조작은 `python3 app/ledger.py --file /tmp/자신이만든폴더/ledger.json deposit r1 100`이며 해당 폴더는 먼저 만든다. 성공 stdout은 `{"balance": 100}`, 종료 코드는 0이다.

## 준비 확인

`python3 kit.py doctor`는 키트와 설정의 구조를 확인한다. `python3 kit.py check` 안에서 등록된 doctor가 별도 CLI 프로세스로 빈 장부 balance=0, 파일 생성 없음을 확인한다. 버전·결과는 실행 폴더 environment.txt에 남긴다. 검사 스크립트를 직접 실행할 때에는 비어 있는 자신의 증거 폴더를 `KIT_RUN_DIR`로 제공해야 한다.

## 조작

`python3 kit.py check`는 문법 검사를 수행하고, business-invariants에서 별도 9 입금→중복→충돌→전액 9 출금→0을 확인한다. ledger-runtime은 `deposit r1 100`, `withdraw r2 30`, 동일 출금 반복, `withdraw r2 20`, `withdraw r3 71`, `balance`, 잘못된 금액을 새로운 디렉터리 두 개에서 각각 실행한다. 기대 잔액은 100→70→70, 오류 시 70 그대로다. 모든 호출은 새 프로세스다. 실패 코드 2, stderr, 표준출력 없음, 파일 바이트 불변도 검사한다. F001/F002/F003 맵은 모두 ledger-runtime과 연결한다. UI는 없는 CLI 앱이다.

## 증거

`.kit/runs/<run-id>/report.json`과 검사 로그, `cli-transcript.jsonl`의 실제 인자·종료 코드·stdout/stderr·이전/이후 파일, `acceptance-final-0.json` 및 `acceptance-final-1.json`, business/runtime-result.json을 읽는다. `python3 kit.py status`로 내용 지문의 현재성을 확인한다. 성공 기준은 세 검사 통과, 저장된 두 요청과 잔액 70, 실패 입력의 파일 보존이다. 내용이 바뀌어 STALE이면 다시 검사한다.

## 정리

공통 실행기가 성공과 실패 모두 `python3 verification/cleanup.py`를 호출한다. 이 명령은 그 실행의 KIT_RUN_DIR/scratch만 지우고 증거 파일은 남긴다. `cleanup-result.json`에서 scratch_removed=true와 preserved 목록을 확인한다. 앱/검사 subprocess는 동기 종료하며 서버가 없다. 자체 실행한 임시 폴더 외의 상태는 정리하지 않는다.

## 맵 갱신

정본은 features/F001.md부터 시작한다. 같은 ID에 `python3 kit.py map add`로 소스·행동·기대값·불변식·runtime 검사 연결을 갱신한 후 `python3 kit.py map sync`, `python3 kit.py map check`를 실행한다. 맵의 의미는 실제 CLI 실행과 소스를 대조한다.
