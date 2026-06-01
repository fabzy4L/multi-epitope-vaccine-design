#!/usr/bin/env python3
"""
Phase 4 — Solubility Pre-screen Before AlphaFold
=================================================

Flags constructs at risk of insolubility before investing in structural prediction.
High pI + hydrophobic stretches = potential expression failure.

Results written to results/solubility_prescreen.json
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from Bio.SeqUtils.ProtParam import ProteinAnalysis
from validation_tier import ALL_CONSTRUCTS


def solubility_prescreen(sequence: str, construct_id: str) -> dict:
    """
    GRAVY score screen before structural prediction investment.
    GRAVY > 0 indicates net hydrophobicity = solubility risk.
    """
    analysis = ProteinAnalysis(sequence)
    gravy = analysis.gravy()
    instability = analysis.instability_index()
    pi = analysis.isoelectric_point()

    # Hydrophobic stretch detection (window of 5+ consecutive hydrophobic residues)
    hydrophobic_aa = set('VILMFYWC')
    max_stretch = 0
    current_stretch = 0
    for aa in sequence:
        if aa in hydrophobic_aa:
            current_stretch += 1
            max_stretch = max(max_stretch, current_stretch)
        else:
            current_stretch = 0

    risk_flags = []
    if gravy > 0:
        risk_flags.append("NET_HYDROPHOBIC")
    if pi > 9.0:
        risk_flags.append("HIGH_PI_EXPRESSION_RISK")
    if max_stretch >= 5:
        risk_flags.append(f"HYDROPHOBIC_STRETCH_{max_stretch}aa")

    return {
        "construct_id": construct_id,
        "gravy_score": round(gravy, 3),
        "theoretical_pi": round(pi, 2),
        "instability_index": round(instability, 2),
        "max_hydrophobic_stretch": max_stretch,
        "risk_flags": risk_flags,
        "proceed_to_alphafold": len(risk_flags) == 0,
        "recommendation": (
            "Manual review required before AlphaFold submission" if risk_flags
            else "Clear for structural prediction"
        ),
    }


def main():
    print("="*55)
    print("PHASE 4 — SOLUBILITY PRE-SCREEN")
    print("="*55)

    results = []
    for construct in ALL_CONSTRUCTS:
        result = solubility_prescreen(construct.sequence, construct.construct_id)
        results.append(result)

        print(f"\nConstruct: {result['construct_id']}")
        print(f"  GRAVY score:        {result['gravy_score']:+.3f}")
        print(f"  Theoretical pI:     {result['theoretical_pi']}")
        print(f"  Instability index:  {result['instability_index']}")
        print(f"  Max hydrophobic stretch: {result['max_hydrophobic_stretch']} aa")
        print(f"  Risk flags:         {result['risk_flags'] if result['risk_flags'] else 'None'}")
        print(f"  Proceed to AlphaFold: {result['proceed_to_alphafold']}")
        print(f"  Recommendation:     {result['recommendation']}")

    output_path = Path("results/solubility_prescreen.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[SAVED] Results written to {output_path}")
    print("[PASS] Phase 4 complete — solubility prescreen generated for all 3 constructs.")
    return results


if __name__ == "__main__":
    main()
