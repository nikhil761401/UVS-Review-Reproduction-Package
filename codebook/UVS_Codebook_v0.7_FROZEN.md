# UVS Codebook v0.7 — FROZEN (Narrow Core Methodology Freeze)

**Status: FROZEN, within the explicit scope defined in Section 0 below.** Adopted from
`UVS_Codebook_v0.7_PROPOSED.md` (Stage M) under owner authorization recorded in Stage O's task
specification, dated **2026-11-14** (the actual execution date of this freeze — not an invented
date). This document is a new, standalone file. It does not overwrite
`UVS_Codebook_v0.7_PROPOSED.md`, which remains on record unchanged as the pre-freeze candidate, and
it does not modify `UVS_Codebook_v0.6.md`, which remains the frozen extraction-stage document.

Full freeze provenance, SHA-256 hashes, and the explicit owner-authorization record are in
`Stage_O_Methodology_Freeze_Manifest.md`. This document carries forward the approved v0.7
definitions verbatim where the owner approved them as-is, and verbatim plus a scope note where the
owner approved them with the modular scope clarification. **No definition, count, or historical
result below has been recalculated, reworded, or silently altered from the version the owner
approved.**

---

## Section 0 — Freeze scope and supplementary-layer scope note

**FROZEN (primary methodology, owner-authorized, binding):**

1. The two-axis framework (Axis A — evidence completeness; Axis B — protocol relationship among
   assessable dimensions).
2. The ten core protocol fields (F01, F02, F03, F06, F07, F08, F09, F11, F12, F13).
3. The approved verdict-to-bucket mapping (Section 7.2 below).
4. F04 (feature-representation) strict flag.
5. F16 (random-baseline-provenance) strict flag.
6. F18 (result formation) as a reference-only field, explicitly excluded from the core/strict
   pairwise framework.
7. Pairwise descriptive reporting and the pairwise-dependence caveat (Section 7.8).
8. The original eligibility universe: 271 eligible units, 69 underlying studies, 17,973
   cross-paper pairs.

**The primary Axis A and Axis B classifications for all 17,973 pairs are unchanged from Stage G's
original computation (independently re-verified by Stage H with zero discrepancies, and
hash-confirmed unchanged at every subsequent stage including this one).**

**SUPPLEMENTARY (approved for supplementary analysis only — NOT part of the frozen primary
methodology):**

- S8 supervision stratification (the six-category pair-level `supervision_relationship` variable)
  and the `strict_supervision_discordant` candidate flag (scoped to the 248 CONFIRMED E136 pairs).
- These are **explicitly NOT additional Axis A or Axis B fields.** They do **not** change, qualify,
  override, or get merged into any primary pairwise classification (Axis A, Axis B, F04, or F16).
  They exist as a separate analytical layer, joined to the pair universe for reference only
  (`Stage_L_Pair_Level_Supervision_Mapping.csv`, keyed by `pair_index`).
- Both original per-side S8 labels (`s8_label_1`, `s8_label_2`) are retained for every pair,
  alongside the derived `supervision_relationship` category — never collapsed to the derived
  category alone. This is confirmed in the actual mapping file's column structure (verified in this
  stage; see `Stage_O_Input_Inventory.csv`).
- The corrected Stage L figures are reported here with their precise denominators (Section 7.7):
  experimental-unit S8 coverage 137/141 = 97.16%; pair-level S8 coverage 15,275/17,973 = 84.99%;
  E136-associated pairs reviewed = 269; confirmed discordance = 248; comparison-side unresolved
  (UNASSESSABLE) = 13; comparison-side record absent (NO_RECORD) = 8.
- **This document does not imply, and no downstream use of it may imply, that every pair involving
  E136 has confirmed discordance.** Only 248 of the 269 E136-touching pairs carry the confirmed
  discordance characterization; the other 21 (13 + 8) are explicitly unresolved for a different,
  separately-documented reason (the comparison side's own supervision status is itself not cleanly
  resolved) and must never be folded into the 248 figure or described as discordant.

**DEFERRED (explicitly not blocking this freeze, per owner authorization):**

- OWN-M05 (S5 exclusion from the stratification), OWN-M06 (whether/when to build a merged
  production file carrying the supplementary fields), and OWN-M07 (whether/when to run the two
  pending integration-test assertions) remain open, future-research/engineering-scheduling
  decisions. None of them changes, qualifies, or is required to resolve before this freeze. They
  do not reopen or narrow the frozen scope in Section 0 above, and resolving them in the future
  (in either direction) cannot retroactively alter anything declared frozen here.

**Historical correction trail (superseded values, retained for the record, never used going
forward):** Stage K's originally-reported 80.92% pair-level S8 coverage and 242-pair E136 count are
superseded by the Stage L / Stage M / Stage N / Stage O corrected figures above. They remain
recorded, labeled SUPERSEDED, in `Stage_M_Historical_Correction_Register.csv`, which this document
does not alter.

---

## Change log v0.6 → v0.7 (carried forward from the proposed document, unchanged)

1. Section 5: F18 explicitly marked reference-only, with its evidentiary basis (Stage K, Stage L §7).
2. Section 6: S8 audited-consistency categories confirmed and formally cross-referenced to the new
   pairwise supervision stratification in Section 7 (Stage L).
3. Section 7 rewritten in full: two-axis comparability framework (Axis A, Axis B), verdict-to-bucket
   mapping, strict-field flags (F04, F16) as independent reports, F18 reference-field treatment,
   S8-based supervision stratification plus a narrow discordance flag, universe reconciliation
   (271 eligible units / 69 studies / 17,973 pairs), and the pairwise-dependence caveat.
4. No change to Sections 1–4 (temporal sets, row unit, source hierarchy, statuses/applicability).
5. **(New at freeze, Stage O)** Section 0 above: explicit freeze scope, supplementary-layer scope
   note, and deferred-decision list, per owner authorization.

---

## 1. Temporal sets and sampling frames
*(unchanged from v0.6 and from the proposed v0.7)*
- Main review window: verified year 2014–2026. Analytical subset 2017–2026 is NESTED in Main (never added to it).
- Strata for tables: A pre-2014 contextual foundation set (separately identified, not in Main); B 2014–2016; C 2017–2026; D year unconfirmed (e.g. P076; P004 until verified).
- Year-unconfirmed records are extracted but excluded from every time-stratified analysis and pilot sampling.
- Primary sampling frame: Core, distinct canonical studies (89). Boundary studies are extracted later, analysed separately, never pooled with Core without a stated reason.
- Counts are classification counts, never PRISMA counts. Units (records, PDFs, publications, studies, methods, experiments, datasets) are never interchanged.

## 2. Row unit and canonical IDs
*(unchanged)*
One row per publication × experimental setting × dataset × field. Study ID = canonical ID (duplicates P063, P046, P017, P071, P038 are not extracted). Setting examples: unsupervised main, supervised variant (never merged), canonical/augmented/transfer split, ablation (extract only if it changes a protocol field).

## 3. Source hierarchy and evidence standard
*(unchanged)*
1. Main text, tables, figures and appendix of the paper's own PDF.
2. Statements that the paper explicitly inherits from cited work ("following [X]"): record with inheritance = INHERITED and keep the cited-work value out unless that work is also in the corpus and read.
3. Nothing else. Never infer from other papers, from code repositories not read, or from author reputation.

## 4. Statuses and applicability
*(unchanged)*
- REP: value fully stated by the paper (inheritance noted separately).
- PART: stated incompletely or ambiguously (say what is missing).
- NR: paper is applicable and read, value not stated.
- NA: field does not apply to the method (justify).
- UNA: information exists but is not accessible (e.g. supplementary file not supplied, unreadable PDF page).

## 5. Fields (extract each per setting × dataset unless marked paper-level)

F01 dataset and version; F02 evaluation split; F03 training/validation regime; **F04 feature extractor and pretraining source — STRICT, see §7.5 (FROZEN)**; F05 frame sampling rate; F06 shot segmentation; F07 summary-selection procedure; F08 summary-length budget; F09 reference-summary construction; F10 metrics reported; F11 metric implementation; F12 aggregation; F13 checkpoint/model selection; F14 seeds and number of runs; F15 variability reported; **F16 random baseline — STRICT, see §7.5 (FROZEN)**; F17 code and configuration availability; **F18 headline result and formation — REFERENCE-ONLY, see §7.6 (FROZEN as reference-only; excluded from the pairwise framework on evidentiary grounds, not discarded).**

## 6. Supervision audit (paper-level, one row per setting)

S1 human task-specific labels used in training; S2 human labels used for validation/model selection; S3 pseudo-labels; S4 external model-generated targets; S5 backbone pretraining (recorded here; its exclusion from the supplementary stratification is a DEFERRED decision per Section 0 — the exclusion itself is already in effect and non-controversial, only the question of ever extending it remains open); S6 external inference inputs; S7 author-claimed paradigm (verbatim, page); **S8 audited consistency: CONSISTENT / CONSISTENT-WITH-QUALIFICATION / DISCORDANT / UNASSESSABLE**.

**S8 is the source for the SUPPLEMENTARY pairwise supervision stratification defined in §7.7. This stratification is not part of the frozen primary methodology (Section 0).**

---

## 7. X3 pairwise comparability framework (FROZEN, except where marked SUPPLEMENTARY)

### 7.0 Universe reconciliation (FROZEN)

**17,973 eligible pairs**, drawn from **271 eligible experimental units** across **69 underlying
studies**. Independently re-verified by Stage H; re-confirmed unchanged at every subsequent stage
through Stage O, by SHA256 hash of the pair-universe file, not by assumption.

- **271 eligible units**: every (study, setting) meeting the unsupervised-eligibility criterion.
- **141 pairwise units**: the subset of the 271 actually referenced by ≥1 of the 17,973 pairs.

**Denominator rule**: every percentage in this section is computed over the full 17,973-pair
universe unless explicitly stated otherwise.

### 7.1 Core comparability dimensions (10) (FROZEN)

F01, F02, F03, F06, F07, F08, F09, F11, F12, F13. F04, F16 excluded (§7.5, FROZEN separately). F18
excluded (§7.6, FROZEN as reference-only).

### 7.2 Verdict-to-bucket mapping (FROZEN)

| Raw verdict | Bucket |
|---|---|
| WORDING-ONLY | SAME |
| GENUINE | DIFFERENT |
| NR-GENUINE | UNASSESSABLE |
| UNA-GENUINE | UNASSESSABLE |
| NA-GENUINE | SAME (reported separately as a structural-NA count) |
| AMBIGUOUS | UNASSESSABLE |
| MISSING-BY-CONSTRUCTION | UNASSESSABLE |
| INHERITANCE-BLOCKED | UNASSESSABLE |

A project-owner ruling (first made for v0.4), re-verified unchanged through Stage I and now frozen.

### 7.3 Axis A — Evidence completeness (FROZEN)

- **Fully Assessable**: zero core dimensions UNASSESSABLE.
- **Partially Assessable**: at least one UNASSESSABLE and at least one not.
- **Insufficient Evidence**: all ten UNASSESSABLE.

**Frozen, owner-approved results (OWN-M01/OWN-M03):**

| Category | Count | % |
|---|---:|---:|
| Fully Assessable | 0 | 0.0000% |
| Partially Assessable | 16,624 | 92.4917% |
| Insufficient Evidence | 1,349 | 7.5057% |

### 7.4 Axis B — Protocol relationship among assessable dimensions (FROZEN, terminology per OWN-M02)

- **Same among assessable dimensions**: `core_diff == 0 and core_same > 0`.
- **Mixed among assessable dimensions**: `core_same > 0 and core_diff > 0`.
- **Different among assessable dimensions**: `core_same == 0 and core_diff > 0`.
- **Undetermined**: `core_same == 0 and core_diff == 0`.

**Required manuscript caveat (frozen requirement, unchanged from the proposed v0.7)**: any report
using these labels SHALL state, at first use: *"'Same among assessable dimensions' indicates that
every core protocol dimension for which a judgment could be made agreed; it does not indicate that
the two protocols were shown to be fully equivalent, and carries no claim about dimensions that
could not be assessed. The companion Axis A value indicates how many of the ten core dimensions
were actually assessable for a given pair."* An analogous statement applies to "Different among
assessable dimensions."

**Frozen, owner-approved results (OWN-M01/OWN-M02/OWN-M03):**

| Category | Count | % |
|---|---:|---:|
| Same among assessable dimensions | 3,915 | 21.7827% |
| Mixed among assessable dimensions | 10,783 | 59.9955% |
| Different among assessable dimensions | 1,926 | 10.7161% |
| Undetermined | 1,349 | 7.5057% |

**Axis A × Axis B cross-tabulation (frozen):**

| | Same | Mixed | Different | Undetermined | Row total |
|---|---:|---:|---:|---:|---:|
| **Fully Assessable** | 0 | 0 | 0 | 0 | 0 |
| **Partially Assessable** | 3,915 | 10,783 | 1,926 | 0 | 16,624 |
| **Insufficient Evidence** | 0 | 0 | 0 | 1,349 | 1,349 |
| **Column total** | 3,915 | 10,783 | 1,926 | 1,349 | **17,973** |

The two axes SHALL NOT be collapsed into a single pair-level label for any manuscript-facing
presentation.

### 7.5 Strict-field flags F04, F16 (FROZEN)

Reported independently, never combined, never automatically folded into Axis A or Axis B.

- `strict_incompatible` (at least one strict field DIFFERENT): 4,391 pairs (24.43%).
- `strict_unresolved` (at least one strict field UNASSESSABLE): 16,883 pairs (93.9353%, explicitly
  "at least one," distinct from "both unresolved" = 12,254 pairs / 68.1800%).

**Frozen F04 × F16 joint table:**

| F04 \ F16 | SAME | DIFFERENT | UNASSESSABLE | Row total |
|---|---:|---:|---:|---:|
| **SAME** | 9 | 435 | 1,313 | 1,757 |
| **DIFFERENT** | 10 | 636 | 1,947 | 2,593 |
| **UNASSESSABLE** | 6 | 1,363 | 12,254 | 13,623 |
| **Column total** | 25 | 2,434 | 15,514 | **17,973** |

A confirmed strict-field difference does not automatically invalidate a comparison; whether a given
mismatch is consequential is a judgment left to the analyst using the flag, never automated.

### 7.6 F18 — result formation (FROZEN as reference-only)

F18 is extracted in full (458 records) but excluded from CORE_FIELDS and STRICT_FIELDS: 89.5% bare
numeric values; only 0.86% of pairs have formation-method language on both sides; demonstrated
overlap with F12/F13. Retained for descriptive transparency, never promoted to a pairwise
comparability dimension.

### 7.7 S8 supervision stratification and the E136 discordance flag (SUPPLEMENTARY — NOT part of the frozen primary methodology)

**This entire section is supplementary, per Section 0 above.** It is reported here, alongside the
frozen primary sections, for completeness and traceability — never as an additional Axis A/B field
and never as something that alters any count in §7.3–7.5.

**Preserved taxonomy**: CONSISTENT, CONSISTENT-WITH-QUALIFICATION, UNASSESSABLE, DISCORDANT — used
as-is, no fifth category, no forced binary collapse.

**Join key**: `(study_id, setting)`, never `study_id` alone. Zero duplicate keys among 232 S8
source rows.

**Primary representation**: both original per-side S8 labels are retained for every pair, plus a
derived six-value relationship variable (`SUPERVISION_CONSISTENT`,
`SUPERVISION_CONSISTENT_WITH_QUALIFICATION_BOTH`, `SUPERVISION_CONSISTENT_MIXED_QUALIFICATION`,
`SUPERVISION_DIFFERENT_ONE_DISCORDANT`, `SUPERVISION_DIFFERENT_BOTH_DISCORDANT` [0 occurrences],
`UNRESOLVED_UNASSESSABLE`, `UNRESOLVED_NO_RECORD`).

**Owner-approved supplementary figures, with precise denominators (OWN-M03, OWN-M04):**

| Metric | Value | Denominator |
|---|---:|---|
| Experimental-unit S8 coverage | 137 / 141 = **97.16%** | of 141 pairwise units |
| Pair-level both-sides-resolved coverage | 15,275 / 17,973 = **84.99%** | of 17,973 pairs |
| E136-associated pairs reviewed (total touching the single DISCORDANT unit) | **269** | — |
| — Confirmed discordance (comparison side cleanly resolved) | **248** | of the 269 |
| — Comparison-side unresolved (UNASSESSABLE) | **13** | of the 269 |
| — Comparison-side record absent (NO_RECORD) | **8** | of the 269 |

248 + 13 + 8 = 269. **Approved as a supplementary supervision flag only** (OWN-M04): the 248-pair
`strict_supervision_discordant` candidate flag is retained, with the 13 and 8 kept separately
identified and never merged into the 248 or described as confirmed-discordant.

**Not every pair involving E136 has confirmed discordance** — only 248 of 269. Any report using
this flag must state this explicitly.

S5 exclusion from this stratification (OWN-M05) is deferred (Section 0); the stratification as
currently defined already excludes S5, and that current state is unaffected either way.

**This flag is not yet wired into the production `x3_v0.5_two_axis_pairs.json` pair records**, and
building that integration (OWN-M06) and its associated tests (OWN-M07) remain deferred, non-blocking
decisions (Section 0).

### 7.8 Pairwise dependence and appropriate descriptive interpretation (FROZEN)

69 unique studies, 271 eligible units, 17,973 pairs; not independent observations (top study,
E065/E108 tied, 1,554 pairs / 8.6463%). Ordinary binomial confidence intervals, standard errors,
chi-square tests, and non-clustered regression are inappropriate without a study-level clustering
adjustment; none is used anywhere in this framework. Every percentage is a descriptive,
finite-corpus summary, never an estimate of a population parameter.

---

## What this document does

- It formally freezes, under explicit owner authorization dated 2026-11-14, the eight primary
  methodology items listed in Section 0.
- It approves the supplementary S8/E136 supervision layer for supplementary analysis only, with
  explicit, binding constraints on how it may and may not be used or described.
- It defers OWN-M05/M06/M07 without allowing them to block or narrow this freeze.

## What this document does not do

- It does not modify `UVS_Codebook_v0.6.md` or `UVS_Codebook_v0.7_PROPOSED.md`.
- It does not recalculate, reword, or alter any historical pair classification, Axis A/B value, or
  F04/F16 status.
- It does not wire the S8 stratification or the E136 flag into the production pair-level JSON file.
- It does not authorize manuscript drafting; it establishes the frozen specification that future
  manuscript drafting must cite.
