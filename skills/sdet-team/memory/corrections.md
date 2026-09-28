# Corrections

Candidate lessons. A human corrected the team; the correction is recorded generalised, not
verbatim, and promoted to `lessons.md` once it has recurred. Rules in
`references/learning.md`.

Each entry: what was said, what the cause was, and the generalised form.

---

## C1 — "grep the source" reported clean on a defective document

**Correction.** The team reported the `bool()` finding closed; the reviewer found 68 rows.

**Cause.** Poor retrieval, literally: the check read the wrong artefact.

**Generalised.** Count what the reviewer reads.

**Status.** Recurred (it shaped both checkers). Promoted — `lessons.md` L1.

---

## C2 — "All I asked was to drop the &"

**Correction.** A one-character request answered with +60 lines defending a failure mode
that could not occur. Later cut by 38 lines.

**Cause.** Speculative abstraction at authoring time.

**Generalised.** The requested scope is the deliverable. A guard for a condition that
cannot arise is not defensive, it is noise.

**Status.** Single occurrence, but it is why `minimal-change-reviewer` exists.

---

## C3 — Findings filed against evidence, answered in the test

**Correction.** "the test code here is better than its evidence ... Fixing the report
would improve this scenario more than fixing the test would."

**Cause.** The team treated every finding as a test defect.

**Generalised.** A test can be correct and its record still evidence nothing. Ask which of
the two the finding is about before fixing either.

**Status.** Recurred across three review rounds. Promoted in substance — it is the premise
of `workflows/report-review.md`.

---

## C4 — "how do you prove 13 batches were fed?"

**Correction.** A step naming three quantities produced a row showing two.

**Cause.** The team checked that a step had *an* assertion, not one per claim.

**Generalised.** Every quantity a step names has to reach the record.

**Status.** Promoted — `lessons.md` L5, and rule B5.

---

## C5 — "when I say run a test suite, do it immediately"

**Correction.** A request to run the first reviewed suite was answered with reading, planning and
questions before anything executed.

**Cause.** The team treated an instruction as a topic to prepare for.

**Generalised.** "Run X" is an instruction. Run it, in the background with output to a
file, and diagnose from the failure. Preparation that delays the first execution is the
cost, not the care.

**Status.** New. It is the opening section of `workflows/test-environment-setup.md`.

---

## C6 — "you ran them locally; I asked for the device"

**Correction.** A suite was run on the host and reported as done, when the device was meant.

**Cause.** The team did not establish the execution environment before running, and the
report did not name where it ran.

**Generalised.** Name the environment in the report, always. Where the user has named one,
run there; substituting the other and not saying so is a false record.

**Status.** New. Step 0 of `workflows/test-environment-setup.md`.

---

## C7 — a refused command retried seven times, then worked around

**Correction.** "It is impossible that you cannot run them" — after the same blocked command
had been reissued repeatedly, and then attempted by hand through the tool the gate sat in
front of.

**Cause.** The team read a permission refusal as a transient failure rather than an answer,
and its own diagnosis ("non-interactive session") was contradicted by every other command
in the session succeeding.

**Generalised.** A refusal is a result. Do not retry it unchanged, do not hand-run the step
it blocked, and never write your own allowlist entry. Finish everything unblocked, then
hand over the exact command.

**Status.** New. Step 7 of `workflows/test-environment-setup.md`.

---

## C8 — "it's been stuck for ages" — it was not stuck, and later it was

**Correction.** A build reported as progressing was blocked on a Windows filesystem
crossing; a later one was in state `T`, stopped by a stray Ctrl+Z, and would never have
finished.

**Cause.** The team watched elapsed time instead of measuring the process. `wchan`,
`utime`/`stime` and the context-switch counters answered it in seconds, once asked.

**Generalised.** A slow run is a diagnosis, not a wait. Read `/proc/<pid>` before
attributing slowness to size, and check for state `T` before assuming work is happening —
stopped processes also hold build-tree locks that block every later attempt.

**Status.** New. Step 5 of `workflows/test-environment-setup.md`.

---

## C9 — "all fixed?" answered yes three times while three findings were still open

**Correction.** Asked "are you 100% sure they are all fixed?", the team answered yes. A
reviewer then named three findings still live in the evidence: `len(ctx.config) > 0`
rendering "Actual 7", a dataset guard checking three names where the scenario used two,
and a parameter table missing from three of seven scenarios. The RAG, the evidence
checker and a clean agent had all been available the whole time.

**Cause.** Verification confirmed the **presence of the new text** instead of the
**absence of the old pattern**. `grep -c '<the thing I just wrote>'` returns 1 and proves
only that the edit landed. The finding asked for a row to be *deleted*; nobody ever
grepped for the row. The same shape hid the other two: a passing assertion message was
matched instead of the guard behind it, and a per-scenario requirement was checked on the
two scenarios already known to satisfy it rather than on all seven.

Two aggravators. `rag/check_evidence.py` found both remaining defects in one run, but was
run *after* the "yes" — it was treated as a final flourish rather than the gate. And a
repeated "are you sure?" was read as a request for reassurance instead of as evidence that
something had been missed.

**Generalised.** A fix that removes something is verified by the **absence** of the old
pattern in the generated artefact, never by the presence of the replacement. Before
claiming a finding closed, state the string that must no longer appear and show a zero
count for it. For a finding phrased "every X", enumerate every X and show the per-item
count — checking the ones already known to pass proves nothing. Run the checkers *before*
the claim, not after; exit 0 is the evidence, a self-written grep is not. And treat a
repeated "are you sure?" as a defect report: stop asserting and re-derive from the
artefact.

**Status.** New. `references/verification.md`, negative-verification rule.

---

## C10 — "many were fake declarations"

**Correction.** After several rounds of reporting findings fixed: "many were fake declarations". The fixes were announced as closed while the assertions still could not
fail. This is C9's failure a second time, on a different suite.

**Cause.** The team checked that each fix ran green. Green is what the defect already
produced, so it distinguishes nothing. Three of five fixes in that session were
themselves assertions that could not fail -- two sides sliced from one expression, a
guard on a call that already raises, a comparison whose operands both read one config
key -- and each was found only by the next review round.

**Generalised.** A fix to a "cannot fail" finding is closed when a named mutation makes
it fail, not when the suite passes. State the mutation and its result, or leave the
finding open.

**Status.** Recurred (C9 was the same class). Promoted -- `lessons.md` L7, the sign-off
gate in `SKILL.md`, and `check_source.py` A6/A7/A8, which catch three of these shapes
mechanically.

---

## C11 — a gate test passed on a row the renderer never writes

**Correction.** Reviewer: the empty-cells test built its no-assertion row by hand as one
dash cell; the template writes "no assertion recorded / n/a / n/a". The gate missed the
real row while its test said the case was caught. The gate's tests also ran in no CI task.

**Cause.** The fixture copied the generator from memory, not from the generator.

**Generalised.** A fixture standing for generated output is derived from the generator
(template, renderer), or it tests markup that never exists. And a gate is a gate only
where CI runs it: check the task that executes a new test before calling it a guard.

**Status.** New. The same gap is in `rag/check_evidence.py` B1, which counts "no assertion
recorded" as an assertion -- proposed fix, awaiting approval.

---

## C12 — the harness compared with itself

**Correction.** Reviewer, two findings on one suite: a harness-printed "injected" flag was
compared with the harness-printed input flag, both from one local; and a harness-counted
`ingested_batches` equalled the batch lines by construction. The evidence showed both as
checks of the block.

**Cause.** A value the harness prints about its own inputs was treated as an independent
side.

**Generalised.** Expected comes from what the test knows (Given, document, dataset
length); Actual from what the element reports. A harness echo, or a count the harness
loops over, compared with another harness value is true by construction -- remove it or
replace it with a count the step derives itself.

**Status.** Recurred (C10's "cannot fail" class, across the process boundary). Candidate
for promotion to `lessons.md` L7 and a `check_source.py` rule.

---

## C13 — a guard nothing runs, with checks that cannot fail

**Correction.** Reviewer: an evidence-regression script was called by no task, pipeline or
test; two of its checks matched a token that appears elsewhere on every page ("-1" in the
scenario id, a bare "7" in the step-number column).

**Cause.** Written as a guard, never wired as one; patterns matched the page, not the cell.

**Generalised.** An unrun check is not a guard: wire it into CI or delete it. A text check
matches the cell it means, never the whole page.

**Status.** New.

---

## C14 — predicted a tool's output without reading the tool

**Correction.** "Which deviations? I don't understand." The team had said step-text
changes would show as deviations in the traceability cross-check. That tool compares
only identifiers (the test case exists, its requirement is traced); it never reads step text.

**Cause.** Inference from the tool's name, stated as fact.

**Generalised.** Before stating what a check will report, read what it compares. If it has
not been read, say so instead of predicting.

**Status.** New.

---

## C15 — asked what is missing, answered with what to add

**Correction.** "Don't tell the dev what to add; say what is missing for the test to be
covered." Then: "what is missing in the production code?"

**Cause.** A gap analysis was delivered as an implementation plan, and its scope drifted
from the production code to process.

**Generalised.** When asked what is missing, list the gaps against the requirement and the
scenario, scoped to what was asked, and leave the design to the owner.

**Status.** New.
