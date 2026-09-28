# Workflow: investigate a failure

## Order

1. **Reproduce it.** A failure you have not seen is a hypothesis.

2. **Read the actual output** — the assertion message, the captured values, the exit
   status. Not the summary line.

3. **Find the first thing that is wrong**, not the first thing that failed. A failing
   assertion is often three steps downstream of the defect.

4. **Check whether it is the test or the code.** Both are possible, and the answer changes
   who owns the fix. If the test is wrong, the fix is not to relax it.

5. **Check the evidence path.** A failure that only appears in the generated document —
   truncation, a missing row, an orphaned step — is a generator defect, and fixing the
   test will not touch it.

6. **Say what you could not run.** An investigation that could not reproduce is
   UNVERIFIED, however plausible its conclusion.
