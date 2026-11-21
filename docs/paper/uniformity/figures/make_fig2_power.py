"""Figure 2: detection curves for planted local sign stocks and planted names.

Sources:
- experiments/uniformity_paper/step2/results.json (part2 power: 20-sign stock in
  Harappa at share q, detected when AUC - within median >= 0.05)
- experiments/redteam_uniformity_step2/results.json (a3 curves: share of draws whose
  AUC - within median exceeds the observed gap; excluded at >= 95%)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import INDUS, REF, load, plt, save  # noqa: E402

s2 = load("uniformity_paper/step2/results.json")
rt2 = load("redteam_uniformity_step2/results.json")

fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.4, 2.5))

# Panel A: planted stock
pools = [("m77_seal", "M77 seals", "-"), ("icit_seal", "ICIT seals", "--"),
         ("icit_sealtype", "ICIT seals + sealings", ":")]
for fam, lab, ls in pools:
    r = next(r for r in s2["part2"] if r["family"] == fam and r["a"] == "Mohenjo-daro" and r["b"] == "Harappa")
    qs = sorted(r["power"], key=float)
    axa.plot([float(q) * 100 for q in qs], [r["power"][q] * 100 for q in qs],
             ls=ls, color=INDUS, marker="o", ms=3, lw=1, label=lab)
axa.axhline(80, color=REF, lw=0.6, ls=":")
axa.text(10.2, 82, "gate 80%", fontsize=7, color=REF, va="bottom")
axa.set_xlabel("Local sign stock (% of tokens)")
axa.set_ylabel("Draws detected (%)")
axa.set_xticks([10, 15, 20])
axa.set_ylim(0, 105)
axa.set_title("A. Planted local sign stock", fontsize=8.5, loc="left")
axa.legend(fontsize=6.8, loc="lower right")

# Panel B: planted names, M77 seals (solid) and ICIT seals (dashed)
forms = [("sign", "invented, one new sign", "#9a9a9a"),
         ("spelt", "invented, two shared signs", "#555555"),
         ("ur3emp", "real Ur III name frequencies", INDUS)]
for pool, ls in [("m77_seal", "-"), ("icit_seal", "--")]:
    curve = rt2["a3"][f"{pool}|curve"]
    for form, lab, col in forms:
        pts = sorted((c["rate"], c["frac_above_obs"]) for c in curve if c["form"] == form)
        axb.plot([p[0] * 100 for p in pts], [p[1] * 100 for p in pts], ls=ls, color=col,
                 marker="o" if ls == "-" else None, ms=2.5, lw=1,
                 label=lab if pool == "m77_seal" else None)
axb.axhline(95, color=REF, lw=0.6, ls=":")
axb.text(55, 88, "excluded at 95%", fontsize=7, color=REF, va="top")
axb.set_xlabel("Seals carrying a site-specific name (%)")
axb.set_ylabel("Draws above observed gap (%)")
axb.set_ylim(0, 105)
axb.set_xlim(0, 102)
axb.set_title("B. Planted names (solid M77, dashed ICIT)", fontsize=8.5, loc="left")
axb.legend(fontsize=6.5, loc="lower right")
fig.tight_layout(w_pad=2)
save(fig, "fig2_power")
