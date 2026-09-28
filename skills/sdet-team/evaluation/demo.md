# The loop, end to end

One traversal of correction → experience → recurrence → recommendation → approval →
evaluation → version, using what actually happened on this repo rather than an invented
example.

It is here because every other file describes one stage. This shows the stages connecting,
and each step names the file that holds it.

## 1. Execution, and a wrong verdict

The team was asked whether the `bool(x) == True` finding was closed. It ran
`grep -c 'bool(' test_*.py`, got `0`, and reported `VERIFIED`.

Recorded as a trajectory — `references/trajectory.md` has the shape. The defect is one
line of it: `retrieval.project_knowledge: [test_signal_sync.py]`.

## 2. Human correction

> "68 of them, in the PDFs."

The highest-value signal the team gets, and the one it would otherwise discard.

## 3. Reflection

`references/reflection.md`, question 4 — which cause? Not missing knowledge; the rule was
understood. **Poor retrieval**, in the literal sense: the rows exist only in the rendered
output, because the generator wraps every bare `assert x`.

## 4. Experience

Generalised, not transcribed. Verbatim it is "grep the HTML", which helps on one task.
The principle is:

> Count what the reviewer reads.

Filed as candidate `C1` in `memory/corrections.md` — one occurrence changes nothing yet.

## 5. Recurrence

It happened again: a check globbed a sidecar the renderer never wrote, scanned zero files,
and reported zero findings on every run while a human found real empty cells in the same
documents. Same cause, different rule. `C1` promoted to `L1` in `memory/lessons.md`.

Two occurrences is what earns promotion. One is a coincidence.

## 6. Recommendation

`references/optimization.md` asks *what capability is missing*, across the whole range —
not *do we need an agent*. The answer here was a deterministic check, because the property
is computable: count matching rows in the rendered evidence.

That is the branch the spec cares about. Under `references/governance.md`'s format, with
`observed_frequency: 2` and the 68 rows as evidence.

## 7. Human approval

A person approved it. The team did not approve it for itself, and could not have.

## 8. Evaluation

The rule is not credible because it exists. A worktree at `<baseline-commit>` — the state QA's
first two reports were written against — is the known-bad corpus, and the checker
reproduces the reviewer's hand count:

```
R2  bool(x) == True     68     the figure QA counted by hand
R11a orphaned rows     137
R3  value vs itself     12
```

`evaluation/benchmarks.md` has the full table. A rule that cannot find its own defect class
in that corpus has not been demonstrated, and `references/evaluation.md` says why a check
that passes on broken input is worse than no check.

## 9. Version

`evaluation/versions.md`, v0.2. Changes, driver, evidence, measurement, rollback.

## What this demonstrates, and what it does not

**Does.** A correction became a principle, the principle became executable, and the
executable reproduced a number a human counted independently. That last step is the whole
argument — the alternative is a system that claims improvement and cannot be checked.

**Does not.** It is one traversal, not a rate. The claim that matters —
`references/evaluation.md`'s human correction rate falling over time — needs many tasks
and is not yet measured. Saying so here is the point; a demonstration that overstated
itself would be the same defect the checkers exist to catch.
