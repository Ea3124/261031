# 합성 CLI 잔액 장부

Python 3.9 이상과 표준 라이브러리만 사용한다. 네트워크·서버·화면 조작이 없다. 저장 파일의 부모 디렉터리는 호출자가 먼저 만든다. 명령은 프로젝트 루트에서 실행한다.

```sh
mkdir -p /tmp/my-ledger-demo
python3 app/ledger.py --file /tmp/my-ledger-demo/ledger.json deposit r1 100
python3 app/ledger.py --file /tmp/my-ledger-demo/ledger.json withdraw r2 30
python3 app/ledger.py --file /tmp/my-ledger-demo/ledger.json withdraw r2 30
python3 app/ledger.py --file /tmp/my-ledger-demo/ledger.json balance
```

새 파일의 결과는 100, 70, 70, 70이다. 동일 폴더에서 이 전체 명령을 다시 실행해도 마지막 잔액은 70이다. 동일 ID는 종류·금액이 같아야 하고 잔액을 두 번 변경하지 않는다. 성공은 종료 0과 JSON balance, 오류는 종료 2와 stderr다. `withdraw r2 20`, `withdraw r3 71`, 0·음수·문자 금액은 거절하고 파일을 보존한다. 빈 파일 경로의 balance는 0이고 파일을 생성하지 않는다. 동시에 여러 쓰기 프로세스를 실행하는 기능은 범위 밖이다.

## 키트가 설치된 프로젝트

```sh
python3 kit.py doctor
python3 kit.py map check
python3 kit.py check
python3 kit.py status
```

doctor 명령은 키트/설정의 구조 점검이다. 실제 앱 doctor와 문법·비즈니스·사용자 경로 검사는 check에서 실행된다. KIT_RUN_DIR은 실행기가 제공한다. 각 check는 새 데이터로 고정 인수 시나리오를 두 번 실행한다. 실패 경로에서도 자기 scratch만 지우고 입력·출력·파일 전후 내용과 보고서를 `.kit/runs/`에 보존한다.

커밋은 `python3 kit.py begin --unit 고유ID --goal '관찰 가능한 목표' --minutes 10 --max-attempts 3` 후 전체 `git add -A`, diff 확인, `git commit`으로 진행한다. 실패 시 같은 단위에서 수정하고 다시 시도한다. `--no-verify`와 예산 초기화는 사용하지 않는다.

## 키트 없는 예제 사본에서 재실행

app/와 verification/만으로도 실제 CLI 검사를 재현할 수 있다. 비어 있는 새 증거 폴더를 만들고 아래 명령을 순서대로 실행한다. 실패해도 cleanup을 실행한다. 이 경로는 CLI 자체 검사이며 키트 커밋 훅 검증을 대신하지 않는다.

```sh
export KIT_RUN_DIR="$(mktemp -d /tmp/ledger-proof.XXXXXX)"
python3 verification/doctor.py
python3 verification/syntax.py
python3 verification/invariants.py
python3 verification/drive.py
python3 verification/cleanup.py
```

커밋 훅까지 재현하려면 공개 키트 c1045e32308fd292a01696406973e5912a442a9c를 별도 경로에 준비하고 빈 Git 프로젝트에 해당 kit.py install을 먼저 실행한 후 예제의 app/, verification/, .agents/skills/verify-app/, work/를 복사한다. 키트 공통 파일은 수정하지 않는다. 공개 예제에는 vendor·.git·개인 환경을 넣지 않는다.

상세 의도와 선택 이유는 work/intent.md 및 work/decisions.tsv, 실행 계약은 .agents/skills/verify-app/SKILL.md, 마지막 결과는 work/handoff.md를 읽는다. 실패 회귀 코드는 최종 앱에 남기지 않는다.

## 이 저장소에서 재실행

공개 키트 원본의 루트에서 python3 scripts/replay_examples.py ledger를 실행하면 빈 Git 프로젝트에 현재 키트를 설치하고 실제 커밋 훅으로 다시 검증한다. evidence/는 준비 단계의 보존 기록이며 현재 프로젝트의 검증 상태로 사용하지 않는다. 원래 .kit/ 경로로 기록된 CSV 증거는 이 내보내기의 evidence/ 아래에 보존했다.
