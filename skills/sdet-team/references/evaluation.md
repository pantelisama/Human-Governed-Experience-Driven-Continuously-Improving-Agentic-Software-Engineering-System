# Evaluation

A change is an improvement when it demonstrably improves something. Sounding better is not
evidence.

## What to measure

Pick the ones the change is supposed to move. Measuring everything is its own waste.

| Measure | Read from |
|---|---|
| findings caught | `rag/check_evidence.py` on a known-bad document set |
| false findings | the same run, counting what a human then dismissed |
| human correction rate | `memory/corrections.md` over time |
| findings that returned | a finding reported closed and filed again |
| regression | `evaluation/regression.md` |
| token use | tokens for a benchmark task, before and after |
| specialists spawned | how many, and whether each changed the verdict |

The two that matter most here are **findings caught** and **false findings**, because they
pull against each other: a checker that flags everything catches everything and is
useless.

## The baseline that exists

The checkers were measured against the documents QA actually reviewed — a worktree at
`<baseline-commit>`, the state their first two reports were written on:

| Rule | QA baseline | After the fixes |
|---|---|---|
| R1 Expected from the measured side | 7 | ok |
| R2 `bool(x) == True` | **68** | ok |
| R3 value compared against itself | 12 | ok |
| R5 claim with no assertion | 1 | ok |
| R11a orphaned rows | 137 | ok |
| R12 header does not identify the document | 7 | ok |

The 68 is the figure QA counted by hand. Reproducing it is what makes the checker
credible — it reads the documents the way the reviewer does.

Keep that worktree recipe: it is the only known-bad corpus, and a new rule that cannot
find its own defect class in it has not been demonstrated.

## Before accepting a change

```
old → benchmark
new → benchmark
compare
```

Both numbers, not just the new one. A change that catches more findings and also flags
five correct rows has not obviously improved anything — that trade is the user's call, not
the team's.

## False positives cost more than they look

A standing false positive teaches people to skim the output, and the next real finding
gets skimmed with it. Three of the checker's rules were narrowed after they fired on
correct code:

- **R5** flagged a step whose evidence was carried by correctly-named derived variables;
- **A1** flagged a filter selecting on monotonicity while the assertion checked a value —
  two properties of one field;
- **R11b** flagged wrapped cells as truncated three times before the check compared
  against the sidecar instead of pattern-matching layout output.

Each was a rule applied outside its principle. `principles.md` has the general form.

## Feed the check known-bad input

From the audit checklist, and the reason it is there: the empty-cells evidence check globbed a
sidecar the renderer never wrote. It scanned zero files and reported zero findings on
every run, while a human found real empty cells in the same documents.

> A check that passes on broken input is worse than no check — it certifies the defect.

So a new rule is not done until it has been shown to fire. The checkers exit `2` rather
than `0` when they cannot parse what they were given, for the same reason.
