"""Starter task S6: pin down the round-seal q-value.

Two checks on experiments/ledger/v2_reruns.py, the script behind ledger row lr_gulf (README #4):

  1. Hash seed.  Run it under PYTHONHASHSEED = 0..19 and compare the outputs byte for byte.
     They must be identical: the result may not depend on Python's string hashing.
  2. Random seed.  Run it under 20 values of --seed and report the range of the Gulf p and of its
     q across all tests. This is the Monte Carlo noise that is left: p rests on 20,000 matched draws
     and a tail of a few draws. q is recomputed over the current docs/test_ledger.csv with the rules
     of merge_rows.py; the ledger file is read, never written.

Run from the repo root:  .venv/bin/python -P -s experiments/ledger/seed_sweep.py [--full]
Do NOT start it with -I: isolated mode ignores PYTHONHASHSEED, so check 1 could not set the seed.
Block D (300 model fits, about 8 min a run) is skipped unless --full; it shares no generator with F.
Writes experiments/ledger/seed_sweep.json. At most 2 worker processes.
"""
import copy, csv, json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import merge_rows  # noqa: E402

FULL = "--full" in sys.argv
DEFAULT_SEED = 20261114
HASH_SEEDS = list(range(20))
RNG_SEEDS = [DEFAULT_SEED] + list(range(1, 20))


def run(tmp, tag, hash_seed, seed):
    out = Path(tmp) / f"{tag}.json"
    cmd = [sys.executable, "-P", "-s", str(HERE / "v2_reruns.py"), "--out", str(out), "--seed", str(seed)]
    if not FULL:
        cmd += ["--skip", "D"]
    env = dict(os.environ, PYTHONHASHSEED=str(hash_seed))
    subprocess.run(cmd, cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)
    return out.read_bytes()


def q_all(rows, p):
    rows = copy.deepcopy(rows)
    for r in rows:
        if r["id"] == "lr_gulf":
            r["p_value"] = p
    merge_rows.correct(rows)
    return next(r for r in rows if r["id"] == "lr_gulf")


def main():
    ledger = list(csv.DictReader(open(merge_rows.LEDGER, newline="")))
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(2) as ex:
        hs = list(ex.map(lambda h: run(tmp, f"h{h}", h, DEFAULT_SEED), HASH_SEEDS))
        rs = list(ex.map(lambda s: run(tmp, f"s{s}", 0, s), RNG_SEEDS))
    same = len(set(hs))
    res = dict(block_D_included=FULL,
               hash_seed=dict(seeds=HASH_SEEDS, distinct_outputs=same, identical=same == 1), rng_seed=[])
    print(f"1. hash seeds {HASH_SEEDS[0]}..{HASH_SEEDS[-1]}: {same} distinct output(s) -> "
          f"{'IDENTICAL' if same == 1 else 'DIFFER'}")
    print("2. random seeds (hash seed 0):\n   seed       gulf p     q_all   q_global   lexicon-null p")
    for s, b in zip(RNG_SEEDS, rs):
        j = json.loads(b); p = j["F_gulf_round"]["p"]; r = q_all(ledger, p)
        row = dict(seed=s, gulf_p=p, q_all=float(r["q_all"]), q_global=float(r["q_global"]),
                   lexicon_null_p=j["A_functional_reading"]["v2"]["lexicon_null_p"])
        res["rng_seed"].append(row)
        print(f"   {s:<9d} {p:.5f}   {row['q_all']:.3f}    {row['q_global']:.4f}    {row['lexicon_null_p']:.4f}")
    for k in ("gulf_p", "q_all", "q_global", "lexicon_null_p"):
        v = [r[k] for r in res["rng_seed"]]
        res[f"{k}_range"] = [min(v), max(v)]
        print(f"   {k}: {min(v):.5g} to {max(v):.5g}")
    res["default_seed"] = res["rng_seed"][0]
    json.dump(res, open(HERE / "seed_sweep.json", "w"), indent=1)
    sys.exit(0 if same == 1 else 1)


if __name__ == "__main__":
    main()
