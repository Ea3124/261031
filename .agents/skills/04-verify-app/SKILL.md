---
name: 04-verify-app
description: 실제 앱의 고정 초기화·실행·관찰·정리 방법과 독립 기대값을 정하고 검증을 실행한다. 검증을 처음 만들거나 실행 환경·방법·기능이 바뀔 때 사용한다.
---

# 04. 재현 가능한 앱 검증

## 먼저 확정할 것
- 기대 동작·불변식·성공 기준이 모호하면 사용자에게 질문한다. 현재 코드의 출력이나 AI의 추정을 정답으로 삼지 않는다.
- docs/features.md의 공통 실행 절차에 필요한 버전·환경변수 이름·고정 데이터·초기화·정확한 명령과 인자·준비 신호·관찰 방법·정리를 적는다.
- 같은 초기 상태에서 항상 동일한 절차로 실행한다. 세션마다 다른 진입점이나 내부 상태 주입으로 대체하지 않는다. 방법을 바꾸면 이유와 영향을 기록하고 새 방법을 실제 검증한다.

## 검사 구성
- 공식 입구는 ./scripts/check, 문제별 실제 명령은 verification/check다. 기존 프로젝트의 검사 도구를 우선 사용하며 검사 종류를 형식적으로 채우지 않는다.
- 필요한 문법·타입·입력 경계 검사와 핵심 비즈니스 불변식, 실제 사용자 경로를 확인한다.
- 재시도·중복·동시성이 있는 계약은 필요한 멱등성·상태 전이도 검사한다. 결과 값뿐 아니라 저장·재조회·중복 요청·오류 후 상태 보존 등 해당 계약의 부수효과를 관찰한다. 기대값은 요구사항에서 독립적으로 정한다.
- 앱·데이터·권한이 준비됐는지 확인하고, 오류·미실행·필수 검사 누락·시간초과를 성공으로 처리하지 않는다.
- 매 실행에 전용 임시 상태를 쓰고 난수·시간·외부 의존성을 필요한 범위에서 고정한다. 서버는 실제 포트와 준비 완료를 확인하고 finally에서 자신이 시작한 프로세스만 종료한다.
- 검사 중 작업 소스나 문서를 수정하지 않는다. 산출물은 EVIDENCE_DIR에, 폐기할 임시 상태는 .evidence/tmp/ 등에 격리한다.

## 신뢰와 기록
- 모든 핵심 로직은 05-test-verifier로 하나씩 깨서 대응 검사의 실제 실패와 복구 성공을 확인한다. 그 기록을 삭제하거나 일반 PASS 로그로 대체하지 않는다.
- 명령·버전·입력·기대값·실제 결과·종료 상태·부수효과·정리 확인과 관련 증거를 남긴다. 비밀 값은 기록하지 않는다.
- .evidence의 통과 증거를 코드와 함께 검토·스테이징한다. Git 훅은 그 대상이 같은지만 확인한다.
- 새 세션은 문서와 현재 상태를 읽고 같은 절차로 실제 검증한다. 오래된 보고서만으로 현재 환경을 통과 처리하지 않는다.
- 성능이 요구되면 기준값을 질문·확정하고 같은 입력·환경에서 반복 측정한다. 실제 완료 작업량과 지연·오류를 함께 확인해 캐시·생략한 작업을 개선으로 오인하지 않는다. 조건·반복·변동을 남긴다.
- 고위험 동시성 등에는 사용 가능한 허용 도구로 범위를 정한 형식 검증을 고려한다. 속성·가정·상태/입력 한도·코드 대응·버전·명령을 남기고 깨진 변형을 잡는지 확인한다. 미실행을 증명 성공으로 표현하지 않는다.
- 통과는 실제 검사한 범위에 한정한다. 불변식 테스트를 형식 증명으로, API 검사를 화면 확인으로 표현하지 않는다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/create-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/create-verification-skill/SKILL.md)
- [skills/maintain-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/maintain-verification-skill/SKILL.md)
- [skills/principle-prove-it-works/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-prove-it-works/SKILL.md)
- [skills/principle-test-behavior-not-implementation/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-test-behavior-not-implementation/SKILL.md)
- [skills/tdd/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/tdd/SKILL.md)
- [skills/benchmark-checklist/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/benchmark-checklist/SKILL.md)
- [skills/principle-make-operations-idempotent/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-make-operations-idempotent/SKILL.md)
- [skills/principle-explain-the-number/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-explain-the-number/SKILL.md)
- [skills/create-formal-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/create-formal-verification-skill/SKILL.md)
- [skills/maintain-formal-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/maintain-formal-verification-skill/SKILL.md)
