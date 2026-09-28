# Strategies

Approaches that worked, kept so they are not rediscovered. Not rules — a strategy is a
default worth trying first, and abandoning when it does not fit.

---

## S1 — Measure a new check against known-bad input

Create a worktree at the commit the reviewer was reading, regenerate the documents from
that state, and run the check. If it cannot find the defect class in the corpus that
provably contains it, it has not been demonstrated.

The baseline is `<baseline-commit>`. It reproduces the reviewer's hand count of 68.

---

## S2 — Narrow a rule by the shape the reviewer named, not by the field

A rule matching "the step mentions `sample_age`" fires on every step that mentions it. A
rule matching "the equality that selected the rows is the claim the step makes" fires on
the defect. The reviewer's own wording is usually the narrower and more accurate form.

---

## S3 — When two rules conflict, ask which one the row can serve

Not "how do I satisfy both" — that produced four rewrites. A row with one source of truth
cannot serve a two-origin rule at all; it can serve the record-the-value rule. Naming
which principle applies resolves it; chasing both alternates forever.

---

## S4 — Read the artefact the reviewer reads, at least once

The checkers parse the HTML sidecar because it holds untruncated values. The reviewer
reads the PDF, where column widths clip and page breaks orphan rows. Both are needed:
28 clipped cells were invisible in the sidecar and obvious in the PDF.
