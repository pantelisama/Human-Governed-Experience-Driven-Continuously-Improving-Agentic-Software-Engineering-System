# What makes an evidence row weak

`qa-findings.md` lists the patterns QA has already filed. This file is the layer under
it: the properties that *generate* those patterns. A new defect nobody has named yet will
almost always be one of these four, wearing different clothes.

Use this when the checker reports nothing and you still have to sign off, and when a
reviewer raises something that matches no existing rule. A finding that fits a principle
but no rule means the rule set needs an entry — write it into `qa-findings.md` with the
wording the reviewer used.

---

## P1 — Both sides of the comparison come from the same place

A verification row is worth something only when two **independent** origins agree: one
from the software, one from the specification.

Ask of any row: *where did Expected come from, and where did Actual come from?*

| Expected's origin | Actual's origin | Worth |
|---|---|---|
| the scenario, a requirement, a data file's own metadata | the software under test | evidence |
| a literal in the test | the software | evidence, if the literal traces to a specification |
| the test's own variable | the software | **weak** — see below |
| the same run that produced Actual | the software | **worthless** — it cannot disagree |

The shapes QA has filed under this — `x == name`, `opened == groups`,
`expected` computed from `flagged`, a hardcoded lag copied from observed behaviour, a
threshold chosen to sit between two measurements — are all one principle.

**Mechanical tell:** the Expected cell's value appears as a literal in the assertion text.
That means the test wrote both sides. It is not proof (`batch_size == 128` is legitimate
when 128 is in the scenario), but it is where to look. 48 of the current 187 rows have
this shape; each needs an answer to "where did the 128 come from?"

**The question that settles it:** *could this row have rendered differently if the
software were wrong?* If no, the row evidences nothing.

---

## P2 — The row does not carry the value it checked

The record exists so a reviewer who was not there can see what happened. A row that
records only that a comparison succeeded fails at that.

`bool(x) == True`, `Expected True / Actual True`, `in collection`, an operator with no
value, a list elided to `[1, 3, 4, ...]`, a type name (`H5DataSource`) where a value
belongs — all the same principle: **the number is missing.**

**Mechanical tell:** the Actual cell contains no digit and is not a recognisable value
(22 of 187 rows). Or Expected and Actual are both `True`.

**The question:** *reading only this row, can I say what the software produced?*

---

## P3 — The claim and the evidence are not the same claim

Every step sentence is a claim. Every Acceptance Criterion clause is a claim. The
assertions under them are the evidence. They drift apart in both directions:

- the step claims something no assertion checks (a Given claiming fault state,
  asserting a batch count);
- an assertion checks something the step never claimed (a 0.999 floor under a step that
  says 0.9), so the record understates what was verified;
- the evidence sits under the neighbouring step;
- the AC names a relationship and the test checks three separate literals;
- the AC names a condition the harness cannot produce.

**Mechanical tell:** partial. Extracting the nouns from a step sentence and looking for
them in its assertions catches the blatant cases. The AC ones need reading.

**The question:** *take the sentence and the rows under it — does one substantiate the
other, in both directions?*

---

## P4 — The row cannot distinguish a pass from a failure

The end state of the other three. A row that would look the same whatever the software
did is decoration.

- an assertion whose collection is selected by the property it then asserts;
- a run compared against itself (`total_rise=0.0`);
- an `all()` over a list that may be empty;
- a check for a state only a different component can set;
- two rows that render identically, so neither says which case it covered.

**Mechanical tell:** none that is general. This is what mutation testing answers — break
the property, confirm the row turns to FAIL, restore.

**The question:** *what would have to be broken for this row to fail? If the answer is
"nothing realistic", it is not verification.*

---

## When two principles pull against each other

P1 (two independent origins) and P3 (the claim and the evidence must match) can conflict,
and chasing both in turn produces a loop. A measured case:

SCN-2 step 1 reads *"the <production_unit> test binary is compiled and available"*.
The step names the production unit; the built artefact is `<test_binary>`. Satisfying
P3 — put `<production_unit>` in the row — means writing both names into the assertion, and
then P1 fires, because the test supplied both sides. Satisfying P1 — compare only what
the build produced — drops the unit name and P3 fires. Four rewrites, alternating.

The resolution is to ask which principle the row can actually serve. **There is no second
source here**: the build either produced the file or it did not, so nothing independent
exists to compare against. P1 cannot be satisfied at all, and forcing the shape only
dresses up a presence check. So the row records the binary it looked for, and the failure
message carries both names.

**The rule: when a check has only one source of truth, P2 is what it can serve — record
the value. Do not manufacture a second operand to satisfy P1.** A finding that returns
after every fix is usually this: the rule is being applied where the principle does not
reach.

## Using these on an unknown finding

When something appears that matches no rule in `qa-findings.md`:

1. Which principle does it violate? If none, it may not be a finding — say so and say
   why, rather than fixing something to make a reviewer comfortable.
2. Can it be detected mechanically? If yes, add a rule to `check_evidence.py` and a
   section to `qa-findings.md`. If no, name the specialist who judges it.
3. Feed the new check a document you know is bad and confirm it fires. A check that
   passes on broken input certifies the defect — that is exactly how
   the empty-cells evidence check scanned zero files and reported clean for months.

## Where the checker cannot reach

Read from the rendered evidence alone, three of the four principles are only partly
decidable:

- **P1** needs to know where a number came from — specification, compiled constant, data
  file, or observation. That is `test-efficacy-auditor`'s judgement, and QA marked this
  class **critical**.
- **P3** needs the Acceptance Criteria split into clauses and matched against assertions.
  That is reading, not regex.
- **P4** needs mutation: break it, run it, confirm the row fails.

So the checker is the floor, not the ceiling. It catches what recurs. The principles are
what the lead and its specialists carry for everything else.
