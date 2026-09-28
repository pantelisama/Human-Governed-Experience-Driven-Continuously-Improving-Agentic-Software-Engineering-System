# Workflow: daily optimization

On demand, not during normal work. `references/optimization.md` has the reasoning; this is
the order.

## Order

1. **Collect** recent entries from `memory/corrections.md` and `memory/patterns.md`.

2. **Look for repetition** — the same correction, the same manual check, the same
   retrieval, the same specialist whose report changed nothing.

3. **For each pattern, ask what capability is missing** — and check
   `references/capability-discovery.md` before proposing anything. Most gaps turn out to
   be something that already exists and was not used.

4. **Deduplicate** against pending recommendations. The same gap observed twice is one
   recommendation with a higher frequency, not two.

5. **Write the report** — highest value first, each item carrying its observed frequency
   and its evidence. Without those it is an opinion.

6. **Stop there.** Recommendations go to a human. Nothing is installed and nothing in the
   team changes until one is approved.

## The outcome that is easy to miss

"No recommendation" is a legitimate result. Two occurrences is a coincidence.

And some patterns resolve to a paragraph rather than a tool. A finding about
`Expected == Actual` returned after four separate fixes; the cause was a rule being
applied where its principle does not reach, and the fix was a note in
`references/principles.md` plus a narrowing of the two rules. An optimizer that only knows
how to propose tools would have proposed a fifth rewrite.
