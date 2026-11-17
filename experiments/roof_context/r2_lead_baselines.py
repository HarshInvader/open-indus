"""Old-data baselines for the frozen lead predictions (docs/prereg/2026-11-15_leads_predictions.md).
Writes lead_baselines.json. Units: distinct texts. Run before freezing the predictions file."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa
from corpus.load import runs  # noqa

OUT = {}
dev, ho = dev_heldout(version=2)
M = [t for t in dev + ho]


def clean(seq):
    return [s for s in seq if s not in ("|", "#")]


# L1 roof initial (M77 all, complete texts >= 2 signs, no breaks)
PM = roof_pairs("M")
roofed = {d for ds in PM.values() for d in ds}
bases = set(PM)
r_i = r_n = b_i = b_n = 0
for t in M:
    if "#" in t["seq"]:
        continue
    s = clean(t["seq"])
    if len(s) < 2:
        continue
    for i, x in enumerate(s):
        if x in roofed:
            r_n += 1; r_i += i == 0
        elif x in bases:
            b_n += 1; b_i += i == 0
OUT["L1_roof_initial"] = {"roofed_initial": r_i, "roofed_n": r_n, "base_initial": b_i, "base_n": b_n,
                          "roofed_share": r_i / r_n, "base_share": b_i / b_n}

# L3 ticked fish final
TICK = {"M60", "M66", "M68", "M71", "M73"}; PLAIN = {"M59", "M65", "M67", "M70", "M72", "M75"}
tk = [i == len(s) - 1 for t in M if "#" not in t["seq"] for s in [clean(t["seq"])] if len(s) >= 2 for i, x in enumerate(s) if x in TICK]
pl = [i == len(s) - 1 for t in M if "#" not in t["seq"] for s in [clean(t["seq"])] if len(s) >= 2 for i, x in enumerate(s) if x in PLAIN]
OUT["L3_ticked_final"] = {"ticked_final": sum(tk), "ticked_n": len(tk), "plain_final": sum(pl), "plain_n": len(pl)}

# L4 / L6 numerals (redteam_pnl tables)
ST = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
SHORT = {f"M{k}": v for k, v in ST["short"].items() if f"M{k}" not in ("M99", "M101")}
TALL = {f"M{k}": v for k, v in ST["tall"].items()}
pre59 = Counter()
pairs = []
for t in M:
    for run in runs(t["seq"]):
        for a, b in zip(run, run[1:]):
            if (a in SHORT or a in TALL) and not (b in SHORT or b in TALL):
                sysn = "tall" if a in TALL else "short"
                val = TALL.get(a) or SHORT.get(a)
                pairs.append((sysn, val, b))
                if b == "M59":
                    pre59[(sysn, val)] += 1
OUT["L4_numeral_before_M59"] = {f"{k[0]}{k[1]}": v for k, v in pre59.most_common()}
LEX = {"M211": ("tall", 3), "M59": ("tall", 2), "M342": ("tall", 2), "M60": ("tall", 2), "M197": ("short", 7),
       "M15": ("short", 3), "M194": ("short", 7), "M403": ("short", 3), "M25": ("short", 1), "M284": ("tall", 2),
       "M190": ("short", 3)}  # redteam_pnl lexeme heads minus M287 (failed its own held-out test)
kept = Counter(); tot = Counter()
for sysn, val, b in pairs:
    if b in LEX and LEX[b][0] == sysn:
        tot[b] += 1; kept[b] += LEX[b][1] == val
OUT["L6_lexeme_heads_all_M77"] = {b: f"{kept[b]}/{tot[b]}" for b in LEX}
OUT["L6_pooled_expected_share"] = 0.325  # redteam_pnl held-out pooled numeral distribution

# L5 M93
m93 = [t for t in m77_texts() if "M93" in t["seq"]]
pos = Counter()
for t in m93:
    s = t["seq"]; i = s.index("M93")
    pos["line_final_or_alone" if i == len(s) - 1 or s[i + 1] == "|" else "medial"] += 1
OUT["L5_M93"] = {"texts": len(m93), "sites": dict(Counter(t["site"] for t in m93)), "position": dict(pos)}

# L2 oval on bangles (ICIT)
I = distinct(icit_texts())
bang = [t for t in icit_texts() if t["type"] == "BNGL"]
seen = set(); B = []
for t in bang:
    k = (tuple(t["seq"]), t["site"])
    if k not in seen:
        seen.add(k); B.append(t)
short_other = [t for t in I if t["type"] != "BNGL" and 1 <= len(clean(t["seq"])) <= 3]
OUT["L2_oval_bangle"] = {"bangle_texts": len(B), "with_W790": sum("W790" in t["seq"] for t in B),
                         "with_W840_M403": sum("W840" in t["seq"] for t in B),
                         "other_short_texts": len(short_other),
                         "other_short_with_W790": sum("W790" in t["seq"] for t in short_other),
                         "other_short_with_W840": sum("W840" in t["seq"] for t in short_other)}

# L7 no-animal seals (ICIT square seals with sizes)
sz = {"none": [], "animal": []}
for t in I:
    if t["type"] != "SEAL:S":
        continue
    try:
        w, h = float(t["width_mm"]), float(t["height_mm"])
    except ValueError:
        continue
    if w <= 0 or h <= 0:
        continue
    (sz["none"] if t["symbol"] == "None" else sz["animal"] if t["symbol"] not in ("-", "") else []).append(max(w, h))
OUT["L7_seal_size_icit_square"] = {k: {"n": len(v), "median_mm": float(np.median(v))} for k, v in sz.items()}
OUT["L7_seal_size_icit_square"]["ratio"] = OUT["L7_seal_size_icit_square"]["none"]["median_mm"] / OUT["L7_seal_size_icit_square"]["animal"]["median_mm"]
print(json.dumps(OUT, indent=1, default=float))
json.dump(OUT, open(HERE / "lead_baselines.json", "w"), indent=1, default=float)
