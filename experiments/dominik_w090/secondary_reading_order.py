"""SECONDARY (not the prereg primary): repeat T2/T3 in reading order, because the prereg's
denominator rule picked listing order, yet only reading order shows the claimed contrast."""
import json, random, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1]))
from run import icit_runs, contrast, zero_cells, within_text_shuffle  # noqa
from corpus.load import icit_texts, distinct, runs, dev_heldout  # noqa
rng = random.Random(191)
icit = distinct(icit_texts())
rs = icit_runs(icit, False)
dev, ho = dev_heldout(version=2)
out = {}
for nm, tx in [("m77_heldout", ho), ("m77_dev", dev)]:
    out[nm] = contrast([r for t in tx for r in runs(t["seq"])], A="M211", B="M342", C="M1", W33="M89")
big = {"Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro"}
out["icit_other_sites"] = contrast(icit_runs([t for t in icit if t["site"] not in big], False))
out["icit_harappa_only"] = contrast(icit_runs([t for t in icit if t["site"] == "Harappa"], False))
out["icit_mohenjo_only"] = contrast(icit_runs([t for t in icit if t["site"] == "Mohenjo-daro"], False))
# what does M342 precede in M77 reading order, vs ICIT W740?
nx = Counter(r[i+1] for t in dev + ho for r in runs(t["seq"]) for i in range(len(r)-1) if r[i] == "M342")
out["m77_followers_of_M342_top"] = nx.most_common(8)
nxi = Counter(r[i+1] for r in rs for i in range(len(r)-1) if r[i] == "W740")
out["icit_followers_of_W740_top"] = nxi.most_common(8)
z, cand, ps = zero_cells(rs)
pc = out_p = contrast(rs)["fisher_p_less"]
nl = [zero_cells(rs, rng, "label")[0] for _ in range(300)]
nw = [zero_cells(within_text_shuffle(rs, rng))[0] for _ in range(200)]
out["T3_reading"] = {"zero_cells_observed": z, "candidate_triples": cand, "rank_of_claim_p": int(sum(p <= pc for p in ps)),
    "n_triples": len(ps), "n_triples_p_le_0.001": int(sum(p <= 0.001 for p in ps)), "label_null_mean": sum(nl)/len(nl),
    "within_text_null_mean": sum(nw)/len(nw), "within_text_p_ge": (1 + sum(x >= z for x in nw)) / 201}
json.dump(out, open(HERE / "secondary_reading_order.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
