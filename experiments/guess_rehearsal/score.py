"""Score blind guesses against the sealed key. Run after all guess files exist:
.venv/bin/python -I experiments/guess_rehearsal/score.py
"""
import json, random
from pathlib import Path
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
key = json.load(open(HERE / "sealed/key.json"))
ids = sorted(key)
rng = random.Random(7)
res = {}
for cond in "ABC":
    f = HERE / f"guesses/{cond}.json"
    if not f.exists():
        continue
    g = json.load(open(f))
    rows = [(i, g[i]["class"], key[i]["class"], bool(g[i].get("recognised")), float(g[i].get("confidence", 0)),
             g[i].get("gloss", "")) for i in ids]
    def acc(rs):
        return (sum(a == b for _, a, b, *_ in rs), len(rs))
    k_all, n_all = acc(rows)
    clean = [r for r in rows if not r[3]]
    k_c, n_c = acc(clean)
    # permutation: shuffle guessed classes across signs (keeps the guesser's class mix)
    guessed = [r[1] for r in rows]
    truth = [r[2] for r in rows]
    obs = sum(a == b for a, b in zip(guessed, truth))
    ge = 0
    for _ in range(20000):
        rng.shuffle(guessed)
        ge += sum(a == b for a, b in zip(guessed, truth)) >= obs
    hi = [r for r in rows if r[4] >= 0.6]
    k_h, n_h = acc(hi)
    res[cond] = {
        "class_acc_all": [k_all, n_all, round(k_all / n_all, 3)],
        "class_acc_not_recognised": [k_c, n_c, round(k_c / n_c, 3) if n_c else None],
        "binom_p_not_recognised_vs_0.125": binomtest(k_c, n_c, 0.125, alternative="greater").pvalue if n_c else None,
        "perm_p_all": (ge + 1) / 20001,
        "n_recognised": sum(r[3] for r in rows),
        "high_conf_acc": [k_h, n_h],
        "per_sign": [{"id": r[0], "guess": r[1], "truth": r[2], "sign": key[r[0]]["sign"], "recognised": r[3],
                      "conf": r[4], "gloss": r[5]} for r in rows],
    }
    print(cond, {k: v for k, v in res[cond].items() if k != "per_sign"})
json.dump(res, open(HERE / "results.json", "w"), indent=1)
