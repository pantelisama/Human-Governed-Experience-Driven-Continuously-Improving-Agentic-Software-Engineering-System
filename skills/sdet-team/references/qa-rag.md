# QA RAG

The knowledge engine. Two knowledge files and two executable checkers, all under this
skill — nothing external, no vector store.

| | |
|---|---|
| `references/qa-findings.md` | the fifteen patterns QA has filed, in their words |
| `references/principles.md` | the four properties that generate those patterns |
| `rag/check_evidence.py` | 21 checks over the rendered evidence documents |
| `rag/check_source.py` | 7 checks that need the step definitions and the feature file |
| `rag/README.md` | how to run them, what they cover, measured results |

## Retrieval, in practice

The spec describes a hierarchy — exact lookup, then lexical, then vector, then rerank,
then graph expansion. What this corpus needs is the first two:

```
1. exact     a rule id (R2, B5, A1), a scenario id (SCN-1-1), a file path
2. lexical   a phrase from a finding, an identifier, a step sentence
3. vector    not built — the corpus is three review documents and one test suite
```

Vector retrieval would add infrastructure without adding findings here. If the corpus
outgrows what one file holds, `report_review_rag.txt` has the fuller design; it should
earn the complexity through use.

**Do not retrieve the whole thing.** One rule for one question. `qa-findings.md` is
organised by rule id so a finding can be looked up without reading the file.

## Traceability

The chain the spec asks for, and where each link actually lives in this repo:

```
Finding        the QA review documents under tests/.../<suite>/audit/
   ↓
Requirement    @req-* tags in the .feature; metadata/requirements.json
   ↓
Scenario       the .feature file
   ↓
Assertion      test_signal_sync.py, by step
   ↓
Execution      pytest-assertions.json
   ↓
Report         evidence/<scenario-id>.html and .pdf
   ↓
Evidence       the rendered rows
```

Both directions work. From a finding: which rule, which scenario, which assertion. From a
row in a document: which step claims it, which requirement the scenario carries.

`check_evidence.py --json` emits the row-level half of this, which is what a caller
wanting to walk the chain should read rather than re-parsing the HTML.

## Provenance

Every finding the checkers report names its document, its step and the assertion text. A
finding that cannot say where it came from is not reportable — that is the same rule the
evidence documents are held to.

## What it deliberately does not do

- No requirement or risk-control store: those live in an external
  requirements/risk-management system, reached through its MCP server when one is
  connected. See `capability-discovery.md` for the
  fallback.
- No standard-clause store: the MISRA rulebook is licensed and not in the repo.
- No embeddings, no index to rebuild, no service to run.
