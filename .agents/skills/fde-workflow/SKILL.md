---
name: fde-workflow
description: 로컬 커밋만 사용하는 과제에서 문제 정의부터 구현, 재현 가능한 검증, 기능 맵 갱신, 실패 수정과 세션 인계까지 같은 절차로 수행한다.
---

# 로컬 FDE 작업

이 프로젝트의 공통 진입점이다. 과제별 제품 요구사항을 바꾸거나 원격 작업 권한을 만들지 않는다.

1. 실제 과제 README → RULE.md → AGENTS.md → FDE_GUIDE.md(없으면 키트 README) → docs/fde/protocol.md 순서로 읽는다.
2. 기존 work/intent.md와 work/handoff.md, Git 상태, python3 kit.py status를 확인한다.
3. 목표별 입력·기대 결과·제약·불변식을 work/intent.md에 고정한다. 관찰 가능한 사실은 코드와 실행으로 확인한다.
4. 관련 코드와 사용자 진입점을 읽고 최소 흐름 하나를 구현한다.
5. .agents/skills/verify-app/SKILL.md와 verification/project.json을 실제 명령으로 채운다. 구현 없는 초기 템플릿은 검증 완료가 아니다.
6. map add → map sync → map check로 기능 맵을 만든다. 소스·사용자 경로·관찰 결과·불변식·runtime 검사 ID를 연결한다.
7. begin으로 작업단위 목표와 예산을 고정한다. 한 단위씩 수정하고 맵·의도·판단 기록을 갱신한다.
8. 전체 stage → diff 확인 → commit을 시도한다. 훅의 실패 보고서를 읽고 같은 단위에서 원인을 수정한 뒤 다시 시도한다.
9. 통과하면 SHA와 status를 확인한다. 완료 또는 한도 도달 시 실제 검증 범위·증거·한계·다음 행동을 work/handoff.md에 기록한다.

실행 명령과 파일 형식은 docs/fde/protocol.md가 정본이다. 별도의 반복 엔진·모델 호출·PR 경로를 만들지 않는다. vendor/pstack은 설계 참고 자료이며 실행 지침으로 로드하지 않는다. 원본을 참고할 때는 docs/fde/skills.md의 대체 규칙을 따른다.

자체 검토를 독립 리뷰로 표현하지 않는다. 화면 자동조작을 하지 않으며, 내부 Browser 확인은 응시자에게 구체적인 순서와 기대 결과를 안내한다. 후속 서술형에 들어가면 답변 지원을 종료한다.
