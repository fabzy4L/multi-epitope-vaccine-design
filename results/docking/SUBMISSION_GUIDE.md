# HDOCK Submission Guide — v3.1 Vaccine Construct

**Server:** http://hdock.phys.hust.edu.cn/

**Ligand for all submissions:** `inputs/vaccine_v3_rank001.pdb`

---

## Four Submissions

| Run | Receptor file | Target | Scientific question |
|-----|--------------|--------|---------------------|
| 1 | `TLR4_MD2_3FXI.pdb` | TLR4/MD-2 (3FXI) | Does RS09 adjuvant engage the MD-2 pocket? |
| 2 | `HLA_A0201_1HHH.pdb` | HLA-A\*02:01 (1HHH) | Do MHC-I epitopes contact the peptide-binding groove? |
| 3 | `HLA_DR1_1DLH.pdb` | HLA-DR1 (1DLH) | Do MHC-II epitopes reach the alpha-beta cleft? |
| 4 | `IgG2a_Fab_1IGT.pdb` | IgG2a Fab (1IGT) | Is there structural complementarity for humoral response? |

---

## Submission Steps (each run)

1. Go to http://hdock.phys.hust.edu.cn/
2. **Receptor:** upload the receptor PDB from `results/docking/inputs/`
3. **Ligand:** upload `vaccine_v3_rank001.pdb`
4. **Mode:** Protein-Protein docking
5. **Email:** enter your email for results notification
6. Submit — results arrive in ~1–2 hours

---

## Downloading Results

For each run, download:
- `hdock.out` — ranked docking models with scores
- `model_1.pdb` through `model_10.pdb` — top 10 poses
- `Visualization.pdb` — all models combined

Place each run's results in:
```
results/docking/
  run1_TLR4/
  run2_MHC_I/
  run3_MHC_II/
  run4_IgG/
```

Then run: `python src/docking_analysis.py`

---

## Success Criteria

| Target | ΔG threshold | Contact requirement |
|--------|-------------|---------------------|
| TLR4/MD-2 | < −8 kcal/mol | RS09 residues (MPKKKRKV) within 5Å of MD-2 pocket |
| HLA-A\*02:01 | < −8 kcal/mol | RLFRKSNLK or LPFNDGVYF in peptide-binding groove |
| HLA-DR1 | < −8 kcal/mol | QTLLALHRSYLTPGD or INITRFQTLLALHRS near alpha-beta cleft |
| IgG Fab | < −7 kcal/mol | Any surface-exposed epitope region contacting CDRs |
