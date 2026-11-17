"""Step 1a: count multi-line texts (distinct, copy-free, by object type) in M77 and ICIT,
estimate the union, and check whether '|' behaves like a wrap (line 1 at capacity).

Does NOT compute any boundary score at the observed break positions.
Run: .venv/bin/python experiments/line_breaks/count.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, icit_texts, distinct, dev_heldout  # noqa

OUT = Path(__file__).parent
res = {}

# ---------------- M77 -----------------
T = m77_texts()
L = m77_lines()
lines_by = defaultdict(list)
for l in L:
    lines_by[(l["text_no"], l["side"])].append(l)

multi = [t for t in T if t["n_lines"] > 1]
dmulti = distinct(multi)
res["m77_multiline_objects"] = len(multi)
res["m77_multiline_distinct"] = len(dmulti)
res["m77_multiline_distinct_by_type"] = dict(Counter(t["object_type"] for t in dmulti))


def m77_usable(t):
    """Usable for a 2-line break test: exactly 2 non-empty lines, no break mark,
    flagged complete, >=3 signs (>=2 possible break slots), text directions not mixed."""
    ls = sorted(lines_by[(t["text_no"], t["side"])], key=lambda x: x["line"])
    ls = [l for l in ls if l["signs"]]
    if len(ls) != 2:
        return False, "not exactly 2 non-empty lines"
    if "#" in t["seq"]:
        return False, "break mark"
    if not t["complete"]:
        return False, "incomplete"
    n = sum(len(l["signs"]) for l in ls)
    if n < 3:
        return False, "<3 signs"
    dirs = {l["direction"] for l in ls} - {"single sign"}
    if len(dirs) > 1:
        return False, "mixed direction"
    return True, "ok"


why = Counter()
usable = []
for t in dmulti:
    ok, r = m77_usable(t)
    why[r] += 1
    if ok:
        usable.append(t)
res["m77_usable"] = len(usable)
res["m77_exclusions"] = dict(why)
res["m77_usable_by_type"] = dict(Counter(t["object_type"] for t in usable))
dev, ho = dev_heldout(version=2)
hos = {" ".join(t["seq"]) for t in ho}
res["m77_usable_heldout_family"] = sum(" ".join(t["seq"]) in hos for t in usable)

# line-2 length profile (descriptive; says nothing about boundary scores)
l1 = []; l2 = []
for t in usable:
    i = t["seq"].index("|")
    l1.append(i); l2.append(len(t["seq"]) - i - 1)
res["m77_usable_line_lengths"] = {
    "line1_mean": float(np.mean(l1)), "line2_mean": float(np.mean(l2)),
    "line2_single_sign_share": float(np.mean(np.array(l2) == 1)),
    "line2_longer_than_line1": int(np.sum(np.array(l2) > np.array(l1))),
}

# ---------------- ICIT -----------------
I = icit_texts()
imulti = [t for t in I if "|" in t["seq"]]
idm = distinct(imulti)
res["icit_multiline_objects"] = len(imulti)
res["icit_multiline_distinct"] = len(idm)
res["icit_multiline_distinct_by_type"] = dict(Counter(t["type"].split(":")[0] for t in idm))

bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
w2m = {f"W{int(k):03d}": {f"M{m}" for m in v["M"]} for k, v in bridge.items()}

SITE = {"Mohenjo-daro": "Mohenjodaro", "Chanhu-daro": "Chanhudaro"}


def matches(iseq, mseq):
    a = [s for s in iseq if s != "#"]; b = [s for s in mseq if s != "#"]
    if len(a) != len(b):
        return False
    hits = 0
    for x, y in zip(a, b):
        if x == "|" or y == "|":
            if x != y:
                return False
            continue
        if x in w2m:
            if y not in w2m[x]:
                return False
            hits += 1
    return hits >= max(1, (len(a) - a.count("|")) // 2)


m77_seqs = [t["seq"] for t in distinct(T)]
unmatched = []
for t in idm:
    if not any(matches(t["seq"], s) for s in m77_seqs):
        unmatched.append(t)
res["icit_multiline_not_matched_to_any_m77_text"] = len(unmatched)
res["icit_unmatched_by_site"] = dict(Counter(t["site"] for t in unmatched))


def icit_usable(t):
    s = t["seq"]
    return ("#" not in s and t["complete"] and s.count("|") == 1
            and s[0] != "|" and s[-1] != "|" and len(s) - 1 >= 3)


iu = [t for t in idm if icit_usable(t)]
iu_new = [t for t in unmatched if icit_usable(t)]
res["icit_usable"] = len(iu)
res["icit_usable_by_type"] = dict(Counter(t["type"].split(":")[0] for t in iu))
res["icit_usable_unmatched_extra"] = len(iu_new)
res["union_usable_estimate"] = len(usable) + len(iu_new)

# ---------------- wrap check: is line 1 at capacity? (ICIT square seals with width) -------
def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0


seals = [t for t in distinct(I) if t["type"] == "SEAL:S" and fnum(t["width_mm"]) > 5 and t["complete"]
         and "#" not in t["seq"]]
single = [t for t in seals if "|" not in t["seq"]]
two = [t for t in seals if t["seq"].count("|") == 1]
w_s = np.array([fnum(t["width_mm"]) for t in single]); n_s = np.array([len(t["seq"]) for t in single])
pct = []
cap_rows = []
for t in two:
    w = fnum(t["width_mm"])
    i = t["seq"].index("|")
    near = n_s[np.abs(w_s - w) <= 2.0]
    if len(near) < 10:
        continue
    pct.append(float(np.mean(near < i) + 0.5 * np.mean(near == i)))
    cap_rows.append((w, i, len(t["seq"]) - i - 1, float(np.percentile(near, 90)), int(near.max())))
pct = np.array(pct)
res["wrap_check"] = {
    "n_two_line_seals_with_width": len(cap_rows),
    "line1_length_percentile_among_single_line_seals_same_width_median": float(np.median(pct)),
    "share_line1_at_or_above_p90_of_single_line": float(np.mean([r[1] >= r[3] for r in cap_rows])),
    "share_line1_below_median_single_line": float(np.mean(pct < 0.5)),
    "total_length_two_line_minus_p90_single_mean": float(np.mean([r[1] + r[2] - r[3] for r in cap_rows])),
    "line2_single_sign_share": float(np.mean([r[2] == 1 for r in cap_rows])),
}
# single-line length vs width: do longer texts simply get a bigger face?
res["single_line_len_vs_width_spearman"] = float(
    __import__("scipy.stats", fromlist=["spearmanr"]).spearmanr(w_s, n_s).correlation)

# direction combos in M77 (are 2nd lines laid out differently?)
combo = Counter()
for t in dmulti:
    ls = sorted(lines_by[(t["text_no"], t["side"])], key=lambda x: x["line"])
    combo[" + ".join(l["direction"] for l in ls)] += 1
res["m77_direction_combos"] = dict(combo.most_common())

json.dump(res, open(OUT / "count.json", "w"), indent=1)
print(json.dumps(res, indent=1))

# sample for eyeballing
with open(OUT / "sample_multiline.txt", "w") as f:
    for t in usable[:40]:
        ls = sorted(lines_by[(t["text_no"], t["side"])], key=lambda x: x["line"])
        f.write(f"{t['text_no']} {t['site']} {t['object_type']} | " +
                " || ".join(f"L{l['line']} {l['direction']}: {' '.join(l['signs'])}" for l in ls) + "\n")
    f.write("\nICIT two-line seals: width, line1 len, line2 len, p90 single-line len at width, max\n")
    for r in cap_rows:
        f.write(f"{r}\n")
