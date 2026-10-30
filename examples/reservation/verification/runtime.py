import json
import os
import selectors
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(os.environ["KIT_RUN_DIR"]).resolve()
RUN.mkdir(parents=True, exist_ok=True)
trace = []
process = None
port = None
outcome = "FAIL"


def save():
    (RUN / "http-trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2))


def request(method, path, payload=None, raw=None):
    data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        response = opener.open(req, timeout=2)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        status, body = response.status, json.loads(response.read())
    trace.append({"method": method, "path": path, "input": payload if raw is None else raw.decode(), "status": status, "body": body})
    save()
    return status, body


def expect(method, path, payload, status, body):
    actual_status, actual = request(method, path, payload)
    assert actual_status == status, (path, actual_status, status)
    for key, value in body.items():
        assert actual.get(key) == value, (path, key, actual.get(key), value)
    return actual


try:
    with tempfile.TemporaryDirectory(prefix="reservation-") as state:
        with (RUN / "server.stderr.log").open("w") as stderr:
            process = subprocess.Popen([sys.executable, "-B", str(ROOT / "app/server.py"), "--port", "0"],
                                       cwd=state, stdout=subprocess.PIPE, stderr=stderr, text=True)
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            assert selector.select(5), "server startup timeout"
            startup = json.loads(process.stdout.readline())
            selector.close()
            assert startup["host"] == "0.0.0.0" and startup["service"] == "reservation" and startup["version"] == 1
            port = startup["port"]
            assert type(port) is int and 0 < port < 65536
            (RUN / "server-start.json").write_text(json.dumps({**startup, "pid": process.pid, "temporary_state": state}))
            expect("GET", "/health", None, 200, {"service": "reservation", "version": 1, "ready": True})
            expect("GET", "/inventory", None, 200, {"stock": 2})
            first = expect("POST", "/reservations", {"request_id": "r1", "quantity": 1}, 200, {"stock": 1, "cancelled": False})
            ident = first["reservation_id"]
            expect("POST", "/reservations", {"request_id": "r1", "quantity": 1}, 200, {"stock": 1, "reservation_id": ident})
            expect("POST", "/reservations", {"request_id": "r1", "quantity": 2}, 409, {})
            expect("GET", "/inventory", None, 200, {"stock": 1})
            expect("POST", "/reservations", {"request_id": "r2", "quantity": 1}, 200, {"stock": 0})
            expect("POST", "/reservations", {"request_id": "r3", "quantity": 1}, 409, {})
            expect("GET", "/inventory", None, 200, {"stock": 0})
            expect("POST", f"/reservations/{ident}/cancel", {}, 200, {"stock": 1, "cancelled": True})
            expect("POST", f"/reservations/{ident}/cancel", {}, 200, {"stock": 1, "cancelled": True})
            for bad in [None, [], {}, {"request_id": "bad", "quantity": 0}, {"request_id": "bad", "quantity": -1},
                        {"request_id": "bad", "quantity": True}, {"request_id": "bad", "quantity": 1.5}]:
                expect("POST", "/reservations", bad, 400, {})
                expect("GET", "/inventory", None, 200, {"stock": 1})
            assert request("POST", "/reservations", raw=b"{")[0] == 400
            expect("POST", "/reservations/absent/cancel", {}, 404, {})
            expect("GET", "/inventory", None, 200, {"stock": 1})
            expect("POST", "/reservations", {"request_id": "r1", "quantity": 1}, 200,
                   {"reservation_id": ident, "stock": 1, "cancelled": True})
            expect("POST", "/reservations/r2/cancel", {}, 200, {"stock": 2})
            expect("POST", "/reservations/r2/cancel", {}, 200, {"stock": 2})
            outcome = "PASS"
finally:
    if process is not None:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        if process.stdout:
            process.stdout.close()
        alive = process.poll() is None
        port_closed = True
        if port:
            with socket.socket() as sock:
                sock.settimeout(0.5)
                port_closed = sock.connect_ex(("127.0.0.1", port)) != 0
        cleanup = {"pid": process.pid, "returncode": process.returncode, "alive": alive,
                   "port": port, "port_closed": port_closed, "runtime_outcome": outcome,
                   "trace_exists": (RUN / "http-trace.json").exists()}
        (RUN / "server-cleanup.json").write_text(json.dumps(cleanup, indent=2))
        assert not alive and port_closed, cleanup
    save()
print(f"PASS: real HTTP scenario; port={port}; {len(trace)} observations; own server stopped")
