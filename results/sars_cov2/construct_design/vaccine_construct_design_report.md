# Multi-Epitope Vaccine Construct Design Report

**Generated:** 2026-06-01
**Pipeline:** SARS-CoV-2 S1 Domain Vaccinology
**Target:** Multi-epitope vaccine construct

## Design Strategy

### Construct Architecture
1. **N-terminal Adjuvant**: TLR4 agonist (RS09) for immune activation
2. **MHC-II Epitopes**: CD4+ T-cell response with GPGPG linkers
3. **Domain Separator**: KK for processing independence
4. **MHC-I Epitopes**: CD8+ T-cell response with AAY linkers
5. **C-terminal Tags**: Stability and purification elements

## Selected Epitopes Summary

### MHC-I Epitopes (CD8+ T-cell targets)
| Peptide | HLA Allele | IC50 (nM) | Length |
|---------|------------|-----------|--------|
| LPFNDGVYF | HLA-B*35:01 | 4.12 | 9 |
| RLFRKSNLK | HLA-A*03:01 | 4.82 | 9 |
| FPNITNLCPF | HLA-B*35:01 | 5.40 | 10 |
| VLYNSASFSTFK | HLA-A*03:01 | 7.53 | 12 |
| VASQSIIAY | HLA-B*35:01 | 7.81 | 9 |
| LYNSASFSTF | HLA-A*24:02 | 8.16 | 10 |

### MHC-II Epitopes (CD4+ T-cell targets)
| Peptide | HLA Allele | IC50 (nM) | Length |
|---------|------------|-----------|--------|
| QTLLALHRSYLTPGD | HLA-DRB1*15:01 | 9.87 | 15 |
| INITRFQTLLALHRS | HLA-DRB1*15:01 | 11.23 | 15 |
| QTLLALHRSYLT | HLA-DRB1*15:01 | 45.82 | 12 |
| PIGINITRFQTLLALHRS | HLA-DRB1*15:01 | 48.82 | 18 |

## Construct Designs

### Version_1_Standard

**Sequence (171 amino acids):**
```
APPHALSGGGSQTLLALHRSYLTPGDGPGPGINITRFQTLLALHRSGPGPGQTLLALHRSYLTGPGPGPIGINITRFQTLLALHRSKKLPFNDGVYFAAYRLFRKSNLKAAYFPNITNLCPFAAYVLYNSASFSTFKAAYVASQSIIAYAAYLYNSASFSTFGGGSPAPAP
```

**Properties:**
- Length: 171 amino acids
- Estimated MW: 18810 Da (18.8 kDa)
- Hydrophobic ratio: 47.37%
- Solubility prediction: moderate

### Version_2_Alternating

**Sequence (172 amino acids):**
```
APPHALSGGGSQTLLALHRSYLTPGDAAYLPFNDGVYFGPGPGINITRFQTLLALHRSAAYRLFRKSNLKGPGPGQTLLALHRSYLTAAYFPNITNLCPFGPGPGPIGINITRFQTLLALHRSAAYVLYNSASFSTFKAAYVASQSIIAYAAYLYNSASFSTFGGGSPAPAP
```

**Properties:**
- Length: 172 amino acids
- Estimated MW: 18920 Da (18.9 kDa)
- Hydrophobic ratio: 48.26%
- Solubility prediction: moderate

### Version_3_Optimized

**Sequence (144 amino acids):**
```
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGDGPGPGINITRFQTLLALHRSKKGPGPGKKLPFNDGVYFAAYRLFRKSNLKAAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
```

**Properties:**
- Length: 144 amino acids
- Estimated MW: 15840 Da (15.8 kDa)
- Hydrophobic ratio: 45.83%
- Solubility prediction: moderate

