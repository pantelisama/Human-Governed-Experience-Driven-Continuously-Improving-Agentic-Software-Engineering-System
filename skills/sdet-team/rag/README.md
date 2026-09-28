# QA evidence knowledge base

Two files. Neither is an agent — this is a capability the `engineering-lead` and its
specialists use, which is what `report_review_rag.txt` asks for.

| File | What it is |
|---|---|
| `qa-findings.md` | The fifteen patterns QA has raised, in their words, with the rule each implies and the shapes that are *not* the finding |
| `principles.md` | The four properties that *generate* those patterns — for judging a defect nobody has named yet |
| `check_evidence.py` | 21 checks over the rendered evidence documents |
| `check_source.py` | 7 checks that need the step definitions and the feature file, because the row looks identical either way |

## Run it

```bash
python .claude/skills/sdet-team/rag/check_evidence.py \
  artifacts/<project>/docs/reports/bdd/unit_tests
```

Exit status: `0` clean, `1` findings, `2` could not check (no evidence directory, or the
documents parsed to nothing). It never reports clean for a check it did not perform.

`--json` for machine-readable output.

## Why it reads the reports, not the source

Every finding QA has filed on this project was filed against a **generated evidence
document**. So does this.

The reason is not stylistic. `bool(x) == True` appeared 68 times in the PDFs while
`grep -c 'bool(' test_*.py` returned zero, because the report generator
wraps every bare `assert x`. Checking the source produced a
clean all-clear on a document full of the defect, and the finding came back.

## What is checked mechanically

| Rule | Pattern |
|---|---|
| R1 | A failing row whose two columns agree |
| R2 | Bare truthiness rendered as `bool(x) == True` |
| R3 | A value compared against itself |
| R4 | The stimulus sits in a Given |
| R5 | A step claim with no assertion behind it |
| R11a–e | Orphaned rows, truncated values, unsubstituted placeholders, implementation leaking into the Assertion column, identical rows under one step |
| R12 | The header does not identify protocol, commit, branch or approval state |
| B1 | A step reports PASS and asserts nothing |
| E2 | A dash in the Assertion cell on a step that passed |
| E4 | A step promising a Gherkin data table that is not rendered |
| E7 | Expected names a type (`in collection`) instead of a value |
| P2 | The Actual cell carries no value — a bare `True`, or a type name |

And from the source (`check_source.py`):

| Rule | Pattern |
|---|---|
| A1 | The step's claim is the equality that selected the rows |
| A4 | An Examples row whose neutral value makes two runs identical |
| A5 | An aggregate that passes over an empty collection |
| B4 | Step text that matches no scenario |

## What needs a specialist

Four patterns need judgement the checker cannot supply. This table is the one copy;
`SKILL.md` and `engineering-lead.md` point here rather than restating it.

| Rule | Pattern | Route to |
|---|---|---|
| R7 | A threshold or expected value with no stated source — QA marked this class **critical** | `test-efficacy-auditor` |
| R8 | An expectation derived from the output under test | `failure-mode-auditor` |
| R13 | No failure path in the scenario set | `test-strategy-engineer` |
| R15 | An acceptance criterion that cannot fail as configured | `requirements-analyst` |

R14 (a scenario that bypasses the production entry point) is a regulatory-QA decision, recorded
rather than fixed.

## Deliberately not checked

Two findings recur and are not code defects:

- **Design-level rather than system-level requirement tags.** The mapping is not agreed. Retagging without
  it writes false traceability into a regulated record.
- **UNCONTROLLED banner, "build unknown".** Correct and honest for a local render. It
  means the set cannot be filed as the verification record until CI regenerates it.

## What it catches, measured

Run against the documents QA actually reviewed — a worktree at `<baseline-commit>`, the state
their first two reports were written on — and against the current branch:

| Rule | QA baseline | Now |
|---|---|---|
| R1 Expected from the measured side | 7 | ok |
| R2 `bool(x) == True` | **68** | ok |
| R3 value compared against itself | 12 | ok |
| R5 claim with no assertion | 1 | ok |
| R11a orphaned rows | 137 | ok |
| R12 header does not identify the document | 7 | ok |

The 68 is the figure QA counted by hand. Reproducing it is the evidence that the checker
reads the documents the way the reviewer does.

## Picking it up

Agent definitions are read when a session starts. If `engineering-lead.md` changed during
a session, the running agent keeps the prompt it was launched with — verified by asking a
fresh one to quote the section back, which it could not. The wiring takes effect in the
next session. Until then, invoke the checker yourself.

## Limits

- The checker parses the HTML sidecars the renderer writes next to each PDF. If
  the evidence template changes its table markup, `read_rows` needs updating — it
  exits `2` rather than reporting a clean result it did not verify.
- R5 matches a fixed vocabulary of step nouns (`fault state`, `lag of`, `sample_age`,
  `quality metric`, `NaN or Inf`, `packetMismatch`). A new scenario using different
  words needs an entry in `claims`.
- R3 flags two specific shapes. A novel way of comparing a value against itself will not
  be caught; `../references/qa-findings.md` describes the class so a reader can recognise it.
- No vector store, no embeddings. The corpus is three review documents and one test
  suite; lexical rules over the rendered evidence answer the question the reviewer asks,
  and a retrieval layer would add infrastructure without adding findings. If the corpus
  grows past what one file can hold, `report_review_rag.txt` describes the fuller design.

## Sources

`<repo>/tests/bdd_tests/unit_tests/test_suites/<suite>/audit/`

- `Review comments 16 Sep2026.docx` — per-step findings and seven cross-cutting actions
- `Review comments 16 Sep2026_1.docx` — the follow-up round
- `findings_qa_review.docx` — the per-scenario analysis, including what the tests do well

## P3, P4, P5 — added after the "all fixed?" miss

Three rules from one session in which the team declared 14 findings closed while three
were still live in the evidence. Each reproduces a finding a human had to file by hand.

| Rule | What it catches | The finding it came from |
|---|---|---|
| **P3** | `len(x) > 0` rendering a bare count | *"SCN-86 step 2 still has len(ctx.config) > 0 with Actual 7"* — the guard passed, the row proved only that seven of something existed |
| **P4** | an absolute path in a cell | a harness path under `/home/<user>/…` evidences the machine, not the build |
| **P5** | an element in most documents, missing from a few | *"parameter table at the top for every test, not only 84 and 91"* — a half-applied fix |

P5 matches on the step's **shape**, not its wording: a rendered data-table step is the
same kind of evidence whether the sentence says "these parameters" or "these settings".
Matching text flagged three legitimate scenarios and would have trained the reader to
ignore the rule.

P3 is P2's sibling. P2 catches `Actual: True`; P3 catches `Actual: 7`. Both answer the
same question — *what did the software actually produce?* — and a count answers it no
better than a boolean. A count is fine when the step itself names the number, so the rule
skips a row whose Actual appears in its own description.

## A6, A7, A8 — added after the "fake declarations" miss

Three rules from a session in which five findings of the form "this assertion cannot
fail" were reported closed, and three of the fixes could not fail either.

| Rule | The shape it catches | What was shipped |
|---|---|---|
| A6 | an equality whose two sides are one local expression measured twice | `reference = ctx.reference[start:]` then `assert len(reference) == len(ctx.reference) - start` |
| A7 | a guard for a condition the guarded call has already excluded | `assert find_binary(BINARY).is_file()`, where `find_binary` raises on a missing path |
| A8 | a bare truthy assert, which the document renders as `bool(x) == True` | `assert lines` — thirty such rows reached one set of PDFs from two lines of source |

A6 is deliberately narrow. Comparing a measurement against a reference legitimately
mentions the same object, so it fires only when both sides are locally assigned names
built from an identical set of roots, with measuring builtins (`len`, `sorted`, `sum`)
excluded — that is the shape a restatement takes. Measured on the two reviewed suites: it catches the shipped defect and reports nothing on either.
