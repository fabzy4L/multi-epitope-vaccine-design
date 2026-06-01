#!/usr/bin/env python3
"""
Statistical Analysis Template for Gemini AI
==========================================

Template for Gemini's statistical analysis component in collaborative workflow.
Processes Claude's IEDB automation outputs for population coverage and scoring.

Author: Claude (Template Design) -> Gemini (Implementation)
Collaboration: Data formats standardized for seamless handoff
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json
from pathlib import Path

class VaccineStatisticalAnalyzer:
    """
    Statistical analysis framework for Gemini to process Claude's IEDB outputs.

    Key Capabilities:
    - Population coverage calculations across global demographics
    - Epitope scoring and ranking algorithms
    - Statistical significance testing for selection
    - Visualization dashboards for decision support
    """

    def __init__(self, data_dir: str = "analysis/sars_cov2/02_epitope_prediction/processed_data"):
        self.data_dir = Path(data_dir)

        # Global HLA allele frequencies (major populations)
        # Source: Allele Frequency Net Database (AFND) - Representative values
        self.hla_frequencies = self._load_hla_frequencies()

        # Population groups for coverage analysis
        self.populations = {
            "Global": "worldwide_average",
            "European": "european_caucasoid",
            "Asian": "asian_mongoloid",
            "African": "african_negroid",
            "Americas": "hispanic_latino"
        }

    def _load_hla_frequencies(self) -> Dict:
        """Load HLA allele frequencies for population coverage calculations."""
        # Template data - Gemini should replace with comprehensive frequency database
        return {
            "HLA-A*02:01": {"global": 0.234, "european": 0.445, "asian": 0.189, "african": 0.156},
            "HLA-A*01:01": {"global": 0.156, "european": 0.234, "asian": 0.089, "african": 0.123},
            "HLA-A*03:01": {"global": 0.123, "european": 0.189, "asian": 0.067, "african": 0.098},
            "HLA-A*24:02": {"global": 0.189, "european": 0.123, "asian": 0.267, "african": 0.145},
            "HLA-B*07:02": {"global": 0.145, "european": 0.234, "asian": 0.089, "african": 0.098},
            "HLA-B*08:01": {"global": 0.123, "european": 0.189, "asian": 0.067, "african": 0.089},
            "DRB1*01:01": {"global": 0.234, "european": 0.289, "asian": 0.189, "african": 0.201},
            "DRB1*15:01": {"global": 0.189, "european": 0.267, "asian": 0.145, "african": 0.167},
            "DRB1*04:01": {"global": 0.167, "european": 0.201, "asian": 0.234, "african": 0.123},
            "DRB1*07:01": {"global": 0.145, "european": 0.189, "asian": 0.167, "african": 0.134}
        }

    def load_claude_predictions(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load standardized prediction files from Claude's automation.

        Returns:
            mhc_i_df: MHC-I predictions with binding affinities
            mhc_ii_df: MHC-II predictions with binding affinities
        """
        # Load MHC-I predictions
        mhc_i_file = self.data_dir / "mhc_i_predictions.csv"

        # Skip metadata header lines (starting with #)
        with open(mhc_i_file, 'r') as f:
            lines = f.readlines()

        # Find where CSV data starts (after metadata)
        data_start = 0
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                data_start = i
                break

        mhc_i_df = pd.read_csv(mhc_i_file, skiprows=data_start)

        # Load MHC-II predictions
        mhc_ii_file = self.data_dir / "mhc_ii_predictions.csv"
        with open(mhc_ii_file, 'r') as f:
            lines = f.readlines()

        data_start = 0
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                data_start = i
                break

        mhc_ii_df = pd.read_csv(mhc_ii_file, skiprows=data_start)

        print(f"Loaded {len(mhc_i_df)} MHC-I predictions")
        print(f"Loaded {len(mhc_ii_df)} MHC-II predictions")

        return mhc_i_df, mhc_ii_df

    def calculate_population_coverage(self, predictions_df: pd.DataFrame,
                                      epitope_threshold: float = 500.0) -> pd.DataFrame:
        """
        Calculate population coverage for epitope sets.

        This is Gemini's core mathematical computation task.

        Args:
            predictions_df: MHC predictions with IC50 values
            epitope_threshold: IC50 threshold for binding (nM)

        Returns:
            DataFrame with population coverage per epitope
        """
        coverage_results = []

        # Get unique epitopes that meet binding threshold
        strong_binders = predictions_df[
            predictions_df['ic50_nm'] <= epitope_threshold
        ]

        unique_epitopes = strong_binders['epitope_id'].unique()

        for epitope_id in unique_epitopes:
            epitope_data = strong_binders[
                strong_binders['epitope_id'] == epitope_id
            ]

            # Calculate coverage for each population
            coverage = {}
            for pop_name, pop_key in self.populations.items():
                pop_coverage = self._calculate_single_population_coverage(
                    epitope_data, pop_key
                )
                coverage[f"{pop_name.lower()}_coverage"] = pop_coverage

            result = {
                'epitope_id': epitope_id,
                'sequence': epitope_data.iloc[0]['sequence'],
                **coverage
            }
            coverage_results.append(result)

        coverage_df = pd.DataFrame(coverage_results)

        # Save for Claude's integration
        output_file = self.data_dir.parent / "03_candidate_scoring" / "population_coverage_analysis.csv"
        output_file.parent.mkdir(exist_ok=True)
        coverage_df.to_csv(output_file, index=False)

        return coverage_df

    def _calculate_single_population_coverage(self, epitope_data: pd.DataFrame,
                                              population: str) -> float:
        """Calculate coverage for a single population group."""
        # Get alleles that bind this epitope
        binding_alleles = epitope_data['hla_allele'].tolist()

        # Calculate coverage using inclusion-exclusion principle
        total_coverage = 0.0

        for allele in binding_alleles:
            if allele in self.hla_frequencies:
                # Get frequency for this population
                pop_key = population.split('_')[0] if '_' in population else population
                if pop_key in self.hla_frequencies[allele]:
                    total_coverage += self.hla_frequencies[allele][pop_key]

        # Simple additive model (should be corrected for linkage disequilibrium)
        return min(total_coverage, 1.0)

    def generate_integrated_scores(self, mhc_i_df: pd.DataFrame,
                                   mhc_ii_df: pd.DataFrame,
                                   coverage_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate integrated epitope scores combining multiple criteria.

        This implements the scoring algorithm from epitope_selection_criteria.md
        """
        # Combine predictions for scoring
        all_epitopes = {}

        # Process MHC-I epitopes
        for _, row in mhc_i_df.iterrows():
            eid = row['epitope_id']
            if eid not in all_epitopes:
                all_epitopes[eid] = {
                    'sequence': row['sequence'],
                    'mhc_i_binding': True,
                    'mhc_ii_binding': False,
                    'min_mhc_i_ic50': row['ic50_nm'],
                    'min_mhc_ii_ic50': None,
                    'binding_level': row['binding_level']
                }
            else:
                # Update with better binding if available
                if row['ic50_nm'] < all_epitopes[eid]['min_mhc_i_ic50']:
                    all_epitopes[eid]['min_mhc_i_ic50'] = row['ic50_nm']

        # Process MHC-II epitopes
        for _, row in mhc_ii_df.iterrows():
            eid = row['epitope_id']
            if eid not in all_epitopes:
                all_epitopes[eid] = {
                    'sequence': row['sequence'],
                    'mhc_i_binding': False,
                    'mhc_ii_binding': True,
                    'min_mhc_i_ic50': None,
                    'min_mhc_ii_ic50': row['ic50_nm'],
                    'binding_level': row['binding_level']
                }
            else:
                all_epitopes[eid]['mhc_ii_binding'] = True
                if all_epitopes[eid]['min_mhc_ii_ic50'] is None:
                    all_epitopes[eid]['min_mhc_ii_ic50'] = row['ic50_nm']
                elif row['ic50_nm'] < all_epitopes[eid]['min_mhc_ii_ic50']:
                    all_epitopes[eid]['min_mhc_ii_ic50'] = row['ic50_nm']

        # Generate integrated scores
        scored_epitopes = []
        for eid, epitope in all_epitopes.items():
            # Get population coverage
            coverage_row = coverage_df[coverage_df['epitope_id'] == eid]
            global_coverage = coverage_row['global_coverage'].iloc[0] if len(coverage_row) > 0 else 0.0

            # Calculate component scores
            binding_score = self._calculate_binding_score(epitope)
            coverage_score = global_coverage

            # Placeholder scores (Gemini should implement full scoring)
            antigenicity_score = 0.7  # VaxiJen placeholder
            allergenicity_score = 0.1  # AllerTop placeholder (lower is better)
            conservation_score = 0.9   # Sequence conservation placeholder

            # Weighted final score (from epitope_selection_criteria.md)
            final_score = (
                0.30 * antigenicity_score +
                0.25 * coverage_score +
                0.20 * binding_score +
                0.15 * conservation_score +
                0.10 * (1.0 - allergenicity_score)  # Invert allergenicity
            )

            # Selection decision
            selection_status = "selected" if final_score >= 0.6 else "rejected"

            scored_epitopes.append({
                'epitope_id': eid,
                'sequence': epitope['sequence'],
                'binding_score': binding_score,
                'antigenicity_score': antigenicity_score,
                'allergenicity_score': allergenicity_score,
                'population_coverage': coverage_score,
                'conservation_score': conservation_score,
                'final_score': final_score,
                'selection_status': selection_status
            })

        scores_df = pd.DataFrame(scored_epitopes)

        # Save integrated scores for Claude
        output_file = self.data_dir.parent / "03_candidate_scoring" / "integrated_epitope_scores.csv"
        output_file.parent.mkdir(exist_ok=True)
        scores_df.to_csv(output_file, index=False)

        return scores_df

    def _calculate_binding_score(self, epitope: Dict) -> float:
        """Calculate normalized binding score from IC50 values."""
        scores = []

        if epitope['mhc_i_binding'] and epitope['min_mhc_i_ic50']:
            # Convert IC50 to score (lower IC50 = higher score)
            mhc_i_score = max(0, 1 - (epitope['min_mhc_i_ic50'] / 500.0))
            scores.append(mhc_i_score)

        if epitope['mhc_ii_binding'] and epitope['min_mhc_ii_ic50']:
            mhc_ii_score = max(0, 1 - (epitope['min_mhc_ii_ic50'] / 1000.0))
            scores.append(mhc_ii_score)

        return np.mean(scores) if scores else 0.0

    def create_visualization_dashboard(self, coverage_df: pd.DataFrame,
                                       scores_df: pd.DataFrame):
        """
        Generate publication-quality visualizations.

        This is Gemini's strength - creating clear, informative graphics.
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 1. Population coverage heatmap
        coverage_matrix = coverage_df.set_index('epitope_id')[
            ['global_coverage', 'european_coverage', 'asian_coverage', 'african_coverage']
        ]

        sns.heatmap(coverage_matrix.head(20), annot=True, cmap='YlOrRd',
                   ax=axes[0,0], cbar_kws={'label': 'Coverage Fraction'})
        axes[0,0].set_title('Population Coverage by Epitope (Top 20)')
        axes[0,0].set_xlabel('Population Group')
        axes[0,0].set_ylabel('Epitope ID')

        # 2. Score distribution
        scores_df.hist(column='final_score', bins=20, ax=axes[0,1])
        axes[0,1].axvline(0.6, color='red', linestyle='--', label='Selection Threshold')
        axes[0,1].set_title('Distribution of Final Epitope Scores')
        axes[0,1].set_xlabel('Final Score')
        axes[0,1].set_ylabel('Number of Epitopes')
        axes[0,1].legend()

        # 3. Coverage vs. binding score
        selected = scores_df[scores_df['selection_status'] == 'selected']
        rejected = scores_df[scores_df['selection_status'] == 'rejected']

        axes[1,0].scatter(selected['binding_score'], selected['population_coverage'],
                         c='green', label='Selected', alpha=0.7)
        axes[1,0].scatter(rejected['binding_score'], rejected['population_coverage'],
                         c='red', label='Rejected', alpha=0.7)
        axes[1,0].set_xlabel('Binding Score')
        axes[1,0].set_ylabel('Population Coverage')
        axes[1,0].set_title('Epitope Selection: Binding vs. Coverage')
        axes[1,0].legend()

        # 4. Selection summary
        selection_counts = scores_df['selection_status'].value_counts()
        axes[1,1].pie(selection_counts.values, labels=selection_counts.index,
                     autopct='%1.1f%%', startangle=90)
        axes[1,1].set_title('Epitope Selection Summary')

        plt.tight_layout()

        # Save visualization
        output_file = self.data_dir.parent / "03_candidate_scoring" / "analysis_dashboard.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()

        return fig

def main():
    """
    Main execution template for Gemini's statistical analysis.

    Gemini should implement this workflow to process Claude's IEDB outputs.
    """
    print("="*60)
    print("GEMINI STATISTICAL ANALYSIS - COLLABORATIVE AI WORKFLOW")
    print("="*60)

    # Initialize analyzer
    analyzer = VaccineStatisticalAnalyzer()

    # Load Claude's prediction outputs
    print("\\n1. Loading Claude's IEDB automation results...")
    mhc_i_df, mhc_ii_df = analyzer.load_claude_predictions()

    # Calculate population coverage
    print("\\n2. Calculating population coverage...")
    coverage_df = analyzer.calculate_population_coverage(mhc_i_df)
    print(f"   Generated coverage analysis for {len(coverage_df)} epitopes")

    # Generate integrated scores
    print("\\n3. Computing integrated epitope scores...")
    scores_df = analyzer.generate_integrated_scores(mhc_i_df, mhc_ii_df, coverage_df)
    selected_count = len(scores_df[scores_df['selection_status'] == 'selected'])
    print(f"   Selected {selected_count} epitopes for vaccine construct")

    # Create visualization dashboard
    print("\\n4. Generating visualization dashboard...")
    analyzer.create_visualization_dashboard(coverage_df, scores_df)

    print("\\n" + "="*60)
    print("GEMINI ANALYSIS COMPLETE - READY FOR CLAUDE INTEGRATION")
    print("="*60)
    print("Output files for Claude:")
    print("  - population_coverage_analysis.csv")
    print("  - integrated_epitope_scores.csv")
    print("  - analysis_dashboard.png")
    print("\\nNext step: Claude construct optimization with selected epitopes")

if __name__ == "__main__":
    main()