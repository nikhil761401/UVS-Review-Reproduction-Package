# UVS Protocol Field Codebook v0.8 — AMB01 Amendment

**This is a new, versioned document. It does not overwrite, modify, or supersede `UVS_Codebook_v0.7_FROZEN.md`, which remains on record unchanged and remains the version every historical statistic in Phases 6 through the Master Forensic Audit was computed against.** v0.8 is additive: it carries forward every v0.7 definition and rule verbatim, and adds exactly one new section (7.9) resolving AMB01. No existing v0.7 rule is altered, reworded, or removed.

## Carried forward from v0.7, unchanged

All of Sections 0–7.8 of `UVS_Codebook_v0.7_FROZEN.md` are incorporated into v0.8 by reference, verbatim, with no changes:
- Section 0 (freeze scope), Sections 1–6 (temporal sets, row unit, source hierarchy, statuses, fields, supervision audit).
- Section 7.0–7.8 (universe reconciliation, core dimensions, verdict-to-bucket mapping, Axis A, Axis B, strict-field flags F04/F16, F18 reference-only treatment, S8 supplementary stratification, pairwise-dependence caveat).

**No existing definition, count, or historical result from v0.7 is recalculated, reworded, or silently altered by this amendment.**

## New Section 7.9 — Asymmetric NA/NR comparison (AMB01, resolved at v0.8)

**7.9.1 Scope.** This section resolves the case left unaddressed by Sec.7.2: one side of a pairwise field comparison carries status NA or NR, and the other side carries a genuine reported value (REP or PART).

**7.9.2 Rule — NR vs. a genuine value.** When one side's status is NR (paper applicable and read, value not stated) and the other side's status is REP or PART, the raw verdict is **AMBIGUOUS**, bucketing to **UNASSESSABLE** per the existing Sec.7.2 table. Rationale: NR records a genuine absence of a stated value; there is nothing to compare the reported side against.

**7.9.3 Rule — NA vs. a genuine value (default).** When one side's status is NA (field does not apply to the method) and the other side's status is REP or PART, the raw verdict is **AMBIGUOUS**, bucketing to **UNASSESSABLE**, **unless** Sec.7.9.4 applies for that specific field.

**7.9.4 Field-specific structural exception (conditions for use).** A field-specific exception to 7.9.3 may be defined, for a specific field, only when the Codebook's own definition of that field (Sec.5) explicitly states a structural, comparable meaning for "not applicable" in that field — for example, a field where the Codebook text itself equates NA with a specific, nameable, cross-paper-comparable configuration. **As of this amendment, no field meets this condition** (confirmed by a full re-read of Sec.5's 18 field definitions during Phase 7 — see `AMB01_FORMAL_DECISION_RECORD.md` Sec.5). Accordingly, **Sec.7.9.3's default applies uniformly to all 12 pairwise-comparability fields (F01–F13 minus F05/F10/F14/F15/F17/F18, plus F04/F16) in this version.** A future Codebook version may add a field-specific exception only by amending this section explicitly, with the supporting Sec.5 text cited.

**7.9.5 Rules — symmetric cases, unchanged.** NA vs. NA and NR vs. NR continue to follow Sec.7.2's existing NA-GENUINE (bucket SAME) and NR-GENUINE (bucket UNASSESSABLE) rows, unaltered.

**7.9.6 Semantic non-conflation (binding interpretive rule).** NA and NR SHALL NOT be treated as interchangeable in implementation, analysis, or manuscript text merely because Sec.7.9.2 and Sec.7.9.3 currently produce the same default bucket. Any future field-specific exception under Sec.7.9.4 applies to NA only and never implies an analogous exception for NR, and vice versa.

**7.9.7 Precedence.** This section's rules fire only after: (a) the inheritance-blocked check, (b) the UNA-handling check, (c) the both-sides-same-missing-status check (Sec.7.2's symmetric *-GENUINE rows, including 7.9.5), and (d) the both-sides-different-missing-status check (one side NA, other side NR — outside this section's scope, unchanged from pre-existing AMBIGUOUS treatment) — all of which take precedence over 7.9.2/7.9.3. Only after all of these fail to apply does field-specific canonicalization (Sec.7.1's `CANON[field]` dispatch) ever run; 7.9.2/7.9.3 fire before field-specific canonicalization for every field, consistent with the pre-existing (pre-v0.8) `one_missing` guard's position in the dispatch order.

**7.9.8 Expected raw verdict and bucket (summary table).**

| Left status | Right status | Rule | Raw verdict | Bucket |
|---|---|---|---|---|
| NR | REP or PART | 7.9.2 | AMBIGUOUS | UNASSESSABLE |
| REP or PART | NR | 7.9.2 (orientation-symmetric) | AMBIGUOUS | UNASSESSABLE |
| NA | REP or PART | 7.9.3 (default; no field currently qualifies for 7.9.4) | AMBIGUOUS | UNASSESSABLE |
| REP or PART | NA | 7.9.3 (orientation-symmetric) | AMBIGUOUS | UNASSESSABLE |
| NA | NA | 7.9.5 (= existing Sec.7.2) | NA-GENUINE | SAME |
| NR | NR | 7.9.5 (= existing Sec.7.2) | NR-GENUINE | UNASSESSABLE |

**7.9.9 Examples.** See `AMB01_FORMAL_DECISION_RECORD.md` Sec.6 for worked examples across all 12 fields' representative cases.

**7.9.10 Which existing results may change.** None. Because 7.9.2 was already production behavior since Phase 6, and 7.9.3's default (with no field-specific exception found) produces the identical bucket, **no pair's Axis A, Axis B, or strict-field classification changes under v0.8 relative to the Phase 6.2 technical baseline** — verified empirically in `AMB01_IMPACT_ANALYSIS.csv`, not assumed. What changes is that this previously `SPECIFICATION-UNRESOLVED` case (AMB01) is now explicitly, textually resolved, and the implementation's internal structure now distinguishes NA-driven from NR-driven AMBIGUOUS outcomes (per 7.9.6), closing the specification gap without altering any published statistic.
