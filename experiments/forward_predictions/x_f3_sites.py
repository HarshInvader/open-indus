"""Exploratory (not gating, after the dry run): F3 rule applied leave-one-site-out to every site with >=10 graffiti."""
import sys, json
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[2])]
from collections import Counter
import fp
I = fp.icit_units()
c = Counter(u["site"] for u in I if u["kind"] == "pot_g")
out = {}
for s, n in c.most_common():
    if n < 10: continue
    r = fp.f3([u for u in I if u["site"] != s], [u for u in I if u["site"] == s], "W")
    out[s] = {k: r[k] for k in ("n_texts", "observed", "expected", "RR", "p_poisson", "gain_bits_per_unit", "verdict")}
    lens = [u["L"] for u in I if u["site"] == s and u["kind"] == "pot_g"]
    out[s]["mean_len"] = round(sum(lens) / len(lens), 2)
json.dump(out, open(Path(__file__).resolve().parent / "x_f3_sites.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
