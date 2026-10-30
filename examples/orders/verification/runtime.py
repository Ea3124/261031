import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

run=Path(os.environ["KIT_RUN_DIR"])
scratch=run / "csv-scratch"
scratch.mkdir()
evidence=run / "csv-evidence"
evidence.mkdir()
source=scratch / "input.csv"
output=scratch / "output.json"
header="order_id,amount,status\n"
valid=header+"a,100,confirmed\na,100,confirmed\nb,40,cancelled\nc,25,confirmed\n"
expected=b'{"confirmed_count":2,"total_amount":125}\n'
records=[]

def invoke(name, content):
    source.write_text(content,encoding="utf-8")
    before=output.read_bytes() if output.exists() else None
    proc=subprocess.run([sys.executable,"app/orders.py",str(source),str(output)],capture_output=True)
    after=output.read_bytes() if output.exists() else None
    (evidence/f"{name}.csv").write_text(content,encoding="utf-8")
    (evidence/f"{name}.stdout").write_bytes(proc.stdout)
    (evidence/f"{name}.stderr").write_bytes(proc.stderr)
    if before is not None: (evidence/f"{name}.before.json").write_bytes(before)
    if after is not None: (evidence/f"{name}.after.json").write_bytes(after)
    record={"case":name,"exit_code":proc.returncode,"before_hex":before.hex() if before is not None else None,"after_hex":after.hex() if after is not None else None,"directory":sorted(p.name for p in scratch.iterdir())}
    records.append(record)
    (evidence/"observed.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
    assert not list(scratch.glob(".orders-*")), record
    return proc, before, after

p,_,first=invoke("normal", valid)
assert p.returncode == 0 and first == expected, records[-1]
p,_,second=invoke("repeat", valid)
assert p.returncode == 0 and second == first, records[-1]
invalid={
 "amount-conflict": valid+"a,101,confirmed\n",
 "status-conflict": valid+"a,100,cancelled\n",
 "negative": header+"a,-1,confirmed\n",
 "nonnumeric": header+"a,no,confirmed\n",
 "unknown-status": header+"a,10,unknown\n",
 "missing-column": "order_id,amount\na,10\n",
 "extra-field": header+"a,10,confirmed,extra\n",
 "missing-field": header+"a,10\n",
 "blank-id": header+",10,confirmed\n",
 "malformed-quote": header+'"a,10,confirmed\n',
}
for name, content in invalid.items():
    p,before,after=invoke(name,content)
    assert p.returncode != 0 and before == expected and after == before, records[-1]
    assert sorted(q.name for q in scratch.iterdir()) == ["input.csv","output.json"]
output.unlink()
p,before,after=invoke("no-partial-output",invalid["negative"])
assert p.returncode != 0 and before is None and after is None, records[-1]
assert sorted(q.name for q in scratch.iterdir()) == ["input.csv"]
print("실제 CLI 정상·재실행·10종 오류 보존·부분 출력 없음 통과")
