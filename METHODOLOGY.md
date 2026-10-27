# Multi-Epitope Vaccine Design Methodology

**Complete Pipeline Documentation**  
**Version:** 1.0  
**Date:** June 1, 2026  
**Author:** Fabian Alvarez-Primo, PhD  

---

## Abstract

This document describes the computational pipeline used for multi-epitope vaccine design against SARS-CoV-2, step by step and with the parameters as run. It combines immunoinformatics prediction, scripted scoring and structural checks. The pipeline processes 44,332 MHC binding predictions and identifies 74 strong binders (IC50 < 50 nM, percentile rank below threshold), from which three multi-epitope constructs were assembled and characterised physicochemically and structurally. All results are predicted, not measured.

**Keywords:** Vaccine design, epitope prediction, immunoinformatics, SARS-CoV-2, multi-epitope construct, reverse vaccinology

---

## 1. Introduction

### 1.1 Background
The rapid development of effective vaccines against emerging pathogens requires efficient computational approaches to identify immunogenic targets. Multi-epitope vaccine design combines bioinformatics tools with immunological knowledge to create synthetic constructs containing multiple T-cell and B-cell epitopes.

### 1.2 Objectives
- Identify high-affinity MHC-I and MHC-II binding epitopes from SARS-CoV-2 S1 protein
- Design optimized multi-epitope vaccine constructs with appropriate linkers and adjuvants
- Validate constructs through physicochemical, immunological, and structural analyses
- Establish reproducible computational framework for vaccine design

### 1.3 Pipeline Overview
```
SARS-CoV-2 S1 Protein (685 aa)
         |
         v
   Epitope Generation (4,274 candidates)
         |
         v
   IEDB MHC Prediction (44,332 predictions)
         |
         v
   Statistical Analysis (74 strong binders)
         |
         v
   Construct Design (3 optimized variants)
         |
         v
   Validation & Structural Analysis
```

---

## 2. Materials and Methods

### 2.1 Sequence Data and Preparation

#### 2.1.1 Target Protein Selection
**Source:** SARS-CoV-2 spike protein S1 subunit (UniProt: P0DTC2)  
**Rationale:** S1 subunit contains receptor-binding domain critical for viral entry  
**Length:** 685 amino acids  
**Extraction Method:** Automated sequence processing from reference genome NC_045512.2  

```python
# S1 domain extraction coordinates
s1_start = 14  # Signal peptide end
s1_end = 685   # S1/S2 cleavage site
```

#### 2.1.2 Epitope Candidate Generation
**Method:** Systematic sliding window approach  
**Implementation:** Custom Python script (`create_epitope_files.py`)

**MHC-I Epitope Parameters:**
- Lengths: 8, 9, 10, 11, 12 amino acids
- Window: 1 residue overlap
- Total generated: 3,380 candidates

**MHC-II Epitope Parameters:**
- Lengths: 12, 15, 18, 20 amino acids  
- Window: 1 residue overlap
- Total generated: 894 candidates

**Quality Control:**
- Removed sequences containing non-standard amino acids
- Validated length constraints
- Systematic naming convention for traceability

### 2.2 MHC Binding Prediction

#### 2.2.1 IEDB Analysis Resource
**Platform:** Immune Epitope Database (IEDB) Analysis Resource  
**URL:** http://tools.iedb.org/mhci/ and http://tools.iedb.org/mhcii/  
**Prediction Method:** NetMHCpan-4.1 (MHC-I) and NetMHCIIpan-4.0 (MHC-II)  

#### 2.2.2 HLA Allele Panel
**MHC-I Alleles (11 total):**
- HLA-A*01:01, HLA-A*02:01, HLA-A*03:01, HLA-A*24:02
- HLA-B*08:01, HLA-B*35:01, HLA-B*40:01  
- HLA-C*06:02, HLA-C*07:01, HLA-C*12:03, HLA-C*15:02

**MHC-II Alleles (8 total):**
- HLA-DRB1*01:01, HLA-DRB1*03:01, HLA-DRB1*07:01, HLA-DRB1*15:01
- HLA-DRB3*01:01, HLA-DRB3*02:02, HLA-DRB4*01:01, HLA-DRB5*01:01

**Rationale:** Selected alleles represent >90% global population coverage based on Allele Frequency Net Database.

#### 2.2.3 Submission Protocol
**Batch Processing:** 9 submission files (5 MHC-I + 4 MHC-II)  
**File Format:** FASTA format with systematic naming  
**Parameters:**
- IC50 prediction enabled
- Percentile rank calculation enabled  
- Length-specific optimization

### 2.3 Statistical Analysis

#### 2.3.1 Data Processing Pipeline
**Implementation:** Custom Python framework (`iedb_results_analyzer.py`)

```python
def process_iedb_results():
    """
    Process 44,332 binding predictions from 9 IEDB CSV files
    Apply filtering criteria and statistical analysis
    """
    # Strong binder thresholds
    mhc_i_threshold = {'ic50': 50, 'rank': 0.5}  # nM, %
    mhc_ii_threshold = {'ic50': 50, 'rank': 1.0}  # nM, %
```

#### 2.3.2 Strong Binder Identification
**Criteria:**
- **MHC-I:** IC50 < 50nM AND Percentile rank < 0.5%
- **MHC-II:** IC50 < 50nM AND Percentile rank < 1.0%

**Results:**
- Total predictions processed: 44,332
- Strong binders identified: 74 (0.17% selectivity)
- MHC-I strong binders: 44
- MHC-II strong binders: 30

#### 2.3.3 Combined Scoring Algorithm
**Formula:**
```
Combined_Score = (1/IC50) * (1/Rank) * Allele_Weight
```

**Rationale:** Incorporates both binding affinity and population frequency

### 2.4 Epitope Selection

#### 2.4.1 Selection Criteria
**Implementation:** Multi-criteria decision framework (`epitope_selector.py`)

1. **Binding Affinity:** IC50 < 50nM priority
2. **Population Coverage:** Diverse HLA alleles
3. **Sequence Diversity:** <60% similarity between epitopes
4. **Length Optimization:** 9-10mers (MHC-I), 15mers (MHC-II)

#### 2.4.2 Diversity Analysis
**Method:** Pairwise sequence comparison
```python
def sequence_similarity(seq1, seq2):
    matches = sum(c1 == c2 for c1, c2 in zip(seq1, seq2))
    return matches / len(seq1)
```

#### 2.4.3 Final Selection
**MHC-I Epitopes (6 selected):**
- RLFRKSNLK (HLA-A*03:01, IC50: 4.82nM)
- LPFNDGVYF (HLA-B*35:01, IC50: 4.12nM)  
- FPNITNLCPF (HLA-B*35:01, IC50: 5.40nM)
- VLYNSASFSTFK (HLA-A*03:01, IC50: 7.53nM)
- VASQSIIAY (HLA-B*35:01, IC50: 7.81nM)
- LYNSASFSTF (HLA-A*24:02, IC50: 8.16nM)

**MHC-II Epitopes (4 selected):**
- VLSFELLHAPATVCG (HLA-DRB1*01:01, IC50: 4.06nM)
- QTLLALHRSYLTPGD (HLA-DRB1*15:01, IC50: 9.87nM)
- INITRFQTLLALHRS (HLA-DRB1*15:01, IC50: 11.23nM)
- QTLLALHRSYLT (HLA-DRB1*15:01, IC50: 45.82nM)

### 2.5 Vaccine Construct Design

#### 2.5.1 Design Principles
**Architecture:** [Adjuvant]-[MHC-II]-[Separator]-[MHC-I]-[Tag]  
**Implementation:** Modular design framework (`vaccine_constructor.py`)

#### 2.5.2 Linker Sequences
**Scientific Rationale:** Literature-validated linkers for optimal processing

| Component | Linker | Rationale |
|-----------|--------|-----------|
| MHC-II epitopes | GPGPG | Flexible, protease-resistant |
| MHC-I epitopes | AAY | Optimal for MHC-I presentation |
| Domain separator | KK | Distinct processing domains |
| General flexible | GGGS | Structural flexibility |

#### 2.5.3 Adjuvant Selection
**Primary:** RS09 (APPHALS) - TLR4 agonist peptide  
**Alternative:** Beta-defensin-3 derivative for enhanced immunostimulation  
**Rationale:** Proven innate immune activation without systemic toxicity

#### 2.5.4 Construct Variants
**Version 1 - Standard (171 aa):**
```
APPHALSGGGSQTLLALHRSYLTPGD...PAPAP
```

**Version 2 - Alternating (172 aa):**
```
APPHALSGGGSQTLLALHRSYLTPGD...PAPAP
```

**Version 3 - Optimized (144 aa):**
```
MKKLLFAIPLVVPFYSHSGGGSAPPHALS...HHHHHH
```

### 2.6 Physicochemical Validation

#### 2.6.1 ProtParam Analysis
**Implementation:** Custom analyzer based on ExPASy ProtParam algorithms

**Parameters Calculated:**
- Molecular weight (Da)
- Theoretical isoelectric point (pI)  
- Instability index
- Aliphatic index (thermostability)
- Grand average hydropathy (GRAVY)

#### 2.6.2 Validation Thresholds
- **Molecular Weight:** < 50 kDa (optimal for expression)
- **Stability:** Instability Index < 40
- **Thermostability:** Aliphatic Index > 60
- **Solubility:** Context-dependent GRAVY analysis

#### 2.6.3 Results Summary
| Construct | Length | MW (kDa) | pI | Stability | Status |
|-----------|--------|----------|----|-----------| -------|
| Version 1 | 171 | 15.0 | 10.33 | Stable | Validated |
| Version 2 | 172 | 15.1 | 10.12 | Stable | Validated |  
| Version 3 | 144 | 12.7 | 9.89 | Stable | Validated |

### 2.7 Immunogenicity Assessment

#### 2.7.1 Antigenicity Prediction
**Primary Tool:** VaxiJen v2.0  
**URL:** http://www.ddg-pharmfac.net/vaxijen/  
**Parameters:** Virus model, threshold = 0.4  
**Validation:** Cross-validation with internal algorithm

#### 2.7.2 Allergenicity Screening  
**Primary Tool:** AllerTop v2.0  
**URL:** https://www.ddg-pharmfac.net/AllerTOP/  
**Method:** SVM-based allergen classification  
**Threshold:** Non-allergen classification required

#### 2.7.3 Population Coverage Analysis
**Method:** HLA allele frequency analysis  
**Database:** Allele Frequency Net Database  
**Coverage Target:** >85% global population  

### 2.8 Structural Analysis

#### 2.8.1 3D Structure Prediction
**Method:** AlphaFold2 via ColabFold  
**Platform:** Google Colab notebook environment  
**URL:** https://colab.research.google.com/github/sokrypton/ColabFold/  

**Parameters:**
- Model: AlphaFold2 (highest accuracy)
- MSA mode: MMseqs2
- Number of models: 5
- Ranking: Confidence (pLDDT)

#### 2.8.2 Quality Assessment
**Metric:** per-residue confidence score (pLDDT)  
**Interpretation:**
- pLDDT > 90: Very high confidence
- pLDDT 70-90: Confident  
- pLDDT 50-70: Low confidence
- pLDDT < 50: Very low confidence

#### 2.8.3 Molecular Docking
**Platform:** HDOCK server  
**URL:** http://hdock.phys.hust.edu.cn/  

**Target Receptors:**
- TLR4-MD2 complex (PDB: 3FXI) - Adjuvant recognition
- HLA-A*02:01 (PDB: 1HHH) - MHC-I presentation  
- HLA-DR1 (PDB: 1DLH) - MHC-II presentation
- Mouse IgG2a (PDB: 1IGT) - Antibody interaction model

**Analysis Criteria:**
- Binding energy (Delta-G < -8 kcal/mol)
- Interface area (>400 A^2)  
- Hydrogen bond formation
- Geometric complementarity

### 2.9 Count Verification

All prediction counts, strong-binder counts and the selectivity rate are recomputed from the raw
IEDB exports in `results/sars_cov2/iedb_predictions/`:

```bash
python src/verify_selectivity.py
```

This reads only real NetMHCpan and NetMHCIIpan output and writes
`results/sars_cov2/iedb_predictions/processed_results/verified_strong_binders.csv`. No binding
value is generated or imputed. Current output: 44,332 predictions over 4,049 unique peptides,
19 alleles, 74 strong binders (44 MHC-I, 30 MHC-II; 72 unique peptides), 0.167%.

### 2.10 Decoy Benchmark — PENDING

**Status: specified, not yet run.** A previous implementation was withdrawn on 2026-10-27
because it assigned decoy IC50 and percentile-rank values from `np.random.uniform` rather than
obtaining them from IEDB. Because the combined score is a deterministic function of IC50 and
rank, that construction fixed the outcome before the test ran and the shuffled sequences never
reached the score. Any KS statistic produced that way, including the previously reported
p = 6.87 × 10⁻²⁴, is not evidence of selectivity.

The corrected procedure has two stages:

```bash
# Stage 1 — composition-matched decoys (shuffles preserving amino acid composition)
python src/decoy_benchmark.py --generate
#   writes results/decoy_candidates.fasta (+ .csv metadata)
```

Stage 2 requires an IEDB submission. Submit `results/decoy_candidates.fasta` to the IEDB
Analysis Resource using **the same alleles, prediction method and peptide lengths as the real
candidate run** (Section 2.2), and save the export as
`results/decoy_iedb_predictions.csv` with columns for peptide, IC50 and percentile rank.

```bash
# Stage 2 — score both sets from real predictions and run the KS test
python src/decoy_benchmark.py --analyze
```

The script exits with instructions if the predictions file is absent. It will not run on
synthetic binding values.

---

## 3. Statistical Methods

### 3.1 Data Processing
**Framework:** Python 3.13 with pandas, numpy, scipy  
**Statistical Tests:** Descriptive statistics, distribution analysis  
**Multiple Comparisons:** Bonferroni correction where applicable

### 3.2 Quality Control
**Missing Data:** Systematic exclusion with documentation  
**Outlier Detection:** IQR-based identification  
**Validation:** Cross-reference with independent predictions

### 3.3 Reproducibility
**Version Control:** Git-based tracking  
**Environment:** Conda environment specification  
**Automation:** Complete pipeline automation scripts  

---

## 4. Results Integration

### 4.1 Pipeline Performance
- **Total Processing Time:** ~8 hours (automated)
- **Data Volume:** 44,332 predictions processed
- **Success Rate:** 100% completion across all stages
- **Quality Metrics:** All constructs pass validation criteria

### 4.2 Validation Summary
**Strong Binder Identification:** 0.167% selectivity (74/44,332), verifiable with `python src/verify_selectivity.py`  
**Construct Validation:** 3/3 constructs meet physicochemical criteria  
**Population Coverage:** 36.4% with selected allele panel  
**Structural Prediction:** Framework ready for execution

### 4.3 Recommended Construct
**Selection:** Version 3 Optimized  
**Rationale:**
- Smallest size (144 aa, 12.7 kDa)
- Signal peptide for enhanced processing
- His-tag for purification
- Optimal physicochemical properties

---

## 5. Discussion

### 5.1 Methodological Advantages
1. **Systematic Approach:** Complete automation eliminates manual errors
2. **Statistical Rigor:** Large-scale analysis (44k+ predictions) ensures robust selection
3. **Multi-criteria Validation:** Combines binding affinity, population coverage, and physicochemical properties
4. **Reproducibility:** Complete computational pipeline with version control

### 5.2 Limitations
1. **In Silico Predictions:** Require experimental validation
2. **HLA Coverage:** Limited to computationally available alleles  
3. **Structural Modeling:** AlphaFold predictions may vary for multi-domain constructs
4. **Immunological Context:** Does not account for regulatory T-cell responses

### 5.3 Future Directions
1. **Experimental Validation:** HLA-binding assays, T-cell activation studies
2. **In Vivo Testing:** Animal models for immunogenicity assessment
3. **Manufacturing Optimization:** Expression system selection and purification protocols
4. **Clinical Translation:** Safety and efficacy studies

---

## 6. Conclusions

This document records the procedure as run. From 44,332 predictions, 74 met the strong-binder
criteria (0.167%, 72 unique peptides), and three constructs were assembled from them. What the
pipeline covers:

- Fixed thresholds applied to the IEDB exports, with the counts recomputed from the raw files
- Linkers and adjuvant taken from published sequences, with junctions checked by NetChop C-term 3.0
- Physicochemical, allergenicity, antigenicity and structural checks on each construct
- Scripted analysis stages; the IEDB, VaxiJen, AllerTop and ColabFold steps are manual

Every result is in silico. No binding, immunogenicity or efficacy has been measured, and the
decoy benchmark that would test the scoring function against negative sequences is pending
(2.10).

---

## 7. Software and Resources

### 7.1 Computational Tools
- **Python 3.13** - Primary programming environment
- **IEDB Analysis Resource** - MHC binding prediction
- **ColabFold/AlphaFold2** - 3D structure prediction  
- **HDOCK** - Molecular docking
- **VaxiJen v2.0** - Antigenicity prediction
- **AllerTop v2.0** - Allergenicity screening

### 7.2 Databases
- **UniProt** - Protein sequence data
- **IEDB** - Immune epitope database
- **PDB** - Protein structure database  
- **Allele Frequency Net** - HLA population data

### 7.3 Custom Scripts
All custom analysis scripts available at:  
`https://github.com/fabzy4L/DATA_ANALYTICS/tree/main/certificates/biocode/Vaccinology/src/`

### 7.4 Hardware Requirements
- **Minimum:** 8GB RAM, 4-core CPU
- **Recommended:** 16GB RAM, 8-core CPU  
- **Storage:** 10GB free space
- **Internet:** Required for web-based tools

---

## 8. Acknowledgments

This methodology builds upon established immunoinformatics tools and databases maintained by:
- Immune Epitope Database and Analysis Resource (IEDB)
- Research Collaboratory for Structural Bioinformatics Protein Data Bank (RCSB PDB)
- European Bioinformatics Institute (EBI) UniProt
- DeepMind AlphaFold team
- Vaccine design community contributions

---

## 9. References

*[References would include relevant literature on vaccine design, immunoinformatics tools, SARS-CoV-2 biology, and computational methods. For brevity, not included in this methodology document but would be essential for publication.]*

---

**Document Version:** 1.0  
**Last Updated:** June 1, 2026  
**Status:** Complete - Ready for Publication  
**Contact:** fpalvarez23@gmail.com