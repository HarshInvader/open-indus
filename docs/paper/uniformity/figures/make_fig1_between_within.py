"""Figure 1: between-site vs within-site AUC, one row per corpus and split.

Sources (all read from results.json, nothing typed in):
- experiments/uniformity_paper/step2/results.json  (part1: Ur III, Latin; part2: Indus)
- experiments/redteam_uniformity_step1/results.json (_gaps: Linear B hands, Indus M77 area split)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import INDUS, REF, load, plt, save  # noqa: E402

s2 = load("uniformity_paper/step2/results.json")
rt1 = load("redteam_uniformity_step1/results.json")

p1 = {(r["corpus"], r["variant"], r["split"]): r for r in s2["part1"]}
p2 = {(r["family"], r["a"], r["b"]): r for r in s2["part2"]}
gaps = rt1["_gaps"]

rows = []  # (group, label, between, within, is_indus)


def add_p2(fam, a, b, label, group):
    r = p2[(fam, a, b)]
    rows.append((group, label, r["between"], r["within"], True))


def add_p1(corpus, variant, split, label, group):
    r = p1[(corpus, variant, split)]
    rows.append((group, label, r["b"], r["w"], False))


def add_gap(key, label, group, indus):
    g = gaps[key]
    rows.append((group, label, g["between"], g["within"], indus))


G1 = "Indus seals"
add_p2("m77_seal", "Mohenjo-daro", "Harappa", "M77, vs MD random halves", G1)
add_gap("Indus M77, MD DK vs HR+VS", "M77, vs MD excavation areas", G1, True)
add_p2("icit_seal", "Mohenjo-daro", "Harappa", "ICIT seals, vs MD halves", G1)
add_p2("icit_sealtype", "Mohenjo-daro", "Harappa", "ICIT seals + sealings, vs MD halves", G1)
G2 = "Indus sealings"
add_p2("icit_sealing", "Mohenjo-daro", "Harappa", "ICIT sealings", G2)
add_p2("m77_sealing", "Harappa", "Mohenjo-daro", "M77 sealings", G2)
G3 = "Ur III seal legends, whole"
add_p1("ur3", "whole", "U_reign", "vs Umma reigns", G3)
add_p1("ur3", "whole", "U_coll", "vs Umma BM / Yale", G3)
add_p1("ur3", "whole", "G_reign", "vs Girsu reigns", G3)
add_p1("ur3", "whole", "G_coll", "vs Girsu BM / Istanbul L", G3)
G4 = "Ur III, personal names removed"
add_p1("ur3", "namefree", "U_reign", "vs Umma reigns", G4)
add_p1("ur3", "namefree", "G_reign", "vs Girsu reigns (gate 62%)", G4)
G5 = "Latin owner/maker marks, whole"
add_p1("lat", "whole", "ge_rlp_vs_bwhe", "vs Germania regions", G5)
add_p1("lat", "whole", "br_north_vs_south", "vs Britannia north / south", G5)
G6 = "Linear B tablets, whole"
add_gap("LB whole, Knossos hand groups", "vs Knossos scribe groups", G6, False)
add_gap("LB whole, Pylos hand groups", "vs Pylos scribe groups", G6, False)

fig, ax = plt.subplots(figsize=(5.6, 5.4))
y = 0
yt, yl = [], []
prev = None
group_y = []
for group, label, b, w, indus in rows:
    if group != prev:
        if prev is not None:
            y -= 0.7
        group_y.append((y + 0.55, group))
        y -= 0.6
        prev = group
    col = INDUS if indus else REF
    ax.plot([w, b], [y, y], color=col, lw=0.9, zorder=1)
    ax.scatter([w], [y], s=22, facecolor="white", edgecolor=col, lw=0.9, zorder=2)
    ax.scatter([b], [y], s=22, color=col, zorder=3)
    yt.append(y)
    yl.append(label)
    y -= 1

for gy, g in group_y:
    ax.text(0.30, gy - 0.35, g, fontsize=8.5, fontweight="bold",
            color=INDUS if g.startswith("Indus") else "black", va="center")

ax.axvline(0.5, color="#cccccc", lw=0.6, ls=":", zorder=0)
ax.set_yticks(yt)
ax.set_yticklabels(yl, fontsize=7.5)
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_xlim(0.30, 0.95)
ax.set_ylim(y + 0.3, 1.0)
ax.set_xlabel("Median AUC (matched size and length mix)")
ax.scatter([], [], s=22, color="black", label="between sites")
ax.scatter([], [], s=22, facecolor="white", edgecolor="black", label="within one site (floor)")
ax.legend(loc="upper right", fontsize=7.5, handletextpad=0.3)
save(fig, "fig1_between_within")
