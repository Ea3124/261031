#!/usr/bin/env python3
"""공개 합성 예제를 빈 Git 프로젝트에 설치하고 실제 훅 커밋으로 재검증한다."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("ledger", "reservation", "orders")


def run(argv, cwd):
    p = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=180)
    result = {"argv": argv, "returncode": p.returncode,
              "output": p.stdout.replace(str(cwd), "<project>")}
    if p.returncode:
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


def replay(name, archive):
    example = ROOT / "examples" / name
    if not example.is_dir():
        raise RuntimeError("예제가 없습니다: " + name)
    with tempfile.TemporaryDirectory(prefix="fde-replay-" + name + "-") as folder:
        project = Path(folder)
        try:
            commands = []
            commands.append(run(["git", "init", "-q", "--initial-branch=main"], project))
            commands.append(run(["git", "config", "--local", "user.name", "FDE Replay"], project))
            commands.append(run(["git", "config", "--local", "user.email", "replay@example.invalid"], project))
            if (example / "README.md").is_file():
                shutil.copy2(example / "README.md", project / "README.md")
            commands.append(run([sys.executable, str(ROOT / "kit.py"), "install",
                                 "--project", str(project)], project))
            for relative in ("app", "verification", "work", ".agents/skills/verify-app"):
                src = example / relative
                if not src.is_dir():
                    raise RuntimeError("예제 구성 누락: " + str(src))
                shutil.copytree(src, project / relative, dirs_exist_ok=True)
            commands.append(run([sys.executable, "kit.py", "map", "check"], project))
            commands.append(run([sys.executable, "kit.py", "begin", "--unit", "REPLAY",
                                 "--goal", name + " 예제의 실제 사용자 동작과 커밋 검증"], project))
            commands.append(run(["git", "add", "-A"], project))
            commands.append(run(["git", "commit", "-m", "합성 예제 사용자 동작 검증"], project))
            commands.append(run([sys.executable, "kit.py", "status"], project))
            head = run(["git", "rev-parse", "HEAD"], project)["output"].strip()
            report = json.loads((project / ".kit/latest.json").read_text())
            return {"scenario": name, "status": "PASS", "commit": head,
                    "verification": report, "commands": commands}
        finally:
            evidence = project / ".kit"
            if evidence.is_dir():
                shutil.copytree(evidence, archive / name, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("tmp", "__pycache__"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=(*NAMES, "all"))
    parser.add_argument("--output", default=".kit/example-replay.json")
    args = parser.parse_args()
    names = NAMES if args.scenario == "all" else (args.scenario,)
    report = {"kit_sha256": hashlib.sha256((ROOT / "kit.py").read_bytes()).hexdigest(),
              "results": []}
    for name in names:
        try:
            result = replay(name, Path(args.output).resolve().parent / "replay-evidence")
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            result = {"scenario": name, "status": "FAIL", "error": str(exc)}
        report["results"].append(result)
        print(name + ": " + result["status"])
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["status"] == "PASS" for r in report["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
