# Project Instructions: Vaccinology Pipeline

## Architecture & Workflow

### Dual-Track Analysis
The workspace is split into two tracks:
1.  **SARS-CoV-2 Pipeline (`analysis/sars_cov2/`):** Primary track for vaccine design. Focuses on Spike S1 subunit, literature-validated epitopes, and multi-epitope construct assembly.
2.  **Guinea Worm Analysis (`analysis/guinea_worm/`):** Secondary track for proteome-wide clustering and homology studies.

### Core Resources
- **Vaccinology.one.pdf:** This is the project's "master protocol." Always refer to the extracted version in `results/sars_cov2/reports/Vaccinology_Notes_Extracted.md` for procedural guidance on validation and simulation.
- **Epitope Selection:** Prioritize clinically validated epitopes from literature (see `results/sars_cov2/reports/REFERENCES.md`) over *de novo* prediction if IEDB/MHC servers are slow.

### Structural Validation
Follow "Protocol 5" in the notes for validating vaccine constructs (SAVES v6.0, ERRAT, Verify3D, ProSA-web) before proceeding to docking.
