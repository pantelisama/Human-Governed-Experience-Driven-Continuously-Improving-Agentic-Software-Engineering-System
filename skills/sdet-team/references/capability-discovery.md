# Capability detection

The skill is the control plane. MCPs, CLI tools and local scripts are **capabilities** —
things that may or may not exist in the session you are running in. The same skill has to
behave the same way across accounts where a different set is connected.

So: never assume a capability exists, and never fail because an optional one does not.

## The rule

```
need something
      │
      ▼
is the capability available here?
      │
   ┌──┴──┐
  yes    no
   │      │
   ▼      ▼
 use it   is there another path to the same evidence?
              │
           ┌──┴──┐
          yes    no
           │      │
           ▼      ▼
      use it    report UNVERIFIED
```

The last box matters more than the others. **Never silently substitute weak evidence for
authoritative evidence.** If the authoritative source is unavailable, the answer is
`UNVERIFIED`, not a best guess dressed as a finding.

## How to detect

Capability detection is cheap and concrete — do it, do not reason about it:

| Capability | How to tell |
|---|---|
| an MCP | its tools appear in the tool list, or a `<system-reminder>` says the server failed to connect |
| a CLI tool | `which <tool>` (`pdftotext`, `gh`, `conan`, `cmake`) |
| a Python package | import it in a one-line `python -c` |
| the C++ build | the binary exists under the configured binary dir |
| a report | the artefacts directory has this run's files, not last week's |
| a git remote | `git remote -v`, and `git fetch` actually succeeding |

A failed connection is **not** a missing capability. If a `<system-reminder>` says a
server failed to connect, say so to the user — they can fix it — rather than concluding
the integration does not exist.

## Known fallbacks in this repo

| Wanted | First choice | Fallback | If neither |
|---|---|---|---|
| requirement text | the requirements-system MCP | `tests/bdd_tests/metadata/requirements.json` | UNVERIFIED |
| design intent | `knowledge-base` MCP | the design docs under `docs/md/` | UNVERIFIED |
| MISRA wording | `misra` MCP | — | UNVERIFIED; the rulebook is licensed and not in the repo |
| PDF text | `pdftotext` | the HTML sidecar next to each PDF | say the PDF half is unchecked |
| the C++ harness | the local build | a WSL clone that has one | cannot run the suite; say so |
| SonarQube findings | `sonarqube` MCP | — | UNVERIFIED |

The sidecar case is worth spelling out because it cuts both ways: the sidecar holds the
untruncated values the PDF may have clipped, so it is the better source for *what a cell
contains* — and a worse one for *what the reviewer sees*. Which you need depends on the
question.

## Before proposing a new capability

The spec is explicit about not duplicating what exists. In order:

1. an MCP already connected
2. a skill already in `.claude/skills/`
3. a CLI tool already on the path
4. the QA RAG under `rag/`
5. a utility already in the repo (an in-repo utility directory, the BDD test
   harness, the report generator)
6. only then, a new capability

A recommendation that skips this check is usually re-implementing something. The
the empty-cells evidence check check already existed and was scanning zero files; the answer
there was to fix it, not to write a second one.

## Deterministic first

If a check can be done by a script, write the script. LLM reasoning is for interpretation,
not for counting.

Deterministic in this repo: requirement ids present, report sections present, duplicate
ids, broken links, missing files, test execution status, version mismatch, schema shape,
evidence existence, every rule in `rag/check_evidence.py`.

Not deterministic: whether a threshold has a legitimate source, whether an acceptance
criterion is weaker than the test, whether a step's claim is substantiated by prose.
Those route to a specialist — see `references/qa-findings.md`.
