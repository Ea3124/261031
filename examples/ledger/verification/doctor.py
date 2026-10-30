import platform
import sys
from support import RUN, sandbox, success
assert sys.version_info >= (3, 9)
path = sandbox('doctor')
success(path, 0, 'balance')
assert not path.exists(), 'read created a ledger'
(RUN / 'environment.txt').write_text('Python ' + platform.python_version() + '\nCLI ready; fresh balance=0; no server required\n')
print('실제 CLI 준비 확인: 빈 장부 조회 0, 파일 생성 없음')
