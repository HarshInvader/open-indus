"""Control for H2: can a syllabic name corpus look 'whole-word' (many 1-sign cores whose signs also stand
alone) just because a noisy role parse deletes core signs and splits runs?  Delete each sign of Linear B
words / Ur III names with probability p (the deleted sign splits the run) and recompute the whole-word
metrics at N=400 cores.  Run from repo root."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import linear_b_words, ur3_names, synthetic
from metrics import whole_word_metrics
rng = np.random.default_rng(5)

def fragment(cores, p):
    out = []
    for c in cores:
        cur = []
        for s in c:
            if rng.random() < p:
                if cur: out.append(tuple(cur))
                cur = []
            else:
                cur.append(s)
        if cur: out.append(tuple(cur))
    return list(dict.fromkeys(out))

print("Indus held-out reference: len1_share 0.343 [0.33,0.35], standalone_tok 0.803 [0.73,0.85]")
for name, f in [("Linear B words", linear_b_words), ("Ur III names", ur3_names), ("synthetic syllabary", lambda: synthetic("syll", 8000, None, 3))]:
    C = list(f())
    for p in (0.0, 0.2, 0.4, 0.6):
        F = fragment(C, p)
        rows = [whole_word_metrics([F[i] for i in rng.choice(len(F), 400, replace=False)]) for _ in range(100)]
        m = {k: np.mean([r[k] for r in rows]) for k in rows[0]}
        print(f"  {name:20s} p={p:.1f}  len1_share {m['len1_share']:.3f}  standalone_tok {m['standalone_tok']:.3f}  fully_decomposable {m['fully_decomposable']:.3f}")
