# UVS Review — v0.6 Prospective Reproduction Package

This package lets a reviewer independently reproduce the headline statistics reported in
the manuscript's Quantitative Audit of Experimental-Protocol Comparability (Section VI),
and the frozen-asset correction described in Section III-D / Table V.

## Contents

- `codebook/` — the frozen classification rulebook: `UVS_Codebook_v0.7_FROZEN.md` (base
  rules R01-R18) plus `CODEBOOK_V0.8_AMB01_AMENDMENT.md` and
  `AMB01_FORMAL_DECISION_RECORD.md` (the Phase-7 amendment formalizing the one-sided
  NA/NR ambiguity-handling rule used by v0.6, Sec. 7.9).
- `run/UVS_Core_v1.0_Extraction.csv` — the frozen per-field extraction data (7,501 rows,
  one row per study/setting/dataset/field), the raw input to pair generation.
- `run/UVS_X3_Protocol_Setting_Mapping_v0.2.csv` — study/setting-to-protocol mapping used
  by the pair-generation step.
- `run/scripts/x3_canon_v0.3.py`, `run/scripts/x3_build_units_v0.3.py` — the
  pair-generation procedure: canonicalizes each field's raw value and assembles the
  eligible cross-study pairs from the extraction data.
- `tools/v05_classify_ORIGINAL_VERIFIED.py` — the classification engine
  (`judge_dimension()` et al.) that assigns a per-field verdict to each pair; see
  `V0.6_METHODOLOGICAL_CLARIFICATION.md` for the exact, SHA-256-verified defect this
  review found in its one-sided NA/NR handling and the v0.6 rule adopted to fix it.
- `tools/axis_ab_calculator.py`, `run/x3_full_analysis_v0.6_prospective.py` — the
  analysis scripts that turn per-pair, per-field verdicts into the Axis A
  (evidence-completeness) and Axis B (protocol-relationship) summary statistics reported
  in Tables III and IV.
- `outputs/x3_v0.6_prospective_pairs.json` — the full, ground-truth generated-pairs file
  (17,973 JSON objects, one per pair, with per-field verdicts) that is the authoritative
  source for every pairwise-universe and Axis A/B statistic in the manuscript.
- `outputs/x3_v0.6_prospective_summary.json` — the aggregated summary statistics computed
  from the pairs file.
- `V0.6_CHANGE_REGISTER.csv` — the per-cell audit trail underlying Table V: one row per
  affected (pair, field) combination (8,406 rows), recording the pre- and post-correction
  verdict and whether the change is confirmed-agreed or (for 464 F09-only cells)
  unresolved between this review's v0.6 re-analysis and an independent Phase 6.2
  cross-check.
- `V0.6_AUDIT_REPORT.md`, `V0.6_PROSPECTIVE_SUMMARY.md`, `V0.6_AXIS_STATS_RAW.txt`,
  `V0.6_METHODOLOGICAL_CLARIFICATION.md` — narrative documentation of the defect found,
  the fix adopted, and the resulting statistics, cross-referencing the SHA-256 hash of
  the unmodified original engine function so the defect claim itself is checkable against
  the code rather than taken on this review's word.
- `SHA256_MANIFEST.csv` — a SHA-256 hash of every file in this package plus two external
  reference hashes (the pre-fix v0.5 baseline and the Phase 6.2 figures superseded by
  this analysis), so a reviewer can confirm these are exactly the frozen files this
  review used, bit-for-bit, and not a reconstruction after the fact.

## How to verify

1. Check file integrity: `sha256sum -c SHA256_MANIFEST.csv` (strip the two
   external-reference rows first, or check them separately against the paper's citation).
2. Re-run pair generation: `python3 run/scripts/x3_build_units_v0.3.py` (consumes
   `run/UVS_Core_v1.0_Extraction.csv` and `run/UVS_X3_Protocol_Setting_Mapping_v0.2.csv`;
   see the script's own header for its exact CLI).
3. Re-run classification and aggregation:
   `python3 run/x3_full_analysis_v0.6_prospective.py`, which applies
   `tools/v05_classify_ORIGINAL_VERIFIED.py` plus the v0.6 one-sided NA/NR rule
   documented in `V0.6_METHODOLOGICAL_CLARIFICATION.md`, and should reproduce
   `outputs/x3_v0.6_prospective_pairs.json` and `outputs/x3_v0.6_prospective_summary.json`
   byte-for-byte (verify against `SHA256_MANIFEST.csv`).
4. Cross-check headline figures directly against `outputs/x3_v0.6_prospective_pairs.json`
   without re-running anything: 17,973 JSON objects; 141 unique (study,setting) pairs;
   271 unique (study,setting,dataset) triples; 69 unique studies — see the manuscript's
   Section VI-B and Fig. 1 for how these relate.

This package is the frozen research-asset basis for the manuscript; no file here was
altered to produce the manuscript text. New, manuscript-specific derived material
(figures, final tables, the reconciled reference list) is not part of this package, since
those are reproducible from the frozen assets above rather than being frozen assets
themselves.

## License

This repository uses split licensing:

- **Code** (`run/scripts/`, `run/x3_full_analysis_v0.6_prospective.py`, `tools/`) is
  licensed under the **MIT License** — see [`LICENSE-CODE.txt`](LICENSE-CODE.txt).
- **Documentation, codebooks, extraction metadata, and derived audit materials**
  (`codebook/`, the `V0.6_*` narrative/audit documents, `V0.6_CHANGE_REGISTER.csv`,
  `SHA256_MANIFEST.csv`, the extraction/mapping CSVs, and the pairs/summary JSON
  outputs) are licensed under **Creative Commons Attribution 4.0 International
  (CC BY 4.0)** — see [`LICENSE-DOCS.txt`](LICENSE-DOCS.txt).

### Third-party material

This repository does **not** redistribute any third-party papers, datasets, or other
copyrighted content. `run/UVS_Core_v1.0_Extraction.csv`,
`run/UVS_X3_Protocol_Setting_Mapping_v0.2.csv`, and the derived pairs/summary JSON
contain only this review's own **extracted metadata and classification verdicts**
about the 69 published studies surveyed (e.g., which protocol fields were reported,
how two studies' settings compare) — not the papers' text, figures, datasets, or any
other original content from them. Each source paper is identified only by its own
public bibliographic citation (as listed in the manuscript's reference list), which is
how the original, copyrighted works themselves should be obtained and cited. The CC
BY 4.0 license above covers this review's own metadata and documentation; it does not
purport to relicense, and has no effect on, the copyright of any third-party paper or
dataset referenced.
