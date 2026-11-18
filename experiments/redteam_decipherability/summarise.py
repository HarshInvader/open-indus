"""Apply the pre-registered verdict rules (docs/prereg/redteam_decipherability.md) to out/runs.jsonl."""
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

D = Path(__file__).parent
rows = [json.loads(l) for l in open(D / "out/runs.jsonl")]
main = [r for r in rows if r.get("model") in ("K0", "K2")]
for r in rows:
    r.setdefault("z", r.get("z_vs_shuffle"))
c4 = [r for r in rows if r.get("z") is not None]
cell = defaultdict(list)
for r in main:
    cell[(r["model"], r["ntok"], r["q"])].append(r)

print("n runs", len(main), "C4 runs", len(c4))
print("\nmodel ntok q | mean blind | mean climb | wrong>true share | gap/tok | n")
for k in sorted(cell):
    rs = cell[k]
    print(k, round(mean(r["blind_acc"] for r in rs), 3), round(mean(r["climb_acc"] for r in rs), 3),
          round(mean(r["wrong_beats_true"] for r in rs), 2), round(mean(r["gap_per_tok"] for r in rs), 4), len(rs))


def m(model, n, q):
    return mean(r["blind_acc"] for r in cell[(model, n, q)])


v = {}
gate = m("K0", 10000, 0.0)
v["gate"] = dict(k0_10k_q0=gate, passes=gate >= 0.70)
c1a, c1b = m("K0", 10000, 0.0), m("K0", 10000, 0.2)
v["C1"] = dict(q0=c1a, q02=c1b, verdict="SURVIVES" if c1a >= 0.70 and c1b >= 0.60 else "WEAKENED")
k2 = {(n, q): m("K2", n, q) for (mod, n, q) in cell if mod == "K2"}
rise = max(k2[(30000, q)] - k2[(2500, q)] for q in (0.0, 0.2))
if max(k2.values()) > 0.50:
    c2 = "FAILS"
elif max(k2.values()) <= 0.35 and rise <= 0.15:
    c2 = "SURVIVES"
else:
    c2 = "WEAKENED"
v["C2"] = dict(cells={f"{n}/{q}": a for (n, q), a in sorted(k2.items())}, max_rise=rise, verdict=c2)
k2r = [r for r in main if r["model"] == "K2"]
k0r = [r for r in main if r["model"] == "K0"]
share = mean(r["wrong_beats_true"] for r in k2r)
by_size = {n: mean(r["wrong_beats_true"] for r in k2r if r["ntok"] == n) for n in sorted({r["ntok"] for r in k2r})}
v["C3"] = dict(share_K2=share, share_K0=mean(r["wrong_beats_true"] for r in k0r), share_K2_by_size=by_size,
               verdict="SURVIVES" if share >= 0.80 else ("WEAKENED" if share > 0.5 else "FAILS"))
if c4:
    zs = [r["z"] for r in c4]
    v["C4"] = dict(z=zs, verdict="SURVIVES" if all(z > 5 for z in zs) else ("WEAKENED" if all(z > 0 for z in zs) else "FAILS"))
print(json.dumps(v, indent=1, default=float))
json.dump(v, open(D / "out/verdicts.json", "w"), indent=1, default=float)
