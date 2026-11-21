"""Shared plotting style and paths for the uniformity paper figures."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
EXP = REPO / "experiments"
OUT = REPO / "docs" / "paper" / "uniformity" / "latex" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INDUS = "#3b3f9e"   # indigo for Indus rows
REF = "#6b6b6b"     # grey for reference corpora
LIGHT = "#b8b8b8"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "savefig.dpi": 300,
})


def load(rel):
    return json.loads((EXP / rel).read_text())


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight")
    print("wrote", OUT / f"{name}.pdf")
