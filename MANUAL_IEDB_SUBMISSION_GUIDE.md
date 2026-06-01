# Manual IEDB Submission Guide for SARS-CoV-2 Epitope Prediction
**Target:** SARS-CoV-2 S1 Domain Epitope Analysis  
**Tools:** IEDB MHC-I and MHC-II Prediction Tools  
**Duration:** 4-6 hours total (including wait times)  
**Audience:** Anyone with basic bioinformatics knowledge

---

## 📋 **Prerequisites**

### **Required Files**
- ✅ **S1 Domain Sequence**: `analysis/sars_cov2/02_epitope_prediction/sars_cov2_s1_domain.fasta`
- ✅ **Browser**: Chrome, Firefox, or Safari (modern browser required)
- ✅ **Spreadsheet Software**: Excel, Google Sheets, or LibreOffice Calc
- ✅ **Text Editor**: Notepad++, VS Code, or any plain text editor

### **HLA Alleles to Test** (Copy This List)
```
MHC-I Alleles:
HLA-A*02:01, HLA-A*01:01, HLA-A*03:01, HLA-A*24:02, HLA-B*07:02, HLA-B*08:01, HLA-B*35:01, HLA-B*40:01, HLA-C*07:01, HLA-C*07:02, HLA-C*06:02

MHC-II Alleles:
DRB1*01:01, DRB1*15:01, DRB1*04:01, DRB1*07:01, DRB1*03:01, DRB1*11:01, DRB1*13:01, DRB1*09:01
```

---

## 🧬 **Step 1: Prepare the S1 Sequence**

### **1.1 Extract Sequence from FASTA File**
1. Open `analysis/sars_cov2/02_epitope_prediction/sars_cov2_s1_domain.fasta`
2. Copy the sequence (everything after the `>` header line)
3. Remove any line breaks to create one continuous sequence
4. Save in a text file as `s1_sequence_for_iedb.txt`

**Example Format:**
```
>sars_cov2_s1_domain
MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAIHVSGTNGTKR
FDNPVLPFNDGVYFASTEKSNIIRGWIFGTTLDSKTQSLLIVNNATNVVIKVCEFQFCNDPFLGVYYHKNNKSWMESE
FRVYSSANNCTFEYVSQPFLMDLEGKQGNFKNLREFVFKNIDGYFKIYSKHTPINLVRDLPQGFSALEPLVDLPIGINI
TRFQTLLALHRSYLTPGDSSSGWTAGAAAYYVGYLQPRTFLLKYNENGTITDAVDCALDPLSETKCTLKSFTVEKGIY
QTSNFRVQPTESIVRFPNITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLC
FTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDIS
TEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNFNFNGL
KGTGVLTESNKKFLPFQQFGRDIADTTDAVRDPQTLEILDITPCSFGGVSVITPGTNTSNQVAVLYQDVNCTEVPVAI
HADQLTPTWRVYSTGSNVFQTRAGCLIGAEHVNNSYECDIPIGAGICASYQTQTNSPRRARSVASQSIIAYTMSLGAE
NSVAYSNNSIAIPTNFTISVTTEILPVSMTKTSVDCTMYICGDSTECSNLLLQYGSFCTQLNRALTGIAVEQDKNTQE
VFAQVKQIYKTPPIKDFGGFNFSQILPDPSKPSKRSFIEDLLFNKVTLADAGFIKQYGDCLGDIAARDLICAQKFNG
LTVLPPLLTDEMIAQYTSALLAGTITSGWTFGAGAALQIPFAMQMAYRFNGIGVTQNVLYENQKLIANQFNSAIGKIQ
DSLSSTASALGKLQDVVNQNAQALNTLVKQLSSNFGAISSVLNDILSRLDKVEAEVQIDRLITGRLQSLQTYVTQQL
IRAAEIRASANLAATKMSECVLGQSKRVDFCGKGYHLMSFPQSAPHGVVFLHVTYVPAQEKNFTTAPAICHDGKAH
FPREGVFVSNGTHWFVTQRNFYEPQIITTDNTFVSGNCDVVIGIVNNTVYDPLQPELDSFKEELDKYFKNHTSPDVD
LGDISGINASVVNIQKEIDRLNEVAKNLNESLIDLQELGKYEQYIKWPWYIWLGFIAGLIAIVMVTIMLCCMTSCCS
CLKGCCSCGSCCKFDEDDSEPVLKGVKLHYT
```

### **1.2 Create Epitope Windows** (Optional - For Focused Analysis)
If you want to test specific regions instead of the full sequence:

**For MHC-I (8-12 amino acids):**
- Take overlapping 9-mer peptides every 3-5 amino acids
- Example: MFVFLVLLP, FLVLLPLVS, LVLLPLVSS, etc.

**For MHC-II (12-20 amino acids):**
- Take overlapping 15-mer peptides every 5 amino acids
- Example: MFVFLVLLPLVSSQC, LLVLLPLVSSQCVNL, etc.

---

## 🔬 **Step 2: MHC-I Prediction (CD8+ T-cell Epitopes)**

### **2.1 Access IEDB MHC-I Tool**
1. Go to **[http://tools.iedb.org/mhci/](http://tools.iedb.org/mhci/)**
2. You should see the "MHC-I Binding Prediction" page

### **2.2 Configure Prediction Settings**

#### **Method Selection**
1. **Prediction Method**: Select **"NetMHCpan BA"** (recommended)
   - This is the most accurate binding affinity prediction method
   - Uses artificial neural networks trained on binding data

#### **Sequence Input**
1. **Input Type**: Select **"Paste sequence(s)"**
2. **Sequence Format**: Leave as **"Auto detect"**
3. **Sequence Text Box**: Paste your S1 sequence from Step 1.1

#### **Allele Selection** 
1. Click **"Select Alleles"**
2. **Species**: Select **"Human"**
3. **Allele Input Method**: Choose **"Select from list"**
4. **Select the following alleles** (check each box):
   - **HLA-A*02:01** ⭐ (most common globally)
   - **HLA-A*01:01**
   - **HLA-A*03:01** 
   - **HLA-A*24:02**
   - **HLA-B*07:02**
   - **HLA-B*08:01**
   - **HLA-B*35:01**
   - **HLA-B*40:01**
   - **HLA-C*07:01**
   - **HLA-C*07:02**
   - **HLA-C*06:02**
5. Click **"Select"** to confirm

#### **Peptide Length**
1. **Length**: Select **"8, 9, 10, 11, 12"** (covers all MHC-I epitope lengths)

#### **Output Options**
1. **Sort by**: Select **"IC50"** (binding affinity)
2. **Show**: Select **"All results"**

### **2.3 Submit and Monitor**

1. **Review Settings**: Ensure all settings are correct
2. Click **"Submit"** button
3. **Submission Confirmation**: 
   - You'll see a job submission page
   - **Save the Job ID** (format: IEDB-xxxxxxxx)
   - **Bookmark the results page** URL

4. **Processing Time**: 
   - **Expected**: 30-60 minutes for full S1 sequence
   - **Status**: Page will refresh automatically
   - **Notification**: Leave tab open or check back periodically

### **2.4 Download MHC-I Results**

Once processing completes:

1. **Download Options**: Click **"Download Results"**
2. **File Format**: Select **"CSV"** 
3. **Save As**: `mhc_i_predictions_sars_cov2_s1.csv`
4. **Backup**: Also download **"Tab-delimited"** as backup

---

## 🧬 **Step 3: MHC-II Prediction (CD4+ T-helper Epitopes)**

### **3.1 Access IEDB MHC-II Tool**
1. Go to **[http://tools.iedb.org/mhcii/](http://tools.iedb.org/mhcii/)**
2. You should see the "MHC-II Binding Prediction" page

### **3.2 Configure Prediction Settings**

#### **Method Selection**
1. **Prediction Method**: Select **"NetMHCIIpan BA"** (recommended)
   - Most accurate for HLA-DR, HLA-DQ, and HLA-DP alleles

#### **Sequence Input**
1. **Input Type**: Select **"Paste sequence(s)"**
2. **Sequence Text Box**: Paste the same S1 sequence from Step 1.1

#### **Allele Selection**
1. Click **"Select Alleles"**
2. **Species**: Select **"Human"**
3. **Select the following HLA-DR alleles** (most important for T-helper responses):
   - **DRB1*01:01** ⭐ (highest frequency worldwide)
   - **DRB1*15:01**
   - **DRB1*04:01**
   - **DRB1*07:01**
   - **DRB1*03:01**
   - **DRB1*11:01**
   - **DRB1*13:01**
   - **DRB1*09:01**
4. Click **"Select"** to confirm

#### **Peptide Length**
1. **Length**: Select **"15"** (standard for MHC-II epitopes)
   - You can also add **"12, 16, 17, 18"** for comprehensive coverage

#### **Output Options**
1. **Sort by**: Select **"IC50"**
2. **Show**: Select **"All results"**

### **3.3 Submit and Monitor**

1. Click **"Submit"** button
2. **Save the Job ID** for MHC-II prediction
3. **Processing Time**: 45-90 minutes for full S1 sequence
4. **Monitor**: Check status periodically

### **3.4 Download MHC-II Results**

1. **Download**: Click **"Download Results"** when complete
2. **Format**: Select **"CSV"**
3. **Save As**: `mhc_ii_predictions_sars_cov2_s1.csv`

---

## 📊 **Step 4: Result Processing and Analysis**

### **4.1 Organize Downloaded Files**
Create folder structure:
```
results/
├── mhc_i_predictions_sars_cov2_s1.csv
├── mhc_ii_predictions_sars_cov2_s1.csv
├── mhc_i_backup.txt
└── mhc_ii_backup.txt
```

### **4.2 Open Results in Spreadsheet**

#### **MHC-I Results Columns (Important Ones)**
- **Peptide**: The epitope sequence
- **Start**: Position in S1 sequence  
- **End**: End position
- **Allele**: HLA allele tested
- **IC50**: Binding affinity (nM) - **Lower is better**
- **Rank**: Percentile rank - **Lower is better**

#### **MHC-II Results Columns**
- **Peptide**: The epitope sequence
- **Start/End**: Position in S1 sequence
- **Allele**: HLA-DR allele tested  
- **IC50**: Binding affinity (nM) - **Lower is better**
- **Core**: 9-amino acid binding core

### **4.3 Filter for Strong Binders**

#### **MHC-I Strong Binders** (Create Filter)
```
Filter Criteria:
- IC50 ≤ 50 nM (very strong)
- IC50 ≤ 500 nM (strong)
- Rank ≤ 2% (strong binding percentile)
```

#### **MHC-II Strong Binders**
```
Filter Criteria:  
- IC50 ≤ 100 nM (very strong)
- IC50 ≤ 1000 nM (strong)
```

### **4.4 Export Filtered Results**
1. **Create new sheets**: `MHC-I_strong_binders` and `MHC-II_strong_binders`
2. **Copy filtered data** to new sheets
3. **Save as**: `epitope_candidates_filtered.xlsx`

---

## 📈 **Step 5: Summary Analysis**

### **5.1 Count Summary Statistics**
Create a summary table:

| Metric | MHC-I | MHC-II |
|--------|-------|--------|
| Total Predictions | [count] | [count] |
| Strong Binders (≤500/1000nM) | [count] | [count] |
| Very Strong Binders (≤50/100nM) | [count] | [count] |
| Unique Epitopes | [count] | [count] |
| Best IC50 Value | [min value] | [min value] |

### **5.2 Identify Top Candidates**
**Selection Criteria:**
1. **IC50 < 50 nM** (MHC-I) or **< 100 nM** (MHC-II)
2. **Binds multiple HLA alleles** (promiscuous binding)
3. **Good population coverage** (alleles with high global frequency)
4. **Reasonable length** (8-12 aa for MHC-I, 12-20 aa for MHC-II)

### **5.3 Create Final Candidate List**
Export top 20-50 epitopes for each class:
- **File**: `final_epitope_candidates.csv`
- **Columns**: `epitope_id, sequence, type, best_ic50, num_alleles_binding, population_coverage`

---

## 💾 **Step 6: File Organization for Pipeline Integration**

### **6.1 Standardize File Names**
Rename files to match pipeline expectations:
```
analysis/sars_cov2/02_epitope_prediction/processed_data/
├── mhc_i_predictions.csv            ← Renamed from IEDB download
├── mhc_ii_predictions.csv           ← Renamed from IEDB download  
├── epitope_selection_summary.xlsx   ← Your analysis spreadsheet
└── final_epitope_candidates.csv     ← Top candidates for construct
```

### **6.2 Add Metadata Headers**
Add to the beginning of each CSV file:
```csv
# File: mhc_i_predictions.csv
# Created: [DATE]
# Created by: Manual IEDB submission
# Data source: IEDB NetMHCpan-4.1
# Sequence: SARS-CoV-2 S1 domain (685 amino acids)
# HLA alleles tested: 11 major global alleles
# Total predictions: [COUNT]
epitope_id,sequence,start_pos,end_pos,hla_allele,ic50_nm,rank_percent...
```

---

## ⏱️ **Timeline Summary**

| Step | Duration | Can Do Parallel |
|------|----------|-----------------|
| **Sequence Prep** | 15 min | - |
| **MHC-I Submission** | 10 min | ✅ |
| **MHC-II Submission** | 10 min | ✅ |
| **MHC-I Processing** | 30-60 min | ✅ Wait time |
| **MHC-II Processing** | 45-90 min | ✅ Wait time |
| **Results Analysis** | 60-90 min | - |
| **File Organization** | 30 min | - |
| **Total Time** | **3-5 hours** | **2 hours active work** |

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"Job Failed" Error**
- **Cause**: Sequence too long or contains invalid characters
- **Solution**: 
  1. Check sequence for non-amino acid characters
  2. Try smaller sequence chunks (first 300 amino acids)
  3. Use FASTA format with proper header

#### **"No Results" After Long Wait**
- **Cause**: Server overload or network timeout
- **Solution**:
  1. Check job status page directly
  2. Try during off-peak hours (early morning/late evening)
  3. Contact IEDB support if issue persists

#### **Results Too Large to Process**
- **Cause**: Full S1 sequence generates >10,000 predictions
- **Solution**:
  1. Focus on specific regions (RBD domain: amino acids 319-541)
  2. Use fewer HLA alleles initially
  3. Process in chunks

### **Quality Control Checklist**
- [ ] Sequence matches original S1 domain
- [ ] All required HLA alleles tested
- [ ] Results downloaded in CSV format
- [ ] Strong binders identified and counted
- [ ] Files properly renamed and organized
- [ ] Metadata added to result files

---

## 📚 **Next Steps After Manual Submission**

### **Integration with Pipeline**
1. **Continue to Stage 03**: Use results for VaxiJen, AllerTop, ProtParam analysis
2. **Population Coverage**: Calculate using HLA frequency data
3. **Construct Design**: Select top epitopes for vaccine design
4. **Structural Analysis**: Proceed with ColabFold and docking

### **Documentation**
1. **Record job IDs**: For reproducibility
2. **Note any modifications**: Sequence changes, allele selections
3. **Save screenshots**: Of submission pages for methods documentation

---

## ✅ **Success Criteria**

By the end of this process, you should have:
- [ ] **MHC-I predictions**: 5,000+ predictions across 11 alleles
- [ ] **MHC-II predictions**: 3,000+ predictions across 8 alleles  
- [ ] **Strong binders identified**: 50-200 high-affinity epitopes
- [ ] **Organized results**: Properly formatted for next pipeline stage
- [ ] **Analysis summary**: Statistics and top candidates selected

---

**Manual Submission Guide Complete**  
**Estimated Total Time**: 3-5 hours  
**Active Work Time**: 2 hours  
**Results**: Publication-ready epitope predictions for SARS-CoV-2 vaccine design

**Next**: Proceed with Stage 03 candidate scoring using VaxiJen, AllerTop, and ProtParam analysis.