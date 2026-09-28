# Workflow: produce or change code

Writing it right is cheaper than reviewing it after. `implementation-engineer` is the
default for any task that produces code, and it carries the reviewers' rules at authoring
time.

**Writing the code is step 5 of 12.** The task is not finished when the edit lands; it is
finished when verification has run against the final state and passed, or when the loop
has stopped at a terminal state that says why. `references/agentic-loop.md` is the machine.

## Order

```
 1 understand ──► 2 completion contract ──► 3 repo conventions ──► 4 plan
                                                                     │
                                                                     ▼
                                                              5 implement
                                                                     │
                                                                     ▼
        ┌──────────────────────────────────────────────► 6 verify
        │                                                        │
        │                                                   pass │ fail
   9 re-verify ◄── 8 repair ◄── 7 diagnose ◄───────────────┘     │
        │              (≤4, and only what the diagnosis names)    │
        └────────────────────────────────────────────────────────┤
                                                                  ▼
                                    10 final verification against the final state
                                                                  ▼
                                             11 capture evidence ──► 12 report
```

1. **Understand.** What is actually being asked, and what is out of scope.

2. **Establish the completion contract** — before implementing, so `done` is not defined
   after the fact. `references/completion-contract.md`.

3. **Read the surrounding code** — comment density, naming, idiom. Code that reads like
   its neighbours is code a reviewer does not have to re-learn.

4. **Plan**, then implement against the plan. These rules apply while writing:

   - **Fail loudly.** A missing input is a failure, not an empty list. Five of twelve
     findings on one PR were silent-failure paths: `return []` on a missing results dir,
     and a protocol written without those tests.
   - **One source of truth.** A value maintained in two places drifts. If a directory name
     has to match a JSON field, something must validate that they still do.
   - **Minimal diff.** Speculative abstraction and guards for impossible failures both get
     cut in review. A one-character request answered with +60 lines was later cut by 38.

5. **Implement.**

6. **Verify.** Deterministic checks first, then the smallest relevant tests, widening only
   as risk requires. `references/verification.md`. Compiled code that no build has seen is
   not written, it is drafted.

7. **Diagnose** every failure before touching anything — did *this* change cause it?
   `references/failure-classification.md`. A pre-existing failure needs baseline evidence,
   not a repair.

8. **Repair** the smallest thing the diagnosis names. Re-check the diff each iteration:
   intended? minimal? unrelated changes? tests still meaningful? Reuse
   `minimal-change-reviewer`. A failed implementation must not become an architecture
   expansion.

9. **Re-verify.** Budget: 4 repair iterations, 2 retries of the same failure. Repeating
   failure means `LOOP_DETECTED` — stop and escalate, do not keep editing.

10. **Final verification against the actual final state.** Intermediate green from an
    earlier iteration says nothing about the state the last repair left behind.

11. **Capture evidence** — a compact ledger, summaries and references, never raw logs.

12. **Report** the terminal state and its evidence. `COMPLETED`, `PARTIALLY_VERIFIED`,
    `BLOCKED`, `UNVERIFIED` or `FAILED` — never `done`.

If the change touches evidence documents, `workflows/report-review.md` before handing over.

## Test changes

A test that ships with the change must be seen to fail against the broken behavior —
`references/test-integrity.md`. Mutation checking is risk-adaptive, and the decision is
recorded either way. A surviving mutation is a finding, not a formality: establish whether
the test is weak or the branch is simply never executed, because those need opposite fixes.

## Evidence ledger

```yaml
iterations:
  - iteration: 1
    action: implement
    verification: {build: failed, tests: not_run}
    failure: compilation_error
  - iteration: 2
    action: repair
    verification: {build: passed, tests: passed, mutation: passed}

final:
  status: COMPLETED
  iterations: 2
  evidence: {build: passed, tests: passed, mutation: passed}
```

Summaries and references. Storing whole command output defeats the point.

## Final report

```
STATUS: COMPLETED

Changed:      src/foo.cpp · tests/test_foo.py
Verification: build PASS · targeted PASS · regression PASS · integrity PASS · mutation PASS
Repairs:      2
Remaining:    none
```

Never report success without evidence. If a gate did not run, say so and mark the state
`PARTIALLY_VERIFIED` — an unrun check is not a passed one.

## Safety

Never weaken an assertion to make a test pass, change an expected value without evidence,
skip or delete a test to reach green, or convert missing evidence into PASS. Those four
produce the same green as a real fix, which is exactly why they are listed.

The loop is autonomous inside the authorized scope. It does not expand requirements, touch
unrelated components, commit, push, merge or release on its own. If a repair would require
any of those: stop, explain, ask. `references/governance.md` has the full list.
