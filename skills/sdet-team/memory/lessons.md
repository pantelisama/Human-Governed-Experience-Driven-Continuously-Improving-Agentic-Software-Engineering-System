# Lessons

Generalised, recurred, and kept. A correction reaches this file only after it has appeared
more than once — candidates live in `corrections.md`. The rules for promotion are in
`references/learning.md`.

Each entry: the principle, why it exists, and what it cost to learn.

---

## L1 — Count what the reviewer reads

A generated document contains rows the source does not. Checking the source can report
clean on a document full of the defect.

**Cost.** The team ran `grep -c 'bool(' test_*.py`, got zero, and reported the finding
closed. The reviewer found 68 `bool(x) == True` rows in the same PDFs, because
the report generator wraps every bare `assert x`.

**Applies to.** Any rule about a rendered artefact rather than the code that produced it.
Both checkers under `rag/` read the rendered evidence for this reason.

---

## L2 — A fix that satisfies the rule can preserve the defect

Check a fix against the principle, not against the rule it was written to clear.

**Cost.** Twice. `bool(x) == True` became `x = name if cond else None; assert x == name` —
no `bool()`, same empty record. Then five name echoes became one `opened == groups`, whose
two sides the test still built from the same literal.

**Applies to.** Every fix to a finding. `references/principles.md` has the four properties
to check against.

---

## L3 — When a check has one source of truth, record the value

Do not manufacture a second operand to satisfy a two-origin rule.

**Cost.** Four rewrites of one step, alternating between two rules. A step asking whether
a binary exists has no independent second source — the build either produced the file or
it did not. Forcing a comparison shape dressed up a presence check and each rewrite
tripped the other rule.

**Applies to.** Existence checks, resolution checks, anything where the specification
cannot disagree with the observation. A finding that returns after every fix is usually
this.

---

## L4 — An auditor reads step by step

Evidence filed under a neighbouring step does not count, however correct it is.

**Cost.** Six findings across two rounds. The drift check sat under "both runs report the
same delay"; the feed checks sat under the When; the registration count sat under a step
about `sample_age` values.

**Applies to.** Any BDD suite. Where a Given claims something only the run can show, move
the *claim* into a Then — the assertion cannot move up.

---

## L5 — Every quantity a step names has to reach the record

Not every word: the numbers, identifiers and literals the sentence commits to.

**Cost.** A step reading "an injected delay of 60 samples, fed as 13 batches of 128
samples" produced a row showing `(60, 128)`. The 13 was parsed, stored, and never
compared. The auditor asked how 13 was proved.

**Applies to.** Every step sentence. Rule B5 in `references/qa-findings.md` checks the
mechanical part.

---

## L6 — A check that passes on broken input certifies the defect

Feed a new check something known to be bad and confirm it fires, before trusting it.

**Cost.** the empty-cells evidence check globbed a sidecar the renderer never wrote. It scanned
zero files and reported zero findings on every run, while a human found real empty cells in
the same documents.

**Applies to.** Every deterministic check. Both checkers under `rag/` exit `2` rather than
`0` when they cannot parse what they were given.

---

## L7 — A fix for "cannot fail" is the likeliest place to write another one

Check every fix against the defect class it closes, not only against the finding.

**Cost.** One session, five findings of the form "this assertion cannot fail". Three of
the fixes written to close them could not fail either: two sides sliced from one
expression, a guard on a call that already raises, a comparison whose operands both read
one config key. A fourth restated a length the previous line had guaranteed. All four
passed, all four reached the evidence document as PASS rows, and each was found only by
the next review round — three rounds to converge on one suite.

**Why it recurs.** Writing an assertion that records a value feels like the fix, so the
question asked is "does this record something" rather than "can this fail". Those come
apart exactly where the defect lives.

**Applies to.** Any change closing a finding about verification strength. Before moving
on: name the input that makes the new assertion fail. If naming it is hard, it cannot.
`rag/check_source.py` A6 and A7 catch two of these shapes mechanically.
