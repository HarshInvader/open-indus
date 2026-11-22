"""Figure 4: site-pair gaps (between minus within) on a schematic map, Chanhu-daro marked.

Source: experiments/uniformity_paper/step2/results.json, part2, family
'icit_sealtype' (ICIT seals + sealings, the only family that covers all six sites).
Coordinates: experiments/recchia_rerun/rr.py COORD (five sites, frozen in that prereg);
Dholavira is added at its approximate published position (23.89 N, 70.21 E).
Positions are for orientation only; no number in the paper depends on them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import INDUS, REF, load, plt, save  # noqa: E402

COORD = {"Mohenjo-daro": (27.3243, 68.1357), "Harappa": (30.6280, 72.8640),
         "Chanhu-daro": (26.1740, 68.3240), "Lothal": (22.5215, 72.2491),
         "Kalibangan": (29.4730, 74.1300), "Dholavira": (23.887, 70.213)}

s2 = load("uniformity_paper/step2/results.json")
rows = [r for r in s2["part2"] if r["family"] == "icit_sealtype"
        and ({r["a"], r["b"]} & {"Mohenjo-daro", "Harappa"})]

fig, ax = plt.subplots(figsize=(5.0, 4.6))
LABEL_SHIFT = {  # (dx, dy) in degrees for edge labels that would collide
    ("Mohenjo-daro", "Chanhu-daro"): (-0.75, -0.05),
    ("Harappa", "Chanhu-daro"): (0.35, -0.35),
    ("Mohenjo-daro", "Harappa"): (0.0, 0.25),
    ("Mohenjo-daro", "Kalibangan"): (1.55, 0.55),
    ("Harappa", "Dholavira"): (0.15, -0.35),
}
for r in rows:
    a, b = r["a"], r["b"]
    (ya, xa), (yb, xb) = COORD[a], COORD[b]
    cd = "Chanhu-daro" in (a, b)
    # Reporting labels (paper Section 2): gate = power at s = 0.15 >= 80%.
    gate = r["power"]["0.15"] >= 0.8
    if r["verdict"] in ("same", "differs"):
        kind = "settled"
    elif gate and r["delta"] >= 0.05:
        kind = "inconclusive"
    else:
        kind = "underpowered"
    ls = {"settled": "-", "inconclusive": (0, (4, 2)), "underpowered": (0, (1, 1.5))}[kind]
    # "differs" against the floor but not against the shuffled-label null
    floor_only = r["verdict"] == "differs" and r["q_chance"] > 0.10
    col = "#b5473a" if cd else (INDUS if kind == "settled" else REF)
    ax.plot([xa, xb], [ya, yb], color=col, lw=0.6 + 8 * max(r["delta"], 0),
            ls=ls, alpha=0.9, zorder=1)
    dx, dy = LABEL_SHIFT.get((a, b), (0, 0))
    ax.text((xa + xb) / 2 + dx, (ya + yb) / 2 + dy,
            f"{r['delta']:+.3f}" + ("*" if kind == "underpowered" else "") + ("†" if floor_only else ""),
            fontsize=8, color=col, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85), zorder=3)

for site, (lat, lon) in COORD.items():
    big = site in ("Mohenjo-daro", "Harappa")
    ax.scatter([lon], [lat], s=46 if big else 22, color="black", zorder=4)
    if site == "Chanhu-daro":
        ax.scatter([lon], [lat], s=170, facecolor="none", edgecolor="#b5473a", lw=1.1, zorder=4)
    off = {"Chanhu-daro": (-0.25, -0.45, "right"), "Mohenjo-daro": (-0.25, 0.15, "right"),
           "Harappa": (0.2, 0.2, "left"), "Lothal": (0.2, -0.25, "left"),
           "Kalibangan": (0.2, 0.1, "left"), "Dholavira": (-0.2, -0.3, "right")}[site]
    ax.text(lon + off[0], lat + off[1], site, fontsize=9, ha=off[2],
            fontweight="bold" if big else "normal", zorder=5)

ax.set_xlim(64.6, 75.8)
ax.set_ylim(21.6, 31.6)
ax.set_aspect(1 / 0.89)  # rough cos(latitude) correction
ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")
ax.plot([], [], color=INDUS, lw=1.2, label="same or differs (gate passes)")
ax.plot([], [], color=REF, lw=1.2, ls=(0, (4, 2)), label="inconclusive (gate passes, q > 0.10)")
ax.plot([], [], color=REF, lw=1.2, ls=(0, (1, 1.5)), label="underpowered (*)")
ax.plot([], [], color="#b5473a", lw=1.2, label="pairs with Chanhu-daro")
ax.plot([], [], color="none", label="† differs vs floor, not vs null")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, columnspacing=1.2)
save(fig, "fig4_sites")
