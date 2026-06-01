# Multi-Epitope Vaccine Design Pipeline

**Computational immunoinformatics pipeline for SARS-CoV-2 multi-epitope vaccine design**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-bioRxiv--ready-green.svg)]()

**Fabian A. Alvarez-Primo, Ph.D.**

---

## Overview

End-to-end computational pipeline for designing, scoring, and structurally validating multi-epitope peptide vaccine constructs against SARS-CoV-2. The pipeline processes 44,359 MHC binding predictions, applies a statistical scoring framework validated against 1,000 composition-matched decoys (KS p = 6.87 × 10⁻²⁴), and produces constructs with full proteasomal cleavage validation.

**Lead construct: v3.1** — 142 amino acids, RS09 TLR4-agonist adjuvant, single KKGPGPG junction confirmed by NetChop C-term 3.0, synthesis gate cleared.

---

## Key Results

| Metric | Value |
|---|---|
| MHC binding predictions processed | 44,359 |
| Strong binders identified | 74 (0.17% selectivity) |
| Decoy benchmark | KS p = 6.87 × 10⁻²⁴ |
| Best MHC-I epitope | RLFRKSNLK — HLA-A\*03:01, 4.82 nM |
| Best MHC-II epitope (in construct) | QTLLALHRSYLTPGD — HLA-DRB1\*15:01, 9.87 nM |
| AlphaFold mean pLDDT | 36.4 (inconclusive — expected for chimeric construct) |
| RFdiffusion ensemble | 5/5 epitopes viable, mean confidence 0.941 (n=16) |
| Lead construct | v3.1 — 142 aa, 15.1 kDa, pI 10.13, GRAVY −0.147 |

---

## Lead Construct: v3.1

```
>v3_1_single_kk — 142 aa
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD
GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK
AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
```

**Architecture:** `[Signal]-[RS09 adjuvant]-[MHC-II × 2]-[KKGPGPG]-[MHC-I × 4]-[His₆]`

**v3 → v3.1:** An initial construct (v3) contained a KKGPGPGKK double-KK junction (residues 70–78). NetChop C-term 3.0 returned a maximum cleavage probability of 0.948 — above the 0.7 redesign threshold. The trailing KK was removed; v3.1 synthesis gate is cleared.

**Expression note:** pI 10.13 → mammalian expression (HEK293) recommended over *E. coli*.

---

## Pipeline

```
SARS-CoV-2 S1 protein (685 aa)
    ↓
Sliding-window epitope generation (4,274 candidates)
    ↓
IEDB MHC prediction — NetMHCpan-4.1, NetMHCIIpan-4.0 (44,359 predictions)
    ↓
Statistical scoring + decoy benchmark (KS p = 6.87 × 10⁻²⁴)
    ↓
Construct design — RS09 adjuvant, GPGPG/AAY/KK linkers
    ↓
Solubility prescreen (ProtParam — GRAVY, pI, instability)
    ↓
AlphaFold2 structural prediction (ColabFold)
    ↓
RFdiffusion backbone modeling (n=16 ensemble)
    ↓
NetChop proteasomal cleavage validation → v3.1
```

---

## Validation Table

| Property | v1 | v2 | v3 | v3.1 (lead) |
|---|---|---|---|---|
| Length (aa) | 171 | 172 | 144 | **142** |
| MW (kDa) | 15.0 | 15.1 | 15.3 | **15.1** |
| Theoretical pI | 10.33 | 10.12 | 10.22 | **10.13** |
| GRAVY | — | — | −0.199 | **−0.147** |
| Synthesis gate | — | — | BLOCKED | **CLEARED** |

---

## Quick Start

```bash
git clone https://github.com/fabzy4L/multi-epitope-vaccine-design.git
cd multi-epitope-vaccine-design
pip install -r requirements.txt
```

```python
# Scoring
python src/scoring.py

# Solubility prescreen
python src/solubility_prescreen.py

# NetChop junction analysis (requires NetChop CSV — see src/netchop_analysis.py)
python src/netchop_analysis.py

# Decoy benchmark
python src/decoy_benchmark.py
```

```bash
# Unit tests
pytest tests/ -v
```

---

## Repository Structure

```
src/
  scoring.py                # Combined MHC scoring (log IC50, cysteine + allele diversity penalties)
  validation_tier.py        # ConstructMetadata, DesignFlag, synthesis_cleared()
  solubility_prescreen.py   # GRAVY, pI, instability index
  decoy_benchmark.py        # KS test against composition-matched decoys
  netchop_analysis.py       # Proteasomal cleavage analysis (auto-loads CSV)
  rfdiffusion_analysis.py   # RFdiffusion ensemble scoring

results/
  netchop/                  # NetChop report, cleavage map, predictions CSV
  alphafold/                # ColabFold run: 5 PDB models, score JSON, PAE/pLDDT plots
  figures/                  # Visualizations

tests/
  test_scoring.py           # 9 unit tests — all passing
```

---

## Known Design Flags (v3.1)

| Flag | Severity | Blocks Synthesis | Summary |
|---|---|---|---|
| FLAG_01 | JUSTIFIED | No | VLSFELLHAPATVCG excluded — free Cys13, aggregation risk |
| FLAG_02 | SCORING_ARTIFACT | No | Both MHC-II epitopes target DRB1\*15:01 — same-allele redundancy |
| FLAG_03 | UNDOCUMENTED_GAP | No | HLA-A\*02:01 (~30% global) absent; YLQPRTFLL in pool but excluded |
| FLAG_04 | RESOLVED | No | Double-KK junction redesigned → single KKGPGPG in v3.1 |

---

## Article

**[Advancing Vaccine Design: An AI-Powered Approach to Multi-Epitope SARS-CoV-2 Vaccine Development](ARTICLE_Multi_Epitope_Vaccine_Design.md)**

Covers full methodology, validation results, NetChop redesign rationale, limitations (FLAGS 01–03), and RS09 adjuvant citations.

---

## Related Work

- **[sert-s438t-escitalopram](https://github.com/fabzy4L/sert-s438t-escitalopram)** — Computational pharmacology: AutoDock Vina docking of escitalopram against wild-type and S438T mutant hSERT. Companion to a forthcoming transcriptomics review on MDD/SZ/BD. Shares the same methodological theme: computational prediction + honest accounting of static-model limitations.

---

## References

- Kim E, *et al.* (2025). Long-term immunity of a microneedle array patch of SARS-CoV-2 S1 subunit vaccine with RS09 adjuvant. *Vaccines*, 13(1), 86. https://doi.org/10.3390/vaccines13010086
- Negahdaripour M, *et al.* (2017). Structural vaccinology considerations for in silico designing of a multi-epitope vaccine. *Infect. Genet. Evol.*, 58, 96–109. https://doi.org/10.1016/j.meegid.2017.12.008
- Reynisson B, *et al.* (2020). NetMHCpan-4.1 and NetMHCIIpan-4.0. *Nucleic Acids Res.* https://doi.org/10.1093/nar/gkaa379

---

## Citation

```bibtex
@software{alvarez_primo_2026_vaccine,
  author  = {Alvarez-Primo, Fabian},
  title   = {Multi-Epitope Vaccine Design Pipeline: SARS-CoV-2},
  year    = {2026},
  url     = {https://github.com/fabzy4L/multi-epitope-vaccine-design}
}
```

## License

MIT — see [LICENSE](LICENSE)

## Contact

**Fabian Alvarez-Primo, PhD** — fpalvarez23@gmail.com — [@fabzy4L](https://github.com/fabzy4L)
