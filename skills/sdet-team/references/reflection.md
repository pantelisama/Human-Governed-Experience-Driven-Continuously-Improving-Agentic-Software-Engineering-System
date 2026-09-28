# Reflection

After a task that went wrong, or went long, ask what happened. Not after every task — a
task that worked teaches nothing worth the tokens.

**Reflection never changes anything.** It produces an observation, and an observation that
recurs becomes a recommendation. See `governance.md`.

## When

- a human corrected the team
- a finding the team reported closed came back
- the same operation was done by hand several times
- a specialist was spawned that the change did not need, or one was missed
- the task took markedly longer than its shape suggested

Not: every task, every PR, every review.

## The questions

Short, and in this order:

1. What happened?
2. What was correct?
3. What was wrong?
4. **Why** was it wrong — which of these?

   | Cause | Looks like |
   |---|---|
   | missing knowledge | the team did not know a rule that exists |
   | poor retrieval | the knowledge was there and not loaded |
   | bad routing | the wrong specialist, or none |
   | weak instruction | the agent did what it was told; the telling was wrong |
   | missing capability | no tool could answer the question |
   | incorrect reasoning | everything was available and the conclusion was still wrong |
   | missing verification | nobody checked the claim |
   | inefficient workflow | right answer, too many steps |
   | human ambiguity | the request could be read two ways |

5. Could it happen again?
6. Does the lesson generalise beyond this task?

Question 4 is the one that matters. "The team missed X" is not a cause; "the check read
the source instead of the rendered document" is.

## Trajectory, not just the answer

When the task is one of the cases above, record the path as it ran —
`references/trajectory.md` has the shape. Reflection reads it; without it the cause has to
be reconstructed from memory.

A correct final answer reached badly is still a problem. Where it is cheap to see, look at
the path:

```
task → planning → retrieval → agent selection → tool use
     → reasoning → implementation → tests → verification → result
```

Signals worth noticing: the same search run twice, an approach tried and abandoned then
tried again, a specialist whose report changed nothing, context retrieved and unused, a
manual operation that a script could do, a human correcting the same thing twice.

Each of those is input to `optimization.md`, not a finding on its own.

## Worked example

> **What happened.** The team reported the `bool(x) == True` finding closed. The reviewer
> found 68 of them in the same documents.
>
> **Why.** Not missing knowledge — the rule was understood. **Poor retrieval, in the
> literal sense**: the check ran `grep -c 'bool(' test_*.py` against the source, and the
> rows exist only in the rendered output, because the generator wraps
> every bare `assert x`.
>
> **Again?** Yes, for any rule about the document rather than the code.
>
> **Generalises?** Yes: *count what the reviewer reads.*

That observation became the opening paragraph of `qa-findings.md` and the reason both
checkers read the rendered evidence.

## Keep it short

Reflection that costs more than the task it examines is not worth running. A few
sentences, the cause named, and either a candidate lesson in `memory/corrections.md` or
nothing.
