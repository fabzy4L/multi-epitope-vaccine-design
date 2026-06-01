#!/usr/bin/env python3
"""
Validation Tier — Structured metadata for construct validation status.

Replaces hardcoded "validated" language with tier-specific, publication-appropriate labels.
Current status for all constructs: COMPUTATIONALLY_VERIFIED.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List


class ValidationTier(Enum):
    COMPUTATIONALLY_VERIFIED = "computationally_verified"
    IN_VITRO_CONFIRMED = "in_vitro_confirmed"
    IN_VIVO_CONFIRMED = "in_vivo_confirmed"


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
    known_design_flags: List[str] = field(default_factory=list)

    def validation_label(self) -> str:
        """Returns publication-appropriate language for this construct's status."""
        labels = {
            ValidationTier.COMPUTATIONALLY_VERIFIED: "computationally designed construct pending experimental validation",
            ValidationTier.IN_VITRO_CONFIRMED: "in vitro confirmed construct",
            ValidationTier.IN_VIVO_CONFIRMED: "experimentally validated construct",
        }
        return labels[self.validation_tier]

    def summary(self) -> str:
        return (
            f"Construct {self.construct_id}: {self.molecular_weight_kda} kDa | "
            f"pI {self.theoretical_pi} | Status: {self.validation_label()}"
        )


# ---- Instantiated constructs ----

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
        "ProtParam", "NetMHCpan-4.1", "NetMHCIIpan-4.0", "IEDB_population_coverage"
    ],
    validation_pending=[
        "AlphaFold_structural", "solubility_prescreen",
        "HLA_binding_assay", "T_cell_activation_study", "animal_model"
    ],
    known_design_flags=[
        # DESIGN DECISION — documented 2026-06-01
        #
        # VLSFELLHAPATVCG (4.06nM, HLA-DRB1*01:01) is the best MHC-II binder in the pipeline
        # but is ABSENT from v3. Under the scoring formula it scored 17.64, higher than the
        # two selected epitopes (17.28 and 11.75). Its exclusion was intentional:
        # REASON: VLSFELLHAPATVCG contains a free cysteine at position 13 (PATVCG).
        # Free cysteines in unstructured peptide constructs cause disulfide bond formation
        # during E. coli expression and IMAC purification, resulting in insoluble aggregates.
        # This is a known practical constraint in peptide subunit vaccine expression.
        # ACTION REQUIRED: Before finalizing v3 for synthesis, evaluate cysteine capping
        # (Cys->Ser substitution at position 13) and retest binding affinity in silico.
        # A v4 construct with VLSFELL(S)APATVCG would restore DRB1*01:01 coverage.
        "VLSFELLHAPATVCG_excluded: free cysteine at pos-13, expression/aggregation risk",

        # MHC-II redundancy: both selected epitopes (QTLLALHRSYLTPGD, INITRFQTLLALHRS)
        # share a 9-mer overlap (QTLLALHRS) and both target HLA-DRB1*15:01.
        # v3 has NO coverage of HLA-DRB1*01:01 in its MHC-II region.
        # This reduces effective allele diversity vs what the scoring intended.
        "MHC-II_overlap: QTLLALHRS 9-mer shared between both MHC-II epitopes, both DRB1*15:01",

        # YLQPRTFLL (4.30nM, HLA-A*02:01) is absent from v3.
        # HLA-A*02:01 is the highest-frequency HLA allele globally (~30% prevalence).
        # Its absence limits v3 population coverage relative to v1/v2.
        "YLQPRTFLL_excluded: HLA-A*02:01 coverage gap, globally most prevalent allele",

        # Structural anomaly: sequence between KK separator and first MHC-I epitope
        # reads KKGPGPGKKLPFNDGVYF — a double-KK with GPGPG between them.
        # This appears to be a manual construction artifact (KK appears at pos 69 and 76).
        # Functional impact unknown; may affect proteasomal processing at the boundary.
        "BOUNDARY_ARTIFACT: double-KK at MHC-II/MHC-I junction (pos 69+76), review needed",
    ],
)

ALL_CONSTRUCTS = [construct_v1, construct_v2, construct_v3]
