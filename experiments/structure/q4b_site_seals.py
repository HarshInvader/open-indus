"""Q4b. Segment-inventory stability MD vs Harappa restricted to SEALS (controls object-type mix)."""
from collections import defaultdict
from common import distinct, m77_texts, runs, save_json
from q4_segment import site_stability

T = distinct(m77_texts())
by = defaultdict(list)
for t in T:
    if t["object_type"] == "seal":
        by[t["site"]] += runs(t["seq"])
r = site_stability(by, reps=10)
r["n_runs"] = {k: len(by[k]) for k in ("Mohenjodaro", "Harappa")}
save_json("q4b_site_stability_seals", r)
print({k: v for k, v in r.items() if k not in ("shared", "MD_only", "HA_only")})
print(r["shared"])
