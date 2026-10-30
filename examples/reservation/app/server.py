import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class InvalidRequest(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class Inventory:
    def __init__(self):
        self.stock = 2
        self.reservations = {}
        self.lock = threading.Lock()

    def snapshot(self):
        with self.lock:
            return {"stock": self.stock}

    def reserve(self, payload):
        if not isinstance(payload, dict) or set(payload) != {"request_id", "quantity"}:
            raise InvalidRequest(400, "invalid request fields")
        request_id, quantity = payload["request_id"], payload["quantity"]
        if not isinstance(request_id, str) or not request_id or type(quantity) is not int or quantity < 1:
            raise InvalidRequest(400, "invalid request values")
        with self.lock:
            old = self.reservations.get(request_id)
            if old is not None:
                if old["quantity"] != quantity:
                    raise InvalidRequest(409, "request ID reused with different content")
                return {"reservation_id": request_id, "stock": self.stock, "cancelled": old["cancelled"]}
            if quantity > self.stock:
                raise InvalidRequest(409, "insufficient stock")
            self.stock -= quantity
            self.reservations[request_id] = {"quantity": quantity, "cancelled": False}
            return {"reservation_id": request_id, "stock": self.stock, "cancelled": False}

    def cancel(self, reservation_id):
        with self.lock:
            if reservation_id not in self.reservations:
                raise InvalidRequest(404, "reservation not found")
            reservation = self.reservations[reservation_id]
            if not reservation["cancelled"]:
                self.stock += reservation["quantity"]
                reservation["cancelled"] = True
            return {"reservation_id": reservation_id, "stock": self.stock, "cancelled": True}


def make_handler(inventory):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"service": "reservation", "version": 1, "ready": True})
            elif self.path == "/inventory":
                self.send_json(200, inventory.snapshot())
            else:
                self.send_json(404, {"error": "route not found"})

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 4096:
                    raise InvalidRequest(400, "invalid body length")
                try:
                    payload = json.loads(self.rfile.read(length))
                except (ValueError, UnicodeError):
                    raise InvalidRequest(400, "invalid JSON")
                if self.path == "/reservations":
                    body = inventory.reserve(payload)
                elif self.path.startswith("/reservations/") and self.path.endswith("/cancel"):
                    reservation_id = self.path[len("/reservations/"):-len("/cancel")]
                    if payload != {} or not reservation_id or "/" in reservation_id:
                        raise InvalidRequest(400, "invalid cancellation")
                    body = inventory.cancel(reservation_id)
                else:
                    raise InvalidRequest(404, "route not found")
                self.send_json(200, body)
            except InvalidRequest as exc:
                self.send_json(exc.status, {"error": exc.message})
            except ValueError:
                self.send_json(400, {"error": "invalid content length"})
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(Inventory()))
    print(json.dumps({"service": "reservation", "version": 1, "host": server.server_address[0], "port": server.server_address[1]}), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
