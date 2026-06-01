#!/usr/bin/env python3
"""
Epitope Scoring — Hardened Scoring Function
============================================

Revised scoring with:
- Log10-scale IC50 (biologically appropriate for nM range)
- Human proteome homology penalty (autoimmunity safeguard)
- Cysteine penalty (expression/aggregation safeguard)
- Allele diversity soft penalty (prevents same-allele redundancy)
- Returns (score, reason) tuple for full traceability
"""

import numpy as np
from scipy.spatial.distance import hamming


def cysteine_penalty(epitope_seq: str) -> float:
    """
    Hard-exclude epitopes containing free cysteines.
    Free Cys in unstructured chimeric constructs causes intermolecular
    disulfide bond formation during expression -> aggregation.

    This is why VLSFELLHAPATVCG (top MHC-II binder, 4.06nM) was excluded
    from v3. The exclusion was correct but previously undocumented.
    A Cys->Ser substitution is proposed for v4 to restore DRB1*01:01 coverage.

    Note: FPNITNLCPF (in v3) also contains Cys — documented in FLAG_01.
    Do not remove from v3 sequence retroactively; fix in v4 scorer.

    Returns 0.0 (hard exclude) if Cys present, 1.0 if clean.
    """
    return 0.0 if 'C' in epitope_seq.upper() else 1.0


def human_proteome_penalty(epitope_seq: str, human_proteome_seqs: list,
                           similarity_threshold: float = 0.6) -> float:
    """
    Hard-exclude epitopes with high homology to human proteome.
    Returns 0.0 (exclude) or 1.0 (pass).
    Prevents autoimmunity risk candidates from passing filter.
    """
    for human_seq in human_proteome_seqs:
        if len(human_seq) >= len(epitope_seq):
            for i in range(len(human_seq) - len(epitope_seq) + 1):
                window = human_seq[i:i + len(epitope_seq)]
                similarity = 1 - hamming(list(epitope_seq), list(window))
                if similarity >= similarity_threshold:
                    return 0.0
    return 1.0


def allele_diversity_penalty(candidate_allele: str,
                              already_selected_alleles: list,
                              max_per_allele: int = 1) -> float:
    """
    Soft penalty for same-allele repeat selection.

    Root cause of v3 MHC-II redundancy: both selected MHC-II epitopes
    target DRB1*15:01, sharing a 9-mer overlap (QTLLALHRS).
    DRB1*01:01 coverage is zero in v3 as a result.

    This penalty fires on the second candidate targeting the same allele.
    Not a hard exclude — allows same-allele selection only if no
    alternatives meet threshold. Set max_per_allele=1 for standard runs.

    Returns:
        1.0 — first epitope for this allele (no penalty)
        0.5 — second epitope for same allele (soft penalty)
        0.1 — third+ for same allele (strong deterrent)
    """
    count = already_selected_alleles.count(candidate_allele)
    if count == 0:
        return 1.0
    elif count == 1:
        return 0.5
    else:
        return 0.1


def combined_score(ic50: float, rank: float, population_weight: float,
                   epitope_seq: str, human_proteome_seqs: list,
                   already_selected_alleles: list = None,
                   candidate_allele: str = None) -> tuple:
    """
    Hardened scoring with log-scale IC50, cysteine penalty, homology penalty,
    and allele diversity soft penalty.

    Args:
        ic50: Binding affinity in nM
        rank: Percentile rank (0-100)
        population_weight: HLA allele population frequency weight (0-1)
        epitope_seq: Amino acid sequence string
        human_proteome_seqs: List of human protein sequences for homology check
        already_selected_alleles: List of HLA alleles already chosen (for diversity)
        candidate_allele: HLA allele for this candidate

    Returns:
        (float, str): (score, reason)
            score=0.0 with reason string for excluded candidates
            score>0.0 with reason='SCORED' for viable candidates
    """
    # Hard excludes first
    if cysteine_penalty(epitope_seq) == 0.0:
        return 0.0, 'EXCLUDED_FREE_CYSTEINE'

    penalty = human_proteome_penalty(epitope_seq, human_proteome_seqs)
    if penalty == 0.0:
        return 0.0, 'EXCLUDED_HOMOLOGY'

    if ic50 <= 0 or rank <= 0:
        return 0.0, 'EXCLUDED_INVALID_INPUT'

    # Allele diversity soft penalty
    diversity = 1.0
    if already_selected_alleles is not None and candidate_allele is not None:
        diversity = allele_diversity_penalty(candidate_allele, already_selected_alleles)

    log_ic50 = np.log10(ic50)
    if log_ic50 <= 0:
        log_ic50 = 0.001  # Prevent division by zero for sub-1nM values

    score = (1 / log_ic50) * (1 / rank) * population_weight * penalty * diversity
    return score, 'SCORED'


def load_human_proteome(fasta_path: str) -> list:
    """
    Load human proteome sequences from UniProt FASTA (UP000005640).
    Returns list of sequence strings.
    """
    sequences = []
    current_seq = []
    try:
        with open(fasta_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_seq:
                        sequences.append(''.join(current_seq))
                    current_seq = []
                else:
                    current_seq.append(line)
        if current_seq:
            sequences.append(''.join(current_seq))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Human proteome FASTA not found at {fasta_path}. "
            "Download UniProt UP000005640 reviewed set and place at data/reference/human_proteome.fasta"
        )
    return sequences
