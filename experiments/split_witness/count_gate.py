"""split_witness step 3: count gate. Implements MINIMUM.txt sections 2, 3, 7 and 9.

Counts eligible splits only. It computes NO cohesion value (no ESR, no percentile, no model)
at any real split. The only per-unit quantities are kind, length, junction index k (needed
to apply the family rule and for nothing else), type, width and the number of Null-2
placements (from widths and lengths of reference texts).

Run: .venv/bin/python -I experiments/split_witness/count_gate.py
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import sw_lib as S  # noqa: E402
from corpus.load import m77_texts, m77_lines, icit_texts  # noqa: E402

N_MIN = 200

# ---- F4: frozen-file check ----
frozen = {}
for line in open(HERE / "MINIMUM.txt"):
    parts = line.split()
    if len(parts) == 2 and len(parts[1]) == 64 and "/" in parts[0]:
        frozen[parts[0]] = parts[1]
    elif len(parts) == 1 and len(parts[0]) > 64 and "/" in parts[0]:
        frozen[parts[0][:-64]] = parts[0][-64:]   # path and hash printed without a space
bad = [p for p, h in frozen.items() if hashlib.sha256(open(ROOT / p, "rb").read()).hexdigest() != h]
if bad:
    sys.exit(f"F4: frozen file changed: {bad}")

I = icit_texts()
icit = {t["id"]: t for t in I}
res = dict(frozen_files_checked=len(frozen))

# ---------------- W: wraps confirmed by both editions ----------------
lines_by = defaultdict(list)
for l in m77_lines():
    lines_by[(l["text_no"], l["side"])].append(l)
m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}

links = defaultdict(set)   # icit id -> {(text_no, side, source)}
for p in json.load(open(ROOT / "experiments/audit_followups/out/b_editor_agreement.json"))["pairs"]:
    if p["norm"] <= 0.8:
        links[p["icit"]].add((p["text_no"], p["side"], "register"))
for k, v in json.load(open(ROOT / "experiments/consensus_corpus/out/seq_links.json")).items():
    tn, sd = json.loads(k)
    if v["norm"] <= 0.5:
        links[v["icit"]].add((tn, sd, "sign"))


def m77_counts(tn, sd):
    t = m77.get((tn, sd))
    if t is None or not t["complete"]:
        return None, "m77 incomplete or missing"
    ls = [l for l in sorted(lines_by[(tn, sd)], key=lambda x: x["line"]) if l["signs"]]
    if len(ls) != 2:
        return None, "m77 not exactly 2 lines"
    if len({l["direction"] for l in ls} - {"single sign"}) > 1:
        return None, "m77 mixed direction"
    return [len(l["signs"]) for l in ls], "ok"


why_w = Counter()
W = []
for t in I:
    s = t["seq"]
    if "|" not in s:
        continue
    why_w["icit records with '|'"] += 1
    if s.count("|") != 1 or s[0] == "|" or s[-1] == "|":
        why_w["x icit not exactly 2 lines"] += 1; continue
    if "#" in s or not t["complete"]:
        why_w["x icit damage or incomplete"] += 1; continue
    i = s.index("|")
    c = [i, len(s) - i - 1]
    if min(c) < 2:
        why_w["x icit a line has < 2 signs"] += 1; continue
    if not links.get(t["id"]):
        why_w["x no M77 link"] += 1; continue
    ok, srcs, reasons, rev = False, set(), set(), False
    for tn, sd, src in links[t["id"]]:
        mc, r = m77_counts(tn, sd)
        if mc is None:
            reasons.add(r); continue
        if mc == c or mc == c[::-1]:
            ok = True; srcs.add(src); rev |= (mc != c)
        else:
            reasons.add("m77 line counts differ")
    if not ok:
        why_w["x " + sorted(reasons)[0]] += 1; continue
    why_w["eligible W (before family rule)"] += 1
    W.append(dict(kind="W", id=t["id"], text=[x for x in s if x != "|"], k=i, type=t["type"],
                  width=S.fnum(t["width_mm"]), site=t["site"],
                  link="register" if "register" in srcs else "sign", reversed_order=rev and c[0] != c[1]))
res["W_funnel"] = dict(why_w)

# ---------------- F: face splits ----------------
by_obj = defaultdict(list)
for t in I:
    by_obj[t["id"].split(".")[0]].append(t)
whole = defaultdict(set)   # joined key -> objects that carry it as one clean single-line text
for t in I:
    s = t["seq"]
    if "|" not in s and "#" not in s and t["complete"] and s:
        whole[S.key(s)].add(t["id"].split(".")[0])
why_f = Counter()
F = []
for obj, recs in by_obj.items():
    if len(recs) < 2:
        continue
    why_f["multi-face objects"] += 1
    for a in recs:
        for b in recs:
            if a is b:
                continue
            why_f["ordered face pairs"] += 1
            if "|" in a["seq"] or "|" in b["seq"] or "#" in a["seq"] or "#" in b["seq"]:
                why_f["x face has '|' or '#'"] += 1; continue
            if not a["seq"] or not b["seq"] or len(a["seq"]) + len(b["seq"]) < 3:
                why_f["x joined < 3 signs"] += 1; continue
            jk = S.key(a["seq"] + b["seq"])
            if not (whole.get(jk, set()) - {obj}):
                why_f["x joined text not found whole elsewhere"] += 1; continue
            why_f["eligible F (before family rule)"] += 1
            F.append(dict(kind="F", id=f"{a['id']}+{b['id']}", text=a["seq"] + b["seq"], k=len(a["seq"]),
                          type=a["type"], width=S.fnum(a["width_mm"]), site=a["site"]))
res["F_funnel"] = dict(why_f)

# ---------------- family rule ----------------
cands = W + F
fam = S.families(extra_keys=[S.key(u["text"]) for u in cands])
for u in cands:
    u["fid"] = fam[S.key(u["text"])]
    u["h"] = hashlib.sha256(f"split_witness:unit:{u['kind']}:{S.key(u['text'])}:{u['k']}".encode()).hexdigest()
best = {}
for u in cands:
    if u["fid"] not in best or u["h"] < best[u["fid"]]["h"]:
        best[u["fid"]] = u
units = sorted(best.values(), key=lambda u: u["h"])
res["candidates_before_family_rule"] = dict(W=len(W), F=len(F),
                                            F_distinct_junctions=len({(S.key(u["text"]), u["k"]) for u in F}),
                                            W_distinct_texts=len({S.key(u["text"]) for u in W}))
res["families_touched"] = dict(W=len({u["fid"] for u in W}), F=len({u["fid"] for u in F}),
                               both=len({u["fid"] for u in W} & {u["fid"] for u in F}))
cnt = Counter(u["kind"] for u in units)
res["eligible_units"] = dict(total=len(units), W=cnt["W"], F=cnt["F"])
res["eligible_W_by_link"] = dict(Counter(u["link"] for u in units if u["kind"] == "W"))
res["eligible_W_reversed_line_order"] = sum(u.get("reversed_order", False) for u in units)
res["eligible_by_type"] = {k: dict(Counter(u["type"] for u in units if u["kind"] == k)) for k in "WF"}
res["eligible_by_site"] = dict(Counter(u["site"] for u in units).most_common())
res["eligible_length_distribution"] = dict(sorted(Counter(len(u["text"]) for u in units).items()))

# ---------------- Null 2 minimum achievable p on eligible units ----------------
# distinct-sequence pool as in power.py
ref = defaultdict(list)
seen = set()
for t in I:
    s = t["seq"]
    if "|" in s or "#" in s or not t["complete"] or len(s) < 2 or S.key(s) in seen:
        continue
    seen.add(S.key(s))
    w = S.fnum(t["width_mm"])
    if w > 5:
        ref[t["type"]].append((w, len(s)))


def n_placements(u):
    if u["width"] <= 5:
        return None
    rows = [L for w, L in ref.get(u["type"], []) if abs(w - u["width"]) <= 2.0]
    if len(rows) < 10:
        return None
    c = float(np.median(rows)); n = len(u["text"])
    return len({int(np.clip(np.floor(c), 1, n - 1)), int(np.clip(np.ceil(c), 1, n - 1))})


kp = [n_placements(u) for u in units]
defined = [x for x in kp if x is not None]
minp2 = float(np.prod([1.0 / x for x in defined])) if defined else 1.0
res["null2"] = dict(units_with_capacity=len(defined), units_with_2_placements=sum(x == 2 for x in defined),
                    minimum_achievable_p=minp2,
                    by_kind={k: dict(defined=sum(1 for u, x in zip(units, kp) if u["kind"] == k and x is not None),
                                     two_placements=sum(1 for u, x in zip(units, kp) if u["kind"] == k and x == 2))
                             for k in "WF"})
res["gate"] = dict(n_min=N_MIN, n_pass=len(units) >= N_MIN, null2_minp_pass=minp2 <= 0.01)
res["gate"]["pass"] = res["gate"]["n_pass"] and res["gate"]["null2_minp_pass"]
json.dump(res, open(HERE / "count_gate.json", "w"), indent=1)
print(json.dumps(res, indent=1))
