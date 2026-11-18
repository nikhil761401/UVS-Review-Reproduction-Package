#!/usr/bin/env python3
"""
The full 17,973-pair X3 analysis, run for the first time in this project, using the
real v0.3 production engine (scripts/x3_build_units_v0.3.py: v3.1's closed-world,
axis-aware F12/F13 logic + the now-fully-resolved mapping register) instead of the
v0.1 diagnostic's naive exact-string-match comparator.

Eligible-pair universe is defined EXACTLY as in scripts/build_x3.py (unchanged logic,
reproduced here, not altered): unsupervised-labeled settings, TVSum/SumMe datasets only,
F1-metric-family only, cross-paper pairs only (same-study self-pairs excluded),
combinations within each dataset. This reproduces the same 17,973-pair count reported in
UVS_X3_Pairwise_Report_v0.1.md as a sanity check that the eligible-unit universe itself
has not silently changed.

Per-pair field judgment: scripts/x3_build_units_v0.3.py's judge_dimension(), called once
per (pair, field) for all 12 STABLE_FIELDS (F01,F02,F03,F04,F06,F07,F08,F09,F11,F12,F13,F16)
via resolve_field() (which consults the mapping register for inheritance, exactly as the
30-pair regression sample did).

Pair-level classification (translates the v0.1 report's Directly/Partially Comparable /
Cannot Be Assessed taxonomy onto the real verdict set, replacing naive string-equality
with the actual canonicalization + axis-aware judgment):
  SAME         <- WORDING-ONLY, NR-GENUINE, NA-GENUINE, UNA-GENUINE
  DIFFERENT    <- GENUINE
  UNASSESSABLE <- AMBIGUOUS, MISSING-BY-CONSTRUCTION, INHERITANCE-BLOCKED
  CORE_FIELDS   = F01,F02,F03,F06,F07,F08,F09,F11,F12,F13  (10 fields)
  STRICT_FIELDS = F04, F16                                  (2 fields)
  any STRICT field DIFFERENT                                 -> Cannot Be Assessed
  elif all CORE fields SAME                                  -> Directly Comparable
  elif count(CORE fields DIFFERENT) > 2                       -> Cannot Be Assessed
  elif any CORE field DIFFERENT                               -> Partially Comparable
  elif any CORE field UNASSESSABLE                            -> Cannot Be Assessed
  else                                                         -> Partially Comparable
"""
import csv, re, json, itertools, collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'scripts'))
import importlib.util
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
v03 = _load(os.path.join(HERE, 'scripts', 'x3_build_units_v0.3.py'), 'x3v03')

# ============================================================================
# PROSPECTIVE v0.6 METHODOLOGICAL CLARIFICATION (NEW decision, not part of the
# frozen v0.4-owner-ruled codebook or any historical pre-registration).
#
# Rationale (Stage 1E/1F audit, 2026-11-17): the original judge_dimension()
# already short-circuits to AMBIGUOUS whenever exactly one side's status is
# UNA (inaccessible evidence), but has NO analogous one-sided guard for NA or
# NR. Confirmed by direct execution that this asymmetry lets a single-sided
# NA/NR case fall through to the generic canonicalization path, where the
# missingness status itself (as a literal 'NA'/'NR' tag, or free text
# explaining *why* a field is NA/NR) gets pattern-matched as if it were a
# real reported value -- producing spurious GENUINE/WORDING-ONLY verdicts.
# Confirmed concretely for F03/F06/F16 (literal NA/NR tag vs real tag),
# F09 (annot_range() reading citation brackets '[19],[20]' as an annotator
# count), F02 (keyword match on NA-explanatory prose), and F08 (percentage
# regex matching a number inside NR-explanatory prose).
#
# Prospective rule: generalize the EXISTING one-sided-UNA guard to also cover
# one-sided NA and one-sided NR, symmetrically, with the same AMBIGUOUS
# destination the engine already uses for one-sided UNA. Symmetric cases
# (both sides identical status) are UNCHANGED and keep their existing
# NA-GENUINE / NR-GENUINE / UNA-GENUINE treatment.
# ============================================================================
_original_judge_dimension = v03.judge_dimension

def _judge_dimension_v06(field, row1, prov1, row2, prov2):
    status1 = row1['status'] if row1 else None
    status2 = row2['status'] if row2 else None
    missing = {'NA', 'NR', 'UNA'}
    if row1 is not None and row2 is not None and status1 != status2:
        if (status1 in missing) != (status2 in missing):
            # exactly one side is a missingness status, the other is not
            return 'AMBIGUOUS', 'PROSPECTIVE v0.6: one-sided missingness status (%s/%s) vs a reported side -- generalized from the existing one-sided-UNA guard' % (status1, status2)
    return _original_judge_dimension(field, row1, prov1, row2, prov2)

v03.judge_dimension = _judge_dimension_v06


ex = v03.ex
FIELDS_FOR_ELIGIBILITY = ['F01','F02','F03','F04','F06','F07','F08','F09','F10','F11','F12','F13','F16','F18']
STABLE_FIELDS = v03.STABLE_FIELDS  # 12 fields, excludes F10/F18 (eligibility-only)

# ---- 1. Build per-unit (study,setting,dataset) field profiles (verbatim from build_x3.py) ----
units = {}
joint_fields = {}
for r in ex:
    if r['field'] not in FIELDS_FOR_ELIGIBILITY:
        continue
    key = (r['study_id'], r['setting'], r['dataset'])
    d = r['dataset'].lower()
    rec = {'value': r['value'], 'status': r['status']}
    if r['field'] != 'F01' and r['field'] != 'F18' and ('joint' in d or d in ('tvsum/summe', 'tvsum/summe (joint)')):
        joint_fields.setdefault((r['study_id'], r['setting']), {})[r['field']] = rec
    else:
        units.setdefault(key, {})[r['field']] = rec

for (sid, joint_setting), fields in joint_fields.items():
    for key in list(units.keys()):
        if key[0] == sid and key[2] in ('TVSum', 'SumMe'):
            for f, rec in fields.items():
                units[key].setdefault(f, rec)

def is_tvsum_summe(u):
    return u[2] in ('TVSum', 'SumMe')

def is_supervised_setting(setting):
    return bool(re.search(r'(?<!un)supervised', setting, re.I))

def metric_family(u):
    rec = units[u].get('F10')
    f18 = units[u].get('F18')
    text = ((rec['value'] if rec else '') + ' ' + (f18['value'] if f18 else '')).lower()
    if 'map' in text and 'f1' not in text and 'f-score' not in text:
        return 'mAP'
    if ('f1' in text or 'f-score' in text or 'fscore' in text):
        return 'F1'
    if 'correlation' in text or 'kendall' in text or 'spearman' in text or re.search(r'\btau\b|\brho\b', text):
        return 'correlation-only'
    return 'unknown'

elig = [u for u in units if is_tvsum_summe(u) and not is_supervised_setting(u[1]) and metric_family(u) == 'F1']

by_dataset = collections.defaultdict(list)
for u in elig:
    by_dataset[u[2]].append(u)

pairs = []
for dataset, ulist in by_dataset.items():
    for u1, u2 in itertools.combinations(sorted(ulist), 2):
        if u1[0] == u2[0]:
            continue
        pairs.append((dataset, u1, u2))

print(f'eligible F1 unsupervised TVSum/SumMe units: {len(elig)}', file=sys.stderr)
print(f'total cross-paper pairs generated: {len(pairs)}', file=sys.stderr)

# ---- 2. Judge every field for every pair using the REAL v0.3 engine ----
SAME = {'WORDING-ONLY', 'NR-GENUINE', 'NA-GENUINE', 'UNA-GENUINE'}
DIFFERENT = {'GENUINE'}
UNASSESSABLE = {'AMBIGUOUS', 'MISSING-BY-CONSTRUCTION', 'INHERITANCE-BLOCKED'}
CORE_FIELDS = ['F01','F02','F03','F06','F07','F08','F09','F11','F12','F13']
STRICT_FIELDS = ['F04', 'F16']

def classify(bucket):
    strict_diff = sum(1 for f in STRICT_FIELDS if bucket[f] == 'DIFFERENT')
    core_diff = sum(1 for f in CORE_FIELDS if bucket[f] == 'DIFFERENT')
    core_unassessable = sum(1 for f in CORE_FIELDS if bucket[f] == 'UNASSESSABLE')
    core_same = sum(1 for f in CORE_FIELDS if bucket[f] == 'SAME')
    if strict_diff > 0:
        return 'Cannot Be Assessed'
    if core_same == len(CORE_FIELDS):
        return 'Directly Comparable'
    if core_diff > 2:
        return 'Cannot Be Assessed'
    if core_diff > 0:
        return 'Partially Comparable'
    if core_unassessable > 0:
        return 'Cannot Be Assessed'
    return 'Partially Comparable'

field_verdict_counts = collections.defaultdict(collections.Counter)
pair_class_counts = collections.Counter()
pair_rows = []

for dataset, u1, u2 in pairs:
    bucket = {}
    field_verdicts = {}
    for field in STABLE_FIELDS:
        row1, prov1 = v03.resolve_field(u1[0], u1[1], u1[2], field)
        row2, prov2 = v03.resolve_field(u2[0], u2[1], u2[2], field)
        verdict, rationale = v03.judge_dimension(field, row1, prov1, row2, prov2)
        field_verdict_counts[field][verdict] += 1
        field_verdicts[field] = verdict
        if verdict in SAME:
            bucket[field] = 'SAME'
        elif verdict in DIFFERENT:
            bucket[field] = 'DIFFERENT'
        else:
            bucket[field] = 'UNASSESSABLE'
    pcls = classify(bucket)
    pair_class_counts[pcls] += 1
    pair_rows.append({
        'dataset': dataset, 'study_1': u1[0], 'setting_1': u1[1],
        'study_2': u2[0], 'setting_2': u2[1], 'pair_class': pcls,
        'field_verdicts': field_verdicts,
    })

print('=== PAIR-CLASS SUMMARY (17,973-pair universe, v0.3 engine) ===')
total = sum(pair_class_counts.values())
for k in ('Directly Comparable', 'Partially Comparable', 'Cannot Be Assessed'):
    v = pair_class_counts.get(k, 0)
    print(f'{k}: {v} ({100*v/total:.4f}%)')
print(f'TOTAL: {total}')
print()
print('=== BY DATASET ===')
by_ds = collections.Counter()
by_ds_total = collections.Counter()
for row in pair_rows:
    by_ds_total[row['dataset']] += 1
    if row['pair_class'] == 'Directly Comparable':
        by_ds[row['dataset']] += 1
for ds in by_ds_total:
    print(f'{ds}: {by_ds_total[ds]} pairs, {by_ds[ds]} Directly Comparable ({100*by_ds[ds]/by_ds_total[ds]:.2f}%)')
print()
print('=== PER-FIELD VERDICT BREAKDOWN ===')
for field in STABLE_FIELDS:
    c = field_verdict_counts[field]
    t = sum(c.values())
    print(field, {k: f'{v} ({100*v/t:.1f}%)' for k, v in sorted(c.items(), key=lambda kv: -kv[1])})

json.dump({
    'eligible_units': len(elig),
    'total_pairs': len(pairs),
    'pair_class_counts': dict(pair_class_counts),
    'by_dataset': {ds: {'total': by_ds_total[ds], 'directly_comparable': by_ds[ds]} for ds in by_ds_total},
    'field_verdict_counts': {f: dict(c) for f, c in field_verdict_counts.items()},
}, open(os.path.join(HERE, 'x3_v0.6_prospective_summary.json'), 'w'), indent=2)

with open(os.path.join(HERE, 'x3_v0.6_prospective_pairs.json'), 'w') as f:
    json.dump(pair_rows, f, indent=1)

print()
print('Wrote x3_v0.6_prospective_summary.json and x3_v0.6_prospective_pairs.json')
