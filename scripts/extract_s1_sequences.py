#!/usr/bin/env python3
"""
extract_s1_sequences.py
=======================
Extract SARS-CoV-2 Spike / S1-subunit sequences from a CD-HIT representative
FASTA file, ready for MHC-I / MHC-II epitope prediction on IEDB or locally
via NetMHCpan / NetMHCIIpan.

Pipeline context
----------------
  Input  : analysis/01_clustering/1624324292.fas.1   (CD-HIT rep seqs)
  Output : analysis/02_epitope_prediction/s1_candidates.fasta
           analysis/02_epitope_prediction/s1_extraction_report.txt

Usage
-----
  # Basic — auto-detect spike / S1 sequences
  python extract_s1_sequences.py \\
      --fasta 1624324292.fas.1 \\
      --out   s1_candidates.fasta

  # Strict — only sequences with "S1" explicitly in header
  python extract_s1_sequences.py \\
      --fasta  1624324292.fas.1 \\
      --out    s1_candidates.fasta \\
      --mode   strict

  # With cluster map — also reports cluster sizes
  python extract_s1_sequences.py \\
      --fasta   1624324292.fas.1 \\
      --clstr   1624324292.fas.1.clstr \\
      --out     s1_candidates.fasta

  # Trim output to S1 domain only (residues 1-685 of spike)
  python extract_s1_sequences.py \\
      --fasta   1624324292.fas.1 \\
      --out     s1_candidates.fasta \\
      --trim-s1

  # Preview only — no file written
  python extract_s1_sequences.py \\
      --fasta 1624324292.fas.1 \\
      --dry-run

Dependencies
------------
  Standard library only — no conda/pip required.
  Optional: biopython (pip install biopython) for richer FASTA parsing.
"""

import argparse
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# S1 / Spike keyword definitions
# ---------------------------------------------------------------------------

# BROAD mode  — catches spike + related surface glycoproteins
BROAD_KEYWORDS = [
    r"spike",
    r"surface glycoprotein",
    r"s protein",
    r"\bS1\b",
    r"receptor.binding domain",
    r"\bRBD\b",
    r"fusion peptide",
    r"heptad repeat",
    r"SARS.CoV",
    r"coronavirus.*spike",
    r"spike.*coronavirus",
    r"2019.nCoV",
    r"COVID",
]

# STRICT mode — only unambiguous S1 annotations
STRICT_KEYWORDS = [
    r"\bS1\b",
    r"spike protein.*S1",
    r"S1 subunit",
    r"receptor.binding domain",
    r"\bRBD\b",
]

# Sequences to EXCLUDE (e.g. nucleocapsid, envelope that share SARS label)
EXCLUDE_KEYWORDS = [
    r"nucleocapsid",
    r"\bN protein\b",
    r"\bE protein\b",
    r"envelope protein",
    r"membrane protein",
    r"\bM protein\b",
    r"ORF[0-9]",
    r"hypothetical",
    r"non-structural",
    r"nsp[0-9]",
    r"replicase",
    r"helicase",
    r"protease",
]

# S1 domain boundaries (approximate, UniProt P0DTC2 numbering)
S1_START = 1      # 1-indexed residue
S1_END   = 685    # last residue of S1 before S2 cleavage site


# ---------------------------------------------------------------------------
# FASTA parser  (no biopython required)
# ---------------------------------------------------------------------------

def parse_fasta(path: Path):
    """
    Yield (header, sequence) tuples from a FASTA file.
    Header does NOT include the leading '>'.
    """
    header, seq_parts = None, []
    with open(path) as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(seq_parts)
                header = line[1:]
                seq_parts = []
            elif line:
                seq_parts.append(line)
    if header is not None:
        yield header, "".join(seq_parts)


def write_fasta(records: list, path: Path, line_width: int = 60):
    """Write a list of (header, sequence) tuples to a FASTA file."""
    with open(path, "w") as fh:
        for header, seq in records:
            fh.write(f">{header}\n")
            for i in range(0, len(seq), line_width):
                fh.write(seq[i : i + line_width] + "\n")


# ---------------------------------------------------------------------------
# CD-HIT cluster file parser
# ---------------------------------------------------------------------------

def parse_clstr(path: Path) -> dict:
    """
    Parse a .clstr file and return a dict:
        { representative_id: {"size": int, "members": [str]} }

    .clstr format example:
        >Cluster 0
        0   123aa, >seq_A... *         ← representative (*)
        1   119aa, >seq_B... at +/95%
    """
    clusters = {}
    current_rep = None
    current_members = []
    current_size = 0

    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(">Cluster"):
                # Save previous cluster
                if current_rep:
                    clusters[current_rep] = {
                        "size": current_size,
                        "members": current_members,
                    }
                current_rep = None
                current_members = []
                current_size = 0
            elif line:
                current_size += 1
                # Extract sequence id (between '>' and '...')
                m = re.search(r">([^.]+)\.\.\.", line)
                if m:
                    seq_id = m.group(1)
                    current_members.append(seq_id)
                    if line.endswith("*"):       # representative marker
                        current_rep = seq_id

    # Don't forget the last cluster
    if current_rep:
        clusters[current_rep] = {"size": current_size, "members": current_members}

    return clusters


# ---------------------------------------------------------------------------
# Filtering logic
# ---------------------------------------------------------------------------

def build_pattern(keywords: list) -> re.Pattern:
    combined = "|".join(f"(?:{kw})" for kw in keywords)
    return re.compile(combined, re.IGNORECASE)


def classify_record(header: str, mode: str) -> bool:
    """
    Return True if a FASTA record header matches spike/S1 criteria.
    mode: "broad" | "strict"
    """
    kws    = BROAD_KEYWORDS if mode == "broad" else STRICT_KEYWORDS
    inc_re = build_pattern(kws)
    exc_re = build_pattern(EXCLUDE_KEYWORDS)

    if exc_re.search(header):
        return False
    return bool(inc_re.search(header))


# ---------------------------------------------------------------------------
# S1 domain trimmer
# ---------------------------------------------------------------------------

def trim_to_s1(seq: str, start: int = S1_START, end: int = S1_END) -> str:
    """
    Trim a full-length spike sequence to the S1 domain (residues start..end).
    Uses 1-based indexing consistent with UniProt / literature.
    If the sequence is shorter than `end`, returns the full sequence.
    """
    s = start - 1            # convert to 0-based
    e = min(end, len(seq))
    return seq[s:e]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def make_report(
    total_input: int,
    hits: list,
    cluster_info: dict,
    mode: str,
    trim: bool,
    out_path: Path,
) -> str:
    lines = [
        "=" * 60,
        "  S1 Sequence Extraction Report",
        "=" * 60,
        f"  Input sequences     : {total_input}",
        f"  S1 candidates found : {len(hits)}",
        f"  Filter mode         : {mode}",
        f"  S1 domain trim      : {'yes (residues 1–685)' if trim else 'no (full spike)'}",
        f"  Output file         : {out_path}",
        "-" * 60,
    ]

    if hits:
        len_list = [len(seq) for _, seq in hits]
        lines += [
            f"  Sequence length — min : {min(len_list)} aa",
            f"  Sequence length — max : {max(len_list)} aa",
            f"  Sequence length — avg : {sum(len_list)//len(len_list)} aa",
            "-" * 60,
        ]

    if cluster_info:
        matched_ids = {h.split()[0] for h, _ in hits}
        lines.append("  Cluster sizes for matched sequences:")
        for seq_id in sorted(matched_ids):
            info = cluster_info.get(seq_id)
            if info:
                lines.append(f"    {seq_id:<30}  cluster size = {info['size']}")
        lines.append("-" * 60)

    lines += [
        "  Headers of extracted sequences:",
        "",
    ]
    for header, seq in hits:
        lines.append(f"    [{len(seq)} aa]  {header[:100]}")

    lines += ["", "=" * 60]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract SARS-CoV-2 S1 sequences from a CD-HIT FASTA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--fasta",    required=True, help="CD-HIT representative FASTA (*.fas.1)")
    parser.add_argument("--out",      required=True, help="Output FASTA path")
    parser.add_argument("--clstr",    default=None,  help="Optional: CD-HIT .clstr file for cluster sizes")
    parser.add_argument("--mode",     default="broad", choices=["broad", "strict"],
                        help="Keyword filter stringency (default: broad)")
    parser.add_argument("--trim-s1",  action="store_true",
                        help="Trim sequences to S1 domain only (residues 1–685)")
    parser.add_argument("--min-len",  type=int, default=8,
                        help="Minimum sequence length to keep (default: 8 aa)")
    parser.add_argument("--max-len",  type=int, default=None,
                        help="Maximum sequence length to keep (optional)")
    parser.add_argument("--report",   default=None,
                        help="Path for text report (default: <out>.report.txt)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print summary without writing any files")
    args = parser.parse_args()

    fasta_path = Path(args.fasta)
    out_path   = Path(args.out)
    report_path = Path(args.report) if args.report else out_path.with_suffix(".report.txt")

    # ── Validate input ──────────────────────────────────────────────────────
    if not fasta_path.exists():
        log.error(f"FASTA file not found: {fasta_path}")
        sys.exit(1)

    # ── Parse cluster file (optional) ───────────────────────────────────────
    cluster_info = {}
    if args.clstr:
        clstr_path = Path(args.clstr)
        if clstr_path.exists():
            log.info(f"Parsing cluster file: {clstr_path}")
            cluster_info = parse_clstr(clstr_path)
            log.info(f"  → {len(cluster_info)} clusters loaded")
        else:
            log.warning(f"Cluster file not found: {clstr_path} — skipping")

    # ── Read and filter FASTA ───────────────────────────────────────────────
    log.info(f"Reading FASTA: {fasta_path}")
    all_records = list(parse_fasta(fasta_path))
    log.info(f"  → {len(all_records)} total sequences")

    hits = []
    rejected_exclude = 0
    rejected_nomatch = 0
    rejected_length  = 0

    for header, seq in all_records:
        if not classify_record(header, args.mode):
            # Distinguish between excluded and no-match for reporting
            if build_pattern(EXCLUDE_KEYWORDS).search(header):
                rejected_exclude += 1
            else:
                rejected_nomatch += 1
            continue

        # Apply domain trim if requested
        if args.trim_s1:
            seq = trim_to_s1(seq)

        # Length filter
        if len(seq) < args.min_len:
            rejected_length += 1
            continue
        if args.max_len and len(seq) > args.max_len:
            rejected_length += 1
            continue

        hits.append((header, seq))

    log.info(f"  → {len(hits)} S1 candidates matched")
    log.info(f"     Excluded by keyword : {rejected_exclude}")
    log.info(f"     No keyword match    : {rejected_nomatch}")
    log.info(f"     Failed length check : {rejected_length}")

    if not hits:
        log.warning(
            "No sequences matched. Try --mode broad or check your FASTA headers."
        )

    # ── Write outputs ────────────────────────────────────────────────────────
    report_text = make_report(
        total_input  = len(all_records),
        hits         = hits,
        cluster_info = cluster_info,
        mode         = args.mode,
        trim         = args.trim_s1,
        out_path     = out_path,
    )

    print(report_text)

    if args.dry_run:
        log.info("Dry run — no files written.")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_fasta(hits, out_path)
    log.info(f"FASTA written → {out_path}")

    with open(report_path, "w") as fh:
        fh.write(report_text)
    log.info(f"Report written → {report_path}")


if __name__ == "__main__":
    main()
