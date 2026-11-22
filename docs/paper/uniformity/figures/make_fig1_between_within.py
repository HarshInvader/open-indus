"""Figures 1 and 2. They use different row sets, so they are separate figures.
Figure 1 (fig1_between_within): between-site vs within-site AUC, single runs.
Figure 2 (fig2_gap): pool-level bootstrap 95% CIs for the gap above the floor.

Sources (all read from results.json, nothing typed in):
- experiments/uniformity_paper/step2/results.json  (part1: Ur III, Latin; part2: Indus)
- experiments/redteam_uniformity_step1/results.json (_gaps: Linear B hands, Indus M77 area split)
- experiments/uniformity_paper/revision/results.json (boot: 200 pool-level bootstrap replicates,
  d_floor = between - within, percentiles 2.5 / 50 / 97.5)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import INDUS, REF, load, plt, save  # noqa: E402

s2 = load("uniformity_paper/step2/results.json")
rt1 = load("redteam_uniformity_step1/results.json")
rev = load("uniformity_paper/revision/results.json")

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


G1 = "Indus seals, MD vs Harappa"
add_p2("m77_seal", "Mohenjo-daro", "Harappa", "M77, vs MD random halves", G1)
add_gap("Indus M77, MD DK vs HR+VS", "M77, vs MD excavation areas", G1, True)
add_p2("icit_seal", "Mohenjo-daro", "Harappa", "ICIT seals, vs MD halves", G1)
add_p2("icit_sealtype", "Mohenjo-daro", "Harappa", "ICIT seals + sealings", G1)
G2 = "Indus sealings"
add_p2("icit_sealing", "Mohenjo-daro", "Harappa", "ICIT sealings", G2)
add_p2("m77_sealing", "Harappa", "Mohenjo-daro", "M77 sealings", G2)
G3 = "Ur III seal legends, whole"
add_p1("ur3", "whole", "U_reign", "vs Umma reigns", G3)
add_p1("ur3", "whole", "U_coll", "vs Umma BM / Yale", G3)
add_p1("ur3", "whole", "G_reign", "vs Girsu reigns", G3)
add_p1("ur3", "whole", "G_coll", "vs Girsu BM / Istanbul L", G3)
G4 = "Ur III, all names removed"
add_p1("ur3", "namefree", "U_reign", "vs Umma reigns", G4)
add_p1("ur3", "namefree", "G_reign", "vs Girsu reigns (gate 62%)", G4)
G5 = "Latin marks, whole (weak reference)"
add_p1("lat", "whole", "ge_rlp_vs_bwhe", "vs Germania regions", G5)
add_p1("lat", "whole", "br_north_vs_south", "vs Britannia north / south", G5)
G6 = "Linear B tablets, whole"
add_gap("LB whole, Knossos hand groups", "vs Knossos scribe groups", G6, False)
add_gap("LB whole, Pylos hand groups", "vs Pylos scribe groups", G6, False)

B = rev["boot"]
brows = [  # (group, label, key, is_indus)
    ("Indus seals, MD vs Harappa", "M77 seals", "MDHA_m77_seal", True),
    ("Indus seals, MD vs Harappa", "ICIT seals", "MDHA_icit_seal", True),
    ("Indus seals, MD vs Harappa", "ICIT seals + sealings", "MDHA_icit_sealtype", True),
    ("Indus seals, MD vs Harappa", "unicorn seals, ICIT seals", "UNI_icit_seal", True),
    ("Indus seals, MD vs Harappa", "unicorn seals, seals + sealings", "UNI_icit_sealtype", True),
    ("Chanhu-daro", "vs Harappa, M77 seals", "CD_m77_seal_Harappa", True),
    ("Chanhu-daro", "vs MD, M77 seals", "CD_m77_seal_Mohenjo-daro", True),
    ("Chanhu-daro", "vs Harappa, ICIT seals + sealings", "CD_icit_sealtype_Harappa", True),
    ("Chanhu-daro", "vs MD, ICIT seals + sealings", "CD_icit_sealtype_Mohenjo-daro", True),
    ("Ur III, Umma vs Girsu", "vs Umma reigns", "REF_ur3_U_reign", False),
    ("Ur III, Umma vs Girsu", "vs Umma BM / Yale", "REF_ur3_U_coll", False),
    ("Ur III, Umma vs Girsu", "vs Girsu reigns", "REF_ur3_G_reign", False),
    ("Ur III, Umma vs Girsu", "vs Girsu BM / Istanbul L", "REF_ur3_G_coll", False),
    ("Ur III, Umma vs Girsu", "CDLI, vs Umma reigns", "REF_cdli_U_reign", False),
    ("Ur III, Umma vs Girsu", "CDLI, vs Girsu reigns", "REF_cdli_G_reign", False),
    ("Latin (weak reference)", "vs Germania regions", "REF_lat_ge_rlp_vs_bwhe", False),
    ("Latin (weak reference)", "vs Britannia north / south", "REF_lat_br_north_vs_south", False),
]


def layout(items):
    """Return y positions for rows and group headers."""
    y, prev, ys, heads = 0.0, None, [], []
    for it in items:
        g = it[0]
        if g != prev:
            if prev is not None:
                y -= 0.7
            heads.append((y - 0.05, g))
            y -= 0.6
            prev = g
        ys.append(y)
        y -= 1
    return ys, heads, y


# Figure 1: between vs within
fig, axa = plt.subplots(figsize=(5.0, 5.3))
ys, heads, ymin = layout(rows)
for (group, label, b, w, indus), y in zip(rows, ys):
    col = INDUS if indus else REF
    axa.plot([w, b], [y, y], color=col, lw=0.9, zorder=1)
    axa.scatter([w], [y], s=22, facecolor="white", edgecolor=col, lw=0.9, zorder=2)
    axa.scatter([b], [y], s=22, color=col, zorder=3)
for gy, g in heads:
    axa.text(0.30, gy, g, fontsize=9, fontweight="bold",
             color=INDUS if g.startswith("Indus") else "black", va="center")
axa.axvline(0.5, color="#cccccc", lw=0.6, ls=":", zorder=0)
axa.set_yticks(ys)
axa.set_yticklabels([r[1] for r in rows])
axa.tick_params(axis="y", length=0)
axa.spines["left"].set_visible(False)
axa.set_xlim(0.30, 0.95)
axa.set_ylim(ymin + 0.3, 0.6)
axa.set_xlabel("Median AUC (matched size, length mix)")
axa.scatter([], [], s=22, color="black", label="between sites")
axa.scatter([], [], s=22, facecolor="white", edgecolor="black", label="within one site (floor)")
axa.legend(loc="center right", bbox_to_anchor=(1.0, 0.70), handletextpad=0.3)
save(fig, "fig1_between_within")

# Figure 2: gap above the floor, bootstrap intervals
fig, axb = plt.subplots(figsize=(5.0, 4.9))
ys, heads, ymin = layout(brows)
axb.axvspan(-0.05, 0.05, color="#eeeeee", zorder=0)
axb.axvline(0, color="#999999", lw=0.6, zorder=0)
for (group, label, key, indus), y in zip(brows, ys):
    d = B[key]["d_floor"]
    col = INDUS if indus else REF
    axb.plot([d["2.5"], d["97.5"]], [y, y], color=col, lw=1.1, zorder=1)
    axb.scatter([d["50"]], [y], s=20, color=col, zorder=2)
for gy, g in heads:
    axb.text(-0.15, gy, g, fontsize=9, fontweight="bold",
             color=INDUS if g.startswith(("Indus", "Chanhu")) else "black", va="center")
axb.set_yticks(ys)
axb.set_yticklabels([r[1] for r in brows])
axb.tick_params(axis="y", length=0)
axb.spines["left"].set_visible(False)
axb.set_xlim(-0.15, 0.45)
axb.set_ylim(ymin + 0.3, 1.5)
axb.set_xlabel(r"$\Delta$ = between $-$ within (AUC), bootstrap 95% CI")
axb.text(0.0, 0.95, "margin $\\pm$0.05", fontsize=8, color=REF, ha="center", va="bottom")
save(fig, "fig2_gap")
