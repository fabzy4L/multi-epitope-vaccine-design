#!/usr/bin/env python3
"""
Local NetMHC Epitope Prediction Runner
Processes SARS-CoV-2 S1 epitope candidates using local NetMHC installation
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path
import time
import tempfile
import shutil

class LocalNetMHCProcessor:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        self.tools_dir = self.project_dir / "tools" / "netmhc"
        self.epitope_dir = self.project_dir / "epitope_files_for_iedb"
        self.results_dir = self.project_dir / "results" / "netmhc_local"

        # Tool paths
        self.netmhcpan_path = self.tools_dir / "netmhcpan"
        self.netmhcIIpan_path = self.tools_dir / "netmhcIIpan"

    def check_installation(self):
        """Verify NetMHC tools are properly installed"""
        print("🔍 Checking NetMHC installation...")

        if not self.tools_dir.exists():
            print(f"❌ Tools directory not found: {self.tools_dir}")
            print("   Run: bash scripts/setup_local_netmhc.sh")
            return False

        if not self.netmhcpan_path.exists():
            print(f"❌ NetMHCpan not found: {self.netmhcpan_path}")
            print("   Run: bash scripts/setup_local_netmhc.sh")
            return False

        if not self.netmhcIIpan_path.exists():
            print(f"❌ NetMHCIIpan not found: {self.netmhcIIpan_path}")
            print("   Run: bash scripts/setup_local_netmhc.sh")
            return False

        # Test tools
        try:
            result = subprocess.run([str(self.netmhcpan_path), "-h"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ NetMHCpan test failed")
                return False
        except Exception as e:
            print(f"❌ NetMHCpan test error: {e}")
            return False

        try:
            result = subprocess.run([str(self.netmhcIIpan_path), "-h"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ NetMHCIIpan test failed")
                return False
        except Exception as e:
            print(f"❌ NetMHCIIpan test error: {e}")
            return False

        print("✅ NetMHC installation verified")
        return True

    def setup_results_directory(self):
        """Create results directory structure"""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        (self.results_dir / "mhc_i").mkdir(exist_ok=True)
        (self.results_dir / "mhc_ii").mkdir(exist_ok=True)
        print(f"📁 Results directory: {self.results_dir}")

    def get_batch_files(self):
        """Find all batch submission files"""
        batch_dir = self.epitope_dir / "batch_submission_files"

        if not batch_dir.exists():
            print(f"❌ Batch files directory not found: {batch_dir}")
            print("   Run epitope generation first!")
            return [], []

        mhc_i_files = sorted(batch_dir.glob("mhc-i_length_*.txt"))
        mhc_ii_files = sorted(batch_dir.glob("mhc-ii_length_*.txt"))

        print(f"📁 Found {len(mhc_i_files)} MHC-I batch files")
        print(f"📁 Found {len(mhc_ii_files)} MHC-II batch files")

        return mhc_i_files, mhc_ii_files

    def convert_iedb_to_fasta(self, iedb_file):
        """Convert IEDB batch file to proper FASTA format for NetMHC"""
        temp_fasta = tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False)

        with open(iedb_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                elif line.startswith('>'):
                    temp_fasta.write(line + '\n')
                else:
                    temp_fasta.write(line + '\n')

        temp_fasta.close()
        return temp_fasta.name

    def run_netmhcpan_i(self, epitope_file, length):
        """Run NetMHCpan-4.1 for MHC-I predictions"""
        print(f"🧬 Processing MHC-I length {length}...")

        # Convert IEDB format to FASTA
        fasta_file = self.convert_iedb_to_fasta(epitope_file)

        try:
            # HLA alleles for global population coverage
            hla_alleles = [
                "HLA-A02:01", "HLA-A01:01", "HLA-A03:01", "HLA-A24:02",
                "HLA-B07:02", "HLA-B08:01", "HLA-B35:01", "HLA-B40:01",
                "HLA-C07:01", "HLA-C07:02", "HLA-C06:02"
            ]

            output_file = self.results_dir / "mhc_i" / f"mhc_i_length_{length}_results.txt"

            # Build NetMHCpan command
            cmd = [
                str(self.netmhcpan_path),
                "-f", fasta_file,
                "-a", ",".join(hla_alleles),
                "-l", str(length),
                "-BA"  # Binding affinity prediction
            ]

            print(f"⚡ Running: {' '.join(cmd[:3])} ... (alleles={len(hla_alleles)})")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Save raw output
                with open(output_file, 'w') as f:
                    f.write(result.stdout)

                # Parse and save CSV
                csv_file = output_file.with_suffix('.csv')
                self.parse_netmhcpan_output(result.stdout, csv_file)
                print(f"✅ MHC-I length {length} complete → {csv_file.name}")
                return True
            else:
                print(f"❌ NetMHCpan error: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout for MHC-I length {length}")
            return False
        except Exception as e:
            print(f"❌ Error processing MHC-I length {length}: {e}")
            return False
        finally:
            # Clean up temp file
            try:
                os.unlink(fasta_file)
            except:
                pass

    def run_netmhcIIpan(self, epitope_file, length):
        """Run NetMHCIIpan-4.0 for MHC-II predictions"""
        print(f"🧬 Processing MHC-II length {length}...")

        fasta_file = self.convert_iedb_to_fasta(epitope_file)

        try:
            # HLA-DR alleles for global coverage
            hla_alleles = [
                "DRB1_0101", "DRB1_1501", "DRB1_0401", "DRB1_0701",
                "DRB1_0301", "DRB1_1101", "DRB1_1301", "DRB1_0901"
            ]

            output_file = self.results_dir / "mhc_ii" / f"mhc_ii_length_{length}_results.txt"

            cmd = [
                str(self.netmhcIIpan_path),
                "-f", fasta_file,
                "-a", ",".join(hla_alleles),
                "-length", str(length)
            ]

            print(f"⚡ Running: {' '.join(cmd[:3])} ... (alleles={len(hla_alleles)})")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Save raw output
                with open(output_file, 'w') as f:
                    f.write(result.stdout)

                # Parse and save CSV
                csv_file = output_file.with_suffix('.csv')
                self.parse_netmhcIIpan_output(result.stdout, csv_file)
                print(f"✅ MHC-II length {length} complete → {csv_file.name}")
                return True
            else:
                print(f"❌ NetMHCIIpan error: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout for MHC-II length {length}")
            return False
        except Exception as e:
            print(f"❌ Error processing MHC-II length {length}: {e}")
            return False
        finally:
            try:
                os.unlink(fasta_file)
            except:
                pass

    def parse_netmhcpan_output(self, output, save_file):
        """Parse NetMHCpan output and save as CSV"""
        lines = output.strip().split('\n')
        data = []

        in_data_section = False
        for line in lines:
            line = line.strip()

            # Skip header lines
            if line.startswith('#') or line.startswith('NetMHCpan'):
                continue

            # Look for data section
            if 'Peptide' in line and 'HLA' in line:
                in_data_section = True
                continue

            if not in_data_section or not line:
                continue

            # Parse data lines
            parts = line.split()
            if len(parts) >= 6:
                try:
                    epitope = parts[2] if len(parts) > 2 else ''
                    hla_allele = parts[1] if len(parts) > 1 else ''
                    ic50_str = parts[3] if len(parts) > 3 else 'NA'
                    rank_str = parts[4] if len(parts) > 4 else 'NA'

                    # Convert IC50 and rank to float
                    ic50_nm = float(ic50_str) if ic50_str not in ['NA', '-'] else None
                    rank_percent = float(rank_str) if rank_str not in ['NA', '-'] else None

                    data.append({
                        'epitope': epitope,
                        'hla_allele': hla_allele,
                        'ic50_nm': ic50_nm,
                        'rank_percent': rank_percent,
                        'binding_level': 'Strong' if ic50_nm and ic50_nm <= 500 else 'Weak' if ic50_nm else 'Unknown'
                    })
                except (ValueError, IndexError):
                    continue

        if data:
            df = pd.DataFrame(data)
            df.to_csv(save_file, index=False)
            print(f"📊 Saved {len(data)} predictions to {save_file.name}")
        else:
            print(f"⚠️ No data parsed from NetMHCpan output")

    def parse_netmhcIIpan_output(self, output, save_file):
        """Parse NetMHCIIpan output and save as CSV"""
        lines = output.strip().split('\n')
        data = []

        in_data_section = False
        for line in lines:
            line = line.strip()

            if line.startswith('#') or line.startswith('NetMHCIIpan'):
                continue

            if 'Peptide' in line and 'HLA' in line:
                in_data_section = True
                continue

            if not in_data_section or not line:
                continue

            parts = line.split()
            if len(parts) >= 5:
                try:
                    epitope = parts[2] if len(parts) > 2 else ''
                    hla_allele = parts[1] if len(parts) > 1 else ''
                    ic50_str = parts[3] if len(parts) > 3 else 'NA'
                    rank_str = parts[4] if len(parts) > 4 else 'NA'

                    ic50_nm = float(ic50_str) if ic50_str not in ['NA', '-'] else None
                    rank_percent = float(rank_str) if rank_str not in ['NA', '-'] else None

                    data.append({
                        'epitope': epitope,
                        'hla_allele': hla_allele,
                        'ic50_nm': ic50_nm,
                        'rank_percent': rank_percent,
                        'core': parts[5] if len(parts) > 5 else ''
                    })
                except (ValueError, IndexError):
                    continue

        if data:
            df = pd.DataFrame(data)
            df.to_csv(save_file, index=False)
            print(f"📊 Saved {len(data)} predictions to {save_file.name}")

    def process_all_epitopes(self):
        """Process all epitope batch files"""
        print("🚀 Starting Local NetMHC Processing")
        print("=" * 50)

        if not self.check_installation():
            return False

        self.setup_results_directory()
        mhc_i_files, mhc_ii_files = self.get_batch_files()

        if not mhc_i_files and not mhc_ii_files:
            print("❌ No batch files found!")
            return False

        start_time = time.time()
        success_count = 0
        total_count = len(mhc_i_files) + len(mhc_ii_files)

        # Process MHC-I files
        if mhc_i_files:
            print(f"\n🔬 Processing {len(mhc_i_files)} MHC-I batch files...")
            for file_path in mhc_i_files:
                # Extract length from filename: mhc-i_length_9_sequences.txt
                length = file_path.stem.split('_')[2]
                if self.run_netmhcpan_i(file_path, length):
                    success_count += 1

        # Process MHC-II files
        if mhc_ii_files:
            print(f"\n🔬 Processing {len(mhc_ii_files)} MHC-II batch files...")
            for file_path in mhc_ii_files:
                length = file_path.stem.split('_')[2]
                if self.run_netmhcIIpan(file_path, length):
                    success_count += 1

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n🎉 Local NetMHC Processing Complete!")
        print("=" * 50)
        print(f"⏱️  Processing time: {duration:.1f} seconds")
        print(f"✅ Successful: {success_count}/{total_count} batch files")
        print(f"📁 Results saved to: {self.results_dir}")

        if success_count == total_count:
            self.generate_summary_report()
            return True
        else:
            print(f"⚠️ {total_count - success_count} files failed to process")
            return False

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\n📈 Generating Summary Report...")

        # Collect all CSV files
        mhc_i_files = list((self.results_dir / "mhc_i").glob("*.csv"))
        mhc_ii_files = list((self.results_dir / "mhc_ii").glob("*.csv"))

        total_predictions = 0
        strong_binders_500 = 0  # IC50 <= 500nM
        strong_binders_50 = 0   # IC50 <= 50nM

        summary_data = []

        # Analyze MHC-I results
        for file_path in mhc_i_files:
            try:
                df = pd.read_csv(file_path)
                if not df.empty:
                    count = len(df)
                    strong_500 = len(df[df['ic50_nm'] <= 500])
                    strong_50 = len(df[df['ic50_nm'] <= 50])

                    total_predictions += count
                    strong_binders_500 += strong_500
                    strong_binders_50 += strong_50

                    summary_data.append({
                        'file': file_path.name,
                        'type': 'MHC-I',
                        'total': count,
                        'strong_500': strong_500,
                        'strong_50': strong_50
                    })
            except Exception as e:
                print(f"⚠️ Could not process {file_path}: {e}")

        # Analyze MHC-II results
        for file_path in mhc_ii_files:
            try:
                df = pd.read_csv(file_path)
                if not df.empty:
                    count = len(df)
                    strong_1000 = len(df[df['ic50_nm'] <= 1000])  # Different threshold for MHC-II
                    strong_100 = len(df[df['ic50_nm'] <= 100])

                    total_predictions += count
                    strong_binders_500 += strong_1000  # Using 1000nM threshold
                    strong_binders_50 += strong_100

                    summary_data.append({
                        'file': file_path.name,
                        'type': 'MHC-II',
                        'total': count,
                        'strong_500': strong_1000,
                        'strong_50': strong_100
                    })
            except Exception as e:
                print(f"⚠️ Could not process {file_path}: {e}")

        # Create summary report
        summary_df = pd.DataFrame(summary_data)
        summary_file = self.results_dir / "processing_summary.csv"
        summary_df.to_csv(summary_file, index=False)

        # Print summary
        print(f"\n📊 NETMHC PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"MHC-I result files: {len(mhc_i_files)}")
        print(f"MHC-II result files: {len(mhc_ii_files)}")
        print(f"Total predictions: {total_predictions:,}")
        print(f"Strong binders (≤500/1000nM): {strong_binders_500:,} ({strong_binders_500/total_predictions*100:.1f}%)")
        print(f"Very strong binders (≤50/100nM): {strong_binders_50:,} ({strong_binders_50/total_predictions*100:.1f}%)")
        print(f"Summary saved: {summary_file}")
        print(f"{'='*50}")

        print(f"\n🎯 Ready for Stage 03: VaxiJen/AllerTop/ProtParam analysis!")


def main():
    """Main execution function"""
    print("🧬 Local NetMHC Epitope Processor")
    print("Vaccinology Project - SARS-CoV-2 S1 Domain Analysis")
    print("=" * 60)

    processor = LocalNetMHCProcessor()
    success = processor.process_all_epitopes()

    if success:
        print("\n🎉 SUCCESS: All epitope predictions completed!")
        print("🚀 Next: Run VaxiJen/AllerTop analysis on results")
    else:
        print("\n❌ Some predictions failed. Check errors above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())