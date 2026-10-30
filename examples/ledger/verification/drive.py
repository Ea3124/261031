import json
from support import RUN, sandbox, success, rejected
for replay in range(2):
    path = sandbox('acceptance-' + str(replay))
    success(path, 100, 'deposit', 'r1', '100')
    deposited = path.read_bytes()
    success(path, 100, 'deposit', 'r1', '100')
    assert path.read_bytes() == deposited
    success(path, 70, 'withdraw', 'r2', '30')
    before = path.read_bytes()
    success(path, 70, 'withdraw', 'r2', '30')
    assert before == path.read_bytes()
    rejected(path, 'withdraw', 'r2', '20')
    rejected(path, 'withdraw', 'r3', '71')
    saved = path.read_bytes()
    success(path, 70, 'balance')
    assert path.read_bytes() == saved
    for amount in ('0', '-1', 'abc'):
        rejected(path, 'deposit', 'invalid', amount)
    success(path, 70, 'balance')
    actual = json.loads(path.read_text())
    assert actual == {'balance': 70, 'requests': {
        'r1': {'kind': 'deposit', 'amount': 100},
        'r2': {'kind': 'withdraw', 'amount': 30}}}
    assert sorted(p.name for p in path.parent.iterdir()) == ['ledger.json']
    (RUN / ('acceptance-final-' + str(replay) + '.json')).write_text(path.read_text())
(RUN / 'runtime-result.json').write_text(json.dumps({'passed': True, 'independent_fresh_runs': 2, 'expected_balance': 70}))
print('고정 인수 시나리오 2회 통과: 새 프로세스 잔액 70, 파일과 임시 파일 잔류 검사 완료')
