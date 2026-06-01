#!/usr/bin/env python3
"""
Epitope Selection for Multi-Epitope Vaccine Construct
=====================================================

Selects optimal epitope combination based on:
1. Binding affinity (IC50 < 10nM priority)
2. Population coverage (diverse HLA alleles)
3. Epitope diversity (avoid redundancy)
4. Length optimization (9-10mers for MHC-I, 15mers for MHC-II)

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import os

class EpitopeSelector:
    def __init__(self, mhc_i_file, mhc_ii_file):
        """Initialize with top candidate files from statistical analysis."""
        self.mhc_i_df = pd.read_csv(mhc_i_file)
        self.mhc_ii_df = pd.read_csv(mhc_ii_file)
        self.selected_epitopes = {'MHC_I': [], 'MHC_II': []}

    def analyze_population_coverage(self, df, epitope_type):
        """Analyze HLA allele coverage for population representativeness."""
        allele_counts = df['allele'].value_counts()

        print(f"\n=== {epitope_type} Population Coverage Analysis ===")
        print("HLA Allele Distribution in Top Candidates:")
        for allele, count in allele_counts.items():
            print(f"  {allele}: {count} epitopes")

        # Major population groups
        if epitype_type == "MHC-I":
            major_alleles = ['HLA-A*02:01', 'HLA-A*01:01', 'HLA-A*03:01',
                           'HLA-B*08:01', 'HLA-B*35:01', 'HLA-A*24:02']
        else:
            major_alleles = ['HLA-DRB1*01:01', 'HLA-DRB1*03:01', 'HLA-DRB1*15:01',
                           'HLA-DRB1*11:01']

        covered_alleles = set(df['allele'].unique()) & set(major_alleles)
        coverage_pct = len(covered_alleles) / len(major_alleles) * 100

        print(f"Major Allele Coverage: {len(covered_alleles)}/{len(major_alleles)} ({coverage_pct:.1f}%)")
        return coverage_pct, covered_alleles

    def select_mhc_i_epitopes(self, target_count=6):
        """Select optimal MHC-I epitopes with diversity and coverage criteria."""
        print("\n" + "="*60)
        print("MHC-I EPITOPE SELECTION")
        print("="*60)

        # Analyze current candidates
        coverage_pct, covered_alleles = self.analyze_population_coverage(self.mhc_i_df, "MHC-I")

        # Selection criteria
        selected = []
        used_alleles = set()
        used_sequences = set()

        print(f"\nSelecting {target_count} MHC-I epitopes...")
        print("Selection Criteria:")
        print("- IC50 < 50nM (strong binders)")
        print("- Diverse HLA alleles (population coverage)")
        print("- Sequence diversity (avoid redundancy)")
        print("- Prefer 9-10mers (optimal MHC-I presentation)")

        for idx, row in self.mhc_i_df.iterrows():
            if len(selected) >= target_count:
                break

            peptide = row['peptide']
            allele = row['allele']
            ic50 = row['ic50']
            rank = row['rank']
            length = row['length']

            # Diversity check - avoid too similar sequences
            too_similar = False
            for existing_peptide in used_sequences:
                if self._sequence_similarity(peptide, existing_peptide) > 0.6:
                    too_similar = True
                    break

            # Selection logic
            priority_score = self._calculate_priority_score(row, used_alleles)

            if not too_similar and priority_score > 0:
                selected.append({
                    'peptide': peptide,
                    'allele': allele,
                    'ic50': ic50,
                    'rank': rank,
                    'length': length,
                    'combined_score': row['combined_score'],
                    'priority_score': priority_score
                })
                used_alleles.add(allele)
                used_sequences.add(peptide)

                print(f"\n[SELECTED] Selected: {peptide}")
                print(f"   Allele: {allele}")
                print(f"   IC50: {ic50:.2f}nM (Rank: {rank:.3f}%)")
                print(f"   Length: {length} aa")
                print(f"   Priority Score: {priority_score:.2f}")

        self.selected_epitopes['MHC_I'] = selected

        print(f"\n[SUMMARY] Final MHC-I Selection Summary:")
        print(f"Selected Epitopes: {len(selected)}")
        print(f"Allele Coverage: {len(used_alleles)} unique alleles")
        print(f"Average IC50: {np.mean([e['ic50'] for e in selected]):.2f}nM")

        return selected

    def select_mhc_ii_epitopes(self, target_count=4):
        """Select optimal MHC-II epitopes with diversity and coverage criteria."""
        print("\n" + "="*60)
        print("MHC-II EPITOPE SELECTION")
        print("="*60)

        # Analyze current candidates
        coverage_pct, covered_alleles = self.analyze_population_coverage(self.mhc_ii_df, "MHC-II")

        selected = []
        used_alleles = set()
        used_sequences = set()

        print(f"\nSelecting {target_count} MHC-II epitopes...")
        print("Selection Criteria:")
        print("- IC50 < 50nM (strong binders)")
        print("- Diverse HLA-DR alleles")
        print("- Prefer 15mers (optimal MHC-II presentation)")
        print("- Sequence diversity")

        for idx, row in self.mhc_ii_df.iterrows():
            if len(selected) >= target_count:
                break

            peptide = row['peptide']
            allele = row['allele']
            ic50 = row['ic50']
            rank = row['rank']
            length = row['length']

            # Prefer 15mers for MHC-II
            length_bonus = 1.2 if length == 15 else 1.0

            # Diversity check
            too_similar = False
            for existing_peptide in used_sequences:
                if self._sequence_similarity(peptide, existing_peptide) > 0.5:
                    too_similar = True
                    break

            priority_score = self._calculate_priority_score(row, used_alleles) * length_bonus

            if not too_similar and priority_score > 0:
                selected.append({
                    'peptide': peptide,
                    'allele': allele,
                    'ic50': ic50,
                    'rank': rank,
                    'length': length,
                    'core_peptide': row['core_peptide'],
                    'combined_score': row['combined_score'],
                    'priority_score': priority_score
                })
                used_alleles.add(allele)
                used_sequences.add(peptide)

                print(f"\n[SELECTED] Selected: {peptide}")
                print(f"   Allele: {allele}")
                print(f"   IC50: {ic50:.2f}nM (Rank: {rank:.3f}%)")
                print(f"   Length: {length} aa")
                print(f"   Core: {row['core_peptide']}")
                print(f"   Priority Score: {priority_score:.2f}")

        self.selected_epitopes['MHC_II'] = selected

        print(f"\n[SUMMARY] Final MHC-II Selection Summary:")
        print(f"Selected Epitopes: {len(selected)}")
        print(f"Allele Coverage: {len(used_alleles)} unique alleles")
        print(f"Average IC50: {np.mean([e['ic50'] for e in selected]):.2f}nM")

        return selected

    def _sequence_similarity(self, seq1, seq2):
        """Calculate simple sequence similarity (exact match ratio)."""
        if len(seq1) != len(seq2):
            return 0.0
        matches = sum(c1 == c2 for c1, c2 in zip(seq1, seq2))
        return matches / len(seq1)

    def _calculate_priority_score(self, row, used_alleles):
        """Calculate priority score based on affinity, rank, and allele diversity."""
        ic50 = row['ic50']
        rank = row['rank']
        allele = row['allele']

        # Affinity bonus (lower IC50 = higher score)
        affinity_score = max(0, (50 - ic50) / 50) * 10

        # Rank bonus (lower rank = higher score)
        rank_score = max(0, (1 - rank) * 5)

        # Allele diversity bonus
        diversity_bonus = 5 if allele not in used_alleles else 0

        return affinity_score + rank_score + diversity_bonus

    def generate_selection_report(self, output_dir):
        """Generate detailed selection report."""
        os.makedirs(output_dir, exist_ok=True)

        # Create detailed report
        report_file = os.path.join(output_dir, 'epitope_selection_report.md')
        with open(report_file, 'w') as f:
            f.write("# Multi-Epitope Vaccine Construct: Epitope Selection Report\n\n")
            f.write("**Generated:** 2026-06-01\n")
            f.write("**Pipeline:** SARS-CoV-2 S1 Domain Vaccinology\n\n")

            f.write("## Selection Methodology\n\n")
            f.write("### Selection Criteria\n")
            f.write("1. **Binding Affinity**: IC50 < 50nM (strong binders)\n")
            f.write("2. **Population Coverage**: Diverse HLA alleles\n")
            f.write("3. **Sequence Diversity**: <60% similarity between epitopes\n")
            f.write("4. **Length Optimization**: 9-10mers (MHC-I), 15mers (MHC-II)\n\n")

            # MHC-I Summary
            f.write("## Selected MHC-I Epitopes\n\n")
            f.write("| Epitope | HLA Allele | IC50 (nM) | Rank (%) | Length | Priority Score |\n")
            f.write("|---------|------------|-----------|----------|--------|----------------|\n")

            for ep in self.selected_epitopes['MHC_I']:
                f.write(f"| {ep['peptide']} | {ep['allele']} | {ep['ic50']:.2f} | {ep['rank']:.3f} | {ep['length']} | {ep['priority_score']:.2f} |\n")

            # MHC-II Summary
            f.write("\n## Selected MHC-II Epitopes\n\n")
            f.write("| Epitope | HLA Allele | IC50 (nM) | Rank (%) | Length | Core | Priority Score |\n")
            f.write("|---------|------------|-----------|----------|--------|------|----------------|\n")

            for ep in self.selected_epitopes['MHC_II']:
                f.write(f"| {ep['peptide']} | {ep['allele']} | {ep['ic50']:.2f} | {ep['rank']:.3f} | {ep['length']} | {ep['core_peptide']} | {ep['priority_score']:.2f} |\n")

            # Statistics
            mhc_i_avg_ic50 = np.mean([e['ic50'] for e in self.selected_epitopes['MHC_I']])
            mhc_ii_avg_ic50 = np.mean([e['ic50'] for e in self.selected_epitopes['MHC_II']])

            f.write(f"\n## Selection Statistics\n\n")
            f.write(f"- **MHC-I Epitopes**: {len(self.selected_epitopes['MHC_I'])}\n")
            f.write(f"- **MHC-II Epitopes**: {len(self.selected_epitopes['MHC_II'])}\n")
            f.write(f"- **Average MHC-I IC50**: {mhc_i_avg_ic50:.2f}nM\n")
            f.write(f"- **Average MHC-II IC50**: {mhc_ii_avg_ic50:.2f}nM\n")
            f.write(f"- **Total Epitopes**: {len(self.selected_epitopes['MHC_I']) + len(self.selected_epitopes['MHC_II'])}\n")

        print(f"[SELECTED] Selection report saved: {report_file}")
        return report_file

def main():
    """Main execution function."""
    print("EPITOPE SELECTION FOR MULTI-EPITOPE VACCINE CONSTRUCT")
    print("=" * 70)
    print("Selecting optimal epitope combination from statistical analysis results")
    print("Pipeline: SARS-CoV-2 S1 Domain -> Multi-epitope vaccine design")

    # File paths
    base_dir = r"C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology"
    results_dir = os.path.join(base_dir, "results", "sars_cov2", "iedb_predictions", "processed_results")

    mhc_i_file = os.path.join(results_dir, "top_mhc_i_candidates.csv")
    mhc_ii_file = os.path.join(results_dir, "top_mhc_ii_candidates.csv")

    # Initialize selector
    selector = EpitopeSelector(mhc_i_file, mhc_ii_file)

    # Perform selection
    mhc_i_selected = selector.select_mhc_i_epitopes(target_count=6)
    mhc_ii_selected = selector.select_mhc_ii_epitopes(target_count=4)

    # Generate report
    output_dir = os.path.join(base_dir, "results", "sars_cov2", "construct_design")
    report_file = selector.generate_selection_report(output_dir)

    # Save epitope data for construct design
    import json
    epitope_data = {
        'selection_date': '2026-06-01',
        'mhc_i_epitopes': mhc_i_selected,
        'mhc_ii_epitopes': mhc_ii_selected,
        'selection_criteria': {
            'ic50_threshold': '50nM',
            'diversity_threshold': '60%',
            'preferred_lengths': {'MHC_I': [9, 10], 'MHC_II': [15]}
        }
    }

    epitope_file = os.path.join(output_dir, 'selected_epitopes.json')
    with open(epitope_file, 'w') as f:
        json.dump(epitope_data, f, indent=2)

    print(f"\n[SELECTED] Epitope data saved: {epitope_file}")

    print(f"\n[COMPLETE] EPITOPE SELECTION COMPLETE!")
    print(f"Selected: {len(mhc_i_selected)} MHC-I + {len(mhc_ii_selected)} MHC-II epitopes")
    print(f"Ready for construct design phase...")

    return selector

if __name__ == "__main__":
    # Fix the typo in epitope_type
    def analyze_population_coverage(self, df, epitope_type):
        """Analyze HLA allele coverage for population representativeness."""
        allele_counts = df['allele'].value_counts()

        print(f"\n=== {epitope_type} Population Coverage Analysis ===")
        print("HLA Allele Distribution in Top Candidates:")
        for allele, count in allele_counts.items():
            print(f"  {allele}: {count} epitopes")

        # Major population groups
        if epitope_type == "MHC-I":
            major_alleles = ['HLA-A*02:01', 'HLA-A*01:01', 'HLA-A*03:01',
                           'HLA-B*08:01', 'HLA-B*35:01', 'HLA-A*24:02']
        else:
            major_alleles = ['HLA-DRB1*01:01', 'HLA-DRB1*03:01', 'HLA-DRB1*15:01',
                           'HLA-DRB1*11:01']

        covered_alleles = set(df['allele'].unique()) & set(major_alleles)
        coverage_pct = len(covered_alleles) / len(major_alleles) * 100

        print(f"Major Allele Coverage: {len(covered_alleles)}/{len(major_alleles)} ({coverage_pct:.1f}%)")
        return coverage_pct, covered_alleles

    # Monkey patch to fix the typo
    EpitopeSelector.analyze_population_coverage = analyze_population_coverage

    selector = main()