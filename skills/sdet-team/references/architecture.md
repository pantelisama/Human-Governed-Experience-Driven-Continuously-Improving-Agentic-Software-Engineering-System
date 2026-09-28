# Architecture

Three layers. The skill decides, the agents work, the capabilities are whatever the
session happens to have.

```
                         HUMAN
                           │  feedback / approval
                           ▼
        ┌──────────────────────────────────────────┐
        │  SKILL.md — control plane                │
        │  routing · what to load · what to run    │
        └────────┬─────────────────────┬───────────┘
                 │                     │
                 ▼                     ▼
        engineering-lead        knowledge + checks
                 │              references/ rag/ memory/
                 ▼
          specialist agents
                 │
                 ▼
            verification
                 │
                 ▼
             the verdict
                 │
                 ▼
         experience capture
                 │
                 ▼
      reflection → recommendation
                 │
                 ▼
            HUMAN REVIEW
```

## Why the skill is the control plane

The skill is the only part that exists in every session. Agents are spawned, MCPs come and
go, tools may or may not be installed. Putting the routing decisions anywhere else means
the team behaves differently depending on which account it runs in.

So: the skill decides *what* to do and *what to load*. The lead decides *who* does it.
Nothing else orchestrates. There is no second orchestrator, and the learning engine is not
an agent — it is a set of files the lead reads and writes.

## Why progressive disclosure

The knowledge base is larger than any one task needs. `references/qa-findings.md` alone is
fifteen patterns with their history; loading it for a task about CI wiring costs context
and teaches nothing.

So `SKILL.md` stays short and says which file answers which kind of question. A task about
evidence documents loads `qa-findings.md`. A task about a novel defect loads
`principles.md`. A task about neither loads neither.

This is the same discipline as the specialist cap: the lead spawns only the defect classes
the change contains, and loads only the references the task needs.

## Why the lead owns the verdict

The lead delegates analysis and never delegates the conclusion. A specialist reports what
it found in its own narrow frame; only the lead has seen all of them, and only the lead
knows what was scoped out. A verdict assembled by concatenating specialist reports is a
verdict nobody checked.

This is also why the lead verifies blocking findings at `file:line` before signing off. A
specialist can be wrong, and has been — one reported that a step's acceptance criterion
was unasserted when it was asserted two lines away.

## The layers, concretely

| Layer | What it is | Where |
|---|---|---|
| Control plane | routing, disclosure, the run commands | `SKILL.md` |
| Knowledge | what QA has filed and the principles under it | `references/` |
| Checks | the deterministic subset, executable | `rag/` |
| Workforce | the specialist agents | `.claude/agents/` |
| Experience | corrections, lessons, patterns; their shape in `references/experience-memory.md` | `memory/` |
| Path | how a task was done, when worth recording | `memory/trajectories/` |
| Measurement | benchmarks, regression tasks, version history | `evaluation/` |

## What this is not

Not an autonomous system. Nothing here rewrites the team; see `governance.md`.

Not a second agent framework. The specialists that exist are the specialists; a new
capability does not justify a new agent.

Not a vector database. The corpus is three review documents and one test suite, and
lexical rules over the rendered evidence answer the question the reviewer asks. If the
corpus outgrows that, `report_review_rag.txt` describes the fuller design — but it should
earn the complexity through use, not be built ahead of it.
