---
name: 02-design-change
description: 기존 시스템의 동작을 이해하거나 변경의 구조·자료형·경계·작업 분해·파급을 정할 때 사용한다. 작은 변경에 별도 설계 체계를 강제하지 않는다.
---

# 02. 변경 이해·설계·영향

1. 사용자의 목표를 확인하고 실제 진입점에서 입력 → 처리 → 저장/부수효과 → 결과 흐름을 읽는다. 관련 소스와 현재 실행으로 확인하며 호출자를 지어내지 않는다.
2. 현재 동작, 사용자가 원하는 동작, 확인하지 못한 사실을 나눈다. 기대 동작이 불명확하면 사용자에게 질문한다.
3. 호출자가 어떻게 사용할지부터 적고 필요한 자료형·상태·모듈 소유권을 정한다. 입력 경계에서 검증하고 잘못된 상태를 표현하기 어렵게 자료형을 정한다. 도메인 규칙은 한 곳에서 유지한다.
4. 가장 작은 완결 사용자 흐름으로 작업을 나눈다. 막히는 선행 작업부터 처리하고, 공유 파일·데이터를 같은 시점에 여러 작업자가 수정하지 않는다.
5. 여러 설계가 실제로 의미 있을 때만 대안을 비교한다. 단순 수정을 위해 병렬 설계·추상화·새 의존성을 추가하지 않는다.
6. 기존 코드에서는 변경 밖의 호출자·저장 형식·권한·오류 처리·재시도·동시성에 미치는 영향을 읽는다. 안전하다는 주장은 실제 검사로 확인한다.
7. 같은 우회나 상태 동기화가 반복되면 원래 자료구조·경계가 잘못됐는지 다시 본다.
8. 최종 설명은 구체적인 코드 위치 → 잘못될 수 있는 상황 → 사용자·데이터에 미치는 영향 → 다음 검증 순서로 작성한다. 확인한 사실과 추정·미검증을 구분한다.

결정은 docs/intent.md에 필요한 만큼만 남긴다. 사용자의 기존 규칙, 법적 설명, 확인되지 않은 외부 제약 주석을 일괄 삭제하지 않는다. 모델 패널·MCP 탐색·외부 조직 기록 조회는 기본 동작이 아니다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/how/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/how/SKILL.md)
- [skills/why/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/why/SKILL.md)
- [skills/architect/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/architect/SKILL.md)
- [skills/blast-radius/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/blast-radius/SKILL.md)
- [skills/teach/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/teach/SKILL.md)
- [skills/principle-model-the-domain/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-model-the-domain/SKILL.md)
- [skills/principle-boundary-discipline/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-boundary-discipline/SKILL.md)
- [skills/principle-laziness-protocol/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-laziness-protocol/SKILL.md)
- [skills/principle-foundational-thinking/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-foundational-thinking/SKILL.md)
- [skills/principle-type-system-discipline/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-type-system-discipline/SKILL.md)
- [skills/interrogate/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/interrogate/SKILL.md)
- [skills/no-comments/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/no-comments/SKILL.md)
