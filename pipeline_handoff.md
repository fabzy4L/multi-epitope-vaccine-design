# Multi-Epitope Vaccine Pipeline — Handoff Document
# Date: June 1, 2026
# Repo: https://github.com/fabzy4L/multi-epitope-vaccine-design
# Author: Fabian Alvarez-Primo, PhD

---

## PROJECT STATUS: 9 of 9 computational phases complete — bioRxiv ready

### One-line summary
SARS-CoV-2 multi-epitope vaccine construct v3.1 (142aa, single-KK junction).
NetChop Phase 8A confirmed v3 FLAG_04 BLOCKED (max cleavage 0.948 > 0.7).
v3.1 redesign removes trailing KK from double-KK junction; synthesis gate CLEARED.
All remaining tasks are manuscript preparation — no blocking computational work.

---

## WHAT IS COMPLETE

| Phase | What | Key Output |
|-------|------|-----------|
| 1 | Scoring hardened — log IC50, homology penalty | src/scoring.py |
| 2 | Validation tier language | src/validation_tier.py |
| 3 | Decoy benchmark | KS p=6.87e-24, selectivity confirmed |
| 4 | Solubility prescreen | v3/v3.1: HIGH_PI_EXPRESSION_RISK, GRAVY=-0.199/-0.147 |
| 5 | RS09 adjuvant justified | vaccine_constructor.py comment block |
| 6 | AlphaFold run + documented | Mean pLDDT 36.4 — INCONCLUSIVE (MSA n=3, expected) |
| 7A | AlphaFold report + paper language | results/alphafold/structural_validation_report.json |
| 7B/7C | Scorer hardening + design flags | cysteine_penalty(), allele_diversity_penalty(), DesignFlag dataclass |
| 8A | NetChop junction analysis | v3 BLOCKED (max 0.948), v3.1 CLEARED — results/netchop/ |
| 8B | RFdiffusion 16-design ensemble | 5/5 epitopes viable, mean confidence 0.941 |

---

## LEAD CONSTRUCT: v3.1 (synthesis candidate)

```
Construct:        v3_1_single_kk
Sequence length:  142 amino acids
Molecular weight: 15.07 kDa (BioPython ProtParam)
Theoretical pI:   10.13 (HIGH_PI_EXPRESSION_RISK — use HEK293, not E. coli)
GRAVY score:      -0.147 (net hydrophilic)
Instability idx:  42.64 (borderline; same class as v3)
Validation tier:  COMPUTATIONALLY_VERIFIED
Synthesis gate:   CLEARED (no blocking flags)

Junction redesign:
  v3:   ...INITRFQTLLALHRS-KK-GPGPG-KK-LPFNDGVYF... (BLOCKED, max cleavage 0.948)
  v3.1: ...INITRFQTLLALHRS-KK-GPGPG-LPFNDGVYF...    (CLEARED)

Sequence:
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD
GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK
AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
```

---

## KNOWN DESIGN FLAGS ON v3.1

| Flag | Severity | Blocks Synthesis | Summary |
|------|----------|-----------------|---------|
| FLAG_01 | JUSTIFIED | No | VLSFELLHAPATVCG excluded — free Cys13. Cys→Ser fix in v4 |
| FLAG_02 | SCORING_ARTIFACT | No | Both MHC-II epitopes target DRB1*15:01. DRB1*01:01 absent |
| FLAG_03 | UNDOCUMENTED_GAP | No | HLA-A*02:01 (~30% global) not covered. YLQPRTFLL in pool but excluded |
| FLAG_04 | RESOLVED | No (removed) | Double-KK redesigned to single KKGPGPG in v3.1 |

---

## REMAINING TASKS (manuscript only — no new computation required)

1. **Abstract rewrite** — two lines:
   - "3 validated" → "3 computationally designed constructs"
   - Add: "Selectivity confirmed against 1,000 composition-matched decoys (KS p=6.87e-24)"
   - Update lead construct from v3 to v3.1 (142aa, single-KK junction)

2. **RS09 citation** — find one paper using RS09 in viral peptide subunit vaccine context,
   add to README references

3. **Limitations section** — document FLAG_02 (MHC-II redundancy) and FLAG_03 (HLA-A*02:01 absent)

4. **Methods update**:
   - VLSFELLHAPATVCG exclusion rationale (FLAG_01)
   - NetChop analysis result: v3 BLOCKED (max 0.948), v3.1 redesign rationale
   - Expression system note: pI 10.13 → HEK293 recommended over E. coli

5. **Push final commit** — tag as v3.1-submission-ready

---

## RESUMING THIS CONVERSATION

If resuming with Claude Code:
- Share this document
- Run: git status && git log --oneline -10
- All computational work is done — focus is manuscript language

If resuming with Claude (not Claude Code):
- Share this document
- Key context: PhD project, SARS-CoV-2 multi-epitope vaccine, GitHub fabzy4L,
  computational pipeline in Python, targeting bioRxiv preprint
  Lead construct is now v3.1 (not v3)
