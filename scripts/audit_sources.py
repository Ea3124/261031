#!/usr/bin/env python3
"""고정 pstack 원본과 실행 권한을 읽기 전용으로 감사한다."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
base = root / "vendor/pstack"
manifest = json.loads((base / "ORIGIN.json").read_text(encoding="utf-8"))
errors = []
for relative, expected in manifest["files"].items():
    path = base / relative
    if not path.is_file():
        errors.append("원본 누락: " + relative)
        continue
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
        errors.append("원본 내용 변경: " + relative)
    if bool(path.stat().st_mode & 0o111) != (expected["git_mode"] == "100755"):
        errors.append("실행 권한 변경: " + relative)
if len(list((base / "skills").glob("*/SKILL.md"))) != manifest["skill_count"]:
    errors.append("스킬 개수 불일치")
for error in errors:
    print(error)
print("원본 감사: " + ("실패" if errors else "통과") + "; 파일 " + str(len(manifest["files"])) + "; 스킬 " + str(manifest["skill_count"]))
sys.exit(1 if errors else 0)
