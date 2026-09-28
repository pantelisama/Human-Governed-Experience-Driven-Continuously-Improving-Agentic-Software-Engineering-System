# QA finding patterns — BDD evidence reports

Every finding QA has raised on this project was raised against a **generated evidence
document**, not against source. The checks below are written the same way: they read
`evidence/<scenario-id>.html` and `pytest-assertions.json`, because that is what the reviewer
reads. A pattern that looks fixed in the source can still be present in the record —
the generator manufactures rows the source does not contain.

Sources: three rounds of human QA review of one BDD suite's evidence documents, anonymised.

---

## R1 — Expected rendered from the measured side

**Raised as:** "The Expected column is rendered from the measured side (j2:47). The two
columns can never disagree, so no document in this set can record a failure."

**Symptom in the record:** a `!=` assertion printing the same number in both columns and
passing (`480.8139` in Expected and Actual).

**Rule:** Expected carries the operand the assertion *declared*, prefixed with the
operator when the relation is not equality. Never the observed value.

**Not a violation:** a passing equality showing the same value on both sides. That is
what an equality does. The test is whether a *failing* row renders distinct columns —
check that before reporting this.

**Where it lives:** the report generator's expected-operand rendering.

---

## R2 — Bare truthiness reaches the record as `bool(x) == True`

**Raised as:** "68 `bool(x) == True` assertions … Expected True / Actual True."

**The trap that caused a wrong all-clear:** the count is of *rendered rows*, not of
`bool(` in the source. the generator wraps any bare `assert x` as
`bool(x) == True`. Grepping the source for `bool(` returns zero while the PDF still
shows dozens.

**Check:** `grep -c 'bool(' evidence/*.html`, never the test source.

**Rule:** every assertion compares values. `assert lines` becomes `len(lines) > 0`;
`assert not wrong` becomes `wrong == []` so the offending items print.

---

## R3 — Name echoes: a value compared against itself

**Raised as:** "49 name echoes — they inflate the assertion count and record nothing",
then "25 remain — `present ==`, `ref_file ==`, `ref_group ==` …"

**Shapes seen:**
- `x = name if cond else None; assert x == name` — satisfies "no bool()" literally while
  keeping the defect: the row shows the dataset name twice and the real condition
  (`returncode == 0`, `averages >= 800`) never reaches the record.
- `opened == groups` where both sides were built by the test from the same literal.
- `assert delay == 60` where `delay` was parsed out of the step sentence: this checks
  the feature file says 60, not that the data carries it.

**Rule:** the two sides must come from independent origins — one from the software, one
from the specification. Keying by dataset (`{name: entry["lag"]} == {name: 60}`) is
legitimate *only* when the payload is a measured value; keyed booleans are echoes again.

---

## R4 — The stimulus sits in a precondition

**Raised as:** "Step 1, a Given, runs the binary. Step 2, the When, then repeats
`returncode == 0` … the action happens before the step that claims it."

**Check:** does any `@given` call the harness, directly or through a helper such as
`_config()`? A Given carrying an exit status or an observation count is this finding.

**Rule:** Givens state preconditions. The run belongs in the When.

---

## R5 — The step's claim and its assertions do not match

**Raised as, repeatedly:**
- SCN-5 Given claims "each batch carrying a fault state"; asserted `_N_BATCHES >= 2`.
- SCN-3 step 3 claims "sample_age is 0 on the batch where each sync registers";
  used `sample_age == 0` as a *filter* and asserted only the count.
- SCN-1 step 2 claims a drift was added; asserted only that the magnitude is finite.

**Check:** take the step sentence, extract its nouns (level, lag, fault, audible,
sample_age), and confirm each appears in an assertion under that step.

**Rule:** the evidence for a claim belongs under the step that makes it. Where the
evidence needs data that only exists later (both runs of a pair), give it a Then of its
own rather than filing it under an unrelated step.

---

## R6 — Assertions stronger than the scenario states

**Raised as:** "`_MIN_PEAK = 0.999` … neither the step nor the AC mentions it, so
the record understates what is verified", and the converse for SCN-3, where the AC
states a one-sided floor while the code asserts a two-sided bound.

**Rule:** either the scenario states the bound, or the bound does not belong in the
verification record. A second, tighter floor with no protocol source is an unstated
expectation recorded as though the protocol required it.

---

## R7 — Thresholds and expected values with no stated source

**Raised as:** "`_MIN_AVERAGES = 800` was chosen to sit between two observed
outputs (829 and 573)", and "Expected lags are hardcoded … the dataset metadata is still
never read" — QA marked this one **critical**.

**Rule:** a value the test expects must come from the specification, the compiled
constants, or the data file's own metadata. A number copied from watching the software
makes the test assert the software against itself.

**Worked example (why this matters):** a constant held a lag of `22` samples for one
dataset, taken from observed behaviour. The file's own metadata declared a delay of
**-18** samples. Sweeping the lag from -30 to +30 and ranking by correlation peak
put all six best values at a negative lag. The metadata was right, the hardcoded value
was wrong, and it was masking the only scenario written to exercise a negative delay.

**Check:** for every constant the test compares against, can you name where the number
came from? If the answer is "it is what the code produces", that is the finding.

---

## R8 — Expected derived from the output being checked

**Raised as:** "Both sides come from the same run's output. `flagged` is what the block
reported it received; `expected` is computed from that. If the harness flagged batches 2
and 5 while the block reported 1 and 3, the test would still pass."

**Rule:** the expectation comes from the feed site or the specification, never from the
output under test. Where the harness owns the stimulus, have it emit what it injected so
the step has an independent side to compare against.

---

## R9 — A row that cannot fail

**Raised as:** "The 0.0 row runs the same command twice, so it only fails if the code is
non-deterministic … a quarter of this document's examples evidence nothing."

**Rule:** an example whose two sides are the same input proves nothing about the
behaviour under test. Either drop it or name it a control case and assert what a control
must show — that the two runs agree.

---

## R10 — Vacuous passing

**Raised as:** filters that would pass an empty set. `_valid_batches()` carries an
explicit guard against this and QA noted it approvingly.

**Rule:** any check that filters a collection and asserts over the result must first
assert the collection is non-empty, or a run where nothing happened passes.

---

## R11 — Rendering defects that hide real work

These are generator bugs, and QA weighted them heavily because they make a good test
look like a weak one.

| Symptom | Rule |
|---|---|
| Rows lose Step/Keyword/Description after a page break | Every row carries its step number; the paginator cannot orphan it |
| Value truncated with `…` | The cap must not cut a mapping the step exists to record |
| `<placeholder>` unsubstituted — "the `dataset_file` dataset" | Scenario Outline values resolve from the Examples row |
| Gherkin data table not rendered | The table the step's trailing `:` promises must appear |
| Loop renders source text, so two iterations look identical | Unroll, or key the assertion by what distinguishes the iterations |
| Implementation leaking into the Assertion column (`== _keyed(0, label)`) | Name both operands before the assert; the report prints the source |
| Two identical rows under one step | A step that runs the harness twice labels each call |

---

## R12 — Document identity

**Raised as:** "The header carries no feature-file version, test-source commit or
approval date, so nothing shows the expectations predated the run", and "the source that
produced them is not on `main`".

**Rule:** the evidence header names the test protocol, the template, the full commit SHA
and the branch. Approval date is a human act the generator has not witnessed — it states
that the record is unapproved rather than inventing a date.

---

## R13 — Coverage of failure paths

**Raised as:** "All four examples are happy paths … Nothing tests a drift the filter
cannot reject." Raised against SCN-1, SCN-2, SCN-3, SCN-4 and SCN-6; only SCN-5 exercises a
failure path.

**Rule:** report the absence. Whether a requirement has a failure path to account for is
a question for the requirement owner, not a defect the test can fix on its own.

---

## R14 — Scenario verifies components, not the product's entry point

**Raised as:** "SCN-6 … orchestrates [the filter, window and correlator] itself instead
of calling `SignalAligner::FilterInputs`. A defect in the product's own
orchestration would not be caught."

**Rule:** a scenario that bypasses the production entry point is a recorded regulatory-QA
decision, not something a reviewer should discover in a C++ comment.

---

## R15 — An acceptance criterion that cannot fail here

**Raised as:** "AC and step both say 'no batch reports packetMismatch' … never set
by the calculator this harness drives, so testing for it alone could not fail."

**Rule:** if a named condition cannot arise in the scenario's configuration, the AC
claims verification it does not perform. Assert the wider property that *can* fail, and
say so in the scenario.

---

## Out of scope for these checks

Two findings recur and are **not** code defects:

- **Traceability tags are design-level, not system-level.** The mapping is not agreed; retagging without
  it writes false traceability into a regulated record.
- **UNCONTROLLED banner / "build unknown".** Correct and honest for a local render. It
  means the set cannot be filed as the verification record until regenerated in CI, not
  that something is broken.
