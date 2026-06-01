#!/usr/bin/env python3
"""
Epitope Scoring — Hardened Scoring Function
============================================

Revised scoring with:
- Log10-scale IC50 (biologically appropriate for nM range)
- Human proteome homology penalty (autoimmunity safeguard)
- Hard-exclude for sequences with >60% similarity to human proteins
"""

import numpy as np
from scipy.spatial.distance import hamming


def human_proteome_penalty(epitope_seq: str, human_proteome_seqs: list, similarity_threshold: float = 0.6) -> float:
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


def combined_score(ic50: float, rank: float, population_weight: float,
                   epitope_seq: str, human_proteome_seqs: list) -> float:
    """
    Revised scoring with log-scale IC50 and autoimmunity penalty.

    Args:
        ic50: Binding affinity in nM
        rank: Percentile rank (0-100)
        population_weight: HLA allele population frequency weight (0-1)
        epitope_seq: Amino acid sequence string
        human_proteome_seqs: List of human protein sequences for homology check

    Returns:
        float: Combined score (0.0 = hard excluded, >0 = viable)
    """
    penalty = human_proteome_penalty(epitope_seq, human_proteome_seqs)
    if penalty == 0.0:
        return 0.0  # Hard exclude — autoimmunity risk

    if ic50 <= 0 or rank <= 0:
        return 0.0

    log_ic50 = np.log10(ic50)
    if log_ic50 <= 0:
        log_ic50 = 0.001  # Prevent division by zero for sub-1nM values

    score = (1 / log_ic50) * (1 / rank) * population_weight * penalty
    return score


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
