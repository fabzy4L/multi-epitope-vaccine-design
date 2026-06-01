#!/usr/bin/env python3
"""
Phase 9C — Antigenicity and Allergenicity Assessment
======================================================
VaxiJen v2.0  — antigenicity score (target: virus, threshold 0.4)
AllerTop v2.0 — allergenicity classification (ALLERGEN / NON-ALLERGEN)

Both are manual web submissions. This script:
  1. Prints the submission-ready sequence and exact steps
  2. Records your results when you pass them as arguments
  3. Generates a JSON report + pass/fail summary

Usage
-----
# Step 1 — print sequence and submission instructions
python src/antigenicity.py

# Step 2 — after web submissions, record results
python src/antigenicity.py --vaxijen 0.5476 --allergop NON-ALLERGEN

# Both flags required to generate the full report.

Servers
-------
VaxiJen v2.0 : http://www.ddg-pharmfac.net/vaxijen/VaxiJen/VaxiJen.html
AllerTop v2.0: http://www.ddg-pharmfac.net/AllerTop/
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

V3_1_SEQUENCE = (
    "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD"
    "GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK"
    "AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
)

FASTA = f">v3_1_single_kk\n{V3_1_SEQUENCE}"

VAXIJEN_THRESHOLD = 0.4   # standard virus threshold


def print_instructions():
    print("=" * 60)
    print("PHASE 9C — ANTIGENICITY & ALLERGENICITY SUBMISSION")
    print("=" * 60)

    print("""
STEP 1 — VaxiJen v2.0 (antigenicity)
  URL:       http://www.ddg-pharmfac.net/vaxijen/VaxiJen/VaxiJen.html
  Sequence:  paste FASTA below
  Target:    Virus
  Threshold: 0.4
  Result:    note the numeric score (e.g. 0.5476)
""")
    print(FASTA)

    print("""
STEP 2 — AllerTop v2.0 (allergenicity)
  URL:       http://www.ddg-pharmfac.net/AllerTop/
  Sequence:  paste FASTA below (same sequence)
  Result:    note ALLERGEN or NON-ALLERGEN
""")
    print(FASTA)

    print("""
STEP 3 — Record results
  python src/antigenicity.py --vaxijen <score> --allergop <ALLERGEN|NON-ALLERGEN>

  Example:
  python src/antigenicity.py --vaxijen 0.5476 --allergop NON-ALLERGEN
""")


def assess_vaxijen(score: float) -> dict:
    predicted_antigen = score >= VAXIJEN_THRESHOLD
    return {
        "score":             round(score, 4),
        "threshold":         VAXIJEN_THRESHOLD,
        "predicted_antigen": predicted_antigen,
        "verdict":           "PROBABLE_ANTIGEN" if predicted_antigen else "NON-ANTIGEN",
        "interpretation": (
            f"Score {score:.4f} ≥ {VAXIJEN_THRESHOLD} threshold — "
            "predicted to induce immune response"
            if predicted_antigen else
            f"Score {score:.4f} < {VAXIJEN_THRESHOLD} threshold — "
            "weak antigenicity predicted; consider adjuvant optimization"
        ),
    }


def assess_allergop(result: str) -> dict:
    is_allergen = result.upper() == "ALLERGEN"
    return {
        "prediction":       result.upper(),
        "is_allergen":      is_allergen,
        "verdict":          "FAIL" if is_allergen else "PASS",
        "interpretation": (
            "Predicted ALLERGEN — potential cross-reactivity risk; "
            "experimental allergenicity testing required before clinical use"
            if is_allergen else
            "Predicted NON-ALLERGEN — no allergenic cross-reactivity detected; "
            "acceptable for therapeutic development"
        ),
    }


def synthesis_cleared(vaxijen: dict, allergop: dict) -> bool:
    return vaxijen["predicted_antigen"] and not allergop["is_allergen"]


def generate_report(vaxijen_score: float, allergop_result: str) -> dict:
    vj = assess_vaxijen(vaxijen_score)
    at = assess_allergop(allergop_result)
    cleared = synthesis_cleared(vj, at)

    report = {
        "construct_id":  "v3_1_single_kk",
        "sequence_length": len(V3_1_SEQUENCE),
        "vaxijen": vj,
        "allergop": at,
        "overall": {
            "cleared":      cleared,
            "gate":         "CLEARED" if cleared else "REVIEW_REQUIRED",
            "summary": (
                f"VaxiJen {vj['verdict']} (score {vj['score']}) — "
                f"AllerTop {at['prediction']} — "
                f"Gate {'CLEARED' if cleared else 'BLOCKED'}"
            ),
        },
    }

    out = ROOT / "results" / "antigenicity_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("PHASE 9C — ANTIGENICITY REPORT")
    print("=" * 60)
    print(f"\nVaxiJen score:   {vj['score']}  ({vj['verdict']})")
    print(f"  {vj['interpretation']}")
    print(f"\nAllerTop:        {at['prediction']}  ({at['verdict']})")
    print(f"  {at['interpretation']}")
    print(f"\nOverall gate:    {report['overall']['gate']}")
    print(f"Report saved:    {out}")

    if cleared:
        print("\n  Add to manuscript methods:")
        print(f"  The v3.1 construct returned a VaxiJen antigenicity score of "
              f"{vj['score']} (threshold 0.4, target: virus), indicating probable "
              f"antigenicity. AllerTop v2.0 predicted NON-ALLERGEN, supporting "
              f"safety for therapeutic development.")
    else:
        issues = []
        if not vj["predicted_antigen"]:
            issues.append(f"low VaxiJen score ({vj['score']})")
        if at["is_allergen"]:
            issues.append("AllerTop ALLERGEN prediction")
        print(f"\n  Review required: {', '.join(issues)}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Record VaxiJen + AllerTop results for v3.1 vaccine construct"
    )
    parser.add_argument("--vaxijen",  type=float, metavar="SCORE",
                        help="VaxiJen antigenicity score (e.g. 0.5476)")
    parser.add_argument("--allergop", type=str,   metavar="RESULT",
                        help="AllerTop result: ALLERGEN or NON-ALLERGEN")
    args = parser.parse_args()

    if args.vaxijen is None and args.allergop is None:
        print_instructions()
        return

    if args.vaxijen is None or args.allergop is None:
        print("Error: provide both --vaxijen and --allergop together.")
        print("Run without arguments to see submission instructions.")
        sys.exit(1)

    if args.allergop.upper() not in ("ALLERGEN", "NON-ALLERGEN"):
        print("Error: --allergop must be ALLERGEN or NON-ALLERGEN")
        sys.exit(1)

    generate_report(args.vaxijen, args.allergop)


if __name__ == "__main__":
    main()
