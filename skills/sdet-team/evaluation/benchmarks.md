# Benchmarks

Representative tasks, used to compare the team before and after a change. Reasoning in
`references/evaluation.md`.

## The known-bad corpus

The only corpus that provably contains the defects:

```bash
git worktree add /tmp/qa-baseline <baseline-commit>
cd /tmp/qa-baseline
# link the datasets and the built binary from the working clone
uv run pytest <repo>/tests/bdd_tests/unit_tests/test_suites/<suite> -q
uv run python -m <report_generator> <repo>/tests/bdd_tests \
    -c <component> --test-level unit_tests
python <skill>/rag/check_evidence.py artifacts/.../bdd/unit_tests
```

Expected on that baseline:

| Rule | Findings |
|---|---|
| R1 Expected from the measured side | 7 |
| R2 `bool(x) == True` | 68 |
| R3 value compared against itself | 12 |
| R5 claim with no assertion | 1 |
| R11a orphaned rows | 137 |
| R12 header does not identify the document | 7 |

The 68 is the reviewer's hand count. A change that alters these numbers has changed what
the checker detects, and the change needs a reason.

## Task set

Each of these has been done at least once, so "before" is measurable:

| Task | What it exercises |
|---|---|
| review generated BDD evidence | `workflows/report-review.md`, both checkers |
| trace a finding to its assertion | `references/qa-rag.md` traceability |
| investigate a failing scenario | `workflows/investigation.md` |
| strengthen a step whose claim is unevidenced | rule B5, `workflows/test-design.md` |
| review a diff touching the report generator | routing, `workflows/review.md` |
| decide whether a threshold has a source | R7, routes to `test-efficacy-auditor` |
| run the suite where the backend does not build | `references/capability-discovery.md` |

## What to record

For a change under evaluation, on the tasks it should affect:

```
findings caught        against the baseline
false findings         rows a human then dismissed
specialists spawned    and whether each changed the verdict
tokens                 for the same task, before and after
could-not-run          anything the environment prevented
```

Both numbers, not just the flattering one.


## The known-defect replay

Every defect that reached a human reviewer, reduced to the rows that carried it, with the
corrected form beside it. A rule is credited only when it fires on the defect **and stays
silent on the fix** — a rule that fires on both detects nothing, it just always complains.

```bash
python3 rag/test_known_defects.py     # exit 0 = every known defect is caught
```

| Case | Rule | Filed by hand as |
|---|---|---|
| D1 count-as-evidence | P3 | *"SCN-86 step 2 still has len(ctx.config) > 0 with Actual 7"* |
| D2 absolute path | P4 | *"repo relative binary path instead of /home/<user>/..."* |
| D3 uneven coverage | P5 | *"parameter table for every test, not only 84 and 91"* |
| D4 record dumped as value | P6 | *"`"peak" in final` prints the entire batch record"* |

D4 is why the replay exists. Three rules were written, reviewed and believed to cover the
session's findings; the replay was built afterwards and showed D4 was caught by nothing —
R11b sees that dump only when the PDF happens to clip it, so a record that fits the column
passed every rule. P6 was written because the harness said so, not because anyone noticed.

**Add a case here whenever a human files a finding the checkers missed.** That is the
only evidence that the team learned something, as opposed to a rule being added and
assumed to work.
