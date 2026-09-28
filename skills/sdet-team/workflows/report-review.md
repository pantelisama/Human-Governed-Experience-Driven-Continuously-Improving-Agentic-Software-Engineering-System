# Workflow: review generated BDD evidence

The job QA does, done first. Every finding they have filed on this project was filed
against a generated document — so this reads the documents, not the source.

## Order

1. **Are the reports current?** A check against last month's documents evidences nothing
   about this change. If they are stale, regenerate:

   ```bash
   uv run pytest <suite-dir> -q
   uv run python -m <report_generator> <bdd-tests-dir> -c <component> \
       --test-level unit_tests --local
   ```

   `--local` marks every page UNCONTROLLED, which is correct for a local render and means
   the set cannot be filed as the verification record.

2. **Run both checkers.**

   ```bash
   python .claude/skills/sdet-team/rag/check_evidence.py <reports-dir>
   python .claude/skills/sdet-team/rag/check_source.py <suite-dir>
   ```

   Exit 2 means the check could not run — treat that as unchecked, never as clean.

3. **Verify each finding at `file:line` before reporting it.** Three of the rules were
   narrowed after firing on correct code; assume a finding might be one of those until
   you have looked.

4. **Read what the checkers cannot decide.** Four patterns need judgement —
   `references/qa-findings.md` names them and routes each. R7, a threshold with no stated
   source, is the class QA marked critical.

5. **Open one document.** The checkers read the HTML sidecar; the reviewer reads the PDF.
   Column widths, page breaks and truncation only show there.

## What to report

Per finding: the rule, the document and step, and the `file:line` you verified it at.
Anything you did not verify is UNVERIFIED, said plainly.

Two things are not defects and should be said rather than fixed: design-level-rather-than-system-level tags
(the mapping is not agreed) and the UNCONTROLLED banner on a local render.

## Do not

- Report clean from a source grep. `bool(x) == True` appeared 68 times in the PDFs while
  `grep -c 'bool(' test_*.py` returned zero.
- Weaken an assertion to clear a finding. If a fix makes a row less informative, it is not
  a fix — check it against `references/principles.md`.
