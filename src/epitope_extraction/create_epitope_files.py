#!/usr/bin/env python3
"""
Epitope Extraction Script: Create Discrete Files for IEDB Submission
==================================================================

This script breaks down the SARS-CoV-2 S1 domain into individual epitope files
that can be easily submitted to IEDB manually in batches.

Output:
- Individual .txt files for each epitope candidate
- Batch submission files organized by length
- Summary files for tracking and organization

Author: Python automation for manual IEDB workflow
Version: 1.0
"""

import os
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import datetime

class EpitopeFileGenerator:
    """
    Generate discrete epitope files for systematic IEDB submission.

    Features:
    - Overlapping windows for comprehensive coverage
    - Organized output folders by epitope type and length
    - Batch submission files for copy-paste into IEDB
    - Tracking spreadsheets for result management
    """

    def __init__(self, output_base_dir: str = "epitope_files_for_iedb"):
        self.output_dir = Path(output_base_dir)
        self.setup_directories()

    def setup_directories(self):
        """Create organized directory structure for epitope files."""
        # Main directories
        self.mhc_i_dir = self.output_dir / "mhc_i_epitopes"
        self.mhc_ii_dir = self.output_dir / "mhc_ii_epitopes"
        self.batch_dir = self.output_dir / "batch_submission_files"

        # Create all directories
        for directory in [self.mhc_i_dir, self.mhc_ii_dir, self.batch_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Create subdirectories by length
        for length in range(8, 13):  # MHC-I: 8-12 amino acids
            (self.mhc_i_dir / f"length_{length}").mkdir(exist_ok=True)

        for length in [12, 15, 18, 20]:  # MHC-II: common lengths
            (self.mhc_ii_dir / f"length_{length}").mkdir(exist_ok=True)

    def load_s1_sequence(self, fasta_file: str = "analysis/sars_cov2/02_epitope_prediction/sars_cov2_s1_domain.fasta") -> str:
        """Load S1 domain sequence from FASTA file."""
        try:
            with open(fasta_file, 'r') as f:
                lines = f.readlines()

            # Find sequence data (skip header)
            sequence = ""
            for line in lines:
                if not line.startswith('>'):
                    sequence += line.strip()

            print(f"Loaded S1 sequence: {len(sequence)} amino acids")
            return sequence.upper()

        except FileNotFoundError:
            print(f"ERROR: File not found: {fasta_file}")
            print("Please ensure the S1 domain FASTA file exists.")
            return None

    def generate_mhc_i_epitopes(self, sequence: str, step_size: int = 1) -> List[Dict]:
        """
        Generate overlapping MHC-I epitope windows (8-12 amino acids).

        Args:
            sequence: S1 protein sequence
            step_size: Step size for overlapping windows (1 = maximum overlap)
        """
        epitopes = []
        epitope_counter = 1

        # Generate epitopes for each length
        for length in range(8, 13):  # 8, 9, 10, 11, 12 amino acids
            print(f"  Generating {length}-mer epitopes...")

            for start in range(0, len(sequence) - length + 1, step_size):
                epitope_seq = sequence[start:start + length]

                epitope_data = {
                    'epitope_id': f"S1_MHC1_{epitope_counter:04d}",
                    'sequence': epitope_seq,
                    'length': length,
                    'start_pos': start + 1,  # 1-based indexing
                    'end_pos': start + length,
                    'type': 'MHC-I'
                }

                epitopes.append(epitope_data)
                epitope_counter += 1

        print(f"Generated {len(epitopes)} MHC-I epitope candidates")
        return epitopes

    def generate_mhc_ii_epitopes(self, sequence: str, step_size: int = 3) -> List[Dict]:
        """
        Generate overlapping MHC-II epitope windows (12-20 amino acids).

        Args:
            sequence: S1 protein sequence
            step_size: Step size for overlapping windows (3 = moderate overlap)
        """
        epitopes = []
        epitope_counter = 1001  # Start at 1001 to distinguish from MHC-I

        # Generate epitopes for selected lengths
        for length in [12, 15, 18, 20]:
            print(f"  Generating {length}-mer epitopes...")

            for start in range(0, len(sequence) - length + 1, step_size):
                epitope_seq = sequence[start:start + length]

                epitope_data = {
                    'epitope_id': f"S1_MHC2_{epitope_counter:04d}",
                    'sequence': epitope_seq,
                    'length': length,
                    'start_pos': start + 1,
                    'end_pos': start + length,
                    'type': 'MHC-II'
                }

                epitopes.append(epitope_data)
                epitope_counter += 1

        print(f"Generated {len(epitopes)} MHC-II epitope candidates")
        return epitopes

    def create_individual_epitope_files(self, epitopes: List[Dict]) -> None:
        """Create individual text files for each epitope."""
        print("Creating individual epitope files...")

        for epitope in epitopes:
            # Determine output directory
            if epitope['type'] == 'MHC-I':
                file_dir = self.mhc_i_dir / f"length_{epitope['length']}"
            else:
                file_dir = self.mhc_ii_dir / f"length_{epitope['length']}"

            # Create filename
            filename = f"{epitope['epitope_id']}.txt"
            file_path = file_dir / filename

            # Write epitope file
            with open(file_path, 'w') as f:
                f.write(f">{epitope['epitope_id']}\n")
                f.write(f"{epitope['sequence']}\n")
                f.write(f"# Position: {epitope['start_pos']}-{epitope['end_pos']}\n")
                f.write(f"# Length: {epitope['length']} amino acids\n")
                f.write(f"# Type: {epitope['type']}\n")

    def create_batch_submission_files(self, epitopes: List[Dict]) -> None:
        """Create batch files for easy copy-paste into IEDB."""
        print("Creating batch submission files...")

        # Group by type and length
        epitope_groups = {}
        for epitope in epitopes:
            key = (epitope['type'], epitope['length'])
            if key not in epitope_groups:
                epitope_groups[key] = []
            epitope_groups[key].append(epitope)

        # Create batch files for each group
        for (epitope_type, length), group_epitopes in epitope_groups.items():

            # Batch sequences file (for IEDB sequence input)
            batch_filename = f"{epitope_type.lower()}_length_{length}_sequences.txt"
            batch_path = self.batch_dir / batch_filename

            with open(batch_path, 'w') as f:
                f.write(f"# IEDB Batch Submission File\n")
                f.write(f"# Type: {epitope_type}\n")
                f.write(f"# Length: {length} amino acids\n")
                f.write(f"# Total sequences: {len(group_epitopes)}\n")
                f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"#\n")
                f.write(f"# Instructions:\n")
                f.write(f"# 1. Copy all sequences below\n")
                f.write(f"# 2. Paste into IEDB sequence input box\n")
                f.write(f"# 3. Select appropriate HLA alleles\n")
                f.write(f"# 4. Submit prediction job\n")
                f.write(f"\n")

                # Write sequences in FASTA format
                for epitope in group_epitopes:
                    f.write(f">{epitope['epitope_id']}\n")
                    f.write(f"{epitope['sequence']}\n")

            print(f"   Created: {batch_filename} ({len(group_epitopes)} sequences)")

    def create_tracking_spreadsheet(self, mhc_i_epitopes: List[Dict], mhc_ii_epitopes: List[Dict]) -> None:
        """Create Excel tracking spreadsheet for IEDB submissions."""
        print("Creating tracking spreadsheet...")

        # Combine all epitopes
        all_epitopes = mhc_i_epitopes + mhc_ii_epitopes

        # Create DataFrame
        df = pd.DataFrame(all_epitopes)

        # Add tracking columns
        df['iedb_submitted'] = False
        df['iedb_job_id'] = ''
        df['iedb_status'] = 'pending'
        df['results_downloaded'] = False
        df['strong_binder'] = ''
        df['best_ic50'] = ''
        df['notes'] = ''

        # Save to Excel with multiple sheets
        excel_path = self.batch_dir / "epitope_tracking_spreadsheet.xlsx"

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # All epitopes sheet
            df.to_excel(writer, sheet_name='All_Epitopes', index=False)

            # MHC-I only sheet
            mhc_i_df = df[df['type'] == 'MHC-I'].copy()
            mhc_i_df.to_excel(writer, sheet_name='MHC-I_Epitopes', index=False)

            # MHC-II only sheet
            mhc_ii_df = df[df['type'] == 'MHC-II'].copy()
            mhc_ii_df.to_excel(writer, sheet_name='MHC-II_Epitopes', index=False)

            # Summary statistics sheet
            summary_data = {
                'Metric': [
                    'Total Epitopes',
                    'MHC-I Epitopes',
                    'MHC-II Epitopes',
                    '8-mers', '9-mers', '10-mers', '11-mers', '12-mers',
                    '15-mers', '18-mers', '20-mers',
                    'Files Created',
                    'Batch Files Created'
                ],
                'Count': [
                    len(all_epitopes),
                    len(mhc_i_epitopes),
                    len(mhc_ii_epitopes),
                    len(df[df['length'] == 8]),
                    len(df[df['length'] == 9]),
                    len(df[df['length'] == 10]),
                    len(df[df['length'] == 11]),
                    len(df[df['length'] == 12]),
                    len(df[df['length'] == 15]),
                    len(df[df['length'] == 18]),
                    len(df[df['length'] == 20]),
                    len(all_epitopes),  # One file per epitope
                    len(df.groupby(['type', 'length']))  # Batch files
                ]
            }

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        print(f"   Created: epitope_tracking_spreadsheet.xlsx")

    def create_iedb_submission_instructions(self) -> None:
        """Create detailed IEDB submission instructions."""
        instructions_file = self.batch_dir / "IEDB_SUBMISSION_INSTRUCTIONS.md"

        instructions = f"""# IEDB Submission Instructions for Generated Epitope Files

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
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Ready for IEDB submission**
"""

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        print(f"   Created: IEDB_SUBMISSION_INSTRUCTIONS.md")

def main():
    """Execute epitope file generation workflow."""
    print("="*70)
    print("EPITOPE FILE GENERATOR FOR IEDB SUBMISSION")
    print("="*70)

    # Initialize generator
    generator = EpitopeFileGenerator()

    # Load S1 sequence
    print("\nLoading SARS-CoV-2 S1 domain sequence...")
    sequence = generator.load_s1_sequence()

    if sequence is None:
        print("ERROR: Cannot proceed without S1 sequence. Please check file path.")
        return

    # Generate epitope candidates
    print("\nGenerating MHC-I epitope candidates...")
    mhc_i_epitopes = generator.generate_mhc_i_epitopes(sequence)

    print("\nGenerating MHC-II epitope candidates...")
    mhc_ii_epitopes = generator.generate_mhc_ii_epitopes(sequence)

    # Create individual files
    print(f"\nCreating individual epitope files...")
    all_epitopes = mhc_i_epitopes + mhc_ii_epitopes
    generator.create_individual_epitope_files(all_epitopes)

    # Create batch submission files
    print(f"\nCreating batch submission files...")
    generator.create_batch_submission_files(all_epitopes)

    # Create tracking spreadsheet
    print(f"\nCreating tracking spreadsheet...")
    generator.create_tracking_spreadsheet(mhc_i_epitopes, mhc_ii_epitopes)

    # Create instructions
    print(f"\nCreating submission instructions...")
    generator.create_iedb_submission_instructions()

    # Final summary
    print("\n" + "="*70)
    print("EPITOPE FILE GENERATION COMPLETE")
    print("="*70)
    print(f"Summary Statistics:")
    print(f"   - Total epitopes generated: {len(all_epitopes):,}")
    print(f"   - MHC-I epitopes: {len(mhc_i_epitopes):,}")
    print(f"   - MHC-II epitopes: {len(mhc_ii_epitopes):,}")
    print(f"   - Individual files created: {len(all_epitopes):,}")
    print(f"   - Batch submission files: {len(set((e['type'], e['length']) for e in all_epitopes))}")

    print(f"\nOutput Directory: epitope_files_for_iedb/")
    print(f"   |-- mhc_i_epitopes/ (organized by length)")
    print(f"   |-- mhc_ii_epitopes/ (organized by length)")
    print(f"   |-- batch_submission_files/")
    print(f"       |-- *_sequences.txt (ready for IEDB)")
    print(f"       |-- epitope_tracking_spreadsheet.xlsx")
    print(f"       |-- IEDB_SUBMISSION_INSTRUCTIONS.md")

    print(f"\nNext Steps:")
    print(f"   1. Review generated files in output directory")
    print(f"   2. Follow IEDB_SUBMISSION_INSTRUCTIONS.md")
    print(f"   3. Submit batch files to IEDB systematically")
    print(f"   4. Track progress in Excel spreadsheet")

    print(f"\nExpected IEDB Submission Time: 1 hour active work + 2-4 hours processing")

if __name__ == "__main__":
    main()