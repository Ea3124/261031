---
name: 03-feature-map
description: 사용자 요청을 실제 기능·진입점·실행 방법과 연결하는 기능 맵을 만들거나 유지할 때 사용한다. 코드 요약이나 테스트 목록만으로 대체하지 않는다.
---

# 03. 기능 맵

정본은 docs/features.md다. 앱이 커지면 문서를 기능별로 나누고 이 파일을 인덱스로 유지한다. 자유로운 Markdown이며 생성기나 고정 JSON 필드는 없다.

## 만드는 순서
1. 실제 사용자·호출자의 진입점을 코드와 실행에서 찾는다. UI, CLI, API, 라이브러리, 파일 처리, 백그라운드 작업을 모두 포함할 수 있다.
2. 내부 함수가 아닌 사용자가 달성하는 결과를 기능으로 묶고 안정적인 이름이나 ID를 준다.
3. 기능의 목적, 진입점, 전제조건·초기 상태, 정확한 입력·동작 순서, 기대 결과·상태 변화, 관련 소스, 확인 명령을 기록한다.
4. 도메인에 필요한 불변식·오류 입력·권한·부수효과·성능·알려진 제약을 추가한다. 필드 추가 때문에 도구 코드를 수정하지 않는다.
5. 관찰한 현재 동작과 사용자가 원하는 동작을 구분한다. 모호한 기대 결과는 질문한다.
6. 해당 경로를 실제로 실행해 문서와 같은지 확인한다. 실행하지 못한 경로·수동 확인이 필요한 화면은 미확인으로 남긴다.

## 바꾸는 순서
- 기능·사용법·제약·소스 경로가 바뀔 때 관련 항목과 검사만 함께 갱신한다. 모든 커밋에서 문서를 다시 쓰지 않는다.
- 사라진 기능은 제거하고 다른 문서의 연결도 확인한다. 중요한 기능 완료 때 전체 목록과 실제 소스를 비교한다.
- 설명이 틀리면 문서를 고친다. 제품 회귀를 문서 수정으로 숨기거나 검사하기 쉬운 경로 하나로 사용자 전체 경로를 대체하지 않는다.
- 화면 조작은 RULE.md를 따른다. 자동 DOM 클릭을 우회 수단으로 쓰지 않고 실제로 확인한 계층만 검증했다고 말한다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/create-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/create-verification-skill/SKILL.md)
- [skills/maintain-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/maintain-verification-skill/SKILL.md)
- [skills/create-verification-skill/references/feature-map-example/README.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/create-verification-skill/references/feature-map-example/README.md)
