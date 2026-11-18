"""v0.5 two-axis classifier (evidence completeness x protocol relationship) + separate
strict-field incompatibility flags.

New, additive module. Does not modify x3_build_units_v0.3.py, x3_full_analysis_v0.3.py,
any canonicalization module, v04_classify.py, or any prior output. Reads only the raw
per-field verdict strings already stored in x3_v0.4_full_analysis_pairs.json's
field_verdicts (identical source values used by v0.4; the field-level engine is not rerun).

Design rationale (full text: UVS_X3_v0.5_Two_Axis_Methodology_Proposal.md):

Axis A (evidence completeness) and Axis B (protocol relationship) are each computed from
a different, non-overlapping projection of the same (core_same, core_diff, core_unassessable)
triple, which always sums to len(CORE_FIELDS) = 10:
  - Axis A depends only on core_unassessable.
  - Axis B depends only on (core_same, core_diff).
This is what "evaluated independently" means operationally: neither axis's category
boundaries reference the other axis's inputs. An unresolved field changes Axis A without
being able to erase a confirmed SAME or DIFFERENT elsewhere, because Axis B's categories are
defined purely from counts of resolved (SAME/DIFFERENT) fields, with unresolved fields simply
absent from that count -- never overwriting a resolved verdict.

A3 (Insufficient Evidence) is defined as core_unassessable == len(CORE_FIELDS), i.e. literally
zero core fields assessable. This is not an invented minimum-evidence threshold -- it is the
only point on the 0-10 scale that requires no cutoff choice at all (the natural zero-information
boundary). No other cutoff (e.g. "at least 3 fields must be assessable") is used, per the
task's explicit instruction not to invent one.

Strict fields (F04, F16) are reported as an independent incompatibility flag, not folded into
Axis A or Axis B, for two reasons documented in UVS_X3_v0.5_Strict_Field_Analysis.md:
 (1) Codebook v0.6 treats strict dimensions as a categorically different kind of check
     (an incompatibility gate) from the ten core comparability dimensions;
 (2) empirically, strict-field evidence is overwhelmingly incomplete (in this corpus, at
     least one strict field is UNASSESSABLE for 93.94% of pairs), so folding an unresolved
     strict judgment into Axis A's completeness count or into Axis B's relationship count
     would dominate and distort the graded core-dimension signal that these two axes exist
     to preserve.
"""

CORE_FIELDS = ['F01', 'F02', 'F03', 'F06', 'F07', 'F08', 'F09', 'F11', 'F12', 'F13']
STRICT_FIELDS = ['F04', 'F16']

# Identical to the v0.4 mapping (UVS_X3_v0.4_Classification_Methodology_Decision.md, Section 3
# -- the project owner's explicit ruling). Not modified here; Section 3 of Stage G re-verifies
# it against Codebook v0.6 and the two schema drafts and finds no reason to change it.
VERDICT_TO_BUCKET = {
    'WORDING-ONLY': 'SAME',
    'GENUINE': 'DIFFERENT',
    'NR-GENUINE': 'UNASSESSABLE',
    'UNA-GENUINE': 'UNASSESSABLE',
    'NA-GENUINE': 'SAME',              # bucket for classification purposes
    'AMBIGUOUS': 'UNASSESSABLE',
    'MISSING-BY-CONSTRUCTION': 'UNASSESSABLE',
    'INHERITANCE-BLOCKED': 'UNASSESSABLE',
}
# Separate tag, never collapsed into the SAME count silently (same discipline as v0.4).
NA_STRUCTURAL_VERDICT = 'NA-GENUINE'


def bucket_of(raw_verdict):
    if raw_verdict not in VERDICT_TO_BUCKET:
        raise ValueError(f"Unrecognized raw verdict: {raw_verdict!r}")
    return VERDICT_TO_BUCKET[raw_verdict]


def classify_v05(field_verdicts):
    """field_verdicts: dict of field -> raw verdict string, covering all 12 stable fields
    (10 CORE_FIELDS + 2 STRICT_FIELDS).

    Returns (axis_a, axis_b, strict_detail, detail_dict):
      axis_a            : 'Fully Assessable' | 'Partially Assessable' | 'Insufficient Evidence'
      axis_b             : 'Same' | 'Mixed' | 'Different' | 'Undetermined'
      strict_detail      : dict with f04_bucket, f16_bucket, strict_incompatible,
                            strict_unresolved, strict_both_incompatible
      detail_dict        : core_same, core_diff, core_unassessable, na_structural_core_count,
                            core_same_fields, core_diff_fields, core_unassessable_fields
    """
    all_fields = CORE_FIELDS + STRICT_FIELDS
    missing = [f for f in all_fields if f not in field_verdicts]
    if missing:
        raise ValueError(f"Missing field verdicts: {missing}")

    core_buckets = {f: bucket_of(field_verdicts[f]) for f in CORE_FIELDS}
    strict_buckets = {f: bucket_of(field_verdicts[f]) for f in STRICT_FIELDS}

    core_same = sum(1 for v in core_buckets.values() if v == 'SAME')
    core_diff = sum(1 for v in core_buckets.values() if v == 'DIFFERENT')
    core_unassessable = sum(1 for v in core_buckets.values() if v == 'UNASSESSABLE')
    assert core_same + core_diff + core_unassessable == len(CORE_FIELDS)

    na_structural_core = sum(
        1 for f in CORE_FIELDS if field_verdicts[f] == NA_STRUCTURAL_VERDICT
    )

    # --- Axis A: evidence completeness (depends only on core_unassessable) ---
    if core_unassessable == 0:
        axis_a = 'Fully Assessable'
    elif core_unassessable == len(CORE_FIELDS):
        axis_a = 'Insufficient Evidence'
    else:
        axis_a = 'Partially Assessable'

    # --- Axis B: protocol relationship (depends only on core_same, core_diff) ---
    if core_same == 0 and core_diff == 0:
        axis_b = 'Undetermined'
    elif core_same > 0 and core_diff == 0:
        axis_b = 'Same'
    elif core_same == 0 and core_diff > 0:
        axis_b = 'Different'
    else:
        axis_b = 'Mixed'

    # --- Strict-field incompatibility: independent flag, never folded into Axis A/B ---
    f04_bucket = strict_buckets['F04']
    f16_bucket = strict_buckets['F16']
    strict_incompatible = (f04_bucket == 'DIFFERENT') or (f16_bucket == 'DIFFERENT')
    strict_both_incompatible = (f04_bucket == 'DIFFERENT') and (f16_bucket == 'DIFFERENT')
    strict_unresolved = (f04_bucket == 'UNASSESSABLE') or (f16_bucket == 'UNASSESSABLE')

    strict_detail = {
        'f04_bucket': f04_bucket,
        'f16_bucket': f16_bucket,
        'strict_incompatible': strict_incompatible,
        'strict_both_incompatible': strict_both_incompatible,
        'strict_unresolved': strict_unresolved,
    }

    detail = {
        'core_same': core_same,
        'core_diff': core_diff,
        'core_unassessable': core_unassessable,
        'na_structural_core_count': na_structural_core,
        'core_same_fields': [f for f in CORE_FIELDS if core_buckets[f] == 'SAME'],
        'core_diff_fields': [f for f in CORE_FIELDS if core_buckets[f] == 'DIFFERENT'],
        'core_unassessable_fields': [f for f in CORE_FIELDS if core_buckets[f] == 'UNASSESSABLE'],
    }

    return axis_a, axis_b, strict_detail, detail
