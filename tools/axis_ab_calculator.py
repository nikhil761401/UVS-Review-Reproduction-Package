#!/usr/bin/env python3
"""
Axis A / Axis B calculator used throughout the Stage 1B-1F reproducibility audit.

This is a standalone re-implementation of the same logic as v05_classify_ORIGINAL_VERIFIED.py
(classify_v05()), built directly from the frozen codebook rules R06-R09 in
CODEBOOK_RULE_SPECIFICATION.csv. It was used to independently verify v0.5, v0.6-prospective,
and PHASE6_2_pairs.json, and reproduced each file's own stored axis_a/axis_b values with
ZERO mismatches in every case checked.

Usage:
    python3 axis_ab_calculator.py <pairs.json>

Expects a JSON list of pair records, each with a "field_verdicts" dict keyed by field code
(F01, F02, F03, F06, F07, F08, F09, F11, F12, F13, F04, F16), holding one of the 8 raw verdict
strings: WORDING-ONLY, GENUINE, NR-GENUINE, UNA-GENUINE, NA-GENUINE, AMBIGUOUS,
MISSING-BY-CONSTRUCTION, INHERITANCE-BLOCKED.
"""
import json
import sys
from collections import Counter

# Codebook R06: the 10 core comparability dimensions (F04/F16 are strict fields, excluded here)
CORE_FIELDS = ['F01', 'F02', 'F03', 'F06', 'F07', 'F08', 'F09', 'F11', 'F12', 'F13']
STRICT_FIELDS = ['F04', 'F16']

# Codebook R07: verdict -> bucket mapping (frozen, owner-ruled since v0.4)
VERDICT_TO_BUCKET = {
    'WORDING-ONLY': 'SAME',
    'GENUINE': 'DIFFERENT',
    'NR-GENUINE': 'UNASSESSABLE',
    'UNA-GENUINE': 'UNASSESSABLE',
    'NA-GENUINE': 'SAME',              # reported separately as structural-NA
    'AMBIGUOUS': 'UNASSESSABLE',
    'MISSING-BY-CONSTRUCTION': 'UNASSESSABLE',
    'INHERITANCE-BLOCKED': 'UNASSESSABLE',
}


def classify_pair(field_verdicts):
    """Returns (axis_a, axis_b, core_same, core_diff, core_unassessable)."""
    same = diff = unassessable = 0
    for f in CORE_FIELDS:
        bucket = VERDICT_TO_BUCKET[field_verdicts[f]]
        if bucket == 'SAME':
            same += 1
        elif bucket == 'DIFFERENT':
            diff += 1
        else:
            unassessable += 1

    # R08: Axis A (evidence completeness) - depends only on core_unassessable
    if unassessable == 0:
        axis_a = 'Fully Assessable'
    elif unassessable == len(CORE_FIELDS):
        axis_a = 'Insufficient Evidence'
    else:
        axis_a = 'Partially Assessable'

    # R09: Axis B (protocol relationship) - depends only on (core_same, core_diff)
    if same == 0 and diff == 0:
        axis_b = 'Undetermined'
    elif same > 0 and diff == 0:
        axis_b = 'Same'
    elif same == 0 and diff > 0:
        axis_b = 'Different'
    else:
        axis_b = 'Mixed'

    return axis_a, axis_b, same, diff, unassessable


def strict_flags(field_verdicts):
    f04b = VERDICT_TO_BUCKET[field_verdicts['F04']]
    f16b = VERDICT_TO_BUCKET[field_verdicts['F16']]
    return {
        'strict_incompatible': f04b == 'DIFFERENT' or f16b == 'DIFFERENT',
        'strict_both_incompatible': f04b == 'DIFFERENT' and f16b == 'DIFFERENT',
        'strict_unresolved_at_least_one': f04b == 'UNASSESSABLE' or f16b == 'UNASSESSABLE',
        'strict_unresolved_both': f04b == 'UNASSESSABLE' and f16b == 'UNASSESSABLE',
    }


def main(path):
    with open(path) as f:
        data = json.load(f)
    n = len(data)

    axis_a_counts = Counter()
    axis_b_counts = Counter()
    strict_incompatible = strict_both = strict_unresolved_1 = strict_unresolved_both = 0
    mismatches_a = mismatches_b = 0

    for p in data:
        fv = p['field_verdicts']
        aa, ab, same, diff, unas = classify_pair(fv)
        axis_a_counts[aa] += 1
        axis_b_counts[ab] += 1

        # cross-check against the file's own stored values, if present
        stored_a = p.get('axis_a_v05', p.get('axis_a'))
        stored_b = p.get('axis_b_v05', p.get('axis_b'))
        if stored_a is not None and stored_a != aa:
            mismatches_a += 1
        if stored_b is not None and stored_b != ab:
            mismatches_b += 1

        sf = strict_flags(fv)
        strict_incompatible += sf['strict_incompatible']
        strict_both += sf['strict_both_incompatible']
        strict_unresolved_1 += sf['strict_unresolved_at_least_one']
        strict_unresolved_both += sf['strict_unresolved_both']

    print(f"File: {path}")
    print(f"Total pairs: {n}\n")

    print("Axis A (evidence completeness):")
    for k, v in axis_a_counts.items():
        print(f"  {k}: {v} ({100*v/n:.4f}%)")

    print("\nAxis B (protocol relationship):")
    for k, v in axis_b_counts.items():
        print(f"  {k}: {v} ({100*v/n:.4f}%)")

    print(f"\nStrict-field flags (F04/F16):")
    print(f"  incompatible (>=1 DIFFERENT): {strict_incompatible} ({100*strict_incompatible/n:.4f}%)")
    print(f"  both incompatible: {strict_both} ({100*strict_both/n:.4f}%)")
    print(f"  unresolved (>=1 UNASSESSABLE): {strict_unresolved_1} ({100*strict_unresolved_1/n:.4f}%)")
    print(f"  unresolved (both): {strict_unresolved_both} ({100*strict_unresolved_both/n:.4f}%)")

    if mismatches_a or mismatches_b:
        print(f"\nWARNING: recomputed axis_a differs from file's stored value in {mismatches_a} pairs")
        print(f"WARNING: recomputed axis_b differs from file's stored value in {mismatches_b} pairs")
    else:
        print("\n(Recomputed axis_a/axis_b match the file's own stored values exactly, where present.)")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <pairs.json>")
        sys.exit(1)
    main(sys.argv[1])
