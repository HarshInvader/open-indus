"""DEV-ONLY discovery. Never reads heldout or ICIT compositions."""
import collections, json, sys
sys.path.insert(0, "experiments/numeral_grammar")
from common import *
dev, ho = dev_heldout(version=2)
print("dev texts", len(dev), "sites", collections.Counter(t["site"] for t in dev).most_common(8))
G = []
for t in dev:
    for g in groups_from_runs(t["seq"], M_NUM):
        g["site"] = t["site"]; g["obj"] = t["object_type"]; g["text"] = " ".join(t["seq"]); G.append(g)
L = collections.Counter(len(g["group"]) for g in G)
print("group lengths", L)
multi = [g for g in G if len(g["group"]) > 1]
kc = collections.Counter(key(g["group"]) for g in multi)
for k, n in kc.most_common(): print(f"  {n:3d}  {k}")
print("\nexamples:")
for g in multi: print("  ", key(g["group"]), "|", g["site"], g["obj"], "|", g["text"])
# singletons by class
sc = collections.Counter((g["group"][0][1], g["group"][0][2]) for g in G if len(g["group"]) == 1)
print("\nsingletons", sorted(sc.items()))
# what follows / precedes 12
for g in G:
    if any(v == 12 for _, c, v in g["group"]):
        print("12:", key(g["group"]), "prev", g["prev"], "next", g["next"], "|", g["text"])
