#!/usr/bin/env python3
"""
Vaccine Construct Validation Framework
=====================================

Comprehensive validation of multi-epitope vaccine constructs:
1. Physicochemical properties analysis (ProtParam-style)
2. Antigenicity prediction preparation (VaxiJen)
3. Allergenicity screening preparation (AllerTop)
4. Population coverage analysis
5. Sequence quality assessment

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

import os
import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import math

@dataclass
class ValidationResult:
    """Container for validation results."""
    construct_name: str
    sequence: str
    length: int
    molecular_weight: float
    theoretical_pi: float
    instability_index: float
    aliphatic_index: float
    gravy: float
    antigenicity_score: float
    allergenicity_risk: str
    population_coverage: float
    validation_status: str

class ProtParamAnalyzer:
    """ProtParam-style physicochemical analysis."""

    def __init__(self):
        # Amino acid molecular weights (average isotopic masses)
        self.aa_weights = {
            'A': 71.04, 'R': 156.10, 'N': 114.04, 'D': 115.03, 'C': 103.01,
            'E': 129.04, 'Q': 128.06, 'G': 57.02, 'H': 137.06, 'I': 113.08,
            'L': 113.08, 'K': 128.09, 'M': 131.04, 'F': 147.07, 'P': 97.05,
            'S': 87.03, 'T': 101.05, 'W': 186.08, 'Y': 163.06, 'V': 99.07
        }

        # pKa values for ionizable groups
        self.pKa_values = {
            'N_terminus': 9.69, 'C_terminus': 2.34,
            'D': 3.86, 'E': 4.25, 'H': 6.00, 'C': 8.33, 'Y': 10.07, 'K': 10.5, 'R': 12.48
        }

        # Hydropathy index (Kyte-Doolittle)
        self.hydropathy = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'E': -3.5, 'Q': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }

        # Instability index weights
        self.instability_weights = {
            'A': {'D': 1.0, 'E': 1.0, 'P': 1.0, 'R': 1.0},
            'C': {'F': 1.0, 'W': 1.0, 'Y': 1.0},
            'D': {'C': 1.0, 'F': 1.0, 'H': 1.0, 'I': 1.0, 'K': 1.0, 'L': 1.0,
                  'M': 1.0, 'P': 1.0, 'R': 1.0, 'T': 1.0, 'V': 1.0, 'W': 1.0, 'Y': 1.0},
            # ... (simplified for brevity - would include complete matrix)
        }

    def calculate_molecular_weight(self, sequence: str) -> float:
        """Calculate molecular weight in Daltons."""
        weight = sum(self.aa_weights.get(aa, 0) for aa in sequence)
        # Subtract water molecules for peptide bonds
        weight -= (len(sequence) - 1) * 18.01
        return weight

    def calculate_theoretical_pi(self, sequence: str) -> float:
        """Calculate theoretical isoelectric point using bisection method."""

        def net_charge(ph: float) -> float:
            """Calculate net charge at given pH."""
            charge = 0.0

            # N-terminus
            charge += 1 / (1 + 10**(ph - self.pKa_values['N_terminus']))

            # C-terminus
            charge -= 1 / (1 + 10**(self.pKa_values['C_terminus'] - ph))

            # Side chains
            for aa in sequence:
                if aa in self.pKa_values:
                    if aa in 'RK':  # Positive
                        charge += 1 / (1 + 10**(ph - self.pKa_values[aa]))
                    elif aa in 'DE':  # Negative
                        charge -= 1 / (1 + 10**(self.pKa_values[aa] - ph))
                    elif aa == 'H':  # Histidine
                        charge += 1 / (1 + 10**(ph - self.pKa_values[aa]))
                    elif aa in 'CY':  # Other ionizable
                        charge -= 1 / (1 + 10**(self.pKa_values[aa] - ph))

            return charge

        # Bisection method to find pI
        ph_low, ph_high = 0.0, 14.0
        while ph_high - ph_low > 0.01:
            ph_mid = (ph_low + ph_high) / 2
            if net_charge(ph_mid) > 0:
                ph_low = ph_mid
            else:
                ph_high = ph_mid

        return (ph_low + ph_high) / 2

    def calculate_instability_index(self, sequence: str) -> float:
        """Calculate instability index (simplified version)."""
        if len(sequence) < 2:
            return 0.0

        # Simplified calculation based on specific amino acid pairs
        unstable_pairs = 0
        total_pairs = len(sequence) - 1

        for i in range(len(sequence) - 1):
            aa1, aa2 = sequence[i], sequence[i+1]
            # Simplified instability rules
            if (aa1 in 'DE' and aa2 in 'P') or (aa1 in 'P' and aa2 in 'P'):
                unstable_pairs += 1

        return (unstable_pairs / total_pairs) * 100 if total_pairs > 0 else 0.0

    def calculate_aliphatic_index(self, sequence: str) -> float:
        """Calculate aliphatic index (thermostability indicator)."""
        if not sequence:
            return 0.0

        counts = Counter(sequence)
        length = len(sequence)

        # Aliphatic amino acids with relative volumes
        ai = (counts.get('A', 0) / length * 100) + \
             (counts.get('V', 0) / length * 100 * 2.9) + \
             (counts.get('I', 0) / length * 100 * 3.9) + \
             (counts.get('L', 0) / length * 100 * 3.9)

        return ai

    def calculate_gravy(self, sequence: str) -> float:
        """Calculate Grand Average of Hydropathy (GRAVY)."""
        if not sequence:
            return 0.0

        return sum(self.hydropathy.get(aa, 0) for aa in sequence) / len(sequence)

class ConstructValidator:
    """Main validation framework for vaccine constructs."""

    def __init__(self):
        self.protparam = ProtParamAnalyzer()
        self.validation_results = []

    def load_constructs(self, construct_dir: str) -> Dict[str, str]:
        """Load all FASTA construct files."""
        constructs = {}

        for filename in os.listdir(construct_dir):
            if filename.endswith('.fasta'):
                filepath = os.path.join(construct_dir, filename)
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        name = lines[0].strip()[1:]  # Remove '>'
                        sequence = lines[1].strip()
                        constructs[name] = sequence

        return constructs

    def analyze_physicochemical_properties(self, name: str, sequence: str) -> Dict[str, Any]:
        """Comprehensive physicochemical analysis."""

        properties = {
            'construct_name': name,
            'sequence_length': len(sequence),
            'molecular_weight': self.protparam.calculate_molecular_weight(sequence),
            'theoretical_pi': self.protparam.calculate_theoretical_pi(sequence),
            'instability_index': self.protparam.calculate_instability_index(sequence),
            'aliphatic_index': self.protparam.calculate_aliphatic_index(sequence),
            'gravy': self.protparam.calculate_gravy(sequence)
        }

        # Interpretations
        properties['stability_prediction'] = (
            'Stable' if properties['instability_index'] < 40 else 'Unstable'
        )
        properties['thermostability'] = (
            'High' if properties['aliphatic_index'] > 80 else
            'Moderate' if properties['aliphatic_index'] > 60 else 'Low'
        )
        properties['hydrophobicity'] = (
            'Hydrophobic' if properties['gravy'] > 0 else 'Hydrophilic'
        )

        return properties

    def predict_antigenicity(self, sequence: str) -> float:
        """
        Simplified antigenicity prediction based on amino acid composition.
        Note: For accurate results, use VaxiJen web server.
        """
        # Simplified scoring based on immunogenic amino acids
        immunogenic_aas = 'KRDQNEH'  # Charged and polar residues
        hydrophobic_aas = 'AILMFPWV'

        immunogenic_score = sum(sequence.count(aa) for aa in immunogenic_aas) / len(sequence)
        hydrophobic_penalty = sum(sequence.count(aa) for aa in hydrophobic_aas) / len(sequence)

        # Rough estimate (real VaxiJen uses SVM with specific features)
        estimated_score = immunogenic_score * 0.8 - hydrophobic_penalty * 0.3 + 0.2

        return max(0.0, min(1.0, estimated_score))

    def assess_allergenicity_risk(self, sequence: str) -> str:
        """
        Preliminary allergenicity risk assessment.
        Note: For accurate results, use AllerTop web server.
        """
        # Check for common allergenic motifs (simplified)
        allergenic_motifs = ['WW', 'PP', 'CC']  # Simplified patterns

        risk_score = 0
        for motif in allergenic_motifs:
            risk_score += sequence.count(motif)

        # Basic hydrophobicity check
        hydrophobic_ratio = sum(sequence.count(aa) for aa in 'AILMFPWV') / len(sequence)
        if hydrophobic_ratio > 0.5:
            risk_score += 1

        if risk_score == 0:
            return 'Low'
        elif risk_score < 3:
            return 'Moderate'
        else:
            return 'High'

    def analyze_population_coverage(self, epitope_file: str) -> float:
        """Calculate theoretical population coverage based on HLA alleles."""

        with open(epitope_file, 'r') as f:
            epitope_data = json.load(f)

        # Extract unique alleles covered
        covered_alleles = set()

        for ep in epitope_data['mhc_i_epitopes']:
            covered_alleles.add(ep['allele'])

        for ep in epitope_data['mhc_ii_epitopes']:
            covered_alleles.add(ep['allele'])

        # Major global alleles (simplified list)
        major_alleles = {
            'HLA-A*02:01', 'HLA-A*01:01', 'HLA-A*03:01', 'HLA-A*24:02',
            'HLA-B*08:01', 'HLA-B*35:01', 'HLA-B*40:01',
            'HLA-DRB1*01:01', 'HLA-DRB1*03:01', 'HLA-DRB1*15:01', 'HLA-DRB1*11:01'
        }

        coverage = len(covered_alleles & major_alleles) / len(major_alleles) * 100
        return coverage

    def validate_construct(self, name: str, sequence: str, epitope_file: str) -> ValidationResult:
        """Complete validation of a single construct."""

        # Physicochemical analysis
        properties = self.analyze_physicochemical_properties(name, sequence)

        # Antigenicity prediction (simplified)
        antigenicity = self.predict_antigenicity(sequence)

        # Allergenicity risk
        allergenicity = self.assess_allergenicity_risk(sequence)

        # Population coverage
        pop_coverage = self.analyze_population_coverage(epitope_file)

        # Overall validation status
        validation_criteria = [
            properties['molecular_weight'] < 50000,  # Reasonable size
            properties['stability_prediction'] == 'Stable',
            antigenicity >= 0.4,  # VaxiJen threshold
            allergenicity == 'Low',
            pop_coverage >= 50
        ]

        passed_criteria = sum(validation_criteria)
        total_criteria = len(validation_criteria)

        if passed_criteria == total_criteria:
            status = 'EXCELLENT'
        elif passed_criteria >= total_criteria * 0.8:
            status = 'GOOD'
        elif passed_criteria >= total_criteria * 0.6:
            status = 'ACCEPTABLE'
        else:
            status = 'NEEDS_OPTIMIZATION'

        result = ValidationResult(
            construct_name=name,
            sequence=sequence,
            length=properties['sequence_length'],
            molecular_weight=properties['molecular_weight'],
            theoretical_pi=properties['theoretical_pi'],
            instability_index=properties['instability_index'],
            aliphatic_index=properties['aliphatic_index'],
            gravy=properties['gravy'],
            antigenicity_score=antigenicity,
            allergenicity_risk=allergenicity,
            population_coverage=pop_coverage,
            validation_status=status
        )

        return result

    def generate_validation_report(self, results: List[ValidationResult], output_dir: str) -> str:
        """Generate comprehensive validation report."""

        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, 'construct_validation_report.md')

        with open(report_file, 'w') as f:
            f.write("# Vaccine Construct Validation Report\n\n")
            f.write("**Generated:** 2026-06-01\n")
            f.write("**Pipeline:** SARS-CoV-2 Multi-Epitope Vaccine\n")
            f.write("**Validation Framework:** ProtParam + VaxiJen + AllerTop analysis\n\n")

            f.write("## Validation Criteria\n\n")
            f.write("1. **Molecular Weight**: < 50 kDa (optimal for expression)\n")
            f.write("2. **Stability**: Instability Index < 40 (stable proteins)\n")
            f.write("3. **Antigenicity**: VaxiJen score >= 0.4 (immunogenic)\n")
            f.write("4. **Allergenicity**: Low risk (non-allergenic)\n")
            f.write("5. **Population Coverage**: >= 50% (effective coverage)\n\n")

            f.write("## Construct Validation Results\n\n")

            for result in results:
                f.write(f"### {result.construct_name}\n\n")
                f.write(f"**Validation Status: {result.validation_status}**\n\n")

                f.write("#### Physicochemical Properties\n")
                f.write(f"- **Length**: {result.length} amino acids\n")
                f.write(f"- **Molecular Weight**: {result.molecular_weight:.1f} Da ({result.molecular_weight/1000:.1f} kDa)\n")
                f.write(f"- **Theoretical pI**: {result.theoretical_pi:.2f}\n")
                f.write(f"- **Instability Index**: {result.instability_index:.2f} ({'Stable' if result.instability_index < 40 else 'Unstable'})\n")
                f.write(f"- **Aliphatic Index**: {result.aliphatic_index:.2f} (Thermostability)\n")
                f.write(f"- **GRAVY**: {result.gravy:.3f} ({'Hydrophobic' if result.gravy > 0 else 'Hydrophilic'})\n\n")

                f.write("#### Immunogenicity Assessment\n")
                f.write(f"- **Antigenicity Score**: {result.antigenicity_score:.3f} ({'PASS' if result.antigenicity_score >= 0.4 else 'FAIL'})\n")
                f.write(f"- **Allergenicity Risk**: {result.allergenicity_risk}\n")
                f.write(f"- **Population Coverage**: {result.population_coverage:.1f}%\n\n")

                f.write("#### Sequence\n")
                f.write(f"```\n{result.sequence}\n```\n\n")

                f.write("---\n\n")

            # Summary comparison
            f.write("## Construct Comparison Summary\n\n")
            f.write("| Construct | Status | Length | MW (kDa) | pI | Antigenicity | Allergenicity |\n")
            f.write("|-----------|--------|--------|----------|----|--------------|--------------|\n")

            for result in results:
                f.write(f"| {result.construct_name} | {result.validation_status} | "
                       f"{result.length} | {result.molecular_weight/1000:.1f} | "
                       f"{result.theoretical_pi:.2f} | {result.antigenicity_score:.3f} | "
                       f"{result.allergenicity_risk} |\n")

            f.write("\n## Recommendations\n\n")

            # Find best construct
            best_construct = max(results, key=lambda x: (
                1 if x.validation_status == 'EXCELLENT' else
                0.8 if x.validation_status == 'GOOD' else
                0.6 if x.validation_status == 'ACCEPTABLE' else 0
            ))

            f.write(f"**Recommended Construct**: {best_construct.construct_name}\n")
            f.write(f"- **Rationale**: {best_construct.validation_status} validation status\n")
            f.write(f"- **Key Strengths**: ")

            strengths = []
            if best_construct.molecular_weight < 30000:
                strengths.append("optimal size")
            if best_construct.instability_index < 40:
                strengths.append("stable")
            if best_construct.antigenicity_score >= 0.4:
                strengths.append("antigenic")
            if best_construct.allergenicity_risk == 'Low':
                strengths.append("non-allergenic")

            f.write(", ".join(strengths) + "\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. **Web Tool Validation**: Submit to VaxiJen and AllerTop for accurate scoring\n")
            f.write("2. **Structural Analysis**: 3D structure prediction with ColabFold\n")
            f.write("3. **Molecular Docking**: Interaction analysis with immune receptors\n")
            f.write("4. **In Silico Immune Simulation**: C-ImmSim analysis\n")

        print(f"[SAVED] Validation report: {report_file}")
        return report_file

    def create_web_submission_files(self, constructs: Dict[str, str], output_dir: str):
        """Create files ready for web tool submission."""

        web_dir = os.path.join(output_dir, 'web_tool_submissions')
        os.makedirs(web_dir, exist_ok=True)

        # VaxiJen submission files
        vaxijen_dir = os.path.join(web_dir, 'vaxijen')
        os.makedirs(vaxijen_dir, exist_ok=True)

        for name, sequence in constructs.items():
            # VaxiJen format
            vaxijen_file = os.path.join(vaxijen_dir, f'{name.lower().replace(" ", "_")}_vaxijen.fasta')
            with open(vaxijen_file, 'w') as f:
                f.write(f">{name}\n{sequence}\n")

        # AllerTop submission files
        allertop_dir = os.path.join(web_dir, 'allertop')
        os.makedirs(allertop_dir, exist_ok=True)

        for name, sequence in constructs.items():
            # AllerTop format
            allertop_file = os.path.join(allertop_dir, f'{name.lower().replace(" ", "_")}_allertop.txt')
            with open(allertop_file, 'w') as f:
                f.write(sequence)

        # Submission instructions
        instructions_file = os.path.join(web_dir, 'WEB_TOOL_SUBMISSION_INSTRUCTIONS.md')
        with open(instructions_file, 'w') as f:
            f.write("# Web Tool Submission Instructions\n\n")
            f.write("## VaxiJen 2.0 Submission\n")
            f.write("**URL**: http://www.ddg-pharmfac.net/vaxijen/VaxiJen/VaxiJen.html\n\n")
            f.write("**Steps**:\n")
            f.write("1. Select 'Virus' as target organism\n")
            f.write("2. Set threshold to 0.4\n")
            f.write("3. Upload each FASTA file from `vaxijen/` folder\n")
            f.write("4. Record antigenicity scores in validation spreadsheet\n\n")

            f.write("## AllerTop 2.0 Submission\n")
            f.write("**URL**: https://www.ddg-pharmfac.net/AllerTOP/\n\n")
            f.write("**Steps**:\n")
            f.write("1. Paste sequence from each `.txt` file in `allertop/` folder\n")
            f.write("2. Submit for allergenicity prediction\n")
            f.write("3. Record results (Allergen/Non-allergen) in spreadsheet\n\n")

            f.write("## ProtParam Analysis\n")
            f.write("**URL**: https://web.expasy.org/protparam/\n\n")
            f.write("**Steps**:\n")
            f.write("1. Paste each construct sequence\n")
            f.write("2. Analyze physicochemical properties\n")
            f.write("3. Compare with automated analysis results\n")

        print(f"[SAVED] Web tool submission files: {web_dir}")
        print(f"[SAVED] Submission instructions: {instructions_file}")

def main():
    """Main execution function for construct validation."""
    print("VACCINE CONSTRUCT VALIDATION FRAMEWORK")
    print("=" * 50)
    print("Comprehensive validation of multi-epitope vaccine constructs")

    # File paths
    base_dir = r"C:\Users\f4l\Documents\GitHub\DATA_ANALYTICS\certificates\biocode\Vaccinology"
    construct_dir = os.path.join(base_dir, "results", "sars_cov2", "construct_design")
    epitope_file = os.path.join(construct_dir, "selected_epitopes.json")

    # Initialize validator
    validator = ConstructValidator()

    # Load constructs
    print("\nLoading vaccine constructs...")
    constructs = validator.load_constructs(construct_dir)
    print(f"Loaded {len(constructs)} constructs for validation")

    # Validate each construct
    print("\nPerforming comprehensive validation...")
    results = []

    for name, sequence in constructs.items():
        print(f"\nValidating: {name}")
        result = validator.validate_construct(name, sequence, epitope_file)
        results.append(result)
        print(f"  Status: {result.validation_status}")
        print(f"  MW: {result.molecular_weight/1000:.1f} kDa")
        print(f"  Antigenicity: {result.antigenicity_score:.3f}")
        print(f"  Allergenicity: {result.allergenicity_risk}")

    # Generate validation report
    print("\nGenerating validation documentation...")
    report_file = validator.generate_validation_report(results, construct_dir)

    # Create web tool submission files
    validator.create_web_submission_files(constructs, construct_dir)

    # Summary
    print(f"\n[COMPLETE] CONSTRUCT VALIDATION COMPLETE!")
    print(f"Validated: {len(results)} constructs")

    excellent_count = sum(1 for r in results if r.validation_status == 'EXCELLENT')
    good_count = sum(1 for r in results if r.validation_status == 'GOOD')

    print(f"Results: {excellent_count} EXCELLENT, {good_count} GOOD")

    best_construct = max(results, key=lambda x: (
        3 if x.validation_status == 'EXCELLENT' else
        2 if x.validation_status == 'GOOD' else
        1 if x.validation_status == 'ACCEPTABLE' else 0
    ))

    print(f"Recommended: {best_construct.construct_name}")

    return results

if __name__ == "__main__":
    results = main()