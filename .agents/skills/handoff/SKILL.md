---
name: handoff
description: 세션 종료·전환·중단·맥락 부족 시 재개 가능한 상태를 남기고, 새 세션에서 실제 파일과 검증 상태를 다시 확인한다.
---

# 인계와 재개

## 남길 때
- 최종 인계 문서는 마지막 ./scripts/check 전에 작성한다. 증거는 .evidence/latest와 그 result를 참조하고 검증 전 성공을 미리 선언하지 않는다. 그 뒤 코드·인계·증거를 함께 스테이징하고 커밋한다.
- docs/handoff.md에 현재 목표와 마지막 변경, 브랜치·직전 커밋·미커밋 변경, 주요 구조·자료형·저장 위치를 적는다.
- 정확한 시작·초기화·검증 명령, 최신 증거 경로, 통과한 범위, 실패·수동 확인·미확인 조건을 구분한다.
- 중요한 결정과 이유는 docs/intent.md, 기능·접근 방법은 docs/features.md를 연결한다. 같은 설명을 여러 파일에 복제하지 않는다.
- 다음 에이전트가 바로 할 수 있는 명령 또는 수정 한 가지를 남긴다. 임시 경로가 사라지면 재생성하는 방법도 적는다.
- 자신이 만든 프로세스·임시 상태를 정리하고 증거가 남았는지 실제 파일로 확인한다.
- 검증된 변경만 정상 절차로 커밋한다. 실패 중인 변경을 숨기거나 강제 WIP·훅 우회로 통과시키지 않는다. 미커밋 상태도 정확히 적는다.
- 자기 자신이 포함될 최종 커밋 SHA를 같은 파일에 넣는 순환을 만들지 않는다. 확인한 직전 SHA와 최신 증거를 기록하고 최종 SHA는 완료 응답에 남긴다.

## 받을 때
1. RULE·과제 안내·의도·기능 맵·인계를 읽는다.
2. 실제 Git 상태·최근 diff·실제 증거를 확인한다. 이전 에이전트의 요약이나 성공 문장만 믿지 않는다.
3. 관련 코드 조사는 재사용하되 현재 앱·초기 상태·환경을 확인하고 공식 절차로 실제 검증한다.
4. 사용자 기대나 변경 목표가 불명확하면 질문한다. 확인된 다음 작업부터 작은 단위로 이어간다.

사용자에게 구조·선택 이유·구체적인 약점·파급·다음 검증을 설명한다. 현재 작업과 무관한 개인 대화·설정을 읽거나 외부 서비스로 인계를 전송하지 않는다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/poteto-mode/playbooks/pause-safely.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/poteto-mode/playbooks/pause-safely.md)
- [skills/poteto-mode/playbooks/session-pickup.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/poteto-mode/playbooks/session-pickup.md)
- [skills/show-me-your-work/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/show-me-your-work/SKILL.md)
- [skills/principle-guard-the-context-window/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-guard-the-context-window/SKILL.md)
- [skills/teach/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/teach/SKILL.md)
- [skills/technical-writing/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/technical-writing/SKILL.md)
- [skills/unslop/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/unslop/SKILL.md)
