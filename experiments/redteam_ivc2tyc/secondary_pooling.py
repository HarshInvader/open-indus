"""SECONDARY (post hoc, after the prereg run): is the pooled-TYC advantage a diversity/pooling artefact?
Compare NN-sim of Indus to: TYC pooled, TYC pooled without Ba-Shu, Bronze pooled (PC+PE), and a pool of
PC+PE+old_naxi... Each pool sampled to 280 glyphs. RAW and NORM conditions, 20 resamples."""
import json, random, sys
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import BASE, TYC, OTH, ALL, N, load, redraw, vec, nnsim  # noqa
import os
rng = random.Random(201)
glyphs = {s: [g for g in (load(BASE / s / f) for f in sorted(os.listdir(BASE / s)) if f.lower().endswith((".png", ".jpg", ".jpeg"))) if g is not None] for s in ALL}
pools = {"TYC_pooled": TYC, "TYC_no_bashu": [s for s in TYC if s != "ba-shu"], "Bronze_pooled": OTH,
         "naxi_dongba_only": ["naxi_dongba"], "proto_cuneiform_only": ["proto_cuneiform"], "ba-shu_only": ["ba-shu"]}
out = {}
for cond in ["RAW", "NORM"]:
    acc = {p: [] for p in pools}; D = []
    for rep in range(20):
        smp = {}
        for p, ss in pools.items():
            allg = [g for s in ss for g in glyphs[s]]
            smp[p] = rng.sample(allg, min(N, len(allg)))
        ind = rng.sample(glyphs["indus"], N)
        imgs = [vec(redraw(g, 3) if cond == "NORM" else g) for g in ind]
        idx = {"indus": np.arange(N)}
        for p in pools:
            start = len(imgs)
            imgs += [vec(redraw(g, 3) if cond == "NORM" else g) for g in smp[p]]
            idx[p] = np.arange(start, len(imgs))
        E = PCA(50, random_state=rep).fit_transform(np.array(imgs))
        s = {p: nnsim(E, idx["indus"], idx[p])[0] for p in pools}
        for p in pools: acc[p].append(s[p])
        D.append(s["TYC_no_bashu"] - s["Bronze_pooled"])
    out[cond] = {"nn_mean": {p: float(np.mean(v)) for p, v in acc.items()},
                 "D_tyc_no_bashu_minus_bronze_pooled": {"mean": float(np.mean(D)), "lo": float(np.percentile(D, 2.5)), "hi": float(np.percentile(D, 97.5))}}
    print(cond, json.dumps(out[cond]), flush=True)
json.dump(out, open(Path(__file__).resolve().parent / "secondary_pooling.json", "w"), indent=1)
