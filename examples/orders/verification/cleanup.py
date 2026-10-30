import json
import os
from pathlib import Path
import shutil
run=Path(os.environ["KIT_RUN_DIR"])
scratch=run/"csv-scratch"
existed=scratch.exists()
if existed:
    shutil.rmtree(scratch)
assert not scratch.exists()
files=sorted(str(p.relative_to(run)) for p in (run/"csv-evidence").glob("*"))
(run/"cleanup.json").write_text(json.dumps({"scratch_existed":existed,"scratch_removed":True,"evidence_files":files},ensure_ascii=False,indent=2))
print(f"자체 임시 상태 정리, 증거 {len(files)}개 보존")
