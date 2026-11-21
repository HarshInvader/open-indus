"""Exploratory, counts only: the most site-skewed tokens in each cleaned reference pool and in Indus.
Score = smoothed log-odds; prints the top tokens per site with counts. No classifier."""
import sys, math
from collections import Counter
sys.path.insert(0, "experiments/redteam_uniformity")
import rt
def top(T, a, b, k=12):
    ca, cb = Counter(), Counter()
    for t in T:
        (ca if t["site"] == a else cb).update(set(w for l in t["lines"] for w in l))
    na = sum(t["site"] == a for t in T); nb = len(T) - na
    sc = {w: math.log((ca[w] + .5) / (na + 1)) - math.log((cb[w] + .5) / (nb + 1)) for w in set(ca) | set(cb) if ca[w] + cb[w] >= 8}
    s = sorted(sc, key=sc.get)
    return [(w, ca[w], cb[w]) for w in s[::-1][:k]], [(w, ca[w], cb[w]) for w in s[:k]], na, nb
for pair, (a, b, _) in rt.REF.items():
    T = rt.ref_pool(pair, "whole")
    A, B, na, nb = top(T, a, b)
    print(f"\n{pair}  {a} n={na} / {b} n={nb}  (token, texts at {a}, texts at {b})\n  {a}: {A}\n  {b}: {B}")
T = rt.ub.clean([t for t in rt.icit_seal_pool() if t["site"] in (rt.MD, rt.HA)])
A, B, na, nb = top(T, rt.MD, rt.HA)
print(f"\nIndus MD n={na} / Harappa n={nb}\n  MD: {A}\n  H: {B}")
L = rt.ref_pool("lat_britannia_germania", "whole")
mil = [t for t in L if any(rt.MIL.match(w) or rt.ROMAN.match(w) for l in t["lines"] for w in l)]
from collections import Counter as C
print("\nLatin texts with military/numeral words:", C(t["site"] for t in mil), "of", C(t["site"] for t in L))
U = rt.ref_pool("ur3_umma_girsu", "whole")
print("Ur III texts with a {ki} token:", C(t["site"] for t in U if any("{ki}" in w for l in t["lines"] for w in l)), "of", C(t["site"] for t in U))
print("Ur III distinct first lines (owners):", {s: len(set(" ".join(t["lines"][0]) for t in U if t["site"] == s)) for s in ("Umma", "Girsu")})
