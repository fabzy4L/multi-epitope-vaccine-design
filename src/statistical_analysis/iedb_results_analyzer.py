#!/usr/bin/env python3
"""
IEDB Results Statistical Analysis
Processes 44,359 binding predictions to identify top epitope candidates

Input: 9 IEDB CSV files (MHC-I and MHC-II predictions)
Output: Top epitope candidates with comprehensive scoring

Author: Fabian Alvarez-Primo
Date: 2026-05-27
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class IEDBAnalyzer:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self.mhc_i_dir = self.results_dir / "mhc_i_results"
        self.mhc_ii_dir = self.results_dir / "mhc_ii_results"
        self.processed_dir = self.results_dir / "processed_results"

        # Create processed results directory
        self.processed_dir.mkdir(exist_ok=True)

        # Binding thresholds for strong binders
        self.mhc_i_thresholds = {"ic50": 50, "rank": 0.5}  # IC50 < 50nM, Rank < 0.5%
        self.mhc_ii_thresholds = {"ic50": 50, "rank": 1.0}  # IC50 < 50nM, Rank < 1.0%

    def load_mhc_results(self, mhc_type="mhc_i"):
        """Load and combine all MHC-I or MHC-II results"""
        if mhc_type == "mhc_i":
            pattern = str(self.mhc_i_dir / "MHC-I*.csv")
            expected_columns = ['allele', 'seq_num', 'start', 'end', 'length', 'peptide', 'ic50', 'rank']
        else:
            pattern = str(self.mhc_ii_dir / "MHC-II*.csv")
            expected_columns = ['allele', 'seq_num', 'start', 'end', 'length', 'core_peptide', 'peptide', 'ic50', 'rank']

        all_files = glob.glob(pattern)
        print(f"Loading {len(all_files)} {mhc_type.upper()} files...")

        combined_data = []
        for file_path in all_files:
            print(f"Processing: {os.path.basename(file_path)}")

            # Read CSV, skip header rows
            df = pd.read_csv(file_path, skiprows=3)
            df.columns = expected_columns

            # Add metadata
            length = int(file_path.split(" - ")[-1].split(".")[0])
            df['epitope_length'] = length
            df['mhc_type'] = mhc_type.upper()

            combined_data.append(df)

        combined_df = pd.concat(combined_data, ignore_index=True)
        print(f"Total {mhc_type.upper()} predictions: {len(combined_df):,}")
        return combined_df

    def identify_strong_binders(self, df, mhc_type):
        """Identify strong binders based on IC50 and rank thresholds"""
        if mhc_type == "mhc_i":
            thresholds = self.mhc_i_thresholds
        else:
            thresholds = self.mhc_ii_thresholds

        strong_binders = df[
            (df['ic50'] <= thresholds['ic50']) &
            (df['rank'] <= thresholds['rank'])
        ].copy()

        print(f"\n{mhc_type.upper()} Strong Binders:")
        print(f"Total predictions: {len(df):,}")
        print(f"Strong binders: {len(strong_binders):,}")
        print(f"Success rate: {len(strong_binders)/len(df)*100:.2f}%")

        return strong_binders

    def calculate_epitope_coverage(self, strong_binders):
        """Calculate HLA allele and population coverage"""
        coverage_stats = {}

        # Count unique epitopes per allele
        allele_coverage = strong_binders.groupby('allele').agg({
            'peptide': ['count', 'nunique'],
            'ic50': ['min', 'median'],
            'rank': ['min', 'median']
        }).round(3)

        # Flatten column names
        allele_coverage.columns = ['_'.join(col).strip() for col in allele_coverage.columns]

        # Count epitopes covered by multiple alleles
        epitope_allele_counts = strong_binders.groupby('peptide')['allele'].nunique()
        multi_allele_epitopes = epitope_allele_counts[epitope_allele_counts > 1]

        coverage_stats['allele_coverage'] = allele_coverage
        coverage_stats['multi_allele_epitopes'] = len(multi_allele_epitopes)
        coverage_stats['total_unique_epitopes'] = len(epitope_allele_counts)

        return coverage_stats

    def generate_summary_statistics(self, mhc_i_strong, mhc_ii_strong):
        """Generate comprehensive summary statistics"""
        summary = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'mhc_i_stats': {
                'total_predictions': len(mhc_i_strong) if len(mhc_i_strong) > 0 else 0,
                'unique_epitopes': mhc_i_strong['peptide'].nunique() if len(mhc_i_strong) > 0 else 0,
                'alleles_covered': mhc_i_strong['allele'].nunique() if len(mhc_i_strong) > 0 else 0,
                'best_ic50': mhc_i_strong['ic50'].min() if len(mhc_i_strong) > 0 else None,
                'best_rank': mhc_i_strong['rank'].min() if len(mhc_i_strong) > 0 else None,
            },
            'mhc_ii_stats': {
                'total_predictions': len(mhc_ii_strong) if len(mhc_ii_strong) > 0 else 0,
                'unique_epitopes': mhc_ii_strong['peptide'].nunique() if len(mhc_ii_strong) > 0 else 0,
                'alleles_covered': mhc_ii_strong['allele'].nunique() if len(mhc_ii_strong) > 0 else 0,
                'best_ic50': mhc_ii_strong['ic50'].min() if len(mhc_ii_strong) > 0 else None,
                'best_rank': mhc_ii_strong['rank'].min() if len(mhc_ii_strong) > 0 else None,
            }
        }

        return summary

    def export_top_candidates(self, strong_binders, mhc_type, top_n=20):
        """Export top epitope candidates"""
        # Rank by combined score (weighted IC50 and rank)
        strong_binders['combined_score'] = (
            (1 / strong_binders['ic50']) * 0.6 +  # IC50 weight
            (1 / (strong_binders['rank'] + 0.001)) * 0.4  # Rank weight (avoid div by 0)
        )

        # Get top candidates
        top_candidates = strong_binders.nlargest(top_n, 'combined_score')

        # Export
        output_file = self.processed_dir / f"top_{mhc_type}_candidates.csv"
        top_candidates.to_csv(output_file, index=False)
        print(f"\nTop {top_n} {mhc_type.upper()} candidates exported to: {output_file}")

        return top_candidates

    def create_visualizations(self, mhc_i_strong, mhc_ii_strong):
        """Create summary visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # MHC-I IC50 distribution
        if len(mhc_i_strong) > 0:
            axes[0,0].hist(mhc_i_strong['ic50'], bins=50, alpha=0.7, color='blue')
            axes[0,0].set_title('MHC-I IC50 Distribution (Strong Binders)')
            axes[0,0].set_xlabel('IC50 (nM)')
            axes[0,0].set_ylabel('Count')

        # MHC-II IC50 distribution
        if len(mhc_ii_strong) > 0:
            axes[0,1].hist(mhc_ii_strong['ic50'], bins=50, alpha=0.7, color='red')
            axes[0,1].set_title('MHC-II IC50 Distribution (Strong Binders)')
            axes[0,1].set_xlabel('IC50 (nM)')
            axes[0,1].set_ylabel('Count')

        # Epitope length distribution
        if len(mhc_i_strong) > 0:
            length_counts_i = mhc_i_strong['epitope_length'].value_counts().sort_index()
            axes[1,0].bar(length_counts_i.index, length_counts_i.values, alpha=0.7, color='blue')
            axes[1,0].set_title('MHC-I Strong Binders by Length')
            axes[1,0].set_xlabel('Epitope Length')
            axes[1,0].set_ylabel('Count')

        if len(mhc_ii_strong) > 0:
            length_counts_ii = mhc_ii_strong['epitope_length'].value_counts().sort_index()
            axes[1,1].bar(length_counts_ii.index, length_counts_ii.values, alpha=0.7, color='red')
            axes[1,1].set_title('MHC-II Strong Binders by Length')
            axes[1,1].set_xlabel('Epitope Length')
            axes[1,1].set_ylabel('Count')

        plt.tight_layout()

        # Save plot
        plot_file = self.processed_dir / "binding_analysis_summary.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to: {plot_file}")
        plt.show()

    def run_complete_analysis(self):
        """Run complete statistical analysis pipeline"""
        print("="*60)
        print("IEDB RESULTS STATISTICAL ANALYSIS")
        print("="*60)

        # Load data
        print("\n1. LOADING DATA...")
        mhc_i_data = self.load_mhc_results("mhc_i")
        mhc_ii_data = self.load_mhc_results("mhc_ii")

        # Identify strong binders
        print("\n2. IDENTIFYING STRONG BINDERS...")
        mhc_i_strong = self.identify_strong_binders(mhc_i_data, "mhc_i")
        mhc_ii_strong = self.identify_strong_binders(mhc_ii_data, "mhc_ii")

        # Export strong binders
        strong_binders_file_i = self.processed_dir / "mhc_i_strong_binders.csv"
        strong_binders_file_ii = self.processed_dir / "mhc_ii_strong_binders.csv"

        if len(mhc_i_strong) > 0:
            mhc_i_strong.to_csv(strong_binders_file_i, index=False)
            print(f"MHC-I strong binders saved: {strong_binders_file_i}")

        if len(mhc_ii_strong) > 0:
            mhc_ii_strong.to_csv(strong_binders_file_ii, index=False)
            print(f"MHC-II strong binders saved: {strong_binders_file_ii}")

        # Generate summary statistics
        print("\n3. CALCULATING SUMMARY STATISTICS...")
        summary = self.generate_summary_statistics(mhc_i_strong, mhc_ii_strong)

        # Export top candidates
        print("\n4. EXPORTING TOP CANDIDATES...")
        if len(mhc_i_strong) > 0:
            top_mhc_i = self.export_top_candidates(mhc_i_strong, "mhc_i", top_n=20)
        if len(mhc_ii_strong) > 0:
            top_mhc_ii = self.export_top_candidates(mhc_ii_strong, "mhc_ii", top_n=15)

        # Create visualizations
        print("\n5. CREATING VISUALIZATIONS...")
        self.create_visualizations(mhc_i_strong, mhc_ii_strong)

        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE - SUMMARY")
        print("="*60)
        print(f"Analysis Date: {summary['analysis_date']}")
        print(f"\nMHC-I Strong Binders:")
        print(f"  Total predictions: {summary['mhc_i_stats']['total_predictions']:,}")
        print(f"  Unique epitopes: {summary['mhc_i_stats']['unique_epitopes']:,}")
        print(f"  HLA alleles covered: {summary['mhc_i_stats']['alleles_covered']}")
        print(f"  Best IC50: {summary['mhc_i_stats']['best_ic50']:.2f} nM" if summary['mhc_i_stats']['best_ic50'] else "  No strong binders found")

        print(f"\nMHC-II Strong Binders:")
        print(f"  Total predictions: {summary['mhc_ii_stats']['total_predictions']:,}")
        print(f"  Unique epitopes: {summary['mhc_ii_stats']['unique_epitopes']:,}")
        print(f"  HLA alleles covered: {summary['mhc_ii_stats']['alleles_covered']}")
        print(f"  Best IC50: {summary['mhc_ii_stats']['best_ic50']:.2f} nM" if summary['mhc_ii_stats']['best_ic50'] else "  No strong binders found")

        return summary, mhc_i_strong, mhc_ii_strong

if __name__ == "__main__":
    # Initialize analyzer
    results_dir = r"C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology\results\sars_cov2\iedb_predictions"
    analyzer = IEDBAnalyzer(results_dir)

    # Run complete analysis
    summary, mhc_i_strong, mhc_ii_strong = analyzer.run_complete_analysis()

    print(f"\nResults saved in: {analyzer.processed_dir}")
    print("Ready for epitope selection and vaccine construct design!")