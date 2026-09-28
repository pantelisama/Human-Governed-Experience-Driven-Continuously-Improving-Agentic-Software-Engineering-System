# Optimization

Reflection looks at one task. Optimization looks at several and asks what keeps happening.

It runs on demand — not during normal work. Injecting the optimizer into every task is the
cost it exists to reduce.

## What it looks for

Patterns across accumulated observations in `memory/`:

| Pattern | What it usually means |
|---|---|
| the same human correction twice | the lesson is not in the team's rules yet |
| the same manual check several times | a deterministic tool is missing |
| the same retrieval every task | the knowledge belongs in a reference, not a search |
| a specialist whose report never changes a verdict | the routing rule is wrong |
| a finding that returns after each fix | the fix addresses the symptom |
| large context retrieved and mostly unused | the retrieval is too coarse |

## The question to ask

Not *"do we need an MCP?"* but **"what capability is missing?"** — then look at the whole
range of answers:

```
an existing MCP · an existing skill · a CLI tool · a Python package
a deterministic checker · a RAG entry · a reference · better instructions
nothing (the frequency does not justify it)
```

"Nothing" is a legitimate outcome and often the right one. Two occurrences is a
coincidence; the bar is a pattern with evidence.

Check `capability-discovery.md` before proposing anything new — most gaps turn out to be
something that already exists and was not used.

## Worked example

> **Observed.** Report completeness checked by hand in six tasks.
>
> **Analysis.** The operation is deterministic: the sections are known, the check is
> presence.
>
> **Recommendation.** A `validate_report_completeness()` check in `rag/`.
>
> **Expected.** Lower token use, earlier detection, a result that does not vary with who
> ran it.

And the counter-example, which is the more useful one:

> **Observed.** A finding about `Expected == Actual` returned after four separate fixes.
>
> **Analysis.** Not a missing tool. The rule was being applied where its principle does
> not reach — an existence check has one source of truth, so no second operand exists to
> compare against.
>
> **Recommendation.** Not a new check. A paragraph in `principles.md` naming the tension,
> and a narrowing of the two rules so they stop reporting it.

The second one produced no code. That was the right answer, and an optimizer that only
knows how to propose tools would have missed it.

## Output

A short report, highest-value first. Each item carries its frequency and its evidence —
without those it is an opinion:

```
SDET Evolution Report — <date>

1. HIGH · repeated manual report completeness check
   Observed: 6 tasks
   Recommendation: deterministic validator in rag/
   Expected: lower token use, earlier detection

2. MEDIUM · human correction pattern
   Observed: 4 tasks
   Lesson: failure branches need explicit execution evidence
   Recommendation: strengthen test-efficacy-auditor guidance

3. LOW · coarse retrieval
   Observed: whole-report reads where one section was needed
   Recommendation: section-level retrieval
```

Recommendations go to a human. Nothing is installed, and nothing in the team changes,
until one is approved — `governance.md` is the contract.

## Deduplicate

Before adding a recommendation, check the ones already pending. The same gap observed
twice is one recommendation with a higher frequency, not two.
