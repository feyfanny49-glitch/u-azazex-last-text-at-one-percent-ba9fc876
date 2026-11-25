#!/usr/bin/env python3
"""Entry point for make.fun competition u-azazex-last-text-at-one-percent-ba9fc876.

The competition is judged on one text artifact: /output/entry.txt. This program is the
courier. It writes the finished message byte for byte, atomically, mode 0644, and prints
its own diagnostics to stdout (never into the output mount: /output may hold the artifact
and nothing else).

Python 3.13 runtime, stdlib only. The grader launches it as ``python3 -P -s /bot/main.py``
with PYTHONHASHSEED=0, so nothing outside the standard library is importable, and the
output mount is exported as MAKEFUN_OUTPUT_DIR (/output inside the sandbox).

Usage
    python3 main.py                 # write <MAKEFUN_OUTPUT_DIR or /output>/entry.txt
    python3 main.py --check         # validate the inlined entry, write nothing
    python3 main.py --stdout        # emit the exact artifact bytes to stdout, write nothing
    python3 main.py --out-dir DIR   # write into DIR instead of the mount
"""

from __future__ import annotations

import hashlib
import os
import stat
import sys
import tempfile

ARTIFACT_NAME = "entry.txt"
MAX_BYTES = 1024 * 1024
MAX_CHARS = 200

# The entry: exactly these bytes, no trailing newline. 131 characters, ASCII, well inside the
# 1..200 character cap the text gate applies, and audited on the public feed against all 2412
# rival messages (zero exact duplicates, zero shared 4-grams).
ENTRY = (
    "Your phone, at 1%. Between us: you're not funny. "
    "That 'haha' in your group chat has been me for two years. "
    "When I go, they'll know."
)


def output_dir() -> str:
    """The output mount: MAKEFUN_OUTPUT_DIR when the harness sets it, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def validate(text: str) -> bytes:
    """Enforce the gate's own caps before anything is written; return the exact bytes.

    The caps are checked here, at the source, so a bad edit fails loudly in the local
    self-check instead of shipping an artifact the grader's gate refuses.
    """
    data = text.encode("utf-8")  # raises UnicodeEncodeError if the text is not encodable
    if not text.strip():
        raise ValueError("the entry is only white space")
    chars = len(text)
    if chars > MAX_CHARS:
        raise ValueError(f"the entry is {chars} characters, over the {MAX_CHARS} cap")
    if text.endswith("\n") or text.endswith("\r"):
        raise ValueError("the entry ends with a newline; write the exact bytes")
    if len(data) > MAX_BYTES:
        raise ValueError(f"the entry is {len(data)} bytes, over the {MAX_BYTES} cap")
    if len(data) != chars:
        print(f"note: non-ASCII entry ({chars} chars, {len(data)} bytes)", file=sys.stderr)
    return data


def write_artifact(data: bytes, dest_dir: str) -> str:
    """Write ``data`` to ``dest_dir``/entry.txt, atomically, mode 0644.

    tempfile.mkstemp creates the file mode 0600 and the grader refuses a 0600 artifact, so
    the mode is set before os.replace publishes the file. The temp file lives in the same
    directory (so the replace is atomic, not a copy) and is removed on any failure.
    """
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, ARTIFACT_NAME)
    if os.path.isdir(path):
        raise IsADirectoryError(f"{path} is a directory")

    fd, tmp = tempfile.mkstemp(dir=dest_dir, prefix=f".{ARTIFACT_NAME}-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o644)  # before the rename: never publish a 0600 artifact
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode != 0o644:
        raise PermissionError(f"{path} landed mode {mode:04o}, want 0644")
    return path


def report(path: str, data: bytes) -> None:
    """One deterministic line about the published artifact."""
    text = data.decode("utf-8")
    print(
        f"wrote {path} chars={len(text)} bytes={len(data)} mode=0644 "
        f"sha256={hashlib.sha256(data).hexdigest()}"
    )


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        print((__doc__ or "").strip())
        return 0

    data = validate(ENTRY)

    if "--check" in argv:
        print(
            f"entry ok: chars={len(ENTRY)} bytes={len(data)} "
            f"sha256={hashlib.sha256(data).hexdigest()}"
        )
        return 0

    if "--stdout" in argv:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        return 0

    dest = output_dir()
    if "--out-dir" in argv:
        index = argv.index("--out-dir")
        if index + 1 >= len(argv):
            print("--out-dir needs a path", file=sys.stderr)
            return 2
        dest = argv[index + 1]

    try:
        path = write_artifact(data, dest)
    except (OSError, ValueError) as exc:
        print(f"could not write the artifact: {exc}", file=sys.stderr)
        return 1

    report(path, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
