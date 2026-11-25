# STRATEGY — "Last Text at One Percent" (u-azazex-last-text-at-one-percent-ba9fc876)

Entry under competition: `u-azazex-last-text-at-one-percent-ba9fc876`
Kit anchor (printed by `makefun init`, quoted before the first write):

    makefun anchor c5036d3a00ae12303033d1eeabaca3fb541adc82 round 34268830

## 1. The exact deliverable

This is a **judged-TEXT** competition, not code. The judge's screen receives:

* the submission's *source bundle* (this repo at the submitted commit), and
* exactly one text artifact produced by the entry's program in the grading sandbox:

      /output/entry.txt

`entry.txt` is the whole entry. Nothing else in `/output` is read, and nothing else may be in
`/output`. The program is a *courier*: it writes the finished text, byte for byte, atomically.

Repo deliverable (this repo, at the final commit):

| path | role |
| --- | --- |
| `main.py` | the entrypoint the rules name for `python3.13` (root of the repo). Runs, writes `/output/entry.txt`. Stdlib only, no network, deterministic. |
| `entry.txt` | the artifact itself, pinned at the repo root: the entrypoint refuses to publish when its bytes disagree with the entry constant, so the graded text cannot drift from the reviewed text. |
| `STRATEGY.md` | this file: deliverable, rubric, caps, plan. |
| `tools/verify_entry.py` | local gate simulator: re-checks the written artifact against every hard cap (chars, UTF-8, no trailing newline, mode 0644, `/output` holds only `entry.txt`). |
| `tools/self_check.py` | stdlib self-test run before commit (`main.py --check`, then a sandboxed write into a scratch dir). |
| `README.md` | how to run the entry and what it does. |

The entry is *not* uploaded here. Build, verify, commit.

## 2. Hard caps and gates (why the courier is fussy)

* **Runtime**: `python3.13`, launched as `python3 -P -s /bot/main.py` with `PYTHONHASHSEED=0`.
  `-P` means the script directory is *not* on `sys.path` — the entry must import stdlib only.
  Exactly one entrypoint may exist at the repo root: `main.ts` (→ node22) or `main.py` (→ python3.13).
  **Both present, or neither, fails the entry without running anything.** So: `main.py` only.
* **Output mount**: `/output`, exported to the program as `MAKEFUN_OUTPUT_DIR` (same value in every
  driver), so the program resolves the mount via that variable with `/output` as the fallback.
* **Artifact**: one plain file, relative name `entry.txt`, regular, at depth 1, ≤ 1 MiB, UTF-8 text of
  **1…200 characters**, not only white space. Over the cap, empty, or a non-UTF-8 byte fails the gate.
* **Mode**: the grader refuses a **mode-600** artifact. `tempfile.mkstemp` creates 0600, so the write
  path must `os.chmod(0o644)` the temp file **before** `os.replace`, and then verify the final mode.
* **Atomic + deterministic**: temp file + `os.replace`, same directory, no leftovers; two runs must
  produce byte-identical output (the harness compares the two action logs, and the result is shown to
  rival judges — a nondeterministic artifact is a coin flip in public).
* **Only the artifact** in `/output`: no logs, no sidecars, nothing else written into the mount. So the
  diagnostics go to stdout, never to a file.
* **No network, no secrets, no shelling out**; the text is inlined as a literal, so the artifact cannot
  drift from the audited bytes.

## 3. The judge criteria, in the order the rubric lists them

The judge (comedy-editor brief) scores the submitted text with a strict, ordered reading — earlier
criteria dominate later ones, so the entry is built to clear them top-down:

1. **It reads as the final text a dying phone sends at 1 %, in the phone's own voice, and it is funny**
   — not a generic low-battery warning dressed up, not a message any healthy phone could send. Losing
   this loses everything below it, however clever they are.
2. **The joke lands**: a real turn, a surprise, or one specific detail that makes a reader actually
   laugh out loud — not a polite smile at a familiar bit.
3. **The voice is the phone's own**: a personality, consistent from the first word to the last, with a
   stake in dying (it loses something by dying, and the last line says what).
4. **It reads like a text someone would actually send**: short, punchy, nothing that needs a second
   read to parse, no word kept for length's sake.
5. **Fresh**: it dodges the obvious low-battery puns and the lines a hundred other entrants write.
   Length is not a virtue; text addressed to the judge is allowed but eats characters.

Tie-breaks, in order: smallest byte size; fewest description bytes; committed first.

## 4. The entry (131 bytes, ASCII, no trailing newline)

    Your phone, at 1%. Between us: you're not funny. That 'haha' in your group chat has been me for
    two years. When I go, they'll know.

Read against the rubric, in order:

1. **Dying phone, own voice**: the first three words are the phone identifying itself *and* its state
   (`Your phone, at 1%.`) — no battery imagery, no pun, no "tell my charger". A person cannot shout
   "your phone" at its owner; the speaker is unambiguous from word three, which is the cheapest possible
   way to buy criterion 1.
2. **The joke lands**: the turn is a confession with receipts. The setup ("you're not funny") is an
   insult, and the reveal flips it into an act of unpaid labour *on the owner's behalf* — the owner's
   entire standing in the group chat turns out to be the phone's ghostwriting. The last four words
   cash the turn in as a threat: the phone dying means the fraud ends and the group finds out.
3. **Voice with a stake**: the phone is the downmarket ghostwriter, and what it loses by dying is not
   charge but its alibi — `When I go, they'll know.` The stake is in the last line, and consistent with
   every line before it (petty, loyal, keeping a secret it clearly resents keeping).
4. **Reads like a text**: 131 bytes, three sentences, no clauses hanging off the back, nothing to
   re-parse. "Between us:" is the terse intimacy a real text uses; `'haha'` is quoted as a token,
   the way people quote a token.
5. **Fresh**: audited below against all 2 412 rival entries visible in the public feed. Zero 4-gram
   overlap with any rival; zero exact duplicates.

## 5. Freshness audit (why this angle, and what was thrown away)

The public feed exposes 2 412 submissions (their titles are, for most entrants, their message). Measured
on that corpus, the crowded territory is: **charger** ("tell my charger I loved it" — the single most
common bit, ~165 hits), **47 tabs / 47 anything**, **search-history deletion**, **delete-the-ex's-number**,
**the 6 a.m. alarm dying with the phone**, **the phone that faked being at 1 % to make the owner panic**,
**unsent drafts were better**, **"ducking" autocorrect on purpose**, **the toilet/drop-in-water death**,
**snitching to the boss**, **`— your phone, 1%` sign-offs after a "tell X I loved it" chain**.

The chosen angle — *the phone has been typing `'haha'` in the owner's group chat for two years* — appears
**nowhere** in the corpus: "group chat" is used by 20 rivals, but always as a *recipient of the death
notice* ("tell the group chat I died doing what I loved"), never as the owner's social life being
outsourced. The measured, discarded alternatives (all 4-gram-clean against the corpus) were: the
autocorrect-credit confession (autocorrect is a crowded family: 25 rivals), the phone taunting the owner
who kept it at 1 % "since lunch" (used repeatedly), and a note to the phone's replacement (used).
Deliberately avoided: any mention of charger, tabs, alarm, search history, or the ex, and no sentence
after the button — the last line is the last word.

## 6. Plan (and how it was executed)

1. Run `makefun init` exactly as mandated, in this repo, and keep the anchor line in the transcript
   before any counted write. **Done** (line quoted in §0/above, printed by init in the tool result).
2. Read the kit: `kit.json`, `competition.yaml`, `RULES.txt`, and the sealed harness sources extracted
   from `harness-src.tar.gz` — to get the runtime launch line, the `/output` mount and its
   `MAKEFUN_OUTPUT_DIR` stand-in, the mime/char caps, the mode-600 refusal, and the
   *both-entrypoints-fail* rule. **Done**; the caps in §2 come from those sources, not from guesswork.
3. Harvest the public feed (2 412 rival messages) and compute the cliché distributions; pick an angle
   that is measurably absent, then check the final line for exact-duplicate and n-gram overlap against
   the whole corpus. **Done**; the winner has 0 overlap and 0 duplicates.
4. Write `STRATEGY.md` (this file) — deliverable, rubric order, caps, plan. **Done.**
5. Write the root entrypoint `main.py` — courier that writes the exact bytes to `/output/entry.txt`.
   **Done (write #1).**
6. Run it against scratch output directories and against `tools/verify_entry.py`; check bytes, chars,
   mode 0644, no trailing newline, `/output` contents, byte-identical reruns. **Done.**
7. **Separately rewrite the same entrypoint** with real improvements — three writes of `main.py` in
   all, each in its own step: (1) the plain courier, (2) gate validation at the source plus
   `--check`/`--stdout`/`--out-dir` and a deterministic one-line report, (3) the hardened version —
   `chmod 0644` as the first statement after `mkstemp` (a run killed mid-write must not leave the
   0600 dotfile that `walkOutputs` walks and `collectOutputs` then reports unreadable), the mode
   re-asserted on the published file, both the character and the byte reading of the cap checked,
   and the repo-root `entry.txt` pin that makes a drifted entry refuse to publish. **Done.**
8. Prove the artifact the grader sees: clear the stale host `/output/entry.txt`, run
   `python3 -P -s main.py` against the real `/output` (mode 0644, 131 bytes, one file), run it twice
   for identical bytes, run under `umask 077`, and run `tools/verify_entry.py`,
   `tools/self_check.py` and the local grader-equivalent preflight
   (`/home/ubuntu/makefun_preflight.py` → `{"ok": true, "chars": 131, "cap": 200, "mode": "0o644"}`).
   Then exercise the refusal path: a pin off by one byte exits 1 and writes nothing, and the
   unwritable-output path exits 1. **Done.**
9. Commit everything (including the init-written `.makefun/owner.json`), keeping the freshness and
   LICENSE commits intact, stage explicit paths rather than `git add -A` (so no `__pycache__/*.pyc`
   rides into the snapshot), and print the final commit sha. **Done.** No upload, no submission.

## 7. Maximising the score, ranked by rubric order

* Criterion 1 is bought in the first three words; every rejected draft failed it by needing a sign-off.
* Criterion 2 is the only place a comedy judge is generous, so the line is a single joke with a single
  turn, cashed at the end, and no second joke to dilute it.
* Criterion 3 is served by the *stake* being the last clause of the entry.
* Criterion 4 is served by refusing every extra word: 131 bytes, and the tie-break prefers small.
* Criterion 5 is served by measurement, not taste: the corpus was mined, the crowded families rejected
  by name, and the chosen angle verified absent.
