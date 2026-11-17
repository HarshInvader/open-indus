"""Baseline rates on the OLD corpora (M77 distinct texts, ICIT) for the frozen new-finds predictions.
Run BEFORE looking at any new text. Writes experiments/new_finds/baselines.json and ref_tables.json
(reference pair orders, opener/closer inventories) used by score.py.

    .venv/bin/python experiments/new_finds/baselines.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, runs

OUT = ROOT / "experiments" / "new_finds"
FISH_PLAIN = {"M59", "M65", "M67", "M70", "M72", "M75"}
FISH_TICK = {"M60", "M66", "M68", "M71", "M73"}
FISH_ALL = FISH_PLAIN | FISH_TICK | {"M61", "M62", "M63", "M64", "M69", "M74"}

T = [t for t in distinct(m77_texts()) if t["site"] != "West Asian finds" and t["seq"]]
signs = lambda t: [s for s in t["seq"] if s not in ("|", "#")]


def unbroken(t):
    return "#" not in t["seq"]


def ok(t):  # complete, no break, >= 2 signs
    return t.get("complete") and unbroken(t) and len(signs(t)) >= 2


C = [t for t in T if ok(t)]
B = {}
B["n_m77_distinct_native"] = len(T); B["n_complete_ge2"] = len(C)
# P1 jar final
B["P1_jar_final_share_complete"] = sum(signs(t)[-1] == "M342" for t in C) / len(C)
seals = [t for t in C if t["object_type"] == "seal"]
B["P1_jar_final_share_seals"] = sum(signs(t)[-1] == "M342" for t in seals) / len(seals)
# jar or jar+M176 ending
B["P1b_jar_or_jar176_end"] = sum(signs(t)[-1] == "M342" or signs(t)[-2:] == ["M342", "M176"] for t in C) / len(C)
# P1c jar position: of M342 tokens in unbroken texts, share line-final
jt = jf = 0
for t in T:
    if not unbroken(t): continue
    for r in runs(t["seq"]):
        for i, s in enumerate(r):
            if s == "M342":
                jt += 1; jf += (i == len(r) - 1) or (i == len(r) - 2 and r[-1] == "M176")
B["P1c_jar_tokens_final_or_before_M176"] = jf / jt; B["P1c_n"] = jt
# P3 ticked fish final (line-final, among occurrences in unbroken runs)
def final_share(group):
    n = f = 0
    for t in T:
        if not unbroken(t): continue
        for r in runs(t["seq"]):
            for i, s in enumerate(r):
                if s in group:
                    n += 1; f += i == len(r) - 1
    return f / n, n
B["P3_ticked_fish_final"], B["P3_ticked_n"] = final_share(FISH_TICK)
B["P3_plain_fish_final"], B["P3_plain_n"] = final_share(FISH_PLAIN)
# P4 six+fish: M109 tokens followed by M59
n109 = f109 = 0
for t in T:
    for r in runs(t["seq"]):
        for i, s in enumerate(r):
            if s == "M109" and i < len(r) - 1:
                n109 += 1; f109 += r[i + 1] == "M59"
B["P4_M109_next_M59"], B["P4_n"] = f109 / n109, n109
# P2 pair order reference
pairs = defaultdict(lambda: [0, 0])
for t in T:
    for r in runs(t["seq"]):
        for a, b in zip(r, r[1:]):
            if a == b: continue
            x, y = sorted((a, b)); pairs[(x, y)][0 if (a, b) == (x, y) else 1] += 1
ref_pairs = {}
for (x, y), (f, rv) in pairs.items():
    if f + rv >= 2 and max(f, rv) / (f + rv) >= 2 / 3:
        ref_pairs[f"{x} {y}" if f >= rv else f"{y} {x}"] = f + rv
B["P2_ref_pairs"] = len(ref_pairs)
B["P2_in_sample_majority_share"] = sum(max(v) for (k, v) in pairs.items() if f"{k[0]} {k[1]}" in ref_pairs or f"{k[1]} {k[0]}" in ref_pairs) / \
    sum(sum(v) for (k, v) in pairs.items() if f"{k[0]} {k[1]}" in ref_pairs or f"{k[1]} {k[0]}" in ref_pairs)
# P6/P7 opener / closer inventories
first = Counter(signs(t)[0] for t in T if len(signs(t)) >= 1 and t["seq"][0] != "#")
last = Counter(signs(t)[-1] for t in T if len(signs(t)) >= 1 and t["seq"][-1] != "#")
inv = Counter(s for t in T for s in signs(t))
B["P6_first_sign_types"] = len(first); B["P7_last_sign_types"] = len(last)
# leave-one-site-out style check: for each M77 site other than MD/H, share of first signs seen as first at other sites
for site in ("Lothal", "Kalibangan", "Chanhudaro"):
    oth = Counter(signs(t)[0] for t in T if t["site"] != site and t["seq"][0] != "#" and signs(t))
    othl = Counter(signs(t)[-1] for t in T if t["site"] != site and t["seq"][-1] != "#" and signs(t))
    st = [t for t in C if t["site"] == site]
    if st:
        B[f"P6_LOSO_{site}_first_known"] = sum(signs(t)[0] in oth for t in st) / len(st)
        B[f"P7_LOSO_{site}_last_known"] = sum(signs(t)[-1] in othl for t in st) / len(st)
        B[f"LOSO_{site}_n"] = len(st)
# P8 token coverage by M77 inventory: LOSO
for site in ("Lothal", "Kalibangan", "Chanhudaro"):
    oth = Counter(s for t in T if t["site"] != site for s in signs(t))
    toks = [s for t in T if t["site"] == site for s in signs(t)]
    B[f"P8_LOSO_{site}_token_known"] = sum(s in oth for s in toks) / len(toks)
# P9 opener position: M267/M391 when present first (or 2nd after a numeral/noun)
o_n = o_first = 0
for t in C:
    s = signs(t)
    for i, x in enumerate(s):
        if x in ("M267", "M391"):
            o_n += 1; o_first += i == 0
B["P9_opener_first_share"], B["P9_n"] = o_first / o_n, o_n
# P10 M176 final
n176 = f176 = a176 = 0
for t in T:
    if not unbroken(t): continue
    for r in runs(t["seq"]):
        for i, s in enumerate(r):
            if s == "M176":
                n176 += 1; f176 += i == len(r) - 1; a176 += i > 0 and r[i - 1] == "M342"
B["P10_M176_final"], B["P10_M176_after_jar"], B["P10_n"] = f176 / n176, a176 / n176, n176
# P11 fish first in fish+partner pairs
fp = ff = 0
for t in T:
    for r in runs(t["seq"]):
        for a, b in zip(r, r[1:]):
            if (a in FISH_ALL) != (b in FISH_ALL):
                fp += 1; ff += a in FISH_ALL
B["P11_fish_first_share"], B["P11_n"] = ff / fp, fp
# P12 lengths
L = [len(signs(t)) for t in C]
import statistics
B["P12_mean_len_complete"] = statistics.mean(L); B["P12_median_len"] = statistics.median(L)
# P13 direction (ICIT, native sites, where recorded)
ic = [t for t in distinct(icit_texts()) if t["direction"] in ("R/L", "L/R")]
B["P13_icit_RL_share"] = sum(t["direction"] == "R/L" for t in ic) / len(ic); B["P13_n"] = len(ic)
# opener/closer: share of complete texts whose first sign is M267/M391/M293 etc.
json.dump(B, open(OUT / "baselines.json", "w"), indent=1)
json.dump(dict(ref_pairs=ref_pairs, first=dict(first), last=dict(last), inventory=dict(inv)),
          open(OUT / "ref_tables.json", "w"))
for k, v in B.items():
    print(f"{k:45s} {v:.3f}" if isinstance(v, float) else f"{k:45s} {v}")
