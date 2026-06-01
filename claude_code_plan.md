# Multi-Epitope Vaccine Pipeline — Hardening Plan
# Feed this directly to Claude Code. Execute phases in order. Do not proceed to next phase until current phase passes all tests.

---

## CONTEXT

Repo: https://github.com/fabzy4L/multi-epitope-vaccine-design
Pipeline: SARS-CoV-2 multi-epitope vaccine design using NetMHCpan-4.1 / NetMHCIIpan-4.0
Language: Python
Status: Computationally complete. Preparing for bioRxiv submission + experimental handoff.

This plan addresses 5 specific technical gaps. Each phase has a clear deliverable and a pass/fail test.
Do not add features outside scope. Do not refactor working code unless a phase explicitly requires it.

---

## PHASE 1 — Scoring Function Hardening
**File to modify:** locate the script containing `Combined_Score` or `combined_score` calculation

### 1A — Add human proteome homology penalty

The current formula:
```
Combined_Score = (1/IC50) × (1/Rank) × Population_Weight
```
Has no autoimmunity safeguard. Add a hard-exclude penalty for epitopes with >60% sequence similarity to the human proteome.

Implement this function and integrate it into the scoring pipeline:

```python
from scipy.spatial.distance import hamming
import numpy as np

def human_proteome_penalty(epitope_seq, human_proteome_seqs, similarity_threshold=0.6):
    """
    Hard-exclude epitopes with high homology to human proteome.
    Returns 0.0 (exclude) or 1.0 (pass).
    Prevents autoimmunity risk candidates from passing filter.
    """
    for human_seq in human_proteome_seqs:
        if len(human_seq) >= len(epitope_seq):
            for i in range(len(human_seq) - len(epitope_seq)):
                window = human_seq[i:i + len(epitope_seq)]
                similarity = 1 - hamming(list(epitope_seq), list(window))
                if similarity >= similarity_threshold:
                    return 0.0
    return 1.0
```

### 1B — Replace linear IC50 with log-scale

IC50 values span multiple orders of magnitude (nM range). Linear inverse is not biologically appropriate. Use log10:

```python
def combined_score(ic50, rank, population_weight, epitope_seq, human_proteome_seqs):
    """
    Revised scoring with log-scale IC50 and autoimmunity penalty.
    """
    penalty = human_proteome_penalty(epitope_seq, human_proteome_seqs)
    if penalty == 0.0:
        return 0.0  # Hard exclude
    
    if ic50 <= 0 or rank <= 0:
        return 0.0
    
    log_ic50 = np.log10(ic50)
    if log_ic50 <= 0:
        log_ic50 = 0.001  # Prevent division by zero for sub-1nM values
    
    score = (1 / log_ic50) * (1 / rank) * population_weight * penalty
    return score
```

**Human proteome source:** Use UniProt human reviewed proteome FASTA (UP000005640). If not already in repo, download and add to `/data/reference/human_proteome.fasta`.

### 1C — Test

Write a unit test that:
- Confirms a known human peptide (e.g., HLA-A signal peptide) returns score = 0.0
- Confirms RLFRKSNLK (4.82nM, rank 0.01%) returns a positive score
- Confirms sub-1nM hypothetical epitope does not cause division by zero

**Phase 1 pass condition:** All 3 unit tests pass. Re-run top 74 epitopes through revised scorer and confirm rank order is preserved (RLFRKSNLK and VLSFELLHAPATVCG remain top-2).

---

## PHASE 2 — Validation Tier Metadata

**Goal:** Replace hardcoded "validated" language in outputs with a structured metadata system.
**Do not edit the paper text directly — fix the output generation code so reports auto-generate correct language.**

### 2A — Add ValidationTier enum

Create `/src/validation_tier.py`:

```python
from enum import Enum
from dataclasses import dataclass
from typing import List

class ValidationTier(Enum):
    COMPUTATIONALLY_VERIFIED = "computationally_verified"
    IN_VITRO_CONFIRMED = "in_vitro_confirmed"
    IN_VIVO_CONFIRMED = "in_vivo_confirmed"

@dataclass
class ConstructMetadata:
    construct_id: str
    sequence: str
    molecular_weight_kda: float
    theoretical_pi: float
    instability_index: float
    validation_tier: ValidationTier
    validation_methods_completed: List[str]
    validation_pending: List[str]
    
    def validation_label(self) -> str:
        """Returns publication-appropriate language for this construct's status."""
        labels = {
            ValidationTier.COMPUTATIONALLY_VERIFIED: "computationally designed construct pending experimental validation",
            ValidationTier.IN_VITRO_CONFIRMED: "in vitro confirmed construct",
            ValidationTier.IN_VIVO_CONFIRMED: "experimentally validated construct"
        }
        return labels[self.validation_tier]
```

### 2B — Instantiate for all 3 constructs

```python
construct_v3 = ConstructMetadata(
    construct_id="v3_optimized",
    sequence="MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPG...",
    molecular_weight_kda=12.7,
    theoretical_pi=9.89,
    instability_index=0.85,
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=["ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0", "IEDB_population_coverage"],
    validation_pending=["AlphaFold_structural", "HLA_binding_assay", "T_cell_activation_study", "animal_model"]
)
```

### 2C — Update any report generation scripts

Find any script that outputs the word "validated" in a report or summary and replace with `construct.validation_label()`.

**Phase 2 pass condition:** Run report generator. Confirm output contains "computationally designed construct pending experimental validation" — not "validated construct."

---

## PHASE 3 — Decoy Benchmark (Selectivity Validation)

**Goal:** The 0.17% selectivity claim currently has no negative control baseline. This phase generates one.
This becomes a figure in the bioRxiv paper.

### 3A — Generate decoy sequences

```python
import random
import numpy as np
from scipy import stats

def generate_decoy_sequences(real_epitopes: list, n_decoys_per_epitope: int = 100) -> list:
    """
    Shuffle real epitope sequences to generate amino-acid-composition-matched negatives.
    Preserves composition, destroys binding motifs.
    """
    decoys = []
    for epitope in real_epitopes:
        for _ in range(n_decoys_per_epitope):
            shuffled = list(epitope)
            random.shuffle(shuffled)
            decoy = "".join(shuffled)
            if decoy != epitope:  # Exclude identity shuffles
                decoys.append(decoy)
    return decoys
```

### 3B — Score decoys through pipeline

Run all decoy sequences through the same MHC binding prediction and scoring pipeline as real candidates.
Store results in `/results/decoy_scores.csv` with columns: `sequence`, `score`, `type` (real/decoy).

### 3C — Generate selectivity figure

```python
import matplotlib.pyplot as plt

def plot_selectivity_benchmark(real_scores, decoy_scores, output_path):
    """
    Overlapping score distributions: real epitopes vs shuffled decoys.
    Quantifies separation between signal and noise.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Distribution overlap
    ax1.hist(decoy_scores, bins=50, alpha=0.6, label='Decoys (shuffled)', color='gray')
    ax1.hist(real_scores, bins=20, alpha=0.8, label='Selected epitopes', color='steelblue')
    ax1.set_xlabel('Combined Score')
    ax1.set_ylabel('Count')
    ax1.set_title('Score Distribution: Signal vs Noise')
    ax1.legend()
    
    # KS test for statistical separation
    ks_stat, p_value = stats.ks_2samp(real_scores, decoy_scores)
    ax1.text(0.7, 0.9, f'KS p={p_value:.2e}', transform=ax1.transAxes)
    
    # Selectivity ROC-style
    thresholds = np.linspace(0, max(real_scores), 100)
    tpr = [np.mean(np.array(real_scores) >= t) for t in thresholds]
    fpr = [np.mean(np.array(decoy_scores) >= t) for t in thresholds]
    ax2.plot(fpr, tpr, color='steelblue', lw=2)
    ax2.plot([0,1],[0,1], 'k--', alpha=0.3)
    ax2.set_xlabel('False Positive Rate (Decoys)')
    ax2.set_ylabel('True Positive Rate (Real Epitopes)')
    ax2.set_title('Selectivity Benchmark')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    return ks_stat, p_value
```

**Phase 3 pass condition:** KS test p-value < 0.01 (real epitope scores are statistically separated from decoy distribution). If p > 0.01, scoring function needs re-evaluation before claiming 0.17% selectivity.

---

## PHASE 4 — Solubility Pre-screen Before AlphaFold

**Goal:** Flag constructs at risk of insolubility before AlphaFold submission.
High pI (9.89) + specific hydrophobic stretches = potential expression failure.

### 4A — GRAVY score screen

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

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
        "recommendation": "Manual review required before AlphaFold" if risk_flags else "Clear for structural prediction"
    }
```

Run on all 3 constructs. Write results to `/results/solubility_prescreen.json`.

**Phase 4 pass condition:** Report generated for all 3 constructs with explicit `proceed_to_alphafold` flag. Flags do not block pipeline — they inform decisions.

---

## PHASE 5 — Adjuvant Justification (Documentation Only — No Code Change)

**DO NOT change RS09 to a different adjuvant.**

RS09 (TLR4 agonist) is documented for use in peptide subunit vaccines including viral targets because it drives MHC-I cross-presentation for CD8+ T-cell responses — which is the intended mechanism for this construct.

The issue is missing justification in the methods, not wrong adjuvant selection.

Add this comment block to the adjuvant selection section of the pipeline:

```python
# ADJUVANT RATIONALE: RS09 (TLR4 agonist)
# RS09 was selected over TLR7/8/9 agonists for the following reasons:
# 1. Peptide subunit vaccines lack endosomal delivery needed for TLR7/8/9 activation
# 2. RS09 drives cross-presentation via DC activation → CD8+ CTL response
# 3. Precedent: RS09 used in SARS-CoV peptide constructs (Ref: add citation)
# 4. TLR7/8/9 agonists optimized for nucleic acid-based (mRNA/DNA) vaccine formats
# This selection is intentional and immunologically justified for peptide subunit format.
# Reference to add: Ahmad et al., or equivalent RS09 peptide vaccine paper
```

Find and add one citation supporting RS09 use in a viral peptide subunit vaccine context.

**Phase 5 pass condition:** Comment block present in code. One supporting citation added to README references section.

---

## FINAL CHECKLIST BEFORE BIOARXIV SUBMISSION

Run this after all phases complete:

```bash
# 1. Confirm no instance of "validated construct" in any output file
grep -r "validated construct" ./results/ ./reports/ ./README.md

# 2. Confirm scoring function uses log-scale IC50
grep -n "log10" ./src/scoring.py  # or wherever scoring lives

# 3. Confirm decoy benchmark figure exists
ls ./results/selectivity_benchmark.png

# 4. Confirm solubility prescreen JSON exists
ls ./results/solubility_prescreen.json

# 5. Confirm ValidationTier enum imported in main pipeline
grep -rn "ValidationTier" ./src/

# All 5 should return results. Any empty = phase incomplete.
```

---

## WHAT NOT TO DO

- Do not add B-cell epitope prediction — out of scope for this iteration
- Do not replace RS09 with another adjuvant
- Do not refactor the IEDB parsing or MHC prediction logic — it's working
- Do not add AlphaFold API calls — that requires manual ColabFold submission, flag for separate task
- Do not add multi-pathogen extension — Phase 5 future directions only
