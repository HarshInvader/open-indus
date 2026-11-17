"""DEVIATION from the hashed m6_confirm.py (logged in RESULTS.md): its 'ICIT sites absent from M77'
filter compared raw site names ('Mohenjodaro' vs 'Mohenjo-daro') and so kept 1,400 texts from
M77 sites. This reruns that set with the project's standard normalisation (novel_methods/common.py:
lowercase, strip '-' and spaces). Nothing else changes."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from common import *  # noqa
import m6_confirm as m6

norm = lambda s: s.lower().replace("-", "").replace(" ", "")
m77 = {norm(s) for _, _, s in m77_corpus("all")}
corpus = [c for c in icit_corpus(False) if norm(c[2]) not in m77]
print("texts", len(corpus), "sites", len({c[2] for c in corpus}))
r = m6.run_set("icitnew", corpus, load_pairs(HERE / "w_decomp.csv"))
json.dump(r, open(HERE / "confirm_newsites_fixed.json", "w"), indent=1, default=float)
for m, v in r["primary"].items():
    print("PRIMARY", m, v)
for m, rec in r["families"].items():
    if rec.get("tested"):
        print(f"  {m:18s} k={rec['k']:2d} " + "  ".join(f"{f}: z={rec[f]['z']:+.1f} T={rec[f]['T']:+.1f} {rec[f]['up']}up/{rec[f]['down']}dn p2={rec[f]['p_two']:.3f}" for f in m6.FEAT_SETS) + f"  power(+0.2/+0.5)={rec['power_final_+0.2']:.2f}/{rec['power_final_+0.5']:.2f}")
    else:
        print(f"  {m:18s} k={rec['k']:2d} not tested", rec.get("pairs", [])[:4])
print("paradigm q<0.1:", [x for x in r["paradigm_family"] if x["q"] < 0.1])
