# Experience memory

`references/learning.md` says what is worth keeping and how to generalise it. This file
says what a kept item looks like, what states it moves through, and how items relate.

Two memories, never mixed:

| | Answers | Lives in |
|---|---|---|
| **Project knowledge** | what is true of this project | the repo, `references/qa-findings.md`, the evidence documents |
| **Experience** | what the team learned from working on it | `memory/` |

A requirement id is project knowledge. "Count what the reviewer reads" is experience. The
first goes stale when the repo changes; the second survives it.

## The record

Entries in `memory/` are prose with a heading, and that stays — a lessons file has to be
readable. This is the set of facts each entry carries, not a file format to impose:

```yaml
id:                    # C1, L3, P-02, S4
type:                  # OBSERVATION CORRECTION PROJECT_FACT GENERAL_PRINCIPLE
                       # WORKFLOW_PATTERN STRATEGY CANDIDATE_RULE VALIDATED_RULE
                       # DEPRECATED_RULE
title:
source:
  trajectory_id:
  human_feedback:      # the words, if a human said them
observation:           # what happened
root_cause:            # from reflection.md's cause table — not a restatement
principle:             # the generalised form, two sentences at most
action:                # what to do differently
evidence:              # file:line, a rule id, a measured count
recurrence:            # occurrences, counted not estimated
confidence:
status:                # candidate | validated | active | deprecated | superseded | rejected
supersedes:
last_validated:
```

`root_cause` and `recurrence` are the fields that make an entry worth loading. Without
them it is an anecdote, and anecdotes are what make a memory file too long to read.

## States

Memory is not append-only. An entry moves:

```
candidate ──recurs──► validated ──used──► active
    │                                       │
    └──────contradicted──► rejected         ├──restated better──► superseded
                                            └──no longer applies──► deprecated
```

- **candidate** — one occurrence. Lives in `memory/corrections.md`. Does not yet change
  how the team works.
- **validated** — recurred, with evidence. Earns a place in `memory/lessons.md`.
- **active** — loaded by a workflow or enforced by a check in `rag/`.
- **superseded** — a later entry states it better. Keep the pointer, drop the text.
- **deprecated** — the code or process it described is gone. Keep with a note saying why;
  a deleted lesson gets relearned.
- **rejected** — tried and found wrong. Worth keeping: it stops the same proposal
  returning.

Promotion between states is a change to how the team works, so it needs approval —
`governance.md`.

## Curation, on write

Run these when adding an entry, not on a schedule:

- **deduplicate** — the same observation twice is one entry with `recurrence: 2`.
- **detect contradiction** — an entry that disagrees with an active one is a finding in
  itself. Resolve it; do not file both.
- **update recurrence** rather than appending a near-duplicate.
- **check the evidence still exists** — a lesson citing a deleted file is deprecated.

## Relations

Experience is a graph, held as `id` references in prose, not a database. The edges that
carry weight:

```
CORRECTION ──generalized_as──► PRINCIPLE ──addressed_by──► STRATEGY
     │                              │
     ├──caused_by──► ROOT CAUSE     └──enforced_by──► DETERMINISTIC CHECK
     ├──supported_by──► EVIDENCE
     ├──similar_to──► EXPERIENCE
     └──resulted_in──► RECOMMENDATION
```

They exist so a recommendation can be asked *why*, and answer with counted evidence rather
than an assertion. The live chain in this repo:

```
C1 "68 of them, in the PDFs"
  caused_by      poor retrieval — checked the source, not the render
  generalized_as L1 "count what the reviewer reads"
  supported_by   68 rows at the <baseline-commit> baseline
  enforced_by    rag/check_evidence.py R2
  resulted_in    both checkers reading rendered evidence
```

**Do not build a graph database.** Four files and an id convention answer every question
the corpus can pose. A store becomes justified when a query cannot be answered by reading
`memory/`, and not before.
