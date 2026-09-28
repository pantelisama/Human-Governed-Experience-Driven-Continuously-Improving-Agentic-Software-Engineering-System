# Failure classification

Every failed verification is classified before anything is repaired. The class decides
the action; repairing before diagnosing is how a pre-existing failure gets blamed on the
current change.

```yaml
failure_class:
  - implementation_defect
  - test_defect
  - requirement_mismatch
  - regression
  - environment_failure
  - tooling_failure
  - flaky_failure
  - pre_existing_failure
  - unrelated_failure
  - insufficient_evidence
```

## The first question

```
              test failure
                   │
     did THIS change cause it?
                   │
         ┌─────────┴─────────┐
       yes                   no
         │                   │
      repair            investigate,
         │              classify, report
     re-verify          — do not fix
```

Never auto-fix a failing test before establishing that the implementation caused it.

| Class | Action |
|---|---|
| `implementation_defect` | repair the implementation |
| `test_defect` | repair the test or its design — never by weakening it |
| `environment_failure` / `tooling_failure` | attempt safe recovery, then escalate |
| `pre_existing_failure` | record with baseline evidence; do not claim causation |
| `flaky_failure` | bounded reruns, then classify |
| `requirement_mismatch` | BLOCKED — a human decides |
| `insufficient_evidence` | get evidence; do not guess |

## Pre-existing failures

```
baseline ──► failure exists ──► implement ──► same failure
                                                  │
                                       classification: pre_existing
```

```yaml
classification: pre_existing_failure
baseline_evidence:  # the failure, observed before the change
current_evidence:   # the same failure, after
impact:             # does it block this task?
```

Establish the baseline by observation — a stash, a clean checkout, the parent commit — not
by assertion. The final verdict must keep task-caused failures, pre-existing failures and
unresolved uncertainty visibly separate.

## Flaky failures

Do not rewrite code because a test might be flaky. Inspect, rerun within the budget
(`max_flaky_retries: 3`), compare, classify.

```yaml
verification:
  attempt: 2
  result: flaky_suspected
  reruns: 3
  outcomes: [pass, pass, fail]
```

A test that passes on the third run is flaky, not fixed. Never silently convert flaky
behavior into PASS.

Related: `agentic-loop.md` · `verification.md` · `test-integrity.md`
