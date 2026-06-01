#!/usr/bin/env python3
"""
Multi-Epitope Vaccine Construct Designer
=======================================

Assembles selected epitopes into optimized vaccine construct with:
1. N-terminal adjuvant peptide
2. MHC-II epitopes with GPGPG linkers
3. Domain separator (KK)
4. MHC-I epitopes with AAY linkers
5. C-terminal stability tags

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class EpitopeInfo:
    """Container for epitope information."""
    peptide: str
    allele: str
    ic50: float
    rank: float
    length: int
    epitope_type: str
    priority_score: float

class VaccineConstructor:
    """Design multi-epitope vaccine constructs with optimized linkers and adjuvants."""

    def __init__(self):
        """Initialize with standard linker and adjuvant sequences."""

        # Linker sequences (validated in literature)
        self.linkers = {
            'MHC_I': 'AAY',           # Optimal for MHC-I presentation
            'MHC_II': 'GPGPG',        # Flexible linker for MHC-II
            'DOMAIN': 'KK',           # Domain separator
            'FLEXIBLE': 'GGGS'        # General flexible linker
        }

        # Adjuvant peptides (immune stimulatory)
        self.adjuvants = {
            'BETA_DEFENSIN_3': 'GIINTLQKYYCRVRGGRCAVLSCLPKEEQIGKCSTRGRKCCRRKK',
            'RS09_TLR4': 'APPHALS',
            'MPLA_MIMIC': 'DPKDKKKKDP',
            'TLR2_AGONIST': 'KKLKKLLKLLKKLL'
        }

        # Stability/purification tags
        self.c_terminal_tags = {
            'HIS6': 'HHHHHH',
            'STABILITY': 'PAPAP',
            'SOLUBILITY': 'GSGSGS'
        }

    def load_selected_epitopes(self, epitope_file: str) -> Dict[str, List[EpitopeInfo]]:
        """Load selected epitopes from JSON file."""
        with open(epitope_file, 'r') as f:
            data = json.load(f)

        epitopes = {'MHC_I': [], 'MHC_II': []}

        # Process MHC-I epitopes
        for ep_data in data['mhc_i_epitopes']:
            epitope = EpitopeInfo(
                peptide=ep_data['peptide'],
                allele=ep_data['allele'],
                ic50=ep_data['ic50'],
                rank=ep_data['rank'],
                length=ep_data['length'],
                epitope_type='MHC_I',
                priority_score=ep_data['priority_score']
            )
            epitopes['MHC_I'].append(epitope)

        # Process MHC-II epitopes
        for ep_data in data['mhc_ii_epitopes']:
            epitope = EpitopeInfo(
                peptide=ep_data['peptide'],
                allele=ep_data['allele'],
                ic50=ep_data['ic50'],
                rank=ep_data['rank'],
                length=ep_data['length'],
                epitope_type='MHC_II',
                priority_score=ep_data['priority_score']
            )
            epitopes['MHC_II'].append(epitope)

        return epitopes

    def design_construct_v1(self, epitopes: Dict[str, List[EpitopeInfo]]) -> str:
        """
        Design Version 1: Standard multi-epitope arrangement
        Structure: [Adjuvant]-[MHC-II epitopes]-[KK]-[MHC-I epitopes]-[Tag]
        """
        construct_parts = []

        # 1. N-terminal adjuvant (β-defensin-3 derivative - shorter version)
        adjuvant = 'APPHALS'  # RS09 TLR4 agonist peptide
        construct_parts.append(adjuvant)

        # 2. Flexible linker after adjuvant
        construct_parts.append(self.linkers['FLEXIBLE'])

        # 3. MHC-II epitopes (sorted by binding affinity)
        mhc_ii_sorted = sorted(epitopes['MHC_II'], key=lambda x: x.ic50)
        for i, epitope in enumerate(mhc_ii_sorted):
            if i > 0:  # Add linker before each epitope (except first)
                construct_parts.append(self.linkers['MHC_II'])
            construct_parts.append(epitope.peptide)

        # 4. Domain separator
        construct_parts.append(self.linkers['DOMAIN'])

        # 5. MHC-I epitopes (sorted by binding affinity)
        mhc_i_sorted = sorted(epitopes['MHC_I'], key=lambda x: x.ic50)
        for i, epitope in enumerate(mhc_i_sorted):
            if i > 0:  # Add linker before each epitope (except first)
                construct_parts.append(self.linkers['MHC_I'])
            construct_parts.append(epitope.peptide)

        # 6. C-terminal stability tag
        construct_parts.append(self.linkers['FLEXIBLE'])
        construct_parts.append(self.c_terminal_tags['STABILITY'])

        return ''.join(construct_parts)

    def design_construct_v2(self, epitopes: Dict[str, List[EpitopeInfo]]) -> str:
        """
        Design Version 2: Alternating arrangement for enhanced processing
        Structure: [Adj]-[MHC-II]-[MHC-I]-[MHC-II]-[MHC-I]-...-[Tag]
        """
        construct_parts = []

        # N-terminal adjuvant
        construct_parts.append('APPHALS')  # RS09
        construct_parts.append('GGGS')

        # Sort epitopes by binding affinity
        mhc_ii_sorted = sorted(epitopes['MHC_II'], key=lambda x: x.ic50)
        mhc_i_sorted = sorted(epitopes['MHC_I'], key=lambda x: x.ic50)

        # Alternate between MHC-II and MHC-I
        max_epitopes = max(len(mhc_ii_sorted), len(mhc_i_sorted))

        for i in range(max_epitopes):
            # Add MHC-II epitope if available
            if i < len(mhc_ii_sorted):
                if len(construct_parts) > 2:  # Not the first epitope
                    construct_parts.append(self.linkers['MHC_II'])
                construct_parts.append(mhc_ii_sorted[i].peptide)

            # Add MHC-I epitope if available
            if i < len(mhc_i_sorted):
                if len(construct_parts) > 2:  # Add linker
                    construct_parts.append(self.linkers['MHC_I'])
                construct_parts.append(mhc_i_sorted[i].peptide)

        # C-terminal tag
        construct_parts.append('GGGS')
        construct_parts.append('PAPAP')

        return ''.join(construct_parts)

    def design_construct_v3_optimized(self, epitopes: Dict[str, List[EpitopeInfo]]) -> str:
        """
        Design Version 3: Optimized for immunogenicity and stability
        Features: Enhanced adjuvant, optimized spacing, immunogenicity-ranked order
        """
        construct_parts = []

        # 1. Enhanced N-terminal immune stimulation
        # Combine TLR agonist with signal peptide mimic
        construct_parts.append('MKKLLFAIPLVVPFYSHS')  # Signal peptide for enhanced processing
        construct_parts.append('GGGS')
        construct_parts.append('APPHALS')  # TLR4 agonist
        construct_parts.append('GPGPG')

        # 2. Best MHC-II epitopes first (immunodominant positioning)
        mhc_ii_best = sorted(epitopes['MHC_II'], key=lambda x: x.ic50)[:2]  # Top 2 only
        for i, epitope in enumerate(mhc_ii_best):
            if i > 0:
                construct_parts.append('GPGPG')
            construct_parts.append(epitope.peptide)

        # 3. Strategic domain break
        construct_parts.append('KKGPGPGKK')

        # 4. Best MHC-I epitopes (top 4 only for optimal size)
        mhc_i_best = sorted(epitopes['MHC_I'], key=lambda x: x.ic50)[:4]
        for i, epitope in enumerate(mhc_i_best):
            if i > 0:
                construct_parts.append('AAY')
            construct_parts.append(epitope.peptide)

        # 5. C-terminal enhancement for stability and detection
        construct_parts.append('GGGS')
        construct_parts.append('PAPAP')    # Stability
        construct_parts.append('GS')
        construct_parts.append('HHHHHH')   # His tag for purification

        return ''.join(construct_parts)

    def analyze_construct_properties(self, sequence: str) -> Dict[str, Any]:
        """Analyze basic properties of the vaccine construct."""

        # Basic properties
        length = len(sequence)
        mw_estimate = length * 110  # Rough MW estimate (110 Da/residue)

        # Amino acid composition
        aa_counts = {}
        for aa in sequence:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1

        # Hydrophobicity (rough estimate using Kyte-Doolittle scale)
        hydrophobic = 'AILMFPWV'
        hydrophilic = 'RKDENQH'

        hydrophobic_count = sum(sequence.count(aa) for aa in hydrophobic)
        hydrophilic_count = sum(sequence.count(aa) for aa in hydrophilic)

        properties = {
            'length': length,
            'molecular_weight_estimate_da': mw_estimate,
            'hydrophobic_residues': hydrophobic_count,
            'hydrophilic_residues': hydrophilic_count,
            'hydrophobic_ratio': hydrophobic_count / length,
            'amino_acid_composition': aa_counts,
            'theoretical_pi_estimate': 'requires_detailed_calculation',
            'solubility_prediction': 'good' if hydrophilic_count > hydrophobic_count else 'moderate'
        }

        return properties

    def generate_construct_report(self, designs: Dict[str, str], epitopes: Dict[str, List[EpitopeInfo]],
                                output_dir: str) -> str:
        """Generate comprehensive construct design report."""

        os.makedirs(output_dir, exist_ok=True)

        report_file = os.path.join(output_dir, 'vaccine_construct_design_report.md')

        with open(report_file, 'w') as f:
            f.write("# Multi-Epitope Vaccine Construct Design Report\n\n")
            f.write("**Generated:** 2026-06-01\n")
            f.write("**Pipeline:** SARS-CoV-2 S1 Domain Vaccinology\n")
            f.write("**Target:** Multi-epitope vaccine construct\n\n")

            f.write("## Design Strategy\n\n")
            f.write("### Construct Architecture\n")
            f.write("1. **N-terminal Adjuvant**: TLR4 agonist (RS09) for immune activation\n")
            f.write("2. **MHC-II Epitopes**: CD4+ T-cell response with GPGPG linkers\n")
            f.write("3. **Domain Separator**: KK for processing independence\n")
            f.write("4. **MHC-I Epitopes**: CD8+ T-cell response with AAY linkers\n")
            f.write("5. **C-terminal Tags**: Stability and purification elements\n\n")

            f.write("## Selected Epitopes Summary\n\n")

            # MHC-I summary
            f.write("### MHC-I Epitopes (CD8+ T-cell targets)\n")
            f.write("| Peptide | HLA Allele | IC50 (nM) | Length |\n")
            f.write("|---------|------------|-----------|--------|\n")
            mhc_i_sorted = sorted(epitopes['MHC_I'], key=lambda x: x.ic50)
            for ep in mhc_i_sorted:
                f.write(f"| {ep.peptide} | {ep.allele} | {ep.ic50:.2f} | {ep.length} |\n")

            # MHC-II summary
            f.write("\n### MHC-II Epitopes (CD4+ T-cell targets)\n")
            f.write("| Peptide | HLA Allele | IC50 (nM) | Length |\n")
            f.write("|---------|------------|-----------|--------|\n")
            mhc_ii_sorted = sorted(epitopes['MHC_II'], key=lambda x: x.ic50)
            for ep in mhc_ii_sorted:
                f.write(f"| {ep.peptide} | {ep.allele} | {ep.ic50:.2f} | {ep.length} |\n")

            f.write("\n## Construct Designs\n\n")

            # Analyze each design
            for version, sequence in designs.items():
                f.write(f"### {version}\n\n")
                f.write(f"**Sequence ({len(sequence)} amino acids):**\n")
                f.write(f"```\n{sequence}\n```\n\n")

                properties = self.analyze_construct_properties(sequence)
                f.write("**Properties:**\n")
                f.write(f"- Length: {properties['length']} amino acids\n")
                f.write(f"- Estimated MW: {properties['molecular_weight_estimate_da']:.0f} Da ({properties['molecular_weight_estimate_da']/1000:.1f} kDa)\n")
                f.write(f"- Hydrophobic ratio: {properties['hydrophobic_ratio']:.2%}\n")
                f.write(f"- Solubility prediction: {properties['solubility_prediction']}\n\n")

        print(f"[SAVED] Construct design report: {report_file}")
        return report_file

    def save_constructs_fasta(self, designs: Dict[str, str], output_dir: str):
        """Save all construct designs as FASTA files."""

        for version, sequence in designs.items():
            fasta_file = os.path.join(output_dir, f'{version.lower().replace(" ", "_")}.fasta')

            with open(fasta_file, 'w') as f:
                f.write(f">{version}\n")
                f.write(f"{sequence}\n")

            print(f"[SAVED] {version} FASTA: {fasta_file}")

def main():
    """Main execution function for vaccine construct design."""
    print("MULTI-EPITOPE VACCINE CONSTRUCT DESIGN")
    print("=" * 50)
    print("Assembling selected epitopes into optimized vaccine constructs")

    # File paths
    base_dir = r"C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology"
    construct_dir = os.path.join(base_dir, "results", "sars_cov2", "construct_design")
    epitope_file = os.path.join(construct_dir, "selected_epitopes.json")

    # Initialize constructor
    constructor = VaccineConstructor()

    # Load selected epitopes
    print("\nLoading selected epitopes...")
    epitopes = constructor.load_selected_epitopes(epitope_file)

    print(f"Loaded: {len(epitopes['MHC_I'])} MHC-I + {len(epitopes['MHC_II'])} MHC-II epitopes")

    # Generate multiple construct designs
    print("\nGenerating vaccine construct designs...")

    designs = {
        'Version_1_Standard': constructor.design_construct_v1(epitopes),
        'Version_2_Alternating': constructor.design_construct_v2(epitopes),
        'Version_3_Optimized': constructor.design_construct_v3_optimized(epitopes)
    }

    # Display results
    print("\n" + "="*70)
    print("CONSTRUCT DESIGN RESULTS")
    print("="*70)

    for version, sequence in designs.items():
        print(f"\n{version} ({len(sequence)} aa):")
        print(f"{sequence}")

        properties = constructor.analyze_construct_properties(sequence)
        print(f"MW: {properties['molecular_weight_estimate_da']/1000:.1f} kDa, "
              f"Hydrophobic: {properties['hydrophobic_ratio']:.1%}")

    # Generate comprehensive report
    print("\nGenerating design documentation...")
    report_file = constructor.generate_construct_report(designs, epitopes, construct_dir)

    # Save FASTA files
    constructor.save_constructs_fasta(designs, construct_dir)

    # Final summary
    print("\n[COMPLETE] VACCINE CONSTRUCT DESIGN COMPLETE!")
    print(f"Generated: {len(designs)} construct variants")
    print("Files created:")
    print(f"  - Design report: vaccine_construct_design_report.md")
    for version in designs.keys():
        print(f"  - {version.lower().replace(' ', '_')}.fasta")

    return designs, epitopes

if __name__ == "__main__":
    designs, epitopes = main()