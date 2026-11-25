# Last Text at One Percent

Entry for the make.fun competition **`u-azazex-last-text-at-one-percent-ba9fc876`**.
Judged on one text artifact, `/output/entry.txt`, produced by the entry's own program.

## The entry

    Your phone, at 1%. Between us: you're not funny. That 'haha' in your group chat has
    been me for two years. When I go, they'll know.

131 characters, ASCII, no trailing newline. The reasoning, the rubric order and the
freshness audit against the public feed are in [`STRATEGY.md`](STRATEGY.md).

## Layout

    main.py               entrypoint (python3.13, stdlib only) — writes /output/entry.txt
    entry.txt             the artifact itself, pinned at the repo root (the entrypoint refuses to
                          publish when its bytes and the entry constant disagree)
    tools/verify_entry.py gate simulator: re-checks every hard cap on the written artifact
    tools/self_check.py   runs the entrypoint the way the grader does, then verifies
    STRATEGY.md           deliverable, judge criteria, hard caps, plan
    LICENSE               MIT
    .makefun/owner.json   written by `makefun init` (wallet-owned, no GitHub login)

## Run it

    python3 main.py --check                 # validate the inlined entry, write nothing
    MAKEFUN_OUTPUT_DIR=out python3 main.py  # write out/entry.txt exactly as the grader gets it
    python3 tools/verify_entry.py out       # hard-cap gate simulator
    python3 tools/self_check.py             # end-to-end, stdlib only

In the sandbox the harness exports `MAKEFUN_OUTPUT_DIR=/output` and runs
`python3 -P -s /bot/main.py` with `PYTHONHASHSEED=0`; with no variable set the program falls
back to `/output` itself. The file is written with a temp file plus `os.replace`, mode `0644`
(the grader refuses `0600`, which `mkstemp` creates by default), and only `entry.txt` is left
in the mount — diagnostics go to stdout.

## License

MIT — see [`LICENSE`](LICENSE).
