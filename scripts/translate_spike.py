
import textwrap

def translate(dna):
    codon_table = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
        'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
    }
    protein = ""
    for i in range(0, len(dna) - 2, 3):
        codon = dna[i:i+3].upper()
        protein += codon_table.get(codon, 'X')
    return protein

def main():
    genome_path = 'data/genomic/NC_045512v2.fa'
    with open(genome_path, 'r') as f:
        lines = f.readlines()
        # Skip header and join sequence lines
        dna_sequence = "".join([line.strip() for line in lines if not line.startswith(">")])

    # Spike gene (S) coordinates from GTF: 21563 to 25384 (1-indexed)
    # 0-indexed: 21562 to 25384
    spike_dna = dna_sequence[21562:25384]
    
    spike_protein = translate(spike_dna)
    
    # Remove stop codon at the end if present
    if spike_protein.endswith('_'):
        spike_protein = spike_protein[:-1]
        
    output_path = 'analysis/02_epitope_prediction/sars_cov2_spike_from_genome.fasta'
    with open(output_path, 'w') as f:
        f.write(">SARS-CoV-2_Spike_Protein|Translated_from_NC_045512.2\n")
        f.write("\n".join(textwrap.wrap(spike_protein, 60)) + "\n")
    
    print(f"Extracted and translated Spike protein to {output_path}")
    print(f"Length: {len(spike_protein)} amino acids")

if __name__ == "__main__":
    main()
