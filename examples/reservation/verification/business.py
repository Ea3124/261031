import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.server import Inventory, InvalidRequest

# Expectations are a reservation ledger derived from the specification, never app constants.
actions = [("reserve", "a", 1), ("reserve", "b", 2), ("reserve", "a", 2),
           ("cancel", "a", 0), ("cancel", "b", 0), ("reserve", "c", 0)]
transitions = 0
for sequence in itertools.product(actions, repeat=4):
    app = Inventory()
    records = {}
    for kind, ident, quantity in sequence:
        expected_stock = 2 - sum(q for q, active in records.values() if active)
        error = None
        if kind == "reserve":
            if quantity < 1:
                error = 400
            elif ident in records:
                if records[ident][0] != quantity:
                    error = 409
            elif quantity > expected_stock:
                error = 409
            else:
                records[ident] = (quantity, True)
        elif ident not in records:
            error = 404
        else:
            records[ident] = (records[ident][0], False)
        try:
            result = app.reserve({"request_id": ident, "quantity": quantity}) if kind == "reserve" else app.cancel(ident)
            assert error is None, (sequence, "expected error", error)
            assert result["reservation_id"] == ident
        except InvalidRequest as exc:
            assert exc.status == error, (sequence, exc.status, error)
        expected_stock = 2 - sum(q for q, active in records.values() if active)
        assert app.snapshot() == {"stock": expected_stock}, (sequence, app.snapshot(), expected_stock)
        assert 0 <= app.snapshot()["stock"] <= 2
        transitions += 1
print(f"PASS: {len(actions) ** 4} independent ledger sequences, {transitions} transitions")
