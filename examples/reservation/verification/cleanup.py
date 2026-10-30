import json
import os
from pathlib import Path

run = Path(os.environ["KIT_RUN_DIR"])
proof = run / "server-cleanup.json"
if proof.exists():
    state = json.loads(proof.read_text())
    assert state["alive"] is False and state["port_closed"] is True, state
    assert (run / "http-trace.json").is_file()
    print("PASS: runtime-owned server stopped, HTTP trace retained")
else:
    assert not (run / "server-start.json").exists(), "started server has no cleanup proof"
    print("PASS: no runtime server started")
(run / "cleanup-evidence.json").write_text(json.dumps({"evidence_preserved": True, "server_proof_present": proof.exists()}))
