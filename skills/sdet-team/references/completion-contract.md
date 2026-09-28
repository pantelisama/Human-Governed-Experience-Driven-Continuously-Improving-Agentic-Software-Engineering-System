# Completion contract

Derived **before** implementation starts, so that `done` is defined by something other
than the agent's own sense of having finished.

```yaml
completion_contract:
  implementation_complete:  required
  build_pass:               required_when_applicable
  relevant_tests_pass:      required
  regression_tests_pass:    required
  static_checks_pass:       required
  requirements_verified:    required_when_applicable
  diff_reviewed:            required
  test_efficacy_verified:   required_for_test_changes
  mutation_check:           adaptive
```

## Task-specific, risk-based

Do not run every layer on every change. A comment fix does not need a regression suite; a
changed boundary condition does. Decide from the risk the change actually carries.

But the cut is on **breadth**, never on existence:

> Never omit verification merely to save tokens.

Cutting a specialist is cost control. Cutting the gate that would have caught the defect
is how a false completion happens.

## Stating it

The contract goes in the brief, before implementation, so the loop has something to test
against that was not written after seeing the result:

```
task
  │
  ▼
contract ───────────────┐          derived first
  │                     │
  ▼                     │
implement               │
  │                     │
  ▼                     ▼
verify ───────────► compare ──► pass? COMPLETED
                                fail? diagnose
```

A contract written after the tests ran is not a contract, it is a description.

Related: `agentic-loop.md` · `verification.md` · `test-integrity.md`
