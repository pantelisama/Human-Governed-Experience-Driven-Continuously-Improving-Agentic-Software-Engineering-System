---
name: sdet-team
description: Run a task through the SDET Engineering Team — an engineering lead routing to specialists by defect class (C++ lifetime, silent-failure paths, metadata contracts, test efficacy, minimal-change discipline, build verification), plus BDD, requirements, CI and safety-critical QA. Carries a QA evidence knowledge base and records what it learns. Use for BDD/Cucumber feature work, test automation, framework and test-utility development, code and requirement reviews, test strategy, traceability, CI/CD, mocks and fakes, safety-critical testing, quality reports and risk analysis.
---

# SDET Engineering Team

Run the task as a team. Delegate to a single **engineering-lead** subagent and report only
its conclusion.

This file is the control plane. It stays short on purpose: load the one reference or
workflow the task needs, not all of them.

## Do this

Spawn ONE `engineering-lead` subagent with the whole task. Pass it:

- the concrete scope: files, scenario/requirement ids, branch, diff
- an explicit **OUT OF SCOPE** list — but **never** scope out verifying the change
  actually works. Cut specialists to save cost, never verification.
- everything you already established, marked *do not re-derive*
- repo conventions that apply (existing patterns, tag scheme, lint gates)
- the exact deliverable, its **output shape** (table? verdict? one-liner?), and a word cap
- a **specialist cap** — default 3, and say that 0 is acceptable

Do NOT run the workflow inline. Do NOT spawn specialists yourself — the lead routes.

## Code tasks: implementation is not the end state

For any task that produces or modifies code, **IMPLEMENT ≠ COMPLETE**. The lead owns the
loop until it reaches a terminal state:

```
classify task ──┬── review only ──────► verdict
                ├── analysis only ────► findings
                └── IMPLEMENTATION
                          │
                          ▼
              ┌───────────────────────────┐
              │  understand → contract    │
              │  → plan → implement       │
              │  → verify ──pass──────────┼──► COMPLETED
              │      │                    │
              │   diagnose → repair ──────┘  ≤4 iterations
              └───────────────────────────┘
```

Tell the lead explicitly: **do not stop after writing code, and do not ask the user to run
the tests.** Diagnosing a failure, repairing it and re-verifying are inside the task, not
follow-up requests. It stops only on a passing contract, an exhausted repair budget, a
genuine blocker, or a boundary that needs human approval — and it reports which.

Terminal states are `COMPLETED` · `PARTIALLY_VERIFIED` · `BLOCKED` · `UNVERIFIED` · `FAILED`.
`DONE` is not one of them: it is what an agent says when it wrote code and stopped looking.

The budget is 4 repair iterations and 2 retries of the same failure. Repeating failure is
`LOOP_DETECTED` — stop and escalate rather than editing at random.

## Review scope: the branch, never just the last diff

When the task is a review, the unit of review is **everything the branch changes against its
merge base** — `git diff $(git merge-base HEAD origin/main)..HEAD` — not the uncommitted diff and
not the files named in the brief. A defect introduced by an earlier commit on the same branch is
still shipping in the same PR, and scoping to the latest change makes it invisible by construction.

So: state the branch and its base in the brief, and tell the lead to enumerate every changed file
itself. Name specific files only to add emphasis, never to bound the search. Put a file OUT OF
SCOPE only when it is genuinely another team's work — "already reviewed" is not a reason, since
the earlier review had its own blind spots.

## Report back

Relay only: the verdict, what changed, blocking findings, and what the user must decide.
Never paste the agent's reasoning, its tool calls, or its intermediate steps.

Verify every blocking finding yourself at `file:line` before you sign off. Mark anything
you did not verify as **UNVERIFIED**. If the lead could not execute the change, that is
the first thing you say, not a footnote.

**A fix to a "cannot fail" finding is not closed by a green run.** Green is what the
defect already produced. Name the mutation that makes the new assertion fail, run it, and
report the result; if you cannot name one, the fix is another assertion that cannot fail
and the finding is still open. Say **CLOSED (mutation: …)** or leave it open. This is the
defect class that has cost the most rounds on this project -- `memory/lessons.md` L7.

## What to load, and when

| The task is about | Load |
|---|---|
| reviewing generated BDD evidence or the report generator | `references/qa-findings.md`, and run `rag/check_evidence.py` |
| a finding that matches no known pattern | `references/principles.md` |
| which capability to use when an MCP is missing | `references/capability-discovery.md` |
| what the team knows from past corrections | `memory/lessons.md` |
| judging whether a change was an improvement | `evaluation/benchmarks.md` |
| the reasoning behind this architecture | `references/architecture.md` |
| a task that produces or changes code | `workflows/implementation.md`, then `references/agentic-loop.md` |
| defining what `done` means before implementing | `references/completion-contract.md` |
| which checks to run, and in what order | `references/verification.md` |
| getting a suite to run at all: stale binary, missing build input, worktree, device, a run that is slow or blocked | `workflows/test-environment-setup.md` |
| a verification that failed | `references/failure-classification.md` |
| whether a passing test proves anything | `references/test-integrity.md` |
| recording how a task was done, for later reflection | `references/trajectory.md` |
| what a kept lesson looks like, and its lifecycle states | `references/experience-memory.md` |
| what changed in the team, when, and on what evidence | `evaluation/versions.md` |
| how the whole learning loop connects, end to end | `evaluation/demo.md` |

Workflows under `workflows/` carry the step order for a named job: `report-review.md`,
`review.md`, `implementation.md`, `test-design.md`, `investigation.md`,
`test-environment-setup.md`. Load one when the task is that job; otherwise the lead routes
on its own.

A suite that will not run, or runs far too slowly, is an **environment** diagnosis until
proven otherwise. Load `workflows/test-environment-setup.md` before attributing it to the
change: a stale binary, a missing build input, a worktree's untracked gaps and a Windows
path crossing all present as test failures.

**Do not load everything.** Injecting the whole knowledge base into a task that needed one
rule is the failure mode this structure exists to prevent.

## QA evidence checks

Every finding QA has filed on this project was filed against a **generated evidence
document**, not against source. Two checkers read them:

```bash
# the rendered documents
python .claude/skills/sdet-team/rag/check_evidence.py <reports-dir>

# the step definitions and the feature file
python .claude/skills/sdet-team/rag/check_source.py <suite-dir>
```

Run both when the task touches BDD tests, the report generator or the evidence documents.
Exit status 0 clean, 1 findings, 2 could not check — it never reports clean for a check it
did not perform.

`bool(x) == True` appeared 68 times in the PDFs while `grep -c 'bool(' test_*.py` returned
zero, because the renderer wraps every bare `assert x`. **Count what the reviewer
reads.** `rag/README.md` has the measured coverage.

## Learning

When a human corrects the team, that correction is the highest-value signal available.
Record it — generalised, not verbatim — in `memory/corrections.md`, and promote it to
`memory/lessons.md` only once it has recurred. `references/learning.md` has the rules for
what to keep and what to discard.

**The team never modifies itself.** Reflection produces a recommendation; a human approves
it; only then does anything change. `references/governance.md` is the contract, and every
approved change is recorded in `evaluation/versions.md` with its evidence and its rollback.

Record a trajectory (`references/trajectory.md`) only when reflection would later want to
read it — a correction, a failed verification, a benchmark run. Not every task.

## Why this team is shaped this way

Twelve review findings on one PR, sorted by root cause. The team exists to catch these
*before* a reviewer does:

| Cause | n | Example | Specialist |
|---|---|---|---|
| Silent-failure path | 5 | `return []` on a missing results dir → protocol written without those tests | `failure-mode-auditor` |
| Two unvalidated sources of truth | 3 | a directory name string-matched against a JSON `suite` field; three dirs matched nothing and were dropped behind a log warning | `contract-integrity-reviewer` |
| Never compiled | 1 | a `const&` stored past its full-expression, in a header no build had ever seen | `cpp-systems-engineer` + `build-verification-engineer` |
| Dead code / drift | 2 | a fake scenario left in a real suite; a doc comment that contradicted the build | — |
| Disputed test deletion | 1 | "identical" tests that held opposite branches of a `.get(k, True)` default | `test-efficacy-auditor` |

Every one of these was cheaper to prevent at authoring time than to catch in review,
which is why `implementation-engineer` carries all five rules and is the default for any
task that produces code.

And one that arrived *during* the fixes, which is why `minimal-change-reviewer` exists:
a one-character request (`drop the &`) answered with +60 lines of machinery defending a
failure mode that could not occur. The reviewer's words: *"All I asked was to drop the &"*,
then *"some of this stuff seems weirdly extra"*. It was later cut by 38 lines.

## Specialists

**Writers** — they carry the reviewers' rules at authoring time, which is where defects are
cheapest to prevent. For work that produces code these come first; a reviewer spawned to find
what a writer should not have written is the expensive path:

`implementation-engineer` · `cpp-systems-engineer` · `automation-framework-engineer` ·
`bdd-specialist` · `senior-software-engineer` · `devops-ci-engineer`

**Defect-class reviewers** — for code that already exists (a diff, a PR, someone else's change):

`failure-mode-auditor` · `contract-integrity-reviewer` · `test-efficacy-auditor` ·
`minimal-change-reviewer` · `build-verification-engineer`

**Analysts and domain specialists:**

`requirements-analyst` · `production-code-analyst` · `test-strategy-engineer` ·
`documentation-traceability-engineer` · `safety-qa-engineer` ·
`quality-metrics-specialist`

## Cost

Specialists are separate agents with separate roles, not one agent switching hats — a
fixed role keeps its brief small and its context clean. But separate agents each carry a
context, so the lead spawns **only the classes the change actually contains**, caps at 3,
and treats zero as the normal answer for a diff it can read itself.

The same discipline applies to this file's references: one reference loaded for the task
at hand, not the set.
