"""Script-drawn pools for the claims stage (prereg meaning_calibration.md 'Claims', v2 seeds).
- eligible = heads eligible in every v2 draw
- A's pool: 60 of them (or all if fewer than 60), class mix kept (stratified by tclass, seeded)
- writes claims_input/A_pool.json (head + class), A_inventory.txt (all tokens, sorted, no counts),
  opaque.json (token -> opaque id; random, seeded), B_inventory.json (opaque id, class, syllable length)
Run after kill2 passes: .venv/bin/python -I experiments/meaning_calibration/pool.py
"""
import json, random, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fcore as F    # noqa: E402
import fcore2 as G   # noqa: E402
F.SEED0 = G.SEED0

OUT = HERE / "claims_input"


def syl(t):
    return len(t.split("-")) if F.tclass(t) == "word" else 1


def main():
    docs = F.LB.documents()
    every = None
    for k in range(F.NDRAW):
        d, h = F.draw(k, docs)
        e = F.eligible(F.Side(d), F.Side(h))
        every = e if every is None else every & e
    every = sorted(every)
    rng = random.Random(G.SEED0 + 777)
    by = {}
    for h in every: by.setdefault(F.tclass(h), []).append(h)
    n = min(60, len(every))
    pool = []
    for c, hs in sorted(by.items()):
        take = round(n * len(hs) / len(every))
        pool += rng.sample(hs, min(take, len(hs)))
    rest = [h for h in every if h not in pool]
    while len(pool) < n and rest: pool.append(rest.pop(rng.randrange(len(rest))))
    pool = sorted(pool)
    inv = sorted({s for d in docs for s in d["seq"] if s != "#"})
    ids = list(range(1, len(inv) + 1)); rng.shuffle(ids)
    opaque = {t: f"T{i:04d}" for t, i in zip(inv, ids)}
    OUT.mkdir(exist_ok=True)
    json.dump(dict(eligible_every_draw=every, A_pool=[dict(head=h, cls=F.tclass(h)) for h in pool],
                   decoy_pool_initial=[h for h in every if h not in pool]), open(OUT / "pools.json", "w"), indent=1, ensure_ascii=False)
    json.dump([dict(head=h, cls=F.tclass(h)) for h in pool], open(OUT / "A_pool.json", "w"), indent=1, ensure_ascii=False)
    open(OUT / "A_inventory.txt", "w").write("\n".join(inv) + "\n")
    json.dump(opaque, open(OUT / "opaque.json", "w"), indent=0, ensure_ascii=False)
    json.dump(sorted([dict(id=opaque[t], cls=F.tclass(t), syllables=syl(t)) for t in inv], key=lambda x: x["id"]),
              open(OUT / "B_inventory.json", "w"), indent=0)
    print(len(every), Counter(F.tclass(h) for h in every), len(pool), Counter(F.tclass(h) for h in pool), len(inv))


if __name__ == "__main__":
    main()
