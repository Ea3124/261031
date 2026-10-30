---
name: test-verifier
description: 검증을 새로 만들거나 핵심 로직·계약·검증 방법을 바꿀 때, 모든 핵심 로직을 하나씩 의도적으로 손상해 검증기의 탐지 능력을 실증한다.
---

# 검증기 실증: 핵심 로직별 결함주입

검증 통과만으로 검증기를 신뢰하지 않는다. docs/intent.md에 핵심 로직 목록과 지켜야 할 조건을 정하고, 각 로직의 증거가 빠지지 않았는지 확인한다.

## 로직 하나마다 수행
1. 정상 소스·초기 데이터·도구·실행 방법을 확정하고 같은 공식 검증 명령의 정상 결과를 보존한다.
2. 안전한 격리 복사본 또는 복구 가능한 실험 상태에서 그 로직만 잘못되게 바꾼다. 실제 사용자 데이터·운영 인스턴스에 결함을 넣지 않는다.
3. 삭제한 중복 방지, 잘못된 상태 전이, 누락한 권한/입력 검사처럼 계약을 실제로 깨는 변형을 택한다. 해당 잘못을 드러내는 입력을 사용한다.
4. 같은 초기 상태와 같은 명령으로 실행해 해당 기대 결과·불변식 때문에 실패하는지 확인한다. 문법 오류·앱 시작 실패·소스 변경 감지·무조건 raise만으로 멈춘 것은 해당 로직의 탐지 증거가 아니다.
5. 변형 내용 또는 재현 가능한 patch, 입력·기대·실제 결과·실패 로그와 어떤 검사가 잡았는지 보존한다.
6. 정상 소스로 복구하고 같은 절차로 다시 통과하는지 확인한다. 다음 변형은 항상 복구된 동일 기준에서 시작한다.

## 판정
- 모든 핵심 로직을 각각 시험한다. 한 번의 결함이 잡혔다고 나머지도 검증됐다고 하지 않는다.
- 잘못된 동작이 통과하면 검증의 누락을 보완한다. 기대값을 바꾸거나 무관한 오류를 넣어 실패를 꾸미지 않는다.
- 실제 동작이 동일한 변형은 유효한 결함이 아니다. 계약을 어기는 변형과 입력을 다시 선택한다.
- 검증 코드를 바꿨다면 관련 결함주입도 다시 수행한다. 정상 상태·모든 필요한 실패·복구 성공의 연결을 남긴다.
- 최종 작업트리에는 의도적 결함을 남기지 않는다. 실험 파일·프로세스는 정리하고 실패 증거는 Git에 보존한다.
- 이것은 시험한 핵심 로직에 대한 탐지 실증이며 전체 입력·상태 공간의 형식 증명은 아니다.

## 추출 출처
원본의 필요한 판단 기준만 이 흐름에 맞게 편집했다. 원본 실행 지시나 전이 의존성을 활성화하지 않는다.
- [skills/create-formal-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/create-formal-verification-skill/SKILL.md)
- [skills/maintain-formal-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/maintain-formal-verification-skill/SKILL.md)
- [skills/principle-test-behavior-not-implementation/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/principle-test-behavior-not-implementation/SKILL.md)
- [skills/tdd/SKILL.md](https://github.com/backnotprop/pstack/blob/25abb38559ddbabec563646224d09eff9a250eca/skills/tdd/SKILL.md)
