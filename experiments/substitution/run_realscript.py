"""Real-script check: does the X <-> YZ miner find genuine logogram <-> syllabic
alternations in a real logo-syllabic SEAL-LEGEND corpus cut to Indus genre?

Data: CDLI Ur III seal legends (sources/paragorth_Indus-/data/codelib/ur3_legends.jsonl,
read as data only; sign-level split as in experiments/language_vs_code/lvc_corpora.py).
Sumerian/Akkadian legends mix logograms (puzur4, lugal, dumu) and syllabic spellings,
so the true answer is partly known from the transliteration itself:
an equation X = Y is "phonetic" when the reading of X equals the concatenated readings
of Y after removing index digits, determinative markers and doubled vowels
(e.g. puzur4 = pu zur8, or ur = u ur). Also run on DAMOS Linear B lines (descriptive).
Usage: .venv/bin/python experiments/substitution/run_realscript.py [nperm]
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import analyse, save_results  # noqa: E402

SRC = ROOT / "sources/paragorth_Indus-/data/codelib"


def jl(name):
    return [json.loads(l)["seq"] for l in open(SRC / name)]


def ur3():
    out = set()
    for t in jl("ur3_legends.jsonl"):
        s = []
        for w in t:
            w = w.replace("_", "")
            w = re.sub(r"\{([^}]*)\}", r"-\1-", w)
            s += [x for x in w.split("-") if x]
        if s:
            out.add(tuple(s))
    return sorted(out)


def linb():
    out = set()
    for t in jl("linear_b.jsonl"):
        s = []
        for w in t:
            s += [x for x in w.split("-") if x and x != "."]
        if s:
            out.add(tuple(s))
    return sorted(out)


def norm(r):
    r = re.sub(r"[0-9₀-₉x]", "", r.lower())
    r = r.replace("sz", "š").replace("s,", "ṣ").replace("t,", "ṭ")
    return r


def phon(x, y):
    a = norm(x)
    parts = [norm(s) for s in y]
    if not a or not all(parts):
        return False
    b = parts[0]
    for s in parts[1:]:
        # CV-VC spelling: pu-zu-ur -> puzur (shared vowel written twice)
        b = b + (s[1:] if b and s and b[-1] == s[0] and s[0] in "aeiu" else s)
    return a == b


def sample(T, n, seed, maxlen=8):
    rng = np.random.default_rng(seed)
    pool = [t for t in T if 2 <= len(t) <= maxlen]
    idx = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
    return [pool[i] for i in sorted(idx)]


if __name__ == "__main__":
    nperm = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    U = ur3()
    res = {"ur3": [], "linb": []}
    runs = [("full", U)] + [("n2300_s%d" % s, sample(U, 2300, s)) for s in range(5)]
    for name, T in runs:
        out, items, ev, units, eqs = analyse(T, nperm=nperm, seed=0, tier="L")
        sig = [r for r in items if r["q"] < 0.05]
        ph_sig = [r for r in sig if phon(r["X"], r["Y"].split())]
        ph_all = [(x, y, k) for (x, y), k in eqs.items() if phon(x, y)]
        ph_rec = [z for z in ph_all if z[2] >= 2]
        d = dict(sample=name, n_texts=len(T), mean_len=float(np.mean([len(t) for t in T])),
                 n_sig=len(sig), phonetic_sig=len(ph_sig), phonetic_any=len(ph_all), phonetic_recurrent=len(ph_rec),
                 G=out["G"], p_G=out["p_G"], S=out["S"], p_S=out["p_S"],
                 top=[{k: r[k] for k in ("X", "Y", "k", "lam", "q")} | {"phonetic": phon(r["X"], r["Y"].split())}
                      for r in items[:15]],
                 phonetic_examples=[(x, " ".join(y), k) for x, y, k in sorted(ph_all, key=lambda z: -z[2])[:15]])
        res["ur3"].append(d)
        print("UR3", name, {k: v for k, v in d.items() if not isinstance(v, list)})
        print("   phonetic eqs:", d["phonetic_examples"][:10])
        print("   top:", [(r["X"], r["Y"], r["k"], "%.2g" % r["q"], r["phonetic"]) for r in d["top"][:10]])
    LB = linb()
    for name, T in [("n2300_s0", sample(LB, 2300, 0))]:
        out, items, ev, units, eqs = analyse(T, nperm=nperm, seed=0, tier="L")
        d = dict(sample=name, n_texts=len(T), mean_len=float(np.mean([len(t) for t in T])),
                 n_sig=out["n_sig_q05"], G=out["G"], S=out["S"],
                 top=[{k: r[k] for k in ("X", "Y", "k", "lam", "q")} for r in items[:15]])
        res["linb"].append(d)
        print("LINB", name, {k: v for k, v in d.items() if not isinstance(v, list)})
        print("   top:", [(r["X"], r["Y"], r["k"], "%.2g" % r["q"]) for r in d["top"][:10]])
    save_results("realscript", res)
