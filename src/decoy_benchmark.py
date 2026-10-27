#!/usr/bin/env python3
"""
Decoy Benchmark: Selectivity Validation
========================================

Tests whether the scoring function separates real epitopes from
composition-matched decoys, using MHC binding predictions obtained the same
way for both sets.

CORRECTED 2026-10-27
--------------------
The earlier version of this script assigned decoy IC50 and percentile rank
values by drawing from np.random.uniform over a "non-binder" range, while the
real epitopes kept their true NetMHCpan values. Because combined_score() is a
deterministic function of IC50 and rank, that guaranteed separation before the
KS test ran: the test measured how the inputs had been assigned, not how the
scoring function performs. The shuffled sequences never reached the score at
all. Any KS p-value produced that way (including the 6.87e-24 previously
reported) is not evidence of selectivity and must not be cited.

This version never invents binding values. Decoys must be submitted to IEDB
and their predictions read back before the test will run.

Usage
-----
    # Stage 1 — generate composition-matched decoys for submission
    python src/decoy_benchmark.py --generate

    # Submit results/decoy_candidates.fasta to the IEDB Analysis Resource
    # (same alleles, methods and settings as the real candidate run), then save
    # the export to results/decoy_iedb_predictions.csv

    # Stage 2 — score both sets and run the KS test
    python src/decoy_benchmark.py --analyze
"""

import argparse
import random
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from scoring import combined_score

RESULTS = Path("results")
DECOY_FASTA = RESULTS / "decoy_candidates.fasta"
DECOY_PREDICTIONS = RESULTS / "decoy_iedb_predictions.csv"
SCORES_CSV = RESULTS / "decoy_scores.csv"
FIGURE = RESULTS / "selectivity_benchmark.png"

DECOYS_PER_EPITOPE = 100
SEED = 42

# Real pipeline epitopes with their NetMHCpan predictions.
# (sequence, ic50_nM, percentile_rank, population_weight)
REAL_EPITOPES = [
    ("RLFRKSNLK",       4.82,  0.01, 0.80),
    ("LPFNDGVYF",       4.12,  0.02, 0.75),
    ("FPNITNLCPF",      5.40,  0.02, 0.75),
    ("YLQPRTFLL",       4.30,  0.03, 0.85),
    ("VASQSIIAY",       7.81,  0.02, 0.75),
    ("LYNSASFSTF",      8.16,  0.02, 0.70),
    ("VLSFELLHAPATVCG", 4.06,  0.31, 0.70),
    ("QTLLALHRSYLTPGD", 9.87,  0.15, 0.72),
    ("INITRFQTLLALHRS", 11.23, 0.20, 0.68),
    ("QTLLALHRSYLT",    45.82, 0.14, 0.65),
]

# Column names accepted from an IEDB export, in priority order.
IC50_COLUMNS = ["ic50", "affinity(nm)", "affinity", "score", "ic50(nm)"]
RANK_COLUMNS = ["percentile_rank", "percentile rank", "rank", "adjusted_rank"]
PEPTIDE_COLUMNS = ["peptide", "sequence", "epitope", "peptide_sequence"]


def generate_decoys(real_epitopes, decoys_per_epitope=DECOYS_PER_EPITOPE, seed=SEED):
    """
    Shuffle each real epitope to produce composition-matched decoys.

    Amino acid composition is preserved exactly; the order, and therefore any
    binding motif, is destroyed. Shuffles identical to the source peptide or to
    any other real epitope are rejected, as are duplicates.
    """
    rng = random.Random(seed)
    real_set = {seq for seq, *_ in real_epitopes}
    decoys = []
    seen = set()

    for seq, _ic50, _rank, pop_weight in real_epitopes:
        made = 0
        attempts = 0
        while made < decoys_per_epitope and attempts < decoys_per_epitope * 50:
            attempts += 1
            shuffled = "".join(rng.sample(seq, len(seq)))
            if shuffled == seq or shuffled in real_set or shuffled in seen:
                continue
            seen.add(shuffled)
            decoys.append({"decoy": shuffled, "parent": seq, "population_weight": pop_weight})
            made += 1
        if made < decoys_per_epitope:
            print(f"  warning: {seq} yielded only {made} unique decoys "
                  f"({len(set(seq))} distinct residues limits the permutations)")

    return decoys


def write_fasta(decoys, path=DECOY_FASTA):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w") as fh:
        for i, d in enumerate(decoys, 1):
            fh.write(f">decoy_{i:04d}|parent={d['parent']}\n{d['decoy']}\n")
    pd.DataFrame(decoys).to_csv(path.with_suffix(".csv"), index=False)


def _pick_column(df, candidates, kind):
    lower = {c.lower().strip(): c for c in df.columns}
    for want in candidates:
        if want in lower:
            return lower[want]
    raise SystemExit(
        f"Could not find a {kind} column in {DECOY_PREDICTIONS}.\n"
        f"  Looked for: {', '.join(candidates)}\n"
        f"  Found: {', '.join(df.columns)}\n"
        f"Rename the column in the export and re-run."
    )


def load_decoy_predictions(path=DECOY_PREDICTIONS):
    """
    Read IEDB predictions for the decoy set.

    Binding values must come from the same prediction method and allele panel
    used for the real candidates. This function never substitutes a value.
    """
    if not path.exists():
        raise SystemExit(
            f"{path} not found.\n\n"
            "Stage 2 needs real IEDB predictions for the decoys. Run:\n"
            "    python src/decoy_benchmark.py --generate\n"
            f"then submit {DECOY_FASTA} to the IEDB Analysis Resource using the same\n"
            "alleles, prediction method and peptide lengths as the real candidate run,\n"
            f"and save the export as {path}.\n\n"
            "The benchmark will not run on synthetic binding values."
        )

    df = pd.read_csv(path)
    pep_col = _pick_column(df, PEPTIDE_COLUMNS, "peptide")
    ic50_col = _pick_column(df, IC50_COLUMNS, "IC50")
    rank_col = _pick_column(df, RANK_COLUMNS, "percentile rank")

    weights = {}
    meta_path = DECOY_FASTA.with_suffix(".csv")
    if meta_path.exists():
        meta = pd.read_csv(meta_path)
        weights = dict(zip(meta["decoy"], meta["population_weight"]))

    rows = []
    for _, r in df.iterrows():
        seq = str(r[pep_col]).strip().upper()
        try:
            ic50 = float(r[ic50_col])
            rank = float(r[rank_col])
        except (TypeError, ValueError):
            continue
        if not np.isfinite(ic50) or not np.isfinite(rank):
            continue
        rows.append((seq, ic50, rank, weights.get(seq, 0.75)))

    if not rows:
        raise SystemExit(f"No usable rows parsed from {path}.")
    return rows


def score_set(entries):
    """Score (seq, ic50, rank, weight) tuples, dropping hard-excluded candidates."""
    scored, excluded = [], []
    for seq, ic50, rank, weight in entries:
        score, reason = combined_score(ic50, rank, weight, seq, [])
        if reason == "SCORED":
            scored.append((seq, score))
        else:
            excluded.append((seq, reason))
    return scored, excluded


def plot(real_scores, decoy_scores, ks_stat, p_value, path=FIGURE):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.hist(decoy_scores, bins=50, alpha=0.6, color="gray",
             label=f"Decoys (n={len(decoy_scores)})")
    ax1.hist(real_scores, bins=20, alpha=0.8, color="steelblue",
             label=f"Real epitopes (n={len(real_scores)})")
    ax1.set_xlabel("Combined score")
    ax1.set_ylabel("Count")
    ax1.set_title("Score distribution")
    ax1.legend()
    ax1.text(0.62, 0.88, f"KS p={p_value:.2e}", transform=ax1.transAxes,
             bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7), fontsize=10)

    thresholds = np.linspace(0, max(real_scores + decoy_scores), 200)
    tpr = [np.mean(np.array(real_scores) >= t) for t in thresholds]
    fpr = [np.mean(np.array(decoy_scores) >= t) for t in thresholds]
    ax2.plot(fpr, tpr, color="steelblue", lw=2, label="Scoring function")
    ax2.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random")
    ax2.set_xlabel("False positive rate (decoys)")
    ax2.set_ylabel("True positive rate (real epitopes)")
    ax2.set_title("Selectivity")
    ax2.legend()

    plt.suptitle(f"Epitope scoring selectivity — KS stat={ks_stat:.3f}, p={p_value:.2e}")
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def cmd_generate():
    print("=" * 55)
    print("DECOY BENCHMARK — STAGE 1: GENERATE")
    print("=" * 55)
    decoys = generate_decoys(REAL_EPITOPES)
    write_fasta(decoys)
    print(f"\nReal epitopes : {len(REAL_EPITOPES)}")
    print(f"Decoys written: {len(decoys)}  ->  {DECOY_FASTA}")
    print(f"Metadata      : {DECOY_FASTA.with_suffix('.csv')}")
    print("\nNext: submit the FASTA to the IEDB Analysis Resource with the same")
    print("alleles, method and peptide lengths as the real candidate run, then save")
    print(f"the export as {DECOY_PREDICTIONS} and run --analyze.")


def cmd_analyze():
    print("=" * 55)
    print("DECOY BENCHMARK — STAGE 2: ANALYZE")
    print("=" * 55)

    decoy_entries = load_decoy_predictions()
    real_scored, real_excluded = score_set(REAL_EPITOPES)
    decoy_scored, decoy_excluded = score_set(decoy_entries)

    real_scores = [s for _, s in real_scored]
    decoy_scores = [s for _, s in decoy_scored]

    if not real_scores or not decoy_scores:
        raise SystemExit("One of the sets is empty after scoring; cannot run the test.")

    print(f"\nReal epitopes scored : {len(real_scores)} "
          f"({len(real_excluded)} hard-excluded)")
    print(f"Decoys scored        : {len(decoy_scores)} "
          f"({len(decoy_excluded)} hard-excluded)")
    print(f"\nReal  — mean {np.mean(real_scores):.3f}, "
          f"min {np.min(real_scores):.3f}, max {np.max(real_scores):.3f}")
    print(f"Decoy — mean {np.mean(decoy_scores):.3f}, "
          f"min {np.min(decoy_scores):.3f}, max {np.max(decoy_scores):.3f}")

    ks_stat, p_value = stats.ks_2samp(real_scores, decoy_scores)

    RESULTS.mkdir(exist_ok=True)
    pd.DataFrame(
        [(s, sc, "real") for s, sc in real_scored] +
        [(s, sc, "decoy") for s, sc in decoy_scored],
        columns=["sequence", "score", "type"],
    ).to_csv(SCORES_CSV, index=False)
    plot(real_scores, decoy_scores, ks_stat, p_value)

    print(f"\nScores : {SCORES_CSV}")
    print(f"Figure : {FIGURE}")
    print(f"\nKS test: stat={ks_stat:.4f}, p={p_value:.4e}")
    if p_value < 0.01:
        print("[PASS] Real epitopes separate from composition-matched decoys (p < 0.01).")
    else:
        print("[FAIL] No separation at p < 0.01. The scoring function does not")
        print("       distinguish real epitopes from shuffled sequences; the")
        print("       selectivity claim cannot be made.")
    return ks_stat, p_value


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true",
                       help="write composition-matched decoys for IEDB submission")
    group.add_argument("--analyze", action="store_true",
                       help="score both sets from real predictions and run the KS test")
    args = parser.parse_args()

    if args.generate:
        cmd_generate()
    else:
        cmd_analyze()


if __name__ == "__main__":
    main()
