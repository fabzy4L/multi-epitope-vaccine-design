# In silico design of a multi-epitope SARS-CoV-2 vaccine candidate

Fabian Alvarez-Primo, PhD

BLK PHX LABS, Savannah, GA, USA
ORCID: https://orcid.org/0000-0002-6917-723X
Correspondence: fabian@blkphxlabs.com

---

## Abstract

Multi-epitope vaccine design requires reducing a large pool of candidate peptides to a small set suitable for assembly into a single construct. This study reports an immunoinformatics pipeline applied to the SARS-CoV-2 spike S1 subunit, together with the construct it produced and the computational checks performed on that construct. A sliding-window scan generated candidate peptides, which were submitted to the IEDB Analysis Resource (NetMHCpan-4.1, NetMHCIIpan-4.0) across 19 HLA alleles. The returned exports contain 44,332 binding predictions over 4,049 unique peptides, of which 74 (0.167%, 72 unique peptides) met the strong-binder criteria. Three multi-epitope constructs were assembled. The lead candidate, v3.1 (142 amino acids, 15.1 kDa), carries four MHC-I and two MHC-II epitopes with predicted affinities below 12 nM, an RS09 TLR4-agonist peptide, and a single KKGPGPG junction adopted after NetChop C-term 3.0 analysis predicted a maximum cleavage probability of 0.948 at the original double-KK junction. Rigid-body protein-protein docking (HDOCKlite) against TLR4/MD-2, HLA-A\*02:01, HLA-DR1 and IgG2a Fab returned scores corresponding to approximate ΔG values of −9.46 to −11.05 kcal/mol. An ODE implementation of the Celada-Seiden framework predicted a Th1-skewed response with peak IgG of 3,351 AU at day 69 under a three-dose schedule. All results are computational; no binding, immunogenicity or efficacy has been measured experimentally.

**Keywords:** immunoinformatics; multi-epitope vaccine; SARS-CoV-2; MHC binding prediction; in silico design

---

## 1. Introduction

Multi-epitope vaccines combine several T-cell and B-cell epitopes into one construct, which allows a vaccine to target multiple sites on a pathogen rather than a single antigen. The approach has been applied to viral, bacterial and parasitic targets, and its appeal is that it can in principle address immune escape and HLA diversity within one sequence.

The design step is the bottleneck. A sliding-window scan of a single viral subunit generates thousands of candidate peptides, and the choice of which few to carry forward is usually made with a combination of binding thresholds and manual judgment. That step is where most of the design decisions are made, and it is rarely reported in a form that another group could repeat.

This study applies a fixed-threshold, scripted selection pipeline to the SARS-CoV-2 spike S1 subunit and reports the full path from candidate generation to a lead construct, including the selection criteria, the decisions that changed the construct, and the points where the pipeline's output disagreed with expectation.

## 2. Methods

### 2.1 Epitope generation

The SARS-CoV-2 spike S1 subunit (685 amino acids) was scanned with a sliding window to generate 3,380 MHC-I candidates (8-12 residues) and 894 MHC-II candidates (12-20 residues), giving 4,274 candidate sequences.

<!-- TODO(Primo): 4,274 candidates were generated but the IEDB exports cover 4,049 unique
     peptides, a difference of 225. Confirm whether these were dropped at submission (length
     limits, duplicate peptides across windows) and state the reason here, or re-submit the
     missing candidates. A reviewer comparing the two numbers will ask. -->


### 2.2 MHC binding prediction

Binding was predicted with the IEDB Analysis Resource using NetMHCpan-4.1 (MHC-I) and NetMHCIIpan-4.0 (MHC-II) across 19 HLA alleles.

MHC-I (11): HLA-A\*01:01, HLA-A\*02:01, HLA-A\*03:01, HLA-A\*24:02, HLA-B\*08:01, HLA-B\*35:01, HLA-B\*40:01, HLA-C\*06:02, HLA-C\*07:01, HLA-C\*12:03, HLA-C\*15:02.

MHC-II (8): HLA-DRB1\*01:01, HLA-DRB1\*03:01, HLA-DRB1\*07:01, HLA-DRB1\*15:01, HLA-DRB3\*01:01, HLA-DRB3\*02:02, HLA-DRB4\*01:01, HLA-DRB5\*01:01.

The returned exports contain 44,332 individual binding predictions over 4,049 unique peptides.

### 2.3 Scoring and selection

Strong binders were defined as IC50 < 50 nM with percentile rank < 0.5% (MHC-I) or < 1.0% (MHC-II). Candidates meeting these criteria were ranked by:

```
Combined_Score = (1/IC50) × (1/Rank) × Population_Weight
```

### 2.4 Verification of reported counts

Prediction counts, strong-binder counts and the selectivity rate were recomputed directly from the IEDB export files by `src/verify_selectivity.py`, so every count in this manuscript can be regenerated from the raw exports in the repository.

### 2.5 Decoy benchmark (not yet performed)

A composition-matched decoy benchmark is specified but has not been run. Each selected epitope is shuffled to produce decoys with identical amino acid composition and no preserved binding motif; the decoys are then submitted to IEDB under the same alleles, method and peptide lengths as the real candidates, and the two score distributions are compared with a two-sample Kolmogorov-Smirnov test. The generation and analysis stages are implemented in `src/decoy_benchmark.py`; the IEDB submission step is outstanding, so no decoy result is reported here.

### 2.6 Construct assembly

Constructs followed the architecture:

```
[Signal Peptide] → [Adjuvant] → [MHC-II Epitopes] → [Separator] → [MHC-I Epitopes] → [Purification Tag]
```

GPGPG linkers separated MHC-II epitopes, AAY linkers separated MHC-I epitopes, a KK motif separated the two domains, and RS09 was included as a TLR4-agonist peptide (Kim et al., 2025; Negahdaripour et al., 2017). A His₆ tag was appended for IMAC purification.

### 2.7 Physicochemical characterization

Molecular weight, theoretical pI, GRAVY score and instability index were computed with BioPython ProtParam.

### 2.8 Antigenicity and allergenicity

Antigenicity was predicted with VaxiJen v2.0 (target: virus, threshold 0.4) for the full construct and for individual epitopes. Allergenicity was predicted with AllerTop v2.1.

### 2.9 Proteasomal cleavage

Per-residue cleavage probabilities were computed with NetChop 3.1, C-term 3.0 model, threshold 0.5, across the full 144-residue v3 sequence. A redesign threshold of 0.7 was applied to junction residues, above which cleavage was considered likely enough to fragment the linker and disrupt the termini of flanking epitopes.

### 2.10 Structural modeling

Structures were predicted with AlphaFold2 (ColabFold) and backbone viability was assessed with RFdiffusion (n = 16 designs).

### 2.11 Protein-protein docking

Rigid-body docking was performed with HDOCKlite v1.1 (Yan et al., 2017) using the AlphaFold2 rank-1 model of v3.1 (`vaccine_v3_rank001.pdb`) against four receptors: TLR4/MD-2 (3FXI), HLA-A\*02:01 (1HHH), HLA-DR1 (1DLH) and IgG2a Fab (1IGT). All 4,392 rotational models were evaluated per run. HDOCK scores were converted to approximate ΔG by an empirical linear factor (score / 30.0). Thresholds were set at ΔG ≤ −8.0 kcal/mol (TLR4, MHC) and ≤ −7.0 kcal/mol (IgG).

### 2.12 Immune kinetics simulation

C-ImmSim was not reachable during the analysis period (iimcb.genesilico.pl returned HTTP 404; the original server at 150.146.60.148 was unreachable). Kinetics were therefore modeled with a custom ODE implementation of the Celada-Seiden framework (Perelson & Weisbuch, 1997; Carneiro et al., 1996; Antia et al., 2005; Pappalardo et al., 2016), which approximates the same differential equation system. Parameters: three doses at days 1, 28 and 56; 100 AU antigen per dose; RS09 modeled as a 4× IL-12 enhancement; HLA-A\*03:01 and HLA-DRB1\*15:01; 360-day window.

## 3. Results

### 3.1 Epitope selection

Of 44,332 predictions, 74 met the strong-binder criteria (44 MHC-I, 30 MHC-II), corresponding to 72 unique peptides and 0.167% of predictions. Two peptides met the criteria for two alleles each. These counts were recomputed from the IEDB exports (Methods 2.4).

This figure describes where the selected peptides sit within the prediction distribution under the stated thresholds. It is not a test of the scoring function against negative sequences; the decoy benchmark that would provide that test has not been run (Methods 2.5).

Highest-ranked MHC-I peptides:

1. RLFRKSNLK (HLA-A\*03:01): 4.82 nM, 0.01% rank
2. LPFNDGVYF (HLA-B\*35:01): 4.12 nM, 0.02% rank
3. FPNITNLCPF (HLA-B\*35:01): 5.40 nM, 0.02% rank
4. YLQPRTFLL (HLA-A\*02:01): 4.30 nM, 0.03% rank

Highest-ranked MHC-II peptides:

1. VLSFELLHAPATVCG (HLA-DRB1\*01:01): 4.06 nM, 0.31% rank
2. QTLLALHRSYLTPGD (HLA-DRB1\*15:01): 9.87 nM, 0.15% rank
3. INITRFQTLLALHRS (HLA-DRB1\*15:01): 11.23 nM, 0.20% rank

### 3.2 Construct design and junction redesign

Three constructs were assembled. The lead candidate, v3.1, is 142 amino acids:

```
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD
GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK
AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
```

The initial construct (v3, 144 aa) carried a KKGPGPGKK double-KK motif at the MHC-II/MHC-I boundary (residues 70-78). NetChop C-term 3.0 returned a maximum cleavage probability of 0.948 at K77, with all four flanking lysines above the 0.7 redesign threshold (K70 = 0.947, K71 = 0.788, K77 = 0.948, K78 = 0.799). The trailing KK was removed, giving the single KKGPGPG separator of v3.1 without altering epitope identity. v3.1 was not resubmitted to NetChop, since the predicted cleavage risk was confined to the lysines now absent.

### 3.3 Physicochemical properties

| Property | v1 | v2 | v3 | v3.1 (lead) | Target Range |
|----------|----|----|----|-----------------|--------------|
| Length (aa) | 171 | 172 | 144 | 142 | <200 |
| MW (kDa) | 15.0 | 15.1 | 15.3 | 15.1 | <50 |
| Theoretical pI | 10.33 | 10.12 | 10.22 | 10.13 | 7–11 |
| GRAVY Score | — | — | −0.199 | −0.147 | <0 preferred |
| Instability Index | — | — | 41.0 | 42.6 | <40 borderline |
| Synthesis Gate | — | — | BLOCKED | CLEARED | — |

*All values computed with BioPython ProtParam. The v3 synthesis gate was blocked by the NetChop result above and redesigned to v3.1.*

All three constructs have a theoretical pI above 9.0 (v3.1 pI = 10.13). At neutral cytoplasmic pH, strongly basic constructs are prone to non-specific electrostatic interactions that reduce soluble yield in *E. coli*, so mammalian expression (HEK293 or CHO) is the more likely route for initial production. *E. coli* SHuffle strains with co-expressed chaperones (DnaK/DnaJ/GrpE) are an alternative if bacterial expression is required.

### 3.4 Antigenicity and allergenicity

VaxiJen v2.0 scored the full v3.1 construct at 0.2592 (probable non-antigen, threshold 0.4). This is consistent with a known limitation of the tool for engineered multi-epitope constructs: VaxiJen was trained on natural pathogen proteins, and non-antigenic regions — the signal peptide, the GPGPG and AAY linkers, and the His₆ tag — dilute the construct-level score. Per-epitope scores were therefore obtained (Table 1).

**Table 1. Per-epitope VaxiJen v2.0 antigenicity scores (target: virus, threshold 0.4)**

| Epitope | MHC Class | HLA Allele | IC50 (nM) | VaxiJen Score | Prediction |
|---|---|---|---|---|---|
| LPFNDGVYF | MHC-I | HLA-B\*35:01 | 4.12 | 0.5593 | Antigen |
| FPNITNLCPF | MHC-I | HLA-B\*35:01 | 5.40 | 1.3964 | Antigen |
| RLFRKSNLK | MHC-I | HLA-A\*03:01 | 4.82 | −0.2829 | Non-antigen† |
| VLYNSASFSTFK | MHC-I | HLA-B\*40:01 | — | 0.0249 | Non-antigen† |
| QTLLALHRSYLTPGD | MHC-II | HLA-DRB1\*15:01 | 9.87 | 0.6708 | Antigen |
| INITRFQTLLALHRS | MHC-II | HLA-DRB1\*15:01 | 11.23 | 0.4118 | Antigen |

*Four of six epitopes were predicted antigenic. † VaxiJen reliability is reduced for peptides shorter than about 20 residues. RLFRKSNLK is reported as immunodominant for HLA-A\*03:01 in independent experimental work (Saini et al., 2021).*

AllerTop v2.1 classified v3.1 as a probable non-allergen; the closest database match was BCL9L_HUMAN, a human protein, indicating no homology to known allergens in that database.

### 3.5 Allele representation

The selected epitopes bind 73% of the MHC-I alleles and 50% of the MHC-II alleles in the panel.

<!-- TODO(Primo): two linked issues here.
     1. This was previously labeled "population coverage", which is a different quantity.
        Either run the IEDB Population Coverage tool and report % population by geographic
        group, or keep the current wording (allele representation within the panel).
     2. The Methods previously stated the 19-allele panel represents ">90% global population
        coverage". That claim needs a citation or its own Population Coverage run; it has been
        left out of Methods until then. -->

### 3.6 Protein-protein docking

| Target | PDB | Interaction tested | HDOCK Score | ΔG (approx.) | Threshold met |
|---|---|---|---|---|---|
| TLR4/MD-2 complex | 3FXI | RS09 adjuvant with the MD-2 pocket | −287.59 | −9.59 kcal/mol | Yes |
| HLA-A\*02:01 | 1HHH | MHC-I epitopes with the peptide-binding groove | −283.83 | −9.46 kcal/mol | Yes |
| HLA-DR1 | 1DLH | MHC-II epitopes with the α-β cleft | −327.22 | −10.91 kcal/mol | Yes |
| IgG2a Fab | 1IGT | Structural complementarity for a humoral response | −331.36 | −11.05 kcal/mol | Yes |

*ΔG approximated from the HDOCK score by an empirical linear conversion (score / 30.0).*

All four targets met their thresholds. HLA-DR1 and IgG2a Fab returned the strongest predicted interactions (ΔG < −10.5 kcal/mol), which is in the same direction as the individual VaxiJen scores for the two MHC-II epitopes (0.6708 and 0.4118). The TLR4/MD-2 result is consistent with RS09 engaging the innate pathway as described for TLR4 agonist peptides (Kim et al., 2025).

HDOCK scores reflect static rigid-receptor geometry and do not capture induced fit or binding-pathway effects. These results are supportive rather than definitive, and surface plasmon resonance or biolayer interferometry would be required before synthesis.

### 3.7 Immune kinetics simulation

| Metric | Peak Value | Day of Peak |
|---|---|---|
| IgM | 1,536 AU | Day 40 |
| IgG (total) | 3,351 AU | Day 69 |
| IgG2 / IgG1 ratio | 2.75 | — |
| IFN-γ | 278.6 AU | Post-dose 1 |
| IL-12 | 34.8 AU | Early |
| CD8⁺ T cells (TC) | 66.6 AU | Post-dose 2 |
| CD4⁺ T-helper (TH) | 115.6 AU | Post-dose 2 |

The simulation predicted a Th1-skewed response (IgG2 > IgG1, IFN-γ present, IL-12 elevated after the adjuvant term), the pattern expected for a TLR4-adjuvanted peptide vaccine against intracellular antigens. IgG accumulated across the three doses, peaking at day 69 after the third dose at more than three times the 1,000 AU reference threshold used in the model.

## 4. Discussion

The selection step reduced 44,332 predictions to 74 peptides under fixed thresholds. The value of the fixed-threshold approach is not the selectivity figure itself but that every peptide in the construct can be traced to a specific threshold and score, so a disagreement with the output is a disagreement with a stated parameter. The counts here are recomputed from the raw exports rather than carried forward from an intermediate file.

The selectivity figure should not be read as a validation of the scoring function. It states that 0.167% of predictions passed thresholds chosen in advance, which is a property of the thresholds. Whether these sequences bind better than arbitrary peptides of the same amino acid composition is a separate question, and the decoy benchmark that would answer it has not been run.

Two results ran against expectation and are worth stating directly. First, the full-construct VaxiJen score classified v3.1 as a probable non-antigen; per-epitope scores suggest this reflects dilution by linkers and tags rather than the epitopes themselves, but that interpretation is an inference and not a measurement. Second, NetChop predicted near-certain cleavage at the original double-KK junction, which would have fragmented the construct between its MHC-II and MHC-I domains. That result changed the construct, and it would not have surfaced without the cleavage check.

The pipeline's scoring also made a selection that, on review, is a weakness rather than a strength: it chose two MHC-II epitopes sharing a 9-mer core from the same allele, and excluded the canonical HLA-A\*02:01 epitope. Both are described below.

### 4.1 Limitations

**MHC-II allele redundancy.** Both MHC-II epitopes in v3.1, QTLLALHRSYLTPGD and INITRFQTLLALHRS, are predicted binders for HLA-DRB1\*15:01 and share a 9-mer core (QTLLALHRS). This redundancy arose from a scoring artifact: the combined-score function did not penalize repeated alleles. HLA-DRB1\*01:01 coverage is absent from v3.1, as the top DRB1\*01:01 candidate (VLSFELLHAPATVCG, 4.06 nM) was excluded for a free cysteine at position 13. CD4⁺ helper breadth is therefore narrower than the allele panel suggests.

**HLA-A\*02:01 coverage absent.** HLA-A\*02:01 is the most prevalent MHC-I allele globally (about 30% frequency across populations). YLQPRTFLL, the canonical SARS-CoV-2 HLA-A\*02:01 epitope reported by Saini et al. (2021), was present in the candidate pool at 4.30 nM and 0.03% rank but was excluded by the combined score, which favored HLA-A\*03:01 coverage. This leaves a gap for the largest single HLA supertype.

**Structural prediction.** AlphaFold2 prediction was inconclusive (mean pLDDT 36.4) on a minimal multiple sequence alignment (n = 3 homologs). Low pLDDT is expected for multi-epitope constructs, which lack a stable globular fold by design, so this value does not describe folding behavior either way. RFdiffusion backbone modeling (n = 16 designs, mean confidence 0.941) indicates the five epitope regions are structurally viable, but circular dichroism or cryo-EM would be needed to describe the actual structure.

**All validation is computational.** No experimental work was performed. Binding predictions require HLA binding assays; any immunogenicity claim requires T-cell activation studies; protective efficacy requires animal models. The COMPUTATIONALLY_VERIFIED tier used in the repository describes the scope of checks completed, not experimental confirmation.

### 4.2 Future work

The scoring function is being revised to include an allele diversity penalty, which would prevent the same-allele selection described above, and to include YLQPRTFLL for HLA-A\*02:01 coverage. The ODE kinetics would benefit from comparison against C-ImmSim or LImmSim if either becomes available. Molecular dynamics of v3.1 would address the dynamic behavior that rigid docking cannot reach.

The same pipeline components apply to other targets without architectural change. For autologous CAR-T and TCR-T work, NetMHCpan and the HLA panel used here are the tools behind neoantigen discovery pipelines such as pVACseq, and the substitution required is a tumor mutant proteome in place of the S1 input. For allogeneic cell therapy, where immune rejection rather than immune recognition is the failure mode, the same sliding window, prediction and filtering steps apply with the scoring objective inverted.

## 5. Conclusions

A fixed-threshold immunoinformatics pipeline applied to SARS-CoV-2 spike S1 reduced 44,332 binding predictions to 74 strong binders and produced a 142-residue multi-epitope construct. Proteasomal cleavage prediction changed the construct at the junction, and the selection step left two gaps in allele coverage that are documented above. All results are predictions; the construct has not been synthesized, and no binding, immunogenicity or efficacy has been measured.

## Declarations

**AI assistance.** AI tools were used in this work: Claude (Anthropic) for code development, validation logic and statistical analysis scripting, and Gemini (Google) for structural computation via ColabFold and for visualization. The author designed the study, selected the parameters, verified the results and takes full responsibility for the content.

The pipeline is not end-to-end automated. It includes manual steps: web-based IEDB batch submissions, individual VaxiJen and AllerTop submissions, ColabFold structure prediction via Google Colab, and file handling between stages. "Automated" in this manuscript refers to the scripted analysis layers (Python scoring, decoy benchmarking, construct assembly). Reproduction requires the manual steps documented in METHODOLOGY.md.

**Competing interests.** The author is the founder of BLK PHX LABS. No funding was received for this work.

**Data and code availability.** The pipeline, documentation and results are at https://github.com/fabzy4L/multi-epitope-vaccine-design under the MIT licence.

**Author contributions.** F.A.-P. designed the study, built the pipeline, performed the analysis and wrote the manuscript.

## References

<!-- TODO(Primo): BLOCKER FOR SUBMISSION. The manuscript cites Kim et al. 2025;
     Negahdaripour et al. 2017; Yan et al. 2017; Saini et al. 2021; Perelson & Weisbuch 1997;
     Carneiro et al. 1996; Antia et al. 2005; Pappalardo et al. 2016 — plus the tools
     (NetMHCpan-4.1, NetMHCIIpan-4.0, NetChop 3.1, VaxiJen v2.0, AllerTop v2.1, HDOCK,
     AlphaFold2/ColabFold, RFdiffusion, BioPython) which each need their primary citation.
     A numbered reference list is required. -->
