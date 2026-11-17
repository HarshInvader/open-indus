"""L5. Consistency check: where do the candidate copper 'picture signs' occur outside the copper slot?

Candidates: M184 (quadruped; rhino slot), M346 (frontal horned head; goat-antelope slot), M362/M363/M364
(horned U; horned archer and twirl-horned goat-antelope slots), M355 (horned U with wheel; hare slot),
M183 (quadruped, inside the hare legend). Wells equivalents for ICIT. For each non-copper occurrence:
object, picture, position. Test: are they initial (opener-like) more than 1/length predicts?
Poisson-binomial exact p; M77 only (ICIT overlaps M77 objects) and ICIT-only as a check.
"""
from common import *

M = {"M355", "M362", "M363", "M364", "M183", "M184", "M346"}
W = {"W777", "W780", "W781", "W782", "W753", "W341", "W343", "W321", "W749"}


def poisbin_sf(k, ps):
    dist = np.zeros(len(ps) + 1); dist[0] = 1
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p; dist[0] *= (1 - p)
    return float(dist[k:].sum())


def main():
    R = {}
    occ = {"M77": [], "ICIT": []}
    for t in m77_texts():
        if t["object_type"] == "copper tablet": continue
        for r in runs(t["seq"]) if "|" not in t["seq"] else [signs(x.split()) for x in " ".join(t["seq"]).split("|")]:
            for i, s in enumerate(r):
                if s in M: occ["M77"].append(dict(id=t["text_no"], sign=s, pos=i, n=len(r), obj=t["object_type"], fs=t["fs80"]))
    for t in icit_texts():
        if t["type"] == "TAB:C": continue
        r = signs(t["seq"])
        for i, s in enumerate(r):
            if s in W: occ["ICIT"].append(dict(id=t["id"], sign=s, pos=i, n=len(r), obj=t["type"], fs=t["symbol"]))
    for src, o in occ.items():
        print(f"{src}: {len(o)} non-copper occurrences")
        for x in o: print("   ", x)
        ns = [x for x in o if x["n"] > 1]
        k = sum(x["pos"] == 0 for x in ns); ps = [1 / x["n"] for x in ns]
        p = poisbin_sf(k, ps)
        print(f"   initial in {k}/{len(ns)} multi-sign lines; expected {sum(ps):.2f}; p={p:.3f}")
        R[src] = dict(occurrences=o, initial=k, n=len(ns), expected=sum(ps), p=p)
    save_json("l5_other_contexts", R)


if __name__ == "__main__":
    main()
