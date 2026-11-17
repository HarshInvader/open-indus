"""Build experiments/structure/sign_table.csv (one row per Mahadevan sign) from q2-q4 outputs. Run after q2-q4."""
import csv
import json
import pickle
from collections import Counter, defaultdict

from common import OUT, ROOT, distinct, is_clean, load_bridge, m77_texts, signs
from q3_positional import profiles

T_all = m77_texts()
T = distinct(T_all)
tok_all = Counter(s for t in T_all for s in signs(t["seq"]))
tok_d = Counter(s for t in T for s in signs(t["seq"]))
ntext = Counter(s for t in T for s in set(signs(t["seq"])))
sites = defaultdict(Counter)
for t in T:
    for s in set(signs(t["seq"])):
        sites[s][t["site"]] += 1
cnt, _, _ = profiles([signs(t["seq"]) for t in T if is_clean(t)])
pos = json.load(open(OUT / "positional.json"))
full = pos["M77_full"]["per_sign"]
icit = pos["ICIT"]["per_sign"]
allo = json.load(open(OUT / "allographs.json"))
vis = allo["merge_map_visual"]
fam = defaultdict(set)
for p in allo["pairs"]:
    if p["verdict"].startswith("variant") or p["verdict"] == "allograph-candidate":
        fam[p["a"]].add(p["b"]); fam[p["b"]].add(p["a"])
lookd = defaultdict(set)
for p in allo["pairs"]:
    if p["verdict"] == "lookalike-distinct" and p["img_sim"] >= 0.9:
        lookd[p["a"]].add(p["b"]); lookd[p["b"]].add(p["a"])
seg = pickle.load(open(OUT / "segments.pkl", "rb"))["full_lex"]
segs_of = defaultdict(list)
for w, c in seg.most_common():
    if len(w) >= 2 and c >= 3:
        for s in set(w):
            segs_of[s].append(("-".join(w), c))
br = load_bridge()
m2w = defaultdict(list)
for w, m in br.items():
    m2w[m].append(w)
ss = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
SHORT = {"M%s" % k for k in ss["short"]}; TALL = {"M%s" % k for k in ss["tall"]}

rows = []
for n in range(1, 418):
    s = f"M{n}"
    c = cnt.get(s)
    tot = float(c.sum()) if c is not None else 0
    prof = [float(x) / tot if tot else "" for x in (c if c is not None else [0, 0, 0, 0])]
    ws = m2w.get(s, [])
    icls = ";".join(sorted({icit[w]["class"] for w in ws if w in icit}))
    rows.append({
        "sign": s,
        "tokens_all_objects": tok_all.get(s, 0),
        "tokens_distinct_texts": tok_d.get(s, 0),
        "distinct_text_count": ntext.get(s, 0),
        "n_initial": int(c[0]) if c is not None else 0, "n_medial": int(c[1]) if c is not None else 0,
        "n_final": int(c[2]) if c is not None else 0, "n_standalone": int(c[3]) if c is not None else 0,
        "p_initial": round(prof[0], 3) if tot else "", "p_medial": round(prof[1], 3) if tot else "",
        "p_final": round(prof[2], 3) if tot else "", "p_standalone": round(prof[3], 3) if tot else "",
        "positional_q_vs_shuffle": round(full[s]["q"], 4) if s in full else "",
        "class": full[s]["class"] if s in full else ("rare(<10 texts)" if ntext.get(s, 0) else "unattested"),
        "stroke_type": "short" if s in SHORT else ("tall" if s in TALL else ""),
        "segment_memberships": "; ".join(f"{w}({c})" for w, c in segs_of.get(s, [])[:6]),
        "probable_allograph_of": vis.get(s, ""),
        "variant_family": ";".join(sorted(fam.get(s, []))),
        "lookalike_but_distinct": ";".join(sorted(lookd.get(s, [])))[:120],
        "wells_codes": ";".join(ws),
        "icit_class": icls,
        "top_sites": ";".join(f"{k}:{v}" for k, v in sites[s].most_common(3)),
    })
with open(OUT / "sign_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(len(rows), "rows;", Counter(r["class"] for r in rows))
