"""Exploratory follow-up (NOT pre-registered): fish precede their non-fish partner in 2-sign cores?

Found on pooled dev+held-out after the registered run: in 2-sign cores with exactly one plain fish, fish is first
in 75/107 (0.70); removing fish pairs makes HFI_prod 0.51.  Independent check on ICIT texts from sites absent
from M77 (bridged W->M), using a crude adjacency definition that needs no parse: adjacent pairs (a, b) with
exactly one plain fish and the other sign a non-fish core sign (>= 5 dev core occurrences, not a numeral).
The same crude definition is first applied to M77 dev and held-out to show it reproduces the parse-based number.
"""
import sys, json
from collections import Counter
import numpy as np
from scipy.stats import binomtest
sys.path.insert(0, __import__("os").path.dirname(__file__))
import cs_data as D
import s2_classes as S2
from corpus.load import icit_texts, distinct, dev_heldout, runs
sys.path.insert(0, str(D.ROOT / "experiments" / "functional_reading"))
import fr  # noqa  (bridge only)

PLAIN = {"M59", "M65", "M67", "M70", "M72", "M75", "M62"}
inc, occ = D.indus_types("dev")
B = S2.build(occ)
CORE = {s for s in B["signs"] if s not in D.FISH and s not in S2.STROKES}
M77_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}


def count(seqs):
    first = n = 0
    for seq in seqs:
        for r in runs(seq):
            for a, b in zip(r, r[1:]):
                if (a in PLAIN) != (b in PLAIN) and ((a in CORE) or (b in CORE)):
                    n += 1; first += a in PLAIN
    return dict(n=n, fish_first=first, share=round(first / n, 3) if n else None,
                p_two_sided=float(binomtest(first, n, 0.5).pvalue) if n else None)


dev, ho = dev_heldout(version=2)
res = {"m77_dev_crude": count([t["seq"] for t in dev]), "m77_heldout_crude": count([t["seq"] for t in ho])}
new = []
seen = set()
for t in icit_texts():
    k = " ".join(t["seq"])
    if k in seen or t["site"] in fr.FOREIGN_SITES or t["site"] in M77_SITES_ICIT or t["site"] == "Unknown":
        continue
    seen.add(k)
    new.append(fr.bridge_seq(t["seq"]))
res["icit_new_sites"] = count(new)
res["icit_new_sites"]["n_texts"] = len(new)
print(json.dumps(res, indent=1))
json.dump(res, open(D.HERE / "e4_fish_order_icit.json", "w"), indent=1)
