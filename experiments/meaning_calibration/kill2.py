"""meaning_calibration v2 kill test (prereg docs/prereg/meaning_calibration_v2.md). Before any claim file exists.
Run: nice -n 20 .venv/bin/python -I experiments/meaning_calibration/kill2.py
"""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fcore as F    # noqa: E402
import fcore2 as G   # noqa: E402
import p34           # noqa: E402

N_PLANT = 40
N_FA = 200
F.SEED0 = G.SEED0    # v2 seeds for the draws


def run_plant(dev_t, held_t, h, P, rng):
    dt, ok1 = G.plant_set(dev_t, h, P, rng); ht, ok2 = G.plant_set(held_t, h, P, rng)
    if not (ok1 and ok2): return None
    D, H = F.Side(dt), F.Side(ht)
    v, r = G.verdict2(D, H, h, P[0], tuple(P[1:]), {})
    rd = r[0] if r else None
    return dict(verdict=v, n_dev=F.Side(dev_t).n(h), n_null_dev=rd["n_null"] if rd else None,
                n_null_held=r[1]["n_null"] if r and r[1] else None)


def job(k):
    docs = F.LB.documents()
    dev_t, held_t = F.draw(k, docs)
    dev, held = F.Side(dev_t), F.Side(held_t)
    elig = sorted(F.eligible(dev, held))
    rng = random.Random(G.SEED0 * 10 + k)
    pool = sorted(s for s in dev.cnt if s != "#" and dev.cnt[s] >= 3)
    pairs, singles = [], []
    for h in rng.sample(elig, min(N_PLANT, len(elig))):
        others = [s for s in pool if s != h]
        P = rng.sample(others, 1 + rng.randint(1, 2))
        r = run_plant(dev_t, held_t, h, P, rng)
        pairs.append(dict(head=h, P=P, cls=F.tclass(h), bin=F.bin_of(dev.n(h)), skipped=r is None, **(r or {})))
        x = rng.choice(others)
        r1 = run_plant(dev_t, held_t, h, [x], rng)
        singles.append(dict(head=h, P=[x], bin=F.bin_of(dev.n(h)), skipped=r1 is None, **(r1 or {})))
    srng = random.Random(G.SEED0 * 100 + k)
    SD, SH = F.Side(p34.shuffle_within(dev_t, srng)), F.Side(p34.shuffle_within(held_t, srng))
    fa = []
    for _ in range(N_FA):
        h = rng.choice(elig); P = rng.sample([s for s in pool if s != h], rng.randint(1, 3))
        v, _r = G.verdict2(SD, SH, h, P[0], tuple(P[1:]), {})
        fa.append(dict(head=h, P=P, verdict=v))
    return dict(k=k, n_eligible=len(elig), eligible=elig, pairs=pairs, singles=singles, false_alarm=fa)


def summ(rows):
    R = [r for r in rows if not r["skipped"]]
    T = [r for r in R if r["verdict"] != "U-resolution"]
    return dict(n=len(R), skipped=len(rows) - len(R), testable=len(T), coverage=round(len(T) / len(R), 3) if R else None,
                power=round(sum(r["verdict"] == "S" for r in T) / len(T), 3) if T else None)


def main():
    with Pool(4) as pool:
        draws = pool.map(job, range(F.NDRAW))
    pairs = [p for d in draws for p in d["pairs"]]; singles = [p for d in draws for p in d["singles"]]
    per_draw_cov = [summ(d["pairs"])["coverage"] for d in draws]
    PS = summ(pairs)
    by_bin = {}
    for b in sorted({p["bin"] for p in pairs}):
        by_bin[b] = summ([p for p in pairs if p["bin"] == b])
    FA = [f for d in draws for f in d["false_alarm"]]
    fa = sum(f["verdict"] == "S" for f in FA) / len(FA)
    passed = all(c is not None and c >= 0.5 for c in per_draw_cov) and PS["power"] is not None and PS["power"] >= 0.8 and fa <= 0.05
    res = dict(pairs=PS, coverage_per_draw=per_draw_cov, power_by_bin=by_bin, singles=summ(singles),
               false_alarm=round(fa, 4), false_alarm_verdicts=dict(Counter(f["verdict"] for f in FA)), passed=passed,
               n_eligible=[d["n_eligible"] for d in draws])
    json.dump(res, open(HERE / "kill2.json", "w"), indent=1, ensure_ascii=False)
    json.dump(draws, open(HERE / "kill2_draws.json", "w"), ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
