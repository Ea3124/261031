---
name: 01-fde-workflow
description: 과제를 시작하거나 업무 요청·메신저 답변으로 목표가 바뀔 때, 근거와 미결 질문을 정리하고 구현·검증·인계로 연결한다. 기대가 이미 확정된 작은 수정에는 질문 절차를 반복하지 않는다.
---

# 01. 문제 파악·업무 질문·작업 연결

처음에는 실제 과제의 README와 제공 안내·자료, RULE.md·AGENTS.md를 확인한다. readme.kit.md는 키트 사용법, readme.skill.md는 필요한 단계의 스킬을 찾는 안내다. 기존 Git 상태와 docs/intent.md·features.md·handoff.md도 읽는다. 샘플 과제나 준비 문서에서 이번 과제의 정답을 가져오지 않는다.

## 무엇을 확정해야 하는가

코드와 파일에서 확인할 수 있는 사실은 먼저 조사한다. 그 뒤 결과를 사용하는 사람, 해결하려는 업무, 필요한 산출물과 제출 위치를 한 문단으로 정리한다. 새 기능 제작인지 기존 동작의 결함 수정인지 나누고, 수정 과제라면 유지해야 할 정상 계약부터 찾는다.

기대 동작을 이해하는 데 필요한 입력 형식·단위·기준 기간, 출력의 의미, 오류나 누락·중복에 대한 처리, 권한·환경·종료 시각을 확인한다. 자료 분석이나 보고서가 목표라면 그 결과에 필요한 흐름을 계획하며, 과제에 없는 웹앱·평가 배점·제출 파일명을 추가하지 않는다.

요구의 정본은 docs/intent.md 한 곳이다. 항목마다 다음 연결을 남기고, 기능 맵이나 인계에는 이 기록을 참조한다.

> 원하는 결과 → 근거가 있는 위치 → 시험할 입력과 기대 결과 → 확인할 검사 → 현재 상태

제공 문서의 명시 사항, 사용자가 확인한 해석, 아직 답이 필요한 부분을 구분한다. 실제 코드가 현재 하는 일과 사용자가 원하는 일도 섞지 않는다. 중요한 변경에는 무엇이 달라졌고 왜 그렇게 판단했는지 덧붙인다.

## 질문이 필요한 지점을 고르기

불명확한 기대·예외 규칙·우선순위·성공 기준은 사용자에게 확인한다. 예를 들어 “합계를 맞춰 달라”면 합산 대상과 단위, 제외 항목이 정해졌는지 먼저 살핀다. 질문은 답이 달라질 때 데이터·구현·검사가 달라지는 지점부터 좁힌다. 이미 제공된 설명을 다시 묻는 대신 충돌한 조건이나 비어 있는 경계를 짚는다.

답변에 의존하는 동작은 임의로 정하지 않는다. 대기 중에는 확정된 입력 구조 조사나 기존 실행법 확인처럼 답과 무관한 작업을 진행한다. 응답이 없다는 이유로 기대값을 스스로 확정하거나 미결 상태를 완료로 표시하지 않는다.

## 메신저에 전달할 질문 초안

실전 메신저의 입력·전송·화면 조작은 RULE.md가 정한 사람의 역할이다. 에이전트는 아래 내용을 짧은 초안으로 준비하고, 실제로 보내거나 답을 받은 것처럼 기록하지 않는다.

- 근거: 어디에서 어떤 조건을 확인했는가.
- 빈칸: 지금 결정되지 않아 작업이 갈리는 부분은 무엇인가.
- 질문: 어떤 기준을 적용할지 한 번에 답할 수 있게 묻는다.
- 차이: 선택 가능한 답이 있다면 각각 바뀌는 결과·구현·검사를 설명한다.

업무 판단은 그 업무를 설명할 담당자에게, 환경 사용·제출 안내는 제공된 도움 창구에, 접속이나 실행 장애는 운영 지원에 묻도록 제안한다. 이런 역할이 실제 환경에 있을 때만 구체적인 대상을 지정하며, 외부 조직이나 서비스를 새로 연결하지 않는다.

질문 번호와 준비한 문안은 docs/intent.md의 미결 질문에 둔다. 사람이 전송을 확인하기 전에는 전달 여부를 미확인으로 남긴다. 답변이 들어오면 답한 범위만 근거와 함께 반영하고, 나머지는 질문을 더 좁혀 남긴다. 메시지 한 건을 받았다는 사실만으로 관련 요구 전부를 해결 처리하지 않는다.

합의가 바뀌면 목표·기대 결과와 영향을 받는 기능 설명·검사를 함께 조정한다. 기존에 확인한 동작을 단순히 문서에서 지워 제품 결함을 감추지 않는다.

## 작은 변경으로 이어가기

- 최소 입력에서 필요한 결과까지 연결하는 첫 작업을 고른다. 구조·변경 영향이 불분명할 때 02-design-change를 읽는다.
- 사용자 기능·접근법·제약이 바뀌면 03-feature-map으로 docs/features.md를 갱신한다.
- 04-verify-app으로 같은 초기 상태와 동일한 절차의 검사를 만들거나 실행한다. 핵심 로직마다 05-test-verifier의 의미 있는 결함주입 실패와 정상 복구 성공을 확인한다.
- 실패 원인을 알 수 없거나 같은 오류가 되풀이되면 06-debug-root-cause로 재현·원인 수정을 진행한다.
- 기본 반복은 작은 변경 → ./scripts/check → 코드·증거 검토 → 함께 스테이징 → 로컬 커밋이다. 검사 약화·오래된 PASS·훅 우회로 통과를 만들지 않는다.
- 같은 작업트리를 동시에 여러 작성자가 바꾸지 않는다. 기본은 제공 Codex 한 세션의 순차 작업이다.
- 세션 전환·중단·완료에는 07-handoff를 사용해 마지막 검사 전에 인계를 쓴다. 증거는 .evidence/latest로 연결하고, 검증·스테이징·커밋 뒤 실제 결과와 최종 SHA를 전달한다.

번호는 필요한 지침을 찾기 위한 표지다. 모든 요청에서 01부터 07까지 순서대로 호출하는 절차가 아니다. 미실행·미확인·검증 불가 상태는 통과와 구별하고, 수행한 검사와 남은 위험을 설명한다. 종료·제출·모델·전송·화면의 허용 범위는 실제 과제 안내와 RULE.md를 적용하며, 이 스킬이 허용이나 중단 시점을 새로 만들지 않는다.

## 참고한 개념과 출처

요구를 근거·검사로 연결하고, 업무 질문을 준비해 답변에 따라 계획을 갱신하는 접근을 [cofa-triage](https://github.com/ripplelover/cofa-ready-kit/blob/main/skills/cofa-triage/SKILL.md)에서 참고했다. 읽은 Git blob은 041e38c27b824de67e95099242ad69970694448e다. 본문은 우리 로컬 검증·기능 맵·인계 흐름에 맞춰 새로 작성했으며, 그 스킬이나 외부 도구를 실행 의존성으로 두지 않는다. 원본 허가문은 ../LICENSE.cofa-ready-kit에 보존한다.

기존 흐름의 pstack 개념 출처는 다음과 같다. 각 링크는 원문 비교용이며 개인 모델 설정·원격 PR·감시 자동화를 활성화하지 않는다.
- [in-your-own-words](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/in-your-own-words/SKILL.md)
- [figure-it-out](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/figure-it-out/SKILL.md)
- [principle-sequence-verifiable-units](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-sequence-verifiable-units/SKILL.md)
- [autonomous-run](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/poteto-mode/playbooks/autonomous-run.md)
- [triage-issue-reports](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/automations/benny/skills/triage-issue-reports/SKILL.md)

<!-- reference: https://github.com/Ea3124/261031/blob/main/.agents/skills/fde-workflow/SKILL.md (번호 변경 전 경로; 당시 내용: https://github.com/Ea3124/261031/blob/bae18c03e3ef562d5e05cb9896004102c3445cc2/.agents/skills/fde-workflow/SKILL.md) -->
