#!/usr/bin/env python3
"""
Selectivity Verification
========================

Recomputes the prediction count, strong-binder count and selectivity rate
directly from the IEDB export files in
results/sars_cov2/iedb_predictions/, so every number reported in the
manuscript can be regenerated from the raw data.

This reads only real NetMHCpan and NetMHCIIpan output. It does not generate,
impute or substitute any binding value.

Strong-binder criteria (as stated in the manuscript):
    MHC-I : IC50 < 50 nM and percentile rank < 0.5%
    MHC-II: IC50 < 50 nM and percentile rank < 1.0%

Usage:
    python src/verify_selectivity.py
"""

import glob
import io
from pathlib import Path

import pandas as pd

PRED_DIR = Path("results/sars_cov2/iedb_predictions")
MHC_I_GLOB = str(PRED_DIR / "mhc_i_results" / "*.csv")
MHC_II_GLOB = str(PRED_DIR / "mhc_ii_results" / "*.csv")

IC50_CUTOFF = 50.0
RANK_CUTOFF = {"I": 0.5, "II": 1.0}


def load_export(path: str, mhc_class: str) -> pd.DataFrame:
    """
    Read one IEDB export. The files carry a short preamble before the header
    row, so the header is located by its first column name.
    """
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    try:
        header = next(i for i, line in enumerate(lines) if line.startswith("allele,"))
    except StopIteration:
        raise SystemExit(f"No header row found in {path}")

    # The preamble lines are padded with the CSV's trailing commas.
    method = next((line.split(":", 1)[1].strip().rstrip(",").strip()
                   for line in lines[:header] if line.lower().startswith("method used")), "unknown")

    df = pd.read_csv(io.StringIO("\n".join(lines[header:])))
    df["mhc_class"] = mhc_class
    df["method"] = method
    df["source_file"] = Path(path).name
    return df


def load_all() -> pd.DataFrame:
    frames = [load_export(p, "I") for p in sorted(glob.glob(MHC_I_GLOB))]
    frames += [load_export(p, "II") for p in sorted(glob.glob(MHC_II_GLOB))]
    if not frames:
        raise SystemExit(f"No IEDB exports found under {PRED_DIR}")

    df = pd.concat(frames, ignore_index=True)
    df["ic50"] = pd.to_numeric(df["ic50"], errors="coerce")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")

    dropped = df["ic50"].isna().sum() + df["rank"].isna().sum()
    df = df.dropna(subset=["ic50", "rank"])
    if dropped:
        print(f"  note: {dropped} row(s) dropped for unparseable ic50 or rank")
    return df


def strong_binders(df: pd.DataFrame) -> pd.DataFrame:
    keep = pd.Series(False, index=df.index)
    for cls, rank_cutoff in RANK_CUTOFF.items():
        keep |= ((df["mhc_class"] == cls)
                 & (df["ic50"] < IC50_CUTOFF)
                 & (df["rank"] < rank_cutoff))
    return df[keep]


def main():
    print("=" * 55)
    print("SELECTIVITY VERIFICATION")
    print("=" * 55)

    df = load_all()
    sb = strong_binders(df)

    by_class = df.groupby("mhc_class").size().to_dict()
    sb_by_class = sb.groupby("mhc_class").size().to_dict()
    methods = sorted(df["method"].unique())

    print(f"\nPrediction methods    : {', '.join(methods)}")
    print(f"Alleles               : {df['allele'].nunique()}")
    print(f"Unique peptides       : {df['peptide'].nunique()}")
    print(f"Total predictions     : {len(df)}")
    print(f"  MHC-I               : {by_class.get('I', 0)}")
    print(f"  MHC-II              : {by_class.get('II', 0)}")

    print(f"\nStrong binders        : {len(sb)}")
    print(f"  MHC-I  (IC50<{IC50_CUTOFF:g} nM, rank<{RANK_CUTOFF['I']}%) : {sb_by_class.get('I', 0)}")
    print(f"  MHC-II (IC50<{IC50_CUTOFF:g} nM, rank<{RANK_CUTOFF['II']}%) : {sb_by_class.get('II', 0)}")
    print(f"  Unique peptides     : {sb['peptide'].nunique()}")
    print(f"\nSelectivity rate      : {100 * len(sb) / len(df):.3f}% of predictions")

    out = PRED_DIR / "processed_results" / "verified_strong_binders.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    sb.sort_values(["mhc_class", "ic50"]).to_csv(out, index=False)
    print(f"\nStrong binders written to {out}")

    print("\nNote: this reports where the selected peptides sit within the")
    print("prediction distribution. It is a description of threshold stringency,")
    print("not a test of the scoring function against negatives. For that, see")
    print("src/decoy_benchmark.py, which requires IEDB predictions for")
    print("composition-matched decoys.")


if __name__ == "__main__":
    main()
