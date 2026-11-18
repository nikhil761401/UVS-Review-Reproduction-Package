# AMB01 Formal Decision Record
## Asymmetric NA/NR Mapping — Research-Owner-Approved Interpretation A (Separate NA/NR Semantics)

**Status: APPROVED by the research owner (Phase 7 task specification, 2026-11-16). This record formalizes that approval into an explicit, testable specification. It does not itself amend the frozen v0.7 Codebook — that is done in `CODEBOOK_V0.8_AMB01_AMENDMENT.md`, a new versioned document.**

---

## 1. Original Codebook provisions (v0.7, frozen, unmodified)

Quoted verbatim from `UVS_Codebook_v0.7_FROZEN.md`:

**Sec.4 (Statuses and applicability):**
> REP: value fully stated by the paper (inheritance noted separately).
> PART: stated incompletely or ambiguously (say what is missing).
> NR: paper is applicable and read, value not stated.
> NA: field does not apply to the method (justify).
> UNA: information exists but is not accessible.

**Sec.7.2 (Verdict-to-bucket mapping, frozen):**
> | NR-GENUINE | UNASSESSABLE |
> | NA-GENUINE | SAME (reported separately as a structural-NA count) |

These two rows only fire when **both sides carry the same missing status** (confirmed by direct code reading of `judge_dimension`'s dispatch order: the `{status}-GENUINE` branch requires `status1 == status2`). No Codebook section anywhere addresses one side NA/NR and the other REP/PART.

## 2. The exact gap

Sec.4 defines NA and NR as semantically distinct: NR means "the paper could report this but didn't"; NA means "this field is categorically inapplicable to the method." Despite this explicit semantic distinction, the Codebook's only two rows that reference these statuses (Sec.7.2's NR-GENUINE and NA-GENUINE rows) collapse them into a shared pattern (both-sides-same-status), and neither row — nor any other Codebook text — specifies what happens when one side is NA/NR and the other is a genuine reported value (REP/PART).

## 3. The three previously considered interpretations (Phase 6.1/6.2, unchanged)

- **Interpretation A (uniform):** AMBIGUOUS/UNASSESSABLE for any single-sided NA/NR case, treating NA and NR identically in the asymmetric case. This was production behavior from Phase 6 onward, but was never formally approved and never distinguished NA's semantics from NR's.
- **Interpretation B:** GENUINE/DIFFERENT, treating a missing value as factually different from a reported one.
- **Interpretation C:** SAME-leaning, by analogy to NA-GENUINE's SAME bucket. Assessed as the least defensible in every prior phase.

## 4. The research owner's selected direction: Interpretation A with separate NA/NR semantics

The research owner selected a **refinement of Interpretation A**, not a different interpretation: the *default outcome* for both NA-vs-genuine and NR-vs-genuine remains AMBIGUOUS/UNASSESSABLE, but the *semantic justification* is no longer shared — NA and NR are never to be treated as interchangeable merely because they currently produce the same default outcome. The formal rule, as specified in the Phase 7 task:

1. **NR vs. a genuine value (REP/PART): AMBIGUOUS/UNASSESSABLE.** NR means the paper was read and is applicable but did not state the value — there is genuinely nothing to compare the reported side against.
2. **NA vs. a genuine value (REP/PART): AMBIGUOUS/UNASSESSABLE by default, unless an explicit field-specific structural rule establishes otherwise.** NA means the field does not apply to this method at all — a categorically different kind of "missingness" from NR's. The door is left open, textually, for a field where "inapplicable" has a *structural*, Codebook-supportable comparable meaning (for example, if a field's Codebook definition itself implied that "not applicable" corresponds to a specific, nameable structural state comparable across methods) — but no such rule may be invented by this audit.
3. **NA vs. NA: preserve the existing approved mapping** (Sec.7.2's NA-GENUINE → SAME, reported separately as a structural-NA count). Unchanged.
4. **NR vs. NR: preserve the existing approved mapping** (Sec.7.2's NR-GENUINE → UNASSESSABLE). Unchanged.
5. **NA and NR are not to be assumed semantically identical** merely because rules 1 and 2 currently produce the same default bucket (UNASSESSABLE/AMBIGUOUS) for the asymmetric case.

## 5. Field-specific structural exception: searched for, none found

Per the Phase 7 task's explicit instruction ("Do not invent field-specific structural rules. If no such rule is explicitly supported, use the default AMBIGUOUS/UNASSESSABLE treatment"), all 18 extraction-field definitions in Codebook Sec.5 and the full Sec.7 pairwise framework were re-read specifically looking for any field where "NA" (field does not apply) carries an explicit, Codebook-stated structural meaning that would make an NA-vs-genuine comparison safely resolvable (e.g., a field where the Codebook itself defines what "not applicable" structurally implies for comparison purposes).

**Finding: no such field-specific exception is explicitly supported by the current Codebook text, for any of the 10 core fields or the 2 strict fields.** Each field's NA justification is idiosyncratic prose ("justify" per Sec.4) with no cross-field structural pattern the Codebook formalizes. Consequently, **every one of the 12 fields uses the default AMBIGUOUS/UNASSESSABLE treatment for NA-vs-genuine in this release.** This is recorded as a finding, not assumed — see `AMB01_MAPPING_SPECIFICATION.csv`'s `requires_field_specific_evidence` column, which is `NO (default applies)` for all 12 fields' NA-vs-genuine rows.

## 6. Explicit examples

| Left | Right | Field | Rule | Expected verdict |
|---|---|---|---|---|
| NR, no value | REP, "contrastive training" | F03 | Rule 1 | AMBIGUOUS |
| NA, "method has no training regime" | PART, "20 annotators" | F09 | Rule 2 (default, no exception found) | AMBIGUOUS |
| NA, "n/a" | NA, "not applicable to this method" | F03 | Rule 3 (unchanged) | NA-GENUINE (bucket SAME) |
| NR, no value | NR, no value | F06 | Rule 4 (unchanged) | NR-GENUINE (bucket UNASSESSABLE) |
| NA, "..." | NR, no value | F16 | Both-sides-different-missing-status (outside AMB01's scope — pre-existing, unchanged Codebook-silent case, still AMBIGUOUS per the existing mixed-missingness guard) | AMBIGUOUS |

## 7. Consequences for Axis A and Axis B

Because rule 1 (NR) was already the production default since Phase 6, and rule 2 (NA) with no field-specific exception found also reduces to the same AMBIGUOUS/UNASSESSABLE default, **this release's numerical outcome is identical to the Phase 6.2 technical baseline** — confirmed empirically, not assumed, in `AMB01_IMPACT_ANALYSIS.csv`. What changes is not the bucket assignment but (a) the Codebook now explicitly states and justifies this rule (closing AMB01 as a specification gap), (b) the implementation now tracks NA-vs-genuine and NR-vs-genuine through semantically distinct code paths rather than one merged `one_missing` guard, so a future field-specific NA exception can be added without re-deriving the whole guard, and (c) a defect class is closed: the old merged guard could not have treated NA and NR differently even if a future field justified it; the new implementation can.

## 8. Consequences for strict-field statistics

F04 and F16 (the two strict fields) are subject to the same rule set as the 10 core fields. No field-specific NA exception was found for either, so strict-field statistics are also confirmed unchanged from the Phase 6.2 baseline in `AMB01_IMPACT_ANALYSIS.csv`.

## 9. Remaining limitations

- This decision resolves the *default* case. It explicitly leaves open the possibility of a future, Codebook-text-supported field-specific NA exception — none exists today, and none is invented here.
- The semantic separation of NA and NR (rule 5) is a specification and implementation change, not a statistical one in this release; its value is in preventing a future silent conflation of the two statuses, not in changing today's numbers.
- This record does not address the Sec.7.2 "reported separately as a structural-NA count" promise for NA-GENUINE, which remains a separate, previously-identified documentation gap (AMB03 in the Master Forensic Audit) outside this phase's scope.
