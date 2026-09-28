# The agentic engineering loop

**IMPLEMENT ≠ COMPLETE.**

Writing the code is an intermediate state. A task that produces or changes code is not
finished until verification has run against the final source state and passed, or until
the loop has stopped at an explicit terminal state that says why.

The user should never have to say *run it*, *fix that*, *check again*, or *continue*.
Those transitions belong to the loop.

## The machine

```
  RECEIVED
     │
     ▼
  ANALYZING ──► PLANNED ──► IMPLEMENTING
                                │
                                ▼
                           VERIFYING ──── pass ────► COMPLETED
                                │
                             failure
                                │
                                ▼
                           DIAGNOSING ──── human needed ────► BLOCKED
                                │
                                ▼
                           REPAIRING
                                │
                                └──────► VERIFYING   (≤ 4 iterations)
```

Every transition carries a reason and evidence. `looks correct`, `should work`,
`probably fixed` and `tests should pass` are not evidence — they are the absence of it.

## Bounded repair

```yaml
limits:
  max_repair_iterations: 4
  max_same_failure_retries: 2
  max_flaky_retries: 3
```

Each iteration: inspect state → verify → if the contract passes, stop → otherwise classify
the failure (`failure-classification.md`) → repair only what the diagnosis names → verify again.

A repair that makes the tests pass is not sufficient on its own. The final state must be
re-evaluated against the whole completion contract, not just the gate that was failing.

## Stop conditions

The loop stops when one of these is true, and never merely because code was written:

1. the completion contract passes
2. the repair budget is exhausted
3. a genuine blocker needs a human
4. the task is underspecified
5. continuing would leave the authorized scope
6. a safety or governance boundary requires approval

## Anti-loop detection

Stop automatic repair and escalate when you see:

- the same file modified repeatedly with no progress
- the same test failing after the same patch pattern
- changes that undo each other
- the diff growing while verification does not
- an assertion getting weaker

```
same failure ──► same failure ──► LOOP_DETECTED ──► diagnose, then hand to a human
```

Increasingly random edits are not repair.

## Terminal states

| State | Meaning |
|---|---|
| `COMPLETED` | every required gate passed against fresh evidence |
| `PARTIALLY_VERIFIED` | implemented, but a non-fatal verification limit remains |
| `BLOCKED` | needs a human decision, missing information, or authorization |
| `UNVERIFIED` | the change exists; correctness could not be shown |
| `FAILED` | not achievable within the repair budget, or definitively broken |

**`DONE` is not a state.** It is what an agent says when it wrote code and stopped looking.

## Fresh-state verification

The final verification must run against the actual final source. Intermediate green from
iteration 2 is not evidence about the state left by iteration 3.

## Scope

Autonomous *inside* the authorized scope. The loop never expands requirements, redesigns
unrelated architecture, touches unrelated components, weakens or deletes tests to reach
green, commits, pushes, merges or releases on its own. If a repair would need any of
those: stop, explain, ask.

Related: `completion-contract.md` · `verification.md` · `failure-classification.md` ·
`test-integrity.md` · `governance.md`
