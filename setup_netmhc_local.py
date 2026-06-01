#!/usr/bin/env python3
"""
NetMHC Local Installation and Epitope Prediction Script
Processes all SARS-CoV-2 S1 epitope candidates locally in minutes
"""

import os
import subprocess
import pandas as pd
from pathlib import Path
import time

class NetMHCLocalProcessor:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.epitope_dir = self.base_dir / "epitope_files_for_iedb"
        self.results_dir = self.base_dir / "results" / "netmhc_local"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # NetMHC tool paths (update after installation)
        self.netmhcpan_path = "netmhcpan"  # Update with full path after install
        self.netmhcIIpan_path = "netmhcIIpan"  # Update with full path after install

    def setup_directories(self):
        """Create necessary directories"""
        print("🔧 Setting up directories...")
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.results_dir / "mhc_i", exist_ok=True)
        os.makedirs(self.results_dir / "mhc_ii", exist_ok=True)
        print(f"✅ Results will be saved to: {self.results_dir}")

    def get_batch_files(self):
        """Get all batch submission files"""
        batch_dir = self.epitope_dir / "batch_submission_files"

        mhc_i_files = list(batch_dir.glob("mhc-i_length_*.txt"))
        mhc_ii_files = list(batch_dir.glob("mhc-ii_length_*.txt"))

        print(f"📁 Found {len(mhc_i_files)} MHC-I batch files")
        print(f"📁 Found {len(mhc_ii_files)} MHC-II batch files")

        return mhc_i_files, mhc_ii_files

    def run_netmhcpan_i(self, epitope_file, length):
        """Run NetMHCpan-4.1 for MHC-I predictions"""
        print(f"🧬 Processing MHC-I length {length}...")

        # Common HLA alleles for broad population coverage
        hla_alleles = [
            "HLA-A02:01", "HLA-A01:01", "HLA-A03:01", "HLA-A24:02",
            "HLA-B07:02", "HLA-B08:01", "HLA-B35:01", "HLA-B40:01",
            "HLA-C07:01", "HLA-C07:02", "HLA-C06:02"
        ]

        output_file = self.results_dir / "mhc_i" / f"mhc_i_length_{length}_results.csv"

        # Build NetMHCpan command
        cmd = [
            self.netmhcpan_path,
            "-f", str(epitope_file),
            "-a", ",".join(hla_alleles),
            "-l", str(length),
            "-BA"  # Binding affinity prediction
        ]

        try:
            print(f"⚡ Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Parse and save results
                self.parse_netmhcpan_output(result.stdout, output_file)
                print(f"✅ MHC-I length {length} complete → {output_file}")
                return True
            else:
                print(f"❌ Error in MHC-I length {length}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout for MHC-I length {length}")
            return False
        except FileNotFoundError:
            print(f"❌ NetMHCpan not found. Please update netmhcpan_path in script.")
            return False

    def run_netmhcIIpan(self, epitope_file, length):
        """Run NetMHCIIpan-4.0 for MHC-II predictions"""
        print(f"🧬 Processing MHC-II length {length}...")

        # Common HLA-DR alleles
        hla_alleles = [
            "DRB1_0101", "DRB1_1501", "DRB1_0401", "DRB1_0701",
            "DRB1_0301", "DRB1_1101", "DRB1_1301", "DRB1_0901"
        ]

        output_file = self.results_dir / "mhc_ii" / f"mhc_ii_length_{length}_results.csv"

        cmd = [
            self.netmhcIIpan_path,
            "-f", str(epitope_file),
            "-a", ",".join(hla_alleles),
            "-length", str(length)
        ]

        try:
            print(f"⚡ Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self.parse_netmhcIIpan_output(result.stdout, output_file)
                print(f"✅ MHC-II length {length} complete → {output_file}")
                return True
            else:
                print(f"❌ Error in MHC-II length {length}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout for MHC-II length {length}")
            return False
        except FileNotFoundError:
            print(f"❌ NetMHCIIpan not found. Please update netmhcIIpan_path in script.")
            return False

    def parse_netmhcpan_output(self, output, save_file):
        """Parse NetMHCpan output and save as CSV"""
        lines = output.strip().split('\n')
        data = []

        for line in lines:
            if line.startswith('NetMHCpan') or line.startswith('#') or not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 6:
                data.append({
                    'epitope': parts[2],
                    'hla_allele': parts[1],
                    'ic50_nm': float(parts[3]) if parts[3] != 'NA' else None,
                    'rank_percent': float(parts[4]) if parts[4] != 'NA' else None,
                    'binding_level': parts[5] if len(parts) > 5 else 'Unknown'
                })

        if data:
            df = pd.DataFrame(data)
            df.to_csv(save_file, index=False)
            print(f"📊 Saved {len(data)} predictions to {save_file}")

    def parse_netmhcIIpan_output(self, output, save_file):
        """Parse NetMHCIIpan output and save as CSV"""
        lines = output.strip().split('\n')
        data = []

        for line in lines:
            if line.startswith('NetMHCIIpan') or line.startswith('#') or not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 5:
                data.append({
                    'epitope': parts[2],
                    'hla_allele': parts[1],
                    'ic50_nm': float(parts[3]) if parts[3] != 'NA' else None,
                    'rank_percent': float(parts[4]) if parts[4] != 'NA' else None,
                    'core': parts[5] if len(parts) > 5 else ''
                })

        if data:
            df = pd.DataFrame(data)
            df.to_csv(save_file, index=False)
            print(f"📊 Saved {len(data)} predictions to {save_file}")

    def process_all_epitopes(self):
        """Process all epitope batch files"""
        print("🚀 Starting local NetMHC processing...")
        start_time = time.time()

        self.setup_directories()
        mhc_i_files, mhc_ii_files = self.get_batch_files()

        # Process MHC-I files
        print("\n🔬 Processing MHC-I epitopes...")
        for file_path in mhc_i_files:
            length = file_path.stem.split('_')[-2]  # Extract length from filename
            self.run_netmhcpan_i(file_path, length)

        # Process MHC-II files
        print("\n🔬 Processing MHC-II epitopes...")
        for file_path in mhc_ii_files:
            length = file_path.stem.split('_')[-2]  # Extract length from filename
            self.run_netmhcIIpan(file_path, length)

        end_time = time.time()
        print(f"\n✅ Local processing complete in {end_time - start_time:.1f} seconds!")
        print(f"📁 Results saved to: {self.results_dir}")

    def generate_summary(self):
        """Generate processing summary"""
        print("\n📈 Generating summary report...")

        # Count results
        mhc_i_files = list((self.results_dir / "mhc_i").glob("*.csv"))
        mhc_ii_files = list((self.results_dir / "mhc_ii").glob("*.csv"))

        total_predictions = 0
        strong_binders = 0

        print(f"\n📊 SUMMARY REPORT")
        print(f"{'='*50}")
        print(f"MHC-I result files: {len(mhc_i_files)}")
        print(f"MHC-II result files: {len(mhc_ii_files)}")

        # Analyze strong binders
        for file_path in mhc_i_files + mhc_ii_files:
            try:
                df = pd.read_csv(file_path)
                total_predictions += len(df)
                strong_binders += len(df[df['ic50_nm'] <= 500])  # Strong binders
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")

        print(f"Total predictions: {total_predictions:,}")
        print(f"Strong binders (IC50 ≤ 500nM): {strong_binders:,}")
        print(f"Strong binder rate: {strong_binders/total_predictions*100:.1f}%")
        print(f"{'='*50}")


def main():
    """Main execution function"""
    print("🧬 NetMHC Local Epitope Processor")
    print("=" * 50)

    processor = NetMHCLocalProcessor()

    # Check if tools are available
    try:
        subprocess.run(["which", "netmhcpan"], check=True, capture_output=True)
        subprocess.run(["which", "netmhcIIpan"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ NetMHC tools not found in PATH")
        print("📝 Please:")
        print("   1. Download NetMHCpan-4.1 and NetMHCIIpan-4.0")
        print("   2. Add them to your PATH or update paths in this script")
        print("   3. Run this script again")
        return

    processor.process_all_epitopes()
    processor.generate_summary()

    print("\n🎉 Ready for Stage 03: VaxiJen/AllerTop/ProtParam analysis!")


if __name__ == "__main__":
    main()