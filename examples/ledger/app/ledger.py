import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def load(path):
    if not path.exists():
        return {'balance': 0, 'requests': {}}
    state = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(state, dict) or set(state) != {'balance', 'requests'}
            or type(state['balance']) is not int or state['balance'] < 0
            or not isinstance(state['requests'], dict)):
        raise ValueError('invalid ledger')
    for request_id, request in state['requests'].items():
        if (not request_id or not isinstance(request, dict)
                or set(request) != {'kind', 'amount'}
                or request['kind'] not in ('deposit', 'withdraw')
                or type(request['amount']) is not int or request['amount'] <= 0):
            raise ValueError('invalid saved request')
    return state


def save(path, state):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=path.parent, prefix='.ledger-',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description='Local JSON ledger')
    parser.add_argument('--file', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('balance')
    for name in ('deposit', 'withdraw'):
        command = commands.add_parser(name)
        command.add_argument('request_id')
        command.add_argument('amount')
    args = parser.parse_args()
    try:
        if args.command != 'balance':
            if not args.request_id.strip():
                raise ValueError('request ID must not be empty')
            if not re.fullmatch(r'[0-9]+', args.amount) or int(args.amount) <= 0:
                raise ValueError('amount must be a positive integer')
            amount = int(args.amount)
        state = load(args.file)
        if args.command != 'balance':
            request = {'kind': args.command, 'amount': amount}
            existing = state['requests'].get(args.request_id)
            if existing is not None and existing != request:
                raise ValueError('request ID conflict')
            if existing is not None:
                print(json.dumps({'balance': state['balance']}))
                return 0
            if args.command == 'withdraw' and amount > state['balance']:
                raise ValueError('insufficient balance')
            delta = amount if args.command == 'deposit' else -amount
            state['balance'] += delta
            state['requests'][args.request_id] = request
            save(args.file, state)
        print(json.dumps({'balance': state['balance']}))
        return 0
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
