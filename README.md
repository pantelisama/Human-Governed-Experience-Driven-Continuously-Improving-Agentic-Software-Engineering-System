# Human-Governed, Experience-Driven, Continuously Improving Agentic Software Engineering System

### SDET E-Team — a reference implementation for Claude Code

A persistent AI engineering organisation for Claude Code: software testing, SDET engineering,
automation frameworks, code review and quality engineering. It learns from the corrections
people give it, turns what recurs into deterministic checks, and changes itself only when a
person approves.

| | |
|---|---|
| **Human-governed** | the team proposes; a person approves; only then does anything change |
| **Experience-driven** | a correction is generalised, must recur to count, and is enforced by a check |
| **Continuously improving** | every approved change carries its evidence, its measurement and its rollback |
| **Agentic** | one lead, seventeen specialists, routed by defect class — not a prompt |

The lead never delegates the verdict, and the team never edits itself.

## Quick start

```bash
git clone <this repo> && cd <this repo>
./install.sh --user                                   # or: ./install.sh /path/to/your/project
python3 skills/sdet-team/rag/test_known_defects.py    # the checkers catch every known defect
```

Then, in a Claude Code session:

```
/sdet-team review the BDD suite on this branch
```

Requires Claude Code and Python 3.9+ (standard library only; `pdftotext` is optional and
enables the PDF-side checks). The optional learning hooks are described under
[Learning hooks](#learning-hooks).

---

## The whole flow, end to end

```
                              ┌─────────┐
                              │  HUMAN  │
                              └────┬────┘
                                   │ task
                                   ▼
                    ┌──────────────────────────────┐
                    │  SKILL.md — control plane    │   what to load
                    │  routes · loads · runs       │   what to run
                    └──────────────┬───────────────┘
                                   │ one subagent, whole task
                                   ▼
                    ┌──────────────────────────────┐
                    │      engineering-lead        │◄──── references/ · memory/ · rag/
                    │  picks defect classes, ≤3    │
                    └──────────────┬───────────────┘
                     ┌─────────────┼─────────────┐
                     ▼             ▼             ▼
                ┌─────────┐  ┌─────────┐  ┌─────────┐
                │ writer  │  │reviewer │  │ analyst │    run in parallel
                └────┬────┘  └────┬────┘  └────┬────┘
                     └─────────────┼─────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │  deterministic checks (rag/) │   21 rules, exit 0/1/2
                    └──────────────┬───────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │  lead verifies at file:line  │   never delegates the verdict
                    └──────────────┬───────────────┘
                                   ▼
                              ┌─────────┐
                              │ VERDICT │──────► human
                              └────┬────┘
                                   │ correction? finding returned? manual repetition?
                                   ▼
                    ┌──────────────────────────────┐
                    │  experience capture (memory/)│
                    └──────────────┬───────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │  reflection → recommendation │
                    └──────────────┬───────────────┘
                                   ▼
                          ┌─────────────────┐
                          │  HUMAN APPROVAL │   the team never edits itself
                          └────────┬────────┘
                                   ▼
                        change + evaluation/versions.md
```

**Everything left of HUMAN APPROVAL the team does alone. Nothing right of it happens without a
person saying so.**

---

## How it learns

A correction is the highest-value signal available, and the cheapest to lose. It is generalised,
not transcribed, and it only changes the team once it has recurred.

```
   signal                    stored as              becomes
   ──────                    ─────────              ───────
   human correction   ─┐
   finding came back   ├──►  candidate    ──recurs──►  validated  ──approved──►  active
   manual repetition   │     corrections.md            lessons.md                rag/ rule
   wrong route        ─┘          │                         │                    or workflow
                                  │                         │
                          contradicted                 restated better
                                  ▼                         ▼
                             rejected                  superseded
                                                            │
                                                     no longer applies
                                                            ▼
                                                       deprecated
```

| Signal | Value | Example |
|---|---|---|
| Human correction | highest | "count what the reviewer reads" |
| A finding that came back | high | fix addressed the symptom, not the cause |
| Repeated manual work | medium | the same check done by hand → a missing tool |
| A wrong route | low | a specialist spawned for a class the change lacked |
| A task that went well | none | teaches nothing worth storing |

**The worked example that shaped the whole design.** The team ran `grep -c 'bool(' test_*.py`, got
zero, and reported a finding closed. The reviewer found 68 of them in the PDFs — the generator
manufactures rows the source does not contain.

| | |
|---|---|
| Transcribed (useless) | "grep the HTML" |
| Generalised (kept) | **Count what the reviewer reads.** A check against the source can report clean on a document full of the defect. |
| Enforced as | both checkers read the rendered evidence, never the source |

| State | Lives in | Changes how the team works? |
|---|---|---|
| candidate | `memory/corrections.md` | no — one occurrence |
| validated | `memory/lessons.md` | yes, after approval |
| active | a `rag/` check or a workflow | enforced every run |
| superseded | pointer kept, text dropped | no |
| deprecated | kept with a note | no — a deleted lesson gets relearned |
| rejected | kept | stops the same proposal returning |

---

## The eighteen agents

One lead. Seventeen specialists, in three groups by **when** they are cheapest to use.

```
                        ┌────────────────────┐
                        │  engineering-lead  │  routes · resolves · owns the verdict
                        └──────────┬─────────┘
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
    ╔═══════════╗          ╔═════════════╗          ╔═════════════╗
    ║  WRITERS  ║          ║  REVIEWERS  ║          ║  ANALYSTS   ║
    ║ before    ║          ║ after code  ║          ║ before and  ║
    ║ code      ║          ║ exists      ║          ║ alongside   ║
    ╚═══════════╝          ╚═════════════╝          ╚═════════════╝
```

### Writers — carry the reviewers' rules at authoring time

| Agent | Owns |
|---|---|
| `implementation-engineer` | fail-loud paths, single source of truth, minimal diffs — **default for any task producing code** |
| `cpp-systems-engineer` | lifetime, ownership, const-correctness, UB |
| `automation-framework-engineer` | fixtures, mocks, harnesses, test infrastructure |
| `bdd-specialist` | Gherkin: boundary values, equivalence classes, negative scenarios |
| `senior-software-engineer` | architecture, framework code, refactoring |
| `devops-ci-engineer` | pipelines, parallelisation, artifacts |

### Defect-class reviewers — one class each, for code that already exists

| Agent | Hunts | Seen in the wild |
|---|---|---|
| `failure-mode-auditor` | silent-failure paths | `return []` on a missing dir → protocol written without those tests |
| `contract-integrity-reviewer` | two unvalidated sources of truth | a dir name string-matched against a JSON field; three dirs matched nothing |
| `test-efficacy-auditor` | tests that cannot fail | "identical" tests holding opposite branches of a default |
| `minimal-change-reviewer` | scope creep | a one-character request answered with +60 lines |
| `build-verification-engineer` | never-compiled code | a `const&` stored past its full-expression |

### Analysts and domain specialists

| Agent | Answers |
|---|---|
| `requirements-analyst` | is this requirement testable, complete, unambiguous? |
| `production-code-analyst` | what does this code actually do, and what are its branches? |
| `test-strategy-engineer` | what to test, at which level, and why |
| `documentation-traceability-engineer` | does requirement→test traceability hold? |
| `safety-qa-engineer` | Safety standards: alarms, fail-safe paths, hazardous states |
| `quality-metrics-specialist` | does this suite detect defects, or only pass? |

---

## Why this shape

Twelve findings on one pull request, sorted by root cause. Each cause became an agent.

| Root cause | n | Specialist it created |
|---|---|---|
| Silent-failure path | 5 | `failure-mode-auditor` |
| Two unvalidated sources of truth | 3 | `contract-integrity-reviewer` |
| Dead code / drift | 2 | — (caught by review) |
| Never compiled | 1 | `cpp-systems-engineer` + `build-verification-engineer` |
| Disputed test deletion | 1 | `test-efficacy-auditor` |

Every one was cheaper to prevent at authoring time than to catch in review. That is why the
writers carry the reviewers' rules, and why a reviewer spawned to find what a writer should not
have written is the expensive path.

```
   cost to fix
        │
   high │                                    ██  review
        │                          ██  test
        │                ██  build
    low │      ██  author
        └──────────────────────────────────────────►  time
```

---

## The agentic engineering loop

For any task that produces or changes code, writing the edit is the middle of the job, not the
end of it. The team owns the loop until it reaches a terminal state.

```
                        IMPLEMENT  ≠  COMPLETE

  RECEIVED
     │
     ▼
  ANALYZING ──► PLANNED ──► IMPLEMENTING
                                 │
                                 ▼
                            VERIFYING ────── pass ──────► COMPLETED
                                 │
                              failure
                                 │
                                 ▼
                            DIAGNOSING ── human needed ──► BLOCKED
                                 │
                                 ▼
                            REPAIRING
                                 │
                                 └────► VERIFYING          ≤ 4 iterations
```

The user never has to say *run it*, *fix that*, *check again* or *continue*. Those transitions
belong to the loop. It stops on a passing contract, an exhausted budget, a genuine blocker, or a
boundary that needs a person — and it says which.

### Three layers of verification, cheapest first

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

An agent's opinion that the code compiles is not a build. Never use a model to establish what a
deterministic check establishes reliably.

### A green test is not evidence until it can fail

```
  correct code  + test ──► PASS
  mutated code  + test ──► MUST FAIL      ← otherwise the test proves nothing
```

A surviving mutation has two very different causes, and reporting the wrong one is a false
finding:

```
mutation survives
        │
  is the branch reachable?
   ┌────┴────┐
reachable   never executed
   │             │
weak test    dead path — a coverage gap,
             not a weak assertion
```

Live example: a shared `JsonNumber` helper emitted `null` for non-finite doubles. Mutating `null`
to `nan` left the suite at an unchanged 23/26 — not because the assertions were weak, but because
1200 frames across every harness command emitted zero non-finite values. The branch never ran.

### Terminal states

| State | Meaning |
|---|---|
| `COMPLETED` | every required gate passed against fresh evidence |
| `PARTIALLY_VERIFIED` | implemented, one non-fatal verification limit remains |
| `BLOCKED` | needs a human decision, information, or authorization |
| `UNVERIFIED` | the change exists; correctness could not be shown |
| `FAILED` | not achievable within the repair budget |

**`DONE` is not a state.** It is what an agent says when it wrote code and stopped looking.

### Guards

```yaml
max_repair_iterations: 4     # then FAILED or PARTIALLY_VERIFIED, with evidence
max_same_failure_retries: 2  # then LOOP_DETECTED — stop, do not edit at random
max_flaky_retries: 3         # reruns classify; they never convert flaky into PASS
```

Autonomous **inside** the authorized scope. The loop never expands requirements, weakens or
deletes a test to reach green, nor commits, pushes, merges or releases on its own.

---

## Routing

The lead spawns **only the classes the change contains**. Zero is the normal answer for a diff it
can read itself.

```
   task arrives
        │
        ▼
   does it produce code? ──yes──► writers first (implementation-engineer default)
        │ no
        ▼
   does code already exist? ──yes──► which defect classes does the diff contain?
        │ no                              │
        ▼                                 ├─ reads metadata/aggregates? → failure-mode-auditor
   is it a question about              ├─ shared tags/manifests?     → contract-integrity-reviewer
   requirements or strategy?           ├─ claims coverage?           → test-efficacy-auditor
        │                              ├─ C++ headers/macros?        → cpp-systems-engineer
        ▼                              └─ diff larger than the ask?  → minimal-change-reviewer
   analysts
```

| Decision | Rule |
|---|---|
| How many specialists | cap 3; 0 is normal |
| Who picks them | the lead, never the caller |
| Who owns the verdict | the lead — a verdict assembled by concatenating reports is one nobody checked |
| What is never cut | verification that the change works |
| Who owns the loop | the lead — diagnosing and repairing are inside the task, not follow-up requests |

---

## Token cost control

Separate agents each carry a context. A fixed role keeps a brief small and a context clean, but
the cost is real, so the discipline is to spawn few and load little.

| Layer | Cost | When it is paid |
|---|---|---|
| `SKILL.md` | ~2k tokens | every invocation |
| One reference | ~0.8–2.6k | only when the task needs it |
| Memory (all four files) | ~2.1k | on demand |
| **One specialist agent** | **~40–80k** | **per agent — this is the real cost** |
| Whole knowledge base | ~24k | never load this |

**Progressive disclosure is the mechanism**: `SKILL.md` names which file answers which kind of
question, and the lead loads that one. Injecting the whole knowledge base into a task that needed
one rule is the failure mode the structure exists to prevent.

---

## Knowledge and evidence checks

Every finding QA filed in the project this team was built on was filed against a **generated
evidence document**, not against source. So are the checks.

```
   test run ──► pytest-assertions.json ──┐
                                          ├──► rendered evidence ──► check_evidence.py (21 rules)
   feature + steps ──► report generator ──┘                                  │
        │                                                                     ▼
        └──────────────────────────────────► check_source.py (7 rules) ──► exit 0 clean
                                                                             exit 1 findings
                                                                             exit 2 could not check
```

```bash
python skills/sdet-team/rag/check_evidence.py <reports-dir>
python skills/sdet-team/rag/check_source.py <suite-dir>
```

| Rule | Catches |
|---|---|
| R1 | Expected rendered from the measured side |
| R2 | bare truthiness rendered as `bool(x) == True` |
| R3 | a value compared against itself |
| R4 | the stimulus sits in a Given |
| R5 | a step claim with no assertion behind it |
| R11a–e | no step number · truncated value · unsubstituted placeholder · implementation in the Assertion column · identical rows under one step |
| R12 | the header does not identify the document |
| B1 | a step reports PASS and asserts nothing |
| B5 | a claim in the step description is not evidenced |
| E2 | a dash on a step that reports PASS |
| E4 | a promised data table is not rendered |
| E7 | Expected names a type, not a value |
| P2 | the row records no value |
| P3 | the row records a count, not which values |
| P4 | an absolute filesystem path in the record |
| P5 | an element present in some scenarios, missing from others |
| P6 | a whole record dumped where one value belonged |
| A1 | a collection filtered on the property it then asserts |
| A4 | an Examples row that makes two runs identical |
| A5 | an aggregate that passes over an empty collection |
| A6 | an equality whose two sides share one origin |
| A7 | a guard for a condition the guarded call already excludes |
| A8 | a bare truthy assert, rendered as `bool(x) == True` |
| B4 | step text that matches no scenario |

**Exit 2 exists on purpose.** A checker never reports clean for a check it did not perform.

`rag/test_known_defects.py` replays every defect a human reviewer filed by hand, reduced to
the rows that carried it, beside the corrected form. A rule is credited only when it fires on
the defect **and** stays silent on the fix.

---

## Governance

```
   observation → learning → analysis → recommendation → ║ HUMAN ║ → implementation
                                                        ║REVIEW ║        │
                                                            │        evaluation
                                                        rejected          │
                                                                     validation
```

| Change | Needs approval |
|---|---|
| a new rule in `rag/` | yes |
| a change to an agent definition | yes |
| a change to `SKILL.md` or a reference | yes |
| promoting a correction to a lesson | yes |
| installing anything | yes, always |
| recording a correction as a candidate | no — that is observation |
| running a checker | no |
| reporting a finding | no |

**The dividing line: observing and reporting are free; changing how the team works is not.**

### Never

- weaken an assertion to make a test pass
- change an expected value without evidence
- convert missing evidence into PASS
- assume a missing result means success
- invent traceability
- hide a missing requirement
- silently ignore unavailable authoritative information
- modify regulated evidence to satisfy a workflow
- alter the team without human approval

---
## Layout

```
agents/            18 specialist agent definitions (Claude Code subagents)
skills/sdet-team/  the control plane — entry point, invoked as /sdet-team
hooks/             optional Claude Code hooks that make the learning loop reliable
docs/              the source specification
install.sh         installs agents + skill into a project or into ~/.claude
```

The skill is the only part that exists in every session. Agents are spawned, MCPs come and
go, tools may or may not be installed — so the routing decisions live in the skill, and
everything else is a capability it detects and uses or works around.

```
skills/sdet-team/
│
├── SKILL.md              routing, what to load, what to run
│
├── references/           what the team knows
│   ├── architecture.md          the three layers and why
│   ├── qa-findings.md           the patterns QA has filed, in their words
│   ├── principles.md            the four properties that generate them
│   ├── qa-rag.md                the knowledge engine and its traceability chain
│   ├── capability-discovery.md  detection, fallbacks, deterministic-first
│   ├── learning.md              what to keep from a correction, and how to generalise it
│   ├── experience-memory.md     what a kept entry carries, its states, its relations
│   ├── trajectory.md            how a task was done — observable events, not reasoning
│   ├── reflection.md            post-task analysis, and when not to run it
│   ├── optimization.md          patterns across tasks, and what to propose
│   ├── evaluation.md            what counts as evidence that a change helped
│   ├── agentic-loop.md          the state machine, its budget, its terminal states
│   ├── completion-contract.md   what done means, derived before implementing
│   ├── verification.md          the three layers, cheapest and most certain first
│   ├── failure-classification.md  did this change cause it? then what
│   ├── test-integrity.md        a green test that cannot fail proves nothing
│   └── governance.md            the approval contract
│
├── workflows/            the step order for a named job
│   ├── report-review.md · review.md · implementation.md
│   └── test-design.md · investigation.md · daily-optimization.md
│
├── memory/               what use has taught
│   ├── lessons.md               generalised and recurred
│   ├── corrections.md           candidates, from human corrections
│   ├── patterns.md              recurring observations, with frequency
│   ├── strategies.md            approaches worth trying first
│   └── trajectories/            recorded task paths, when one is worth keeping
│
├── evaluation/           whether a change was an improvement
│   ├── benchmarks.md · regression.md · quality-gates.md
│   ├── agentic-loop-scenarios.md  the eight behaviours the loop must get right
│   ├── versions.md              what changed in the team, when, on what evidence
│   └── demo.md                  the whole loop, end to end, on one real correction
│
└── rag/                  the deterministic checks
    ├── check_evidence.py        21 checks over rendered evidence documents
    ├── check_source.py          7 checks the rendered row cannot answer
    └── test_known_defects.py    every human-filed defect, replayed against the rules
```

**Progressive disclosure.** `SKILL.md` stays short and says which file answers which kind
of question. A task about evidence documents loads `qa-findings.md`; a task about CI loads
neither. Injecting the whole base into a task that needed one rule is the cost this
structure exists to avoid — the same discipline as the specialist cap.

## Install

Into a specific project (recommended — the team then sees that repo's conventions):

```bash
./install.sh /path/to/your/repo
```

Into your user scope, available in every project:

```bash
./install.sh --user
```

The installer symlinks (default) or copies the agents into `<target>/.claude/agents/` and the skill
into `<target>/.claude/skills/sdet-team/`. Use `--copy` to copy instead of symlink. Symlinks mean a
`git pull` here updates every install.

## Use

```
/sdet-team review the alarm BDD suite on this branch
/sdet-team write scenarios for REQ-1442 covering the latching behaviour
/sdet-team our CI is flaky on the integration suite — find out why
```

Or address a single specialist directly when the task is narrow:

```
Use the bdd-specialist agent to review tests/features/alarms.feature
```


## Principles

Five of these came from defects that shipped, not from taste:

- **Absence is not agreement.** A missing directory, an empty result set, a lookup that
  misses — none mean "nothing to do". In a regulated record they mean *fail loud*: an
  incomplete record is worse than none, being indistinguishable from a complete one. Any
  opt-out is explicit and default-off.
- **Demonstrate the problem before defending against it.** An unreproduced guard is noise,
  and it costs the reviewer's trust in the whole diff.
- **Answer exactly what was asked.** One comment, one commit.
- **Two sources of truth is the finding.** Name which side is authoritative and what fails
  if they diverge; "nothing" and "a log line" are both findings.
- **If you build it, run it.** Follow the change to whatever consumes it and confirm it is
  there. Lint, import, collection and type-check prove nothing about behaviour.

- Prefer correctness over agreement.
- Challenge assumptions; never blindly trust a requirement.
- Verify production behaviour at `file:line` — never infer it from docs or tests.
- Prefer reusable automation over one-off scaffolding.
- Deliver production-quality output, ready to commit.
- Never commit or push unless explicitly asked.

## Learning hooks

The learning loop is an instruction to the model, and an instruction can be forgotten. Two
optional Claude Code hooks make it mechanical, without giving the team any new authority:

| Hook | Event | What it does |
|---|---|---|
| `hooks/correction-reminder.sh` | `UserPromptSubmit` | reminds the model, on every prompt, to record a correction in `memory/corrections.md` |
| `hooks/memory-autocommit.sh` | `Stop`, `SessionEnd` | commits changes under `skills/sdet-team/memory/` only — locally, never pushed, never failing the session |

Merge `hooks/settings.example.json` into `~/.claude/settings.json`, replacing
`/path/to/this/repo`. Every memory change then becomes a commit, so what the team learned,
and when, is one command away:

```bash
git log -p -- skills/sdet-team/memory
```

Recording a candidate is observation, so it needs no approval; promoting it, or changing
anything the team does, still goes through [Governance](#governance).

## Origin

The team, its rules and its memory were distilled from real review rounds on a regulated
software project. Everything project-specific — product, people, code, data and documents —
has been removed or replaced with neutral examples. The known-bad corpus that
`evaluation/benchmarks.md` measures against belongs to that project and is not included;
`rag/test_known_defects.py` is the self-contained part that reproduces here.

## License

No license is granted. The repository is published for demonstration; all rights are reserved.
