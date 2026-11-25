#!/usr/bin/env python3
"""Local gate simulator for the /output artifact of u-azazex-last-text-at-one-percent.

Re-checks everything the grader's text gate and the harness's output collection check:
one artifact named entry.txt and nothing else in the mount, a regular file at depth 1, not
mode 0600, <= 1 MiB, valid UTF-8, 1..200 characters, not only white space, and (per the
task) no trailing newline. Exits 0 when every check passes, 1 with the first failure listed.

Usage: python3 tools/verify_entry.py [output-dir]
"""

from __future__ import annotations

import os
import stat
import sys

ARTIFACT_NAME = "entry.txt"
MAX_BYTES = 1024 * 1024
MAX_CHARS = 200


def check(out_dir: str) -> list[str]:
    """Return a list of problems; empty means the artifact passes every check."""
    problems: list[str] = []

    if not os.path.isdir(out_dir):
        return [f"{out_dir}: not a directory"]

    entries = sorted(os.listdir(out_dir))
    if entries != [ARTIFACT_NAME]:
        problems.append(f"{out_dir} must hold only {ARTIFACT_NAME}, found {entries}")

    path = os.path.join(out_dir, ARTIFACT_NAME)
    if not os.path.isfile(path):
        problems.append(f"{path}: not a regular file")
        return problems

    info = os.lstat(path)
    mode = stat.S_IMODE(info.st_mode)
    if mode != 0o644:
        problems.append(f"{path}: mode {mode:04o}, the grader refuses 0600 (want 0644)")
    if info.st_size > MAX_BYTES:
        problems.append(f"{path}: {info.st_size} bytes, over the {MAX_BYTES} byte cap")
    if info.st_size == 0:
        problems.append(f"{path}: empty")

    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        problems.append(f"{path}: not valid UTF-8 ({exc})")
        return problems

    chars = len(text)
    if chars > MAX_CHARS:
        problems.append(f"{path}: {chars} characters, over the {MAX_CHARS} character cap")
    if not text.strip():
        problems.append(f"{path}: only white space")
    if text.endswith("\n") or text.endswith("\r"):
        problems.append(f"{path}: trailing newline (write the exact bytes)")

    print(f"{path}: mode={mode:04o} bytes={info.st_size} chars={chars}")
    print(f"text: {text!r}")
    return problems


def main(argv: list[str]) -> int:
    out_dir = argv[1] if len(argv) > 1 else (
        os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    )
    problems = check(out_dir)
    if problems:
        print("FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("PASS: artifact satisfies every hard cap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
