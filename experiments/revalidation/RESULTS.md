# Revalidation on the leak-free family split (splits_v2)

All four claims the red team ranked defensible survive on held-out texts that have no near-copy in dev (571 texts in 505 families; 0 within one edit of a dev text).

| Claim (fixed in advance) | Clean held-out result | Verdict |
|---|---|---|
| Order beats permutations | true order strictly best in 40.2% of 321 runs vs 5.7% chance | survives |
| Ticked fish take the final slot | 11 of 19 final (58%) vs plain fish 7%; frequency-matched null 0.19, p=0.004 | survives |
| Two-tier six + fish | M109 followed by M59 in 7 of 10 vs base rate 3.1%, binomial p=2.8e-9 | survives (small n) |
| Object-type registers | AUC copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67; all above the 95th percentile of label permutations (0.55-0.61) | survives |

Script: `revalidate.py`. Bigram add-0.1 trained on dev; logistic regression on a sign set trained on dev.
