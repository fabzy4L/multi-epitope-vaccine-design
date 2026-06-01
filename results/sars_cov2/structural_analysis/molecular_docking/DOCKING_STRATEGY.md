# Molecular Docking Strategy

## Overview
Molecular docking analysis to evaluate vaccine construct interactions with immune system receptors.

## Docking Targets

### TLR4-MD2 Complex (PDB: 3FXI)
- **Description**: Toll-like receptor 4 with MD-2 co-receptor
- **Binding Site**: MD-2 ligand-binding pocket
- **Significance**: Innate immune recognition and adjuvant response
- **Download**: https://files.rcsb.org/download/3FXI.pdb

### HLA-A*02:01 (PDB: 1HHH)
- **Description**: MHC Class I molecule (most common allele)
- **Binding Site**: Peptide-binding groove
- **Significance**: CD8+ T-cell epitope presentation
- **Download**: https://files.rcsb.org/download/1HHH.pdb

### HLA-DR1 (PDB: 1DLH)
- **Description**: MHC Class II molecule
- **Binding Site**: Alpha-beta peptide-binding cleft
- **Significance**: CD4+ T-cell epitope presentation
- **Download**: https://files.rcsb.org/download/1DLH.pdb

### Mouse IgG2a (PDB: 1IGT)
- **Description**: Antibody Fab fragment
- **Binding Site**: Complementarity-determining regions
- **Significance**: Humoral immune response model
- **Download**: https://files.rcsb.org/download/1IGT.pdb

## Docking Workflow

### Phase 1: Structure Preparation
1. **Receptor Preparation**:
   - Download target PDB structures
   - Remove water molecules and hetero atoms
   - Add hydrogen atoms
   - Define binding sites

2. **Ligand Preparation** (Vaccine Constructs):
   - Use ColabFold-predicted 3D structures
   - Optimize geometry
   - Generate conformational ensemble

### Phase 2: Molecular Docking
**Recommended Tools:**
- **HDOCK**: http://hdock.phys.hust.edu.cn/ (protein-protein docking)
- **AutoDock Vina**: Local installation for flexible docking
- **HADDOCK**: https://wenmr.science.uu.nl/haddock2.4/ (data-driven docking)

**HDOCK Submission Protocol:**
1. Upload receptor PDB file
2. Upload vaccine construct PDB file
3. Select 'Protein-Protein' docking mode
4. Use default parameters (grid search + refinement)
5. Submit and wait for results (~1-2 hours)

### Phase 3: Result Analysis
**Evaluation Criteria:**
- **Binding Affinity**: Predicted Delta-G (kcal/mol)
- **Interface Area**: Contact surface area (A^2)
- **Hydrogen Bonds**: Number and quality of H-bonds
- **Hydrophobic Contacts**: Non-polar interaction analysis
- **Geometric Complementarity**: Shape-based scoring

**Success Indicators:**
- TLR4 docking: Delta-G < -8 kcal/mol (strong adjuvant interaction)
- MHC docking: Epitope regions in binding groove
- Antibody docking: CDR contact with antigenic surfaces

