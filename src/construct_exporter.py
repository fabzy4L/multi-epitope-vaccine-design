#!/usr/bin/env python3
"""
Construct Exporter — LabOps.AI Integration Manifest
====================================================
Assembles validated v3.1 construct data from pipeline result files into a
standardized JSON manifest consumable by LabOps.AI's construct_intake module.

Reads:
  results/docking/docking_report.json
  results/immune_simulation/ode_simulation_metadata.json
  results/sars_cov2/construct_design/selected_epitopes.json

Writes:
  results/labops_manifest.json

Run: python src/construct_exporter.py
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Source files ──────────────────────────────────────────────────────────────
DOCKING_REPORT    = ROOT / "results" / "docking" / "docking_report.json"
SIM_METADATA      = ROOT / "results" / "immune_simulation" / "ode_simulation_metadata.json"
SELECTED_EPITOPES = ROOT / "results" / "sars_cov2" / "construct_design" / "selected_epitopes.json"
MANIFEST_OUT      = ROOT / "results" / "labops_manifest.json"

# ── v3.1 construct data (web-tool results have no single JSON source) ─────────
V3_1 = {
    "version_id":          "v3.1",
    "sequence":            (
        "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD"
        "GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK"
        "AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
    ),
    "length_aa":            142,
    "molecular_weight_kda": 15.1,
    "theoretical_pi":       10.13,
    "gravy_score":         -0.147,
    "instability_index":    42.6,
    # pI > 9.0 → non-specific electrostatic interactions in E. coli cytoplasm
    "expression_system":   "HEK293",
    "expression_risk":     "HIGH_PI_EXPRESSION_RISK",
    "allergenicity":       "NON-ALLERGEN",
    "allergenicity_tool":  "AllerTop_v2.1",
    "allergenicity_match": "BCL9L_HUMAN",
    "antigenicity_overall": 0.2592,
    "antigenicity_tool":   "VaxiJen_v2.0",
    "validation_tier":     "computationally_verified",
    "synthesis_gate":      "CLEARED",
}

# VaxiJen per-epitope results (web-tool; stored here for reproducibility)
VAXIJEN_SCORES = {
    "RLFRKSNLK":        {"score": -0.2829, "prediction": "NON-ANTIGEN"},
    "LPFNDGVYF":        {"score":  0.5593, "prediction": "ANTIGEN"},
    "FPNITNLCPF":       {"score":  1.3964, "prediction": "ANTIGEN"},
    "VLYNSASFSTFK":     {"score":  0.0249, "prediction": "NON-ANTIGEN"},
    "QTLLALHRSYLTPGD":  {"score":  0.6708, "prediction": "ANTIGEN"},
    "INITRFQTLLALHRS":  {"score":  0.4118, "prediction": "ANTIGEN"},
}


def get_pipeline_version() -> str:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        return f"git:{sha}"
    except Exception:
        return "unknown"


def build_epitope_list(epitope_data: dict) -> list[dict]:
    """Select v3.1 epitopes (top-2 MHC-II, top-4 MHC-I by IC50) and attach VaxiJen scores."""
    mhc_i  = sorted(epitope_data["mhc_i_epitopes"],  key=lambda x: x["ic50"])[:4]
    mhc_ii = sorted(epitope_data["mhc_ii_epitopes"], key=lambda x: x["ic50"])[:2]

    result = []
    for pos, ep in enumerate(mhc_ii, start=1):
        vj = VAXIJEN_SCORES.get(ep["peptide"], {})
        result.append({
            "peptide":             ep["peptide"],
            "mhc_class":          "MHC_II",
            "hla_allele":         ep["allele"],
            "ic50_nm":            ep["ic50"],
            "percentile_rank":    ep.get("rank"),
            "position_in_construct": pos,
            "vaxijen_score":      vj.get("score"),
            "vaxijen_prediction": vj.get("prediction"),
        })
    for pos, ep in enumerate(mhc_i, start=len(mhc_ii) + 1):
        vj = VAXIJEN_SCORES.get(ep["peptide"], {})
        result.append({
            "peptide":             ep["peptide"],
            "mhc_class":          "MHC_I",
            "hla_allele":         ep["allele"],
            "ic50_nm":            ep["ic50"],
            "percentile_rank":    ep.get("rank"),
            "position_in_construct": pos,
            "vaxijen_score":      vj.get("score"),
            "vaxijen_prediction": vj.get("prediction"),
        })
    return result


def build_docking_list(docking: dict) -> list[dict]:
    return [
        {
            "run_id":             run_id,
            "target":             v["label"],
            "epitope":            v["epitope"],
            "hdock_score":        v["best_score"],
            "delta_g_kcal_mol":   v["best_dg_approx"],
            "mean_top5_dg":       v["mean_top5_dg"],
            "threshold_kcal_mol": v["target_dg"],
            "n_models":           v["n_models"],
            "verdict":            v["status"],
        }
        for run_id, v in docking.items()
    ]


def main() -> None:
    docking  = json.loads(DOCKING_REPORT.read_text())
    sim      = json.loads(SIM_METADATA.read_text())
    epitopes = json.loads(SELECTED_EPITOPES.read_text())

    manifest = {
        "manifest_version":    "1.0",
        "pipeline":            "multi-epitope-vaccine-design",
        "pipeline_version":    get_pipeline_version(),
        "export_timestamp":    datetime.now(timezone.utc).isoformat(),
        "construct":           V3_1,
        "epitopes":            build_epitope_list(epitopes),
        "docking_results":     build_docking_list(docking),
        "immune_simulation": {
            "model":           sim["simulation"],
            "model_references": sim["model_references"],
            "injection_days":  sim["injection_days"],
            "dose_au":         sim["dose_AU"],
            "adjuvant":        sim["adjuvant"],
            "hla_i":           sim["HLA_I"],
            "hla_ii":          sim["HLA_II"],
            "total_duration":  sim["total_duration"],
            "results": {
                "IgM_peak_au":      sim["peak_IgM"],
                "IgM_peak_day":     sim.get("day_peak_IgM"),
                "IgG1_peak_au":     sim["peak_IgG1"],
                "IgG2_peak_au":     sim["peak_IgG2"],
                "IgG_peak_au":      sim["peak_IgG"],
                "IgG_peak_day":     sim["day_peak_IgG"],
                "IgG2_IgG1_ratio":  sim["IgG2_IgG1_ratio"],
                "IFNg_peak_au":     sim["peak_IFNg"],
                "IL12_peak_au":     sim["peak_IL12"],
                "CD8_TC_peak_au":   sim["peak_TC"],
                "CD4_TH_peak_au":   sim["peak_TH"],
                "Th1_polarized":    sim["Th1_polarized"],
                "IgG_threshold_pass": sim["IgG_threshold_pass"],
            },
        },
    }

    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2))
    print(f"[OK] Manifest written: {MANIFEST_OUT}")
    print(f"     Pipeline version : {manifest['pipeline_version']}")
    print(f"     Construct        : {V3_1['version_id']} ({V3_1['length_aa']} aa)")
    print(f"     Epitopes         : {len(manifest['epitopes'])}")
    print(f"     Docking runs     : {len(manifest['docking_results'])}")


if __name__ == "__main__":
    main()
