#!/usr/bin/env python3
"""The checks that need the test source and the feature file, not the report.

`check_evidence.py` reads the rendered documents, because that is what the reviewer
reads. Four defect classes in `audit/bdd_evidence_review_checklist.md` cannot be seen
there at all -- the row looks identical whether or not the assertion could ever fail:

    A1  a collection selected by the property that is then asserted of it
    A4  a parameterised row whose two runs receive the same arguments
    A5  an assertion over a collection that may be empty, with no guard
    B4  step text in the document that no longer matches the .feature

Run both. A suite passing one and failing the other is still not merge-ready.

Usage:
    python check_source.py <suite-dir> [--json]

    <suite-dir> holds the .feature file and its test_*.py, e.g.
    <repo>/tests/bdd_tests/unit_tests/test_suites/<suite>

Exit status: 0 clean, 1 findings, 2 could not check.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

# Collection-building calls whose result an emptiness guard must precede.
_AGGREGATES = {"all", "any", "sum", "max", "min"}


def _src(node: ast.AST, source: str) -> str:
    return ast.get_source_segment(source, node) or ""


def _step_functions(tree: ast.AST, source: str):
    """(decorator_text, function_node) for every pytest-bdd step in the module."""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            call = dec if isinstance(dec, ast.Call) else None
            name = getattr(getattr(call, "func", dec), "id", None) or \
                getattr(getattr(call, "func", dec), "attr", None)
            if name in ("given", "when", "then"):
                text = ""
                if call and call.args:
                    arg = call.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        text = arg.value
                    elif isinstance(arg, ast.Call) and arg.args:
                        inner = arg.args[0]
                        if isinstance(inner, ast.Constant):
                            text = str(inner.value)
                yield text, node


def a1_filter_then_assert(tree, source, feature):
    """A1 -- the step's claim is the equality that selected the rows.

    QA on SCN-3 step 3, whose step read "sample_age is 0 on the batch where each
    sync registers":

        registrations = [b["batch_idx"] for b in ctx.batches if b["sample_age"] == 0]
        assert len(registrations) >= 2

    "sample_age == 0 is used as a filter, not asserted. The step defines a registration
    as sample_age being 0, then counts them. It never verifies the property the step
    states."

    The rule is narrow on purpose. Only an **equality** in the filter predetermines an
    assertion about that value; a relative test selects on a different property than the
    one asserted. The same suite, corrected, filters on whether sample_age stopped ageing
    monotonically and then asserts the value is 0 -- two properties of one field, and a
    legitimate check. Matching on the field name alone flags that too.
    """
    out = []
    for text, fn in _step_functions(tree, source):
        if not text:
            continue
        claim = text.lower()
        asserted = " ".join(_src(a.test, source)
                            for a in ast.walk(fn) if isinstance(a, ast.Assert))
        for node in ast.walk(fn):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target, comp = node.targets[0], node.value
            if not isinstance(target, ast.Name):
                continue
            if not isinstance(comp, (ast.ListComp, ast.SetComp, ast.DictComp,
                                     ast.GeneratorExp)):
                continue
            for gen in comp.generators:
                for cond in gen.ifs:
                    # Only a direct equality fixes the value the step claims.
                    if not isinstance(cond, ast.Compare) or len(cond.ops) != 1:
                        continue
                    if not isinstance(cond.ops[0], ast.Eq):
                        continue
                    cond_src = _src(cond, source)
                    field = re.search(r'\[[\'"](\w+)[\'"]\]|\.(\w{4,})\b', cond_src)
                    value = _src(cond.comparators[0], source).strip()
                    if not field or not value:
                        continue
                    name = field.group(1) or field.group(2)
                    # The step has to name both the field and the value it is fixed at.
                    if name.lower() not in claim:
                        continue
                    if value.strip("\"'").lower() not in claim:
                        continue
                    # If the assertion compares that field against something else, the
                    # step does verify a property the filter did not guarantee.
                    if re.search(r"%s[\"\']?\]?\s*(?:!=|[<>])" % re.escape(name), asserted):
                        continue
                    out.append(
                        "%s: the step claims %r is %s, and that is the condition that "
                        "selected %r -- the assertion cannot fail"
                        % (fn.name, name, value, target.id))
    return out


def a4_identical_runs(tree, source, feature):
    """A4 -- an Examples row whose neutral value makes two runs identical.

    QA filed this against `total_rise = 0.0`: the drifted and undrifted runs are the
    same command, so the comparison only fails on non-determinism. Legitimate as a
    named control case; a finding when nothing says so.
    """
    if not feature:
        return []
    out = []
    neutral = {"0", "0.0", "", "none", "null", "[]", "{}"}
    for block in re.split(r"\n\s*(?=Scenario)", feature):
        header = block.strip().splitlines()[0] if block.strip() else ""
        if "Examples" not in block:
            continue
        is_control = "control" in block.lower()
        for line in block.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")] \
                if line.strip().startswith("|") else []
            if len(cells) == 1 and cells[0].lower() in neutral and not is_control:
                out.append("%s: Examples row %r makes the two runs identical; name it "
                           "a control case or drop it" % (header[:48], cells[0]))
    return out


def a5_vacuous_pass(tree, source, feature):
    """A5 -- an aggregate over a collection with no non-emptiness guard.

    `assert all(...)` and `assert x == []` both pass over an empty collection, so a run
    where nothing was produced is recorded as verified. The suite's own `_valid_batches`
    carries the guard QA approved of; the rule looks for the ones that do not.
    """
    out = []
    for text, fn in _step_functions(tree, source):
        # Names a len()/emptiness check has already vouched for in this function.
        guarded: set[str] = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Assert):
                t = _src(node.test, source)
                for m in re.finditer(r"len\((\w+)\)\s*[=!<>]", t):
                    guarded.add(m.group(1))
                for m in re.finditer(r"(\w+)\s*!=\s*(?:\[\]|\{\}|0)", t):
                    guarded.add(m.group(1))
        for node in ast.walk(fn):
            if not isinstance(node, ast.Assert):
                continue
            t = _src(node.test, source)
            for m in re.finditer(r"\b(%s)\(" % "|".join(_AGGREGATES), t):
                over = re.search(r"for\s+\w+\s+in\s+(\w+)", t)
                name = over.group(1) if over else None
                if name and name not in guarded:
                    out.append("%s: %s() over %r with no emptiness guard -- an empty "
                               "collection passes" % (fn.name, m.group(1), name))
    return out


def b4_step_text_drift(tree, source, feature):
    """B4 -- a step decorator whose text is not in the feature file.

    A decorator the feature no longer matches means either a dead step definition or a
    scenario running a step nobody wrote. Parameterised decorators are skipped: their
    placeholders never match literally.
    """
    if not feature:
        return []
    feature_text = " ".join(feature.split())
    out = []
    for text, fn in _step_functions(tree, source):
        if not text or "{" in text or "<" in text:
            continue
        if " ".join(text.split()) not in feature_text:
            out.append("%s: the step text %r appears in no scenario" % (fn.name, text[:56]))
    return out


def _assert_nodes(tree):
    """Every assert in the file, with the function that holds it."""
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                if isinstance(node, ast.Assert):
                    yield fn, node


_MEASURING_BUILTINS = frozenset({"len", "sorted", "set", "list", "tuple", "abs", "sum"})


def a6_both_sides_one_origin(tree, source, feature):
    """A6 -- an equality whose two sides are slices of one local expression.

    Shipped twice in one session, each written to close a finding:

        reference = ctx.reference[start:]
        expected_frames = len(ctx.reference) - start
        assert len(reference) == expected_frames

    Both sides are `ctx.reference` measured two ways, so the assertion holds by
    construction and the document records a PASS for a check that cannot fail.

    Deliberately narrow. Comparing a measurement against a reference legitimately
    mentions the same object -- `assert produced == len(ctx.reference)` is real. The
    rule fires only when both sides are *locally assigned* names whose values were
    built from an identical set of roots, which is the shape a restatement takes.
    """
    out = []
    for fn, node in _assert_nodes(tree):
        test = node.test
        if not (isinstance(test, ast.Compare) and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)):
            continue
        # Builtins are how a value is measured, not where it came from.
        plain = lambda node: frozenset(
            n.id for n in ast.walk(node)
            if isinstance(n, ast.Name) and n.id not in _MEASURING_BUILTINS)
        built_from = {}
        for stmt in ast.walk(fn):
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                    and isinstance(stmt.targets[0], ast.Name):
                built_from[stmt.targets[0].id] = plain(stmt.value)
        ln, rn = plain(test.left), plain(test.comparators[0])
        # Both sides must be locals assigned in this function, and not the same name.
        if not (ln and rn and ln != rn):
            continue
        if not (ln <= set(built_from) and rn <= set(built_from)):
            continue
        lroots = frozenset().union(*(built_from[n] for n in ln))
        rroots = frozenset().union(*(built_from[n] for n in rn))
        if lroots and lroots == rroots:
            out.append("%s: %s -- both sides are %s measured twice" % (
                fn.name, _src(node, source)[:60], sorted(lroots)))
    return out


def a7_guard_after_raising_call(tree, source, feature):
    """A7 -- a guard for a condition the call it guards has already excluded.

    Shipped as:

        assert find_binary(BINARY).is_file()

    `find_binary` raises when the path does not exist, so `.is_file()` can only be
    False for a directory -- impossible for a build artefact. The row records no
    value and the check cannot fire. Flags an assert whose subject is a call the
    file elsewhere relies on to raise.
    """
    raising = {"find_binary", "run_binary", "LoadManifest"}
    out = []
    for fn, node in _assert_nodes(tree):
        for call in ast.walk(node.test):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) \
                    and call.func.id in raising:
                out.append("%s: %s -- %s already raises when absent" % (
                    fn.name, _src(node, source)[:60], call.func.id))
    return out


def a8_bare_truthiness(tree, source, feature):
    """A8 -- a bare truthy assert, which the evidence renders as bool(x) == True.

    Thirty such rows reached one set of documents from two lines of source. The
    collector stores the assert's source text, so `assert lines` reaches QA with no
    operand in it. `len(lines) > 0` states the same thing and records the count.
    """
    out = []
    for fn, node in _assert_nodes(tree):
        if isinstance(node.test, ast.Name) or (
                isinstance(node.test, ast.Attribute)
                and isinstance(node.test.value, ast.Name)):
            out.append("%s: %s -- renders as bool(...) == True" % (
                fn.name, _src(node, source)[:60]))
    return out


CHECKS = [
    ("A1", "a collection filtered on the property it then asserts", a1_filter_then_assert),
    ("A4", "an Examples row that makes two runs identical", a4_identical_runs),
    ("A5", "an aggregate that passes over an empty collection", a5_vacuous_pass),
    ("A6", "an equality whose two sides share one origin", a6_both_sides_one_origin),
    ("A7", "a guard for a condition the guarded call excludes", a7_guard_after_raising_call),
    ("A8", "a bare truthy assert, rendered as bool(x) == True", a8_bare_truthiness),
    ("B4", "step text that matches no scenario", b4_step_text_drift),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("suite_dir", type=pathlib.Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tests = sorted(args.suite_dir.glob("test_*.py"))
    if not tests:
        print("No test_*.py under %s -- nothing to check." % args.suite_dir,
              file=sys.stderr)
        return 2

    features = sorted(args.suite_dir.glob("*.feature"))
    feature = features[0].read_text(encoding="utf-8") if features else ""
    if not feature:
        print("No .feature file under %s; A4 and B4 cannot be evaluated and are "
              "reported as unchecked, not clean." % args.suite_dir, file=sys.stderr)

    results = []
    for path in tests:
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            print("Could not parse %s: %s" % (path, exc), file=sys.stderr)
            return 2
        for rule, title, check in CHECKS:
            findings = ["%s: %s" % (path.name, f) for f in check(tree, source, feature)]
            results.append({"rule": rule, "title": title, "findings": findings})

    merged: dict[str, dict] = {}
    for res in results:
        m = merged.setdefault(res["rule"], {"rule": res["rule"], "title": res["title"],
                                            "findings": []})
        m["findings"].extend(res["findings"])
    ordered = [merged[r] for r, _, _ in CHECKS]

    if args.json:
        print(json.dumps({"suite": str(args.suite_dir), "results": ordered}, indent=2))
    else:
        print("Source checked: %s" % ", ".join(p.name for p in tests))
        print()
        for res in ordered:
            findings = res["findings"]
            unchecked = not feature and res["rule"] in ("A4", "B4")
            mark = "??  " if unchecked else ("FAIL" if findings else "ok  ")
            print("%s %-4s %s%s" % (mark, res["rule"], res["title"],
                                    "" if not findings else " (%d)" % len(findings)))
            for f in findings[:8]:
                print("        %s" % f)
            if len(findings) > 8:
                print("        ... and %d more" % (len(findings) - 8))
        print()
        failed = [r["rule"] for r in ordered if r["findings"]]
        print("Not merge-ready: %s." % ", ".join(failed) if failed
              else "No source-level findings.")

    return 1 if any(r["findings"] for r in ordered) else 0


if __name__ == "__main__":
    sys.exit(main())
