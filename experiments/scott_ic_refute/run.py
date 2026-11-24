"""Refute-only IC bench of the Scott (Dunn) key (prereg docs/prereg/scott_ic_refute.md).
Run: .venv/bin/python -I experiments/scott_ic_refute/run.py all
Order (frozen): step 0 coverage -> K2 saturation (fixes LMIN) -> W_real -> K1 -> K3 -> K4 -> ladder -> her key.
Output: result.json with aggregates only (no sign-level values, planted keys or readings).

Code-level choices fixed with this file's seal:
- IC per segment: exact maximum over each token's alternatives (enumeration, cached on the tuple of value sets)
  and over segmentation (ic_seg DP); ties -> fewer consonants. IC = sum covered / sum consonants of chosen readings.
- the Rigveda stream: words of rv_names_epithets.txt -> class skeletons; words with a class outside A are dropped.
- plant: c = consonant count of the real sign's first alternative (her key). Candidate signs are those whose planted
  set has an alternative equal to the next c stream consonants; the stream advances by the longest planted
  alternative of the chosen sign that matches at the current position. Up to 50 one-step skips, then a miss
  (random sign of the same class, weighted by frequency). Each text starts at a random stream position.
- chunks: n-grams (n = 4, 3, 2) of real signs inside segments with >= 5 occurrences in the corpus; longest match
  at each position, left to right. A stored chunk is reused with the stream position set to its stored end.
- K3 corpora are seeds 0-39 (K1 uses 0-4 of them). K4 uses seeds 100-139 with a unigram-shuffled stream.
- 75%-token partial key power (reported beside R): on the K3 corpora, a planted key right on >= 75% of tokens.
- ladder: corpora 0-9, 10 draws per level.
"""
import json, re, sys, time
from collections import Counter, defaultdict
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np, random

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/language"))
import values as V                                   # noqa: E402
from yj_common import iast_to_slp                     # noqa: E402
from corpus.load import m77_texts, distinct, runs     # noqa: E402

SEED = 20261204
MAXW = 7
NPERM = 1000; NK3 = 40; NK1 = 5; NK4 = 40; NRAND = 200; NLAD_C = 10; NLAD_D = 10
ENDINGS = [(), ("m",), ("S",), ("S", "y"), ("T",), ("N",)]
CLS_OFF = dict(V.CLS, b="b", v="v", r="R", l="l", f="R", F="R", x="l", t="T", d="d", w="T", q="d")


# ------------------------------------------------------------------ corpus, lexicon
def corpus(key):
    out = set()
    for r in distinct(m77_texts()):
        segs = []
        for run in runs(r["seq"]):
            cur = []
            for s in run:
                if key.get(s):
                    cur.append(s)
                else:
                    if cur: segs.append(tuple(cur))
                    cur = []
            if cur: segs.append(tuple(cur))
        if segs: out.add(tuple(segs))
    return [list(t) for t in sorted(out)]


def coverage(key):
    def cov(recs):
        tok = [s for r in recs for run in runs(r["seq"]) for s in run]
        return sum(1 for s in tok if key.get(s)) / len(tok), len(tok)
    d, nd = cov(distinct(m77_texts())); a, na = cov(m77_texts())
    return dict(distinct=d, distinct_tokens=nd, all=a, all_tokens=na)


def word_skels(slp, cls, A):
    """skeleton variants of one SLP1 word: anusvara -> m or N; T+S -> also S. None if outside A."""
    base = []
    for ch in slp:
        if ch in V.VOW: continue
        if ch == "M": base.append(("m", "N")); continue
        if ch not in cls: return []
        base.append((cls[ch],))
    out = set()
    for t in product(*base):
        if any(c not in A for c in t): continue
        out.add(t)
        u = []; i = 0
        while i < len(t):
            if t[i] == "T" and i + 1 < len(t) and t[i + 1] == "S": u.append("S"); i += 2
            else: u.append(t[i]); i += 1
        out.add(tuple(u))
    return [t for t in out if t]


def build_lexicon(A, cls=V.CLS):
    lex = set()
    for w in open(ROOT / "experiments/language/ext/skt/mw_headwords.txt"):
        w = w.strip()
        if not w: continue
        for sk in word_skels(w, cls, A):
            for e in ENDINGS:
                if all(c in A for c in e):
                    t = sk + e
                    if len(t) <= MAXW: lex.add(t)
    return lex


def density(lex, A, L):
    return sum(1 for t in lex if len(t) == L) / len(A) ** L


# ------------------------------------------------------------------ statistic
def ic_seg(c, lex, lmin):
    n = len(c); best = [0] * (n + 1)
    for i in range(1, n + 1):
        b = best[i - 1]
        for L in range(lmin, min(MAXW, i) + 1):
            if best[i - L] + L > b and c[i - L:i] in lex:
                b = best[i - L] + L
        best[i] = b
    return best[n]


class IC:
    def __init__(self, lex, lmin):
        self.lex, self.lmin, self.cache = lex, lmin, {}

    def seg(self, sets):
        r = self.cache.get(sets)
        if r is None:
            best = None
            for choice in product(*sets):
                c = tuple(x for a in choice for x in a)
                cov = ic_seg(c, self.lex, self.lmin) if c else 0
                if best is None or cov > best[0] or (cov == best[0] and len(c) < best[1]):
                    best = (cov, len(c))
            r = self.cache[sets] = best
        return r

    def full(self, texts, key):
        cov = tot = 0
        for t in texts:
            for g in t:
                a, b = self.seg(tuple(tuple(key[s]) for s in g)); cov += a; tot += b
        return cov / tot if tot else 0.0


def first_cc(key, s):
    return len(key[s][0])


def class_bins(key, freq, size=10):
    by = defaultdict(list)
    for s in key:
        if key[s]: by[first_cc(key, s)].append(s)
    bins = []
    for ss in by.values():
        ss = sorted(ss, key=lambda s: (-freq[s], int(s[1:])))
        bins += [ss[i:i + size] for i in range(0, len(ss), size)]
    return bins


def permute(key, bins, rng):
    k = dict(key)
    for b in bins:
        v = [key[s] for s in b]; rng.shuffle(v); k.update(zip(b, v))
    return k


def shuffle_class(key, signs, rng):
    k = dict(key); by = defaultdict(list)
    for s in signs: by[first_cc(key, s)].append(s)
    for ss in by.values():
        v = [key[s] for s in ss]; rng.shuffle(v); k.update(zip(ss, v))
    return k


def n1(S, texts, key, freq, rng, n=NPERM, observed=True):
    bins = class_bins(key, freq)
    null = np.array([S.full(texts, permute(key, bins, rng)) for _ in range(n)])
    out = dict(n1_mean=float(null.mean()), n1_p99=float(np.quantile(null, .99)),
               width=float(np.quantile(null, .99) - null.mean()))
    if observed:
        t = S.full(texts, key)
        out.update(ic=t, beats=bool(t > np.quantile(null, .99)), p=float((1 + (null >= t).sum()) / (n + 1)))
    return out


# ------------------------------------------------------------------ plant
def rv_stream(A, rng, shuffled=False):
    st = []
    for l in open(ROOT / "experiments/language/ext/eqstats/rv_names_epithets.txt", encoding="utf8"):
        for w in l.split():
            sk = []
            ok = True
            for ch in iast_to_slp(w):
                if ch in V.VOW: continue
                c = "N" if ch == "M" else V.CLS.get(ch)
                if c is None or c not in A: ok = False; break
                sk.append(c)
            if ok: st += sk
    if shuffled: rng.shuffle(st)
    return st


def chunks_of(texts):
    cnt = Counter()
    for t in texts:
        for g in t:
            for n in (2, 3, 4):
                for i in range(len(g) - n + 1): cnt[tuple(g[i:i + n])] += 1
    return {c for c, k in cnt.items() if k >= 5}


def parse(g, CH):
    out, i = [], 0
    while i < len(g):
        for n in (4, 3, 2, 1):
            if n == 1 or (i + n <= len(g) and tuple(g[i:i + n]) in CH):
                out.append(tuple(g[i:i + n])); i += n; break
    return out


def plant(texts, key, pk, freq, stream, CH, rng):
    by_alt = defaultdict(list); by_c = defaultdict(list)
    for s, v in pk.items():
        if not v: continue
        for a in v: by_alt[a].append(s)
        by_c[len(v[0])].append(s)
    pick = lambda ss: rng.choices(ss, weights=[freq[s] for s in ss])[0]
    L = len(stream); store = {}
    out, miss, slots, skipped, used = [], 0, 0, 0, 0

    def fill(sign, p):
        nonlocal miss, slots, skipped, used
        c = first_cc(key, sign); slots += 1
        if c == 0:
            return pick(by_c[0]) if by_c[0] else sign, p
        for _ in range(50):
            v = tuple(stream[(p + i) % L] for i in range(c))
            if by_alt.get(v):
                s = pick(by_alt[v])
                best = max((a for a in pk[s] if tuple(stream[(p + i) % L] for i in range(len(a))) == a), key=len)
                used += len(best)
                return s, p + len(best)
            p += 1; skipped += 1
        miss += 1
        return pick(by_c[c]), p

    for t in texts:
        p = rng.randrange(L); nt = []
        for g in t:
            ng = []
            for ch in parse(g, CH):
                if len(ch) > 1 and ch in store:
                    signs, end = store[ch]; ng += signs; p = end; continue
                signs = []
                for s in ch:
                    s2, p = fill(s, p); signs.append(s2)
                if len(ch) > 1: store[ch] = (signs, p)
                ng += signs
            nt.append(ng)
        out.append(nt)
    return out, dict(miss=miss / slots, skipped=skipped / max(1, skipped + used))


def bigram_share(texts):
    c = Counter((g[i], g[i + 1]) for t in texts for g in t for i in range(len(g) - 1))
    tot = sum(c.values())
    return sum(v for _, v in c.most_common(50)) / tot if tot else 0.0


def unigram(texts, freq, rng):
    signs = list(freq); w = [freq[s] for s in signs]
    return [[rng.choices(signs, weights=w, k=len(g)) for g in t] for t in texts]


# ------------------------------------------------------------------ workers
G = {}


def init(lmin):
    key, _ = V.load()
    texts = corpus(key)
    freq = Counter(s for t in texts for g in t for s in g)
    A = sorted({c for v in key.values() if v for a in v for c in a})
    lex = build_lexicon(set(A))
    G.update(key=key, texts=texts, freq=freq, A=A, lex=lex, lmin=lmin, CH=chunks_of(texts))


def planted_job(args):
    seed, shuffled, partial = args
    key, texts, freq = G["key"], G["texts"], G["freq"]
    rng = random.Random(SEED * 1000 + seed + (500 if shuffled else 0))
    keyed = [s for s in key if key[s]]
    pk = shuffle_class(key, keyed, rng)
    stream = rv_stream(set(G["A"]), rng, shuffled=shuffled)
    pt, st = plant(texts, key, pk, freq, stream, G["CH"], rng)
    pfreq = Counter(s for t in pt for g in t for s in g)
    S = IC(G["lex"], G["lmin"])
    res = n1(S, pt, pk, pfreq, rng)
    res.update(seed=seed, shuffled=shuffled, bigram_share=bigram_share(pt), **st)
    if partial:
        # 75%-token partial key: keep signs right until they hold >= 75% of planted tokens; shuffle the rest
        order = keyed[:]; rng.shuffle(order); kept, tok = set(), 0; tot = sum(pfreq.values())
        for s in order:
            if tok / tot >= 0.75: break
            kept.add(s); tok += pfreq[s]
        k75 = shuffle_class(pk, [s for s in keyed if s not in kept], rng)
        r75 = n1(S, pt, k75, pfreq, rng)
        res["p75"] = dict(ic=r75["ic"], n1_mean=r75["n1_mean"], width=r75["width"])
    return res


def ladder_job(seed):
    key, texts, freq = G["key"], G["texts"], G["freq"]
    rng = random.Random(SEED * 7 + seed)
    keyed = [s for s in key if key[s]]
    pk = shuffle_class(key, keyed, rng)
    pt, _ = plant(texts, key, pk, freq, rv_stream(set(G["A"]), rng), G["CH"], rng)
    pfreq = Counter(s for t in pt for g in t for s in g); tot = sum(pfreq.values())
    S = IC(G["lex"], G["lmin"]); out = {}
    for lev in (0, .25, .5, .75):
        vals, chance = [], []
        for _ in range(NLAD_D):
            order = keyed[:]; rng.shuffle(order); kept, tok = set(), 0
            for s in order:
                if tok / tot >= lev: break
                kept.add(s); tok += pfreq[s]
            k = shuffle_class(pk, [s for s in keyed if s not in kept], rng)
            vals.append(S.full(pt, k))
            chance.append(sum(pfreq[s] for s in keyed if k[s] == pk[s]) / tot)
        out[str(lev)] = dict(ic=float(np.mean(vals)), right_share=float(np.mean(chance)))
    out["1.0"] = dict(ic=S.full(pt, pk), right_share=1.0)
    return out


def random_key_job(seed):
    key, texts = G["key"], G["texts"]
    rng = random.Random(SEED * 3 + seed)
    k = shuffle_class(key, [s for s in key if key[s]], rng)
    S = IC(G["lex"], G["lmin"])
    k1 = {s: (v[:1] if v else v) for s, v in k.items()}
    return S.full(texts, k), S.full(texts, k1)


def wreal_job(seed):
    key, texts, freq = G["key"], G["texts"], G["freq"]
    rng = random.Random(SEED * 5 + seed)
    S = IC(G["lex"], G["lmin"]); bins = class_bins(key, freq)
    return [S.full(texts, permute(key, bins, rng)) for _ in range(NPERM // 10)]


# ------------------------------------------------------------------ main
def swap_off_mean(key, texts, lmin, A):
    """K2 report: random-key mean IC with her swap classes off (b/v, r/l, d/t kept apart)."""
    rows = {}
    import csv
    raw = {r["M"]: r["value"] for r in csv.DictReader(open(V.LOCAL / "key.csv", encoding="utf-8"))}
    ov = {r["M"]: r["value"] for r in csv.DictReader(open(V.LOCAL / "overrides.csv", encoding="utf-8"))}
    k2 = {}
    for s, v in key.items():
        if not v: k2[s] = v; continue
        sk = []
        for a in V._alts(ov.get(s, raw[s])):
            slp = iast_to_slp(a.lower().replace("sh", "ś"))
            t = tuple(CLS_OFF[ch] if ch in CLS_OFF else ("N" if ch == "M" else None) for ch in slp if ch not in V.VOW)
            if None not in t and t not in sk: sk.append(t)
        k2[s] = sk or v
    A2 = {c for v in k2.values() if v for a in v for c in a}
    lex = build_lexicon(A2, CLS_OFF); S = IC(lex, lmin); rng = random.Random(SEED * 11)
    vals = [S.full(texts, shuffle_class(k2, [s for s in k2 if k2[s]], rng)) for _ in range(20)]
    return float(np.mean(vals))


def main():
    t0 = time.time()
    key, rep = V.load()
    assert not rep["flagged"], "unparsed entries outside overrides.csv"
    out = {"overrides": rep["n_override"], "keyed": sum(1 for v in key.values() if v)}
    cov = coverage(key); out["coverage"] = cov
    print("coverage", cov, flush=True)
    if cov["distinct"] < 0.90:
        out["verdict"] = "below standard"; json.dump(out, open(HERE / "result.json", "w"), indent=1); return
    texts = corpus(key)
    A = sorted({c for v in key.values() if v for a in v for c in a}); out["A"] = len(A)
    lex = build_lexicon(set(A))
    out["corpus"] = dict(texts=len(texts), tokens=sum(len(g) for t in texts for g in t))
    # K2 saturation (fixes LMIN before any power is seen)
    lmin = None
    for L in (4, 5):
        dens = density(lex, A, L)
        with Pool(4, initializer=init, initargs=(L,)) as P:
            rk = P.map(random_key_job, range(NRAND))
        m = float(np.mean([a for a, _ in rk])); m1 = float(np.mean([b for _, b in rk]))
        so = swap_off_mean(key, texts, L, A)
        ok = dens <= 0.25 and m <= 0.50
        out.setdefault("K2", []).append(dict(lmin=L, density=dens, random_mean=m, random_mean_first_alt=m1,
                                             random_mean_swaps_off=so, passed=bool(ok)))
        print("K2", out["K2"][-1], flush=True)
        if ok: lmin = L; break
    if lmin is None:
        out["verdict"] = "untestable at stated power (K2 saturation)"
        json.dump(out, open(HERE / "result.json", "w"), indent=1); return
    out["lmin"] = lmin
    with Pool(4, initializer=init, initargs=(lmin,)) as P:
        # W_real from her key's shuffles (her unshuffled key is not scored here)
        wr = np.array([x for xs in P.map(wreal_job, range(10)) for x in xs])
        W_real = float(np.quantile(wr, .99) - wr.mean()); out["W_real"] = W_real
        print("W_real", W_real, flush=True)
        # K1 then K3 (K1 = seeds 0-4 of K3)
        k3 = P.map(planted_job, [(s, False, True) for s in range(NK3)], chunksize=1)
        thr = lambda r: max(r["width"], W_real)
        passes = [r["ic"] - r["n1_mean"] > thr(r) for r in k3]
        k1 = sum(passes[:NK1]); out["K1"] = dict(passes=int(k1), of=NK1, passed=bool(k1 >= 3))
        n3 = sum(passes); out["K3"] = dict(passes=int(n3), of=NK3, passed=bool(n3 >= 32))
        p75 = sum(r["p75"]["ic"] - r["p75"]["n1_mean"] > max(r["p75"]["width"], W_real) for r in k3)
        out["K3"]["p75_passes"] = int(p75)
        bs = [r["bigram_share"] for r in k3]
        out["plant"] = dict(miss=float(np.mean([r["miss"] for r in k3])), skipped=float(np.mean([r["skipped"] for r in k3])),
                            bigram_share_planted=float(np.mean(bs)), bigram_share_real=bigram_share(texts),
                            widths_planted=[r["width"] for r in k3])
        out["plant"]["formula_faithful"] = bool(out["plant"]["bigram_share_planted"] >= 0.8 * out["plant"]["bigram_share_real"])
        print("K1", out["K1"], "K3", out["K3"], "plant", {k: v for k, v in out["plant"].items() if k != "widths_planted"}, flush=True)
        if not out["K1"]["passed"]:
            out["verdict"] = "untestable at stated power (K1)"
        elif not out["K3"]["passed"]:
            out["verdict"] = "untestable at stated power (K3)"
        else:
            k4 = P.map(planted_job, [(100 + s, True, False) for s in range(NK4)], chunksize=1)
            fa = sum(r["ic"] - r["n1_mean"] > max(r["width"], W_real) for r in k4)
            out["K4"] = dict(passes=int(fa), of=NK4, passed=bool(fa <= 2))
            print("K4", out["K4"], flush=True)
            if not out["K4"]["passed"]:
                out["verdict"] = "untestable at stated power (K4)"
        lad = P.map(ladder_job, range(NLAD_C))
        out["ladder"] = {lev: dict(ic=float(np.mean([l[lev]["ic"] for l in lad])),
                                   right_share=float(np.mean([l[lev]["right_share"] for l in lad])))
                         for lev in lad[0]}
        levs = ["0", "0.25", "0.5", "0.75", "1.0"]
        out["ladder"]["strict_rise_share"] = float(np.mean([all(l[a]["ic"] < l[b]["ic"] for a, b in zip(levs, levs[1:])) for l in lad]))
    if "verdict" not in out:
        S = IC(lex, lmin); rng = random.Random(SEED * 13)
        freq = Counter(s for t in texts for g in t for s in g)
        her = n1(S, texts, key, freq, rng)
        out["her_key"] = her
        k1a = {s: (v[:1] if v else v) for s, v in key.items()}
        out["secondary_first_alt"] = n1(S, texts, k1a, freq, rng)
        for name, kw in [("secondary_uncertain_blank", dict(blank_uncertain=True)),
                         ("secondary_overrides_blank", dict(blank_overrides=True))]:
            k2, _ = V.load(**kw); t2 = corpus(k2); f2 = Counter(s for t in t2 for g in t for s in g)
            out[name] = n1(S, t2, k2, f2, rng)
        X = out["K3"]["passes"] / NK3; n = NK3; z = 1.96
        c = (X + z * z / (2 * n)) / (1 + z * z / n); h = z * np.sqrt(X * (1 - X) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        out["power"] = dict(X=X, wilson95=[float(c - h), float(c + h)], p75=out["K3"]["p75_passes"] / NK3,
                            label="upper bound, plant not formula-faithful" if not out["plant"]["formula_faithful"] else "")
        out["verdict"] = "R: fails to beat its shuffles" if not her["beats"] else "not refuted; no support"
        print("her key", her, flush=True)
    out["seconds"] = time.time() - t0
    print("VERDICT", out["verdict"], flush=True)
    json.dump(out, open(HERE / "result.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1:] == ["all"]: main()
