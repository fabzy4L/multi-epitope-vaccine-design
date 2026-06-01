# Quick Start Guide - Local NetMHC Pipeline

**Goal:** Process 4,274 SARS-CoV-2 epitopes in 20 minutes instead of 24-48 hours

## 🚀 **One-Command Pipeline**

```bash
# Complete epitope prediction pipeline
./run_netmhc_pipeline.sh
```

**That's it!** The script handles everything automatically.

---

## 📋 **Manual Steps (If One-Command Fails)**

### **Step 1: Download NetMHC Tools (5 minutes - one-time)**
```bash
# Open download instructions
cat tools/netmhc/DOWNLOAD_INSTRUCTIONS.md

# Download to: tools/netmhc/downloads/
# - netMHCpan-4.1.Linux.tar.gz
# - netMHCIIpan-4.0.Linux.tar.gz
```

### **Step 2: Setup and Run (15 minutes)**
```bash
# Install tools
bash scripts/setup_local_netmhc.sh

# Activate environment
source scripts/activate_netmhc.sh

# Run predictions
python scripts/run_local_predictions.py
```

---

## 📊 **Expected Results**

```
🧬 Local NetMHC Epitope Processor
==================================================
✅ NetMHC installation verified
📁 Found 9 batch files (5 MHC-I + 4 MHC-II)

🔬 Processing MHC-I epitopes...
✅ MHC-I length 8 complete → 678 epitopes processed
✅ MHC-I length 9 complete → 677 epitopes processed
...

📊 NETMHC PROCESSING SUMMARY
Total predictions: 45,847
Strong binders (≤500/1000nM): 8,756 (19.1%)
Very strong binders (≤50/100nM): 2,143 (4.7%)

🎯 Ready for Stage 03: VaxiJen/AllerTop/ProtParam analysis!
```

---

## 📁 **What Gets Created**

```
results/netmhc_local/
├── mhc_i/                           ← MHC-I predictions
│   ├── mhc_i_length_8_results.csv   ← ~7,500 predictions
│   ├── mhc_i_length_9_results.csv   ← ~7,500 predictions
│   └── ...
├── mhc_ii/                          ← MHC-II predictions  
│   ├── mhc_ii_length_12_results.csv ← ~1,800 predictions
│   └── ...
└── processing_summary.csv           ← Overall stats
```

**File Format:**
- `epitope`: PEPTIDE sequence
- `hla_allele`: HLA-A02:01, DRB1_0101, etc.
- `ic50_nm`: Binding strength (lower = stronger)
- `rank_percent`: Percentile rank (lower = better)

---

## 🎯 **Success Criteria**

✅ **Complete when you see:**
- Total predictions: ~45,000
- Strong binder rate: 15-25%
- 9 result CSV files created
- Processing time: <20 minutes

✅ **Ready for next stage:**
- Stage 03: VaxiJen antigenicity scoring
- AllerTop allergenicity filtering  
- Population coverage analysis
- Multi-epitope construct design

---

**🚀 Get Results in 20 Minutes vs 24-48 Hours via IEDB**