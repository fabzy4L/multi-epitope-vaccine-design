# Phase 7B + Phase 8 — Design Flag Fixes + RFdiffusion 16-Design Analysis
# Feed to Claude Code. Execute in order.
# RFdiffusion ZIP will be provided after this plan is fed — Phase 8 waits for it.

---

## CONTEXT

Four design flags identified during construct reconciliation.
RFdiffusion partial diffusion run in progress — 16 designs (not 10).
All Phase 1-7 code intact. Do not modify existing phases.

---

## PHASE 7B — Scorer Hardening: Cysteine + Allele Diversity

### 7B-1: Add cysteine penalty to scoring pipeline

Open `src/scoring.py`. Add this function alongside `human_proteome_penalty`:

```python
def cysteine_penalty(epitope_seq: str) -> float:
    """
    Hard-exclude epitopes containing free cysteines.
    Free Cys in unstructured chimeric constructs causes intermolecular
    disulfide bond formation during expression -> aggregation.
    
    This is why VLSFELLHAPATVCG (top MHC-II binder, 4.06nM) was excluded
    from v3. The exclusion was correct but previously undocumented.
    A Cys->Ser substitution is proposed for v4 to restore DRB1*01:01 coverage.
    
    Returns 0.0 (hard exclude) if Cys present, 1.0 if clean.
    """
    return 0.0 if 'C' in epitope_seq.upper() else 1.0
```

Integrate into `combined_score()` — add alongside homology penalty:

```python
def combined_score(ic50, rank, population_weight, epitope_seq, 
                   human_proteome_seqs, already_selected_alleles=None,
                   candidate_allele=None):
    
    # Hard excludes first
    if cysteine_penalty(epitope_seq) == 0.0:
        return 0.0, 'EXCLUDED_FREE_CYSTEINE'
    
    penalty = human_proteome_penalty(epitope_seq, human_proteome_seqs)
    if penalty == 0.0:
        return 0.0, 'EXCLUDED_HOMOLOGY'
    
    # Allele diversity soft penalty
    diversity = 1.0
    if already_selected_alleles is not None and candidate_allele is not None:
        diversity = allele_diversity_penalty(candidate_allele, 
                                            already_selected_alleles)
    
    if ic50 <= 0 or rank <= 0:
        return 0.0, 'EXCLUDED_INVALID_INPUT'
    
    log_ic50 = np.log10(ic50)
    if log_ic50 <= 0:
        log_ic50 = 0.001
    
    score = (1 / log_ic50) * (1 / rank) * population_weight * penalty * diversity
    return score, 'SCORED'
```

### 7B-2: Add allele diversity penalty

Add to `src/scoring.py`:

```python
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
```

### 7B-3: Update unit tests

Add to the existing test file (Phase 1 tests):

```python
def test_cysteine_penalty():
    # VLSFELLHAPATVCG — contains C at position 13 — must be excluded
    assert cysteine_penalty('VLSFELLHAPATVCG') == 0.0
    # RLFRKSNLK — no cysteine — must pass
    assert cysteine_penalty('RLFRKSNLK') == 1.0
    # FPNITNLCPF — contains C — must be excluded
    assert cysteine_penalty('FPNITNLCPF') == 0.0

def test_allele_diversity_penalty():
    selected = ['DRB1*15:01']
    # First DRB1*01:01 — no penalty
    assert allele_diversity_penalty('DRB1*01:01', selected) == 1.0
    # Second DRB1*15:01 — soft penalty
    assert allele_diversity_penalty('DRB1*15:01', selected) == 0.5
    # Third DRB1*15:01 — strong deterrent
    selected_2 = ['DRB1*15:01', 'DRB1*15:01']
    assert allele_diversity_penalty('DRB1*15:01', selected_2) == 0.1

def test_fpnitnlcpf_now_excluded():
    # FPNITNLCPF was in v3 but contains Cys — should now score 0
    score, reason = combined_score(
        ic50=5.40, rank=0.02, population_weight=1.0,
        epitope_seq='FPNITNLCPF',
        human_proteome_seqs=[],
        already_selected_alleles=[],
        candidate_allele='HLA-B35:01'
    )
    assert score == 0.0
    assert reason == 'EXCLUDED_FREE_CYSTEINE'
```

**Phase 7B pass condition:** All new tests pass. Re-run scoring on original 74 candidates and confirm:
- VLSFELLHAPATVCG returns score=0.0 reason=EXCLUDED_FREE_CYSTEINE
- FPNITNLCPF returns score=0.0 reason=EXCLUDED_FREE_CYSTEINE
- RLFRKSNLK still returns highest positive score

---

## PHASE 7C — ConstructMetadata: Document All Four Flags

Update `src/validation_tier.py`. Add a `known_design_flags` field to ConstructMetadata:

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class DesignFlag:
    flag_id: str
    severity: str          # 'JUSTIFIED' | 'SCORING_ARTIFACT' | 'UNDOCUMENTED_GAP' | 'UNKNOWN_RISK'
    description: str
    paper_action: str      # What goes in the paper
    code_action: str       # What was fixed in code
    blocks_synthesis: bool # True = do not order synthesis until resolved

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
    known_design_flags: List[DesignFlag] = field(default_factory=list)
    structural_notes: Optional[Dict] = None
    
    def synthesis_cleared(self) -> bool:
        """Returns False if any flag blocks synthesis."""
        return not any(f.blocks_synthesis for f in self.known_design_flags)
    
    def validation_label(self) -> str:
        labels = {
            ValidationTier.COMPUTATIONALLY_VERIFIED: 
                "computationally designed construct pending experimental validation",
            ValidationTier.IN_VITRO_CONFIRMED: "in vitro confirmed construct",
            ValidationTier.IN_VIVO_CONFIRMED: "experimentally validated construct"
        }
        return labels[self.validation_tier]
```

Instantiate all four flags on construct_v3:

```python
construct_v3 = ConstructMetadata(
    construct_id="v3_optimized",
    sequence="MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPG...",  # full sequence
    molecular_weight_kda=12.7,
    theoretical_pi=9.89,
    instability_index=0.85,
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=[
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0",
        "IEDB_population_coverage", "AlphaFold2_structural_prediction",
        "decoy_benchmark_KS_p6.87e-24"
    ],
    validation_pending=[
        "NetChop_junction_analysis", "HLA_binding_assay",
        "T_cell_activation_study", "animal_model"
    ],
    known_design_flags=[
        DesignFlag(
            flag_id="FLAG_01_CYS_EXCLUSION",
            severity="JUSTIFIED",
            description=(
                "VLSFELLHAPATVCG (top MHC-II binder, 4.06nM, DRB1*01:01) excluded "
                "due to free cysteine at position 13. Intermolecular disulfide "
                "bond formation risk during expression. Exclusion is correct."
            ),
            paper_action=(
                "Document in methods: VLSFELLHAPATVCG excluded due to Cys13 "
                "aggregation risk. Cys->Ser substitution proposed for v4 to "
                "restore DRB1*01:01 coverage."
            ),
            code_action="cysteine_penalty() added to combined_score() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_02_MHCII_REDUNDANCY",
            severity="SCORING_ARTIFACT",
            description=(
                "Both MHC-II epitopes target DRB1*15:01. 9-mer overlap "
                "(QTLLALHRS) between QTLLALHRSYLTPGD and INITRFQTLLALHRS. "
                "DRB1*01:01 MHC-II coverage is zero in v3. "
                "Diversity penalty did not fire for same-allele repeats."
            ),
            paper_action=(
                "Limitations: v3 MHC-II coverage restricted to DRB1*15:01 "
                "due to scoring artifact. DRB1*01:01 absence acknowledged. "
                "Addressed in v4 design scope."
            ),
            code_action="allele_diversity_penalty() added to combined_score() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_03_HLA_A0201_ABSENT",
            severity="UNDOCUMENTED_GAP",
            description=(
                "HLA-A*02:01 (~30% global frequency) not covered in v3. "
                "YLQPRTFLL did not meet combined scoring threshold. "
                "Most prevalent MHC-I allele globally — absence notable for peer review."
            ),
            paper_action=(
                "Limitations: HLA-A*02:01 coverage absent. YLQPRTFLL identified "
                "in candidate pool but excluded by scoring threshold. "
                "Prioritized for v4."
            ),
            code_action="No code change — documented gap only. Scorer working as designed.",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_04_DOUBLE_KK_JUNCTION",
            severity="UNKNOWN_RISK",
            description=(
                "Sequence reads KKGPGPGKK at MHC-II/MHC-I junction (res ~70-78). "
                "Two KK proteasomal processing separators flanking a GPGPG linker. "
                "Likely manual assembly error. Cleavage impact unknown — "
                "could generate spurious GPGPG fragment or destroy flanking epitope termini."
            ),
            paper_action=(
                "Methods note: KK-GPGPG-KK junction identified at MHC-II/MHC-I "
                "boundary. NetChop cleavage analysis pending. Junction will be "
                "revised to single KK if cleavage probability > 0.7."
            ),
            code_action="NetChop analysis pending — see Phase 8",
            blocks_synthesis=True   # ← BLOCKS SYNTHESIS until NetChop resolves
        ),
    ]
)
```

**Phase 7C pass condition:**
```python
# Synthesis gate check
assert construct_v3.synthesis_cleared() == False  # Double-KK blocks until NetChop done
assert len(construct_v3.known_design_flags) == 4
assert any(f.flag_id == 'FLAG_04_DOUBLE_KK_JUNCTION' and f.blocks_synthesis 
           for f in construct_v3.known_design_flags)
```

---

## PHASE 8 — NetChop Junction Analysis + RFdiffusion 16-Design Analysis

**Two independent sub-phases. Run in parallel — neither depends on the other.**

---

### PHASE 8A — NetChop Double-KK Junction Analysis

NetChop cannot be run via API — submit manually.

**Manual step:**
1. Go to: https://services.healthtech.dtu.dk/services/NetChop-3.1/
2. Paste full v3 sequence:
   MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGDGPGPGINITRFQTLLALHRSKKGPGPGKKLPFNDGVYFAAYRLFRKSNLKAAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
3. Method: C-term 3.0
4. Threshold: 0.5
5. Submit and download/copy the per-residue cleavage scores

Create `/src/netchop_analysis.py`:

```python
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Paste NetChop output here as a list of (residue, aa, score) tuples
# Format from NetChop output table: residue number, amino acid, cleavage score
# Example — replace with actual NetChop output:
NETCHOP_SCORES = [
    # (residue_number, amino_acid, cleavage_score)
    # Paste all 144 rows from NetChop output here
]

CONSTRUCT = (
    "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPG"
    "QTLLALHRSYLTPGD"
    "GPGPG"
    "INITRFQTLLALHRS"
    "KK"
    "GPGPG"
    "KKLPFNDGVYF"
    "AAY"
    "RLFRKSNLK"
    "AAY"
    "FPNITNLCPF"
    "AAY"
    "VLYNSASFSTFK"
    "GGGSPAPAPG"
    "SHHHHHH"
).replace(' ', '').replace('\n', '')

# Junction region of interest: KKGPGPGKK
# Find exact position
KK_GPGPG_KK = "KKGPGPGKK"
junction_start = CONSTRUCT.find("KKGPGPGKK")
junction_end = junction_start + len(KK_GPGPG_KK) - 1

EPITOPE_BOUNDARIES = {
    "INITRFQTLLALHRS_Cterm": CONSTRUCT.find("INITRFQTLLALHRS") + 14,
    "KK_GPGPG_KK_start":     junction_start,
    "KK_GPGPG_KK_end":       junction_end,
    "LPFNDGVYF_Nterm":       CONSTRUCT.find("LPFNDGVYF"),
}


def parse_netchop_output(raw_scores: list) -> np.ndarray:
    """Convert NetChop output rows to per-residue score array."""
    scores = np.zeros(len(CONSTRUCT))
    for res_num, aa, score in raw_scores:
        idx = res_num - 1  # Convert to 0-indexed
        if 0 <= idx < len(CONSTRUCT):
            scores[idx] = float(score)
    return scores


def analyze_junction(cleavage_scores: np.ndarray) -> dict:
    """
    Assess cleavage risk at KKGPGPGKK junction.
    Decision threshold: > 0.7 = redesign required.
    """
    junction_scores = cleavage_scores[junction_start:junction_end+1]
    max_junction = float(np.max(junction_scores))
    mean_junction = float(np.mean(junction_scores))
    
    # Check 3-residue flanks of adjacent epitopes
    initr_cterm = cleavage_scores[EPITOPE_BOUNDARIES["INITRFQTLLALHRS_Cterm"]]
    lpfnd_nterm = cleavage_scores[EPITOPE_BOUNDARIES["LPFNDGVYF_Nterm"]]
    
    redesign_required = max_junction > 0.7
    
    return {
        "junction_sequence": KK_GPGPG_KK,
        "junction_residues": f"{junction_start+1}-{junction_end+1}",
        "max_cleavage_score": round(max_junction, 3),
        "mean_cleavage_score": round(mean_junction, 3),
        "per_residue_scores": junction_scores.tolist(),
        "adjacent_epitope_Cterm_score": round(float(initr_cterm), 3),
        "adjacent_epitope_Nterm_score": round(float(lpfnd_nterm), 3),
        "redesign_required": redesign_required,
        "verdict": (
            "REDESIGN_JUNCTION_TO_SINGLE_KK" if redesign_required
            else "JUNCTION_ACCEPTABLE"
        ),
        "synthesis_gate": (
            "BLOCKED" if redesign_required else "CLEARED"
        )
    }


def plot_netchop_full(cleavage_scores: np.ndarray, output_path: str):
    """Full construct cleavage probability plot with junction highlighted."""
    fig, ax = plt.subplots(figsize=(14, 5), facecolor='#0d0d0d')
    ax.set_facecolor('#0d0d0d')

    residues = np.arange(1, len(cleavage_scores) + 1)
    ax.bar(residues, cleavage_scores, color='#60a5fa', alpha=0.7, width=0.8)
    ax.axhline(0.7, color='#f87171', lw=1.2, linestyle='--',
               label='Redesign threshold (0.7)', alpha=0.8)
    ax.axhline(0.5, color='#facc15', lw=0.8, linestyle='--',
               label='NetChop threshold (0.5)', alpha=0.6)

    # Highlight junction
    ax.axvspan(junction_start+1, junction_end+1,
               alpha=0.3, color='#f87171', label='KK-GPGPG-KK junction')

    ax.set_xlim(1, len(cleavage_scores))
    ax.set_ylim(0, 1.1)
    ax.set_xlabel('Residue Position', color='#cbd5e1', fontsize=11)
    ax.set_ylabel('Cleavage Probability', color='#cbd5e1', fontsize=11)
    ax.set_title('v3_optimized — NetChop C-term 3.0 Cleavage Prediction',
                 color='#f1f5f9', fontsize=12, fontweight='bold')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')
    ax.legend(facecolor='#1e293b', edgecolor='#334155',
              labelcolor='#cbd5e1', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0d0d0d')
    print(f"NetChop figure saved: {output_path}")


def run_netchop_analysis():
    if not NETCHOP_SCORES:
        raise ValueError(
            "NETCHOP_SCORES is empty.\n"
            "Paste NetChop output into the NETCHOP_SCORES list before running."
        )

    cleavage_scores = parse_netchop_output(NETCHOP_SCORES)
    junction_result = analyze_junction(cleavage_scores)

    print("=== Junction Analysis ===")
    print(f"Junction: {junction_result['junction_sequence']} "
          f"(res {junction_result['junction_residues']})")
    print(f"Max cleavage score: {junction_result['max_cleavage_score']}")
    print(f"Verdict: {junction_result['verdict']}")
    print(f"Synthesis gate: {junction_result['synthesis_gate']}")

    plot_netchop_full(cleavage_scores, 'results/netchop/netchop_cleavage_map.png')

    # Write report
    report = {
        "construct_id": "v3_optimized",
        "tool": "NetChop 3.1 C-term 3.0",
        "junction_analysis": junction_result,
        "full_cleavage_scores": cleavage_scores.tolist(),
    }
    with open('results/netchop/netchop_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Update FLAG_04 in construct metadata
    if junction_result['synthesis_gate'] == 'CLEARED':
        print("\nFLAG_04 resolved — update construct_v3.known_design_flags[3].blocks_synthesis = False")
        print("Remove 'NetChop_junction_analysis' from validation_pending")
    else:
        print("\nFLAG_04 unresolved — junction redesign required before synthesis")
        print("Redesign: replace KKGPGPGKK with single KK at MHC-II/MHC-I boundary")

    return report


if __name__ == "__main__":
    run_netchop_analysis()
```

**Phase 8A pass condition:**
```bash
ls results/netchop/netchop_report.json
ls results/netchop/netchop_cleavage_map.png
# Check synthesis gate
python3 -c "
import json
with open('results/netchop/netchop_report.json') as f:
    r = json.load(f)
print('Synthesis gate:', r['junction_analysis']['synthesis_gate'])
print('Verdict:', r['junction_analysis']['verdict'])
"
```

---

### PHASE 8B — RFdiffusion 16-Design Ensemble Analysis

**Wait for ZIP before running this phase.**

When ZIP arrives, extract to `results/rfdiffusion/output/`.

Update `src/rfdiffusion_analysis.py` — change one line:

```python
# Line in analyze_backbone_ensemble() — update expected count
pdb_files = sorted(Path(pdb_dir).glob('*.pdb'))
print(f'Found {len(pdb_files)} RFdiffusion designs')
# No hard assertion on count — 16 expected but handle gracefully
```

Run exactly as Phase 7 specified:
```bash
python src/rfdiffusion_analysis.py
```

Outputs:
- `results/rfdiffusion/ensemble_scores.csv` — 16-row table
- `results/rfdiffusion/ensemble_epitope_confidence.png` — box plot
- `results/rfdiffusion/rfdiffusion_structural_report.json` — go/no-go verdict

**Phase 8B pass condition:**
```bash
python3 -c "
import json
with open('results/rfdiffusion/rfdiffusion_structural_report.json') as f:
    r = json.load(f)
print('Designs analyzed:', r['n_designs'])
print('Viable epitopes:', r['viable_epitopes'])
print('Verdict:', r['global_verdict'])
print('Next step:', r['recommended_next_step'])
"
```

---

## FINAL STATE CHECKLIST

```bash
# 7B — Scorer updates
grep -n "cysteine_penalty" src/scoring.py
grep -n "allele_diversity_penalty" src/scoring.py

# 7B — Tests
python -m pytest tests/ -v  # All tests pass including 3 new ones

# 7C — All 4 flags on construct_v3
python3 -c "
from src.validation_tier import construct_v3
print('Flags:', len(construct_v3.known_design_flags))
print('Synthesis cleared:', construct_v3.synthesis_cleared())
"
# Expected: Flags: 4 | Synthesis cleared: False (until NetChop resolves FLAG_04)

# 8A — NetChop (after manual submission)
ls results/netchop/netchop_report.json

# 8B — RFdiffusion (after ZIP provided)
ls results/rfdiffusion/rfdiffusion_structural_report.json
```

---

## WHAT NOT TO DO

- Do not attempt to redesign the KK junction before NetChop results are in
- Do not remove FPNITNLCPF from the construct sequence retroactively —
  document the scoring change for v4, leave v3 sequence intact for paper
- Do not run ProteinMPNN or AlphaFold validation from the RFdiffusion notebook
- Do not modify Phase 1-7 code
- Do not advance ValidationTier — still COMPUTATIONALLY_VERIFIED
- Phase 8A and 8B are independent — run whichever is ready first
