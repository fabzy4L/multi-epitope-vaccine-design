#!/usr/bin/env python3
"""
Phase 1 Unit Tests — Scoring Function Hardening
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scoring import combined_score, human_proteome_penalty


# ---- Known human peptide (HLA-A signal peptide fragment)
HUMAN_PEPTIDE = "MAVMAPRTL"

# ---- Lead SARS-CoV-2 epitopes from pipeline
RLFRKSNLK = "RLFRKSNLK"   # 4.82nM, rank 0.01%
VLSFELLHAPATVCG = "VLSFELLHAPATVCG"  # 4.06nM, rank 0.31%

# Minimal human proteome mock: just contains the human peptide above
MOCK_HUMAN_PROTEOME = [
    "MAVMAPRTLLLLLSGALALTQTWAGSHSMRYFFTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASQRMEPRAPWIEQEGPEYWDGETRKVKAHSQTHRVDLGTLRGYYNQSEAGSHTVQRMYGCDVGSDWRFLRGYHQYAYDGKDYIALNEDLRSWTAADMAAQTTKHKWEAAHVAEQLRAYLEGTCVEWLRRYLENGKETLQRTDAPKTHMTHHAVSDHEATLRCWALSFYPAEITLTWQRDGEDQTQDTELVETRPAGDGTFQKWAAVVVPSGQEQRYTCHVQHEGLPKPLTLRWEPPPSTVSNMATVAVLVNLSSSMDAATQQHKWEAAHVAEQLRAYLEGTCVEWLRRYLENGKETLQRTDAPKTHMTHHAVSDHEATLRCWALSFYPAEITLTWQRDGEDQTQDTELVETRPAGD"
]


def test_human_peptide_excluded():
    """A known human peptide must score 0.0 (hard excluded)."""
    score = combined_score(
        ic50=5.0, rank=0.01, population_weight=0.8,
        epitope_seq=HUMAN_PEPTIDE,
        human_proteome_seqs=MOCK_HUMAN_PROTEOME
    )
    assert score == 0.0, f"Expected 0.0 for human peptide, got {score}"
    print(f"[PASS] Human peptide hard-excluded: score={score}")


def test_rlfrksnlk_positive():
    """RLFRKSNLK (4.82nM) must return a positive score against non-human proteome."""
    score = combined_score(
        ic50=4.82, rank=0.01, population_weight=0.8,
        epitope_seq=RLFRKSNLK,
        human_proteome_seqs=MOCK_HUMAN_PROTEOME
    )
    assert score > 0.0, f"Expected positive score for RLFRKSNLK, got {score}"
    print(f"[PASS] RLFRKSNLK positive score: {score:.4f}")


def test_sub_1nm_no_division_by_zero():
    """Hypothetical sub-1nM epitope must not raise ZeroDivisionError."""
    try:
        score = combined_score(
            ic50=0.5, rank=0.01, population_weight=0.8,
            epitope_seq="AAAAAAAA",
            human_proteome_seqs=MOCK_HUMAN_PROTEOME
        )
        assert score >= 0.0
        print(f"[PASS] Sub-1nM no division by zero: score={score:.4f}")
    except ZeroDivisionError:
        assert False, "ZeroDivisionError raised for sub-1nM IC50"


def test_log_scale_ordering():
    """Log-scale IC50 must preserve ordering: better affinity = higher score."""
    score_4nm = combined_score(4.0, 0.01, 0.8, "AAAAAAAA", MOCK_HUMAN_PROTEOME)
    score_40nm = combined_score(40.0, 0.01, 0.8, "AAAAAAAA", MOCK_HUMAN_PROTEOME)
    assert score_4nm > score_40nm, "4nM epitope should score higher than 40nM epitope"
    print(f"[PASS] Log-scale ordering preserved: 4nM={score_4nm:.4f} > 40nM={score_40nm:.4f}")


def test_rlfrksnlk_ranks_above_vlsfell():
    """RLFRKSNLK should rank above VLSFELLHAPATVCG based on IC50/rank."""
    score_mhc_i = combined_score(4.82, 0.01, 0.8, RLFRKSNLK, MOCK_HUMAN_PROTEOME)
    score_mhc_ii = combined_score(4.06, 0.31, 0.7, VLSFELLHAPATVCG, MOCK_HUMAN_PROTEOME)
    # MHC-I has better rank (0.01% vs 0.31%), so should score higher
    assert score_mhc_i > score_mhc_ii, \
        f"RLFRKSNLK should outscore VLSFELLHAPATVCG on rank (0.01 vs 0.31): {score_mhc_i:.4f} vs {score_mhc_ii:.4f}"
    print(f"[PASS] RLFRKSNLK ({score_mhc_i:.4f}) ranks above VLSFELLHAPATVCG ({score_mhc_ii:.4f})")


if __name__ == "__main__":
    print("="*55)
    print("PHASE 1 SCORING FUNCTION TESTS")
    print("="*55)
    test_human_peptide_excluded()
    test_rlfrksnlk_positive()
    test_sub_1nm_no_division_by_zero()
    test_log_scale_ordering()
    test_rlfrksnlk_ranks_above_vlsfell()
    print("\n[ALL TESTS PASSED] Phase 1 scoring hardening verified.")
