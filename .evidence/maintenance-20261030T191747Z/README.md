# 키트 유지보수 검증

실제 과제 앱이 없는 상태에서 공통 도구를 임시 Git 저장소로 검증했다. 이 기록은 앱의 기능 검증 통과를 뜻하지 않는다.

- baseline.log·final-baseline.log: 실제 commit과 훅을 포함한 전체 23개 검사
- skill-validation.json: 활성 스킬 7개 형식 검사
- syntax.json: 실행 파일별 Bash 문법 검사
- mutations/: 공통 도구의 핵심 규칙 10개를 하나씩 의미상 깨고 같은 검사에서 실패·복구 성공을 확인한 patch와 로그
- result.json: 명령·종료 코드·소스 식별자·SHA256

모든 결함주입은 별도 임시 복사본에서 실행했다. 원본 소스와 실제 index는 바꾸지 않았다. 원본 verification/check는 미설정으로 실패하는 상태를 유지했다.
