# Human governance

**The team never modifies itself.** Reflection produces a recommendation; a human approves
it; only then does anything change.

This is not caution for its own sake. The team works on a regulated codebase where a
weakened assertion or an invented traceability link is a defect in the record, and a
system that could quietly edit its own rules could quietly edit those too.

## The lifecycle

```
observation → learning → analysis → recommendation → HUMAN REVIEW → implementation
                                                          │              │
                                                      rejected      evaluation
                                                                         │
                                                                    validation
```

Everything left of HUMAN REVIEW the team does on its own. Nothing right of it happens
without a person saying so.

## What needs approval

| Change | Needs approval |
|---|---|
| a new rule in `rag/check_evidence.py` | yes |
| a change to an agent definition | yes |
| a change to `SKILL.md` or a reference | yes |
| promoting a correction to a lesson | yes |
| installing anything | yes, always |
| recording a correction as a candidate | no — that is observation |
| running a checker | no |
| reporting a finding | no |

The dividing line: **observing and reporting are free; changing how the team works is
not.**

## Never

These come from the existing SDET rules and stay authoritative:

- weaken an assertion to make a test pass
- change an expected value without evidence
- hide a missing requirement
- convert missing evidence into PASS
- silently ignore unavailable authoritative information
- invent traceability
- assume a missing result means success
- modify regulated evidence to satisfy a workflow
- alter the team without human approval

Two of these have live examples in this repo, which is why they are listed rather than
assumed. The QA reviewer asked for design-level requirement tags to be retagged as system-level; the mapping is not
agreed, so retagging would have written false traceability into a regulated record. And
the `UNCONTROLLED` banner on a local render is correct — the honest answer is that the set
cannot be filed as the verification record, not that something is broken.

## Recommendation format

Small enough to read, structured enough to act on:

```yaml
id:
category:            # SKILL AGENT PROMPT WORKFLOW RAG MEMORY MCP PLUGIN TOOL
                     # DETERMINISTIC_CHECK EVALUATION OBSERVABILITY
title:
problem:
observed_frequency:  # how many tasks, not a guess
evidence:            # file:line, task ids, or the correction itself
current_cost:
proposed_solution:
alternatives:        # including "do nothing"
expected_benefit:
implementation_cost:
confidence:
risk:
status:              # PENDING_REVIEW APPROVED REJECTED DEFERRED IMPLEMENTED VALIDATED
```

`observed_frequency` and `evidence` are the fields that make a recommendation worth
reading. A proposal without them is an opinion.

## After approval

Record the change in `evaluation/versions.md` — driver, evidence, measurement, rollback.
An approved change with no version entry is a change nobody can revert on purpose.

An approved change is not finished until it is evaluated. `evaluation/benchmarks.md` has
the tasks; the question is whether the change measurably improved something, not whether
it sounded better. A change that fixes one thing and breaks another is a regression, and
`evaluation/regression.md` exists to catch exactly that.
