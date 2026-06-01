# C-ImmSim Submission Guide — v3.1 Vaccine

**Server:** https://iimcb.genesilico.pl/cimsim/

---

## Sequence to Submit (v3.1, 142 aa)

```
MKKLLFAIPLVVPFYSHSGGGSAPPHALSGPGPGQTLLALHRSYLTPGDGPGPGINITRFQTLLALHRSKKGPGPGLPFNDGVYFAAYRLFRKSNLKAAYFPNITNLCPFAAYVLYNSASFSTFKGGGSPAPAPGSHHHHHH
```

---

## Submission Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Injections | 3 | Prime-boost-boost schedule |
| Injection days | 1, 28, 56 | Standard 4-week intervals |
| HLA-I allele | A\*03:01 | Top MHC-I allele in construct (RLFRKSNLK, 4.82 nM) |
| HLA-II allele | DRB1\*15:01 | Top MHC-II allele in construct (QTLLALHRSYLTPGD, 9.87 nM) |
| Random seed | 12345 | For reproducibility |

---

## Downloading Results

Download the CSV output file and save as:
`results/immune_simulation/cimsim_results.csv`

Then run: `python src/immune_simulation.py`

---

## Expected Signals

| Metric | Minimum acceptable | Strong response |
|---|---|---|
| Peak IgG titer | > 1,000 AU | > 10,000 AU |
| Peak IFN-γ | Detectable rise | > 3× baseline |
| CD8+ T cell peak | Detectable rise post dose 1 | Strong boost post dose 2/3 |
| IL-12 | Elevated (Th1 polarization) | Sustained across doses |

A Th1-skewed response (IFN-γ, IL-12, CD8+ T cells) is desired for a viral peptide vaccine
targeting intracellular antigen presentation.
