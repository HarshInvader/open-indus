"""Exploratory: does P3 HAR~HAR_VATS survive after removing texts (sign sequences) attested in both excavations?"""
import h1_main as H
from hl_lib import *
H.rng = np.random.default_rng(13)
D = build_icit(); V = build_m77_depth("Harappa")
key = lambda u: tuple(x for x in u["seq"] if x not in ("|", "#"))
sh = set(map(key, D["HAR"])) & set(map(key, V))
print("texts in both excavations:", len(sh), "of", len(D["HAR"]), len(V))
A = [u for u in D["HAR"] if key(u) not in sh]; B = [u for u in V if key(u) not in sh]
res = H.p3({"HAR": A, "HAR_VATS": B}, [("HAR", "HAR_VATS")], nperm=2000)
print("P3 without shared texts:", res)
json.dump(dict(n_shared_texts=len(sh), res=res), open(OUT / "results_noshared.json", "w"), indent=1, default=float)
