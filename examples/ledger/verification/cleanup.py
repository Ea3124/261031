import json
import os
from pathlib import Path
import shutil
run = Path(os.environ['KIT_RUN_DIR']).resolve()
scratch = run / 'scratch'
if scratch.exists():
    shutil.rmtree(scratch)
assert not scratch.exists()
evidence = sorted(p.name for p in run.iterdir() if p.is_file())
(run / 'cleanup-result.json').write_text(json.dumps({'scratch_removed': True, 'preserved': evidence}))
print('이 실행의 scratch만 정리함; 증거 보존: ' + ', '.join(evidence))
