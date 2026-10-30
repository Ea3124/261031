import json
import socket
import sys
import tempfile
from pathlib import Path

assert sys.version_info >= (3, 9), sys.version
assert Path("app/server.py").is_file()
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "probe"
    path.write_text("synthetic")
    assert path.read_text() == "synthetic"
with socket.socket() as sock:
    sock.bind(("0.0.0.0", 0))
    assert sock.getsockname()[1] > 0
assert json.loads('{"quantity":1}')["quantity"] == 1
print(f"PASS: Python {sys.version.split()[0]}, temporary storage, JSON and bind available")
