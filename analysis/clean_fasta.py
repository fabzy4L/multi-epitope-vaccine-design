"""
FASTA cleaner — removes sequences containing non-standard amino acid characters.

IEDB, NetMHCpan, and NetMHCIIpan only accept the 20 standard amino acids.
This script filters out any sequence that contains ambiguous or non-standard
residues (X, B, Z, U, O, *, -) and writes a clean FASTA ready for submission.

Usage:
    python clean_fasta.py <input.fasta> [output.fasta]

    If output is omitted, writes <input>_clean.fasta next to the input file.

Examples:
    python clean_fasta.py ../01_clustering/1624324292.fas.1
    python clean_fasta.py ../01_clustering/1624324292.fas.1 iedb_ready.fasta
"""

import sys
import re
from pathlib import Path

STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")
NONSTANDARD  = set("XBZUO*-")   # ambiguous / special residues that break tools


def parse_fasta(path: Path) -> list[tuple[str, str]]:
    """Return list of (header, sequence) tuples."""
    records = []
    header, seq_parts = None, []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(seq_parts)))
                header = line[1:]
                seq_parts = []
            else:
                seq_parts.append(line.upper())
    if header is not None:
        records.append((header, "".join(seq_parts)))
    return records


def write_fasta(records: list[tuple[str, str]], path: Path, width: int = 60):
    with path.open("w") as fh:
        for header, seq in records:
            fh.write(f">{header}\n")
            for i in range(0, len(seq), width):
                fh.write(seq[i:i + width] + "\n")


def find_bad_chars(seq: str) -> set[str]:
    return set(seq) - STANDARD_AA


def clean(records: list[tuple[str, str]]) -> tuple[list, list]:
    """Return (clean_records, rejected_records).
    Each rejected entry is (header, sequence, bad_chars).
    """
    clean_records, rejected = [], []
    for header, seq in records:
        bad = find_bad_chars(seq)
        if bad:
            rejected.append((header, seq, bad))
        else:
            clean_records.append((header, seq))
    return clean_records, rejected


def print_report(total: int, clean_records: list, rejected: list):
    kept    = len(clean_records)
    removed = len(rejected)
    print(f"\n{'='*55}")
    print(f"  FASTA Cleaning Report")
    print(f"{'='*55}")
    print(f"  Total sequences  : {total}")
    print(f"  Kept (clean)     : {kept}  ({kept/total*100:.1f}%)")
    print(f"  Removed          : {removed}  ({removed/total*100:.1f}%)")

    if rejected:
        # Tally which bad characters appeared
        from collections import Counter
        char_tally: Counter = Counter()
        for _, _, bad in rejected:
            char_tally.update(bad)
        print(f"\n  Bad characters found:")
        for char, count in char_tally.most_common():
            print(f"    '{char}'  in {count} sequence(s)")

        print(f"\n  First 5 rejected sequences:")
        for header, seq, bad in rejected[:5]:
            # find first bad position
            for i, aa in enumerate(seq):
                if aa not in STANDARD_AA:
                    first_pos = i + 1  # 1-indexed
                    first_char = aa
                    break
            preview = seq[:60] + ("..." if len(seq) > 60 else "")
            print(f"    >{header[:60]}")
            print(f"     First bad: '{first_char}' at position {first_pos}")
            print(f"     Sequence : {preview}")
            print()
    print(f"{'='*55}\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    in_path = Path(sys.argv[1]).resolve()
    if not in_path.exists():
        print(f"ERROR: file not found: {in_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2]).resolve()
    else:
        out_path = in_path.with_stem(in_path.stem + "_clean")

    records = parse_fasta(in_path)
    if not records:
        print("ERROR: no sequences found in file.")
        sys.exit(1)

    clean_records, rejected = clean(records)
    print_report(len(records), clean_records, rejected)

    write_fasta(clean_records, out_path)
    print(f"Clean file written to:\n  {out_path}")

    if rejected:
        # Write rejected sequences to a separate log for reference
        log_path = out_path.with_stem(out_path.stem.replace("_clean", "") + "_rejected")
        with log_path.open("w") as fh:
            fh.write("# Sequences removed due to non-standard residues\n")
            fh.write("# Format: header | bad_chars | sequence\n")
            for header, seq, bad in rejected:
                fh.write(f">{header}\n")
                fh.write(f"# bad_chars: {sorted(bad)}\n")
                fh.write(seq + "\n\n")
        print(f"Rejected sequences logged to:\n  {log_path}\n")


if __name__ == "__main__":
    main()
