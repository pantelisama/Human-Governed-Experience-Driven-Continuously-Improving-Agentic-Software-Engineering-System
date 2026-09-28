#!/usr/bin/env python3
"""Run QA's evidence-report checks before a merge.

Every finding QA has raised on this project was raised against a generated evidence
document. So are these checks: they read the rendered sidecars and the captured
assertions, not the test source. A pattern can look fixed in the source and still be
present in the record -- the generator manufactures rows the source does not contain,
which is how `grep -c 'bool(' test_*.py` once returned zero while the PDFs still showed
68 of them.

The rule IDs match `../references/qa-findings.md`, which carries the wording QA used and the reasoning
behind each rule. Read that file before dismissing a finding.

Usage:
    python check_evidence.py <reports-dir> [--json]

    <reports-dir> holds evidence/<scenario-id>.html and pytest-assertions.json,
    e.g. artifacts/<project>/docs/reports/bdd/unit_tests

Exit status is 1 when any check fails, so it can gate a merge.
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

# A row is (step, keyword, description, assertion, expected, actual, result).
# `step` is empty on a row the document did not attribute -- a rowspan continuation,
# which a page break can strand. `owner` is the step it belongs to either way, so rules
# that group by step still see it.
Row = collections.namedtuple(
    "Row", "sid step keyword description assertion expected actual result owner")

# Evidence sidecars are named for the scenario they document, one document per
# scenario, and the host project decides that naming. The glob therefore matches
# any sidecar in the evidence directory; narrow it here if a project writes other
# files alongside them. `path.stem` is the scenario id either way.
_EVIDENCE_HTML = "*.html"
_EVIDENCE_PDF = "*.pdf"

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
# The shortest token worth checking for truncation. Below this a value fits any column,
# and searching for it in the PDF text collides with unrelated words.
_MIN_TRUNCATABLE_LEN = 12


def _text(fragment: str) -> str:
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", fragment))).strip()


def _fold(text: str) -> str:
    """Letters only, lowercased, so one identifier reads the same in any convention.

    A step names `packetMismatch`, after the C++ enumerator; the row asserting it
    is `packet_mismatch == []`, in Python's. A reviewer reads those as the same
    word, and a rule that compares them literally reports a finding that is not there.
    """
    return re.sub(r"[^a-z]", "", text.lower())


def read_rows(evidence_dir: pathlib.Path) -> list[Row]:
    """Every assertion row in every evidence sidecar, with its step carried forward.

    The step cells are written on a step's first row only, so a row that leaves them
    blank belongs to the step above it.
    """
    rows: list[Row] = []
    for path in sorted(evidence_dir.glob(_EVIDENCE_HTML)):
        sid = path.stem
        step = keyword = description = ""
        for fragment in _ROW.findall(path.read_text(encoding="utf-8")):
            cells = [_text(c) for c in _CELL.findall(fragment)]
            # Seven cells is a row that carries its own step; four is a rowspan
            # continuation, whose step cells were emitted once on the row above. Both
            # are assertion rows -- dropping the four-cell ones would discard exactly
            # the rows the orphan rule exists to find.
            if len(cells) == 7:
                if cells[3] == "Assertion":
                    continue
                spanned = False
                step = cells[0] or step
                if cells[1]:
                    keyword, description = cells[1], cells[2]
                body = cells[3:]
            elif len(cells) == 4:
                spanned = True
                body = cells
            else:
                continue
            rows.append(Row(sid, "" if spanned else step,
                            "" if spanned else keyword,
                            "" if spanned else description,
                            body[0], body[1], body[2], body[3], step))
    return rows


def read_assertions(reports_dir: pathlib.Path) -> list[dict]:
    path = reports_dir / "pytest-assertions.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


# --- checks -----------------------------------------------------------------
# Each returns a list of finding strings. Empty means the rule holds.

def r2_bool_rows(rows, assertions, evidence_dir):
    """R2 -- bare truthiness rendered as bool(x) == True."""
    return ["%s step %s: %s" % (r.sid, r.step, r.assertion)
            for r in rows if r.assertion.startswith("bool(")]


def r3_name_echoes(rows, assertions, evidence_dir):
    """R3 -- a value compared against itself.

    Flags the two shapes QA named and nothing else:

    - `x == name`, the idiom that satisfied "no bool()" while keeping the defect;
    - an equality whose right side is the left side's own name (`opened == groups`,
      `present == dataset_file`), so the test built both sides from one literal.

    An empty-collection comparison (`wrong == []`, `missing == []`) is what QA asked
    for -- the offending items print when they exist -- and an output compared against
    a specification literal (`validity == "valid"`) has two independent origins. Neither
    is this finding.
    """
    out = []
    sentence = ""
    last_step = None
    for r in rows:
        if r.description:
            sentence = r.description.lower()
        elif (r.sid, r.owner) != last_step:
            sentence = ""
        last_step = (r.sid, r.owner)
        if re.search(r"==\s*name\s*$", r.assertion):
            out.append("%s step %s: %s" % (r.sid, r.step, r.assertion))
            continue
        # An existence check has one source: the artefact is there or it is not. The
        # row can only record what it looked for, so comparing that name against the
        # constant holding it is the honest shape, not an echo. See principles.md,
        # "When two principles pull against each other".
        if re.match(r"^\w*(built|present|resolved|found|available)\w*\s*==\s*_[A-Z]",
                    r.assertion):
            continue
        m = re.match(r"^(\w+)\s*==\s*([\w.\[\]\"']+)$", r.assertion)
        if not m:
            continue
        left, right = m.group(1), m.group(2).strip("\"'")
        # A step parameter is the specification, not something the test built: the
        # scenario states it and pytest-bdd parses it out of the Examples row. Comparing
        # a measured value against one is two independent origins, which is what the rule
        # requires -- so the right-hand name appearing in the step text clears it.
        # `opened == groups` does not: the step never mentions `groups`.
        # A step parameter is the specification, not something the test built: the
        # scenario states it and pytest-bdd substitutes the Examples value into the step
        # text. So the tell is the rendered *value* appearing in the step sentence --
        # "the channels that differ between the runs are none" against `'none'`. That is
        # two independent origins, which is what the rule requires. `opened == groups`
        # does not clear it: the step never mentions what `groups` holds.
        # The words of the value, against the words of the step sentence. A list
        # renders as ['channel_a', 'channel_b'] where the step says "channel_a and channel_b", so comparing
        # the two strings fails; comparing their words does not.
        words = re.findall(r"[a-z]{3,}", (r.expected or "").lower())
        if words and all(w in sentence for w in words):
            continue
        # An empty collection is what a step saying "none" asks for: the row states the
        # absence, so the emptiness is the measurement rather than a missing one.
        if r.expected.strip() in ("[]", "{}", "set()", "()") and "none" in sentence:
            continue
        # `opened == groups`, `present == dataset_file`: the right side names the same
        # thing the left was built from, and nothing numeric was measured.
        if (left != right and r.expected == r.actual
                and not re.search(r"\d", r.expected or "")
                and right.isidentifier()):
            out.append("%s step %s: %s -> %s" % (r.sid, r.step, r.assertion, r.expected))
    return out


def r4_stimulus_in_given(rows, assertions, evidence_dir):
    """R4 -- a Given that runs the stimulus the When claims.

    QA raised this against SCN-3, whose Given read the compiled constants: an exit
    status and an observation count appeared under a precondition before the When
    claimed to run anything. A Given that loads the data it says it provides is that
    step doing its job, so the rule looks for the config read and the sync pass
    rather than for any harness call.
    """
    stimulus = ("config", "pass ", "ctx.config", "sync pass")
    ran = ("exit_status", "returncode", "observations")
    return ["%s step %s (Given): %s -> %s" % (r.sid, r.step, r.assertion, r.expected)
            for r in rows
            if r.keyword == "Given"
            and any(m in r.assertion for m in ran)
            and any(m in (r.expected + r.actual) for m in stimulus)]


def r11_orphan_rows(rows, assertions, evidence_dir):
    """R11 -- a row with no step number, which a page break can strand."""
    return ["%s: %s" % (r.sid, r.assertion) for r in rows if not r.step.strip()]


def r11_truncated(rows, assertions, evidence_dir):
    """R11 -- a value cut off, hiding what the step recorded.

    Two places this happens:

    - the renderer's own cap, which writes an ellipsis into the cell, visible in the
      sidecar;
    - the PDF column being too narrow, which cuts the text at layout time while the
      sidecar still holds the full value. QA's worst instance was the second kind --
      "invalid == expected, both lists elided ... the assertion carrying the whole
      verification" -- so the PDF has to be read to answer this rule at all.

    The PDF half compares the sidecar's values against the PDF's text rather than trying
    to recognise a cut fragment. `pdftotext -layout` interleaves columns, so a fragment
    on one line is not one cell, and three attempts at pattern-matching that output
    produced only false positives. A value the column cut is missing its tail from the
    PDF; a value the column wrapped is present once layout whitespace is collapsed.

    Needs `pdftotext`. Without it the PDF half is reported as unchecked, not passed.
    """
    out = ["%s step %s: %s -> %s" % (r.sid, r.owner, r.assertion, r.expected[-28:])
           for r in rows if "\u2026" in r.expected or "\u2026" in r.actual]

    if shutil.which("pdftotext") is None:
        out.append("pdftotext is not available, so PDF-layout truncation was not "
                   "checked; this rule is unverified, not clean")
        return out

    by_doc: dict[str, list[Row]] = collections.defaultdict(list)
    for r in rows:
        by_doc[r.sid].append(r)

    for pdf in sorted(evidence_dir.glob(_EVIDENCE_PDF)):
        group = by_doc.get(pdf.stem)
        if not group:
            continue
        try:
            text = subprocess.run(["pdftotext", str(pdf), "-"],
                                  capture_output=True, text=True, timeout=60).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            out.append("%s: could not read the PDF (%s); truncation unchecked"
                       % (pdf.stem, exc))
            continue
        for r in group:
            for column, value in (("Expected", r.expected), ("Actual", r.actual)):
                # The atoms of the value: unbroken runs of word characters and dots,
                # which the layout never splits. Searching for the whole rendered string
                # fails when the page interleaves a wrapped cell with its neighbours,
                # even though every character is present.
                atoms = [a for a in re.findall(r"[\w.]+", value)
                         if len(a) >= _MIN_TRUNCATABLE_LEN]
                missing = [a for a in atoms if a not in text]
                if missing:
                    out.append("%s step %s: the %s cell is cut in the rendered PDF: "
                               "%s (missing %s)"
                               % (pdf.stem, r.owner, column, value[:32], missing[0][:24]))
    return sorted(set(out))


def r11_unresolved_placeholder(rows, assertions, evidence_dir):
    """R11 -- a Scenario Outline placeholder that reached the document unsubstituted."""
    out = []
    for r in rows:
        # "total_rise=total_rise": the Examples column name rendered as its own value.
        for m in re.finditer(r"\b(\w+)\s*=\s*\1\b", r.description):
            out.append("%s step %s: placeholder rendered as its own name: %s"
                       % (r.sid, r.owner, m.group(0)))
        # "the \"dataset_file\" dataset": the column name standing in for a value.
        for m in re.finditer(r"the \"?(\w+_file|\w+_value)\"? dataset", r.description):
            out.append("%s step %s: placeholder rendered as a literal: %s"
                       % (r.sid, r.owner, m.group(1)))
    for path in sorted(evidence_dir.glob(_EVIDENCE_HTML)):
        if re.search(r"&lt;\w+&gt;", path.read_text(encoding="utf-8")):
            out.append("%s: an unsubstituted <placeholder> is in the document"
                       % path.stem)
    return sorted(set(out))


def r11_implementation_leak(rows, assertions, evidence_dir):
    """R11 -- helper calls and conditionals printed in the Assertion column."""
    marks = ("_keyed(", " if label", "== ok", "!= none", "lambda ")
    return ["%s step %s: %s" % (r.sid, r.step, r.assertion)
            for r in rows if any(m in r.assertion for m in marks)]


def r11_duplicate_rows(rows, assertions, evidence_dir):
    """R11 -- two identical rows under one step of one run.

    A Scenario Outline renders one table per Examples row, and those tables are meant to
    look alike -- they are the same scenario at different values. The captured
    assertions carry the run in `test`, so duplicates are counted per run there rather
    than across the rendered documents.
    """
    if not assertions:
        return []
    seen = collections.Counter(
        (a.get("test", ""), a.get("step_name") or "", a.get("label") or "",
         a.get("assertion", ""), a.get("explanation", ""))
        for a in assertions)
    return ["%s / %s: %s (x%d)" % (k[0][:40], (k[1] or "?")[:28], k[3][:48], n)
            for k, n in seen.items() if n > 1]


def r12_document_identity(rows, assertions, evidence_dir):
    """R12 -- the header must name the protocol and the source that produced it."""
    required = ("Test Protocol ID", "Test Source Commit", "Test Source Branch",
                "Approval Date")
    out = []
    for path in sorted(evidence_dir.glob(_EVIDENCE_HTML)):
        body = path.read_text(encoding="utf-8")
        missing = [f for f in required if f not in body]
        if missing:
            out.append("%s: header omits %s" % (path.stem, ", ".join(missing)))
    return out


def r5_claim_without_assertion(rows, assertions, evidence_dir):
    """R5 -- a step whose claim names something no assertion under it mentions.

    A step may name a quantity and then assert over a variable derived from it --
    SCN-3 step 4 claims "successive sample_age of 0" and asserts over `gaps`, which is
    computed from the sample_age-0 batch indices. So a name bound on the left of an
    earlier assertion in the same step counts as naming what it was derived from;
    otherwise the rule fires on correctly-written evidence, and a standing false
    positive is how a real one gets waved through.
    """
    # Noun in the step text -> a term that must appear in one of its assertion rows.
    claims = {
        "fault state": ("fault", "injected", "invalid", "flag"),
        "failedpacketmatching": ("validity", "unexpected", "packetmatching"),
        "nan or inf": ("finite", "offender", "nan", "inf"),
        "quality metric": ("peak",),
        "sample_age": ("sample_age", "ages", "registration", "gap"),
        "lag of": ("lag",),
    }
    by_step: dict[tuple, list[Row]] = collections.defaultdict(list)
    descriptions: dict[tuple, str] = {}
    for r in rows:
        key = (r.sid, r.owner)
        by_step[key].append(r)
        if r.description:
            descriptions[key] = r.description
    out = []
    for key, group in by_step.items():
        sid, step = key
        desc = descriptions.get(key, "")
        blob = _fold(" ".join("%s %s %s" % (r.assertion, r.expected, r.actual)
                              for r in group))
        # Names the step binds on the left of an assertion: asserting over one of these
        # is asserting over whatever it was derived from.
        bound = {m.group(1).lower()
                 for r in group
                 for m in [re.match(r"^(\w+)\s*(?:==|!=|>=|<=|>|<)", r.assertion)]
                 if m}
        for claim, needles in claims.items():
            if claim not in desc.lower():
                continue
            if any(_fold(n) in blob for n in needles):
                continue
            if any(_fold(n) in _fold(b) for b in bound for n in needles):
                continue
            out.append("%s step %s claims %r; no assertion mentions %s"
                       % (sid, step, desc[:52], "/".join(needles)))
    return out


def r1_expected_from_actual(rows, assertions, evidence_dir):
    """R1 -- Expected rendered from the measured side, so the columns cannot disagree.

    QA named the visible symptom: "rows asserting two values are different printing the
    same number in both columns and passing". That is unambiguous -- a passing `!=`
    whose two columns match can only mean Expected was filled in from Actual.

    A passing equality showing the same value on both sides is not this finding; that is
    what an equality does. And a FAILED row whose columns agree is the same defect seen
    from the other side.
    """
    out = []
    for r in rows:
        if not r.expected or r.expected != r.actual:
            continue
        passing = r.result.upper().startswith("PASS")
        differs = "!=" in r.assertion or "is not" in r.assertion
        if passing and differs:
            out.append("%s step %s: asserts a difference, both columns read %s, and "
                       "passes: %s" % (r.sid, r.owner, r.expected[:30], r.assertion[:44]))
        elif r.result.upper().startswith("FAIL"):
            out.append("%s step %s: FAILED row shows the same value in both columns: %s"
                       % (r.sid, r.owner, r.assertion))
    return out


def e2_dash_on_a_passing_step(rows, assertions, evidence_dir):
    """E2 -- a placeholder dash on a step that reports PASS.

    The dash is legitimate where the step never ran (BLOCKED, SKIPPED). On a PASS it
    says the step verified nothing and was recorded as verified anyway.
    """
    dashes = {"-", "\u2013", "\u2014"}
    return ["%s step %s: %r with result %s" % (r.sid, r.owner, r.assertion, r.result)
            for r in rows
            if r.assertion.strip() in dashes
            and r.result.strip().upper().startswith("PASS")]


def e4_data_table_not_rendered(rows, assertions, evidence_dir):
    """E4 -- a step promising a Gherkin data table that is not in the document.

    A trailing colon is the data-table marker. QA called the missing table "the worst
    defect in the set": SCN-2's five constants collapsed into two booleans because the
    table they were compared against never appeared.

    The renderer writes table rows into the step-description cell, so a step whose text
    ends in ":" must have something after the colon somewhere in its group.
    """
    by_step: dict[tuple, list[Row]] = collections.defaultdict(list)
    for r in rows:
        by_step[(r.sid, r.owner)].append(r)
    out = []
    for (sid, step), group in by_step.items():
        desc = next((r.description for r in group if r.description), "")
        if not desc.rstrip().endswith(":"):
            continue
        # The table is rendered inside the description cell, after the colon.
        if any(len(r.description.rstrip()) > len(desc.rstrip()) or "|" in r.description
               for r in group):
            continue
        out.append("%s step %s: %r promises a data table; none is rendered"
                   % (sid, step, desc[:52]))
    return out


def e7_operator_instead_of_value(rows, assertions, evidence_dir):
    """E7 -- an Expected cell naming a type or a bare operator, not a value.

    "in collection", "in dict", "is not None": a reviewer has nothing to compare the
    Actual cell against. The fix QA asked for was to render the collection itself.
    """
    typenames = ("collection", "dict", "list", "set", "tuple", "object", "str", "int")
    out = []
    for r in rows:
        e = r.expected.strip()
        if not e:
            continue
        # "in collection" / "not in dict": an operator followed only by a type name.
        m = re.match(r"^(in|not in|is|is not)\s+(\w+)$", e)
        if m and m.group(2).lower() in typenames:
            out.append("%s step %s: Expected is a type, not a value: %r (%s)"
                       % (r.sid, r.owner, e, r.assertion[:36]))
    return out


def b1_step_reports_pass_with_no_assertion(rows, assertions, evidence_dir):
    """B1 -- a step that reports PASS while asserting nothing.

    Distinct from E2: E2 is a dash in the Assertion cell, this is a step whose group
    holds no assertion row at all.
    """
    by_step: dict[tuple, list[Row]] = collections.defaultdict(list)
    for r in rows:
        by_step[(r.sid, r.owner)].append(r)
    out = []
    for (sid, step), group in by_step.items():
        if any(r.assertion.strip() and r.assertion.strip() not in {"-", "\u2013", "\u2014"}
               for r in group):
            continue
        if any(r.result.strip().upper().startswith("PASS") for r in group):
            desc = next((r.description for r in group if r.description), "")
            out.append("%s step %s (%s) reports PASS and asserts nothing"
                       % (sid, step, desc[:44]))
    return out


def p2_actual_carries_no_value(rows, assertions, evidence_dir):
    """P2 -- the row does not record what the software produced.

    The generalised form of the bool() finding: whatever the assertion text looks like,
    an Actual cell holding `True`, `False` or a bare type name tells a reviewer nothing.
    QA filed this against `H5DataSource` appearing where a path belonged, and against
    every `Expected True / Actual True` row.
    """
    empty_values = {"true", "false", "none", "null"}
    out = []
    for r in rows:
        a = r.actual.strip()
        if not a:
            continue
        if a.lower() in empty_values:
            out.append("%s step %s: Actual is %r, so the row records no value: %s"
                       % (r.sid, r.owner, a, r.assertion[:40]))
        # A bare CamelCase identifier is a type name, not a value.
        elif re.fullmatch(r"[A-Z][A-Za-z0-9]{3,}", a):
            out.append("%s step %s: Actual is a type name, not a value: %r (%s)"
                       % (r.sid, r.owner, a, r.assertion[:36]))
    return out


def b5_claim_not_evidenced(rows, assertions, evidence_dir):
    """B5 -- something the step description commits to that no row under it records.

    The auditor on SCN-1 step 1: the step reads "a reference/delayed signal pair with
    an injected delay of 60 samples, fed as 13 batches of 128 samples", the row reads
    `(60, 128)`, and the question is "how do you prove 13 batches were fed?". The batch
    count was parsed out of the sentence, stored on the context and never compared.

    R5 does not catch it -- that rule asks whether a step has *an* assertion, and this
    step has two. B5 asks whether every commitment in the sentence has one.

    Three kinds of commitment are decidable from the cells:

    - a **quantity** the step names (60, 13, 128, 0.9);
    - an **identifier** it names (`sample_age`, `packetMismatch`, `total_rise`),
      which is a field or symbol the software produces;
    - a **quoted literal** it names ("clean_signal.h5").

    Prose claims ("ingestion succeeds", "both runs report the same delay") are not
    decidable here. They are P3 in principles.md and belong to the lead, not a regex.
    """
    by_step: dict[tuple, list[Row]] = collections.defaultdict(list)
    descriptions: dict[tuple, str] = {}
    for r in rows:
        key = (r.sid, r.owner)
        by_step[key].append(r)
        if r.description:
            descriptions[key] = r.description

    out = []
    for key, group in by_step.items():
        sid, step = key
        desc = descriptions.get(key, "")
        if not desc:
            continue
        evidenced = " ".join("%s %s %s" % (r.assertion, r.expected, r.actual)
                             for r in group)

        claims: list[tuple[str, str]] = []
        # Quantities. 0 and 1 are too common to carry a commitment; a number inside an
        # identifier or a version is not one either.
        for m in re.finditer(r"(?<![\w.-])(\d+(?:\.\d+)?)(?![\w.-])", desc):
            if m.group(1) not in ("0", "1"):
                claims.append(("quantity", m.group(1)))
        # Identifiers: snake_case or camelCase, which name a field the software emits.
        for m in re.finditer(r"\b([a-z]+_[a-z_0-9]+|[a-z]+[A-Z][A-Za-z]+)\b", desc):
            claims.append(("identifier", m.group(1)))
        # Quoted literals.
        for m in re.finditer(r"[\"\u201c\u2018\']([\w./-]+)[\"\u201d\u2019\']", desc):
            claims.append(("literal", m.group(1)))

        # Folded: a step naming "channel B" is answered by `channel_b_min`, and one naming
        # "packetMismatch" by `packet_mismatch`.
        evidenced_lower = evidenced.lower()
        evidenced_folded = _fold(evidenced)
        # An identifier may reach the record through a value derived from it in an
        # earlier step -- SCN-3 claims sample_age and asserts over `gaps`, computed
        # from the sample_age-0 registrations. The derivation is not in this step's
        # rows, so the whole document is the context for identifiers.
        document = " ".join("%s %s %s" % (r.assertion, r.expected, r.actual)
                            for r in rows if r.sid == sid).lower()
        # An existence check names the artefact it looked for; a second name in the
        # same row would be one the test supplied, which R3 rejects. The message
        # carries it instead. See principles.md.
        existence_check = any(
            re.match(r"^\w*(built|present|resolved|found|available)\w*\s*==", r.assertion)
            for r in group)
        for kind, token in dict.fromkeys(claims):
            needle = token.lower()
            if existence_check and kind == "identifier":
                continue
            if re.search(r"(?<![\w.])%s(?![\w.])" % re.escape(needle), evidenced_lower):
                continue
            if kind == "identifier":
                # `sample_age` answered by `sample_age_at_registration`, or by a row
                # elsewhere in the document that names it, in either convention.
                if needle in evidenced_lower or needle in document:
                    continue
                if _fold(token) in evidenced_folded or _fold(token) in _fold(document):
                    continue
                stem = needle.split("_")[0]
                if len(stem) >= 4 and stem in evidenced_lower:
                    continue
            out.append("%s step %s commits to %s %r; no row records it (%r)"
                       % (sid, step, kind, token, desc[:40]))
    return out



def p3_count_as_evidence(rows, assertions, evidence_dir):
    """P3 -- the row records how many, where the reviewer needed which.

    QA on SCN-86: "len(ctx.config) > 0 with Actual 7". The guard passed, the run was
    green, and the row proved only that the binary emitted *seven of something*. Which
    seven, and whether the constants the scenario depends on were among them, the record
    never said. P2's sibling: P2 catches True/False, this catches a bare cardinality.

    A count is legitimate when the step itself names the number ("13 batches"); it is
    evidence of nothing when the assertion is a non-emptiness guard.
    """
    guard = re.compile(r"^\s*len\s*\(.*\)\s*(>=?\s*1|>\s*0)\s*$")
    out = []
    for r in rows:
        if not guard.match(r.assertion):
            continue
        # The step naming the same number is stating a fact, not guarding emptiness.
        if r.actual.strip() and r.actual.strip() in r.description:
            continue
        out.append("%s step %s: %s records a count (%s), not which values arrived"
                   % (r.sid, r.owner, r.assertion[:44], r.actual.strip()[:12]))
    return sorted(set(out))


def P4_absolute_path(rows, assertions, evidence_dir):
    """P4 -- an absolute filesystem path in the record.

    A path under a developer's home directory evidences the machine that ran the suite,
    not the build it ran against. Two runs of the same commit on two machines produce
    different records, and a reader cannot tell whether the artefact under test was the
    right one. Record the path relative to the repository instead.
    """
    abs_path = re.compile(r"(?:/home/|/Users/|[A-Za-z]:\\\\)[\w./\\-]{8,}")
    out = []
    for r in rows:
        for column, value in (("Expected", r.expected), ("Actual", r.actual)):
            m = abs_path.search(value)
            if m:
                out.append("%s step %s: the %s cell carries an absolute path (%s)"
                           % (r.sid, r.owner, column, m.group(0)[:46]))
    return sorted(set(out))


def P5_uneven_coverage(rows, assertions, evidence_dir):
    """P5 -- an evidence element present in some scenarios and missing from others.

    The "every test, not only 84 and 91" finding. A reviewer asks for a parameter table
    on every scenario; it lands on the two that already had one plus the two being
    edited, and nobody enumerates the rest. Verifying the items already known to pass is
    not a sample.

    Decidable without knowing which elements a project requires: an element carried by
    most documents and absent from a few is a coverage hole, while one carried by a
    couple is simply scenario-specific. The rule reports only the lopsided case.
    """
    # Match on the step's shape, not its wording: two scenarios can carry the same kind
    # of evidence under different sentences ("these parameters" / "these settings"), and
    # flagging that as a hole trains the reader to ignore the rule.
    def shape(text: str) -> str:
        t = text.strip().lower()
        # A rendered data-table step inlines its rows as "... : parameter | value ...".
        # Every such step is the same kind of evidence whatever sentence introduces it.
        if "|" in t and re.search(r":\s*\w+\s*\|", t):
            return "<data table step>"
        return re.sub(r"[-+]?\d*\.?\d+", "#", t)[:40]

    by_doc: dict[str, set] = collections.defaultdict(set)
    for r in rows:
        head = shape(r.description)
        if head:
            by_doc[r.sid].add(head)
    docs = sorted(by_doc)
    if len(docs) < 4:
        return []
    counts: dict[str, int] = collections.Counter()
    for sid in docs:
        for head in by_doc[sid]:
            counts[head] += 1
    out = []
    for head, n in counts.items():
        # Carried by most, missing from a handful: the shape of a half-applied fix.
        if n >= len(docs) - 2 and n < len(docs):
            missing = [d for d in docs if head not in by_doc[d]]
            out.append("step %r is in %d of %d documents; missing from %s"
                       % (head[:38], n, len(docs), ", ".join(missing)))
    return sorted(set(out))



def P6_record_dumped_as_value(rows, assertions, evidence_dir):
    """P6 -- a whole record dumped where one value belonged.

    QA on SCN-87: `"peak" in final` put the entire batch dict in the Expected column and
    recorded no value of its own. The reviewer needs the metric; the cell gives them the
    batch. R11b only sees this when the PDF happens to cut it, so a dump that fits the
    column passes every other rule.

    A membership test is the usual source: the container renders as Expected and the key
    as Actual, which inverts what the columns mean.
    """
    out = []
    for r in rows:
        for column, value in (("Expected", r.expected), ("Actual", r.actual)):
            v = value.strip()
            # A mapping literal carrying several keys is a record, not a value.
            if not (v.startswith("{") and v.endswith("}")):
                continue
            if v.count(":") < 3:
                continue
            out.append("%s step %s: the %s cell dumps a whole record (%d fields): %s"
                       % (r.sid, r.owner, column, v.count(":"), r.assertion[:38]))
    return sorted(set(out))


CHECKS = [
    ("R2", "bare truthiness rendered as bool(x) == True", r2_bool_rows),
    ("R3", "a value compared against itself", r3_name_echoes),
    ("R4", "the stimulus sits in a Given", r4_stimulus_in_given),
    ("R5", "a step claim with no assertion behind it", r5_claim_without_assertion),
    ("R11a", "a row with no step number", r11_orphan_rows),
    ("R11b", "a value truncated with an ellipsis", r11_truncated),
    ("R11c", "an unsubstituted placeholder", r11_unresolved_placeholder),
    ("R11d", "implementation leaking into the Assertion column", r11_implementation_leak),
    ("R11e", "identical rows under one step", r11_duplicate_rows),
    ("R12", "the header does not identify the document", r12_document_identity),
    ("R1", "Expected rendered from the measured side", r1_expected_from_actual),
    ("B1", "a step reports PASS and asserts nothing", b1_step_reports_pass_with_no_assertion),
    ("E2", "a dash on a step that reports PASS", e2_dash_on_a_passing_step),
    ("E4", "a promised data table is not rendered", e4_data_table_not_rendered),
    ("E7", "Expected names a type, not a value", e7_operator_instead_of_value),
    ("P2", "the row records no value", p2_actual_carries_no_value),
    ("B5", "a claim in the step description is not evidenced",
     b5_claim_not_evidenced),
    ("P3", "the row records a count, not which values", p3_count_as_evidence),
    ("P4", "an absolute filesystem path in the record", P4_absolute_path),
    ("P5", "an element present in some scenarios, missing from others", P5_uneven_coverage),
    ("P6", "a whole record dumped where one value belonged", P6_record_dumped_as_value),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reports_dir", type=pathlib.Path)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    evidence_dir = args.reports_dir / "evidence"
    if not evidence_dir.is_dir():
        print("No evidence directory under %s -- nothing to check. Generate the "
              "reports first." % args.reports_dir, file=sys.stderr)
        return 2

    rows = read_rows(evidence_dir)
    if not rows:
        print("No assertion rows parsed from %s. Either the documents are empty or the "
              "trace-table markup changed; this check cannot report a clean result it "
              "did not verify." % evidence_dir, file=sys.stderr)
        return 2
    assertions = read_assertions(args.reports_dir)

    results = []
    for rule, title, check in CHECKS:
        findings = check(rows, assertions, evidence_dir)
        results.append({"rule": rule, "title": title, "findings": findings})

    if args.json:
        print(json.dumps({
            "documents": len({r.sid for r in rows}),
            "rows": len(rows),
            "results": results,
        }, indent=2))
    else:
        docs = sorted({r.sid for r in rows})
        print("Evidence checked: %d documents, %d assertion rows"
              % (len(docs), len(rows)))
        print("  %s" % ", ".join(docs))
        print()
        for res in results:
            findings = res["findings"]
            mark = "FAIL" if findings else "ok  "
            print("%s %-5s %s%s" % (mark, res["rule"], res["title"],
                                    "" if not findings else
                                    " (%d)" % len(findings)))
            for f in findings[:8]:
                print("        %s" % f)
            if len(findings) > 8:
                print("        ... and %d more" % (len(findings) - 8))
        print()
        failed = [r["rule"] for r in results if r["findings"]]
        if failed:
            print("Not merge-ready: %s. See references/qa-findings.md for what QA wrote and "
                  "why." % ", ".join(failed))
        else:
            print("No QA-pattern findings in the generated evidence.")

    return 1 if any(r["findings"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
