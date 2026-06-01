# Data Formats Specification: Claude + Gemini Handoffs
**Purpose:** Standardized data exchange for collaborative AI workflow  
**Scope:** All intermediate files and API responses  
**Version:** 1.0

---

## 📁 **Directory Structure Standards**

```
analysis/sars_cov2/
├── 02_epitope_prediction/
│   ├── raw_outputs/              # Direct tool outputs (preserve original)
│   ├── processed_data/           # Standardized CSV/JSON formats  
│   └── validation_reports/       # Quality control summaries
├── 03_candidate_scoring/  
│   ├── scoring_matrices/         # Individual tool scores
│   ├── integrated_scores/        # Combined scoring results
│   └── selection_criteria/       # Applied filters and thresholds
└── 05_docking_simulation/
    ├── structure_files/          # PDB files and conformations
    ├── docking_results/          # Raw docking outputs
    └── binding_analysis/         # Processed interaction data
```

---

## 🧬 **Epitope Prediction Data Formats**

### **MHC-I Prediction Output** 
**File:** `mhc_i_predictions.csv`
```csv
epitope_id,sequence,start_pos,end_pos,hla_allele,ic50_nm,rank_percent,binding_level
S1_001,YLQPRTFLL,19,27,HLA-A*02:01,125.5,0.15,strong
S1_002,KIADYNYKL,45,53,HLA-A*02:01,890.2,1.25,weak
S1_003,FSTFKCYGV,78,86,HLA-B*07:02,45.8,0.08,strong
```

**Required Columns:**
- `epitope_id`: Unique identifier (format: S1_XXX)
- `sequence`: Amino acid sequence (single letter code)
- `start_pos`, `end_pos`: Position in source protein (1-based indexing)
- `hla_allele`: Standard nomenclature (HLA-X*XX:XX)
- `ic50_nm`: Binding affinity in nanomolar
- `rank_percent`: Percentile rank (lower = better)
- `binding_level`: strong/weak/non-binding classification

### **MHC-II Prediction Output**
**File:** `mhc_ii_predictions.csv`
```csv
epitope_id,sequence,start_pos,end_pos,hla_allele,ic50_nm,core_sequence,binding_level
S1_201,KIADYNYKLPDDFTGC,45,60,DRB1*01:01,245.8,IADYNYKLP,strong
S1_202,FSTFKCYGVSPTKLNG,78,93,DRB1*15:01,1250.4,KCYGVSPTK,weak
```

**Additional Columns:**
- `core_sequence`: 9-amino acid binding core
- Extended length range: 12-20 amino acids

---

## 📊 **Scoring and Analysis Formats**

### **Population Coverage Analysis**
**File:** `population_coverage_analysis.csv`
```csv
epitope_id,sequence,global_coverage,european_coverage,asian_coverage,african_coverage,americas_coverage
S1_001,YLQPRTFLL,0.234,0.445,0.189,0.156,0.298
S1_003,FSTFKCYGV,0.187,0.234,0.267,0.123,0.201
```

### **Integrated Scoring Matrix**
**File:** `integrated_epitope_scores.csv`
```csv
epitope_id,antigenicity_score,allergenicity_score,population_coverage,conservation_score,final_score,selection_status
S1_001,0.72,0.15,0.234,0.89,0.67,selected
S1_002,0.45,0.23,0.145,0.76,0.52,rejected
S1_003,0.81,0.08,0.187,0.94,0.73,selected
```

---

## 🧪 **Structural Analysis Formats**

### **Structure Quality Assessment**
**File:** `structure_quality_report.json`
```json
{
  "construct_id": "vaccine_construct_v1",
  "prediction_confidence": 0.87,
  "structure_metrics": {
    "clash_score": 2.1,
    "ramachandran_favored": 0.94,
    "ramachandran_outliers": 0.02,
    "rotamer_outliers": 0.03
  },
  "domain_analysis": {
    "structured_regions": 0.78,
    "disordered_regions": 0.22,
    "secondary_structure": {
      "alpha_helix": 0.45,
      "beta_sheet": 0.23,
      "coil": 0.32
    }
  }
}
```

### **Docking Results Format**
**File:** `docking_results.csv`
```csv
complex_id,receptor,ligand,binding_score,rank,interface_area,binding_residues
TLR4_001,3FXI_chain_A,vaccine_construct,-8.2,1,1245.7,"A:LYS45;A:GLU78;A:TRP123"
MHC1_002,1HHH_chain_A,vaccine_construct,-6.8,1,987.3,"A:TYR56;A:PHE89;A:LEU134"
```

---

## 🔧 **API Integration Formats**

### **IEDB Submission Payload**
```json
{
  "method": "netmhcpan",
  "sequence_text": "YLQPRTFLLKIADYNYKL",
  "allele": ["HLA-A*02:01", "HLA-A*01:01", "HLA-B*07:02"],
  "length": "8,9,10,11",
  "species": "human"
}
```

### **HDOCK Submission Format**
```json
{
  "receptor_pdb": "3FXI_clean.pdb",
  "ligand_pdb": "vaccine_construct.pdb", 
  "binding_site": "auto",
  "cluster_rmsd": 2.0,
  "max_models": 100
}
```

---

## 📈 **Visualization Data Formats**

### **Coverage Heatmap Data**
**File:** `coverage_heatmap_data.csv`
```csv
population,epitope_S1_001,epitope_S1_003,epitope_S1_005,combined_coverage
European,0.445,0.234,0.567,0.892
Asian,0.189,0.267,0.445,0.756
African,0.156,0.123,0.334,0.623
Americas,0.298,0.201,0.456,0.798
```

### **Binding Affinity Distribution**
**File:** `binding_affinity_stats.json`
```json
{
  "mhc_i_distribution": {
    "mean_ic50": 245.7,
    "median_ic50": 189.3,
    "percentiles": {"25": 78.5, "75": 345.2},
    "strong_binders": 23,
    "weak_binders": 15
  },
  "mhc_ii_distribution": {
    "mean_ic50": 578.9,
    "median_ic50": 445.6,
    "strong_binders": 18,
    "weak_binders": 12
  }
}
```

---

## 🔄 **Status Tracking Formats**

### **Pipeline Progress Tracker**
**File:** `pipeline_progress_tracker.json`
```json
{
  "last_updated": "2026-05-25T14:30:00Z",
  "stages": {
    "stage_02_epitope_prediction": {
      "status": "completed",
      "completion_percentage": 100,
      "responsible_ai": "claude",
      "output_files": ["mhc_i_predictions.csv", "mhc_ii_predictions.csv"],
      "quality_check": "passed"
    },
    "stage_03_scoring": {
      "status": "in_progress",  
      "completion_percentage": 60,
      "responsible_ai": "gemini",
      "current_task": "population_coverage_analysis",
      "estimated_completion": "2026-05-25T18:00:00Z"
    }
  }
}
```

### **Quality Control Checklist**
**File:** `quality_control_status.json`
```json
{
  "validation_checks": {
    "data_format_compliance": true,
    "missing_values_check": true,
    "range_validation": true,
    "cross_reference_integrity": true
  },
  "peer_review_status": {
    "claude_review_complete": false,
    "gemini_review_complete": false,
    "conflicts_resolved": false
  },
  "approval_status": {
    "technical_approval": "pending",
    "statistical_approval": "pending", 
    "final_approval": "pending"
  }
}
```

---

## 🔧 **File Naming Conventions**

### **Raw Data Files**
```
# IEDB outputs (preserve original names, add metadata)
iedb_mhc_i_raw_2026-05-25_14-30.txt
iedb_mhc_ii_raw_2026-05-25_14-45.txt

# ColabFold outputs
vaccine_construct_colabfold_result_1.pdb  
vaccine_construct_colabfold_confidence.json

# HDOCK outputs  
hdock_TLR4_result_complex_1.pdb
hdock_MHC1_result_complex_1.pdb
```

### **Processed Data Files**
```
# Standardized analysis outputs
mhc_i_predictions_processed.csv
population_coverage_analysis.csv
epitope_selection_final.csv

# Visualization data
binding_affinity_distribution.json
coverage_heatmap_data.csv
structural_analysis_summary.json
```

---

## 🚨 **Error Handling Standards**

### **Missing Data Encoding**
- **Numerical fields**: `null` (not -1, 0, or empty string)
- **Text fields**: `"N/A"` (consistent placeholder)
- **Boolean fields**: `null` (not false when unknown)

### **Error Reporting Format**
```json
{
  "error_type": "data_validation_failure",
  "timestamp": "2026-05-25T14:30:00Z", 
  "responsible_ai": "claude",
  "stage": "stage_02_epitope_prediction",
  "description": "IC50 values outside expected range (0.1-50000 nM)",
  "affected_files": ["mhc_i_predictions.csv"],
  "suggested_action": "manual_review_required"
}
```

---

## 📝 **Documentation Standards**

### **Metadata Headers** (All CSV files)
```csv
# File: mhc_i_predictions.csv
# Created: 2026-05-25T14:30:00Z  
# Created by: Claude (IEDB automation)
# Reviewed by: Pending Gemini review
# Data source: IEDB NetMHCpan-4.1 API
# Record count: 1,247 predictions
# Quality status: Passed initial validation
epitope_id,sequence,start_pos...
```

### **JSON Schema Validation** 
All JSON files must include schema reference:
```json
{
  "$schema": "./schemas/docking_results_schema.json",
  "data": { ... }
}
```

---

## ✅ **Implementation Checklist**

### **For Claude** (Automation & Integration)
- [ ] Implement CSV parsers with schema validation
- [ ] Build JSON serializers with error handling  
- [ ] Create API response standardization functions
- [ ] Set up automated file naming and metadata

### **For Gemini** (Analysis & Visualization)
- [ ] Configure data import pipelines for standard formats
- [ ] Build visualization templates using standardized data
- [ ] Implement statistical analysis with consistent outputs
- [ ] Create quality control validation scripts

---

**Updated:** 2026-05-25  
**Status:** Ready for collaborative implementation  
**Next Review:** After Phase 1 completion