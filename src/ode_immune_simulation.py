#!/usr/bin/env python3
"""
Phase 9B — ODE Immune Simulation for v3.1 Multi-Epitope Vaccine
================================================================
Implements an ODE model of the adaptive immune response for a
3-dose prime-boost-boost schedule (days 1, 28, 56).

Run this script to generate cimsim_results.csv, then run
  python src/immune_simulation.py
to produce plots and the final report.

Model state variables (arbitrary units, AU):
  A      - Antigen (depot kinetics with RS09 adjuvant)
  TH     - Effector CD4+ T helper cells
  TC     - Effector CD8+ cytotoxic T cells
  B      - Activated B cells / plasmablasts
  IgM    - IgM antibody titer
  IgG1   - IgG1 titer (Th2-associated, suppressed by RS09)
  IgG2   - IgG2 titer (Th1-associated, dominant with RS09 TLR4 agonist)
  IL2    - IL-2 (from TH, drives TC expansion)
  IL12   - IL-12 (from APCs, RS09-enhanced 4x, drives Th1)
  IFNg   - IFN-gamma (from TH+TC, Th1 polarization marker)

References:
  Perelson AS & Weisbuch G (1997) Rev Mod Phys 69:1219
  Carneiro J et al. (1996) J Biol Syst 4:53
  Antia R et al. (2005) Nature 437:108-111
  Pappalardo F et al. (2016) Pharmacol Res 110:13-22
  Kim DH et al. (2025) RS09 TLR4 adjuvant enhances Th1 responses
"""

import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from scipy.integrate import solve_ivp

ROOT    = Path(__file__).parent.parent
SIM_DIR = ROOT / "results" / "immune_simulation"
SIM_DIR.mkdir(parents=True, exist_ok=True)

INJECTION_DAYS = [1, 28, 56]
DOSE   = 100.0   # AU, antigen dose per injection
T_END  = 360     # days, total simulation
DT_OUT = 1.0     # output resolution (days)

# ── Parameters ────────────────────────────────────────────────────────────────
P = {
    # Antigen: depot release with RS09 adjuvant (half-life ~4.6 days)
    "d_A":      0.15,
    "k_AT":     0.005,   # T cell-mediated clearance coefficient
    "k_AB":     0.008,   # B cell-mediated clearance coefficient

    # CD4+ T helper (TH)
    "s_TH":     0.05,    # thymic source rate
    "p_TH":     0.55,    # max proliferation /day
    "KA_TH":    15.0,    # antigen half-saturation (AU)
    "KIL12_TH": 2.0,     # IL-12 half-saturation
    "d_TH":     0.07,    # effector death rate /day

    # CD8+ T cytotoxic (TC)
    "s_TC":     0.02,
    "p_TC":     0.70,
    "KA_TC":    15.0,
    "KIL2_TC":  1.5,
    "d_TC":     0.09,

    # B cells / plasmablasts
    "s_B":      0.02,
    "p_B":      0.80,
    "KA_B":     15.0,
    "KTH_B":    0.40,    # TH help threshold
    "d_B":      0.20,

    # Antibodies
    "k_IgM":    35.0,    # production per B cell
    "d_IgM":    0.09,    # decay /day  (~8 day half-life)
    "k_IgG1":   10.0,    # Th2-associated (suppressed by RS09)
    "d_IgG1":   0.006,   # decay /day (~116 day half-life)
    "k_IgG2":   30.0,    # Th1-associated (dominant with RS09)
    "d_IgG2":   0.006,
    "KIFNg_sw": 1.5,     # IFN-gamma half-sat for IgG2 class switching

    # IL-12 (from APCs, RS09/TLR4 agonist enhances 4x)
    "k_IL12":   6.0,     # base APC production rate
    "RS09":     3.0,     # fold-enhancement (total factor = 1+3 = 4)
    "KA_IL12":  10.0,
    "d_IL12":   0.55,

    # IL-2 (from TH, autocrine + paracrine TC expansion)
    "k_IL2":    2.0,
    "KA_IL2":   15.0,
    "d_IL2":    0.85,

    # IFN-gamma (Th1 polarization, from TH + TC)
    "k_IFNg":   2.5,
    "KA_IFNg":  15.0,
    "KIL12_Ig": 1.5,
    "d_IFNg":   0.50,
}

# State vector indices
iA, iTH, iTC, iB, iIgM, iIgG1, iIgG2, iIL2, iIL12, iIFNg = range(10)


def ode_system(t, y, p):
    y = np.maximum(y, 0.0)
    A, TH, TC, B, IgM, IgG1, IgG2, IL2, IL12, IFNg = y

    fA_TH   = A    / (p["KA_TH"]    + A)
    fA_TC   = A    / (p["KA_TC"]    + A)
    fA_B    = A    / (p["KA_B"]     + A)
    fA_I12  = A    / (p["KA_IL12"]  + A)
    fA_IL2  = A    / (p["KA_IL2"]   + A)
    fA_IFNg = A    / (p["KA_IFNg"]  + A)
    fIL12   = IL12 / (p["KIL12_TH"] + IL12)
    fIL2    = IL2  / (p["KIL2_TC"]  + IL2)
    fTH     = TH   / (p["KTH_B"]    + TH)
    fIFNg   = IFNg / (p["KIFNg_sw"] + IFNg)
    fIL12i  = IL12 / (p["KIL12_Ig"] + IL12)

    dA    = -p["d_A"] * A - p["k_AT"] * TH * A - p["k_AB"] * B * A

    dIL12 = p["k_IL12"] * (1.0 + p["RS09"]) * fA_I12 - p["d_IL12"] * IL12

    dTH   = p["s_TH"] + p["p_TH"] * fA_TH * fIL12 * TH - p["d_TH"] * TH

    dIL2  = p["k_IL2"] * TH * fA_IL2 - p["d_IL2"] * IL2

    dTC   = p["s_TC"] + p["p_TC"] * fA_TC * fIL2 * TC - p["d_TC"] * TC

    dIFNg = (p["k_IFNg"] * (TH + TC) * fA_IFNg * fIL12i
             - p["d_IFNg"] * IFNg)

    dB    = p["s_B"] + p["p_B"] * fA_B * fTH * B - p["d_B"] * B

    dIgM  = p["k_IgM"] * B - p["d_IgM"] * IgM

    dIgG1 = p["k_IgG1"] * B - p["d_IgG1"] * IgG1

    dIgG2 = p["k_IgG2"] * B * fIFNg - p["d_IgG2"] * IgG2

    return [dA, dTH, dTC, dB, dIgM, dIgG1, dIgG2, dIL2, dIL12, dIFNg]


def run_simulation(p):
    """Integrate ODE across injection breakpoints; return (times, Y_matrix)."""
    TH0 = p["s_TH"] / p["d_TH"]
    TC0 = p["s_TC"] / p["d_TC"]
    B0  = p["s_B"]  / p["d_B"]

    y0 = np.array([0.0, TH0, TC0, B0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    t_out = np.arange(0.0, T_END + DT_OUT, DT_OUT)

    breakpoints = [0.0] + [float(d) for d in INJECTION_DAYS] + [float(T_END)]

    times_all, Y_all = [], []
    y_curr = y0.copy()

    for i in range(len(breakpoints) - 1):
        t0, t1 = breakpoints[i], breakpoints[i + 1]

        if t0 in INJECTION_DAYS:
            y_curr[iA] += DOSE

        mask = (t_out >= t0) & (t_out <= t1)
        t_seg = t_out[mask]
        if len(t_seg) < 2:
            t_seg = np.array([t0, t1])

        sol = solve_ivp(
            ode_system,
            [t0, t1],
            y_curr,
            args=(p,),
            t_eval=t_seg,
            method="RK45",
            rtol=1e-7,
            atol=1e-10,
            max_step=0.25,
        )

        if not sol.success:
            print(f"  WARNING: solver failed in [{t0}, {t1}]: {sol.message}")
            break

        # Drop duplicate boundary point on subsequent segments
        skip = 1 if (times_all and abs(sol.t[0] - times_all[-1]) < 1e-9) else 0
        times_all.extend(sol.t[skip:].tolist())
        Y_all.extend(sol.y.T[skip:].tolist())
        y_curr = sol.y[:, -1].copy()

    return np.array(times_all), np.array(Y_all)


def save_csv(times, Y, out_path):
    """Write CSV in the column format expected by immune_simulation.py."""
    fields = ["Time", "IgM", "IgG1", "IgG2", "TH", "TC", "IFNg", "IL2", "IL12"]
    col_idx = {
        "Time": None, "IgM": iIgM, "IgG1": iIgG1, "IgG2": iIgG2,
        "TH": iTH, "TC": iTC, "IFNg": iIFNg, "IL2": iIL2, "IL12": iIL12,
    }
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, t in enumerate(times):
            row = {}
            for col in fields:
                if col == "Time":
                    row[col] = f"{t:.4f}"
                else:
                    row[col] = f"{Y[i, col_idx[col]]:.6f}"
            w.writerow(row)
    print(f"  CSV: {out_path}")


def print_summary(times, Y):
    IgM   = Y[:, iIgM]
    IgG1  = Y[:, iIgG1]
    IgG2  = Y[:, iIgG2]
    IgG   = np.maximum(IgG1, IgG2)
    TH    = Y[:, iTH]
    TC    = Y[:, iTC]
    IFNg  = Y[:, iIFNg]
    IL12  = Y[:, iIL12]

    th1_ratio = IgG2.max() / max(IgG1.max(), 1e-9)

    print(f"  Peak IgM:   {IgM.max():>10.1f} AU  (day {times[IgM.argmax()]:>4.0f})")
    print(f"  Peak IgG1:  {IgG1.max():>10.1f} AU  (day {times[IgG1.argmax()]:>4.0f})")
    print(f"  Peak IgG2:  {IgG2.max():>10.1f} AU  (day {times[IgG2.argmax()]:>4.0f})")
    print(f"  Peak IgG:   {IgG.max():>10.1f} AU  (day {times[IgG.argmax()]:>4.0f})")
    print(f"  Peak CD4+:  {TH.max():>10.2f} AU  (day {times[TH.argmax()]:>4.0f})")
    print(f"  Peak CD8+:  {TC.max():>10.2f} AU  (day {times[TC.argmax()]:>4.0f})")
    print(f"  Peak IFN-g: {IFNg.max():>10.2f} AU  (day {times[IFNg.argmax()]:>4.0f})")
    print(f"  Peak IL-12: {IL12.max():>10.2f} AU  (day {times[IL12.argmax()]:>4.0f})")
    print()
    print(f"  IgG2/IgG1 ratio: {th1_ratio:.1f}x  "
          f"({'Th1-polarized [PASS]' if th1_ratio > 2.0 else 'Th2-dominant [FAIL]'})")
    print(f"  Peak IgG >1000 AU: "
          f"{'[PASS]' if IgG.max() > 1000 else '[FAIL]'}")
    print(f"  IFN-g detectable: "
          f"{'[PASS]' if IFNg.max() > 1.0 else '[FAIL]'}")


def save_metadata(times, Y, out_path):
    IgM  = Y[:, iIgM]
    IgG1 = Y[:, iIgG1]
    IgG2 = Y[:, iIgG2]
    IgG  = np.maximum(IgG1, IgG2)
    TH   = Y[:, iTH]
    TC   = Y[:, iTC]
    IFNg = Y[:, iIFNg]
    IL12 = Y[:, iIL12]

    meta = {
        "construct":        "v3_1_single_kk",
        "simulation":       "ODE-Celada-Seiden (local)",
        "model_references": [
            "Perelson & Weisbuch (1997) Rev Mod Phys 69:1219",
            "Carneiro et al. (1996) J Biol Syst 4:53",
            "Antia et al. (2005) Nature 437:108-111",
            "Pappalardo et al. (2016) Pharmacol Res 110:13-22",
        ],
        "injection_days":   INJECTION_DAYS,
        "dose_AU":          DOSE,
        "adjuvant":         "RS09 (TLR4 agonist, 4x IL-12 enhancement)",
        "HLA_I":            "A*03:01",
        "HLA_II":           "DRB1*15:01",
        "total_duration":   float(times[-1]),
        "peak_IgM":         float(IgM.max()),
        "day_peak_IgM":     float(times[IgM.argmax()]),
        "peak_IgG1":        float(IgG1.max()),
        "peak_IgG2":        float(IgG2.max()),
        "peak_IgG":         float(IgG.max()),
        "day_peak_IgG":     float(times[IgG.argmax()]),
        "IgG2_IgG1_ratio":  float(IgG2.max() / max(IgG1.max(), 1e-9)),
        "peak_TH":          float(TH.max()),
        "peak_TC":          float(TC.max()),
        "peak_IFNg":        float(IFNg.max()),
        "peak_IL12":        float(IL12.max()),
        "Th1_polarized":    bool(IgG2.max() / max(IgG1.max(), 1e-9) > 2.0),
        "IgG_threshold_pass": bool(IgG.max() > 1000),
    }
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  Metadata: {out_path}")


def main():
    print("=" * 60)
    print("PHASE 9B — ODE IMMUNE SIMULATION (v3.1 VACCINE)")
    print("=" * 60)
    print(f"  Schedule: {INJECTION_DAYS} days | Duration: {T_END} days")
    print(f"  Adjuvant: RS09 (TLR4 agonist, 4x IL-12 boost)")
    print(f"  HLA: A*03:01 / DRB1*15:01")
    print()

    print("Running ODE integration...")
    times, Y = run_simulation(P)
    print(f"  {len(times)} time points solved\n")

    print("Peak immune response metrics:")
    print_summary(times, Y)
    print()

    csv_path  = SIM_DIR / "cimsim_results.csv"
    meta_path = SIM_DIR / "ode_simulation_metadata.json"
    save_csv(times, Y, csv_path)
    save_metadata(times, Y, meta_path)
    print()
    print("Next: python src/immune_simulation.py")


if __name__ == "__main__":
    main()
