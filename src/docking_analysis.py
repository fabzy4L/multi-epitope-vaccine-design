#!/usr/bin/env python3
"""
Phase 9A — HDOCK Result Analysis
==================================
Parses HDOCK docking output files and generates a structured report
with binding scores, confidence levels, and interface assessment.

After HDOCK submissions complete, place results in:
  results/docking/run1_TLR4/hdock.out
  results/docking/run2_MHC_I/hdock.out
  results/docking/run3_MHC_II/hdock.out
  results/docking/run4_IgG/hdock.out

Then run: python src/docking_analysis.py
"""

import json
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCKING_DIR = ROOT / "results" / "docking"

RUNS = {
    "run1_TLR4":  {"label": "TLR4/MD-2",     "target_dg": -8.0, "epitope": "RS09 adjuvant"},
    "run2_MHC_I": {"label": "HLA-A*02:01",   "target_dg": -8.0, "epitope": "RLFRKSNLK / LPFNDGVYF"},
    "run3_MHC_II":{"label": "HLA-DR1",       "target_dg": -8.0, "epitope": "QTLLALHRSYLTPGD"},
    "run4_IgG":   {"label": "IgG2a Fab",     "target_dg": -7.0, "epitope": "Surface epitopes"},
}

# HDOCK hdock.out format:
# Model   Score    Confidence   Ligand-RMSD
# 1       -300.45  0.9132       0.000
HDOCK_PATTERN = re.compile(
    r"^\s*(\d+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", re.MULTILINE
)

# HDOCK score → approximate ΔG conversion (empirical linear fit from HDOCK benchmarks)
# Score < -200: strong binding; -100 to -200: moderate; > -100: weak
def hdock_score_to_dg(score: float) -> float:
    return round(score / 30.0, 2)


def parse_hdock_out(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    models = []
    for m in HDOCK_PATTERN.finditer(text):
        rank, score, confidence, rmsd = m.groups()
        dg = hdock_score_to_dg(float(score))
        models.append({
            "rank":       int(rank),
            "score":      float(score),
            "dg_approx":  dg,
            "confidence": float(confidence),
            "ligand_rmsd":float(rmsd),
        })
    return models


def assess_binding(models: list[dict], target_dg: float) -> dict:
    if not models:
        return {"status": "NO_DATA", "best_score": None, "best_dg": None, "verdict": "No results found"}

    best = models[0]
    top5_dg = [m["dg_approx"] for m in models[:5]]
    mean_top5 = round(np.mean(top5_dg), 2)

    if best["dg_approx"] <= target_dg:
        verdict = "BINDING_PREDICTED"
    elif best["dg_approx"] <= target_dg + 1.5:
        verdict = "MARGINAL_BINDING"
    else:
        verdict = "WEAK_BINDING"

    return {
        "status":          verdict,
        "best_score":      best["score"],
        "best_dg_approx":  best["dg_approx"],
        "best_confidence": best["confidence"],
        "mean_top5_dg":    mean_top5,
        "target_dg":       target_dg,
        "n_models":        len(models),
    }


def plot_docking_summary(results: dict, out_path: Path):
    labels = [cfg["label"] for cfg in RUNS.values()]
    best_dgs = []
    colors = []

    for run_key, cfg in RUNS.items():
        r = results.get(run_key, {})
        dg = r.get("best_dg_approx")
        best_dgs.append(dg if dg is not None else 0)
        if r.get("status") == "BINDING_PREDICTED":
            colors.append("#4ade80")
        elif r.get("status") == "MARGINAL_BINDING":
            colors.append("#facc15")
        else:
            colors.append("#f87171")

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#0d0d0d")
    ax.set_facecolor("#0d0d0d")

    x = np.arange(len(labels))
    bars = ax.bar(x, best_dgs, color=colors, alpha=0.85, width=0.5)

    for bar, val in zip(bars, best_dgs):
        if val:
            ax.text(bar.get_x() + bar.get_width() / 2, val - 0.2,
                    f"{val:.1f}", ha="center", va="top",
                    color="#f1f5f9", fontsize=10, fontweight="bold")

    thresholds = [cfg["target_dg"] for cfg in RUNS.values()]
    for xi, thr in zip(x, thresholds):
        ax.hlines(thr, xi - 0.3, xi + 0.3, colors="#f87171",
                  linestyle="--", linewidth=1.2, alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color="#cbd5e1", fontsize=10)
    ax.set_ylabel("Approx. ΔG (kcal/mol)", color="#cbd5e1", fontsize=11)
    ax.set_title("v3.1 Vaccine Construct — HDOCK Binding Summary",
                 color="#f1f5f9", fontsize=12, fontweight="bold")
    ax.tick_params(colors="#94a3b8")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    from matplotlib.patches import Patch
    legend = [
        Patch(color="#4ade80", alpha=0.85, label="Binding predicted"),
        Patch(color="#facc15", alpha=0.85, label="Marginal"),
        Patch(color="#f87171", alpha=0.85, label="Weak / no data"),
    ]
    ax.legend(handles=legend, facecolor="#1e293b", edgecolor="#334155",
              labelcolor="#cbd5e1", fontsize=9)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#0d0d0d")
    plt.close()
    print(f"Figure: {out_path}")


def run_docking_analysis():
    print("=" * 55)
    print("PHASE 9A — HDOCK RESULT ANALYSIS")
    print("=" * 55)

    results = {}
    missing = []

    for run_key, cfg in RUNS.items():
        hdock_out = DOCKING_DIR / run_key / "hdock.out"
        if not hdock_out.exists():
            print(f"\n  [{run_key}] hdock.out not found — submit via HDOCK first")
            missing.append(run_key)
            continue

        models = parse_hdock_out(hdock_out)
        assessment = assess_binding(models, cfg["target_dg"])
        results[run_key] = {**assessment, "label": cfg["label"], "epitope": cfg["epitope"]}

        print(f"\n  {cfg['label']} ({cfg['epitope']})")
        print(f"    Best ΔG (approx): {assessment['best_dg_approx']} kcal/mol "
              f"(target: ≤ {cfg['target_dg']})")
        print(f"    Confidence:       {assessment['best_confidence']}")
        print(f"    Mean top-5 ΔG:    {assessment['mean_top5_dg']}")
        print(f"    Verdict:          {assessment['status']}")

    if missing:
        print(f"\n  Missing runs: {missing}")
        print("  See results/docking/SUBMISSION_GUIDE.md")
        if not results:
            return

    out_json = DOCKING_DIR / "docking_report.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nReport: {out_json}")

    plot_docking_summary(results, DOCKING_DIR / "docking_summary.png")

    cleared = [k for k, v in results.items() if v.get("status") == "BINDING_PREDICTED"]
    print(f"\nBinding predicted: {len(cleared)}/{len(results)} targets")
    if len(cleared) == len(RUNS):
        print("ALL TARGETS: structural docking support confirmed — add to manuscript methods.")
    elif len(cleared) >= 2:
        print("PARTIAL: report successful targets; discuss failures in limitations.")
    else:
        print("WEAK: review poses in ChimeraX before reporting.")

    return results


if __name__ == "__main__":
    run_docking_analysis()
