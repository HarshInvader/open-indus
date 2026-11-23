"""Pre-prereg feasibility (Fable: 'check the null width before sealing'). Latin only; no Indus outcome computed.
Can a counted-vs-frozen object contrast be seen with Indus-sized samples? Run: .venv/bin/python -I experiments/numerals_by_object/feasibility.py
"""
import glob, json, sys, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/count_index_rehearsal")); sys.path.insert(0, str(ROOT / "corpus"))
import cir

def load():
    ty = {}
    for f in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        for it in json.load(open(f))["items"]:
            ty[it["id"]] = (it.get("type_of_inscription") or "?").rstrip("?")
    texts = cir.greedy_fast(cir.edh_texts())
    pairs = cir.edh_pairs(texts)
    for p in pairs: p["type"] = ty.get(p["text"], "?")
    return pairs

def index_table(pairs):
    vals = defaultdict(list)
    for p in pairs: vals[p["head"]].append(p["value"])
    return {h: cir.rarefied_distinct(v) for h, v in vals.items() if len(v) >= cir.NMIN}

def stat(tok_idx, lab):
    a = tok_idx[lab == 1]; b = tok_idx[lab == 0]
    return a.mean() - b.mean()

if __name__ == "__main__":
    pairs = load()
    print(Counter(p["type"] for p in pairs).most_common(10))
    A = [p for p in pairs if p["type"] in ("epitaph",)]                       # counted-rich (ages)
    B = [p for p in pairs if p["type"] in ("honorific inscription", "building/dedicatory inscription", "military diploma")]  # frozen-rich
    print("A", len(A), "B", len(B))
    rng = np.random.default_rng(1)
    for nA, nB in ((30, 136), (23, 494), (53, 630)):
        passes = 0; D = 30
        for d in range(D):
            # sample by text (whole texts) until token counts reached
            def take(P, n):
                byt = defaultdict(list)
                for p in P: byt[p["text"]].append(p)
                ks = list(byt); rng.shuffle(ks); out = []
                for k in ks:
                    out += byt[k]
                    if len(out) >= n: break
                return out
            a, b = take(A, nA), take(B, nB)
            idx = index_table(a + b)
            tok = [(idx[p["head"]], 1, p["text"]) for p in a if p["head"] in idx] + [(idx[p["head"]], 0, p["text"]) for p in b if p["head"] in idx]
            if not tok or len({l for _, l, _ in tok}) < 2: continue
            x = np.array([t[0] for t in tok]); lab = np.array([t[1] for t in tok]); txt = np.array([t[2] for t in tok])
            obs = stat(x, lab); ut = list(dict.fromkeys(txt)); tl = {t: l for _, l, t in tok}
            null = []
            for _ in range(300):
                perm = dict(zip(ut, rng.permutation([tl[t] for t in ut])))
                null.append(stat(x, np.array([perm[t] for t in txt])))
            p = (1 + sum(n >= obs for n in null)) / 301
            passes += p <= 0.01
        print(nA, nB, "power", passes / D, "kept tokens last draw", len(tok), "heads", len(idx))
