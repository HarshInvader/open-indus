"""Decoy heads for Writer B (prereg meaning_calibration.md 'Uninformed claims'): for each of A's heads, in A's order,
a decoy from the decoy pool (eligible-every-draw heads not used by A), class-matched when possible, else any; no reuse.
Writes claims_input/B_decoys.json (opaque ids only) and claims/decoy_map.json (A head -> decoy token).
Run: .venv/bin/python -I experiments/meaning_calibration/decoys.py
"""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fcore as F  # noqa: E402
from pool import syl  # noqa: E402

A = json.load(open(HERE / "claims/A_claims.json"))
pools = json.load(open(HERE / "claims_input/pools.json"))
opaque = json.load(open(HERE / "claims_input/opaque.json"))
used = {a["head"] for a in A}
avail = [h for h in pools["eligible_every_draw"] if h not in used]
rng = random.Random(20261125 + 999)
dmap = []
for a in A:
    same = [h for h in avail if F.tclass(h) == F.tclass(a["head"])]
    pick = rng.choice(same if same else avail)
    avail.remove(pick)
    dmap.append(dict(A_head=a["head"], decoy=pick, class_matched=bool(same)))
json.dump(dmap, open(HERE / "claims/decoy_map.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict(id=opaque[d["decoy"]], cls=F.tclass(d["decoy"]), syllables=syl(d["decoy"])) for d in dmap],
          open(HERE / "claims_input/B_decoys.json", "w"), indent=1)
print(sum(d["class_matched"] for d in dmap), "of", len(dmap), "class-matched")
