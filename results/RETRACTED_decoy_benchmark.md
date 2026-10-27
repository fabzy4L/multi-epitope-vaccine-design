# Withdrawn: decoy benchmark outputs (2026-10-27)

These two files are the output of a decoy benchmark that has been withdrawn. They are kept so
the earlier published record stays visible. They are not a selectivity result and are not cited
in the manuscript, the README or METHODOLOGY.md.

| File | What it is |
|---|---|
| `decoy_scores.csv` | Scores for 10 real epitopes and 1,000 decoys from the withdrawn run |
| `selectivity_benchmark.png` | The figure plotting those distributions, annotated KS p = 6.87 × 10⁻²⁴ |

## What was wrong

The decoys were sequence shuffles of the real epitopes, which was correct. Their binding values
were not. The script assigned each decoy an IC50 and a percentile rank drawn from
`np.random.uniform` over a non-binder range (IC50 500–50,000 nM, rank 5–50%), while the real
epitopes kept their true NetMHCpan predictions (IC50 4–46 nM, rank 0.01–0.31%).

The scoring function is deterministic in those two inputs:

```
score = (1 / log10(IC50)) × (1 / rank) × population_weight
```

So the two distributions were separated by construction, before any test ran. The KS statistic
describes how the inputs were assigned, not how the scoring function performs. The shuffled
sequences never influenced the score at all: sequence enters only through the cysteine and
human-homology checks, and the homology check was disabled in that script
(`human_proteome_seqs = []`).

## What replaced it

`src/decoy_benchmark.py` was rewritten in two stages. Stage 1 generates composition-matched
shuffles and writes them as FASTA for submission. Stage 2 reads real IEDB predictions for those
decoys and runs the test. It exits with instructions if the predictions file is absent and will
not run on synthetic values.

The IEDB submission for the decoys is outstanding, so no decoy result is currently reported in
the manuscript, the README or METHODOLOGY.md.

## What was unaffected

Every other count was recomputed from the raw IEDB exports by `src/verify_selectivity.py` and
held: 74 strong binders (44 MHC-I, 30 MHC-II), 0.167% of predictions. The prediction total was
corrected from 44,359 to 44,332, the number of parseable rows in the exports.
