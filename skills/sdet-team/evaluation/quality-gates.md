# Quality gates

What has to be true before work is handed over. Not a checklist to recite — a set of
conditions, each of which has been violated at least once.

## Before reporting a finding

- [ ] Verified at `file:line`, not inferred from a tool's output
- [ ] Checked against `references/qa-findings.md` — is this shape actually the finding?
- [ ] If the checker did not raise it, does it fit a principle in `references/principles.md`?

## Before reporting a fix

- [ ] The suite ran, and passed, here
- [ ] The evidence documents were regenerated
- [ ] Both checkers were run on the regenerated documents
- [ ] The fix does not satisfy the rule while preserving the defect (`lessons.md` L2)
- [ ] Nothing was weakened to make a test pass

## Before reporting clean

- [ ] Every check actually ran — exit 2 is unchecked, not clean
- [ ] Anything unverifiable in this environment is named as UNVERIFIED
- [ ] The reports being checked are this run's, not an earlier one

## Before changing the team

- [ ] A human approved it (`references/governance.md`)
- [ ] The known-bad corpus still reports its baseline counts
- [ ] The current evidence still reports clean
- [ ] A new check has been shown to fire on input known to be bad

## The one that is easiest to skip

**Reports being checked are this run's.** A check against stale documents evidences
nothing about the change, and reports clean while the defect is still there. Regenerate
first.
