import ast
from pathlib import Path
files = sorted(Path("app").glob("*.py")) + sorted(Path("verification").glob("*.py"))
assert files
for path in files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print(f"실제 Python 문법 검사: {len(files)}개 파일")
