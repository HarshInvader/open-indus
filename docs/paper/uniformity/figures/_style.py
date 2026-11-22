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

TEXTWIDTH = 6.29  # inches: A4 with 2.5 cm margins (160 mm); figures must not exceed it
MIN_PT = 8

INDUS = "#3b3f9e"   # indigo for Indus rows
REF = "#6b6b6b"     # grey for reference corpora
LIGHT = "#b8b8b8"

plt.rcParams.update({
    "font.family": "serif",
    # Figures are drawn at their printed size and included unscaled, so these are the
    # printed sizes in points. Nothing in any figure is smaller than 8 pt.
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8,
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


def _check_fonts(fig):
    small = sorted({round(t.get_fontsize(), 2) for t in fig.findobj(matplotlib.text.Text)
                    if t.get_text().strip() and t.get_visible() and t.get_fontsize() < MIN_PT})
    if small:
        raise SystemExit(f"text below {MIN_PT} pt: {small}")


def save(fig, name):
    _check_fonts(fig)
    # No creation date in the PDF, so both formats rebuild byte for byte.
    meta = {"pdf": {"CreationDate": None}, "png": {}}
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", metadata=meta[ext])
    w = fig.get_tightbbox(fig.canvas.get_renderer()).width + 2 * plt.rcParams["savefig.pad_inches"]
    if w > TEXTWIDTH:
        raise SystemExit(f"{name}: {w:.2f} in wide, over the {TEXTWIDTH} in text width")
    print("wrote", OUT / f"{name}.pdf", f"({w:.2f} in wide)")
