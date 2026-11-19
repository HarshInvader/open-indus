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
    d = json.loads((ROOT / "experiments/split_leakage/results.json").read_text())
    rules = ["1 edit", "exact or contained", "1 edit or contained", "2 edits", "2 edits or contained"]
    labels = ["1 edit", "exact or contained", "1 edit or contained*", "2 edits", "2 edits or contained"]
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    h = 0.36
    for key, off, col, lab in [("A_all_texts", -h / 2, MUTED, "all texts"),
                               ("B_exact_repeats_removed", h / 2, ACCENT, "exact repeats removed")]:
        for i, r in enumerate(rules):
            v = d[key][r]
            ax.barh(i + off, v["median"], height=h, color=col, label=lab if i == 0 else None)
            ax.errorbar(v["median"], i + off, xerr=[[v["median"] - v["p2.5"]], [v["p97.5"] - v["median"]]],
                        color=INK, lw=0.7, capsize=1.5)
    ax.set_yticks(range(len(rules)), labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 80)
    ax.set_xlabel("test texts with a copy in training (%)")
    ax.legend(frameon=False, fontsize=7.5, ncol=2, loc="lower center", bbox_to_anchor=(0.4, 1.0))
    save(fig, "fig2_leakage")


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
    fig_order()
    print("wrote", sorted(p.name for p in OUT.glob("*.pdf")))
