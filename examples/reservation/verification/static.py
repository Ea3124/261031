import ast
from pathlib import Path

files = sorted(Path("app").glob("*.py")) + sorted(Path("verification").glob("*.py"))
assert files
for path in files:
    ast.parse(path.read_text(), filename=str(path))
    compile(path.read_text(), str(path), "exec")
print(f"PASS: {len(files)} Python sources parse and compile without generated files")
