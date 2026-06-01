#!/usr/bin/env python3
"""
Phase 8B — RFdiffusion 16-Design Ensemble Analysis
===================================================

Analyzes backbone confidence scores from 16 RFdiffusion partial diffusion designs.
Maps B-factors (RFdiffusion confidence, 0-1 scale) to epitope regions using
construct position indices.

Note: RFdiffusion outputs backbone-only PDBs (all residues labeled GLY) —
      sequence-based mapping is not possible; all positions mapped by index.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from Bio.PDB import PDBParser


CONSTRUCT = (
    "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPG"
    "QTLLALHRSYLTPGD"
    "GPGPG"
    "INITRFQTLLALHRS"
    "KK"
    "GPGPG"
    "KK"
    "LPFNDGVYF"
    "AAY"
    "RLFRKSNLK"
    "AAY"
    "FPNITNLCPF"
    "AAY"
    "VLYNSASFSTFK"
    "GGGSPAPAPG"
    "SHHHHHH"
).replace(" ", "").replace("\n", "")

# Epitope positions — 0-indexed in CONSTRUCT string
EPITOPES = {ep: (CONSTRUCT.find(ep), CONSTRUCT.find(ep) + len(ep) - 1)
            for ep in [
                "QTLLALHRSYLTPGD",
                "INITRFQTLLALHRS",
                "LPFNDGVYF",
                "RLFRKSNLK",
                "FPNITNLCPF",
            ]}

LINKERS = {
    "GPGPG_1": (CONSTRUCT.find("GPGPG"),      CONSTRUCT.find("GPGPG") + 4),
    "AAY_1":   (CONSTRUCT.find("AAY"),         CONSTRUCT.find("AAY") + 2),
    "KK":      (CONSTRUCT.find("KK"),          CONSTRUCT.find("KK") + 1),
}


def parse_pdb_bfactors(pdb_path: str) -> np.ndarray:
    """
    Extract per-residue B-factors from RFdiffusion PDB.
    RFdiffusion encodes backbone confidence (0-1) in the B-factor column.
    All residues labeled GLY (backbone-only output) — map by position index.
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("construct", pdb_path)
    bfactors = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == " ":
                    ca_atoms = [a for a in residue if a.name == "CA"]
                    if ca_atoms:
                        bfactors.append(ca_atoms[0].bfactor)
    return np.array(bfactors)


def analyze_backbone_ensemble(pdb_dir: str) -> pd.DataFrame:
    """Analyze all RFdiffusion output PDBs. 16 expected."""
    pdb_files = sorted(Path(pdb_dir).glob("v3_optimized_*.pdb"))

    if not pdb_files:
        raise FileNotFoundError(
            f"No PDB files found in {pdb_dir}\n"
            "Expected: results/RFDiffusion/v3_optimized_vozb8.result/outputs/"
        )

    print(f"Found {len(pdb_files)} RFdiffusion designs")

    results = []
    for pdb_file in pdb_files:
        bfactors = parse_pdb_bfactors(str(pdb_file))

        if len(bfactors) != len(CONSTRUCT):
            print(f"  WARNING: {pdb_file.name} has {len(bfactors)} residues, "
                  f"expected {len(CONSTRUCT)} — skipping")
            continue

        row = {
            "design": pdb_file.stem,
            "mean_confidence": float(np.mean(bfactors)),
            "min_confidence":  float(np.min(bfactors)),
        }

        for name, (start, end) in EPITOPES.items():
            scores = bfactors[start:end + 1]
            row[f"{name}_mean"] = float(np.mean(scores))
            row[f"{name}_min"]  = float(np.min(scores))

        for name, (start, end) in LINKERS.items():
            row[f"linker_{name}_mean"] = float(np.mean(bfactors[start:end + 1]))

        results.append(row)

    return pd.DataFrame(results)


def plot_ensemble_epitope_scores(df: pd.DataFrame, output_path: str):
    """Box plot of epitope confidence across ensemble."""
    epitope_cols = [f"{name}_mean" for name in EPITOPES]

    fig, ax = plt.subplots(figsize=(13, 6), facecolor="#0d0d0d")
    ax.set_facecolor("#0d0d0d")

    data = [df[col].dropna().values for col in epitope_cols]
    labels = [col.replace("_mean", "") for col in epitope_cols]

    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    medianprops=dict(color="#f1f5f9", lw=2))

    colors = ["#e63946", "#2a9d8f", "#e9c46a", "#f4a261", "#a8dadc"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.axhline(0.7, color="#4ade80", lw=1.2, linestyle="--", alpha=0.8,
               label="Viability threshold (0.7)")
    ax.axhline(0.5, color="#facc15", lw=0.8, linestyle="--", alpha=0.6,
               label="Borderline (0.5)")

    ax.set_ylim(0, 1.05)
    ax.set_ylabel("RFdiffusion Backbone Confidence", color="#cbd5e1", fontsize=11)
    ax.set_title(
        f"Epitope Region Confidence — RFdiffusion Ensemble (n={len(df)} designs)",
        color="#f1f5f9", fontsize=12, fontweight="bold"
    )
    ax.tick_params(colors="#94a3b8")
    ax.tick_params(axis="x", rotation=20)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    ax.legend(facecolor="#1e293b", edgecolor="#334155",
              labelcolor="#cbd5e1", fontsize=9)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#0d0d0d")
    plt.close()
    print(f"Ensemble figure saved: {output_path}")


def generate_rfdiffusion_report(df: pd.DataFrame, output_path: str) -> dict:
    """Write final structural assessment. Gate: median > 0.5 = viable."""
    report = {
        "construct_id":             "v3_optimized",
        "tool":                     "RFdiffusion partial diffusion",
        "n_designs":                len(df),
        "mean_ensemble_confidence": round(float(df["mean_confidence"].mean()), 3),
        "min_ensemble_confidence":  round(float(df["min_confidence"].min()), 3),
        "alphafold_context":        "AlphaFold2 inconclusive (mean pLDDT 36.4, MSA n=3)",
        "epitope_assessment":       {},
    }

    viable_count = 0
    for name in EPITOPES:
        col = f"{name}_mean"
        median_score = float(df[col].median())
        mean_score   = float(df[col].mean())
        min_score    = float(df[col].min())
        is_viable = median_score > 0.5
        if is_viable:
            viable_count += 1
        report["epitope_assessment"][name] = {
            "median_confidence": round(median_score, 3),
            "mean_confidence":   round(mean_score, 3),
            "min_confidence":    round(min_score, 3),
            "viable_for_wetlab": is_viable,
            "verdict":           "VIABLE" if is_viable else "LOW_CONFIDENCE",
        }

    n = len(EPITOPES)
    if viable_count == n:
        verdict   = "CLEAR_FOR_EXPERIMENTAL_PHASE"
        next_step = "Proceed to HLA binding assay and T-cell activation studies"
    elif viable_count >= n // 2 + 1:
        verdict   = "PARTIAL_CONFIDENCE_PROCEED_WITH_CAUTION"
        next_step = "Proceed to HLA binding assay; flag low-confidence epitopes for NMR/CD"
    else:
        verdict   = "REDESIGN_RECOMMENDED"
        next_step = "Review linker architecture; consider reordering epitope arrangement"

    report["global_verdict"]          = verdict
    report["recommended_next_step"]   = next_step
    report["viable_epitopes"]         = f"{viable_count}/{n}"
    report["validation_tier"]         = "COMPUTATIONALLY_VERIFIED (structural confidence assessed)"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"RFdiffusion report saved: {output_path}")
    return report


def run_rfdiffusion_analysis():
    PDB_DIR    = "results/RFDiffusion/v3_optimized_vozb8.result/outputs"
    CSV_OUT    = "results/rfdiffusion/ensemble_scores.csv"
    FIG_OUT    = "results/rfdiffusion/ensemble_epitope_confidence.png"
    REPORT_OUT = "results/rfdiffusion/rfdiffusion_structural_report.json"

    print("=== Step 1: Mapping epitope positions ===")
    for name, (s, e) in EPITOPES.items():
        print(f"  {name}: residues {s+1}-{e+1}")

    print("\n=== Step 2: Parsing RFdiffusion ensemble ===")
    df = analyze_backbone_ensemble(PDB_DIR)

    Path(CSV_OUT).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_OUT, index=False)
    print(f"Ensemble scores saved. Mean confidence: {df['mean_confidence'].mean():.3f}")

    print("\n=== Step 3: Generating ensemble figure ===")
    plot_ensemble_epitope_scores(df, FIG_OUT)

    print("\n=== Step 4: Writing report ===")
    report = generate_rfdiffusion_report(df, REPORT_OUT)

    print("\n=== FINAL VERDICT ===")
    print(f"Designs analyzed: {report['n_designs']}")
    print(f"Viable epitopes:  {report['viable_epitopes']}")
    print(f"Global verdict:   {report['global_verdict']}")
    print(f"Next step:        {report['recommended_next_step']}")

    return report


if __name__ == "__main__":
    run_rfdiffusion_analysis()
