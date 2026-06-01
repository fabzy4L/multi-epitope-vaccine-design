# Multi-Epitope Vaccine Pipeline — Handoff Document
# Date: June 1, 2026
# Repo: https://github.com/fabzy4L/multi-epitope-vaccine-design
# Author: Fabian Alvarez-Primo, PhD

---

## PROJECT STATUS: All core computation complete — 3 steps to bioRxiv

### One-line summary
v3.1 (142aa) is the lead construct. All scoring, structural, and safety validation
is complete. Three tasks remain before submission: HDOCK docking (inputs ready),
LImmSim immune simulation (WSL2 installing), and final manuscript pass.

---

## WHAT IS COMPLETE

| Phase | What | Key Output |
|-------|------|-----------|
| 1 | Scoring hardened | src/scoring.py — log IC50, cysteine + allele diversity penalties |
| 2 | Validation tier | src/validation_tier.py — ConstructMetadata, DesignFlag |
| 3 | Decoy benchmark | KS p=6.87e-24 — selectivity confirmed |
| 4 | Solubility prescreen | v3.1: HIGH_PI_EXPRESSION_RISK, GRAVY=-0.147 |
| 5 | RS09 adjuvant | Justified — Kim et al. 2025, Negahdaripour et al. 2017 |
| 6 | AlphaFold | Mean pLDDT 36.4 — INCONCLUSIVE (MSA n=3, expected) |
| 7A | AlphaFold report | results/alphafold/ — 5 PDB models, PAE/pLDDT plots |
| 7B/7C | Scorer hardening | cysteine_penalty(), allele_diversity_penalty(), DesignFlag dataclass |
| 8A | NetChop junction | v3 BLOCKED (max 0.948) → v3.1 redesigned, CLEARED |
| 8B | RFdiffusion ensemble | 5/5 epitopes viable, mean confidence 0.941 (n=16) |
| 9C | VaxiJen + AllerTop | 4/6 epitopes antigenic; NON-ALLERGEN (BCL9L_HUMAN match) |

---

## WHAT IS PENDING (in order)

### 1. HDOCK — protein-protein docking (Phase 9A)
**Status:** Input files ready. Manual web submissions not yet done.

**Do this:**
1. Go to http://hdock.phys.hust.edu.cn/
2. Submit 4 runs using files in `results/docking/inputs/`:
   - Receptor: `TLR4_MD2_3FXI.pdb`   + Ligand: `vaccine_v3_rank001.pdb`
   - Receptor: `HLA_A0201_1HHH.pdb`  + Ligand: `vaccine_v3_rank001.pdb`
   - Receptor: `HLA_DR1_1DLH.pdb`    + Ligand: `vaccine_v3_rank001.pdb`
   - Receptor: `IgG2a_Fab_1IGT.pdb`  + Ligand: `vaccine_v3_rank001.pdb`
3. Download `hdock.out` from each run into:
   `results/docking/run1_TLR4/`, `run2_MHC_I/`, `run3_MHC_II/`, `run4_IgG/`
4. Run: `python src/docking_analysis.py`

Full protocol: `results/docking/SUBMISSION_GUIDE.md`

---

### 2. LImmSim — immune simulation (Phase 9B)
**Status:** WSL2 installing (reboot required). After reboot:

```bash
# In WSL2 terminal (Ubuntu):
git clone https://github.com/jtextor/limmsim
cd limmsim
make
# Then configure and run for v3.1 3-dose schedule
```

**After simulation:** drop output CSV into `results/immune_simulation/cimsim_results.csv`
then run: `python src/immune_simulation.py`

Full guide: `results/immune_simulation/CIMSIM_SUBMISSION_GUIDE.md`

Note: LImmSim is an open-source C++ derivative of C-ImmSim (Celada-Seiden model).
Output format may differ slightly from web C-ImmSim — update immune_simulation.py
parser if column names differ.

---

### 3. Final manuscript pass + bioRxiv submission
**Status:** Pending HDOCK and LImmSim results.

After both analyses complete:
1. Add HDOCK structural docking section to article
2. Add LImmSim immune response section + figure to article
3. Update abstract with docking and immune simulation results
4. Run: `python src/build_html.py`
5. Generate PDF (weasyprint or export from browser print-to-PDF)
6. Tag: `git tag v3.1-bioRxiv-submitted && git push origin --tags`
7. Submit PDF to bioRxiv

---

## LEAD CONSTRUCT: v3.1

```
Construct:        v3_1_single_kk
Sequence (142aa): MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD
                  GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK
                  AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
MW:               15.1 kDa  |  pI: 10.13  |  GRAVY: -0.147
Synthesis gate:   CLEARED
VaxiJen:          0.2592 construct / 4 of 6 epitopes antigenic
AllerTop:         NON-ALLERGEN
```

---

## KEY FLAGS ON v3.1

| Flag | Severity | Blocks | Summary |
|------|----------|--------|---------|
| FLAG_01 | JUSTIFIED | No | VLSFELLHAPATVCG excluded — Cys13 aggregation risk |
| FLAG_02 | SCORING_ARTIFACT | No | Both MHC-II epitopes target DRB1*15:01 |
| FLAG_03 | UNDOCUMENTED_GAP | No | HLA-A*02:01 absent — YLQPRTFLL in pool but excluded |
| FLAG_04 | RESOLVED | No | Double-KK → single KKGPGPG in v3.1 |

---

## RELATED REPOS

| Repo | Status | Relation |
|------|--------|----------|
| fabzy4L/sert-s438t-escitalopram | Live | Computational pharmacology — molecular docking companion |
| Transcriptomics review | Local only (not yet published) | Translational neuroscience — holds until medRxiv |

---

## RESUMING WITH CLAUDE CODE

Tell Claude Code:
- "Pick up from pipeline_handoff.md"
- Run: `git log --oneline -5 && git status`
- Priority: HDOCK submissions → LImmSim setup in WSL2 → manuscript final pass
