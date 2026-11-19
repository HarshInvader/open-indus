"""Draw the figures for docs/paper/latex/main.tex.

Values are read from results files where they are stored as data, and
copied by hand (with the file named) where they exist only in a RESULTS.md
table. Run: .venv/bin/python -I scripts/paper_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/paper/latex/figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#222222"
MUTED = "#9a9a9a"
ACCENT = "#b5452b"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
})


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


def fig_disagreement():
    # experiments/redteam_consensus/RESULTS.md, section B ("Sites differ")
    bars = [(0.0, "Mohenjo-\ndaro", 10.8, INK), (1.0, "Harappa", 17.5, INK),
            (2.6, "Seals", 11, MUTED), (3.6, "Tablets", 18, MUTED), (4.6, "Sealings", 24, MUTED)]
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    ax.axhline(12.9, color=ACCENT, lw=0.9, ls="--", zorder=0)
    for x, lab, v, c in bars:
        ax.bar(x, v, color=c, width=0.7)
        ax.text(x, v - 0.8, f"{v:g}%", ha="center", va="top", fontsize=7.5, color="white")
    ax.text(5.0, 13.3, "all\nobjects\n12.9%", color=ACCENT, ha="left", va="bottom", fontsize=7.5)
    ax.set_xlim(-0.5, 5.75)
    ax.set_xticks([b[0] for b in bars], [b[1] for b in bars], fontsize=8)
    ax.set_ylabel("signs read differently (%)")
    ax.set_ylim(0, 27)
    ax.text(0.5, -0.36, "by site", transform=ax.get_xaxis_transform(), ha="center", fontsize=8, color=MUTED)
    ax.text(3.6, -0.36, "by object type", transform=ax.get_xaxis_transform(), ha="center", fontsize=8, color=MUTED)
    save(fig, "fig1_disagreement")


def fig_leakage():
    d = json.loads((ROOT / "experiments/redteam_bench_restoration/results.json").read_text())
    g = d["leak_grid"]
    rows = [("exact copy", g["k0_containFalse"]["share"]),
            ("1 edit", g["k1_containFalse"]["share"]),
            ("exact or contained", g["k0_containTrue"]["share"]),
            ("1 edit or contained*", g["k1_containTrue"]["share"]),
            ("2 edits", g["k2_containFalse"]["share"]),
            ("2 edits or contained", g["k2_containTrue"]["share"])]
    s3 = d["S3_random_object_split_share"]
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for i, (lab, v) in enumerate(rows):
        primary = lab.endswith("*")
        ax.barh(i, v, color=ACCENT if primary else MUTED, height=0.65)
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=8)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 60)
    ax.set_xlabel("test texts with a copy in training (%)")
    ax.axvspan(s3["p2.5"], s3["p97.5"], ymin=0, ymax=1, color=ACCENT, alpha=0.08, lw=0)
    save(fig, "fig2_leakage")


def fig_restoration():
    # experiments/bench_restoration/RESULTS.md, retraining table
    conds = ["size control", "near-copies\nremoved", "split by\nfamily"]
    vals = {"trigram": [41.71, 35.44, 35.45],
            "transformer": [39.00, 33.10, 35.66],
            "blend": [43.42, 36.16, 36.41]}
    colours = {"trigram": INK, "transformer": MUTED, "blend": ACCENT}
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    w = 0.26
    for j, (m, v) in enumerate(vals.items()):
        xs = [i + (j - 1) * w for i in range(3)]
        ax.bar(xs, v, width=w, color=colours[m], label=m)
    ax.set_xticks(range(3), conds, fontsize=8)
    ax.set_ylabel("top-1 accuracy (%)")
    ax.set_ylim(0, 50)
    ax.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    save(fig, "fig3_restoration")


def fig_order():
    # experiments/audit_followups/RESULTS.md, order-test table (median of 5 seeds)
    rows = [("METAR weather reports", "code", 0.98), ("chess openings", "code", 0.63),
            ("Old Babylonian seal legends", "writing", 0.60), ("emoji sequences", "code", 0.60),
            ("heraldic blazons", "code", 0.49), ("Ur III seal legends", "writing", 0.47),
            ("Indus (held-out)", "indus", 0.40),
            ("Linear B entry lines", "writing", 0.34), ("Egyptian verbless phrases", "writing", 0.24),
            ("pop chord phrases", "code", 0.23), ("ICD-10 codes", "code", 0.13),
            ("Latin labels and stamps", "writing", 0.11), ("Latin short inscriptions", "writing", 0.10),
            ("khipu", "code", 0.09)]
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    for i, (lab, kind, v) in enumerate(rows):
        if kind == "indus":
            ax.plot(v, i, "D", color=ACCENT, ms=5)
        elif kind == "code":
            ax.plot(v, i, "o", mfc="white", mec=INK, ms=4.5)
        else:
            ax.plot(v, i, "o", color=INK, ms=4.5)
        ax.hlines(i, 0, v, color="#dddddd", lw=0.6, zorder=0)
    ax.axvline(0.30, color=ACCENT, lw=0.8, ls="--")
    ax.text(0.31, -0.6, "pass bar 0.30", color=ACCENT, fontsize=7.5, va="center")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=7.5)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(len(rows) - 0.4, -1.2)
    ax.set_xlabel("share of texts whose real order beats every reordering")
    ax.plot([], [], "o", mfc="white", mec=INK, ms=4.5, ls="", label="non-linguistic code")
    ax.plot([], [], "o", color=INK, ms=4.5, ls="", label="writing")
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    save(fig, "fig4_order")


if __name__ == "__main__":
    fig_disagreement()
    fig_leakage()
    fig_restoration()
    fig_order()
    print("wrote", sorted(p.name for p in OUT.glob("*.pdf")))
