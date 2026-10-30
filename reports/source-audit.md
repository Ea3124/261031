# pstack 소스감사

## 확인한 원본

- 저장소: https://github.com/backnotprop/pstack
- SHA: 25abb38559ddbabec563646224d09eff9a250eca
- 원본 보존: Git 추적 파일 581개, 루트 스킬 58개, 원본 실행 권한과 MIT 라이선스.
- 감사 방식: 별도 Astra가 루트 SKILL.md 58개를 모두 전문 읽고, 도입 관련 참조·helper·playbook을 추가 조사. 루트 에이전트가 도입할 검증·설계·설명·로그·원칙과 setup-pstack을 직접 읽고 통합 방안을 검토.
- 원본 보존 검증: python3 scripts/audit_sources.py 통과. RULE.md는 사용자 원본과 cmp로 바이트 일치 확인.

## 실제로 읽은 주요 참조

README·LICENSE·setup-pstack, 검증 생성/유지관리, 기능 맵 예제 3개, show-me-your-work의 TSV와 log.sh, how의 설명/조사 prompt, architect의 설계 기준·근거 template·runner prompt, why의 사실/추정 분리와 조사·종합 prompt, poteto-mode의 feature·bug-fix·opening-a-pr·session-pickup·pause-safely 등과 실제 watch-pr 실행기·반복 정책을 검토했다.

statechart 전체 구현과 모든 성능·원격 자동화 코드를 전부 검토하거나 실행했다고 주장하지 않는다. 이들은 비활성 원본 자료이며 공통 실행기의 의존성이 아니다.

## 발견과 반영

1. 원본 README의 독립 스킬 표보다 본문의 전이 의존성이 넓다. 원문 비교와 의존성 누락 방지를 위해 원본을 보존하되 활성 진입 스킬은 두 개로 제한했다.
2. poteto-mode는 원격 PR·다른 모델·강제 위임·화면 자동조작을 전제로 한다. 실전 제한과 충돌하므로 원본 전체를 실행하지 않는다.
3. setup-pstack은 모델 설정용이며 훅이나 반복 실행기 설치용이 아니다. 개인 전역 설정을 바꾸지 않는다.
4. show-me-your-work의 다른 모델 계열 리뷰 요구는 실전용 단독 검토와 맞지 않는다. 검토 방식을 정직하게 기록하고 독립 리뷰라고 꾸미지 않는다.
5. API·CLI 검사 결과를 화면 확인으로 바꾸어 보고할 수 없다. 사람의 내부 Browser 확인과 에이전트 명령 검증을 구분한다.
6. 앱별 불변식 검사는 형식 증명이 아니다. 검증 범위·가정·미확인 부분을 남긴다.

선정 스킬별 이유와 실전 대체 규칙은 docs/fde/skills.md가 정본이다.
