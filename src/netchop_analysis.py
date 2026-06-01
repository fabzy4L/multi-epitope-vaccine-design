#!/usr/bin/env python3
"""
Phase 8A — NetChop Junction Analysis
=====================================

Analyzes proteasomal cleavage probability at the KKGPGPGKK double-KK junction
in v3_optimized. Determines whether FLAG_04 blocks synthesis.

MANUAL STEP REQUIRED before running:
1. Go to: https://services.healthtech.dtu.dk/services/NetChop-3.1/
2. Paste the v3 sequence below into the input box
3. Method: C-term 3.0
4. Threshold: 0.5
5. Submit and copy the per-residue cleavage scores table
6. Paste results into NETCHOP_SCORES below as list of (residue, aa, score) tuples
7. Then run: python src/netchop_analysis.py

v3 sequence to submit:
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGDGPGPGINITRFQTLLALHRSKKGPGPGKKLPFNDGVYFAAYRLFRKSNLKAAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
"""

import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# If non-empty, these manual scores take precedence over CSV auto-load.
# Format: list of (residue_number, amino_acid, cleavage_score)
NETCHOP_SCORES = []

# CSV downloaded from NetChop server (auto-loaded when NETCHOP_SCORES is empty)
_CSV_PATHS = [
    Path(__file__).parent / "netchop_predictions_6A1D33D0002BF97E62F521C8.csv",
    Path(__file__).parent.parent / "results" / "netchop" /
        "netchop_predictions_6A1D33D0002BF97E62F521C8.csv",
]


def _load_csv() -> list:
    for p in _CSV_PATHS:
        if p.exists():
            rows = []
            with open(p, newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    rows.append((int(row["pos"]), row["AA"], float(row["score"])))
            print(f"NetChop scores loaded from {p} ({len(rows)} residues)")
            return rows
    raise FileNotFoundError(
        "No NetChop CSV found. Submit v3 to NetChop 3.1 and place the CSV in src/."
    )

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
).replace(' ', '').replace('\n', '')

# Junction region: KKGPGPGKK
KK_GPGPG_KK = "KKGPGPGKK"
junction_start = CONSTRUCT.find(KK_GPGPG_KK)
junction_end = junction_start + len(KK_GPGPG_KK) - 1

EPITOPE_BOUNDARIES = {
    "INITRFQTLLALHRS_Cterm": CONSTRUCT.find("INITRFQTLLALHRS") + 14,
    "KK_GPGPG_KK_start":     junction_start,
    "KK_GPGPG_KK_end":       junction_end,
    "LPFNDGVYF_Nterm":       CONSTRUCT.find("LPFNDGVYF"),
}


def parse_netchop_output(raw_scores: list) -> np.ndarray:
    """Convert NetChop output rows to per-residue score array."""
    scores = np.zeros(len(CONSTRUCT))
    for res_num, aa, score in raw_scores:
        idx = res_num - 1
        if 0 <= idx < len(CONSTRUCT):
            scores[idx] = float(score)
    return scores


def analyze_junction(cleavage_scores: np.ndarray) -> dict:
    """
    Assess cleavage risk at KKGPGPGKK junction.
    Decision threshold: max > 0.7 = redesign required.
    """
    junction_scores = cleavage_scores[junction_start:junction_end + 1]
    max_junction = float(np.max(junction_scores))
    mean_junction = float(np.mean(junction_scores))

    initr_cterm = float(cleavage_scores[EPITOPE_BOUNDARIES["INITRFQTLLALHRS_Cterm"]])
    lpfnd_nterm = float(cleavage_scores[EPITOPE_BOUNDARIES["LPFNDGVYF_Nterm"]])

    redesign_required = max_junction > 0.7

    return {
        "junction_sequence": KK_GPGPG_KK,
        "junction_residues": f"{junction_start + 1}-{junction_end + 1}",
        "max_cleavage_score": round(max_junction, 3),
        "mean_cleavage_score": round(mean_junction, 3),
        "per_residue_scores": junction_scores.tolist(),
        "adjacent_epitope_Cterm_score": round(initr_cterm, 3),
        "adjacent_epitope_Nterm_score": round(lpfnd_nterm, 3),
        "redesign_required": redesign_required,
        "verdict": (
            "REDESIGN_JUNCTION_TO_SINGLE_KK" if redesign_required
            else "JUNCTION_ACCEPTABLE"
        ),
        "synthesis_gate": "BLOCKED" if redesign_required else "CLEARED",
    }


def plot_netchop_full(cleavage_scores: np.ndarray, output_path: str):
    """Full construct cleavage probability plot with junction highlighted."""
    fig, ax = plt.subplots(figsize=(14, 5), facecolor='#0d0d0d')
    ax.set_facecolor('#0d0d0d')

    residues = np.arange(1, len(cleavage_scores) + 1)
    ax.bar(residues, cleavage_scores, color='#60a5fa', alpha=0.7, width=0.8)
    ax.axhline(0.7, color='#f87171', lw=1.2, linestyle='--',
               label='Redesign threshold (0.7)', alpha=0.8)
    ax.axhline(0.5, color='#facc15', lw=0.8, linestyle='--',
               label='NetChop threshold (0.5)', alpha=0.6)

    ax.axvspan(junction_start + 1, junction_end + 1,
               alpha=0.3, color='#f87171', label='KK-GPGPG-KK junction')

    ax.set_xlim(1, len(cleavage_scores))
    ax.set_ylim(0, 1.1)
    ax.set_xlabel('Residue Position', color='#cbd5e1', fontsize=11)
    ax.set_ylabel('Cleavage Probability', color='#cbd5e1', fontsize=11)
    ax.set_title('v3_optimized — NetChop C-term 3.0 Cleavage Prediction',
                 color='#f1f5f9', fontsize=12, fontweight='bold')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')
    ax.legend(facecolor='#1e293b', edgecolor='#334155',
              labelcolor='#cbd5e1', fontsize=9)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0d0d0d')
    plt.close()
    print(f"NetChop figure saved: {output_path}")


def run_netchop_analysis():
    scores = NETCHOP_SCORES if NETCHOP_SCORES else _load_csv()
    cleavage_scores = parse_netchop_output(scores)
    junction_result = analyze_junction(cleavage_scores)

    print("=== NetChop Junction Analysis ===")
    print(f"Junction:           {junction_result['junction_sequence']} "
          f"(res {junction_result['junction_residues']})")
    print(f"Max cleavage score: {junction_result['max_cleavage_score']}")
    print(f"Mean cleavage score:{junction_result['mean_cleavage_score']}")
    print(f"Verdict:            {junction_result['verdict']}")
    print(f"Synthesis gate:     {junction_result['synthesis_gate']}")

    plot_netchop_full(cleavage_scores, 'results/netchop/netchop_cleavage_map.png')

    report = {
        "construct_id": "v3_optimized",
        "tool": "NetChop 3.1 C-term 3.0",
        "junction_analysis": junction_result,
        "full_cleavage_scores": cleavage_scores.tolist(),
    }
    with open('results/netchop/netchop_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("Report saved: results/netchop/netchop_report.json")

    if junction_result['synthesis_gate'] == 'CLEARED':
        print("\nFLAG_04 RESOLVED — update construct_v3.known_design_flags[3].blocks_synthesis = False")
        print("Remove 'NetChop_junction_analysis' from validation_pending")
    else:
        print("\nFLAG_04 UNRESOLVED — redesign KKGPGPGKK to single KK before synthesis")

    return report


if __name__ == "__main__":
    run_netchop_analysis()
