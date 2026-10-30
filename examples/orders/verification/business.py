import importlib.util
import io
import json
import os
from pathlib import Path
spec = importlib.util.spec_from_file_location("orders", "app/orders.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
header = "order_id,amount,status\n"
cases = [
    ("fixed", "a,100,confirmed\na,100,confirmed\nb,40,cancelled\nc,25,confirmed\n", {"confirmed_count": 2, "total_amount": 125}),
    ("empty", "", {"confirmed_count": 0, "total_amount": 0}),
    ("zero", "a,0,confirmed\na,0,confirmed\nb,9,cancelled\n", {"confirmed_count": 1, "total_amount": 0}),
    ("conflict-amount", "a,1,confirmed\na,2,confirmed\n", None),
    ("conflict-status", "a,1,confirmed\na,1,cancelled\n", None),
    ("negative", "a,-1,confirmed\n", None),
    ("nonnumeric", "a,hello,confirmed\n", None),
    ("unknown", "a,1,pending\n", None),
]
records=[]
try:
    for name, body, expected in cases:
        try:
            actual=module.aggregate(io.StringIO(header+body))
        except ValueError:
            actual=None
        records.append({"case": name, "expected": expected, "actual": actual})
        assert actual == expected, records[-1]
    print("독립 기대값 기반 불변식 8종 통과")
finally:
    Path(os.environ["KIT_RUN_DIR"], "business.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
