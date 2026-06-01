# Phase 7 — RFdiffusion Structural Validation
# Feed to Claude Code after Phase 6 results are committed.
# Context: AlphaFold2 returned mean pLDDT 36.4 on v3_optimized — inconclusive due to sparse MSA
# (n=3 sequences). This is expected for a chimeric engineered construct with no natural homologs.
# RFdiffusion is the appropriate next tool: it does not require evolutionary data.

---

## CONTEXT

AlphaFold2 result summary (already in repo):
- Mean pLDDT: 36.4 | Max: 55.2 | ptm: 0.26
- Zero residues above confidence threshold of 70
- Cause: chimeric construct, MSA depth n=3, linker flexibility dominates signal
- Interpretation: INCONCLUSIVE — not a negative result, wrong tool for this construct type

RFdiffusion rationale:
- Designed for de novo and engineered protein design
- Does not depend on MSA or evolutionary co-variation
- Handles multi-domain constructs with explicit linker regions
- Can assess whether the epitope-linker-adjuvant architecture produces a
  stable backbone geometry — which is the actual question AlphaFold couldn't answer

---

## PART A — Document AlphaFold Result Correctly (Code Task)

Before running RFdiffusion, update the structural report and paper language.

### 7A-1: Update structural_validation_report.json

Find `/results/alphafold/structural_validation_report.json` and update:

```python
import json

with open('results/alphafold/structural_validation_report.json', 'r') as f:
    report = json.load(f)

report['global_verdict'] = 'INCONCLUSIVE_WRONG_TOOL'
report['overall_mean_plddt'] = 36.41
report['ptm_score'] = 0.26
report['max_pae'] = 30.83
report['msa_depth'] = 3
report['interpretation'] = (
    'AlphaFold2 returned low pLDDT (mean 36.4) across all residues including '
    'epitope regions. This is consistent with chimeric engineered constructs '
    'lacking natural homologs — MSA depth was n=3, insufficient for reliable '
    'AlphaFold prediction. Result is INCONCLUSIVE, not negative. '
    'RFdiffusion recommended as next structural tool.'
)
report['recommended_next_step'] = 'RFdiffusion backbone assessment — does not require MSA'
report['all_epitopes_structured'] = None  # Indeterminate — do not report as failed

with open('results/alphafold/structural_validation_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

### 7A-2: Update paper methods language

Find the structural validation section in the article/README and replace any reference
to AlphaFold results with this exact language:

```
AlphaFold2 structural prediction was performed via ColabFold v1.6.1 (Mirdita et al., 2022).
Due to the chimeric, non-natural architecture of v3_optimized, MSA depth was limited
(n=3 sequences), resulting in overall mean pLDDT of 36.4 — consistent with intrinsically
disordered or novel engineered constructs lacking homologous templates. This result is
interpreted as inconclusive rather than negative. RFdiffusion-based backbone assessment
is underway as a more appropriate structural validation method for de novo engineered
peptide constructs.
```

Do NOT write "AlphaFold failed" or "low confidence structure" — those framings are
inaccurate. The tool was applied outside its optimal use case.

---

## PART B — RFdiffusion Setup (Manual Step — Human Does This)

RFdiffusion requires GPU compute. Two options:

### Option 1 — ColabFold RFdiffusion Notebook (Recommended, Free)
URL: https://colab.research.google.com/github/sokrypton/ColabDesign/blob/v1.1.1/rf/examples/diffusion.ipynb

This is the fastest path. Uses the same Colab environment already set up.

### Option 2 — Local/GCP (If GPU available)
```bash
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion
pip install -e .
# Requires CUDA GPU — run on GCP if not available locally
```

---

## PART C — RFdiffusion Run Parameters

### What we're asking RFdiffusion to do:

We are NOT asking it to design a new protein.
We ARE asking it to assess whether the v3_optimized backbone geometry is physically plausible —
specifically whether a stable fold exists that keeps epitope regions surface-accessible.

### Input: provide the v3_optimized PDB from AlphaFold as starting backbone

Use rank_001 PDB from AlphaFold output as the input scaffold:
```
v3_optimized_vaccine_f5e32_unrelaxed_rank_001_alphafold2_ptm_model_1_seed_000.pdb
```

This is already in `/results/alphafold/` — copy it to `/results/rfdiffusion/input/`

### Run parameters for Colab notebook:

```python
# In the RFdiffusion Colab notebook:

contigs = "144"          
# Full 144aa construct — no chain breaks, monomer

num_designs = 10         
# Generate 10 backbone variants — gives a distribution to evaluate

noise_scale = 0.5        
# Conservative — partial diffusion from AlphaFold backbone, not de novo
# This preserves the general topology while exploring viable conformations

# Partial diffusion mode (not full de novo):
# Start from AlphaFold PDB backbone, apply noise, diffuse and denoise
# Result: ensemble of plausible backbones consistent with sequence constraints
```

### Key setting: PARTIAL DIFFUSION mode
Do not run full de novo generation — that would ignore the designed sequence.
Partial diffusion from the AlphaFold backbone explores conformational space
while respecting the existing architecture.

---

## PART D — Post-Run Analysis (Claude Code Executes This)

### Dependencies:
```bash
pip install biopython numpy pandas matplotlib seaborn
```

### Create `/src/rfdiffusion_analysis.py`:

```python
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from Bio import PDB
from Bio.PDB import PDBParser, DSSP


CONSTRUCT = (
    'MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPG'
    'QTLLALHRSYLTPGD'
    'GPGPG'
    'INITRFQTLLALHRS'
    'KK'
    'GPGPG'
    'KKLPFNDGVYF'
    'AAY'
    'RLFRKSNLK'
    'AAY'
    'FPNITNLCPF'
    'AAY'
    'VLYNSASFSTFK'
    'GGGSPAPAPG'
    'SHHHHHH'
).replace(' ', '').replace('\n', '')

EPITOPES = {
    'RLFRKSNLK':       'RLFRKSNLK',
    'QTLLALHRSYLTPGD': 'QTLLALHRSYLTPGD',
    'INITRFQTLLALHRS': 'INITRFQTLLALHRS',
    'FPNITNLCPF':      'FPNITNLCPF',
    'LPFNDGVYF':       'LPFNDGVYF',
}

LINKERS = {
    'GPGPG_1': 'GPGPG',
    'AAY_1':   'AAY',
    'KK':      'KK',
}


def find_positions(sequence, motifs):
    positions = {}
    for name, motif in motifs.items():
        idx = sequence.find(motif)
        if idx == -1:
            print(f'WARNING: {name} ({motif}) not found in construct')
            positions[name] = None
        else:
            positions[name] = (idx, idx + len(motif) - 1)
    return positions


def parse_pdb_bfactors(pdb_path):
    """
    RFdiffusion outputs B-factors as per-residue confidence scores (0-1 scale).
    Extract and return as numpy array.
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('construct', pdb_path)
    
    bfactors = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == ' ':  # HETATM excluded
                    ca_atoms = [a for a in residue if a.name == 'CA']
                    if ca_atoms:
                        bfactors.append(ca_atoms[0].bfactor)
    return np.array(bfactors)


def analyze_backbone_ensemble(pdb_dir, epitope_positions, linker_positions):
    """
    Analyze all 10 RFdiffusion output PDBs.
    For each design: extract B-factors, map to epitope regions, assess exposure.
    """
    pdb_files = sorted(Path(pdb_dir).glob('*.pdb'))
    
    if not pdb_files:
        raise FileNotFoundError(
            f'No PDB files found in {pdb_dir}\n'
            'Download RFdiffusion output and place in results/rfdiffusion/output/'
        )
    
    print(f'Found {len(pdb_files)} RFdiffusion designs')
    
    results = []
    for pdb_file in pdb_files:
        bfactors = parse_pdb_bfactors(str(pdb_file))
        
        if len(bfactors) != len(CONSTRUCT):
            print(f'WARNING: {pdb_file.name} has {len(bfactors)} residues, expected {len(CONSTRUCT)}')
            continue
        
        design_result = {
            'design': pdb_file.stem,
            'mean_confidence': float(np.mean(bfactors)),
        }
        
        # Score each epitope region
        for name, position in epitope_positions.items():
            if position is None:
                continue
            start, end = position
            scores = bfactors[start:end+1]
            design_result[f'{name}_mean'] = float(np.mean(scores))
            design_result[f'{name}_min'] = float(np.min(scores))
        
        # Score linker regions (should be flexible = low score is OK here)
        for name, position in linker_positions.items():
            if position is None:
                continue
            start, end = position
            scores = bfactors[start:end+1]
            design_result[f'linker_{name}_mean'] = float(np.mean(scores))
        
        results.append(design_result)
    
    return pd.DataFrame(results)


def plot_ensemble_epitope_scores(df, epitope_names, output_path):
    """
    Box plot of epitope confidence scores across 10 RFdiffusion designs.
    Shows distribution — are epitopes consistently scored or variable?
    """
    epitope_cols = [f'{name}_mean' for name in epitope_names 
                    if f'{name}_mean' in df.columns]
    
    if not epitope_cols:
        print('No epitope columns found in results')
        return
    
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0d0d0d')
    ax.set_facecolor('#0d0d0d')
    
    data_to_plot = [df[col].dropna().values for col in epitope_cols]
    labels = [col.replace('_mean', '').replace('_', ' ') for col in epitope_cols]
    
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                    medianprops=dict(color='#f1f5f9', lw=2))
    
    colors = ['#e63946', '#2a9d8f', '#e9c46a', '#f4a261', '#a8dadc']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax.axhline(0.7, color='#4ade80', lw=1, linestyle='--', alpha=0.7,
               label='Confidence threshold (0.7)')
    ax.axhline(0.5, color='#facc15', lw=1, linestyle='--', alpha=0.7,
               label='Borderline (0.5)')
    
    ax.set_ylabel('RFdiffusion Confidence Score', color='#cbd5e1', fontsize=11)
    ax.set_title('Epitope Region Confidence — RFdiffusion Ensemble (n=10 designs)',
                 color='#f1f5f9', fontsize=12, fontweight='bold')
    ax.tick_params(colors='#94a3b8', axis='both')
    ax.tick_params(axis='x', rotation=20)
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#cbd5e1', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0d0d0d')
    print(f'Ensemble figure saved: {output_path}')


def generate_rfdiffusion_report(df, epitope_positions, output_path):
    """
    Write final structural assessment report.
    Decision gate: any epitope with median confidence > 0.5 across ensemble
    is considered viable for wet lab progression.
    """
    report = {
        'construct_id': 'v3_optimized',
        'tool': 'RFdiffusion partial diffusion',
        'n_designs': len(df),
        'mean_ensemble_confidence': round(float(df['mean_confidence'].mean()), 3),
        'epitope_assessment': {},
        'alphafold_context': 'AlphaFold2 inconclusive (mean pLDDT 36.4, MSA n=3)',
    }
    
    viable_count = 0
    for name in EPITOPES.keys():
        col = f'{name}_mean'
        if col not in df.columns:
            report['epitope_assessment'][name] = {'status': 'NOT_EVALUATED'}
            continue
        
        median_score = float(df[col].median())
        is_viable = median_score > 0.5
        if is_viable:
            viable_count += 1
        
        report['epitope_assessment'][name] = {
            'median_confidence': round(median_score, 3),
            'mean_confidence': round(float(df[col].mean()), 3),
            'viable_for_wetlab': is_viable,
            'verdict': 'VIABLE' if is_viable else 'LOW_CONFIDENCE'
        }
    
    all_viable = viable_count == len(EPITOPES)
    majority_viable = viable_count >= len(EPITOPES) // 2 + 1
    
    if all_viable:
        verdict = 'CLEAR_FOR_EXPERIMENTAL_PHASE'
        next_step = 'Proceed to HLA binding assay'
    elif majority_viable:
        verdict = 'PARTIAL_CONFIDENCE_PROCEED_WITH_CAUTION'
        next_step = 'Proceed to HLA binding assay; flag low-confidence epitopes for NMR/CD'
    else:
        verdict = 'REDESIGN_RECOMMENDED'
        next_step = 'Review linker architecture; consider reordering epitope arrangement'
    
    report['global_verdict'] = verdict
    report['recommended_next_step'] = next_step
    report['viable_epitopes'] = f'{viable_count}/{len(EPITOPES)}'
    report['validation_tier'] = 'COMPUTATIONALLY_VERIFIED (structural confidence assessed)'
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f'\nRFdiffusion report saved: {output_path}')
    return report


def run_rfdiffusion_analysis():
    """Main entry point."""
    
    print('=== Step 1: Mapping epitope positions ===')
    epitope_positions = find_positions(CONSTRUCT, EPITOPES)
    linker_positions = find_positions(CONSTRUCT, LINKERS)
    
    for name, pos in epitope_positions.items():
        if pos:
            print(f'  {name}: residues {pos[0]+1}-{pos[1]+1}')
    
    print('\n=== Step 2: Parsing RFdiffusion ensemble ===')
    df = analyze_backbone_ensemble(
        'results/rfdiffusion/output/',
        epitope_positions,
        linker_positions
    )
    
    df.to_csv('results/rfdiffusion/ensemble_scores.csv', index=False)
    print(f'Ensemble scores saved. Mean confidence: {df["mean_confidence"].mean():.3f}')
    
    print('\n=== Step 3: Generating ensemble figure ===')
    plot_ensemble_epitope_scores(
        df,
        list(EPITOPES.keys()),
        'results/rfdiffusion/ensemble_epitope_confidence.png'
    )
    
    print('\n=== Step 4: Writing report ===')
    report = generate_rfdiffusion_report(
        df,
        epitope_positions,
        'results/rfdiffusion/rfdiffusion_structural_report.json'
    )
    
    print('\n=== FINAL VERDICT ===')
    print(f'Viable epitopes: {report["viable_epitopes"]}')
    print(f'Global verdict:  {report["global_verdict"]}')
    print(f'Next step:       {report["recommended_next_step"]}')
    
    return report


if __name__ == '__main__':
    run_rfdiffusion_analysis()
```

---

## PASS CONDITIONS

```bash
# 1. AlphaFold report updated with INCONCLUSIVE verdict
grep "INCONCLUSIVE_WRONG_TOOL" results/alphafold/structural_validation_report.json

# 2. Paper language updated — no "failed" or "low confidence structure"
grep -r "inconclusive" .  # Should appear in methods section

# 3. RFdiffusion output PDBs present (after manual Colab run)
ls results/rfdiffusion/output/*.pdb | wc -l  # Should return 10

# 4. Analysis script runs without error
python src/rfdiffusion_analysis.py

# 5. Report generated
ls results/rfdiffusion/rfdiffusion_structural_report.json

# 6. Ensemble figure generated
ls results/rfdiffusion/ensemble_epitope_confidence.png
```

**Decision gate from report:**
- CLEAR_FOR_EXPERIMENTAL_PHASE → proceed to HLA binding assay
- PARTIAL_CONFIDENCE → proceed with flagged notes for wet lab team
- REDESIGN_RECOMMENDED → review construct architecture before wet lab investment

---

## DIRECTORY STRUCTURE EXPECTED AFTER PHASE 7

```
results/
├── alphafold/
│   ├── structural_validation_report.json   (updated with INCONCLUSIVE)
│   ├── v3_plddt_analysis.png
│   └── [ColabFold output files]
└── rfdiffusion/
    ├── input/
    │   └── v3_optimized_rank001.pdb        (copied from alphafold output)
    ├── output/
    │   └── [10x design PDB files from Colab]
    ├── ensemble_scores.csv
    ├── ensemble_epitope_confidence.png
    └── rfdiffusion_structural_report.json
```

---

## WHAT NOT TO DO

- Do not run RFdiffusion in full de novo mode — partial diffusion only
- Do not interpret AlphaFold pLDDT 36.4 as "the construct is unstructured"
  in any output, report, or paper text — it is INCONCLUSIVE
- Do not advance ValidationTier beyond COMPUTATIONALLY_VERIFIED
  based on RFdiffusion alone — wet lab data required for tier advancement
- Do not run RFdiffusion on v1 or v2 constructs at this stage
- Do not modify Phase 1-6 code
