# 261031 — 로컬 커밋 기반 FDE 키트

혼자 과제를 수행하는 Codex가 문제의 의도, 실행 방법, 기능의 구조, 검증 근거를 잃지 않고 작업하도록 만드는 준비용 키트다. 과제별 애플리케이션은 포함하지 않는다. 실제 문제가 주어지면 애플리케이션과 검증 명령을 채운다.

공통 실행기는 Python 3.9 이상·POSIX 환경·Git만 사용한다. 원격 CI, 외부 AI 호출, 화면 자동조작, 외부 전송을 기본 경로에 넣지 않는다. 커밋 전 검증이 실패하면 커밋을 막고, 에이전트가 원인을 수정한 뒤 다시 시도한다.

## 먼저 읽기

1. 실제 과제 안내와 제출 조건.
2. [RULE.md](RULE.md). 사용자가 공개를 요청한 내부 에이전트 지침의 원본이다.
3. [AGENTS.md](AGENTS.md).
4. [공통 실행 절차](docs/fde/protocol.md).
5. [스킬 선정과 실전 대체 규칙](docs/fde/skills.md).
6. [검증 범위와 보안 한계](docs/fde/verification.md).

실제 응시 중에는 제공된 Codex와 허용된 모델만 사용한다. Astra 검증 기록은 이 공개 키트를 만드는 준비 단계의 시험이며 실전 실행 지침이 아니다. 후속 서술형이 시작되면 답변 지원을 종료한다.

## 전체 흐름

~~~mermaid
flowchart TD
    A["문제·제약·목표·완료 조건 정의<br/>in-your-own-words"]
    B["첫 번째 동작 구현<br/>architect의 설계 기준"]
    C["재현 가능한 실행·검증·증거 저장 구축<br/>create-verification-skill"]
    D["기능 맵·진입 경로·갱신 절차 작성<br/>create-verification-skill"]

    A --> B --> C --> D

    subgraph LOOP["에이전트의 로컬 작업 반복"]
        E["작은 작업 단위 구현·수정<br/>principle-sequence-verifiable-units"]
        F["관련 기능 맵·의도·판단 기록 갱신<br/>show-me-your-work"]
        G["변경 전체 스테이징·로컬 커밋 시도"]
        H["pre-commit → kit.py iterate --staged<br/>정적 검사·불변식·동작 검증·증거 저장"]
        I{"검증 통과?"}
        J["실패 증거 확인·원인 분류<br/>principle-fix-root-causes"]
        K["검증한 코드·기능 맵·기록 커밋"]
        L{"목표 달성 또는 시간 한도?"}

        E --> F --> G --> H --> I
        I -->|실패| J
        J --> E
        I -->|통과| K
        K --> L
        L -->|계속| E
    end

    D --> E
    L -->|종료| M["증거·구조·위험·남은 작업 인계<br/>teach의 설명 기준·로컬 인계 절차"]
    J -->|시간·시도 한도| M
~~~

그림의 pstack 이름은 원본의 설계 근거다. 원본 스킬을 통째로 실행한다는 뜻이 아니다. 실제 진입점은 [fde-workflow](.agents/skills/fde-workflow/SKILL.md)와 [verify-app](.agents/skills/verify-app/SKILL.md) 두 개다. 원본은 vendor/pstack에 보존한다.

## 제공 환경에 가져오기

실제 과제의 Git 저장소 루트에서 실행한다. 기존 README와 과제 파일을 교체하지 않는다. 공개 키트를 가져오는 단계 이후에는 네트워크가 필요 없다.

~~~sh
git clone --depth 1 https://github.com/Ea3124/261031.git /tmp/fde-kit-261031
cd /실제/과제/저장소
python3 /tmp/fde-kit-261031/kit.py install --project .
python3 kit.py doctor
~~~

위 경로는 실제 과제 위치로 바꾼다. 현재 폴더가 Git 저장소가 아니면 설치를 중지한다. 연습용 새 폴더에서는 먼저 git init을 수행한다. 기존 훅이나 다른 내용의 키트 파일과 충돌하면 덮어쓰지 않으며, 원인을 확인해 명시적으로 해결한다.

설치 후 FDE_GUIDE.md가 이 안내의 프로젝트 내부 사본이 된다. 전역 모델 설정이나 개인 스킬 디렉터리는 변경하지 않는다. 원본 스킬을 재귀 탐색하는 범용 설치 명령 대신 위 설치 명령을 사용한다.

## 과제를 받은 뒤 수행할 순서

| 순서 | 에이전트가 하는 일 | 다음 단계로 넘어가는 조건 |
|---|---|---|
| 1 | 과제 안내와 기존 코드를 읽고 work/intent.md 작성 | 목표별 입력·기대 결과·제약·제출 경로가 명시됨 |
| 2 | 핵심 사용자 흐름 하나를 최소 구현 | 실제 사용자 인터페이스로 한 번 실행 가능 |
| 3 | verification/project.json에 환경 점검·정적 검사·불변식·실행 검증·정리 명령 등록 | 명령은 인자 배열이며 새 상태에서 재실행 가능 |
| 4 | verify-app의 실행·준비 확인·조작·증거·정리 방법을 실제 명령으로 작성 | 빈 설명이나 실행하지 않은 예시가 없음 |
| 5 | 기능별 맵을 만들고 인덱스 동기화 | 모든 기능에 소스·사용자 경로·불변식·실행 검증 연결 |
| 6 | 작업단위를 시작하고 관련 변경·맵·판단 기록 작성 | 이번 단위의 목표와 제한 시간이 고정됨 |
| 7 | 전체 변경을 스테이징하고 커밋 시도 | 훅이 동일한 내용으로 검증하고 성공해야 커밋 생성 |
| 8 | 실패 로그를 읽고 원인을 수정한 뒤 재시도 | 검증을 약화하거나 횟수를 초기화하지 않음 |
| 9 | 완료 또는 한도 도달 시 work/handoff.md 갱신 | 실제 통과 범위·미확인 부분·다음 행동을 재개 가능하게 기록 |

초기 설정에는 앱별 명령이 없으므로 검증이 실패하는 것이 정상이다. 아무것도 검사하지 않았는데 통과시키지 않는다. 상세 파일 형식과 실패 시 행동은 [공통 실행 절차](docs/fde/protocol.md)에 있다.

## 통일된 작업 명령

앱별 설정과 기능 맵을 채운 다음 실행한다.

~~~sh
python3 kit.py map sync
python3 kit.py map check
python3 kit.py check
python3 kit.py begin --unit U001 --goal "이번 단위의 관찰 가능한 결과" --minutes 10 --max-attempts 3
git add -A
git diff --cached
git commit -m "첫 사용자 흐름 구현과 검증"
python3 kit.py status
~~~

기능 맵을 만드는 명령은 다음 형태다. 실제 경로와 실제 검사 ID로 바꾼다.

~~~sh
python3 kit.py map add --id F001 --title "항목 생성" \
  --source app/main.py \
  --entry "python3 app/main.py create" \
  --precondition "빈 임시 데이터 디렉터리" \
  --action "이름이 같은 항목을 두 번 생성한다" \
  --expected "항목 하나만 저장되고 재조회된다" \
  --invariant "같은 요청의 재실행은 중복 항목을 만들지 않는다" \
  --check create-runtime
python3 kit.py map sync
~~~

검증 결과와 로그는 .kit/runs/ 아래에 보존한다. cleanup은 증거를 지우지 않는다. status는 마지막 결과가 현재 파일 내용과 일치하는지 확인한다. 코드나 맵이 바뀌면 예전 성공은 유효한 증거가 아니다.

## 기능 맵을 만드는 고정 순서

1. 현재 소스의 사용자 진입점을 읽는다. CLI 명령, HTTP 경로, 파일 입출력, 화면 경로를 구분한다.
2. 사용자가 달성하는 결과 하나에 F001부터 순서대로 ID를 준다. 내부 함수 하나를 기능으로 세지 않는다.
3. 전제조건과 초기 데이터를 정한다. 현재 소스와 실제 실행 결과에서 확인한다.
4. 정확한 진입 명령·입력·조작·관찰 결과·불변식을 적는다.
5. 그 결과를 실제로 검사하는 runtime 검사 ID를 연결한다. 내부 함수만 호출한 검사는 사용자 경로의 증거로 대신하지 않는다.
6. map add로 기능 파일을 만들거나 갱신한다. map sync로 인덱스를 정렬 생성하고 map check로 참조를 확인한다.
7. 실제 검증을 실행해 출력과 부수효과를 확인한다. 기능 맵의 의미가 맞는지는 사람이 읽는 소스 검토와 실제 실행으로 판단한다.
8. 기능을 바꾸면 같은 ID의 설명과 검사를 함께 고친다. 기능이 사라지면 해당 파일을 삭제하고 다시 map sync한다.

전체 유지관리는 주요 기능 완료 시 수행한다. 모든 맵을 소스와 비교하고 실제로 실행한다. 원본 maintain-verification-skill의 방법을 참고하되 PR·다른 모델·화면 자동조작은 사용하지 않는다.

## 세 가지 준비용 검증 시나리오

- [CLI 잔액 장부](docs/fde/scenarios/ledger.md).
- [HTTP 재고 예약](docs/fde/scenarios/reservation.md).
- [CSV 주문 집계](docs/fde/scenarios/orders.md).

각 시나리오는 요구사항만 제공한다. 평가 에이전트가 빈 프로젝트에 설치하고 앱·검사·기능 맵을 직접 만든다. 서로 다른 앱에서도 같은 설치 명령, 맵 형식, 훅, 실패 수정 절차를 따르는지 검증한다. 결과는 reports/에 남긴다.

## 출처와 범위

- pstack 원본은 backnotprop/pstack의 고정 커밋을 사용한다. [출처 명세](vendor/pstack/ORIGIN.json)에서 SHA와 파일별 해시를 확인한다.
- 원본 스킬 58개와 참조 자료는 전이 의존성과 원문의 확인을 위해 비활성 자료로 보존했다. 매 작업에 전부 읽거나 실행하지 않는다.
- 실제 흐름에 필요한 선정 목록과 제외·대체 이유는 [스킬 선정 문서](docs/fde/skills.md)에 있다.
- setup-pstack은 역할별 모델 선택용이다. 훅이나 반복 실행기를 설치하는 스킬이 아니므로 자동 실행하지 않는다.
- 원본 저작권과 MIT 허가문은 [pstack LICENSE](vendor/pstack/LICENSE)에 보존한다. 이 키트의 추가 코드도 MIT로 제공한다.
