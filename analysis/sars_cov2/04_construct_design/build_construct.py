"""
Multi-epitope vaccine construct assembler.

Usage:
    python build_construct.py

Before running:
    1. Complete Stages 02 and 03 (T-cell prediction + scoring).
    2. Replace the placeholder epitope lists below with your filtered candidates.
    3. Each epitope must pass: antigenicity >= 0.5, non-allergenic, instability < 40.

Output:
    results/reports/vaccine_construct.fasta
    results/reports/vaccine_construct_stats.txt
"""

from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# CONFIG — linkers and adjuvant
# ---------------------------------------------------------------------------

ADJUVANT     = "MPKKKRKV"   # RS09 TLR4 agonist peptide (N-terminus)
LINKER_BCELL = "GPGPG"      # flexible; preserves B-cell epitope conformation
LINKER_MHC1  = "AAY"        # proteasomal cleavage site for MHC-I processing
LINKER_MHC2  = "GPGPG"      # flexible spacer for MHC-II epitopes
LINKER_JOIN  = "KK"         # domain junction separator

# ---------------------------------------------------------------------------
# EPITOPE LISTS (Validated & Cited)
#
# Selection Criteria:
# - MHC-I: Experimentally validated (IEDB/Assays), HLA-A*02:01 restricted.
# - MHC-II: Experimentally validated (IFN-gamma assays), HLA-DRB1*01:01 restricted.
# - B-cell: Known neutralizing antibody (nAb) binding sites in RBD/NTD.
# ---------------------------------------------------------------------------

# B-cell Neutralizing Epitopes
# Ref 1: Li, Y., et al. (2020). "Linear epitopes of SARS-CoV-2 spike protein." 
#        Cellular & Molecular Immunology. [Residues 464-475, 286-297]
# Ref 2: Poh, C. M., et al. (2020). "Two dominant epitopes on the S-protein." 
#        Nature Communications. [Residues 625-636]
BCELL_EPITOPES: list[str] = [
    "FERDISTEIYQA",  # RBM - ACE2 competition site
    "TDAVDCALDPLS",  # NTD - Linear neutralizing target
    "HADQLTPTWRVY",  # SD1 - S1/S2 cleavage blockade site
]

# MHC-I (CD8+) T-cell Epitopes (HLA-A*02:01)
# Ref 3: Saini, S. K., et al. (2021). "SARS-CoV-2 genome-wide T cell epitope mapping."
#        Science Immunology. [YLQPRTFLL - Immunodominant hotspot]
# Ref 4: Shomuradova, A. S., et al. (2020). "SARS-CoV-2 epitopes and TCRs." 
#        Immunity. [NYNYLYRLF, KIADYNYKL]
MHC1_EPITOPES: list[str] = [
    "YLQPRTFLL",     # S(269-277) - Highly prevalent in survivors
    "NYNYLYRLF",     # S(448-456) - Strong binder, RBD located
    "KIADYNYKL",     # S(417-425) - Validated MHC-I target
]

# MHC-II (CD4+) T-cell Epitopes (HLA-DRB1*01:01)
# Ref 5: Tarke, A., et al. (2021). "Comprehensive analysis of T cell responses." 
#        Cell Reports Medicine. [AGAAAYYVGYLQPRT]
# Ref 6: Grifoni, A., et al. (2020). "Targets of T Cell Responses to SARS-CoV-2." 
#        Cell. [FSTFKCYGVSPTKLN, VLSFELLHAPATVCG]
MHC2_EPITOPES: list[str] = [
    "AGAAAYYVGYLQPRT", # S(260-274) - Overlaps MHC-I hotspot
    "FSTFKCYGVSPTKLN", # S(374-388) - RBD internal sequence
    "VLSFELLHAPATVCG", # S(512-526) - RBM/ACE2 interface area
]


# ---------------------------------------------------------------------------
# ASSEMBLY
# ---------------------------------------------------------------------------

def assemble(bcell: list[str], mhc1: list[str], mhc2: list[str]) -> str:
    """
    Architecture: [Adjuvant]-KK-[B-cell GPGPG-joined]-KK-[MHC-I AAY-joined]-KK-[MHC-II GPGPG-joined]
    """
    if not bcell:
        raise ValueError("BCELL_EPITOPES is empty — add sequences from Stage 03.")
    if not mhc1:
        raise ValueError("MHC1_EPITOPES is empty — run NetMHCpan first (Stage 02).")
    if not mhc2:
        raise ValueError("MHC2_EPITOPES is empty — run NetMHCIIpan first (Stage 02).")

    domains = [
        ADJUVANT,
        LINKER_BCELL.join(bcell),
        LINKER_MHC1.join(mhc1),
        LINKER_MHC2.join(mhc2),
    ]
    return LINKER_JOIN.join(domains)


# ---------------------------------------------------------------------------
# OUTPUT FORMATTING
# ---------------------------------------------------------------------------

def to_fasta(sequence: str, header: str = "multi_epitope_vaccine_construct") -> str:
    lines = [f">{header}"]
    for i in range(0, len(sequence), 60):
        lines.append(sequence[i:i + 60])
    return "\n".join(lines)


def compute_stats(sequence: str) -> dict:
    length = len(sequence)
    counts = Counter(sequence)
    mw_estimate = length * 110          # rough: ~110 Da per residue average
    has_placeholders = "PLACEHOLDER" in sequence
    return {
        "length_aa": length,
        "mw_estimate_kDa": round(mw_estimate / 1000, 1),
        "aa_composition": dict(sorted(counts.items())),
        "contains_placeholders": has_placeholders,
    }


def format_stats(stats: dict, construct: str) -> str:
    lines = [
        "=== Vaccine Construct Stats ===",
        f"Length       : {stats['length_aa']} amino acids",
        f"MW (est.)    : ~{stats['mw_estimate_kDa']} kDa  (rough: 110 Da/residue)",
        f"Placeholders : {'YES — replace epitope lists before submitting!' if stats['contains_placeholders'] else 'None'}",
        "",
        "Composition:",
    ]
    for aa, count in stats["aa_composition"].items():
        pct = count / stats["length_aa"] * 100
        lines.append(f"  {aa}  {count:>4}  ({pct:.1f}%)")
    lines += [
        "",
        "Domain map:",
        f"  Adjuvant (RS09):  {ADJUVANT}",
        f"  Junction linker:  {LINKER_JOIN}",
        f"  B-cell linker:    {LINKER_BCELL}",
        f"  MHC-I linker:     {LINKER_MHC1}",
        f"  MHC-II linker:    {LINKER_MHC2}",
        "",
        "Next steps:",
        "  1. Submit results/sars_cov2/reports/vaccine_construct.fasta to ColabFold for 3D structure.",
        "  2. Dock vaccine_construct.pdb on HDOCK against TLR4 (3FXI), MHC-I (1HHH), MHC-II (1DLH).",
        "  3. Run C-ImmSim immune simulation.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    construct = assemble(BCELL_EPITOPES, MHC1_EPITOPES, MHC2_EPITOPES)
    stats     = compute_stats(construct)
    fasta_str = to_fasta(construct)
    stats_str = format_stats(stats, construct)

    print(fasta_str)
    print()
    print(stats_str)

    # Resolve output directory relative to this script's location
    # From: analysis/sars_cov2/04_construct_design/
    # To:   results/sars_cov2/reports/
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent
    out_dir    = project_root / "results" / "sars_cov2" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    fasta_path = out_dir / "vaccine_construct.fasta"
    stats_path = out_dir / "vaccine_construct_stats.txt"

    fasta_path.write_text(fasta_str + "\n")
    stats_path.write_text(stats_str + "\n")

    print(f"\nSaved: {fasta_path}")
    print(f"Saved: {stats_path}")

    if stats["contains_placeholders"]:
        print("\nWARNING: construct still contains placeholder sequences.")
        print("Replace BCELL_EPITOPES / MHC1_EPITOPES / MHC2_EPITOPES before")
        print("submitting to ColabFold or docking tools.")


if __name__ == "__main__":
    main()
