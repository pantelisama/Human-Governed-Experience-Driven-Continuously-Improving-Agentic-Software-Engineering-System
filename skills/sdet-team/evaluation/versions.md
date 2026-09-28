# Versions

The team is an artefact with a version. A change to how it works is a release, and a
release is auditable: what changed, on what evidence, who approved it, what it measured,
how to undo it.

Without this, "the team learned something" is unfalsifiable. With it, a version that made
things worse can be named and reverted.

## What counts as a version change

Anything on the approval side of `references/governance.md`: a new check in `rag/`, an
agent definition, `SKILL.md` or a reference, a correction promoted to a lesson.

Not: recording a candidate correction, running a checker, reporting a finding. Those are
observation, and observation does not bump a version.

## The entry

One block per version, appended here. Git holds the diff; this holds the reasoning that
the diff does not.

```yaml
version:
date:
changes:               # what moved, by file
driven_by:             # the recommendation id, and the experience ids under it
evidence:              # counted occurrences, not "we noticed"
approved_by:           # a person. "the team agreed" is not an approval
evaluation:            # benchmark numbers before and after — both
regression:            # evaluation/regression.md result
rollback:              # the commit to revert, and what returns to the previous behaviour
```

`evaluation` with one number is incomplete. A change is an improvement relative to a
baseline, and the baseline has to be stated to be argued with.

## History

### v0.1 — the team

```yaml
version: 0.1
changes: engineering-lead + 17 specialists; SKILL.md routing by defect class
driven_by: twelve review findings on one PR, sorted by root cause
evidence: 5 silent-failure, 3 two-sources-of-truth, 1 never-compiled, 2 drift, 1 disputed deletion
evaluation: not measured — this is the baseline
rollback: n/a
```

### v0.2 — knowledge and checks

```yaml
version: 0.2
changes: references/qa-findings.md, references/principles.md, rag/check_evidence.py,
         rag/check_source.py
driven_by: C1 — a source grep reported clean on a defective document
evidence: 68 bool(x) == True rows the reviewer counted by hand and the team's check missed
evaluation: worktree at <baseline-commit> reproduces QA's counts — R2 68, R11a 137, R3 12, R1 7,
            R12 7, R5 1. See evaluation/benchmarks.md
rollback: the checkers are standalone scripts; deleting them returns manual review
```

### v0.3 — the learning layer

```yaml
version: 0.3
changes: references/trajectory.md, references/experience-memory.md,
         evaluation/versions.md, evaluation/demo.md; SKILL.md disclosure table
driven_by: the SDET Agentic Evolution specification
evidence: none yet — this version adds the machinery to gather it
confidence: low on utility, high on cost being small
evaluation: pending. The measurable claim is that human correction rate falls; it needs
            trajectories from real tasks before it can be tested
rollback: the four files are additive and referenced only from the SKILL.md table
```

That last entry states its own weakness on purpose. A version added on a specification
rather than on counted evidence is a hypothesis, and recording it as one is what stops it
being cited later as a demonstrated improvement.
