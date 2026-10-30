---
{"action": "정상 입력 후 음수·문자 금액·알 수 없는 상태·필수 컬럼 누락 입력", "checks": ["orders-cli"], "entry": "python3 app/nonexistent.py input.csv output.json", "expected": "정상은 성공, 오류는 실패하며 기존 출력 보존", "id": "F001", "invariants": ["잘못된 행 하나면 전체 거절"], "precondition": "UTF-8 CSV와 기존 출력", "sources": ["app/nonexistent.py"], "title": "CSV 가져오기와 유효성 검사"}
---

# F001: CSV 가져오기와 유효성 검사

이 파일은 메타데이터와 본문을 함께 검증합니다. 변경은 kit.py map add로 수행하세요.

- 사전 조건: UTF-8 CSV와 기존 출력
- 사용자 진입 경로: python3 app/nonexistent.py input.csv output.json
- 조작/입력: 정상 입력 후 음수·문자 금액·알 수 없는 상태·필수 컬럼 누락 입력
- 관측할 결과: 정상은 성공, 오류는 실패하며 기존 출력 보존

## 소스
- app/nonexistent.py

## 불변식
- 잘못된 행 하나면 전체 거절

## 검사
- orders-cli
