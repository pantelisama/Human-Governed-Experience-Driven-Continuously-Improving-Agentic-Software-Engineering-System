# Learning from use

The team gets better by keeping what it learned and discarding what it did not. The hard
part is not storage — it is deciding what is worth keeping, and generalising it enough to
apply next time without being so general it says nothing.

## What counts as a signal

In descending order of value:

1. **A human correction.** Someone told the team it was wrong. This is the strongest
   signal available and the cheapest to miss.
2. **A finding that came back.** The team reported something fixed and a reviewer found
   it again — the fix addressed the symptom, not the cause.
3. **Repeated manual work.** The same deterministic operation done by hand more than a
   few times is a missing tool.
4. **A wrong route.** A specialist spawned for a defect class the change did not contain,
   or one that should have been spawned and was not.

Everything else is noise. A task that went well teaches nothing that needs recording.

## Generalise, do not transcribe

The mistake is storing the correction verbatim:

> Human: "No. It doesn't verify the failure branch."
>
> Stored: *"Check failure branch."*

That helps only on the identical task. The lesson is the principle underneath:

> *A test must demonstrate the intended failure branch, not merely execute the
> surrounding happy-path code.*

Worked example from this project. The team ran `grep -c 'bool(' test_*.py`, got zero, and
reported a finding closed. The reviewer found 68 of them in the PDFs. Verbatim, the
lesson is "grep the HTML". Generalised:

> *Count what the reviewer reads. A generated document contains rows the source does not:
> the generator manufactures them. A check against the source can report clean on a
> document full of the defect.*

That one now sits in `references/qa-findings.md` and shaped the whole checker.

## Then decide what kind of lesson it is

`references/experience-memory.md` has the facts each entry carries and the states it moves
through. This section decides which file it lands in.

| Kind | Where it goes |
|---|---|
| one-off — a typo, a local accident | nowhere |
| project-specific — true of this repo | `memory/lessons.md`, scoped to the repo |
| general principle — true of any regulated suite | `references/principles.md` |
| a rule a script can enforce | a check in `rag/`, plus an entry in `references/qa-findings.md` |

Promotion needs recurrence. A single unusual event does not change how the team works;
`memory/corrections.md` holds candidates, and a correction that arrives twice earns a
place in `memory/lessons.md`.

## Curate, or it rots

Uncontrolled memory growth is its own failure: a lessons file nobody can read is a
lessons file nobody loads. So:

- a lesson contradicted by a later one is **superseded**, not left alongside it;
- a lesson about code that no longer exists is **removed**;
- two lessons saying the same thing are **merged**;
- a lesson that has not applied in a long time is **deprecated** rather than deleted, with
  a note saying why.

Check for these when you add an entry, not on a schedule.

## What not to store

- whole conversations
- task transcripts
- anything already in the repo (code structure, git history, CLAUDE.md)
- anything true only of one conversation
- a lesson you cannot state in two sentences

If a lesson needs a paragraph to state, it is probably two lessons or none.
