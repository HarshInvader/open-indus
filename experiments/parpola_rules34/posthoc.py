"""POST HOC, exploratory (not pre-registered, not a pass route).
The pre-registered near-copy collapse (fish_tick_closer rule, union-find) chains 571 dev texts
into one family. Here: greedy de-duplication WITHOUT chaining -- a text is dropped only if it is
close (same rule) to a text already kept; texts are visited longest first.
Also: how many distinct left neighbours and sites carry M403 M87.
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fish_tick_closer"))
import ftc  # noqa: E402
import p34 as P  # noqa: E402


def greedy(texts_raw):
    T = P.L.distinct(texts_raw)
    T.sort(key=lambda t: (-len([s for s in t["seq"] if s not in "|#"]), " ".join(t["seq"])))
    kept, ks = [], []
    for t in T:
        sg = [s for s in t["seq"] if s not in ("|", "#")]
        if sg and any(ftc._close(sg, k) for k in ks):
            continue
        kept.append(t); ks.append(sg)
    return kept


out = {}
for split in ("dev", "held"):
    dev, ho = P.L.dev_heldout(version=2)
    raw = dev if split == "dev" else ho
    g = P.prep(greedy(raw))
    r4 = P.rule4(g, "M403", "M87", ("M51", "M52"), P.EXCLUDE["M"])
    r3 = P.rule3(g, "M87", "M59", P.EXCLUDE["M"])
    left = Counter()
    for t in P.prep(raw):
        for i in range(len(t) - 1):
            if t[i] == "M403" and t[i + 1] == "M87":
                left["^" if i == 0 else t[i - 1]] += 1
    out[split] = dict(n_texts=len(g),
                      rule4={k: r4[k] for k in ("n_with_next", "obs_share", "null_q95", "null_q99", "p")},
                      rule3={k: r3[k] for k in ("obs", "null_median", "null_q95", "p")},
                      distinct_left_neighbours_of_M403_M87=len(left))
    print(split, out[split], flush=True)
P.save("posthoc_greedy_dedup", out)
