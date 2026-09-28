#!/usr/bin/env python3
"""Replay every defect that reached a human reviewer, and assert a rule catches it.

Each case is a defect QA or the user filed by hand, reduced to the rows that carried it.
A rule is only credited when it fires on the defect AND stays silent on the corrected
form, because a rule that fires on both detects nothing -- it just always complains.

Run: python3 rag/test_known_defects.py    (exit 0 all caught, 1 otherwise)
"""
import importlib.util
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ce", _HERE / "check_evidence.py")
ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ce)
R = ce.Row


def row(sid="S-1", step="1", keyword="Then", description="", assertion="",
        expected="", actual="", result="PASS", owner=None):
    return R(sid=sid, step=step, keyword=keyword, description=description,
             assertion=assertion, expected=expected, actual=actual,
             result=result, owner=owner if owner is not None else step)


# (id, rule, bad rows, good rows, what a human had to file by hand)
CASES = [
    ("D1-count-as-evidence", "P3",
     [row(sid="SCN-86-1", step="2", description="the constants are read",
          assertion="len(ctx.config) > 0", expected="> 0", actual="7")],
     [row(sid="SCN-86-1", step="5", description="the run used these settings: parameter | value",
          assertion="compiled == {name: value}", expected="{'repeat_period': 28}",
          actual="{'repeat_period': 28}")],
     "SCN-86 step 2 still has len(ctx.config) > 0 with Actual 7"),

    ("D2-absolute-path", "P4",
     [row(sid="SCN-85-1", step="1", keyword="Given",
          description="the harness is compiled and available",
          assertion="executable_binary == where",
          expected="/home/dev/project/build/bin/signal_sync_test_binary",
          actual="/home/dev/project/build/bin/signal_sync_test_binary")],
     [row(sid="SCN-85-1", step="1", keyword="Given",
          description="the harness is compiled and available",
          assertion="executable_binary == where",
          expected="build/native/Release/bin/signal_sync_test_binary",
          actual="build/native/Release/bin/signal_sync_test_binary")],
     "repo relative binary path instead of /home/<user>/..."),

    ("D3-uneven-coverage", "P5",
     # The half-applied fix: the table landed on 84 and 91 only.
     [row(sid=s, step="1", keyword="Given",
          description="the run used these parameters: parameter | value delay_samples | 60")
      for s in ("SCN-84-1", "SCN-91-1")]
     + [row(sid=s, step="1", keyword="Given", description="a reference/delayed signal pair")
        for s in ("SCN-85-1", "SCN-86-1", "SCN-87-1", "SCN-89-1", "SCN-90-1")],
     # Corrected: every scenario carries one, wording may differ.
     [row(sid=s, step="1", keyword="Given",
          description="the run used these parameters: parameter | value delay_samples | 60")
      for s in ("SCN-84-1", "SCN-87-1", "SCN-89-1", "SCN-90-1", "SCN-91-1")]
     + [row(sid="SCN-85-1", step="1", keyword="Given",
            description="the sync constants match: parameter | value batch_size | 128"),
        row(sid="SCN-86-1", step="1", keyword="Given",
            description="the run used these settings: parameter | value repeat_period | 28")],
     "parameter table at the top for every test, not only 84 and 91"),

    ("D4-whole-record-in-expected", "P6",
     [row(sid="SCN-87-1", step="6", description="the quality metric is reported",
          assertion='"peak" in final',
          expected="{'batch_idx': 12, 'delay': 60, 'sample_age': 5, 'peak': 1, 'channel_a_validity': 'valid'}",
          actual="'peak'")],
     [row(sid="SCN-87-1", step="6", description="the quality metric is reported",
          assertion='reported == ["peak"]', expected="['peak']", actual="['peak']")],
     '"peak" in final prints the entire batch record and records no value of its own'),
]


def _args(case_rows):
    """Rendered rows for most rules; captured assertions (dicts) for the rules that read those."""
    return ([], case_rows) if case_rows and isinstance(case_rows[0], dict) else (case_rows, [])


def _captured(label=None):
    """One captured assertion of a looped check, as the pytest plugin records it."""
    return {"test": "test_cv", "step_name": "the CV is below the bound", "label": label,
            "assertion": "cv < threshold", "explanation": "4.8e-09 < 1e-05"}


CASES.append(
    ("D5-unlabelled-loop-rows", "R11e",
     [_captured(), _captured()],
     [_captured("sensor 0"), _captured("sensor 1")],
     "two identical rows under one step -- the rows do not identify which iteration each covers"))


def main() -> int:
    failures = []
    for case_id, rule_id, bad, good, filed_by in CASES:
        fn = dict((r[0], r[2]) for r in ce.CHECKS).get(rule_id)
        if fn is None:
            failures.append("%s: rule %s is not registered" % (case_id, rule_id))
            continue
        empty = pathlib.Path(".")
        fires_on_bad = bool(fn(*_args(bad), empty))
        fires_on_good = bool(fn(*_args(good), empty))
        if not fires_on_bad:
            failures.append("%s: %s MISSED the defect a human filed (%s)"
                            % (case_id, rule_id, filed_by))
        elif fires_on_good:
            failures.append("%s: %s also fires on the corrected form, so it detects nothing"
                            % (case_id, rule_id))
        else:
            print("  caught  %-28s %s" % (case_id, rule_id))

    print()
    if failures:
        for f in failures:
            print("  FAIL    %s" % f)
        print("\n%d of %d known defects not detected." % (len(failures), len(CASES)))
        return 1
    print("All %d known defects are detected, and no rule fires on the corrected form."
          % len(CASES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
