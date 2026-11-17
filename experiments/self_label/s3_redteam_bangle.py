"""Exploratory red-team of the single confirmed pair (bangle x M373 = Wells W790). NOT pre-registered.
Checks: (1) length-matched control: bangle texts are 1-2 signs; is W790 just a short-text sign?
(2) which other classes is W790 enriched on, i.e. is it a general 'small object' sign?
(3) power: how many bangle texts carry ANY single sign this often?
Run: .venv/bin/python -I experiments/self_label/s3_redteam_bangle.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/self_label"))
from s2_test import W2M, icit_cls  # noqa: E402
from corpus.load import icit_texts  # noqa: E402

rng = np.random.default_rng(7)
ic, seen = [], set()
for t in icit_texts():
    ws = [s for s in t["seq"] if s.startswith("W")]
    if not ws:
        continue
    cls = icit_cls(t["type"])
    key = (" ".join(t["seq"]), cls, t["site"])
    if key in seen:
        continue
    seen.add(key)
    ms = set()
    for w in ws:
        ms.update(W2M.get(w, [w]))
    ic.append({"site": t["site"], "cls": cls, "signs": ms, "nw": len(ws), "material": t["material"]})
ln = lambda t: t["nw"]  # length in raw Wells signs (one W can map to several M)
out = {}

# 1. length-matched control: compare bangles to non-bangle texts with the same number of distinct signs
bang = [t for t in ic if t["cls"] == "bangle"]
others = [t for t in ic if t["cls"] != "bangle"]
has = lambda t: "M373" in t["signs"]
obs = sum(map(has, bang))
by_len = {}
for t in others:
    by_len.setdefault(min(ln(t), 5), []).append(t)
null = []
for _ in range(10000):
    c = 0
    for t in bang:
        pool = by_len[min(ln(t), 5)]
        c += has(pool[rng.integers(len(pool))])
    null.append(c)
null = np.array(null)
out["length_matched"] = {"obs": obs, "n_bangle": len(bang), "exp": float(null.mean()),
                         "p": float((1 + (null >= obs).sum()) / 10001)}
# same, also matched on site
by_ls = {}
for t in others:
    by_ls.setdefault((t["site"], min(ln(t), 5)), []).append(t)
null = []
for _ in range(10000):
    c = 0
    for t in bang:
        pool = by_ls.get((t["site"], min(ln(t), 5))) or by_len[min(ln(t), 5)]
        c += has(pool[rng.integers(len(pool))])
    null.append(c)
null = np.array(null)
out["length_site_matched"] = {"obs": obs, "exp": float(null.mean()), "p": float((1 + (null >= obs).sum()) / 10001)}

# 2. W790 rate per class
rate = {}
for c in sorted({t["cls"] for t in ic}):
    xs = [t for t in ic if t["cls"] == c]
    rate[c] = [sum(map(has, xs)), len(xs)]
out["rate_by_class"] = rate
# single-sign texts only
one = Counter((t["cls"], has(t)) for t in ic if ln(t) == 1)
out["one_sign_texts"] = {c: [one[(c, True)], one[(c, True)] + one[(c, False)]] for c in {k for k, _ in one}}

# 3. look-elsewhere: for every pool sign, its bangle enrichment; where does W790 rank?
cnt = Counter(s for t in bang for s in t["signs"])
tot = Counter(s for t in ic for s in t["signs"])
nb, n = len(bang), len(ic)
from scipy.stats import hypergeom
ps = {s: hypergeom.sf(cnt[s] - 1, n, tot[s], nb) for s in cnt}
rank = sorted(ps, key=ps.get)
out["bangle_top_signs"] = [(s, cnt[s], tot[s], float(ps[s])) for s in rank[:6]]
print(json.dumps(out, indent=1))
json.dump(out, open(ROOT / "experiments/self_label/redteam_bangle.json", "w"), indent=1)
