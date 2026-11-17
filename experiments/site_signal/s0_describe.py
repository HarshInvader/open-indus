"""Data sizes only (no site-prediction outcomes). Run before the prereg."""
import time
from collections import Counter

import lib

t0 = time.time()
for v in ("strict", "chain", "rep", "all"):
    E = lib.eligible_icit(v)
    c = Counter(t["site"] for t in E)
    print(v, len(E), "families", len(set(t["fam"] for t in E)), c.most_common(10))
    md_h = [t for t in E if t["site"] in ("Mohenjo-daro", "Harappa")]
    print("  bands", Counter((t["site"], lib.band(t)) for t in md_h))
    print("  len>=3", Counter(t["site"] for t in md_h if len(t["signs"]) >= 3))
print("icit seals usable (complete, no break)", len(lib.icit_seals()))
M = lib.eligible_m77()
print("m77 strict", len(M), Counter(t["site"] for t in M).most_common(6))
for lv in ("A1", "A2"):
    g = lib.allograph_groups(lv)
    print(lv, len(g), "groups;", sum(len(x) for x in g.values()), "signs")
print(lib.allograph_groups("A1"))
print("time", round(time.time() - t0, 1))
