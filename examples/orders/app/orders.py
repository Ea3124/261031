import argparse
import csv
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def aggregate(stream):
    reader = csv.DictReader(stream, strict=True)
    if reader.fieldnames is None or len(reader.fieldnames) != 3 or set(reader.fieldnames) != {"order_id", "amount", "status"}:
        raise ValueError("필수 컬럼 order_id, amount, status가 정확히 필요합니다")
    seen = {}
    count = total = 0
    for line, row in enumerate(reader, 2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{line}행: 컬럼 수 오류")
        order_id, raw_amount, status = row["order_id"], row["amount"], row["status"]
        if not order_id.strip() or not re.fullmatch(r"[0-9]+", raw_amount) or status not in {"confirmed", "cancelled"}:
            raise ValueError(f"{line}행: 주문 ID, 금액 또는 상태 오류")
        amount = int(raw_amount)
        record = (amount, status)
        if order_id in seen:
            if seen[order_id] != record:
                raise ValueError(f"{line}행: 같은 ID의 금액 또는 상태 충돌")
            continue
        seen[order_id] = record
        if status == "confirmed":
            count += 1
            total += amount
    return {"confirmed_count": count, "total_amount": total}


def main(argv=None):
    parser = argparse.ArgumentParser(description="CSV 확정 주문 집계")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    temp = None
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("입력과 출력 경로가 같을 수 없습니다")
        with args.input.open(encoding="utf-8", newline="") as stream:
            result = aggregate(stream)
        data = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        with tempfile.NamedTemporaryFile(dir=args.output.parent, prefix=".orders-", delete=False) as stream:
            temp = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, args.output)
        temp = None
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
