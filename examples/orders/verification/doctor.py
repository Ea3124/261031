import subprocess
import sys
from pathlib import Path
assert sys.version_info >= (3, 9), "Python 3.9 이상 필요"
assert Path("app/orders.py").is_file()
p = subprocess.run([sys.executable, "app/orders.py", "--help"], capture_output=True, text=True)
assert p.returncode == 0 and "input" in p.stdout and "output" in p.stdout, p.stderr
print("Python 준비 및 CLI 인수 계약 확인")
