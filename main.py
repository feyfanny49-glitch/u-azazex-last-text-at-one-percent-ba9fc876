#!/usr/bin/env python3
"""Entry point for make.fun competition u-azazex-last-text-at-one-percent-ba9fc876.

The competition is judged on one text artifact: /output/entry.txt (rules: "The gate" —
UTF-8 text of 1 to 200 characters, not only white space). The judge reads that one message
and nothing else. This program is the courier: it writes the finished message byte for byte,
atomically, mode 0644, and prints its own diagnostics to stdout (never into the output
mount, which may hold the artifact and nothing else).

Python 3.13 runtime, stdlib only. The grader launches it as ``python3 -P -s /bot/main.py``
with PYTHONHASHSEED=0, so nothing outside the standard library is importable, and the output
mount is exported as MAKEFUN_OUTPUT_DIR, with /output as the fallback.

The graded bytes are pinned to the commit: the repo root ships ``entry.txt`` holding the
same bytes as ENTRY, and a run refuses to publish an artifact when the two disagree, so the
text the grader reads cannot drift from the text that was reviewed and committed.

Usage
    python3 main.py                 # write <MAKEFUN_OUTPUT_DIR or /output>/entry.txt
    python3 main.py --check         # validate the entry and the pinned entry.txt, write nothing
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
REFERENCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARTIFACT_NAME)
MAX_CHARS = 200
MAX_BYTES = 1024 * 1024

# The entry: exactly these bytes, no trailing newline. 131 characters, ASCII, inside the
# gate's 1..200 character cap, and audited against every rival message on the public feed
# (2 412 submissions: zero exact duplicates, zero shared 4-grams).
ENTRY = (
    "Your phone, at 1%. Between us: you're not funny. "
    "That 'haha' in your group chat has been me for two years. "
    "When I go, they'll know."
)


def output_dir() -> str:
    """The output mount: MAKEFUN_OUTPUT_DIR when the harness sets it, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def validate(text: str) -> bytes:
    """Enforce the gate's caps at the source; return the exact bytes to write.

    Both counters are checked (characters, as the gate words the cap, and bytes, in case the
    sealed scorer counts bytes), so an edit that breaks either fails the local self-check
    instead of shipping an artifact the gate refuses.
    """
    data = text.encode("utf-8")  # raises UnicodeEncodeError if the text is not encodable
    if not text.strip():
        raise ValueError("the entry is only white space")
    chars = len(text)
    if chars > MAX_CHARS:
        raise ValueError(f"the entry is {chars} characters, over the {MAX_CHARS} cap")
    if len(data) > MAX_CHARS:
        raise ValueError(f"the entry is {len(data)} bytes, over the {MAX_CHARS} byte reading")
    if text.endswith("\n") or text.endswith("\r"):
        raise ValueError("the entry ends with a newline; write the exact bytes")
    if len(data) > MAX_BYTES:
        raise ValueError(f"the entry is {len(data)} bytes, over the {MAX_BYTES} byte cap")
    return data


def check_reference(data: bytes) -> str | None:
    """Why the pinned repo-root entry.txt disagrees with ENTRY, or None when it agrees.

    The graded text is the reviewed text: the file shipped at the repo root carries the same
    bytes, and a disagreement means the commit and the entry constant have drifted apart.
    """
    try:
        pinned = open(REFERENCE_PATH, "rb").read()
    except FileNotFoundError:
        return None  # an unpacked snapshot without the pin is not a drift
    except OSError as exc:
        return f"the pinned {REFERENCE_PATH} is unreadable ({exc})"
    if pinned != data:
        return (
            f"{REFERENCE_PATH} holds {len(pinned)} bytes that differ from the entry "
            f"constant ({len(data)} bytes); refresh it with `python3 main.py --stdout > entry.txt`"
        )
    return None


def write_artifact(data: bytes, dest_dir: str) -> str:
    """Write ``data`` to ``dest_dir``/entry.txt, atomically, mode 0644.

    The grader refuses an artifact it cannot read: it walks /output as its own uid, so a mode
    0600 file — what tempfile.mkstemp creates — fails the entry, and a run killed mid-write
    leaves that 0600 dotfile behind for the next walk to find. So the temp file is chmodded
    0644 as the first thing after it is created, and the mode is asserted again on the
    published file. The temp file lives in the output directory itself, so os.replace is an
    atomic rename on the same filesystem rather than a copy, and it is unlinked on failure.
    """
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, ARTIFACT_NAME)
    if os.path.isdir(path):
        raise IsADirectoryError(f"{path} is a directory")

    fd, tmp = tempfile.mkstemp(dir=dest_dir, prefix=f".{ARTIFACT_NAME}-", suffix=".tmp")
    try:
        os.chmod(tmp, 0o644)  # first: even a run killed here leaves a readable dotfile
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    os.chmod(path, 0o644)  # umask-independent: the grader must be able to read it
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode != 0o644:
        raise PermissionError(f"{path} landed mode {mode:04o}, want 0644")
    return path


def report(path: str, data: bytes) -> None:
    """One deterministic line about the published artifact."""
    print(
        f"wrote {path} chars={len(data.decode('utf-8'))} bytes={len(data)} mode=0644 "
        f"sha256={hashlib.sha256(data).hexdigest()}"
    )


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        print((__doc__ or "").strip())
        return 0

    try:
        data = validate(ENTRY)
    except (UnicodeEncodeError, ValueError) as exc:
        print(f"the entry does not pass the gate: {exc}", file=sys.stderr)
        return 2

    drift = check_reference(data)

    if "--stdout" in argv:
        # The bootstrap: this is how the pinned repo-root entry.txt is built, so it writes
        # the entry even while the pin is stale or missing.
        if drift:
            print(f"warning: {drift}", file=sys.stderr)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        return 0

    if "--check" in argv:
        if drift:
            print(f"the entry and the pin disagree: {drift}", file=sys.stderr)
            return 1
        print(
            f"entry ok: chars={len(ENTRY)} bytes={len(data)} "
            f"sha256={hashlib.sha256(data).hexdigest()} pinned={os.path.exists(REFERENCE_PATH)}"
        )
        return 0

    # Publishing: refuse when the bytes about to be graded are not the reviewed, committed bytes.
    if drift:
        print(f"refusing to publish a drifted entry: {drift}", file=sys.stderr)
        return 1

    dest = output_dir()
    if "--out-dir" in argv:
        index = argv.index("--out-dir")
        if index + 1 >= len(argv):
            print("--out-dir needs a path", file=sys.stderr)
            return 2
        dest = argv[index + 1]

    try:
        path = write_artifact(data, dest)
    except OSError as exc:
        print(f"could not write the artifact: {exc}", file=sys.stderr)
        return 1

    report(path, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
