# Patterns

Recurring observations that are not yet lessons: things that keep happening, recorded so
the optimizer can see frequency rather than guess at it.

A pattern becomes a recommendation when it has enough occurrences to justify the cost of
acting on it. `workflows/daily-optimization.md` has the process.

---

## P-01 — A finding returns after each fix

**Observed.** Four rewrites of one assertion, alternating between two rules.

**What it means.** Usually a rule applied where its principle does not reach, not a bad
fix. Check `references/principles.md` before the fifth attempt.

**Resolution.** Documented rather than automated — see `lessons.md` L3.

---

## P-02 — A new rule fires on correct code

**Observed.** Three times: R5 on derived variable names, A1 on a filter selecting a
different property than the assertion checked, R11b on wrapped cells three separate times.

**What it means.** A rule written from one example generalises badly. The narrowing is
part of writing the rule, not a later fix.

**Cost of not acting.** A standing false positive teaches people to skim, and the next
real finding gets skimmed with it.

---

## P-03 — Report regeneration is manual and multi-step

**Observed.** Run the suite, regenerate with `--local`, copy to the other filesystem, run
two checkers. Repeated many times in one session.

**What it means.** Deterministic, ordered, and currently held in someone's head.

**Candidate.** A single entry point. Not proposed yet — the sequence is stable but the
paths are environment-specific.
