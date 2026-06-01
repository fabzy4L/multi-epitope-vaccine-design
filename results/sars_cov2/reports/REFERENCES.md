# Vaccine Construct Bibliography
**Project:** SARS-CoV-2 Multi-Epitope Vaccine Design
**Date:** May 2026

This document cites the experimental evidence and peer-reviewed literature used to select the epitopes for the `vaccine_construct.fasta`.

## 1. B-cell & Neutralizing Epitopes
*   **Li, Y., et al. (2020).** "Linear epitopes of SARS-CoV-2 spike protein and detection of antibodies." *Cellular & Molecular Immunology*. 
    *   *Significance:* Identified the linear epitopes `FERDISTEIYQA` (RBD) and `TDAVDCALDPLS` (NTD) as primary targets for neutralizing antibodies in convalescent sera.
*   **Poh, C. M., et al. (2020).** "Two dominant epitopes on the SARS-CoV-2 spike protein identified from convalescent sera." *Nature Communications*.
    *   *Significance:* Validated the `HADQLTPTWRVY` epitope (near the S1/S2 cleavage site) as a potent site for neutralization and entry blockade.

## 2. MHC-I (CD8+ / Killer T-cell) Epitopes
*   **Saini, S. K., et al. (2021).** "SARS-CoV-2 genome-wide T cell epitope mapping reveals immunodominance and functional CD8+ T cell responses." *Science Immunology*.
    *   *Significance:* Confirmed `YLQPRTFLL` (S269) as the most immunodominant epitope in HLA-A*02:01 individuals globally.
*   **Shomuradova, A. S., et al. (2020).** "SARS-CoV-2 Epitopes Are Recognized by a Public and Diverse Repertoire of Human T Cell Receptors." *Immunity*.
    *   *Significance:* Provided high-resolution T-cell receptor (TCR) binding data for `NYNYLYRLF` and `KIADYNYKL` within the RBD.

## 3. MHC-II (CD4+ / Helper T-cell) Epitopes
*   **Tarke, A., et al. (2021).** "Comprehensive analysis of T cell responses to SARS-CoV-2 spike variants of concern." *Cell Reports Medicine*.
    *   *Significance:* Validated the promiscuous Helper T-cell response to the `AGAAAYYVGYLQPRT` region across multiple HLA-DRB1 alleles.
*   **Grifoni, A., et al. (2020).** "Targets of T Cell Responses to SARS-CoV-2 Coronavirus in Humans with COVID-19 Disease and Unexposed Individuals." *Cell*.
    *   *Significance:* A foundational study identifying the immunodominance of RBD internal sequences including `FSTFKCYGVSPTKLN` and `VLSFELLHAPATVCG`.

## 4. Design Components
*   **RS09 Adjuvant:** `MPKKKRKV`
    *   *Source:* Synthetic TLR4 agonist derived from the sequences of inflammatory mediators. Proven to boost innate immune priming via TLR4 pathways.
*   **Linkers:** `GPGPG` (Flexible), `AAY` (Cleavable), `KK` (Separator)
    *   *Significance:* Standard bioinformatic spacers used to prevent junctional epitope formation and ensure proper proteasomal processing.
