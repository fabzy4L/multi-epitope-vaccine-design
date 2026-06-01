# IEDB Submission Instructions for Generated Epitope Files

## 📁 Files Created

### **Individual Epitope Files**
- **MHC-I Epitopes**: `mhc_i_epitopes/` (organized by length)
- **MHC-II Epitopes**: `mhc_ii_epitopes/` (organized by length)

### **Batch Submission Files**
- **MHC-I Batches**: Ready-to-paste sequences for IEDB
- **MHC-II Batches**: Ready-to-paste sequences for IEDB
- **Tracking Spreadsheet**: `epitope_tracking_spreadsheet.xlsx`

## 🔬 **Submission Workflow**

### **Step 1: MHC-I Submissions**
1. Go to [http://tools.iedb.org/mhci/](http://tools.iedb.org/mhci/)
2. Select **NetMHCpan BA** method
3. For each length (8, 9, 10, 11, 12):
   - Open `batch_submission_files/mhc-i_length_X_sequences.txt`
   - Copy all sequences (Ctrl+A, Ctrl+C)
   - Paste into IEDB sequence box
   - Select HLA alleles: `HLA-A*02:01, HLA-A*01:01, HLA-A*03:01, HLA-A*24:02, HLA-B*07:02, HLA-B*08:01, HLA-B*35:01, HLA-B*40:01, HLA-C*07:01, HLA-C*07:02, HLA-C*06:02`
   - Submit and record Job ID in tracking spreadsheet

### **Step 2: MHC-II Submissions**
1. Go to [http://tools.iedb.org/mhcii/](http://tools.iedb.org/mhcii/)
2. Select **NetMHCIIpan BA** method
3. For each length (12, 15, 18, 20):
   - Open corresponding batch file
   - Copy and paste sequences into IEDB
   - Select HLA-DR alleles: `DRB1*01:01, DRB1*15:01, DRB1*04:01, DRB1*07:01, DRB1*03:01, DRB1*11:01, DRB1*13:01, DRB1*09:01`
   - Submit and record Job ID

### **Step 3: Result Management**
1. Open `epitope_tracking_spreadsheet.xlsx`
2. Update submission status and Job IDs
3. Monitor jobs and download results when complete
4. Update spreadsheet with binding results

## ⏱️ **Estimated Timeline**

| Task | Time | Notes |
|------|------|-------|
| **File Review** | 15 min | Check generated files |
| **MHC-I Submissions** | 30 min | 5 batch submissions |
| **MHC-II Submissions** | 20 min | 4 batch submissions |
| **Processing Wait** | 2-4 hours | IEDB processing time |
| **Result Download** | 30 min | Download and organize |
| **Total** | **3-5 hours** | **1 hour active work** |

## 📊 **Quality Control**

### **Before Submission**
- [ ] All batch files contain sequences
- [ ] Tracking spreadsheet opens properly
- [ ] File counts match summary statistics
- [ ] Sample epitope files contain proper formatting

### **After Submission**
- [ ] All Job IDs recorded in tracking spreadsheet
- [ ] Job status pages bookmarked
- [ ] Submission confirmation emails saved

## 🎯 **Success Criteria**

By completion, you should have:
- [ ] 9 IEDB prediction jobs submitted (5 MHC-I + 4 MHC-II)
- [ ] All Job IDs tracked in spreadsheet
- [ ] Organized results ready for analysis
- [ ] Strong binding epitopes identified

## 📞 **Support**

If issues arise:
1. Check IEDB server status
2. Try smaller batch sizes (split large files)
3. Contact IEDB support: iedb-help@liai.org
4. Use individual epitope files as backup

---
**Generated**: 2026-05-25 17:54
**Ready for IEDB submission**
