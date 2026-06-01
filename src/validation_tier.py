#!/usr/bin/env python3
"""
Validation Tier — Structured metadata for construct validation status and design flags.

Replaces hardcoded "validated" language with tier-specific, publication-appropriate labels.
DesignFlag dataclass provides structured traceability for known design decisions.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict


class ValidationTier(Enum):
    COMPUTATIONALLY_VERIFIED = "computationally_verified"
    IN_VITRO_CONFIRMED = "in_vitro_confirmed"
    IN_VIVO_CONFIRMED = "in_vivo_confirmed"


@dataclass
class DesignFlag:
    flag_id: str
    severity: str           # 'JUSTIFIED' | 'SCORING_ARTIFACT' | 'UNDOCUMENTED_GAP' | 'UNKNOWN_RISK'
    description: str
    paper_action: str       # What goes in the paper
    code_action: str        # What was fixed in code
    blocks_synthesis: bool  # True = do not order synthesis until resolved


@dataclass
class ConstructMetadata:
    construct_id: str
    sequence: str
    molecular_weight_kda: float
    theoretical_pi: float
    instability_index: float
    validation_tier: ValidationTier
    validation_methods_completed: List[str] = field(default_factory=list)
    validation_pending: List[str] = field(default_factory=list)
    known_design_flags: List[DesignFlag] = field(default_factory=list)
    structural_notes: Optional[Dict] = None

    def synthesis_cleared(self) -> bool:
        """Returns False if any flag blocks synthesis."""
        return not any(f.blocks_synthesis for f in self.known_design_flags)

    def validation_label(self) -> str:
        """Returns publication-appropriate language for this construct's status."""
        labels = {
            ValidationTier.COMPUTATIONALLY_VERIFIED:
                "computationally designed construct pending experimental validation",
            ValidationTier.IN_VITRO_CONFIRMED: "in vitro confirmed construct",
            ValidationTier.IN_VIVO_CONFIRMED: "experimentally validated construct",
        }
        return labels[self.validation_tier]

    def summary(self) -> str:
        cleared = "CLEARED" if self.synthesis_cleared() else "BLOCKED"
        return (
            f"Construct {self.construct_id}: {self.molecular_weight_kda} kDa | "
            f"pI {self.theoretical_pi} | {self.validation_label()} | "
            f"Synthesis: {cleared} | Flags: {len(self.known_design_flags)}"
        )


# ---- Construct definitions ----

construct_v1 = ConstructMetadata(
    construct_id="v1_standard",
    sequence=(
        "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGVLSFELLHAPATVCGGPGPGQTLLALHRSYLTPGD"
        "GPGPGINITRFQTLLALHRSKKRLFRKSNLKAAYLLPFNDGVYFAAYFPNITNLCPFAAYVLYNSASFSTFK"
        "GGGSPAPAPGSHHHHHH"
    ),
    molecular_weight_kda=15.0,
    theoretical_pi=10.33,
    instability_index=28.4,
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=[
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0", "IEDB_population_coverage"
    ],
    validation_pending=[
        "AlphaFold_structural", "solubility_prescreen",
        "HLA_binding_assay", "T_cell_activation_study", "animal_model"
    ],
)

construct_v2 = ConstructMetadata(
    construct_id="v2_alternating",
    sequence=(
        "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGVLSFELLHAPATVCGAAYRLFRKSNLK"
        "GPGPGQTLLALHRSYLTPGDAAYLLPFNDGVYFGPGPGINITRFQTLLALHRSAAYFPNITNLCPF"
        "AAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
    ),
    molecular_weight_kda=15.1,
    theoretical_pi=10.12,
    instability_index=27.9,
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=[
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0", "IEDB_population_coverage"
    ],
    validation_pending=[
        "AlphaFold_structural", "solubility_prescreen",
        "HLA_binding_assay", "T_cell_activation_study", "animal_model"
    ],
)

construct_v3 = ConstructMetadata(
    construct_id="v3_optimized",
    sequence=(
        "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD"
        "GPGPGINITRFQTLLALHRSKKGPGPGKKLPFNDGVYFAAYRLFRKSNLK"
        "AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
    ),
    molecular_weight_kda=12.7,
    theoretical_pi=9.89,
    instability_index=0.85,
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=[
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0",
        "IEDB_population_coverage", "decoy_benchmark_KS_p6.87e-24",
        "solubility_prescreen"
    ],
    validation_pending=[
        "NetChop_junction_analysis", "AlphaFold_structural",
        "HLA_binding_assay", "T_cell_activation_study", "animal_model"
    ],
    known_design_flags=[
        DesignFlag(
            flag_id="FLAG_01_CYS_EXCLUSION",
            severity="JUSTIFIED",
            description=(
                "VLSFELLHAPATVCG (top MHC-II binder, 4.06nM, DRB1*01:01) excluded "
                "due to free cysteine at position 13. Intermolecular disulfide "
                "bond formation risk during E. coli expression and IMAC purification. "
                "Also applies to FPNITNLCPF (in v3, Cys at pos 8) — flagged for v4 redesign."
            ),
            paper_action=(
                "Document in methods: VLSFELLHAPATVCG excluded due to Cys13 "
                "aggregation risk. FPNITNLCPF retained in v3 sequence for paper "
                "continuity but excluded by updated scorer. Cys->Ser substitutions "
                "proposed for both in v4 to restore DRB1*01:01 coverage."
            ),
            code_action="cysteine_penalty() added to combined_score() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_02_MHCII_REDUNDANCY",
            severity="SCORING_ARTIFACT",
            description=(
                "Both MHC-II epitopes target DRB1*15:01. 9-mer overlap "
                "(QTLLALHRS) between QTLLALHRSYLTPGD and INITRFQTLLALHRS. "
                "DRB1*01:01 MHC-II coverage is zero in v3. "
                "Diversity penalty did not fire for same-allele repeats in original scorer."
            ),
            paper_action=(
                "Limitations: v3 MHC-II coverage restricted to DRB1*15:01 "
                "due to scoring artifact. DRB1*01:01 absence acknowledged. "
                "Addressed by allele_diversity_penalty() in updated scorer for v4."
            ),
            code_action="allele_diversity_penalty() added to combined_score() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_03_HLA_A0201_ABSENT",
            severity="UNDOCUMENTED_GAP",
            description=(
                "HLA-A*02:01 (~30% global frequency) not covered in v3. "
                "YLQPRTFLL identified in candidate pool but excluded by combined scoring threshold. "
                "Most prevalent MHC-I allele globally — absence notable for peer review."
            ),
            paper_action=(
                "Limitations: HLA-A*02:01 coverage absent from v3. YLQPRTFLL identified "
                "in candidate pool (4.30nM, rank 0.03%) but excluded by scoring threshold. "
                "Prioritized for inclusion in v4 construct."
            ),
            code_action="No code change — documented gap only. Scorer working as designed.",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_04_DOUBLE_KK_JUNCTION",
            severity="UNKNOWN_RISK",
            description=(
                "KKGPGPGKK double-KK junction at MHC-II/MHC-I boundary (res 70-78). "
                "NetChop C-term 3.0 analysis (Phase 8A): max cleavage score 0.948 "
                "(K77), mean 0.411. K70=0.947, K71=0.788, K77=0.948, K78=0.799 — "
                "all four flanking lysines exceed 0.7 redesign threshold. "
                "High cleavage probability at both KK sites risks fragmentation of "
                "the GPGPG linker, destroying the MHC-I epitope N-terminus."
            ),
            paper_action=(
                "Methods: NetChop C-term 3.0 analysis of v3 KKGPGPGKK junction "
                "returned max cleavage score 0.948 (threshold 0.7). Junction "
                "redesigned to single KKGPGPG in v3.1 (trailing KK removed). "
                "v3 not advanced to synthesis; v3.1 is the lead candidate."
            ),
            code_action=(
                "Phase 8A complete. results/netchop/netchop_report.json generated. "
                "v3.1 construct defined in validation_tier.py with corrected junction."
            ),
            blocks_synthesis=True   # v3 blocked; v3.1 is the synthesis candidate
        ),
    ]
)

construct_v3_1 = ConstructMetadata(
    construct_id="v3_1_single_kk",
    sequence=(
        "MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGD"
        "GPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLK"
        "AAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH"
    ),
    molecular_weight_kda=15.07,   # BioPython ProtParam
    theoretical_pi=10.13,          # BioPython ProtParam; HIGH_PI_EXPRESSION_RISK
    instability_index=42.64,       # BioPython ProtParam
    validation_tier=ValidationTier.COMPUTATIONALLY_VERIFIED,
    validation_methods_completed=[
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0",
        "IEDB_population_coverage", "decoy_benchmark_KS_p6.87e-24",
        "solubility_prescreen", "NetChop_junction_analysis"
    ],
    validation_pending=[
        "AlphaFold_structural", "RFdiffusion_ensemble",
        "HLA_binding_assay", "T_cell_activation_study", "animal_model"
    ],
    known_design_flags=[
        DesignFlag(
            flag_id="FLAG_01_CYS_EXCLUSION",
            severity="JUSTIFIED",
            description=(
                "VLSFELLHAPATVCG (top MHC-II binder, DRB1*01:01) excluded due to "
                "free Cys13. FPNITNLCPF retained for paper continuity but flagged. "
                "Cys->Ser substitutions proposed for v4."
            ),
            paper_action=(
                "Cys-containing epitopes excluded or flagged. Cys->Ser substitutions "
                "proposed for v4 to restore DRB1*01:01 coverage."
            ),
            code_action="cysteine_penalty() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_02_MHCII_REDUNDANCY",
            severity="SCORING_ARTIFACT",
            description=(
                "Both MHC-II epitopes target DRB1*15:01. DRB1*01:01 coverage absent. "
                "allele_diversity_penalty() added to scorer for v4."
            ),
            paper_action=(
                "Limitations: v3.1 MHC-II coverage restricted to DRB1*15:01. "
                "Addressed by updated scorer in v4."
            ),
            code_action="allele_diversity_penalty() in scoring.py",
            blocks_synthesis=False
        ),
        DesignFlag(
            flag_id="FLAG_03_HLA_A0201_ABSENT",
            severity="UNDOCUMENTED_GAP",
            description=(
                "HLA-A*02:01 (~30% global frequency) not covered. YLQPRTFLL "
                "identified in candidate pool but excluded by scoring threshold."
            ),
            paper_action=(
                "Limitations: HLA-A*02:01 absent. YLQPRTFLL prioritized for v4."
            ),
            code_action="No code change — documented gap only.",
            blocks_synthesis=False
        ),
        # FLAG_04 resolved: double-KK removed in v3.1. No synthesis block.
    ]
)

ALL_CONSTRUCTS = [construct_v1, construct_v2, construct_v3, construct_v3_1]
