---
name: debug-root-cause
description: 검증 실패·버그·반복되는 같은 오류를 재현하고 최초 원인을 수정할 때 사용한다. 증상 완화나 근거 없는 재시도를 해결로 처리하지 않는다.
---

# 근본 원인 디버깅

1. 사용자가 원하는 결과와 실제 잘못된 결과, 입력·환경·발생 조건을 구분한다. 기대 동작이 불명확하면 질문한다.
2. 실제 사용자 진입점과 고정 초기 상태에서 재현하고 실패 증거를 먼저 보존한다.
3. 앱 준비/초기 상태 문제, 검증 도구 문제, 문서 불일치, 제품 로직 문제를 나눈다. 소스 위치와 실제 값을 읽으며 결과가 처음 잘못되는 지점을 추적한다.
4. 필요한 관측을 추가하되 사용자 데이터나 결과를 바꿔 증상을 숨기지 않는다. 같은 가설이 반복 실패하면 전제부터 실험한다.
5. 정당한 입력 상태를 처리하는 오류라면 해당 경계·도메인 로직을 고친다. 근거 없는 guard·재시도·예외 삼키기·값 강제 보정으로 원인을 가리지 않는다.
6. 저렴한 회귀 검사로 수정 전 실패·수정 후 성공을 확인한다. 전후 같은 초기 상태·명령·관찰 방법을 사용한다.
7. 같은 패턴이 있는 관련 호출자·저장 경로를 확인한다. 수정 범위를 불필요하게 넓히지 않는다.
8. 입력·원인 위치·수정 이유·실제 검증·남은 한계를 기록한다. 제품 오류를 문서나 기대값만 바꿔 통과시키지 않는다.

실제로 반복되는 실수가 확인되면 작은 회귀 검사·타입·스크립트로 예방한다. 지침이나 범용 엔진을 먼저 늘리지 않는다.

실패한 실험의 증거는 유지한다. 확인하지 못한 원인을 확정 사실처럼 말하지 않는다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/principle-fix-root-causes/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-fix-root-causes/SKILL.md)
- [skills/principle-attack-the-premise/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-attack-the-premise/SKILL.md)
- [skills/tdd/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/tdd/SKILL.md)
- [skills/poteto-mode/playbooks/bug-fix.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/poteto-mode/playbooks/bug-fix.md)
- [automations/benny/skills/reproduce-and-fix-issues/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/automations/benny/skills/reproduce-and-fix-issues/SKILL.md)
- [skills/correct/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/correct/SKILL.md)
- [skills/principle-encode-lessons-in-structure/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-encode-lessons-in-structure/SKILL.md)
