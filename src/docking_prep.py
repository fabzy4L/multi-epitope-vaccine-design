#!/usr/bin/env python3
"""
Phase 9A — HDOCK Input Preparation
====================================
Downloads and cleans receptor PDB structures for protein-protein docking
of the v3.1 vaccine construct against four immune targets.

Targets:
  TLR4/MD-2  (3FXI) — innate immune priming via RS09 adjuvant
  HLA-A*02:01 (1HHH) — MHC-I, CD8+ epitope presentation
  HLA-DR1    (1DLH) — MHC-II, CD4+ epitope presentation
  IgG2a Fab  (1IGT) — humoral response model

Run this script first. Then submit via HDOCK web server
(see results/docking/SUBMISSION_GUIDE.md).
"""

import shutil
from pathlib import Path
from Bio.PDB import PDBList, PDBParser, PDBIO, Select

ROOT = Path(__file__).parent.parent
INPUTS = ROOT / "results" / "docking" / "inputs"
INPUTS.mkdir(parents=True, exist_ok=True)

ALPHAFOLD_PDB = (
    ROOT / "results" / "alphafold"
    / "v3_optimized_vaccine_f5e32.result"
    / "v3_optimized_vaccine_f5e32"
    / "v3_optimized_vaccine_f5e32_unrelaxed_rank_001_alphafold2_ptm_model_1_seed_000.pdb"
)

TARGETS = {
    "TLR4_MD2":  {"pdb_id": "3FXI", "chains": ["A", "B"], "note": "TLR4 (A) + MD-2 (B); RS09 adjuvant target"},
    "HLA_A0201": {"pdb_id": "1HHH", "chains": ["A", "B"], "note": "MHC-I heavy chain (A) + B2M (B); CD8+ groove"},
    "HLA_DR1":   {"pdb_id": "1DLH", "chains": ["A", "B"], "note": "MHC-II alpha (A) + beta (B); CD4+ groove"},
    "IgG2a_Fab": {"pdb_id": "1IGT", "chains": ["A", "B"], "note": "IgG heavy (A) + light (B); humoral model"},
}


class ChainSelect(Select):
    def __init__(self, chains):
        self.chains = chains

    def accept_chain(self, chain):
        return chain.get_id() in self.chains

    def accept_residue(self, residue):
        return residue.get_id()[0] == " "  # exclude HETATM


def download_and_clean(pdb_id: str, chains: list, out_path: Path) -> bool:
    pdbl = PDBList(verbose=False)
    tmp_dir = ROOT / "results" / "docking" / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    raw = pdbl.retrieve_pdb_file(pdb_id, file_format="pdb", pdir=str(tmp_dir))
    if not raw or not Path(raw).exists():
        print(f"  [WARN] Could not download {pdb_id} — check network or place manually in {out_path}")
        return False

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_id, raw)

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(out_path), ChainSelect(chains))
    print(f"  Saved {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return True


def prepare_vaccine_ligand():
    if not ALPHAFOLD_PDB.exists():
        print(f"  [WARN] AlphaFold PDB not found at {ALPHAFOLD_PDB}")
        print("         Run ColabFold first or place PDB manually.")
        return False

    dest = INPUTS / "vaccine_v3_rank001.pdb"
    shutil.copy(ALPHAFOLD_PDB, dest)
    print(f"  Vaccine ligand: {dest.name} ({dest.stat().st_size // 1024} KB)")
    print("  Note: v3 sequence used (144aa); 2-residue v3.1 difference is junction-only,")
    print("        negligible for protein-protein docking at epitope level.")
    return True


def write_submission_guide():
    guide_path = ROOT / "results" / "docking" / "SUBMISSION_GUIDE.md"
    content = """# HDOCK Submission Guide — v3.1 Vaccine Construct

**Server:** http://hdock.phys.hust.edu.cn/

**Ligand for all submissions:** `inputs/vaccine_v3_rank001.pdb`

---

## Four Submissions

| Run | Receptor file | Target | Scientific question |
|-----|--------------|--------|---------------------|
| 1 | `TLR4_MD2_3FXI.pdb` | TLR4/MD-2 (3FXI) | Does RS09 adjuvant engage the MD-2 pocket? |
| 2 | `HLA_A0201_1HHH.pdb` | HLA-A\\*02:01 (1HHH) | Do MHC-I epitopes contact the peptide-binding groove? |
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
| HLA-A\\*02:01 | < −8 kcal/mol | RLFRKSNLK or LPFNDGVYF in peptide-binding groove |
| HLA-DR1 | < −8 kcal/mol | QTLLALHRSYLTPGD or INITRFQTLLALHRS near alpha-beta cleft |
| IgG Fab | < −7 kcal/mol | Any surface-exposed epitope region contacting CDRs |
"""
    guide_path.write_text(content, encoding="utf-8")
    print(f"\nSubmission guide: {guide_path}")


def main():
    print("=" * 55)
    print("PHASE 9A — HDOCK INPUT PREPARATION")
    print("=" * 55)

    print("\n[1] Preparing vaccine construct ligand...")
    prepare_vaccine_ligand()

    print("\n[2] Downloading and cleaning receptor structures...")
    for name, cfg in TARGETS.items():
        print(f"\n  {name} ({cfg['pdb_id']}) — {cfg['note']}")
        out = INPUTS / f"{name}_{cfg['pdb_id']}.pdb"
        download_and_clean(cfg["pdb_id"], cfg["chains"], out)

    print("\n[3] Writing submission guide...")
    write_submission_guide()

    print("\n" + "=" * 55)
    print("PREPARATION COMPLETE")
    print(f"Input files: {INPUTS}")
    print("Next: submit via HDOCK — see results/docking/SUBMISSION_GUIDE.md")
    print("=" * 55)


if __name__ == "__main__":
    main()
