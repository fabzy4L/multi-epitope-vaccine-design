# Epitope Selection Criteria: Standardized Guidelines
**For:** Claude + Gemini Collaborative Analysis  
**Purpose:** Consistent epitope evaluation across AI agents  
**Version:** 1.0

---

## 🎯 **B-cell Epitope Criteria**

### **Primary Requirements**
- **Length**: 8-20 amino acids (optimal: 12-16)
- **Antigenicity**: VaxiJen score ≥ 0.4 (threshold for probable antigen)
- **Allergenicity**: AllerTop score < 0.5 (non-allergenic classification)
- **Hydrophobicity**: GRAVY score between -1.0 and 0.5 (balanced hydrophilicity)
- **Surface accessibility**: > 60% predicted surface exposure

### **Secondary Criteria**
- **Conservation**: Present in ≥ 85% of analyzed SARS-CoV-2 variants
- **Flexibility**: B-factor prediction > 0.8 (flexible regions preferred)
- **Charge distribution**: Avoid regions with excessive positive/negative clustering
- **Glycosylation sites**: Exclude N-linked glycosylation motifs (NXT/NXS)

---

## 🧬 **MHC-I (CD8+) Epitope Criteria**

### **Primary Requirements**  
- **Length**: 8-12 amino acids (strict requirement)
- **HLA binding**: IC50 ≤ 500 nM for at least 2 major HLA-A/B alleles
- **Population coverage**: Covers ≥ 70% of target population (global or specific)
- **Proteasomal cleavage**: C-terminal cleavage score ≥ 0.5
- **TAP transport**: TAP binding score ≥ 0.5

### **HLA Allele Priorities**
1. **High frequency global**: HLA-A*02:01, HLA-A*01:01, HLA-B*07:02
2. **Regional coverage**: Population-specific high-frequency alleles
3. **Promiscuous binders**: Epitopes binding multiple HLA alleles

---

## 🔬 **MHC-II (CD4+) Epitope Criteria**

### **Primary Requirements**
- **Length**: 12-20 amino acids (optimal: 15-17)  
- **HLA-DR binding**: IC50 ≤ 1000 nM for at least 2 major HLA-DR alleles
- **Core binding region**: 9-amino acid core with anchor residues
- **Stability**: Predicted binding half-life > 1 hour
- **Processing**: No internal cleavage sites in core region

### **HLA-DR Allele Priorities**
1. **DRB1*01:01**: Most frequent worldwide (20-25% frequency)
2. **DRB1*15:01**: High frequency in European populations  
3. **DRB1*04:01**: Significant in Asian populations
4. **DRB1*07:01**: Broad population coverage

---

## 📊 **Population Coverage Requirements**

### **Target Coverage Metrics**
- **Global coverage**: ≥ 90% for combined epitope set
- **Regional coverage**: ≥ 95% for major population groups
- **Individual HLA coverage**: Each epitope covers ≥ 10% of target population
- **Redundancy factor**: 2-3 epitopes per immune pathway (backup coverage)

### **Coverage Calculation Method**
```python
# Population coverage formula for multiple epitopes
coverage = 1 - Π(1 - individual_epitope_coverage)
# Where Π is the product operator across all epitopes
```

---

## 🧪 **Physicochemical Constraints**

### **Acceptable Ranges**
- **Molecular weight**: 800-3000 Da (size limitations for processing)
- **Isoelectric point**: 4.0-11.0 (avoid extreme pH sensitivity)  
- **Instability index**: < 40 (stable under physiological conditions)
- **Aliphatic index**: 40-120 (appropriate hydrophobic character)
- **Half-life**: > 1 hour in mammalian cells (stability requirement)

### **Exclusion Criteria**
- **Cysteine content**: > 2 cysteines per epitope (disulfide complications)
- **Proline clusters**: > 3 consecutive prolines (rigid structure issues)
- **Repeated sequences**: > 50% sequence similarity to human proteins
- **Toxic motifs**: Known cytotoxic or apoptosis-inducing sequences

---

## 🔗 **Linker Requirements**

### **Standard Linker Sequences**
- **B-cell linkers**: GPGPG (flexible, non-immunogenic)
- **MHC-I linkers**: AAY (prevents junctional epitopes)  
- **MHC-II linkers**: GPGPG (maintains peptide presentation)
- **Domain separators**: KK (clear functional boundaries)

### **Linker Validation**
- **Junctional epitope check**: No new epitopes formed at linker junctions
- **Cleavage site avoidance**: No protease recognition sites in linkers
- **Length optimization**: Minimum spacing for independent folding

---

## 🎯 **Scoring Integration**

### **Weighted Scoring System**
```python
epitope_score = (
    0.30 * antigenicity_score +      # Primary immunogenic potential
    0.25 * population_coverage +      # Public health impact  
    0.20 * binding_affinity +         # Immune recognition strength
    0.15 * conservation_score +       # Variant robustness
    0.10 * physicochemical_score      # Stability and safety
)
```

### **Minimum Thresholds**
- **Combined score**: ≥ 0.6 for inclusion in construct
- **Individual criteria**: Must pass all primary requirements
- **Safety check**: Zero tolerance for allergenicity or toxicity flags

---

## 🔍 **AI-Specific Implementation Notes**

### **For Claude** (Code Implementation)
```python
# Validation function template
def validate_epitope(sequence, prediction_data):
    checks = {
        'length': check_length_range(sequence, 8, 20),
        'antigenicity': prediction_data['vaxijen'] >= 0.4,
        'allergenicity': prediction_data['allertop'] < 0.5,
        'population_coverage': prediction_data['coverage'] >= 0.7
    }
    return all(checks.values()), checks
```

### **For Gemini** (Statistical Analysis)
```python
# Coverage calculation template  
def calculate_population_coverage(epitope_list, hla_frequencies):
    coverage_matrix = compute_hla_binding_matrix(epitope_list)
    population_coverage = 1 - np.prod(1 - coverage_matrix, axis=0)
    return population_coverage.mean()
```

---

## ✅ **Quality Control Checklist**

### **Pre-Selection Validation**
- [ ] All prediction scores within acceptable ranges
- [ ] Population coverage targets met
- [ ] No safety flag violations
- [ ] Physicochemical properties validated

### **Post-Selection Verification**  
- [ ] Construct-level population coverage ≥ 90%
- [ ] No junctional epitope formation
- [ ] Balanced immune pathway representation
- [ ] Literature validation for similar epitopes

---

**Updated:** 2026-05-25  
**Reviewers:** Claude (Technical) + Gemini (Statistical)  
**Status:** Approved for collaborative implementation