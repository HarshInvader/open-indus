"""Kill test for meaning_calibration (prereg docs/prereg/meaning_calibration.md). Runs before any claim file exists.
F power (planted partners at ceil(0.4 n), dev + held-out rule), F false alarm (random heads and partner sets on
within-text shuffled draws), eligibility census, and the E power report (full corpus, single stage).
Run: nice -n 20 .venv/bin/python -I experiments/meaning_calibration/kill.py
"""
import json, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
from scipy.stats import poisson

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fcore as F  # noqa: E402
import p34         # noqa: E402

N_PLANT = 40
N_FA = 200


def job(k):
    docs = F.LB.documents()
    dev_t, held_t = F.draw(k, docs)
    dev, held = F.Side(dev_t), F.Side(held_t)
    elig = sorted(F.eligible(dev, held))
    rng = random.Random(F.SEED0 * 10 + k)
    pool = sorted(s for s in dev.cnt if s != "#" and dev.cnt[s] >= 3)
    # --- power
    planted = []
    for h in rng.sample(elig, min(N_PLANT, len(elig))):
        x = rng.choice([s for s in pool if s != h])
        dt, ok1 = F.plant(dev_t, h, x, rng); ht, ok2 = F.plant(held_t, h, x, rng)
        if not (ok1 and ok2):
            planted.append(dict(head=h, partner=x, skipped=True)); continue
        D, H = F.Side(dt), F.Side(ht)
        rd = F.f_test(D, h, x, ()); rh = F.f_test(H, h, x, ())
        surv = bool(rd and rd["obs"] >= F.SHARE and rd["p"] <= 0.01 and rh and rh["p"] <= 0.05)
        planted.append(dict(head=h, partner=x, cls=F.tclass(h), n_dev=dev.n(h), bin=F.bin_of(dev.n(h)), skipped=False,
                            survives=surv, dev=rd, held=rh))
    # --- false alarm on within-text shuffled draws
    srng = random.Random(F.SEED0 * 100 + k)
    SD, SH = F.Side(p34.shuffle_within(dev_t, srng)), F.Side(p34.shuffle_within(held_t, srng))
    fa = []
    for _ in range(N_FA):
        h = rng.choice(elig); size = rng.randint(1, 3)
        P = rng.sample([s for s in pool if s != h], size)
        v, _r = F.verdict(SD, SH, h, P[0], tuple(P[1:]), {})
        fa.append(dict(head=h, P=P, verdict=v))
    return dict(k=k, n_dev=len(dev_t), n_held=len(held_t), eligible=elig, planted=planted, false_alarm=fa)


def e_report():
    docs = F.LB.documents()
    by_site = defaultdict(list)
    for d in docs: by_site[d["site"]].append(d)
    toks = Counter(s for d in docs for s in set(d["seq"]) if s != "#")
    toks = [s for s, c in toks.items() if c >= 5]
    out = {}
    for name, cls in (("sealing", {"sealing"}), ("sealing+vase", {"sealing", "vase"})):
        res = []
        for s in toks:
            # exact null mean of within-site label permutation: sum over sites of (docs with s) x (class share)
            mu = sum(sum(s in d["seq"] for d in D) * sum(d["cls"] in cls for d in D) / len(D) for D in by_site.values())
            q99 = poisson.ppf(0.99, mu) if mu > 0 else 0
            pw = float(1 - poisson.cdf(q99 - 1, 2 * mu)) if q99 >= 1 else None
            res.append((s, round(mu, 3), pw))
        powered = [r for r in res if r[2] is not None and r[2] >= 0.8]
        out[name] = dict(n_tokens=len(res), n_powered=len(powered), powered=powered,
                         n_class_docs=sum(d["cls"] in cls for d in docs))
    return out


def main():
    with Pool(4) as pool:
        draws = pool.map(job, range(F.NDRAW))
    P = [p for d in draws for p in d["planted"] if not p["skipped"]]
    skipped = sum(p["skipped"] for d in draws for p in d["planted"])
    power = sum(p["survives"] for p in P) / len(P)
    by_bin = {b: dict(n=len(v), power=round(sum(p["survives"] for p in v) / len(v), 3)) for b in sorted({p["bin"] for p in P})
              for v in [[p for p in P if p["bin"] == b]]}
    by_cls = {c: dict(n=len(v), power=round(sum(p["survives"] for p in v) / len(v), 3)) for c in sorted({p["cls"] for p in P})
              for v in [[p for p in P if p["cls"] == c]]}
    FA = [f for d in draws for f in d["false_alarm"]]
    fa_rate = sum(f["verdict"] == "S" for f in FA) / len(FA)
    every = set(draws[0]["eligible"])
    for d in draws[1:]: every &= set(d["eligible"])
    every = sorted(every)
    passed = fa_rate <= 0.05 and power >= 0.8
    res = dict(F=dict(power=round(power, 3), n_planted=len(P), skipped=skipped, power_by_bin=by_bin, power_by_class=by_cls,
                      false_alarm=round(fa_rate, 4), n_false_alarm=len(FA), passed=passed),
               eligible_every_draw=dict(n=len(every), by_class=dict(Counter(F.tclass(h) for h in every)), heads=every),
               draws=[dict(k=d["k"], n_dev=d["n_dev"], n_held=d["n_held"], n_eligible=len(d["eligible"])) for d in draws],
               E_power_report=e_report())
    json.dump(res, open(HERE / "kill.json", "w"), indent=1, ensure_ascii=False)
    json.dump(draws, open(HERE / "kill_draws.json", "w"), ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "E_power_report"}, indent=1, ensure_ascii=False)[:3000])
    print({k: dict(n_tokens=v["n_tokens"], n_powered=v["n_powered"], n_class_docs=v["n_class_docs"]) for k, v in res["E_power_report"].items()})


if __name__ == "__main__":
    main()
