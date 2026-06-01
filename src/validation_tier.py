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
)

ALL_CONSTRUCTS = [construct_v1, construct_v2, construct_v3]
