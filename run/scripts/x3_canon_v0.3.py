#!/usr/bin/env python3
"""
Canonicalization dictionary, v0.3. Extends v0.2 (scripts/x3_canon_v0.2.py, PRESERVED UNCHANGED)
with THREE changes, all scoped to F12 and F13, per the authorized Phase 3 plan:

  1. F12: fixed split-aggregation under-matching (clause-aware detection, replacing a
     too-tight character-gap regex that failed on real phrasing like "Average F-score over
     the five random splits").
  2. F12: added an explicit "cited external rule" tag (`annot:cited_external_rule`) for
     aggregation rules described only by reference to another paper, and explicit
     "component stated as not reported" tags (`annot:explicitly_not_stated`,
     `across:explicitly_not_stated`) distinguishing "paper explicitly says this is not
     reported" from "no information found at all" (silent absence).
  3. F13: added a new, separate hyperparameter-tuning category
     (`method:sensitivity_analysis_hyperparameter_tuning`) for sensitivity-analysis /
     parameter-analysis-based hyperparameter selection, kept distinct from checkpoint/epoch
     selection (oracle / validation / grid-search / fixed-epoch, all unchanged). This new
     category ONLY fires when the tuning-data provenance sub-component is ALSO determinable
     (either a named source, or the paper explicitly states the data is not stated) --
     if the value mentions "sensitivity analysis" but gives no data-provenance information
     at all, the function returns None (stays fully AMBIGUOUS) rather than emitting a
     method-only tag that could spuriously tag-match another value with a different,
     merely-also-unstated data provenance. This design was chosen specifically so F13's new
     category needs NO change to the pair-judgment engine (judge_dimension in
     x3_build_units_v0.2.py): plain tag-set equality already produces the correct outcome.

IMPORTANT -- WHAT THIS FILE DOES NOT DO:
  F12's new tags (`annot:cited_external_rule`, `annot:explicitly_not_stated`,
  `across:explicitly_not_stated`) are NOT safe to run through the existing generic
  tag-set-equality judgment logic unmodified: two values that both cite the same external
  source, or both explicitly omit the same sub-component, would incorrectly resolve
  WORDING-ONLY under that generic logic, which is exactly the false-equivalence risk the
  user's authorization explicitly warned against. This file therefore implements tag
  GENERATION only. It is deliberately NOT wired into any pair-judgment engine (no new
  x3_build_units_v0.3.py was created). See UVS_Phase3_Engine_Extension_Proposal.md for the
  proposed, not-yet-implemented, minimal judge_dimension extension this requires, and why.

Everything not explicitly listed above (F01, F02, F03, F04, F06, F07, F08, F09, F11, F16,
F13's four existing categories, F12's annot:max / annot:mean / annot:single_gt_moot
detection, the module interface) is copied UNCHANGED from x3_canon_v0.2.py.
"""
import re

def _has(v, *pats):
    t = v.lower()
    return any(re.search(p, t) for p in pats)

def _clauses(v):
    """Split a compound value into its component clauses. The extraction convention in this
    corpus consistently uses ';' as the separator between independently-reported sub-facts
    within one field value (confirmed by inspection of every sampled F12/F13 compound value).
    Splitting here, before any keyword search, is what makes the split-aggregation and
    not-stated detection below clause-scoped rather than gap-based: a keyword pair only
    counts as co-occurring if both keywords fall in the SAME clause, which cannot span a ';'
    boundary. This directly addresses the reviewer's instruction not to widen a character-gap
    regex without regard to clause boundaries."""
    return [c.strip() for c in re.split(r';', v) if c.strip()]

# ============================================================================
# F01-F11, F16 : UNCHANGED from v0.2 (copied verbatim for a self-contained module)
# ============================================================================

def canon_f01(v):
    if not v:
        return None, None
    t = v.lower()
    names = frozenset(n for n in ['tvsum', 'summe', 'ovp', 'youtube', 'cosum', 'vtw', 'wikihow',
                                   'finegym', 'ostd'] if n in t)
    return (names if names else None), 'HIGH' if names else None

def canon_f02(v):
    if not v:
        return None, None
    t = v.lower()
    tags = set()
    if _has(t, r'5[\s-]*fold', r'five.{0,10}fold', r'five random', r'5 random'):
        tags.add('kfold_or_repeated_random:5')
    elif _has(t, r'k[\s-]*fold'):
        tags.add('kfold_generic')
    if _has(t, r'80\s*/?\s*20', r'80%.{0,15}20%', r'80-20'):
        tags.add('ratio:80_20')
    if _has(t, r'transfer'):
        tags.add('protocol:transfer_cross_dataset')
    if _has(t, r'augment'):
        tags.add('protocol:augmented_with_extra_data')
    if _has(t, r'canonical'):
        tags.add('protocol:canonical')
    if _has(t, r'no train.{0,5}test split', r'all \d+ videos evaluated', r'no split'):
        tags.add('protocol:no_split_all_videos')
    if _has(t, r'leave[\s-]*one[\s-]*out'):
        tags.add('protocol:leave_one_out')
    if _has(t, r'cross[\s-]*database', r'train.{0,15}tested on'):
        tags.add('protocol:cross_database')
    if not tags:
        return None, None
    conf = 'HIGH' if len(tags) >= 2 else 'MEDIUM'
    return frozenset(tags), conf

def canon_f03(v, status=None):
    if status == 'NA':
        return frozenset(['NA']), 'HIGH'
    if not v:
        return None, None
    t = v.lower()
    tags = set()
    if _has(t, r'contrastive'):
        tags.add('paradigm:contrastive')
    if _has(t, r'adversarial', r'\bgan\b'):
        tags.add('paradigm:adversarial_gan')
    if _has(t, r'reinforce', r'reward', r'policy', r'bernoulli'):
        tags.add('paradigm:rl_reward')
    if _has(t, r'self[\s-]*supervised', r'masked[\s-]*reconstruction', r'reconstruction'):
        tags.add('paradigm:self_supervised_reconstruction')
    if _has(t, r'supervised') and not _has(t, r'unsupervised', r'self[\s-]*supervised'):
        tags.add('paradigm:supervised')
    if _has(t, r'without using any labels', r'label[\s-]*free', r'no ground[\s-]*truth'):
        tags.add('paradigm:label_free')
    if _has(t, r'training[\s-]*free'):
        tags.add('paradigm:training_free')
    if _has(t, r'other.{0,10}datasets?', r'augment', r'pooled'):
        tags.add('data:augmented_with_other_datasets')
    if _has(t, r'target.{0,10}only', r"target\'?s? training set", r'80%.{0,20}training'):
        tags.add('data:target_only')
    if _has(t, r'other three databases', r'trained on other', r'none of the target'):
        tags.add('data:transfer_only_other_datasets')
    if not tags:
        return None, None
    return frozenset(tags), 'MEDIUM' if len(tags) == 1 else 'HIGH'

def canon_f06(v, status=None):
    if status == 'NA':
        return frozenset(['NA']), 'HIGH'
    if not v:
        return None, None
    t = v.lower()
    if _has(t, r'\bkts\b'):
        return frozenset(['algo:kts']), 'HIGH'
    if _has(t, r'equal[\s-]*length', r'fixed[\s-]*length', r'fixed[\s-]*duration'):
        return frozenset(['algo:fixed_length_clips']), 'HIGH'
    if _has(t, r'dataset[\s-]*provided', r'dataset[\s-]*supplied'):
        return frozenset(['algo:dataset_provided_boundaries']), 'HIGH'
    if _has(t, r'k[\s-]*means', r'clustering', r'bundling[\s-]*centre'):
        return frozenset(['algo:clustering']), 'MEDIUM'
    if _has(t, r'histogram', r'edge change ratio', r'hybrid'):
        return frozenset(['algo:hybrid_shot_detector']), 'MEDIUM'
    if _has(t, r'ffprobe'):
        return frozenset(['algo:ffprobe']), 'HIGH'
    if _has(t, r'frame[\s-]*level', r'no shot[\s-]*boundary', r'no occurrence'):
        return frozenset(['NA_implicit_frame_level']), 'MEDIUM'
    return None, None

def canon_f07(v):
    if not v:
        return None, None
    t = v.lower()
    if _has(t, r'knapsack'):
        return frozenset(['mech:knapsack']), 'HIGH'
    if _has(t, r'bernoulli', r'sampled from.{0,10}action'):
        return frozenset(['mech:stochastic_rl_sampling']), 'HIGH'
    if _has(t, r'top[\s-]*k', r'differentiable top'):
        return frozenset(['mech:topk_selection']), 'HIGH'
    if _has(t, r'k[\s-]*means', r'cluster prototype', r'affinity propagation', r'gmm'):
        return frozenset(['mech:clustering_based']), 'MEDIUM'
    if _has(t, r'greedy'):
        return frozenset(['mech:greedy']), 'MEDIUM'
    if _has(t, r'actor selects', r'picking game'):
        return frozenset(['mech:sequential_actor_selection']), 'MEDIUM'
    if _has(t, r'threshold'):
        return frozenset(['mech:thresholding']), 'MEDIUM'
    return None, None

def annotator_count_range(v):
    if not v:
        return None
    nums = [int(x) for x in re.findall(r'\b(\d{1,2})\b', v) if 1 <= int(x) <= 30]
    if not nums:
        return None
    return (min(nums), max(nums))

def canon_f09_annotator_count(v):
    rng = annotator_count_range(v)
    if rng is None:
        return None, None
    return rng, 'MEDIUM'

def canon_f09_construction(v):
    if not v:
        return None, None
    t = v.lower()
    tags = set()
    if _has(t, r'binar', r'top[\s-]*n%'):
        tags.add('method:binarized')
    if _has(t, r'used directly', r'binary human summaries.{0,10}used'):
        tags.add('method:used_directly_no_aggregation')
    if _has(t, r'aggregat', r'unified'):
        tags.add('method:aggregated')
    if _has(t, r'\bmax\b.{0,15}annotator'):
        tags.add('rule:max_over_annotators')
    if _has(t, r'\bmean\b.{0,15}annotator', r'averag.{0,15}annotator'):
        tags.add('rule:mean_over_annotators')
    if not tags:
        return None, None
    return frozenset(tags), 'MEDIUM'

def canon_f11(v):
    if not v:
        return None, None
    t = v.lower()
    unit = None
    if _has(t, r'frame[\s-]*level', r'frame overlap', r'per[\s-]*frame'):
        unit = 'unit:frame'
    elif _has(t, r'shot', r'key[\s-]*fragment', r'keyshot'):
        unit = 'unit:shot_or_keyfragment'
    elif _has(t, r'\bclip\b'):
        unit = 'unit:clip'
    elif _has(t, r'kendall', r'spearman', r'\btau\b', r'\brho\b', r'correlation'):
        unit = 'unit:rank_correlation'
    formula = 'formula:standard_PRF1' if _has(t, r'p\s*=', r'precision', r'2pr', r'harmonic') else None
    tags = {x for x in (unit, formula) if x}
    if not tags:
        return None, None
    return frozenset(tags), 'HIGH' if unit else 'LOW'

def canon_f16(v, status=None):
    if status == 'NR':
        return frozenset(['NR']), 'HIGH'
    if not v:
        return None, None
    t = v.lower()
    if _has(t, r'cited', r'\[\d+\]', r'from \['):
        return frozenset(['provenance:cited_from_other_work']), 'MEDIUM'
    if _has(t, r'repetition', r'repeats', r'\d+\s*runs', r'own run', r'100 rand'):
        return frozenset(['provenance:own_repeated_runs_stated']), 'HIGH'
    if _has(t, r'not stated', r'provenance.{0,10}not'):
        return frozenset(['provenance:unstated']), 'MEDIUM'
    return None, None

def canon_f08(v):
    if not v:
        return None, None
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', v)
    if m:
        return frozenset([f'pct:{float(m.group(1))}']), 'HIGH'
    return None, None

def canon_f04(v):
    if not v:
        return None, None
    t = v.lower()
    tags = set()
    if re.search(r'googlenet|googlenet', t):
        tags.add('arch:googlenet')
    if re.search(r'pool\s*5', t):
        tags.add('layer:pool5')
    if re.search(r'1024[\s-]*d(im)?', t):
        tags.add('dim:1024')
    if re.search(r'imagenet[\s-]*pretrain\w*|pretrain\w*\s*on\s*imagenet', t):
        tags.add('pretrain:imagenet')
    if re.search(r'\bi3d\b', t):
        tags.add('arch:i3d')
    if re.search(r'\bvgg', t):
        tags.add('arch:vgg')
    if re.search(r'\bresnet\b', t):
        tags.add('arch:resnet')
    if re.search(r'\bclip\b', t):
        tags.add('arch:clip')
    if re.search(r's3d', t):
        tags.add('arch:s3d')
    if re.search(r'hand[\s-]*craft', t):
        tags.add('arch:handcrafted')
    return (frozenset(tags) if tags else None), ('HIGH' if tags else None)

# ============================================================================
# F12 (aggregation): v0.3 -- clause-aware, with explicit-not-stated and
# cited-external-rule components
# ============================================================================

_NOT_STATED_RE = r'not stated|\bnr\b|unstated|not reported'
_CITE_RE = r'follows\b|inherited|per \[|\bper\s+\[|\bet al\b|\[[^\]]{1,40}\]|following the same setting'

def canon_f12(v, status=None):
    if status == 'NR':
        return frozenset(['NR']), 'HIGH'
    if not v:
        return None, None

    tags = set()
    for clause in _clauses(v):
        c = clause.lower()
        has_annotator_ctx = _has(c, r'annotator') or _has(c, r'aggregat')
        has_split_ctx = _has(c, r'\bfolds?\b', r'\bsplits?\b')

        # --- annotator-aggregation sub-component ---
        if _has(c, r'annotator'):
            if _has(c, _CITE_RE) and has_annotator_ctx:
                tags.add('annot:cited_external_rule')
            elif _has(c, _NOT_STATED_RE):
                tags.add('annot:explicitly_not_stated')
            elif _has(c, r'\bmax\b'):
                tags.add('annot:max')
            elif _has(c, r'\bmean\b', r'\baverag\w*\b'):
                tags.add('annot:mean')
        elif has_annotator_ctx and _has(c, _CITE_RE):
            # e.g. "F1 multi-reference aggregation per [2] (not stated)" -- no literal
            # "annotator" token, but "aggregat...per [citation]" is the same external-rule
            # pattern applied to a closely related sub-concept (reference/annotator handling).
            tags.add('annot:cited_external_rule')

        if _has(c, r'single.{0,10}(ground.truth|gt)', r'\bmoot\b'):
            tags.add('annot:single_gt_moot')

        # --- split/fold-aggregation sub-component ---
        if has_split_ctx:
            if _has(c, _NOT_STATED_RE):
                tags.add('across:explicitly_not_stated')
            elif _has(c, r'\bmean\b', r'\baverag\w*\b'):
                tags.add('across:mean_over_splits')

    if not tags:
        return None, None
    return frozenset(tags), 'MEDIUM'

# ============================================================================
# F13 (model/checkpoint selection): v0.3 -- adds a separate hyperparameter-
# tuning category, conditional on a determinable tuning-data sub-component
# ============================================================================

_KNOWN_DATASETS = ('tvsum', 'summe', 'ovp', 'youtube', 'cosum', 'vtw', 'wikihow', 'finegym', 'ostd')

def canon_f13(v, status=None):
    if status == 'NA':
        return frozenset(['NA']), 'HIGH'
    if status == 'NR':
        return frozenset(['NR']), 'HIGH'
    if not v:
        return None, None
    t = v.lower()

    # --- existing checkpoint/epoch-selection categories, UNCHANGED, checked first so the
    # new hyperparameter-tuning category can never override an existing determination ---
    if _has(t, r'oracle', r'test set', r'test[\s-]*set criterion'):
        return frozenset(['method:test_set_oracle_selection']), 'HIGH'
    if _has(t, r'validation'):
        return frozenset(['method:validation_set_selection']), 'HIGH'
    if _has(t, r'grid search'):
        return frozenset(['method:grid_search_tuned']), 'MEDIUM'
    if _has(t, r'max epoch', r'fixed.{0,10}epoch', r'last epoch'):
        return frozenset(['method:fixed_epoch_no_selection']), 'MEDIUM'

    # --- new: sensitivity-analysis / parameter-analysis hyperparameter tuning.
    # Conceptually distinct from the four categories above: those answer "which checkpoint
    # or training epoch was reported," this answers "how was a hyperparameter's VALUE chosen"
    # -- a different methodological question the codebook's F13 field also covers. Kept as
    # its own tag family (never merged into method:grid_search_tuned or the epoch tags) per
    # the user's explicit instruction not to conflate hyperparameter choice with checkpoint
    # choice.
    if _has(t, r'sensitivity analys', r'parameter analys'):
        data_tag = None
        if _has(t, r'data (used|for tuning).{0,15}not stated',
                    r'data.{0,10}not stated',
                    r'criterion and data.{0,15}not stated'):
            data_tag = 'tuning_data:explicitly_not_stated'
        else:
            for ds in _KNOWN_DATASETS:
                # require the dataset name to appear in a clause that also signals it is the
                # tuning/selection data (not merely the paper's main eval dataset mentioned
                # elsewhere in a long value) -- scope to clauses containing both.
                for clause in _clauses(v):
                    cl = clause.lower()
                    if ds in cl and _has(cl, r'tun\w*|chosen|selected|sampled'):
                        data_tag = f'tuning_data:named_dataset:{ds}'
                        break
                if data_tag:
                    break
        if data_tag is None:
            # Method phrase recognized, but tuning-data provenance is not determinable from
            # this text (e.g. "chosen by sensitivity analysis on F-score" with no stated data
            # source, or ambiguous language like "evaluation data" that does not establish
            # validation vs. test). Per the user's explicit requirement that such ambiguous
            # language "must remain AMBIGUOUS unless the source explicitly establishes"
            # which data was used, this function returns None entirely rather than emitting
            # a method-only tag that could spuriously tag-match another, differently-vague
            # value under the existing equality-based judgment logic.
            return None, None
        return frozenset(['method:sensitivity_analysis_hyperparameter_tuning', data_tag]), 'MEDIUM'

    return None, None

CANON = {
    'F01': canon_f01, 'F02': canon_f02, 'F03': canon_f03, 'F04': canon_f04, 'F06': canon_f06,
    'F07': canon_f07, 'F08': canon_f08, 'F11': canon_f11, 'F12': canon_f12, 'F13': canon_f13,
    'F16': canon_f16,
}
