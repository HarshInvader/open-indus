"""Pre-registered tests H1-H4 (docs/prereg/elamite_bridge.md).
Run: .venv/bin/python experiments/elamite_bridge/eb_test.py
"""
import json, random, re, sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from corpus.load import icit_texts, m77_texts, distinct, runs as split_runs
from experiments.elamite_bridge.eb_core import (ROOT, diversity_residuals, auc, set_vs_rest_perm,
                                                 freq_strata)

FIG9 = ["850", "502", "455", "370", "371", "012", "058", "360", "440", "330", "323", "400", "402",
        "684", "167", "625", "899", "900", "913", "335", "032", "615", "794", "831", "482"]
UNIVERSAL = {"850", "625", "899", "900", "913", "032"}
KEY = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/fuls2024-le-indus-key.json"))["key"]
W = lambda n: "W" + n


def set_test(D, tok, test, label, seed):
    st = freq_strata(tok, list(D))
    test = [s for s in test if s in D]
    obs, p, n = set_vs_rest_perm(D, test, n_perm=20000, seed=seed, strata=st)
    rest = [D[s] for s in D if s not in test]
    return {"label": label, "signs": test, "n": n, "mean_D": obs,
            "mean_D_all": float(np.mean(list(D.values()))), "p_one_sided": p,
            "auc_vs_rest": auc([D[s] for s in test], rest),
            "per_sign": {s: round(D[s], 3) for s in test}}


def le_pairs():
    d = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/linear-elamite-corpus-hled.json"))
    pairs = set()
    for x in d:
        t = x.get("translit", "") or ""
        t = re.sub(r"[\[\]⸢⸣{}()!?]", "", t)
        for line in t.split("||"):
            for seg in line.split("|"):
                for word in seg.split():
                    sy = [s for s in re.split(r"[-⁓+]", word)]
                    for a, b in zip(sy, sy[1:]):
                        if not a or not b or "X" in a + b or "…" in a + b or "." in a + b: continue
                        pairs.add((a, b))
    return pairs


def key_test(runs_, pairs, n_perm=20000, seed=7):
    signs = sorted(KEY); vals = [KEY[s] for s in signs]
    adj = Counter()
    for r in runs_:
        for a, b in zip(r, r[1:]):
            if a[1:] in KEY and b[1:] in KEY: adj[(a[1:], b[1:])] += 1

    def score(m):
        return sum(c for (a, b), c in adj.items() if (m[a], m[b]) in pairs)
    obs = score(KEY)
    rng = random.Random(seed); null = []
    for _ in range(n_perm):
        v = vals[:]; rng.shuffle(v); null.append(score(dict(zip(signs, v))))
    null = np.array(null)
    return {"mapped_pair_tokens": int(sum(adj.values())), "mapped_pair_types": len(adj),
            "pairs": {f"{a}-{b}": c for (a, b), c in adj.most_common()},
            "observed_attested": int(obs), "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "p_one_sided": float(((null >= obs).sum() + 1) / (n_perm + 1)),
            "n_le_pair_types": len(pairs)}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); out = [0] * len(ps); m = len(ps); prev = 0
    for rank, i in enumerate(order):
        prev = max(prev, min(1, (m - rank) * ps[i])); out[i] = prev
    return out


if __name__ == "__main__":
    out = {}
    icit_runs = [r for t in distinct(icit_texts()) for r in split_runs(t["seq"])]
    D, tok = diversity_residuals(icit_runs)
    C = [W(n) for n in FIG9 if n not in UNIVERSAL]
    out["H1"] = set_test(D, tok, C, "complex look-alikes (ICIT)", seed=11)
    out["H2"] = set_test(D, tok, [W(n) for n in FIG9], "all look-alikes (ICIT)", seed=12)
    # H3: M77 replication through the bridge
    br = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    m_of = {}
    for n in FIG9:
        if n in UNIVERSAL: continue
        e = br.get(str(int(n)))
        if e and len(e["M"]) == 1: m_of[n] = "M%d" % e["M"][0]
    cnt = Counter(m_of.values())
    m_set = sorted({m for n, m in m_of.items() if cnt[m] == 1})
    m77_runs = [r for t in distinct(m77_texts()) for r in split_runs(t["seq"])]
    Dm, tokm = diversity_residuals(m77_runs)
    out["H3"] = set_test(Dm, tokm, m_set, "complex look-alikes bridged to M77", seed=13)
    out["H3"]["bridge"] = m_of
    out["H4"] = key_test(icit_runs, le_pairs())
    adj = holm([out["H1"]["p_one_sided"], out["H4"]["p_one_sided"]])
    out["H1"]["p_holm"], out["H4"]["p_holm"] = adj
    out["verdict"] = {"H1": "supported" if adj[0] < 0.05 else "not supported",
                      "H4": "supported" if adj[1] < 0.05 else "not supported"}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    json.dump(out, open(ROOT / "experiments/elamite_bridge/test_results.json", "w"), indent=1, ensure_ascii=False)
