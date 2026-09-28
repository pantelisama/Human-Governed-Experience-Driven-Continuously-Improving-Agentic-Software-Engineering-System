# The verification stack

Three layers, cheapest and most certain first.

```
                      VERIFICATION
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  Deterministic        Behavioral        Adversarial
     checks              tests              checks
   build · lint      unit → targeted     does the test
   types · format     → regression       fail when the
   schema · static                       code is broken?
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    Completion gate
```

## Layer A — deterministic

Build, compile, lint, type check, format validation, schema validation, static analysis,
generated-artifact checks, traceability and evidence checks. Use the repository's own
tooling; this project already has `rag/check_evidence.py` and `rag/check_source.py`.

> Never use an LLM to reason about something a deterministic check establishes reliably.

An agent's opinion that the code compiles is not a build.

## Layer B — behavioral

Smallest relevant tests first, widening only when risk justifies it:

```
changed unit tests ──► targeted suite ──► related regression ──► broader suite
```

Running the whole repository for a trivial change is waste, not rigour.

## Layer C — adversarial

For changes carrying real behavioral risk — boundaries, error handling, failure paths,
state transitions, serialization, contracts, safety behavior, changed assertions, bug
fixes, new tests — establish that the tests distinguish correct from incorrect behavior.

> A green test must be evidence that the intended behavior is actually tested.

Green from a test that cannot fail is not evidence. See `test-integrity.md`.

## Independent verification

The context that wrote the change is not authoritative about whether the change is right.

```
implementer ──► change ──┬──► deterministic checks
                         ├──► tests
                         ├──► audit specialist
                         └──► test integrity
                                   │
                                   ▼
                             final verdict
```

Reuse the specialists that already exist — `build-verification-engineer`,
`test-efficacy-auditor`, `failure-mode-auditor`, `minimal-change-reviewer`,
`contract-integrity-reviewer` — rather than inventing a verification agent per stage.

The implementation agent claiming success is a claim, not a result.

### Negative verification — the rule that catches a "fixed" that is not

A fix that **removes** something is verified by the old pattern's **absence from the
generated artefact**, never by the new text's presence. `grep -c '<what I just wrote>'`
returns 1 for any edit that landed and says nothing about the defect.

Before calling a finding closed, write down both sides:

| | what to run | passing result |
|---|---|---|
| negative | `grep -rl '<old pattern>' <evidence>/*.html \| wc -l` | `0` |
| positive | `grep -c '<new text>' <evidence>/<scenario>.html` | `>= 1` |

The negative row is the one that matters; the positive row only shows the edit deployed.
A finding phrased **"every X"** needs the per-item count for *every* X enumerated — the
items already known to pass are not the sample.

Order matters: `rag/check_evidence.py` and `rag/check_source.py` run **before** the claim.
Exit 0 is the evidence. A grep the team wrote for itself is not, because it tests the
author's belief about the fix rather than the artefact.

And a repeated **"are you sure?"** is a defect report, not a request for reassurance.
Stop asserting, re-derive from the artefact, and answer with the counts.

## Cost discipline

```
cheap deterministic check ──► targeted test ──► targeted specialist ──► broader verification
```

Each repair iteration receives the task, the current state, the failure evidence, the
relevant files and the previous attempt — not the whole history, not whole files, not
entire logs.

Related: `agentic-loop.md` · `completion-contract.md` · `test-integrity.md`
