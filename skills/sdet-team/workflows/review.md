# Workflow: review a change

## Order

1. **Read the diff yourself.** Most changes hit one or two defect classes, and a lead that
   has read the diff spawns fewer specialists than one that has not.

2. **Route by what the change contains**, not by what it touches. The table in
   `.claude/agents/engineering-lead.md` maps class to specialist. Cap 3; zero is the
   normal answer for a diff you can read.

3. **Verify the change runs.** Never scope this out. If the build or the suite could not
   run here, say so first — not as a footnote.

4. **Verify every blocking finding at `file:line`** before it reaches the user. A
   specialist has been wrong: one reported an acceptance criterion unasserted when it was
   asserted two lines away.

5. If the change touches BDD tests, the report generator or evidence documents, run
   `workflows/report-review.md` as well.

## What to report

The verdict, what changed, blocking findings, and what the user must decide. Not the
reasoning, not the tool calls, not the intermediate steps.
