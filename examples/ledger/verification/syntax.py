import ast
from pathlib import Path
paths = sorted(Path('app').glob('*.py')) + sorted(Path('verification').glob('*.py'))
assert paths
for path in paths:
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
print(f'Python 문법 검사 통과: {len(paths)}개 파일')
