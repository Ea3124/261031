import json
from support import RUN, sandbox, success, rejected

path = sandbox('business')
for index, amount in enumerate(('0', '-1', 'abc', '1.5', ' 1', '+1', 'True')):
    rejected(path, 'deposit', 'invalid-' + str(index), amount)
assert not path.exists()
success(path, 9, 'deposit', 'seed', '9')
initial = path.read_bytes()
success(path, 9, 'deposit', 'seed', '9')
assert path.read_bytes() == initial
rejected(path, 'withdraw', 'seed', '9')
rejected(path, 'deposit', 'seed', '10')
rejected(path, 'withdraw', 'too-much', '10')
for amount in ('0', '-2', 'hello'):
    rejected(path, 'withdraw', 'invalid-withdraw', amount)
success(path, 0, 'withdraw', 'all', '9')
zero = path.read_bytes()
success(path, 0, 'withdraw', 'all', '9')
assert path.read_bytes() == zero
rejected(path, 'withdraw', 'negative', '1')
success(path, 0, 'balance')
assert json.loads(path.read_text()) == {'balance': 0, 'requests': {
    'seed': {'kind': 'deposit', 'amount': 9}, 'all': {'kind': 'withdraw', 'amount': 9}}}
corrupt = sandbox('corrupt')
corrupt.write_text('{broken json')
rejected(corrupt, 'deposit', 'safe', '1')
(RUN / 'business-result.json').write_text(json.dumps({'passed': True, 'final_balance': 0, 'invalid_inputs_unchanged': True}))
print('불변식 통과: 음수 방지, ID 충돌, 중복, 오류 입력과 손상 파일 보존')
