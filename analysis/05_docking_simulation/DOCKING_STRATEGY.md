# Molecular Docking & Structural Validation Strategy

This document outlines the procedure for validating the 3D structure of the multi-epitope vaccine construct against key immune receptors.

## 1. Receptor Selection (PDB Targets)

| Target Receptor | PDB ID | Rationale |
| :--- | :--- | :--- |
| **TLR4/MD-2** | `3FXI` | Verify interaction with the N-terminal **RS09 adjuvant** for innate priming. |
| **MHC-I** | `1HHH` | Validate binding of CD8+ epitopes (`YLQPRTFLL`, etc.) to **HLA-A*02:01**. |
| **MHC-II** | `1DLH` | Validate binding of CD4+ epitopes to **HLA-DRB1*01:01**. |
| **Antibody** | `1IGT` | Model the interaction of B-cell epitopes with a representative IgG scaffold. |

## 2. Docking Protocol (HDOCK / ClusPro)

1.  **Preparation:** 
    *   Obtain the vaccine construct PDB from **ColabFold**.
    *   Clean receptor PDBs (remove water, ligands, and heteroatoms).
2.  **Execution:** 
    *   Perform **Protein-Protein Docking** with the vaccine as the **Ligand**.
    *   Target the binding grooves for MHC and the dimerization interface for TLR4.
3.  **Metrics for Success:**
    *   **Binding Energy ($\Delta G$):** Aim for < -10 kcal/mol.
    *   **Root Mean Square Deviation (RMSD):** Consistent pose across top 10 models.
    *   **Interface Residues:** Confirm that the vaccine's epitopes (not just linkers) are making contact with the receptor.

## 3. Post-Docking Analysis

*   **Hydrogen Bond Analysis:** Use PyMOL or ChimeraX to identify H-bonds and salt bridges at the interface.
*   **Immune Simulation:** Run the final sequence through **C-ImmSim** to predict the antibody titer trajectory (IgG + IgM) and cytokine profiles (IFN-$\gamma$, IL-2) over a 3-dose schedule.
