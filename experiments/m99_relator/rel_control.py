"""Known-answer control (board #42). Ur III and Old Babylonian seal legends, word level,
thinned to the Indus held-out configuration. Must flag dumu ('son of') with power >= 0.8
in BOTH corpora and must not flag title words (pooled false-flag rate <= 0.10).
Resumable: appends to out/control.jsonl.
Run: board/run.sh .venv/bin/python -I experiments/m99_relator/rel_control.py
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rel_lib as R  # noqa: E402

ROOT = HERE.parents[1]
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

N_POOL = 1285      # break-free distinct consensus texts (dev + held-out)
N_HOST = 314       # held-out break-free distinct texts
TARGET_OCC = 49    # mid-text M99 occurrences among held-out hosts
REPS = 100
N_SHUF = 100
TITLES = {
    "ur3": ["dub-sar", "ensi2", "lugal", "ugula", "nu-banda3", "sagi", "szabra", "sukkal",
            "sipa", "gudu4", "muhaldim", "aga3-us2"],
    "ob": ["dub-sar", "lugal", "ensi2", "sanga", "ugula", "lukur", "dam-gar3", "gudu4",
           "sukkal", "gudu4-abzu", "sza13-dub-ba"],
}
EXTRA = {"ur3": ["arad2", "arad2-zu"], "ob": ["arad", "arad2", "u3"]}


def load(name):
    f = ROOT / "experiments/genre_alignment/data" / f"seals_{name}.jsonl"
    return list(dict.fromkeys(tuple(w for line in json.loads(x)["lines"] for w in line)
                              for x in open(f)))


def one(D, corpus, rep, harsh):
    rng = random.Random(1000 * rep + (7 if harsh else 0) + (0 if corpus == "ur3" else 500000))
    pool = rng.sample(D, N_POOL)
    hosts = rng.sample(range(N_POOL), N_HOST)
    if harsh:  # N_HOST hosts with <= TARGET_OCC mid dumu: dumu-bearing legends until the
        # count is reached, then dumu-free legends to fill (M99 is on ~15% of Indus hosts)
        order = list(range(N_POOL))
        rng.shuffle(order)
        keep, cnt = [], 0
        for i in order:
            if len(keep) >= N_HOST:
                break
            t = pool[i]
            c = sum(1 for j in range(1, len(t) - 1) if t[j] == "dumu")
            if c and cnt + c > TARGET_OCC:
                continue
            cnt += c
            keep.append(i)
        hosts = keep
    targets = ["dumu"] + TITLES[corpus] + EXTRA[corpus]
    res = R.run_test(pool, hosts, targets, n_shuffle=N_SHUF, seed=rep)
    row = {"corpus": corpus, "rep": rep, "harsh": harsh, "n_hosts": res["n_hosts"],
           "n_candidates": res["n_candidates"]}
    for t in targets:
        r = res[t]
        row[t] = {k: r.get(k) for k in ("n_occ", "d2", "a", "pct_d2", "pct_a", "n_matched",
                                        "p_shuffle", "flag")}
    return row


def main():
    path = OUT / "control.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            r = json.loads(l)
            done.add((r["corpus"], r["rep"], r["harsh"]))
    with open(path, "a") as fh:
        for corpus in ("ur3", "ob"):
            D = load(corpus)
            for harsh in (True, False):
                reps = REPS if harsh else 30
                for rep in range(reps):
                    if (corpus, rep, harsh) in done:
                        continue
                    fh.write(json.dumps(one(D, corpus, rep, harsh)) + "\n")
                    fh.flush()
    rows = [json.loads(l) for l in open(path)]
    summary = {}
    for corpus in ("ur3", "ob"):
        for harsh in (True, False):
            rr = [r for r in rows if r["corpus"] == corpus and r["harsh"] == harsh]
            if not rr:
                continue
            key = f"{corpus}_{'harsh' if harsh else 'natural'}"
            tf = [r[t]["flag"] for r in rr for t in TITLES[corpus] if r[t].get("pct_d2") is not None]
            per_title = {t: [sum(r[t]["flag"] for r in rr), sum(r[t].get("pct_d2") is not None for r in rr)]
                         for t in TITLES[corpus]}
            summary[key] = {
                "reps": len(rr),
                "power_dumu": sum(r["dumu"]["flag"] for r in rr) / len(rr),
                "dumu_pct_d2_mean": sum((r["dumu"]["pct_d2"] or 0) for r in rr) / len(rr),
                "dumu_n_occ_mean": sum(r["dumu"]["n_occ"] for r in rr) / len(rr),
                "dumu_pct_a_ge95": sum((r["dumu"]["pct_a"] or 0) >= 0.95 for r in rr) / len(rr),
                "title_evals": len(tf),
                "title_false_flag": (sum(tf) / len(tf)) if tf else None,
                "per_title_flag_of_evaluable": per_title,
                "extra_flag": {t: sum(r[t]["flag"] for r in rr) / len(rr) for t in EXTRA[corpus]},
                "n_candidates_mean": sum(r["n_candidates"] for r in rr) / len(rr),
            }
    gate = all(summary[f"{c}_harsh"]["power_dumu"] >= 0.8 for c in ("ur3", "ob")) and all(
        (summary[f"{c}_harsh"]["title_false_flag"] or 0) <= 0.10 for c in ("ur3", "ob"))
    summary["gate_pass"] = gate
    json.dump(summary, open(OUT / "control.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
