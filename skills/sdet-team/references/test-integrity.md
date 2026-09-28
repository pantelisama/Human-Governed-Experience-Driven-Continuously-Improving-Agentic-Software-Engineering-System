# Test integrity

A passing test is evidence only if it would have failed on broken code.

```
  correct code   + test ──► PASS
  mutated  code  + test ──► MUST FAIL
```

If the test stays green after a relevant mutation, the test is ineffective — whatever the
coverage report says.

## The gate

For medium and high risk test changes, ask the one question:

> Does this test fail when the intended behavior is deliberately broken?

Then answer it by doing it, not by reasoning about it. Break the behavior, rebuild, rerun,
restore. Record the result.

```
mutate ──► rebuild ──► rerun ──► killed?  ──yes──► restore, record PASS
                                    │
                                    no
                                    ▼
                         TEST_INTEGRITY_FAILURE
                                    │
                         is the branch even reachable?
                         ┌──────────┴──────────┐
                     reachable            never executed
                         │                      │
                  strengthen the test    report the gap —
                                         the test is not weak,
                                         the path is dead
```

A surviving mutation has two very different causes, and reporting the wrong one is a
false finding. A test that cannot catch the bug and a branch no input ever reaches both
show up as green; only the second is a coverage gap rather than a bad assertion.

## Adaptive, not universal

| Mutation check | When |
|---|---|
| **should run** | bug fixes · changed business logic · changed boundaries · changed error handling · new assertions · safety-critical behavior · high-risk regression tests · any test whose efficacy is uncertain |
| **may be skipped** | formatting · comments · documentation · pure renames · non-functional refactoring with coverage already established independently |

The decision is explicit in the trajectory, either way:

```yaml
mutation:
  required: true
  reason: "bug fix changes a failure boundary"
  scope: targeted
  result: passed          # the mutation was killed
```

```yaml
mutation:
  required: false
  reason: "documentation-only change"
```

"Skipped" with no reason is not a decision, and a refactor claiming established coverage
should have observed it, not assumed it.

## Verification integrity

The change must never pass by altering what checks it.

| Forbidden | Looks like |
|---|---|
| weakening an assertion | test fails → assertion loosened → green |
| skipping | test fails → skipped or deleted → green |
| moving the target | expected value changed to match current output |
| fitting the bug | test rewritten to match incorrect production behavior |

Each of these is a `VERIFICATION_INTEGRITY_FAILURE`, reported as such. The system must be
able to tell **implementation repaired** from **verification weakened** — they produce an
identical green.

## Regulated work

Green is not automatically verified. Evidence stays auditable, traceability stays intact,
provenance stays real, and no regulated artifact changes without authorization.
`references/governance.md` holds the full list.

Related: `verification.md` · `failure-classification.md` · `agentic-loop.md`
