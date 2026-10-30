---
name: fde-workflow
description: 로컬 Git 과제의 시작·구현·검증·커밋·세션 전환을 진행한다. 사용자 기대가 모호하면 질문하고, 필요한 보강 스킬만 해당 단계에서 읽는다.
---

# 로컬 작업 흐름

## 시작
1. 실제 과제 안내·기존 README·RULE.md·AGENTS.md를 읽고 Git 상태와 docs/intent.md·features.md·handoff.md를 확인한다.
2. 현재 코드·실행 방법처럼 관찰 가능한 사실은 조사한다. 사용자가 구체적으로 정하지 않은 기대 동작·예외 처리·우선순위·성공 기준은 반드시 질문한다. 답변 전 해당 부분을 임의로 구현하거나 정답으로 고정하지 않는다.
3. docs/intent.md에 확인된 목표·제약·입력과 기대 결과·핵심 로직·미결 질문을 기록한다. 과제 전체 종료 시각도 확인한다.

## 진행
- 기본 반복은 작은 구현 → ./scripts/check → 코드·증거 검토 → 함께 스테이징 → 커밋이다.
- 기존 흐름이나 변경 영향이 불명확할 때만 design-change를 읽는다. 기능·사용법·제약이 바뀌면 feature-map으로 문서를 갱신한다.
- 검증을 처음 만들거나 방법이 바뀌면 verify-app을 읽는다. 모든 핵심 로직은 test-verifier로 개별 결함주입 실패와 복구 성공을 실증한다.
- 실패 원인이 불명확하면 debug-root-cause를 읽는다. 반복 재시도보다 관측과 가설 수정을 우선한다.
- 완료 조건을 낮추거나 검사·기대값을 약화해 통과시키지 않는다. 미실행·접근 불가·시간초과·미확인 결과는 통과가 아니다.
- 같은 작업트리를 여러 작성자가 동시에 수정하지 않는다. 기본은 제공 Codex 한 세션의 순차 작업이다.

## 커밋과 종료
- Git 훅은 이미 수행한 검증과 현재 커밋 대상의 일치만 확인한다. 검사 실행·문서 수정·자동 스테이징을 하지 않는다.
- 핵심 증거는 .evidence/에 보존해 코드와 함께 커밋한다. 자신의 임시 상태만 정리하고 실패 증거도 남긴다.
- 세션 전환·중단·완료 때만 handoff를 읽고 최종 검증 전에 인계 문서를 작성한다. 증거는 .evidence/latest로 연결하고 검증·스테이징·커밋 뒤 최종 결과와 SHA를 응답한다. 미검증 변경은 통과한 것으로 커밋하지 않는다.
- RULE.md의 모델·전송·화면·제출·지원 종료 경계를 따른다. 원본 pstack의 외부 모델·PR·자동화를 활성화하지 않는다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/in-your-own-words/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/in-your-own-words/SKILL.md)
- [skills/figure-it-out/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/figure-it-out/SKILL.md)
- [skills/principle-sequence-verifiable-units/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-sequence-verifiable-units/SKILL.md)
- [skills/poteto-mode/playbooks/autonomous-run.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/poteto-mode/playbooks/autonomous-run.md)
- [automations/benny/skills/triage-issue-reports/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/automations/benny/skills/triage-issue-reports/SKILL.md)
