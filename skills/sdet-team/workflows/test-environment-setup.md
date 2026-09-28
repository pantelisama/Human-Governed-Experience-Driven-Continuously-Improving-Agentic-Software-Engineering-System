# Workflow: getting a test suite to actually run

## "Run the test suite" means run it now

It is an instruction, not a topic. Run the suite first; read this file only when a step
fails. Do not open a plan, survey the repo, or ask what the user meant by running tests.

```bash
<device-cli> build deploy run --suite <name> --release --reports
```

Long runs go to the background with output to a file, and you watch the file (step 6) —
that is how you run it immediately *and* keep seeing it. Reading this whole workflow up
front is the failure it exists to prevent.

Two things, and only these two, are worth one line before starting:

- **Where** — host or device. The device tool's suite flag, or the host task. If the user
  named a device, that is the answer; do not ask again.
- **Reports** — often off by default on a device run. Pass the flag.

Everything below is diagnosis for when a step fails. Read the section you landed in.

---

Run the checks below **before** claiming a suite passes, and **before** concluding that a
slow or failing run is the code's fault. Every one cost real time in a session where the
code was correct from the start and four environment faults were mistaken for code faults.

The order matters: each step's failure mode is invisible until the one above it passes.

---

## 0. Where the run happens

Host, target device, or both — the report must name it. A host run reported as a device
run is a false record, and in a regulated suite that is the expensive kind of wrong.

If the user named the environment, that settles it: run there. Ask only when nothing in
the request or the repo answers it. If a device run is blocked, run on the host, say which
ran, and mark the other **UNVERIFIED** — never silently substitute one for the other.

---

## 1. Is the binary under test current?

A stale binary is the single most misleading failure: the suite fails, the diff looks
wrong, and the code is fine. Compare the **source's** interface against the **built**
artefact — never trust a timestamp alone.

```bash
# What the source offers
grep -oE '"(config|run|measure|report)"' <harness>.cpp | sort -u
# What the binary actually contains
strings <build>/bin/<harness> | grep -xE "config|run|measure|report" | sort -u
```

A subcommand or JSON field present in the source and absent from the binary means the
build is old. Symptoms that mean *rebuild*, not *debug*:

- `KeyError: '<field>'` on a field the source clearly emits
- a harness subcommand exiting non-zero for no stated reason

Check this on **every** architecture the suite will run on. A fresh x86 binary says
nothing about the aarch64 one.

---

## 2. Separate pre-existing failures from yours

Before attributing a single failure to the change:

```bash
git stash push -u -m "wip-$$"
git stash list --format='%H %gs' | head -1     # capture the SHA immediately
<run the suite>                                 # this is the baseline
git stash apply <sha> && git stash drop <n>
```

Same failures with and without the change ⇒ pre-existing. Say so explicitly and do not
spend the session on them. (Never bare `git stash pop` — the stack is shared across
worktrees.)

---

## 3. Build inputs fetched from outside the repo

Version-pinned artefacts (model weights, filter taps, reference datasets) are downloaded,
not committed. An expired cloud session fails the download, and the build then dies in a
code-generation step that looks unrelated to the test.

```bash
aws sts get-caller-identity     # or the equivalent for the credential in play
<task that fetches the pinned build inputs>
<task that fetches the suite's datasets>
```

Two distinct failure shapes, and only one is survivable:

| Missing thing | What happens |
|---|---|
| A **dataset** | Falls back to the local copy if present — the run may proceed |
| A **build input** | The generator aborts; **nothing compiles**, host or target |

If a download fails, fix the credential. Reconstructing a build input locally is a
diagnostic step only: it may prove the rest of the pipeline works, but a regulated record
must be built from the pinned artefact. Say clearly which one produced the evidence.

---

## 4. Worktree-specific faults

A git worktree does not carry what git does not track. These are absent by definition, and
each one fails far from its cause.

| Missing | Symptom |
|---|---|
| `.venv` (or a shell of one, with no interpreter) | A deploy/helper script dies on `.venv/bin/python: No such file or directory` |
| tool `.env` (device host, user, profile) | The tool tries to lease a device from a broker and demands a CI token |
| Untracked sources another branch left behind | `CMake Error: Source file ... expected but not found` |

Fixes:

```bash
# Recreate the environment properly — do not hand-patch symlinks into it.
# A venv is located by its own path; pointing its python at another env's
# interpreter does not give it that env's packages.
rm -rf .venv && env -u VIRTUAL_ENV UV_PROJECT_ENVIRONMENT=.venv uv sync

# Copy the gitignored config from the primary checkout, and verify it holds no secrets
grep -vE "PASSWORD|TOKEN|SECRET|KEY" <primary>/<tool>/.env
```

For untracked sources from **another ticket** that break configure: move them aside, build,
then **put them back**. They are someone's work in progress — never delete them, and record
where they went.

---

## 5. A slow run is a diagnosis, not a wait

If a build or scan runs far longer than expected, stop watching and measure. One command
separates *working slowly* from *blocked*:

```bash
cat /proc/<pid>/wchan          # what the kernel is waiting on
awk '{print "utime="$14" stime="$15}' /proc/<pid>/stat
grep ctxt_switches /proc/<pid>/status   # sample twice, a few seconds apart
```

Read it as:

- **`stime` ≫ `utime`** — the process is not computing, it is waiting on I/O
- **`voluntary_ctxt_switches` climbing fast** — many small blocking syscalls, not one hang
- **counters frozen** — genuinely stuck
- **state `T`** — *stopped*, not busy. Something sent SIGTSTP (a stray Ctrl+Z). Nothing will
  ever finish. `kill -CONT <pid>`, and kill any older stopped run first: stopped processes
  hold build-tree locks and silently block every later attempt.

**Known cause, WSL2:** `wchan` reading `p9_client_rpc` means the process is blocked on the
9P protocol — a Windows filesystem crossing. The usual source is Windows entries inherited
into `PATH`, so every tool lookup becomes a round trip to the host OS.

```bash
echo "$PATH" | tr ':' '\n' | grep -c "^/mnt/"     # non-zero on a default WSL shell
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "^/mnt/" | paste -sd: -)
```

Observed cost: 94% of wall time in I/O wait, ~1700 context switches/second, a configure
step that normally takes seconds running for tens of minutes.

---

## 6. Run it where you can see it

Long runs go to the background with the output on disk, then watch the file. A foreground
run shows nothing until it ends, and a permission prompt or a stray Ctrl+Z both look
identical to "still working".

Filter for **both** outcomes. A filter that matches only success is silent through a crash,
which is indistinguishable from progress.

```
Linking|Built target|CMake Error|Error [0-9]|Traceback|PASS|FAIL|passed|failed|Exit code
```

---

## 7. Blocked by a permission gate

When a command is refused, it did not run — that is not a result, and it is not the code's
fault. Rules:

1. **Do not retry it unchanged.** A refusal is an answer.
2. **Do not reach for the tool the gate sits in front of.** Hand-running the deploy that
   the gate stopped is working around the intent, not around the obstacle.
3. **Never grant yourself the permission.** Writing your own allowlist entry is refused by
   design.
4. Say plainly what was refused, hand over the exact command, and offer the allowlist entry
   as something the user applies.

Everything not blocked gets finished first, so the handover is one command, not a task.

---

## 8. Device runs: what actually runs where

Before reporting a device run, know the topology — it is rarely "the tests ran on the
device".

A common shape: **the test driver runs on the host; only the binary under test is executed
on the target over SSH.** Results, and therefore the evidence record, are written
host-side. An env var selects the target, another tells it where the deployed binary lives.

Consequences worth stating in the report:

- Datasets may upload to the device on demand at first reference, not at deploy time
- Report rendering is often **off by default** on a device run — an explicit flag is needed,
  or the run leaves raw JSON and no readable evidence
- The device path may be a *different command* from the CI path. CI scripts usually claim a
  device from a broker unconditionally; the developer path uses a configured host. Reading
  the CI script to learn the mechanism is right; running it as a developer usually is not.

---

## Before saying it passed

- [ ] The run happened on the environment that was asked for, and the report names it
- [ ] The binary was rebuilt from current source, on **that** architecture
- [ ] Pre-existing failures were separated from the change's, by baseline
- [ ] Evidence was built from pinned artefacts, or the substitution is stated
- [ ] Assertions were read for the **values** they recorded, not just for PASS
- [ ] Anything moved aside during the run was put back
- [ ] Anything not executed is marked **UNVERIFIED**, in the first line, not a footnote
