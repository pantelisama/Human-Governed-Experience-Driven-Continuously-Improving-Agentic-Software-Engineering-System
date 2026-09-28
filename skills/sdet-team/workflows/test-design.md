# Workflow: write or strengthen a test

## Order

1. **Read the requirement and the production code** before writing anything. A test
   written from the requirement alone asserts the requirement; one written from the code
   alone asserts the code. Both are needed to find the disagreement between them.

2. **Decide the level.** IEC 62304 unit vs integration vs system is not a preference — see
   the repo's CLAUDE.md, where those words collide with their everyday meanings.

3. **Two independent origins per assertion.** One side from the software, one from the
   specification. A threshold copied from watching the software makes the test assert the
   software against itself, which QA marked as the critical class.

   The worked case: a lag table held `negative_delay: 22`, taken from observed behaviour.
   The file declares `meta/true_delay_s = -18 samples`. Sweeping the lag showed every
   correlation peak at a negative value — the metadata was right, the hardcoded number was
   wrong, and it had been masking the only scenario written for a negative delay.

4. **Make each step's claim answerable.** The step sentence is the claim; the assertions
   under it are the evidence. Every quantity and identifier the sentence names has to
   reach the record — `references/qa-findings.md`, rule B5.

   A step reading "fed as 13 batches of 128 samples" whose row shows `(60, 128)` leaves an
   auditor asking how 13 was proved.

5. **Put the evidence under the step that claims it.** An auditor reads step by step, so a
   check filed under a neighbour does not count. Where a Given claims something only the
   run can show, move the *claim* into a Then rather than leaving it unevidenced.

6. **Cover the failure branch.** A test that only executes the happy path around a failure
   branch has not tested it.

7. **Guard against vacuous passing.** An `all()` over a possibly-empty collection passes
   when nothing happened.

8. **Run it, then read the evidence document it produces.** A test can be correct and its
   record still evidence nothing — that gap is most of what QA files.
