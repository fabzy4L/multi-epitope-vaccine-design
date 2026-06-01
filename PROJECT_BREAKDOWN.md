# Vaccinology Project Breakdown

This project is organized into two distinct analytical tracks to ensure clarity and scientific rigor.

## Track A: SARS-CoV-2 Vaccine Design
Targeting the Spike glycoprotein (S1 subunit) for multi-epitope vaccine development.

- **Antigen Source:** NC_045512.2 reference genome (translated Spike protein).
- **Location:** `analysis/sars_cov2/`
- **Current Status:**
    - [x] Genome-to-Protein translation.
    - [x] S1 domain extraction (residues 1-685).
    - [x] Validated epitope selection (cited from literature).
    - [x] Multi-epitope construct assembly.
- **Key Artifacts:** 
    - `results/sars_cov2/reports/vaccine_construct.fasta`
    - `results/sars_cov2/reports/REFERENCES.md` (Formal bibliography)

## Track B: Guinea Worm Proteome Analysis
Large-scale protein clustering of *Dracunculus medinensis* (UP000274756).

- **Location:** `analysis/guinea_worm/`
- **Tool:** [CD-HIT](http://cd-hit.org) (Cluster Database at High Identity with Tolerance).
- **Parameters:** 90% identity threshold (`-c 0.9`).
- **Results:** 10,868 sequences processed into 10,778 clusters.
- **Key Artifacts:**
    - `analysis/guinea_worm/01_clustering/1624324292.fas.1`: Clustered representative sequences.
    - `analysis/guinea_worm/01_clustering/1624324292.fas.1.clstr`: Clustering map.

## Summary of Tools Used
- **CD-HIT**: Sequence clustering.
- **gnuplot**: Generating visual reports for clustering results.
- **Perl**: Used for statistical analysis of FASTA files (`faa_stat.pl`).
- **R (seqinr)**: General sequence manipulation and analysis.
- **PyMOL/VMD (implied)**: For viewing the `.pdb` files.
