#!/usr/bin/env python3
"""
Scoring Unit Tests — Phase 1 + Phase 7B
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scoring import (
    combined_score, human_proteome_penalty,
    cysteine_penalty, allele_diversity_penalty
)


# ---- Known human peptide (HLA-A signal peptide fragment)
HUMAN_PEPTIDE = "MAVMAPRTL"

# ---- Lead SARS-CoV-2 epitopes from pipeline
RLFRKSNLK = "RLFRKSNLK"          # 4.82nM, rank 0.01%
VLSFELLHAPATVCG = "VLSFELLHAPATVCG"  # 4.06nM, rank 0.31% — contains Cys
FPNITNLCPF = "FPNITNLCPF"        # 5.40nM — contains Cys, present in v3

# Minimal human proteome mock
MOCK_HUMAN_PROTEOME = [
    "MAVMAPRTLLLLLSGALALTQTWAGSHSMRYFFTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASQRMEPRAPWIEQEGPEYWDGETRKVKAHSQTHRVDLGTLRGYYNQSEAGSHTVQRMYGCDVGSDWRFLRGYHQYAYDGKDYIALNEDLRSWTAADMAAQTTKHKWEAAHVAEQLRAYLEGTCVEWLRRYLENGKETLQRTDAPKTHMTHHAVSDHEATLRCWALSFYPAEITLTWQRDGEDQTQDTELVETRPAGDGTFQKWAAVVVPSGQEQRYTCHVQHEGLPKPLTLRWEPPPSTVSNMATVAVLVNLSSSMDAATQQHKWEAAHVAEQLRAYLEGTCVEWLRRYLENGKETLQRTDAPKTHMTHHAVSDHEATLRCWALSFYPAEITLTWQRDGEDQTQDTELVETRPAGD"
]


# ============================================================
# PHASE 1 TESTS (preserved)
# ============================================================

def test_human_peptide_excluded():
    """A known human peptide must score 0.0 (hard excluded)."""
    score, reason = combined_score(
        ic50=5.0, rank=0.01, population_weight=0.8,
        epitope_seq=HUMAN_PEPTIDE,
        human_proteome_seqs=MOCK_HUMAN_PROTEOME
    )
    assert score == 0.0, f"Expected 0.0 for human peptide, got {score}"
    print(f"[PASS] Human peptide hard-excluded: score={score}, reason={reason}")


def test_rlfrksnlk_positive():
    """RLFRKSNLK (4.82nM) must return a positive score against non-human proteome."""
    score, reason = combined_score(
        ic50=4.82, rank=0.01, population_weight=0.8,
        epitope_seq=RLFRKSNLK,
        human_proteome_seqs=MOCK_HUMAN_PROTEOME
    )
    assert score > 0.0, f"Expected positive score for RLFRKSNLK, got {score}"
    assert reason == 'SCORED'
    print(f"[PASS] RLFRKSNLK positive score: {score:.4f}")


def test_sub_1nm_no_division_by_zero():
    """Hypothetical sub-1nM epitope must not raise ZeroDivisionError."""
    try:
        score, reason = combined_score(
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
    score_4nm, _ = combined_score(4.0, 0.01, 0.8, "AAAAAAAA", MOCK_HUMAN_PROTEOME)
    score_40nm, _ = combined_score(40.0, 0.01, 0.8, "AAAAAAAA", MOCK_HUMAN_PROTEOME)
    assert score_4nm > score_40nm, "4nM epitope should score higher than 40nM epitope"
    print(f"[PASS] Log-scale ordering preserved: 4nM={score_4nm:.4f} > 40nM={score_40nm:.4f}")


def test_rlfrksnlk_ranks_above_vlsfell():
    """RLFRKSNLK must outscore VLSFELLHAPATVCG — but VLSF is Cys-excluded first."""
    score_rlfr, reason_rlfr = combined_score(4.82, 0.01, 0.8, RLFRKSNLK, MOCK_HUMAN_PROTEOME)
    score_vlsf, reason_vlsf = combined_score(4.06, 0.31, 0.7, VLSFELLHAPATVCG, MOCK_HUMAN_PROTEOME)
    assert score_rlfr > 0.0
    assert score_vlsf == 0.0 and reason_vlsf == 'EXCLUDED_FREE_CYSTEINE'
    print(f"[PASS] RLFRKSNLK ({score_rlfr:.4f}) > VLSFELLHAPATVCG ({score_vlsf}, {reason_vlsf})")


# ============================================================
# PHASE 7B TESTS
# ============================================================

def test_cysteine_penalty():
    """Cysteine penalty must hard-exclude sequences containing Cys."""
    assert cysteine_penalty('VLSFELLHAPATVCG') == 0.0, "VLSFELLHAPATVCG (Cys13) must be excluded"
    assert cysteine_penalty('RLFRKSNLK') == 1.0, "RLFRKSNLK (no Cys) must pass"
    assert cysteine_penalty('FPNITNLCPF') == 0.0, "FPNITNLCPF (Cys8) must be excluded"
    print("[PASS] cysteine_penalty: VLSFELLHAPATVCG=0.0, RLFRKSNLK=1.0, FPNITNLCPF=0.0")


def test_allele_diversity_penalty():
    """Allele diversity penalty must apply soft penalties for same-allele repeats."""
    selected = ['DRB1*15:01']
    assert allele_diversity_penalty('DRB1*01:01', selected) == 1.0, "First DRB1*01:01 — no penalty"
    assert allele_diversity_penalty('DRB1*15:01', selected) == 0.5, "Second DRB1*15:01 — soft penalty"
    selected_2 = ['DRB1*15:01', 'DRB1*15:01']
    assert allele_diversity_penalty('DRB1*15:01', selected_2) == 0.1, "Third DRB1*15:01 — strong deterrent"
    print("[PASS] allele_diversity_penalty: 1.0 / 0.5 / 0.1 at 0/1/2 repeats")


def test_fpnitnlcpf_now_excluded():
    """FPNITNLCPF was in v3 but contains Cys — must now score 0 with correct reason."""
    score, reason = combined_score(
        ic50=5.40, rank=0.02, population_weight=1.0,
        epitope_seq=FPNITNLCPF,
        human_proteome_seqs=[],
        already_selected_alleles=[],
        candidate_allele='HLA-B*35:01'
    )
    assert score == 0.0, f"Expected 0.0, got {score}"
    assert reason == 'EXCLUDED_FREE_CYSTEINE', f"Expected EXCLUDED_FREE_CYSTEINE, got {reason}"
    print(f"[PASS] FPNITNLCPF excluded: score={score}, reason={reason}")


def test_allele_diversity_in_combined_score():
    """Second same-allele epitope must score lower than first."""
    score_first, _ = combined_score(
        9.87, 0.15, 0.7, "QTLLALHRSYLTPGD", [],
        already_selected_alleles=[],
        candidate_allele='DRB1*15:01'
    )
    score_second, _ = combined_score(
        11.23, 0.20, 0.68, "INITRFQTLLALHRS", [],
        already_selected_alleles=['DRB1*15:01'],
        candidate_allele='DRB1*15:01'
    )
    assert score_first > score_second, \
        f"First allele selection ({score_first:.4f}) must outscore second ({score_second:.4f})"
    print(f"[PASS] Allele diversity in combined_score: first={score_first:.4f} > second={score_second:.4f}")


if __name__ == "__main__":
    print("="*55)
    print("SCORING TESTS — Phase 1 + Phase 7B")
    print("="*55)
    print("\n-- Phase 1 --")
    test_human_peptide_excluded()
    test_rlfrksnlk_positive()
    test_sub_1nm_no_division_by_zero()
    test_log_scale_ordering()
    test_rlfrksnlk_ranks_above_vlsfell()
    print("\n-- Phase 7B --")
    test_cysteine_penalty()
    test_allele_diversity_penalty()
    test_fpnitnlcpf_now_excluded()
    test_allele_diversity_in_combined_score()
    print("\n[ALL TESTS PASSED]")
