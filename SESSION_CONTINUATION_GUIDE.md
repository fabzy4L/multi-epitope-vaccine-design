# Session Continuation Guide - IEDB Epitope Submission
**Created:** 2026-05-27  
**Purpose:** Complete guide for continuing IEDB submission process in next session  
**Status:** Ready for immediate execution

---

## 🎯 **Current State Summary**

### **✅ What Was Accomplished**
- **4,274 epitope candidates** generated from SARS-CoV-2 S1 domain
- **9 batch files** created and formatted for IEDB submission  
- **Reproducible NetMHC pipeline** built and committed to git
- **NetMHC tools downloaded** but Windows compatibility issues discovered
- **IEDB submission** chosen as primary execution method
- **Complete tracking system** ready with Excel spreadsheet

### **🚀 What's Ready for Next Session**
- All batch files formatted for copy-paste submission
- HLA allele lists prepared
- Job tracking spreadsheet ready
- Step-by-step submission instructions documented

---

## 📁 **File Locations (Verify These Exist)**

### **Submission Files**
```bash
# Navigate to project directory
cd C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology

# Verify batch files exist
ls epitope_files_for_iedb/batch_submission_files/*.txt

# Expected files:
# mhc-i_length_8_sequences.txt   (678 epitopes)
# mhc-i_length_9_sequences.txt   (677 epitopes)  
# mhc-i_length_10_sequences.txt  (676 epitopes)
# mhc-i_length_11_sequences.txt  (675 epitopes)
# mhc-i_length_12_sequences.txt  (674 epitopes)
# mhc-ii_length_12_sequences.txt (225 epitopes)
# mhc-ii_length_15_sequences.txt (224 epitopes)
# mhc-ii_length_18_sequences.txt (223 epitopes)
# mhc-ii_length_20_sequences.txt (222 epitopes)
```

### **Tracking System**
```bash
# Open job tracking spreadsheet
epitope_files_for_iedb/batch_submission_files/epitope_tracking_spreadsheet.xlsx
```

---

## 🔬 **IEDB Submission Process (Step-by-Step)**

### **Phase 1: MHC-I Submissions (5 files)**

#### **Setup: Open IEDB MHC-I Tool**
1. **Open browser** → http://tools.iedb.org/mhci/
2. **Keep browser tab open** for all MHC-I submissions

#### **For Each MHC-I File (Repeat 5 times):**

**1. Method Selection:**
- **Prediction Method:** Select **"NetMHCpan BA"**

**2. Sequence Input:**
- **Input Type:** Select **"Paste sequences"**  
- **Copy sequences from file:**
  ```bash
  # In terminal, copy file content:
  cat epitope_files_for_iedb/batch_submission_files/mhc-i_length_X_sequences.txt
  
  # Or open in text editor and copy all content
  # Skip comment lines starting with #, copy only sequence data
  ```
- **Paste into IEDB** sequence text box

**3. Allele Selection:**
- Click **"Select Alleles"**
- **Species:** Human  
- **Method:** Select from list
- **Copy-paste these alleles:**
  ```
  HLA-A*02:01, HLA-A*01:01, HLA-A*03:01, HLA-A*24:02, HLA-B*07:02, HLA-B*08:01, HLA-B*35:01, HLA-B*40:01, HLA-C*07:01, HLA-C*07:02, HLA-C*06:02
  ```

**4. Peptide Length:**
- **Length:** Match the filename (8, 9, 10, 11, or 12)

**5. Submit and Track:**
- Click **"Submit"**
- **SAVE JOB ID** (format: IEDB-xxxxxxxx)
- **Record in tracking spreadsheet:**
  - File name
  - Job ID  
  - Submission time
  - Status

#### **MHC-I Submission Order:**
| Order | File | Length | Sequences | Expected Time |
|-------|------|--------|-----------|---------------|
| 1st | `mhc-i_length_8_sequences.txt` | 8 | 678 | 30-60 min |
| 2nd | `mhc-i_length_9_sequences.txt` | 9 | 677 | 30-60 min |
| 3rd | `mhc-i_length_10_sequences.txt` | 10 | 676 | 30-60 min |
| 4th | `mhc-i_length_11_sequences.txt` | 11 | 675 | 30-60 min |
| 5th | `mhc-i_length_12_sequences.txt` | 12 | 674 | 30-60 min |

---

### **Phase 2: MHC-II Submissions (4 files)**

#### **Setup: Open IEDB MHC-II Tool**  
1. **New browser tab** → http://tools.iedb.org/mhcii/
2. **Keep both IEDB tabs open** for monitoring

#### **For Each MHC-II File (Repeat 4 times):**

**1. Method Selection:**
- **Prediction Method:** Select **"NetMHCIIpan BA"**

**2. Sequence Input:**
- **Input Type:** Select **"Paste sequences"**
- **Copy sequences from file** (same process as MHC-I)
- **Paste into IEDB** sequence text box

**3. Allele Selection:**
- Click **"Select Alleles"**
- **Species:** Human
- **Copy-paste these HLA-DR alleles:**
  ```
  DRB1*01:01, DRB1*15:01, DRB1*04:01, DRB1*07:01, DRB1*03:01, DRB1*11:01, DRB1*13:01, DRB1*09:01
  ```

**4. Peptide Length:**
- **Length:** Match the filename (12, 15, 18, or 20)

**5. Submit and Track:**
- Click **"Submit"**
- **SAVE JOB ID**
- **Record in tracking spreadsheet**

#### **MHC-II Submission Order:**
| Order | File | Length | Sequences | Expected Time |
|-------|------|--------|-----------|---------------|
| 6th | `mhc-ii_length_12_sequences.txt` | 12 | 225 | 45-90 min |
| 7th | `mhc-ii_length_15_sequences.txt` | 15 | 224 | 45-90 min |
| 8th | `mhc-ii_length_18_sequences.txt` | 18 | 223 | 45-90 min |
| 9th | `mhc-ii_length_20_sequences.txt` | 20 | 222 | 45-90 min |

---

## 📊 **Job Monitoring and Tracking**

### **Tracking Spreadsheet Management**
**File:** `epitope_tracking_spreadsheet.xlsx`

**Columns to fill:**
- **File Name:** e.g., mhc-i_length_8_sequences.txt
- **Job ID:** e.g., IEDB-12345678  
- **Submission Time:** e.g., 2026-05-28 10:15 AM
- **Status:** Submitted → Processing → Complete → Downloaded
- **Results File:** Link or path to downloaded CSV
- **Notes:** Any issues or observations

### **Job Status Monitoring**
**Check job status periodically:**
1. **IEDB job pages** usually show progress automatically
2. **Bookmark result pages** for easy checking
3. **Email notifications** may be sent when jobs complete
4. **Processing time:** 30-90 minutes per job typically

### **Expected Total Timeline**
- **Active submission work:** 1-2 hours
- **Total processing time:** 8-15 hours (varies by IEDB load)
- **Result availability:** Usually within 24-48 hours

---

## 📥 **Results Download and Organization**

### **When Jobs Complete**
**For each completed job:**

**1. Download Results:**
- Click **"Download Results"** on job page
- **Format:** Select **"CSV"** (preferred)
- **Also download:** Tab-delimited as backup

**2. File Naming Convention:**
```
results/iedb_predictions/
├── mhc_i_length_8_results.csv
├── mhc_i_length_9_results.csv
├── mhc_i_length_10_results.csv
├── mhc_i_length_11_results.csv
├── mhc_i_length_12_results.csv
├── mhc_ii_length_12_results.csv
├── mhc_ii_length_15_results.csv
├── mhc_ii_length_18_results.csv
├── mhc_ii_length_20_results.csv
└── processing_summary.xlsx
```

**3. Update Tracking:**
- Mark job status as **"Downloaded"**
- Record download file path
- Note any issues or observations

---

## 🔍 **Quality Control Checklist**

### **Before Submission**
- [ ] All 9 batch files present and readable
- [ ] Tracking spreadsheet opens correctly
- [ ] IEDB websites accessible
- [ ] HLA allele lists copied and ready
- [ ] Text editor available for viewing sequence files

### **During Submission**
- [ ] Job ID recorded for each submission
- [ ] Correct HLA alleles selected
- [ ] Correct peptide length specified
- [ ] Submission confirmation received
- [ ] Tracking spreadsheet updated immediately

### **After Submission**
- [ ] All 9 jobs submitted successfully
- [ ] All Job IDs recorded and verified
- [ ] Job status pages bookmarked
- [ ] Monitoring schedule established
- [ ] Download folder prepared

---

## ⚠️ **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **"Sequence too long" Error**
- **Cause:** IEDB has sequence length limits
- **Solution:** Submit files in smaller batches if needed
- **Prevention:** Our files are pre-sized correctly

#### **"Invalid allele" Error**  
- **Cause:** Typo in HLA allele selection
- **Solution:** Use exact copy-paste from this guide
- **Check:** HLA-A*02:01 format with asterisk and colon

#### **"Job failed" Status**
- **Cause:** Server overload or input format issue
- **Solution:** Wait 30 minutes and resubmit
- **Note:** Record failed job ID and retry details

#### **Very Long Processing Time (>48 hours)**
- **Cause:** IEDB server overload
- **Solution:** Contact IEDB support with job IDs
- **Alternative:** Consider resubmitting after peak hours

### **Emergency Contacts**
- **IEDB Support:** Via their website contact form
- **Documentation:** Full IEDB API documentation available online

---

## 🧪 **Expected Results Format**

### **CSV File Columns**
**MHC-I Results:**
- `peptide`: Epitope sequence (e.g., MFVFLVLLP)
- `hla_allele`: HLA allele (e.g., HLA-A*02:01)  
- `ic50_nm`: Binding affinity in nM (lower = stronger)
- `rank_percent`: Percentile rank (lower = better)
- `binding_level`: Strong/Weak classification

**MHC-II Results:**
- `peptide`: Epitope sequence  
- `hla_allele`: HLA-DR allele
- `ic50_nm`: Binding affinity in nM
- `rank_percent`: Percentile rank
- `core`: 9-amino acid binding core sequence

### **Success Metrics**
- **Total predictions:** ~45,000 across all files
- **Strong binders (IC50 ≤ 500nM):** Expected 15-25%
- **Very strong binders (IC50 ≤ 50nM):** Expected 3-8%
- **Coverage:** All 4,274 input epitopes analyzed

---

## 🎯 **Next Phase Preparation**

### **After IEDB Results Complete**
**Ready for Stage 03 Analysis:**

**1. Strong Binder Filtering:**
- Filter results for IC50 ≤ 500nM (MHC-I) and ≤ 1000nM (MHC-II)
- Combine results across all lengths
- Remove duplicates and rank by binding strength

**2. VaxiJen Antigenicity Analysis:**
- Input: Top 200-500 strong binders
- Tool: VaxiJen 2.0 online server
- Threshold: Antigenicity score ≥ 0.4

**3. AllerTop Allergenicity Screening:**
- Input: Antigenic epitopes from VaxiJen
- Tool: AllerTop 2.0 online server  
- Filter: Remove allergenic sequences (score > 0.5)

**4. Population Coverage Analysis:**
- Calculate HLA frequency coverage globally
- Optimize epitope selection for maximum coverage
- Target: >90% global population coverage

---

## 🔄 **Session Restart Checklist**

### **At Start of Next Session**
1. **Navigate to project:**
   ```bash
   cd C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology
   ```

2. **Verify files exist:**
   ```bash
   ls epitope_files_for_iedb/batch_submission_files/*.txt
   ```

3. **Open tracking spreadsheet:**
   ```bash
   # Open in Excel or LibreOffice
   epitope_files_for_iedb/batch_submission_files/epitope_tracking_spreadsheet.xlsx
   ```

4. **Open IEDB websites:**
   - http://tools.iedb.org/mhci/
   - http://tools.iedb.org/mhcii/

5. **Start with first file:**
   ```bash
   cat epitope_files_for_iedb/batch_submission_files/mhc-i_length_8_sequences.txt
   ```

### **Success Confirmation**
✅ **All 9 jobs submitted successfully**  
✅ **All Job IDs recorded in tracking spreadsheet**  
✅ **Monitoring schedule established**  
✅ **Download preparation complete**

---

## 📋 **Quick Reference**

### **HLA Alleles (Copy-Ready)**
```
MHC-I: HLA-A*02:01, HLA-A*01:01, HLA-A*03:01, HLA-A*24:02, HLA-B*07:02, HLA-B*08:01, HLA-B*35:01, HLA-B*40:01, HLA-C*07:01, HLA-C*07:02, HLA-C*06:02

MHC-II: DRB1*01:01, DRB1*15:01, DRB1*04:01, DRB1*07:01, DRB1*03:01, DRB1*11:01, DRB1*13:01, DRB1*09:01
```

### **IEDB URLs**
- **MHC-I:** http://tools.iedb.org/mhci/
- **MHC-II:** http://tools.iedb.org/mhcii/

### **File Count Verification**
```bash
# Should show exactly 9 .txt files
ls epitope_files_for_iedb/batch_submission_files/*.txt | wc -l
```

### **Estimated Timeline**
- **Submission work:** 1-2 hours active
- **Processing time:** 24-48 hours waiting  
- **Download:** 30 minutes
- **Total to results:** 1-3 days

---

**📌 START HERE NEXT SESSION:** Begin with MHC-I length 8 submission and work through the checklist systematically.