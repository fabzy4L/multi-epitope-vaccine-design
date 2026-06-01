#!/usr/bin/env python3
"""
Phase 9B — C-ImmSim Immune Simulation Analysis
================================================
Parses and visualizes C-ImmSim output for a 3-dose immunization schedule
of the v3.1 multi-epitope vaccine construct.

C-ImmSim server: http://150.146.2.1/C-IMMSIM/submit.php  (CRS4, primary)
IIMCB mirror (https://iimcb.genesilico.pl/cimsim/) is currently unavailable.

After submission and download, place C-ImmSim CSV output at:
  results/immune_simulation/cimsim_results.csv

Then run: python src/immune_simulation.py

C-ImmSim submission parameters:
  Sequence:      v3.1 (paste from validation_tier.py construct_v3_1.sequence)
  Injections:    3
  Injection days: 1, 28, 56  (standard prime-boost-boost schedule)
  HLA alleles:   A*03:01, DRB1*15:01 (top MHC-I and MHC-II alleles in construct)
"""

import json
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
SIM_DIR = ROOT / "results" / "immune_simulation"
SIM_DIR.mkdir(parents=True, exist_ok=True)

V3_1_SEQUENCE = (
    "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD"
    "GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK"
    "AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
)

INJECTION_DAYS = [1, 28, 56]

# C-ImmSim CSV columns (standard output):
# Time, TH, TC, B, IgM, IgG1, IgG2, IgE, IL2, IL4, IL10, IL12, IFNg, ...
COLUMNS_OF_INTEREST = {
    "Time":  "Time (days)",
    "IgM":   "IgM titer",
    "IgG1":  "IgG1 titer",
    "IgG2":  "IgG2 titer",
    "TH":    "T helper cells",
    "TC":    "Cytotoxic T cells",
    "IFNg":  "IFN-γ",
    "IL2":   "IL-2",
    "IL12":  "IL-12",
}


def parse_cimsim_csv(path: Path) -> dict:
    data = {col: [] for col in COLUMNS_OF_INTEREST}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in COLUMNS_OF_INTEREST:
                if col in row:
                    try:
                        data[col].append(float(row[col]))
                    except ValueError:
                        data[col].append(0.0)
    return data


def compute_metrics(data: dict) -> dict:
    time = data.get("Time", [])
    if not time:
        return {}

    def peak(series):
        return round(max(series), 4) if series else None

    def time_to_peak(series):
        if not series:
            return None
        idx = series.index(max(series))
        return time[idx] if idx < len(time) else None

    igg = [max(data.get("IgG1", [0])[i], data.get("IgG2", [0])[i])
           for i in range(len(time))]

    return {
        "peak_IgM":       peak(data.get("IgM", [])),
        "peak_IgG":       peak(igg),
        "day_peak_IgG":   time_to_peak(igg),
        "peak_TH":        peak(data.get("TH", [])),
        "peak_TC":        peak(data.get("TC", [])),
        "peak_IFNg":      peak(data.get("IFNg", [])),
        "peak_IL2":       peak(data.get("IL2", [])),
        "peak_IL12":      peak(data.get("IL12", [])),
        "injection_days": INJECTION_DAYS,
        "total_duration": max(time) if time else None,
    }


def plot_immune_response(data: dict, metrics: dict, out_path: Path):
    time = data["Time"]
    igg = [max(data.get("IgG1", [0])[i], data.get("IgG2", [0])[i])
           for i in range(len(time))]
    igm = data.get("IgM", [])
    th  = data.get("TH", [])
    tc  = data.get("TC", [])
    ifng = data.get("IFNg", [])

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor="#0d0d0d")
    fig.suptitle("v3.1 Vaccine — C-ImmSim Immune Response (3-dose schedule)",
                 color="#f1f5f9", fontsize=13, fontweight="bold")

    plot_configs = [
        (axes[0, 0], [("IgG", igg, "#4ade80"), ("IgM", igm, "#60a5fa")],
         "Antibody Titer"),
        (axes[0, 1], [("T helper (CD4+)", th, "#a78bfa"),
                       ("Cytotoxic T (CD8+)", tc, "#f472b6")],
         "T Cell Response"),
        (axes[1, 0], [("IFN-γ", ifng, "#fb923c")],
         "IFN-γ (Th1 response)"),
        (axes[1, 1], [("IL-2", data.get("IL2", []), "#facc15"),
                       ("IL-12", data.get("IL12", []), "#34d399")],
         "Pro-inflammatory Cytokines"),
    ]

    for ax, series_list, ylabel in plot_configs:
        ax.set_facecolor("#0d0d0d")
        for label, series, color in series_list:
            if series:
                ax.plot(time, series, color=color, lw=1.8, label=label, alpha=0.9)
        for day in INJECTION_DAYS:
            ax.axvline(day, color="#94a3b8", lw=0.8, linestyle="--", alpha=0.5)
        ax.set_xlabel("Days", color="#94a3b8", fontsize=9)
        ax.set_ylabel(ylabel, color="#94a3b8", fontsize=9)
        ax.tick_params(colors="#94a3b8", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")
        if any(s for _, s, _ in series_list):
            ax.legend(facecolor="#1e293b", edgecolor="#334155",
                      labelcolor="#cbd5e1", fontsize=8)

    inj_patch = mpatches.Patch(color="#94a3b8", alpha=0.5,
                                label=f"Injections: days {INJECTION_DAYS}")
    fig.legend(handles=[inj_patch], loc="lower center",
               facecolor="#1e293b", edgecolor="#334155",
               labelcolor="#cbd5e1", fontsize=9)

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#0d0d0d")
    plt.close()
    print(f"Figure: {out_path}")


def write_submission_guide():
    guide = SIM_DIR / "CIMSIM_SUBMISSION_GUIDE.md"
    content = f"""# C-ImmSim Submission Guide — v3.1 Vaccine

**Server:** https://iimcb.genesilico.pl/cimsim/

---

## Sequence to Submit (v3.1, 142 aa)

```
{V3_1_SEQUENCE}
```

---

## Submission Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Injections | 3 | Prime-boost-boost schedule |
| Injection days | 1, 28, 56 | Standard 4-week intervals |
| HLA-I allele | A\\*03:01 | Top MHC-I allele in construct (RLFRKSNLK, 4.82 nM) |
| HLA-II allele | DRB1\\*15:01 | Top MHC-II allele in construct (QTLLALHRSYLTPGD, 9.87 nM) |
| Random seed | 12345 | For reproducibility |

---

## Downloading Results

Download the CSV output file and save as:
`results/immune_simulation/cimsim_results.csv`

Then run: `python src/immune_simulation.py`

---

## Expected Signals

| Metric | Minimum acceptable | Strong response |
|---|---|---|
| Peak IgG titer | > 1,000 AU | > 10,000 AU |
| Peak IFN-γ | Detectable rise | > 3× baseline |
| CD8+ T cell peak | Detectable rise post dose 1 | Strong boost post dose 2/3 |
| IL-12 | Elevated (Th1 polarization) | Sustained across doses |

A Th1-skewed response (IFN-γ, IL-12, CD8+ T cells) is desired for a viral peptide vaccine
targeting intracellular antigen presentation.
"""
    guide.write_text(content, encoding="utf-8")
    print(f"Submission guide: {guide}")


def run_immune_simulation():
    print("=" * 55)
    print("PHASE 9B — C-IMMSIM IMMUNE SIMULATION ANALYSIS")
    print("=" * 55)

    write_submission_guide()

    csv_path = SIM_DIR / "cimsim_results.csv"
    if not csv_path.exists():
        print(f"\nC-ImmSim results not found at {csv_path}")
        print("Server: http://150.146.2.1/C-IMMSIM/submit.php")
        print("Guide:  results/immune_simulation/CIMSIM_SUBMISSION_GUIDE.md")
        print("\nv3.1 sequence for submission:")
        print(V3_1_SEQUENCE)
        return None

    print("\nParsing C-ImmSim results...")
    data = parse_cimsim_csv(csv_path)
    metrics = compute_metrics(data)

    print(f"\n  Peak IgG:     {metrics.get('peak_IgG')} AU  (day {metrics.get('day_peak_IgG')})")
    print(f"  Peak IgM:     {metrics.get('peak_IgM')} AU")
    print(f"  Peak CD4+ TH: {metrics.get('peak_TH')}")
    print(f"  Peak CD8+ TC: {metrics.get('peak_TC')}")
    print(f"  Peak IFN-γ:   {metrics.get('peak_IFNg')}")
    print(f"  Peak IL-12:   {metrics.get('peak_IL12')}")

    report = {"construct": "v3_1_single_kk", "simulation": "C-ImmSim", **metrics}
    out_json = SIM_DIR / "immune_simulation_report.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport: {out_json}")

    plot_immune_response(data, metrics, SIM_DIR / "immune_response_curves.png")

    return report


if __name__ == "__main__":
    run_immune_simulation()
