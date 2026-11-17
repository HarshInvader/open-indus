"""Run the same decipherment search on the REAL Indus corpus (distinct M77 texts, break-free runs)
with every candidate LM, versus frequency-matched shuffles. Output: out/indus_run.json.
The gains are placed against the planted-corpus null in analyze.py."""
import sys, json, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1]))
from corpus.load import m77_texts, distinct, runs
import langdata as LD
from decipher import LM, Corpus, anneal, shuffle_corpus

texts = distinct(m77_texts())
seqs_s = [r for t in texts for r in runs(t["seq"])]
signs = sorted({s for q in seqs_s for s in q})
sid = {s: i for i, s in enumerate(signs)}
seqs = [[sid[s] for s in q] for q in seqs_s]
corp = Corpus(seqs)
print("Indus: texts", len(texts), "runs", len(seqs), "tokens", corp.ntok, "signs", corp.S)

L = LD.load()
santali = [[LD.norm_ascii_indic(w)] for w in LD._lines(LD.SRC / "derived/lex_santali.txt")]
bank = {f"{l}:K1": L[l]["K1"] for l in ["san", "tam", "sux", "lat", "fin"]}
bank.update({f"{l}:K2": L[l]["K2"] for l in ["san", "tam", "lat", "fin"]})
bank["pdr:roots"] = L["_pdr"]["K1"]
bank["santali:lex"] = [t for t in santali if t[0]]
rng = np.random.default_rng(2026)
shufs = [Corpus(shuffle_corpus(seqs, rng), S=corp.S) for _ in range(4)]
out = dict(ntok=corp.ntok, S=corp.S, ntexts=len(texts), runs=len(seqs), lms={})
for q in [0.2, 0.4]:
    for name, tx in bank.items():
        lm = LM(tx, q, True, name=name)
        key, sc = anneal(corp, lm, rng)
        sh = [anneal(s, lm, rng, sweeps=100, restarts=2)[1] for s in shufs]
        g = (sc - np.mean(sh)) / corp.ntok
        z = (sc - np.mean(sh)) / (np.std(sh, ddof=1) + 1e-9)
        nlogo = int((key == 101).sum())
        out["lms"][f"{name}@q{q}"] = dict(best=sc, shuf=sh, gain=g, z=z, n_logo_signs=nlogo,
                                          top_values={signs[a]: (LD.VALUES[key[a]] if key[a] < 101 else "LOGO")
                                                      for a in np.argsort(-corp.c)[:15]})
        print(f"{name:12s} q={q} gain/token={g:.3f} z={z:.0f} logo-signs={nlogo}", flush=True)
json.dump(out, open(HERE / "out/indus_run.json", "w"), indent=1, default=float)
