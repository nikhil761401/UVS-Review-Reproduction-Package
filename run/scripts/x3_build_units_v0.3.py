#!/usr/bin/env python3
"""
v0.3 of the pairing-unit judgment engine. Identical to x3_build_units_v0.2.py EXCEPT:

  (1) imports the actual canonicalization module via importlib, since x3_canon_v0.2.py /
      x3_canon_v0.3.py were committed under their versioned names, not as a literal
      canon.py the v0.2 file's `from canon import ...` statement assumes exists (this
      import target has never actually existed in scripts/ -- confirmed in
      x3_targeted_tests_v0.3.py's own docstring, which works around it the same way).
  (2) adds two new field-specific branches, F12 and F13, immediately alongside the
      existing F09 bespoke branch -- same pattern, same place in the dispatch order --
      implementing the closed-world axis-aware judgment logic from
      UVS_Phase3_Engine_Extension_Proposal_v3.1.md. All other fields (F01-F08, F09, F11,
      F16) are byte-identical in behavior to v0.2; this file does not change their logic,
      only adds the F12/F13 branches and uses x3_canon_v0.3.py (a superset vocabulary of
      x3_canon_v0.2.py for every field) instead of x3_canon_v0.2.py.

x3_build_units_v0.2.py is left completely unmodified on disk. This file is additive.

Decision-log note (Phase 3 v3.1, entry 36): `annot:single_gt_moot` vs. a real `max`/`mean`
value resolves AMBIGUOUS here -- the flagged, reversible conservative default adopted
because Codebook v0.6's resolution of that specific question was not available when this
file was written. If that question is later resolved to the GENUINE reading instead, only
the `_annot_axis` function below needs to change.
"""
import csv, json, collections, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

_canon_v3 = _load(os.path.join(HERE, 'x3_canon_v0.3.py'), 'canon_v3')
CANON = _canon_v3.CANON
canon_f09_construction = _canon_v3.canon_f09_construction
canon_f09_annotator_count = _canon_v3.canon_f09_annotator_count
canon_f12 = _canon_v3.canon_f12
canon_f13 = _canon_v3.canon_f13

ex = list(csv.DictReader(open(os.path.join(HERE, '..', 'UVS_Core_v1.0_Extraction.csv'))))
STABLE_FIELDS = ['F01','F02','F03','F04','F06','F07','F08','F09','F11','F12','F13','F16']

# index: (study, setting, dataset, field) -> row  [verbatim from x3_build_units_v0.2.py]
idx = {}
for r in ex:
    idx[(r['study_id'], r['setting'], r['dataset'], r['field'])] = r

# also index by (study, setting) ignoring dataset for joint rows (F03/F04 joint "TVSum/SumMe (joint)")
idx_joint = {}
for r in ex:
    if 'joint' in r['dataset'].lower():
        idx_joint[(r['study_id'], r['setting'], r['field'])] = r

mapping_rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'UVS_X3_Protocol_Setting_Mapping_v0.2.csv'))))
# register: (study, child_setting_prefix, field) -> decision row
REGISTER = collections.defaultdict(dict)
for m in mapping_rows:
    REGISTER[m['study']][(m['child_setting'], m['field'])] = m

def find_register_entry(study, setting, field):
    entries = REGISTER.get(study, {})
    for (child, f), m in entries.items():
        if f != field:
            continue
        if child in setting or setting in child or child.split(' (')[0] in setting:
            return m
    return None

def lookup(study, setting, dataset, field):
    """Direct lookup, with joint-row fallback, matching the original build_x3.py behavior."""
    r = idx.get((study, setting, dataset, field))
    if r:
        return r
    r = idx_joint.get((study, setting, field))
    if r:
        return r
    return None

def resolve_field(study, setting, dataset, field):
    """Returns (row_or_none, provenance_tag) where provenance_tag in
    {'direct','inherited','blocked','missing'}."""
    r = lookup(study, setting, dataset, field)
    if r:
        return r, 'direct'
    reg = find_register_entry(study, setting, field)
    if reg is None:
        return None, 'missing'
    if reg['decision'] == 'INHERIT':
        parent_setting = reg['parent_setting']
        candidates = [rr for rr in ex if rr['study_id'] == study and rr['field'] == field
                      and rr['dataset'] == dataset and parent_setting.split(' (')[0][:30] in rr['setting']]
        if not candidates:
            candidates = [rr for rr in ex if rr['study_id'] == study and rr['field'] == field
                          and parent_setting.split(' (')[0][:30] in rr['setting']
                          and ('joint' in rr['dataset'].lower() or rr['dataset'] == dataset)]
        if candidates:
            return candidates[0], 'inherited'
        return None, 'missing'
    if reg['decision'] in ('DO-NOT-INHERIT', 'NEEDS-VERIFICATION'):
        return None, 'blocked'
    return None, 'missing'  # NOT-APPLICABLE with no direct row left = genuinely missing

# ---------------------------------------------------------------------------------------
# F13 closed-world judgment (UVS_Phase3_Engine_Extension_Proposal_v3.1.md, Section 1)
# ---------------------------------------------------------------------------------------
_KNOWN_DATASETS = ('tvsum', 'summe', 'ovp', 'youtube', 'cosum', 'vtw', 'wikihow', 'finegym', 'ostd')
_F13_METHOD_TAGS = {
    'method:test_set_oracle_selection', 'method:validation_set_selection',
    'method:grid_search_tuned', 'method:fixed_epoch_no_selection',
    'method:sensitivity_analysis_hyperparameter_tuning',
}
_F13_UNKNOWN_DATA_LITERAL = 'tuning_data:explicitly_not_stated'
_F13_NAMED_DATASET_PREFIX = 'tuning_data:named_dataset:'

def _f13_recognized(tag):
    if tag in ('NA', 'NR'):
        return True
    if tag in _F13_METHOD_TAGS:
        return True
    if tag == _F13_UNKNOWN_DATA_LITERAL:
        return True
    if tag.startswith(_F13_NAMED_DATASET_PREFIX):
        return tag[len(_F13_NAMED_DATASET_PREFIX):] in _KNOWN_DATASETS
    return False

def f13_judge(t1, t2):
    if not (t1 and t2):
        return 'AMBIGUOUS', 'F13 canonicalization rule did not fire on at least one side'
    if not all(_f13_recognized(x) for x in t1) or not all(_f13_recognized(x) for x in t2):
        return 'AMBIGUOUS', 'an unrecognized F13 tag is present on at least one side (closed-world check failed)'
    m1 = t1 & _F13_METHOD_TAGS; m2 = t2 & _F13_METHOD_TAGS
    if m1 and m2:
        if m1.isdisjoint(m2):
            return 'GENUINE', f'disjoint F13 method categories ({sorted(m1)} vs {sorted(m2)})'
        if m1 != m2 or len(m1) != 1:
            return 'AMBIGUOUS', 'F13 method-tag sets overlap but are not a clean single-category match'
        if m1 == {'method:sensitivity_analysis_hyperparameter_tuning'}:
            d1 = t1 - _F13_METHOD_TAGS; d2 = t2 - _F13_METHOD_TAGS
            if d1 == {_F13_UNKNOWN_DATA_LITERAL} or d2 == {_F13_UNKNOWN_DATA_LITERAL}:
                return 'AMBIGUOUS', 'tuning-data provenance unknown on at least one side'
            if d1 and d2:
                return ('WORDING-ONLY' if d1 == d2 else 'GENUINE'), f'tuning-data tags {sorted(d1)} vs {sorted(d2)}'
            return 'AMBIGUOUS', 'tuning-data sub-tag did not resolve on at least one side'
        return 'WORDING-ONLY', f'same F13 method category ({sorted(m1)})'
    return 'AMBIGUOUS', 'no recognized F13 method tag present on at least one side'

# ---------------------------------------------------------------------------------------
# F12 closed-world, axis-aware judgment (same proposal, Section 2-3)
# ---------------------------------------------------------------------------------------
_F12_ACROSS_KNOWN = {'across:mean_over_splits'}
_F12_ACROSS_UNKNOWN = {'across:explicitly_not_stated'}
_F12_ACROSS_RECOGNIZED = _F12_ACROSS_KNOWN | _F12_ACROSS_UNKNOWN

_F12_ANNOT_KNOWN_VALUE = {'annot:max', 'annot:mean'}
_F12_ANNOT_MOOT = 'annot:single_gt_moot'
_F12_ANNOT_UNKNOWN = {'annot:explicitly_not_stated', 'annot:cited_external_rule'}
_F12_ANNOT_RECOGNIZED = _F12_ANNOT_KNOWN_VALUE | {_F12_ANNOT_MOOT} | _F12_ANNOT_UNKNOWN

def _recognized(tagset, allowed):
    return all(t in allowed for t in tagset)

def _across_axis(a1, a2):
    if not _recognized(a1, _F12_ACROSS_RECOGNIZED) or not _recognized(a2, _F12_ACROSS_RECOGNIZED):
        return 'UNASSESSABLE'
    k1 = a1 & _F12_ACROSS_KNOWN; u1 = bool(a1 & _F12_ACROSS_UNKNOWN)
    k2 = a2 & _F12_ACROSS_KNOWN; u2 = bool(a2 & _F12_ACROSS_UNKNOWN)
    if (k1 and u1) or (k2 and u2):
        return 'UNASSESSABLE'
    if k1 and k2:
        return 'MATCH' if k1 == k2 else 'DIFFERENT'
    if not a1 and not a2:
        return 'BOTH_ABSENT'
    return 'UNASSESSABLE'

def _annot_axis(n1, n2):
    if not _recognized(n1, _F12_ANNOT_RECOGNIZED) or not _recognized(n2, _F12_ANNOT_RECOGNIZED):
        return 'UNASSESSABLE'
    k1 = n1 & _F12_ANNOT_KNOWN_VALUE; u1 = bool(n1 & _F12_ANNOT_UNKNOWN); moot1 = _F12_ANNOT_MOOT in n1
    k2 = n2 & _F12_ANNOT_KNOWN_VALUE; u2 = bool(n2 & _F12_ANNOT_UNKNOWN); moot2 = _F12_ANNOT_MOOT in n2
    if (k1 and u1) or (k2 and u2):
        return 'UNASSESSABLE'
    if (k1 and moot1) or (k2 and moot2):
        return 'UNASSESSABLE'
    if (moot1 and u1) or (moot2 and u2):
        return 'UNASSESSABLE'
    if moot1 and moot2:
        return 'MATCH'
    if moot1 or moot2:
        # Decision-log entry 36: flagged conservative default, adopted now (see module docstring).
        return 'UNASSESSABLE'
    if k1 and k2:
        return 'MATCH' if k1 == k2 else 'DIFFERENT'
    if not n1 and not n2:
        return 'BOTH_ABSENT'
    return 'UNASSESSABLE'

def f12_judge(t1, t2):
    if not (t1 and t2):
        return 'AMBIGUOUS', 'F12 canonicalization rule did not fire on at least one side'
    a1 = {x for x in t1 if x.startswith('across:')}; a2 = {x for x in t2 if x.startswith('across:')}
    n1 = {x for x in t1 if x.startswith('annot:')};  n2 = {x for x in t2 if x.startswith('annot:')}
    sv = _across_axis(a1, a2)
    av = _annot_axis(n1, n2)
    if sv == 'DIFFERENT' or av == 'DIFFERENT':
        return 'GENUINE', f'axis difference (split={sv}, annot={av})'
    if sv in ('MATCH', 'BOTH_ABSENT') and av in ('MATCH', 'BOTH_ABSENT'):
        return 'WORDING-ONLY', f'both axes match or both-absent (split={sv}, annot={av})'
    return 'AMBIGUOUS', f'at least one axis unassessable (split={sv}, annot={av})'

# ---------------------------------------------------------------------------------------
def judge_dimension(field, row1, prov1, row2, prov2):
    status1 = row1['status'] if row1 else None
    status2 = row2['status'] if row2 else None
    val1 = row1['value'] if row1 else None
    val2 = row2['value'] if row2 else None

    if prov1 == 'blocked' or prov2 == 'blocked':
        return 'INHERITANCE-BLOCKED', 'at least one side requires an inheritance decision the register marks DO-NOT-INHERIT or NEEDS-VERIFICATION; not safe to compare'
    if row1 is None or row2 is None:
        return 'MISSING-BY-CONSTRUCTION', 'no direct value and no applicable INHERIT rule on at least one side'
    if status1 == 'UNA' or status2 == 'UNA':
        if status1 == status2 == 'UNA':
            return 'UNA-GENUINE', 'both sides UNA: evidence exists but is inaccessible per the paper\'s own access limits on both sides'
        return 'AMBIGUOUS', 'one side UNA (inaccessible), the other has a value -- cannot confirm a real difference against an inaccessible value'
    if status1 in ('NR', 'NA') and status2 in ('NR', 'NA') and status1 == status2:
        return (f'{status1}-GENUINE'), f'both sides {status1}, consistent (not merged with the other missingness state)'
    if status1 in ('NR', 'NA') and status2 in ('NR', 'NA') and status1 != status2:
        return 'AMBIGUOUS', f'one side NR, other NA -- genuinely different missingness KIND, not merged, left for review'

    if field == 'F09':
        c1, _ = canon_f09_construction(val1)
        c2, _ = canon_f09_construction(val2)
        a1 = annot_range(val1)
        a2 = annot_range(val2)
        if a1 and a2 and ranges_overlap(a1, a2) and c1 and c2 and c1 == c2:
            return 'WORDING-ONLY', f'same annotator-count range {a1}/{a2} overlap and same construction tags {sorted(c1)}'
        if a1 and a2 and not ranges_overlap(a1, a2):
            return 'GENUINE', f'annotator-count ranges do not overlap ({a1} vs {a2})'
        if c1 and c2 and c1 != c2 and c1.isdisjoint(c2):
            return 'GENUINE', f'disjoint construction-method tags ({sorted(c1)} vs {sorted(c2)})'
        return 'AMBIGUOUS', 'F09 sub-field rules did not both resolve on this pair'

    if field == 'F12':
        t1, _ = canon_f12(val1, status1)
        t2, _ = canon_f12(val2, status2)
        return f12_judge(t1, t2)

    if field == 'F13':
        t1, _ = canon_f13(val1, status1)
        t2, _ = canon_f13(val2, status2)
        return f13_judge(t1, t2)

    fn = CANON.get(field)
    if fn is None:
        return 'AMBIGUOUS', f'{field} has no canonicalization rule'
    try:
        t1, conf1 = fn(val1, status1)
        t2, conf2 = fn(val2, status2)
    except TypeError:
        t1, conf1 = fn(val1)
        t2, conf2 = fn(val2)
    if t1 and t2:
        if t1 == t2:
            return 'WORDING-ONLY', f'both canonicalize to {sorted(t1)}'
        if t1.isdisjoint(t2):
            return 'GENUINE', f'disjoint canonical tags ({sorted(t1)} vs {sorted(t2)})'
        return 'AMBIGUOUS', f'partial tag overlap ({sorted(t1 & t2)}) -- not a clean match or a clean difference'
    return 'AMBIGUOUS', f'{field} canonicalization rule did not fire on at least one side'

def annot_range(v):
    import re
    if not v:
        return None
    nums = [int(x) for x in re.findall(r'\b(\d{1,2})\b', v) if 1 <= int(x) <= 30]
    return (min(nums), max(nums)) if nums else None

def ranges_overlap(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])

if __name__ == '__main__':
    # Scoped, as in v0.2, to the 30-pair regression sample -- NOT the full 17,973-pair
    # universe, which remains unauthorized pending explicit approval of that specific step.
    sample = json.load(open(os.path.join(HERE, '..', 'x3_sample.json')))
    out = []
    counts = collections.Counter()
    for i, pair in enumerate(sample, 1):
        s1, set1, s2, set2, ds = pair['study_1'], pair['setting_1'], pair['study_2'], pair['setting_2'], pair['dataset']
        for field in STABLE_FIELDS:
            row1, prov1 = resolve_field(s1, set1, ds, field)
            row2, prov2 = resolve_field(s2, set2, ds, field)
            verdict, rationale = judge_dimension(field, row1, prov1, row2, prov2)
            counts[verdict] += 1
            out.append({
                'pair': i, 'study_1': s1, 'setting_1': set1, 'study_2': s2, 'setting_2': set2, 'dataset': ds,
                'field': field, 'prov1': prov1, 'prov2': prov2,
                's1_status': row1['status'] if row1 else None, 's1_value': row1['value'] if row1 else None,
                's2_status': row2['status'] if row2 else None, 's2_value': row2['value'] if row2 else None,
                'verdict_v0.3': verdict, 'rationale': rationale,
            })
    json.dump(out, open(os.path.join(HERE, '..', 'x3_v0.3_regression_annotations.json'), 'w'), indent=2)
    print('total rows:', len(out))
    print(counts)
    pct_sum = sum(counts.values())
    for k, v in sorted(counts.items()):
        print(f'{k}: {v} ({100*v/pct_sum:.2f}%)')
    print('SUM CHECK: %.4f%%' % sum(100*v/pct_sum for v in counts.values()))
