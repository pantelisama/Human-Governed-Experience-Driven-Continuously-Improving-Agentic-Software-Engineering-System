# Trajectory

What the team records about *how* a task was done, not just what it concluded.

A verdict alone cannot be reflected on. "The team missed the 68 rows" is an outcome; "the
check ran against `test_*.py` when the rows exist only in the rendered HTML" is a cause,
and only the path shows it.

**Observable events only.** Routing decisions, retrievals, tool calls, verification steps,
outcomes, human feedback. Never model internals, never hidden reasoning, never a
transcript. If it could not be seen from outside the agent, it is not a trajectory event.

## When to record one

Not every task. Record when the task is one reflection would later want to read:

- a human corrected the team
- verification failed, or could not run
- a specialist was spawned whose report changed nothing
- the task is a benchmark run being compared against a baseline

Otherwise the cost of recording exceeds the value of having it.

## Shape

```yaml
trajectory_id:            # T-<date>-<n>
task:                     # one line, what was asked
task_type:                # review | implementation | test-design | investigation | report-review

context:
  repository:
  branch:
  relevant_files:         # paths, not contents

plan:                     # the steps intended, before execution

agent_routing:
  lead:
  specialists:            # each with the defect class that justified it

retrieval:
  project_knowledge:      # files/docs read, with the question each answered
  experience_knowledge:   # which memory/ or references/ entries were loaded

actions:                  # tool calls that changed something, or produced evidence

verification:             # what ran, and its exit status — "not run" is a valid value

outcome:
  status:                 # VERIFIED | PARTIALLY VERIFIED | UNVERIFIED
  findings:
  tests:

human_feedback:           # verbatim here; generalisation happens in memory/corrections.md

metrics:
  duration:
  tokens:
  tool_calls:
  specialists_used:
```

Fields with nothing to say are omitted, not filled with placeholders. An empty
`verification` block and a missing one mean different things — write `not run` and why.

## Where they go

`memory/trajectories/` as one YAML file each. They are inputs to
`references/reflection.md` and `workflows/daily-optimization.md`, and they are **not**
experience: a trajectory says what happened once, a lesson says what to do next time.

Trajectories age out. Once the observations in one have been promoted to
`memory/corrections.md` or discarded, the file has served its purpose — keep the ones
still feeding an open pattern, drop the rest.

## The one worked example

The `bool(x) == True` miss, as a trajectory, is the reason this file exists:

```yaml
trajectory_id: T-baseline-01
task: confirm the bool(x) == True finding is closed
task_type: report-review
retrieval:
  project_knowledge: [test_signal_sync.py]     # <- the cause is visible here
verification:
  - cmd: grep -c 'bool(' test_*.py
    result: 0
outcome:
  status: VERIFIED          # <- and wrong
human_feedback:
  - "68 of them, in the PDFs"
```

The defect is in `retrieval`, one line, visible without reading any reasoning. That is the
whole argument for recording the path.
