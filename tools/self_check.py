#!/usr/bin/env python3
"""Stdlib self-test for the entry: run the entrypoint the way the grader does, then verify.

  1. `main.py --check`      — validate the inlined entry without touching /output.
  2. `main.py` into a fresh directory with MAKEFUN_OUTPUT_DIR set (what the sandbox exports),
     twice, and require byte-identical artifacts.
  3. `tools/verify_entry.py <dir>` — the hard-cap gate simulator.
  4. A failing run (unwritable output directory) must leave nothing behind and exit non-zero.

Exits 0 when every step passes.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(REPO, "main.py")
VERIFY = os.path.join(REPO, "tools", "verify_entry.py")


def run(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args], env=env, cwd=REPO, capture_output=True, text=True
    )


def main() -> int:
    base = tempfile.mkdtemp(prefix="makefun-selfcheck-")
    failures: list[str] = []
    try:
        env = dict(os.environ)
        env.pop("MAKEFUN_OUTPUT_DIR", None)

        checks = run([MAIN, "--check"], env)
        print(f"[1] main.py --check -> {checks.returncode}")
        print(checks.stdout.strip())
        if checks.returncode != 0:
            failures.append("main.py --check failed")

        out_a = os.path.join(base, "a")
        out_b = os.path.join(base, "b")
        digests = []
        for out_dir in (out_a, out_b):
            env["MAKEFUN_OUTPUT_DIR"] = out_dir
            proc = run([MAIN], env)
            print(f"[2] main.py -> {out_dir}: rc={proc.returncode}")
            print(proc.stdout.strip())
            if proc.returncode != 0:
                failures.append(f"main.py failed writing {out_dir}")
                continue
            digest = hashlib.sha256(
                open(os.path.join(out_dir, "entry.txt"), "rb").read()
            ).hexdigest()
            digests.append(digest)
            gate = run([VERIFY, out_dir], env)
            print(gate.stdout.strip())
            if gate.returncode != 0:
                failures.append(f"verify_entry.py rejected {out_dir}")
        if len(digests) == 2 and digests[0] != digests[1]:
            failures.append("two runs produced different bytes")

        blocked = os.path.join(base, "blocked")
        with open(blocked, "w") as handle:
            handle.write("not a directory\n")
        env["MAKEFUN_OUTPUT_DIR"] = blocked
        proc = run([MAIN], env)
        print(f"[4] unwritable output -> rc={proc.returncode}")
        if proc.returncode == 0:
            failures.append("entrypoint did not fail on an unwritable output path")
        if os.path.isfile(blocked) and os.path.getsize(blocked) != len("not a directory\n"):
            failures.append("a failed run modified the blocked path")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASS: entrypoint, determinism and gate checks all pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
