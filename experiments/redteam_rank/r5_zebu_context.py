"""Step 5: zebu seals at Mohenjo-daro by excavator (MIC=Marshall, FEM=Mackay), area and depth (M77 metadata; no sizes)."""
import json, collections as C
from pathlib import Path
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[2]
L = [json.loads(l) for l in open(ROOT / "data/m77_lines.jsonl")]
seals = {}
for l in L:
    if l["object_type"] == "seal" and l["site"].startswith("Mohenjo"):
        seals[l["text_no"]] = l


def cls(d):
    d = d.lower()
    if "humped" in d or "zebu" in d:
        return "zebu"
    if "unicorn" in d:
        return "unicorn"
    return "other"


def src(n):
    return "MIC" if n < 2000 else ("FEM" if n < 3000 else "other")


def lvl(l):
    try:
        return float(l["level"])
    except Exception:
        return None


out = {}
for c in ["zebu", "unicorn"]:
    X = [l for l in seals.values() if cls(l["fs_description"]) == c]
    lv = [lvl(l) for l in X if lvl(l) is not None]
    out[c] = dict(n=len(X), source=dict(C.Counter(src(l["text_no"]) for l in X)),
                  top_locus=C.Counter((l["locus"] or "-").split()[0] for l in X).most_common(3),
                  deep_share=sum(v <= -10 for v in lv) / len(lv), n_level=len(lv))
    print(c, out[c])
z, u = out["zebu"], out["unicorn"]
zd = round(z["deep_share"] * z["n_level"]); ud = round(u["deep_share"] * u["n_level"])
o, p = fisher_exact([[zd, z["n_level"] - zd], [ud, u["n_level"] - ud]])
print(f"deep (<=-10 ft) zebu {zd}/{z['n_level']} vs unicorn {ud}/{u['n_level']}: OR {o:.2f} p={p:.3f}")
out["deep_fisher"] = dict(odds=o, p=p)
json.dump(out, open(ROOT / "experiments/redteam_rank/r5.json", "w"), indent=1)
