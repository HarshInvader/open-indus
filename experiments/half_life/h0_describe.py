"""Descriptive only: dataset sizes, object-type mix, role coverage. No slot comparison computed here."""
from hl_lib import *
R = lexicon_roles()
D = build_icit()
D["HAR_VATS"] = build_m77_depth("Harappa")
D["MD_M77"] = build_m77_depth("Mohenjodaro")
for k, U in D.items():
    c = Counter((u["period"], u["ot"]) for u in U)
    per = Counter(u["period"] for u in U)
    toks = Counter(x for u in U for x in u["signs"])
    cls = Counter(R.get(x, (None, "UNMAPPED"))[1] for u in U for x in u["signs"])
    tot = sum(cls.values())
    print(f"{k}: units {len(U)} per period {sorted(per.items())}")
    print("   period x type", sorted(c.items()))
    print("   sign types", len(toks), " class share of sign-in-text tokens", {a: round(b / tot, 3) for a, b in cls.most_common()})
