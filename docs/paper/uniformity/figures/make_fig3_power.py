"""Figure 3: detection curves for planted local sign stocks, planted names and diffuse effects.

Sources:
- experiments/uniformity_paper/step2/results.json (part2 power: 20-sign stock in
  Harappa at share s, detected when AUC - within median >= 0.05)
- experiments/uniformity_paper/revision/results.json
    names:   60 replicates per rate, r = 0 to 0.5; exceed_obs = share of replicates whose gap
             above the floor exceeds the observed step-2 gap; excluded at >= 95%
    diffuse: 50 draws per level; power = share with AUC - step-2 within >= 0.05;
             x = share of Harappa tokens actually altered
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import INDUS, REF, load, plt, save  # noqa: E402

s2 = load("uniformity_paper/step2/results.json")
rev = load("uniformity_paper/revision/results.json")

POOLS = [("m77_seal", "M77 seals", "-"), ("icit_seal", "ICIT seals", "--"),
         ("icit_sealtype", "ICIT seals + sealings", ":")]

fig, ((axa, axb), (axc, axk)) = plt.subplots(2, 2, figsize=(5.9, 5.0))

# Panel A: planted stock
for fam, lab, ls in POOLS:
    r = next(r for r in s2["part2"] if r["family"] == fam and r["a"] == "Mohenjo-daro" and r["b"] == "Harappa")
    qs = sorted(r["power"], key=float)
    axa.plot([float(q) * 100 for q in qs], [r["power"][q] * 100 for q in qs],
             ls=ls, color=INDUS, marker="o", ms=3, lw=1, label=lab)
axa.axhline(80, color=REF, lw=0.6, ls=":")
axa.text(10.2, 82, "gate 80%", fontsize=8, color=REF, va="bottom")
axa.set_xlabel("Local sign stock (% of tokens)")
axa.set_ylabel("Draws detected (%)")
axa.set_xticks([10, 15, 20])
axa.set_ylim(0, 105)
axa.set_title("A. Local sign stock", loc="left")

# Panel B: planted names, finer grid
forms = [("sign", "invented, one new sign", "#9a9a9a"),
         ("spelt", "invented, two shared signs", "#555555"),
         ("ur3emp", "real Ur III frequencies", INDUS)]
for fam, _, ls in POOLS:
    fr = rev["names"][fam]["forms"]
    for form, lab, col in forms:
        ex = fr[form]["exceed_obs"]
        rs = sorted(ex, key=float)
        axb.plot([float(r) * 100 for r in rs], [ex[r] * 100 for r in rs], ls=ls, color=col,
                 lw=1, label=lab if fam == "m77_seal" else None)
axb.axhline(95, color=REF, lw=0.6, ls=":")
axb.text(1, 97, "excluded at 95%", fontsize=8, color=REF, va="bottom")
axb.set_xlabel("Legends with a site-specific name (%)")
axb.set_ylabel("Replicates above observed gap (%)")
axb.set_ylim(0, 108)
axb.set_xlim(0, 51)
axb.set_title("B. Planted names", loc="left")
axb.legend(loc="lower right", handlelength=1.6)

# Panel C: diffuse effects
kinds = [("variants", "local variants", INDUS), ("shift", "frequency shift", "#9a9a9a")]
D = rev["diffuse"]
for fam, _, ls in POOLS:
    for kind, lab, col in kinds:
        pts = sorted((v["share"], v["power"]) for v in D.values()
                     if v["family"] == fam and v["kind"] == kind)
        axc.plot([p[0] * 100 for p in pts], [p[1] * 100 for p in pts], ls=ls, color=col,
                 marker="o", ms=3, lw=1, label=lab if fam == "m77_seal" else None)
axc.axhline(80, color=REF, lw=0.6, ls=":")
axc.set_xlabel("Harappa tokens altered (%)")
axc.set_ylabel("Draws detected (%)")
axc.set_ylim(0, 105)
axc.set_xlim(0, 52)
axc.set_title("C. Diffuse differences", loc="left")
axc.legend(loc="lower right", handlelength=1.6)

# Fourth cell: the key for line style (pool), shared by all three panels
axk.axis("off")
for fam, lab, ls in POOLS:
    axk.plot([], [], ls=ls, color="black", lw=1, label=lab)
axk.legend(loc="center", title="Pool (all panels)", handlelength=2.4)

fig.tight_layout(w_pad=1.2, h_pad=1.2)
save(fig, "fig3_power")
