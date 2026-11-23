"""Known-script certification on Linear B (prereg docs/prereg/lb_certify.md).
Run: .venv/bin/python -I experiments/lb_certify/run.py kill        # one subsample, 74% coverage
     .venv/bin/python -I experiments/lb_certify/run.py full [cov]  # 20 subsamples (only if kill passes)
"""
import json, re, sys, unicodedata, random
from collections import Counter, defaultdict
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
SEED = 20261125
MAXW = 7
SYL = re.compile(r"^(?:[dkmnpqrstwzj]?[aeiou]|[a-z]{1,3}[aeiou]\d?|[aeiou]\d?)$")
WORD = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEYLET = set("dkmnpqrstz")          # j, w removed from every key value (no Homeric reflex)
INV = defaultdict(set)              # Greek reading consonant -> key letters that may produce it
for c in "dkmnprstz":
    INV[c].add(c)
for c in "ptk":
    INV[c].add("q")

# ------------------------------------------------------------------ data
def lb_texts():
    out = []
    for l in open(ROOT / "sources/paragorth_Indus-/data/codelib/linear_b.jsonl"):
        r = json.loads(l); sig = []
        for w in r["seq"]:
            if not WORD.match(w):
                continue
            parts = w.split("-")
            if not all(SYL.match(p) for p in parts):
                continue
            sig += parts
        if len(sig) >= 2:
            out.append((r["id"], sig))
    return out


def m77_lengths():
    L = [sum(1 for s in json.loads(l)["seq"] if s != "|")
         for l in open(ROOT / "data/m77_texts.jsonl") if json.loads(l)["object_type"] in ("seal", "sealing")]
    return [x for x in L if x >= 2]


def chunk(texts, lens, rng):
    out = []
    for tid, sig in texts:
        i = 0
        while len(sig) - i >= 2:
            L = min(lens[rng.integers(len(lens))], len(sig) - i)
            out.append((tid, sig[i:i + L])); i += L
    return out


GMAP = {"β": "p", "π": "p", "φ": "p", "γ": "k", "κ": "k", "χ": "k", "θ": "t", "τ": "t", "δ": "d", "λ": "r", "ρ": "r",
        "ζ": "z", "ξ": "ks", "ψ": "ps", "μ": "m", "ν": "n", "σ": "s", "ς": "s"}
VOW = set("αεηιουω")


def skeleton(word):
    w = "".join(ch for ch in unicodedata.normalize("NFD", word.lower()) if not unicodedata.combining(ch))
    seq = []  # (cons or 'V')
    for ch in w:
        if ch in VOW:
            seq.append("V")
        elif ch in GMAP:
            seq += list(GMAP[ch])
    cons = []
    for i, c in enumerate(seq):
        if c == "V":
            continue
        nxt = seq[i + 1] if i + 1 < len(seq) else None
        if nxt is None and c in "snr":
            continue
        if nxt is not None and nxt != "V" and c in "snrm":
            continue
        if cons and cons[-1] == c and i > 0 and seq[i - 1] == c:
            continue
        cons.append(c)
    return cons


def build_lexicon():
    words = set()
    for f in ("homer_001.xml", "homer_002.xml"):
        txt = re.sub(r"<[^>]+>", " ", open(ROOT / "experiments/cognate_decipher/ext/greek" / f, encoding="utf8").read())
        words.update(re.findall(r"[Ͱ-Ͽἀ-῿]+", txt))
    sk = set()
    for w in words:
        c = skeleton(w)
        if 1 <= len(c) <= MAXW:
            for t in product(*[sorted(INV[ch]) for ch in c]):
                sk.add(t)
    return sk, len(words)


def true_value(sign):
    return [c for c in re.sub(r"\d", "", sign)[:-1] if c in KEYLET]


# ------------------------------------------------------------------ scorer (logic of a1_key_null)
def min_words(cons, lex):
    n = len(cons); INF = 10 ** 9
    best = [0] + [INF] * n; best2 = [True] + [False] * n
    for i in range(1, n + 1):
        for L in range(1, min(MAXW, i) + 1):
            if best[i - L] < INF and tuple(cons[i - L:i]) in lex:
                best[i] = min(best[i], best[i - L] + 1)
                if L >= 2 and best2[i - L]:
                    best2[i] = True
    return best[n], best2[n]


class Scorer:
    def __init__(self, texts, lex):
        self.texts, self.lex = texts, lex
        self.by_sign = defaultdict(list)
        for i, t in enumerate(texts):
            for s in set(t):
                self.by_sign[s].append(i)

    def text_score(self, t, key):
        segs, cur = [], []
        for s in t:                       # masked (unkeyed) signs are breaks; keyed vowel signs give no consonant
            if s in key:
                cur += key[s]
            else:
                segs.append(cur); cur = []
        segs.append(cur)
        segs = [c for c in segs if len(c) >= 2]
        if not segs:
            return None
        C = W = 0; L2 = True
        for c in segs:
            w, l2 = min_words(c, self.lex)
            if w >= 10 ** 9:
                w, l2 = len(c), False
            C += len(c); W += w; L2 = L2 and l2
        return (C, W, L2)

    def full(self, key):
        self.cache = [self.text_score(t, key) for t in self.texts]
        return self.summary()

    def summary(self):
        v = [c for c in self.cache if c]
        C = sum(x[0] for x in v); W = sum(x[1] for x in v)
        return dict(cpw=C / W, long=sum(x[2] for x in v) / len(v), n=len(v))

    def cpw_after(self, key, signs):
        idx = set()
        for s in signs:
            idx.update(self.by_sign[s])
        new = {i: self.text_score(self.texts[i], key) for i in idx}
        C = W = 0
        for i, c in enumerate(self.cache):
            c = new.get(i, c)
            if c:
                C += c[0]; W += c[1]
        return C / W, new


def fit(scorer, key0, signs, iters, rng):
    key = dict(key0); cur = scorer.full(key)["cpw"]
    for _ in range(iters):
        a, b = rng.sample(signs, 2)
        if key[a] == key[b]:
            continue
        key[a], key[b] = key[b], key[a]
        nc, new = scorer.cpw_after(key, [a, b])
        if nc >= cur:
            cur = nc
            for i, c in new.items():
                scorer.cache[i] = c
        else:
            key[a], key[b] = key[b], key[a]
    return key


def bins_of(signs, freq, size=10):
    ss = sorted(signs, key=lambda s: -freq[s])
    return [ss[i:i + size] for i in range(0, len(ss), size)]


def permute_in_bins(key, bins, rng):
    k = dict(key)
    for b in bins:
        vals = [key[s] for s in b]; rng.shuffle(vals)
        for s, v in zip(b, vals):
            k[s] = v
    return k


def unigram(texts, rng):
    toks = [s for t in texts for s in t]
    return [[rng.choice(toks) for _ in t] for t in texts]


def markov(texts, rng):
    nxt = defaultdict(list); starts = []
    for t in texts:
        starts.append(t[0])
        for a, b in zip(t, t[1:]):
            nxt[a].append(b)
    out = []
    for t in texts:
        s = [rng.choice(starts)]
        while len(s) < len(t):
            s.append(rng.choice(nxt[s[-1]]) if nxt[s[-1]] else rng.choice(starts))
        out.append(s)
    return out


# ------------------------------------------------------------------ one subsample
LEX = None


def init():
    global LEX
    LEX = build_lexicon()[0]


def subsample(args):
    k, cov, nperm, iters, restarts = args
    rng_np = np.random.default_rng(SEED + 1000 * k + int(cov * 100)); rng = random.Random(SEED + 1000 * k + int(cov * 100))
    texts = lb_texts(); lens = m77_lengths()
    ch = chunk(texts, lens, rng_np)
    pick = rng_np.choice(len(ch), size=min(2300, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    ids = sorted({tid for tid, _ in ch}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    dev = [t for tid, t in ch if tid in dev_ids]; ho = [t for tid, t in ch if tid not in dev_ids]
    freq = Counter(s for t in dev + ho for s in t)
    signs = list(freq)                 # every sign has a known reading; vowel signs map to []
    order = signs[:]; rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= cov:
            break
        kept.append(s); c += freq[s]
    true = {s: true_value(s) for s in kept}
    bins = bins_of(kept, freq)
    H = Scorer(ho, LEX); D = Scorer(dev, LEX)
    t_ho = H.full(true); t_dev = D.full(true)
    n1 = np.array([H.full(permute_in_bins(true, bins, rng))["cpw"] for _ in range(nperm)])
    mono = {}
    for frac in (0.25, 0.5, 0.75):
        keep = set(rng.sample(kept, int(frac * len(kept))))
        rest = [s for s in kept if s not in keep]; vals = [true[s] for s in rest]; rng.shuffle(vals)
        pk = dict(true); pk.update(dict(zip(rest, vals)))
        mono[frac] = H.full(pk)["cpw"]
    n2 = defaultdict(list)
    for name, corp in (("real", dev), ("unigram", unigram(dev, rng)), ("markov", markov(dev, rng))):
        S = Scorer(corp, LEX)
        for r in range(restarts):
            vals = [true[s] for s in kept]; rng.shuffle(vals)
            fk = fit(S, dict(zip(kept, vals)), kept, iters, rng)
            n2[name].append(H.full(fk)["cpw"])
    pooled = np.array([x for v in n2.values() for x in v])
    return dict(k=k, cov=cov, n_dev=len(dev), n_ho=len(ho), n_signs_keyed=len(kept), true_ho=t_ho, true_dev=t_dev,
                n1_mean=float(n1.mean()), n1_p99=float(np.quantile(n1, .99)),
                refute=bool(t_ho["cpw"] > np.quantile(n1, .99)),
                n2={k_: [float(x) for x in v] for k_, v in n2.items()}, n2_p95=float(np.quantile(pooled, .95)),
                certify=bool(t_ho["cpw"] > np.quantile(pooled, .95)),
                mono=mono, mono_ok=bool(mono[0.25] < mono[0.5] < mono[0.75] < t_ho["cpw"]))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    lex, nwords = build_lexicon(); print(dict(homer_forms=nwords, skeletons=len(lex), lb_texts=len(lb_texts())), flush=True)
    if mode == "kill":
        init(); r = subsample((0, 0.74, 1000, 3000, 3)); print(json.dumps(r, indent=1))
        json.dump(r, open(HERE / "kill.json", "w"), indent=1)
    elif mode == "full":
        kr = json.load(open(HERE / "kill.json"))
        assert kr["mono_ok"] and (kr["refute"] or kr["certify"]), "kill test stopped the study"
        cov = float(sys.argv[2])
        with Pool(4, initializer=init) as P:
            res = P.map(subsample, [(k, cov, 1000, 3000, 3) for k in range(1, 21)])
        out = dict(cov=cov, refute_rate=float(np.mean([r["refute"] for r in res])),
                   certify_rate=float(np.mean([r["certify"] for r in res])),
                   mono_rate=float(np.mean([r["mono_ok"] for r in res])), runs=res)
        print({k: v for k, v in out.items() if k != "runs"})
        json.dump(out, open(HERE / f"full_{int(cov * 100)}.json", "w"), indent=1)
