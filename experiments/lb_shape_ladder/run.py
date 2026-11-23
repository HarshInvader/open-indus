"""Shape ladder for dictionary fit on Linear B (prereg docs/prereg/lb_shape_ladder.md).
Run: .venv/bin/python -I experiments/lb_shape_ladder/run.py kill   # R3, subsample 0
     .venv/bin/python -I experiments/lb_shape_ladder/run.py full   # 20 subsamples x 4 rungs (only if kill passes)
     .venv/bin/python -I experiments/lb_shape_ladder/run.py time   # speed check on a shuffled key, prints no score
"""
import json, sys, random, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/lb_certify"))
import run as base                                   # hashed lb_certify code: data, lexicon, true values

SEED = 20261124
MAXW = base.MAXW
LMIN = 4                                             # smallest L with q-free lexicon density <= 25% of 9^L (0.177)
NPERM, ITERS, RESTARTS, NPART, NSUB = 1000, 3000, 3, 40, 20
RUNGS = {"R0": ("chunk", 0.74), "R1": ("chunk", 1.0), "R2": ("line", 1.0), "R3": ("word", 1.0)}


# ------------------------------------------------------------------ data
def lb_lines():
    """[(line id, [word, ...])], word = [syllable sign, ...]; syllabic words only (as lb_certify)."""
    out = []
    for l in open(ROOT / "sources/paragorth_Indus-/data/codelib/linear_b.jsonl"):
        r = json.loads(l); ws = []
        for w in r["seq"]:
            if base.WORD.match(w):
                parts = w.split("-")
                if all(base.SYL.match(p) for p in parts):
                    ws.append(parts)
        if sum(len(w) for w in ws) >= 2:
            out.append((r["id"], ws))
    return out


def build(k, form):
    """Return dev, ho as lists of texts; a text is a list of words (lists of signs)."""
    rng_np = np.random.default_rng(SEED + 1000 * k); rng = random.Random(SEED + 1000 * k)
    lines = lb_lines(); lens = base.m77_lengths()
    flat = [(tid, [s for w in ws for s in w]) for tid, ws in lines]
    ch = base.chunk(flat, lens, rng_np)
    pick = rng_np.choice(len(ch), size=min(2300, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    T = sum(len(t) for _, t in ch)                   # token budget shared by every rung of subsample k
    if form == "chunk":
        items = [(tid, [t]) for tid, t in ch]
    else:
        order = list(range(len(lines))); rng.shuffle(order); items, n = [], 0
        for i in order:
            if n >= T:
                break
            tid, ws = lines[i]
            items.append((tid, ws if form == "word" else [[s for w in ws for s in w]])); n += sum(len(w) for w in ws)
    ids = sorted({tid for tid, _ in items}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    dev = [t for tid, t in items if tid in dev_ids]; ho = [t for tid, t in items if tid not in dev_ids]
    return dev, ho, rng


# ------------------------------------------------------------------ statistic
def ic_seg(c, lex):
    """Max consonants covered by lexicon words of >= LMIN consonants (uncovered consonants allowed)."""
    n = len(c); best = [0] * (n + 1)
    for i in range(1, n + 1):
        b = best[i - 1]
        for L in range(LMIN, min(MAXW, i) + 1):
            if tuple(c[i - L:i]) in lex and best[i - L] + L > b:
                b = best[i - L] + L
        best[i] = b
    return best[n]


class IC:
    def __init__(self, texts, lex):
        self.texts, self.lex = texts, lex
        self.by_sign = defaultdict(list)
        for i, t in enumerate(texts):
            for s in {s for w in t for s in w}:
                self.by_sign[s].append(i)

    def segs(self, t, key):
        out = []
        for w in t:                                  # word division (R3) and unkeyed signs are breaks
            cur = []
            for s in w:
                if s in key:
                    cur += key[s]
                else:
                    out.append(cur); cur = []
            out.append(cur)
        return [c for c in out if c]

    def text(self, t, key):
        sg = self.segs(t, key)
        return (sum(ic_seg(c, self.lex) for c in sg), sum(len(c) for c in sg), len(sg))

    def full(self, key):
        self.cache = [self.text(t, key) for t in self.texts]
        return self.value()

    def value(self, cache=None):
        cache = cache or self.cache
        cov = sum(x[0] for x in cache); tot = sum(x[1] for x in cache)
        return cov / tot if tot else 0.0

    def after(self, key, signs):
        idx = set()
        for s in signs:
            idx.update(self.by_sign[s])
        new = {i: self.text(self.texts[i], key) for i in idx}
        cov = tot = 0
        for i, c in enumerate(self.cache):
            c = new.get(i, c); cov += c[0]; tot += c[1]
        return (cov / tot if tot else 0.0), new

    def shape(self, key):
        sg = [c for t in self.texts for c in self.segs(t, key)]
        return dict(cons_per_seg=float(np.mean([len(c) for c in sg])), n_segs=len(sg),
                    share_cons_in_segs_ge_lmin=float(sum(len(c) for c in sg if len(c) >= LMIN) / sum(len(c) for c in sg)))


# ------------------------------------------------------------------ nulls and controls
def classes(kept, key):
    cl = defaultdict(list)
    for s in kept:
        cl[len(key[s])].append(s)
    return cl


def permute_in_class_bins(key, cl, freq, rng, size=10):
    k = dict(key)
    for ss in cl.values():
        ss = sorted(ss, key=lambda s: -freq[s])
        for i in range(0, len(ss), size):
            b = ss[i:i + size]; vals = [key[s] for s in b]; rng.shuffle(vals)
            k.update(zip(b, vals))
    return k


def shuffle_in_class(key, signs, cl_of, rng):
    k = dict(key); by = defaultdict(list)
    for s in signs:
        by[cl_of[s]].append(s)
    for ss in by.values():
        vals = [key[s] for s in ss]; rng.shuffle(vals); k.update(zip(ss, vals))
    return k


def restructure(texts, flat):
    out, i = [], 0
    for t in texts:
        nt = []
        for w in t:
            nt.append(flat[i:i + len(w)]); i += len(w)
        out.append(nt)
    return out


def unigram(texts, rng):
    toks = [s for t in texts for w in t for s in w]
    return restructure(texts, [rng.choice(toks) for _ in toks])


def markov(texts, rng):
    nxt = defaultdict(list); starts = []
    for t in texts:
        seq = [s for w in t for s in w]; starts.append(seq[0])
        for a, b in zip(seq, seq[1:]):
            nxt[a].append(b)
    flat = []
    for t in texts:
        n = sum(len(w) for w in t); s = [rng.choice(starts)]
        while len(s) < n:
            s.append(rng.choice(nxt[s[-1]]) if nxt[s[-1]] else rng.choice(starts))
        flat += s
    return restructure(texts, flat)


def fit(S, key0, kept, cl_of, iters, rng):
    key = dict(key0); cur = S.full(key)
    by = defaultdict(list)
    for s in kept:
        by[cl_of[s]].append(s)
    pools = [v for v in by.values() if len(v) >= 2]
    w = [len(v) for v in pools]
    for _ in range(iters):
        a, b = rng.sample(rng.choices(pools, weights=w)[0], 2)
        if key[a] == key[b]:
            continue
        key[a], key[b] = key[b], key[a]
        nc, new = S.after(key, [a, b])
        if nc >= cur:
            cur = nc
            for i, c in new.items():
                S.cache[i] = c
        else:
            key[a], key[b] = key[b], key[a]
    return key


# ------------------------------------------------------------------ one (subsample, rung)
LEX = None


def init():
    global LEX
    LEX = base.build_lexicon()[0]


def one(args):
    k, rung = args
    form, cov = RUNGS[rung]
    dev, ho, rng = build(k, form)
    rng = random.Random(SEED + 1000 * k + 7 * list(RUNGS).index(rung))
    freq = Counter(s for t in dev + ho for w in t for s in w)
    order = sorted(freq); rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= cov:
            break
        kept.append(s); c += freq[s]
    true = {s: base.true_value(s) for s in kept}
    cl = classes(kept, true); cl_of = {s: len(true[s]) for s in kept}
    H = IC(ho, LEX)
    t_ho = H.full(true); shape = H.shape(true)
    n1 = np.array([H.full(permute_in_class_bins(true, cl, freq, rng)) for _ in range(NPERM)])
    # control iii: unigram-shuffled held-out, true key vs its own N1
    Hs = IC(unigram(ho, rng), LEX); t_sh = Hs.full(true)
    n1s = np.array([Hs.full(permute_in_class_bins(true, cl, freq, rng)) for _ in range(NPERM)])
    # control ii: partial keys, mean of NPART draws per level
    part = {}
    for f in (0.0, 0.25, 0.5, 0.75):
        v = []
        for _ in range(NPART):
            keep = set(rng.sample(kept, int(f * len(kept))))
            v.append(H.full(shuffle_in_class(true, [s for s in kept if s not in keep], cl_of, rng)))
        part[f] = float(np.mean(v))
    part[1.0] = t_ho
    # N2: keys hill-climbed on dev-shaped corpora, swaps within consonant-count class
    n2 = defaultdict(list)
    for name, corp in (("real", dev), ("unigram", unigram(dev, rng)), ("markov", markov(dev, rng))):
        S = IC(corp, LEX)
        for _ in range(RESTARTS):
            fk = fit(S, shuffle_in_class(true, kept, cl_of, rng), kept, cl_of, ITERS, rng)
            n2[name].append(H.full(fk))
    pooled = [x for v in n2.values() for x in v]
    return dict(k=k, rung=rung, cov=cov, n_dev=len(dev), n_ho=len(ho), n_keyed=len(kept),
                tokens_ho=sum(len(w) for t in ho for w in t), shape=shape,
                true_ic=t_ho, n1_mean=float(n1.mean()), n1_p99=float(np.quantile(n1, .99)),
                refute=bool(t_ho > np.quantile(n1, .99)),
                n2={a: [float(x) for x in b] for a, b in n2.items()}, n2_max=float(max(pooled)),
                certify=bool(t_ho > max(pooled)),
                partial=part, partial_rise=bool(part[0.0] < part[0.25] < part[0.5] < part[0.75] < part[1.0]),
                shuffled_true=t_sh, shuffled_n1_p99=float(np.quantile(n1s, .99)),
                shuffled_refute=bool(t_sh > np.quantile(n1s, .99)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    if mode == "time":
        init(); dev, ho, rng = build(0, "line")
        freq = Counter(s for t in dev + ho for w in t for s in w); kept = sorted(freq)
        key = {s: base.true_value(s) for s in kept}; vals = list(key.values()); rng.shuffle(vals); key = dict(zip(kept, vals))
        H = IC(ho, LEX); t0 = time.time(); H.full(key); print(dict(full_score_s=round(time.time() - t0, 3), n_ho=len(ho)))
        t0 = time.time(); fit(IC(dev, LEX), key, kept, {s: 0 for s in kept}, 300, rng); print(dict(fit300_s=round(time.time() - t0, 2)))
    elif mode == "kill":
        init(); r = one((0, "R3")); print(json.dumps(r, indent=1))
        json.dump(r, open(HERE / "kill.json", "w"), indent=1)
    elif mode == "full":
        kr = json.load(open(HERE / "kill.json"))
        assert kr["refute"], "kill test stopped the study"
        jobs = [(k, r) for r in RUNGS for k in range(1, NSUB + 1)]
        with Pool(4, initializer=init) as P:
            res = P.map(one, jobs, chunksize=1)
        summ = {}
        for r in RUNGS:
            rr = [x for x in res if x["rung"] == r]
            summ[r] = dict(refute_n=sum(x["refute"] for x in rr), certify_n=sum(x["certify"] for x in rr),
                           shuffled_refute_n=sum(x["shuffled_refute"] for x in rr),
                           partial_means={f: float(np.mean([x["partial"][f] for x in rr])) for f in rr[0]["partial"]},
                           cons_per_seg=float(np.mean([x["shape"]["cons_per_seg"] for x in rr])),
                           true_ic_mean=float(np.mean([x["true_ic"] for x in rr])))
        print(json.dumps(summ, indent=1))
        json.dump(dict(summary=summ, runs=res), open(HERE / "full.json", "w"), indent=1)
