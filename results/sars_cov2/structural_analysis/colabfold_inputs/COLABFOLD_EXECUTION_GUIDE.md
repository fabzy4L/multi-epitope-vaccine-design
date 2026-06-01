# ColabFold Execution Guide

## Overview
ColabFold provides free access to AlphaFold2 and ChimeraX for protein structure prediction.

## Setup Instructions

### Step 1: Access ColabFold
**URL**: https://colab.research.google.com/github/deepmind/alphafold/blob/main/notebooks/AlphaFold.ipynb
**Alternative**: https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb

### Step 2: Sequence Submission
For each construct:
- Upload `version_1_standard_colabfold.fasta`
- Upload `version_2_alternating_colabfold.fasta`
- Upload `version_3_optimized_colabfold.fasta`

### Step 3: Prediction Parameters
**Recommended Settings:**
- **Model**: AlphaFold2 (highest accuracy)
- **MSA Mode**: MMseqs2 (default, good balance)
- **Number of Models**: 5 (for confidence assessment)
- **Ranking Method**: confidence (pLDDT scores)

### Step 4: Results Download
For each construct, download:
- **Best model PDB file**: `*_unrelaxed_rank_001_*.pdb`
- **Confidence scores**: `*_scores_rank_001_*.json`
- **MSA visualization**: For assessment of template coverage

### Step 5: Quality Assessment
**pLDDT Score Interpretation:**
- **pLDDT > 90**: Very high confidence (experimental accuracy)
- **pLDDT 70-90**: Confident (generally correct backbone)
- **pLDDT 50-70**: Low confidence (may be correct)
- **pLDDT < 50**: Very low confidence (likely incorrect)

## Expected Results
Multi-epitope constructs typically show:
- **High confidence** in individual epitope regions
- **Lower confidence** in linker regions (expected flexibility)
- **Variable confidence** depending on epitope structural context

