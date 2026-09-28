# Regression

A change that fixes one thing and breaks another is not an improvement. This is the guard.

## Before accepting a change to the team

```
old → the benchmark task set → record
new → the same set → record
compare
```

Specifically:

1. **The known-bad corpus still reports the same counts.** `benchmarks.md` has them. A
   new rule that changes an old rule's count has interacted with it.

2. **The current evidence still reports clean.** A rule that fires on correct code is a
   regression even if it catches something new — see `patterns.md` P-02, which happened
   three times.

3. **The suites still pass.**
   ```bash
   uv run pytest <suite> -q          # 12 passed
   uv run pytest <report-generator> <bdd-test-harness> -q
   ```

4. **The reports still render.** A CSS or template change can clip a column without
   failing anything: 28 cells were clipped and every test passed.

## Known interactions

Rules that have pulled against each other, so a change to one needs the other re-checked:

| | |
|---|---|
| R3 and B5 | an existence check satisfies one by violating the other — `lessons.md` L3 |
| R2 and P2 | both fire on a bare truthiness; fixing for one usually clears both |
| R11b and column widths | widening a column changes what the PDF clips |
| A1 and A5 | both read comprehensions; a change to `_registrations` moves both |

## What a regression looks like here

Not a test failure — those are loud. It looks like: a rule that quietly stops finding its
defect class, a check that starts exiting 0 because its parser no longer matches the
markup, or a document that renders without the column a reviewer needs.

All three have happened. The first two are why the checkers exit `2` rather than `0` when
they cannot parse their input.
