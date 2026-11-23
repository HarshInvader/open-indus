"""Power-gated IC refute test of Yajnadevam's Sanskrit key (prereg docs/prereg/yj_ic_refute.md).
Run: .venv/bin/python -I experiments/yj_ic_refute/run.py lmin    # lexicon densities only, no key scored
     .venv/bin/python -I experiments/yj_ic_refute/run.py kill    # planted corpus 0, generous matcher
     .venv/bin/python -I experiments/yj_ic_refute/run.py full    # gate (20 planted x 2 matchers), controls, then the real key
"""
import csv, json, random, sys, time
from collections import Counter, defaultdict
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
LANG = ROOT / "experiments/language"
sys.path.insert(0, str(LANG)); sys.path.insert(0, str(ROOT))
from yj_common import iast_to_slp                     # noqa
from corpus.load import icit_texts, distinct, runs     # noqa

SEED = 20261126
MAXW = 7
NPERM, NPLANT, NPART, ITERS, RESTARTS = 1000, 20, 10, 3000, 3
KEYLET = "kgcjtdnpbmyrlvsh"
GENEROUS = {"s": "sSzhH", "n": "nNRYmM", "d": "dDqQ", "t": "tTwW", "b": "bB", "k": "kK", "c": "cC",
            "j": "jJ", "p": "pP", "m": "mM"}           # a1_key_null.py, unchanged
STRICT = {}
ENDINGS = [(), ("m",), ("s",), ("s", "y"), ("t",), ("n",)]
KEYS = {"upstream_fc8813a": ROOT / "sources/yajnadevam_lipi_fc8813a/xlits.csv",
        "fieldcady_copy": ROOT / "sources/field-cady_indus_valley_script_corpus/xlits.csv"}


# ------------------------------------------------------------------ key, corpus, lexicon
def load_key(path):
    rows = list(csv.DictReader(open(path)))
    raw = {r["sign"]: r["xlit"] for r in rows}; canon = {r["sign"]: r["canonical"] for r in rows}
    key = {}
    for s in raw:
        v = raw[s]
        if v == "" and canon.get(s):
            v = "".join(raw.get(p, "") for p in canon[s].split("-") if p != s)
        key[s] = v.strip()
    return key


def readable(v):
    return any(ch.isalpha() for ch in v)


def cons(v):
    return tuple(c for c in v if c in KEYLET)


def corpus(key):
    """Distinct ICIT texts as lists of segments; a segment is a list of sign codes.
    Line breaks, '#' breaks and signs without a readable value split segments."""
    out = set()
    for r in distinct(icit_texts()):
        segs = []
        for run in runs(r["seq"]):
            cur = []
            for s in run:
                c = s[1:]
                if c in key and readable(key[c]):
                    cur.append(c)
                else:
                    if cur: segs.append(tuple(cur))
                    cur = []
            if cur: segs.append(tuple(cur))
        if segs:
            out.add(tuple(segs))
    return [list(t) for t in sorted(out)]


def build_lexicon(classes):
    inv = defaultdict(set)
    for kl in KEYLET:
        for ch in classes.get(kl, kl):
            inv[ch].add(kl)
    words = [w.strip() for w in open(LANG / "ext/skt/mw_headwords.txt") if w.strip()]
    sk = set()
    for w in words:
        c = [ch for ch in w if ch in inv]
        if not c or len(c) > MAXW:
            continue
        for e in ENDINGS:
            cc = c + list(e)
            if len(cc) <= MAXW:
                for t in product(*[sorted(inv[ch]) for ch in cc]):
                    sk.add(t)
    return sk, inv


def lmin_of(lex):
    """Frozen rule: smallest L whose lexicon density is <= 25% of the 16^L key-letter strings."""
    for L in range(1, MAXW + 1):
        if sum(1 for t in lex if len(t) == L) / len(KEYLET) ** L <= 0.25:
            return L


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
    def __init__(self, texts, lex, lmin):
        self.texts, self.lex, self.lmin = texts, lex, lmin
        self.by_sign = defaultdict(list)
        for i, t in enumerate(texts):
            for s in {s for g in t for s in g}:
                self.by_sign[s].append(i)

    def text(self, t, kc):
        cov = tot = 0
        for g in t:
            c = tuple(x for s in g for x in kc[s])
            if c:
                cov += ic_seg(c, self.lex, self.lmin); tot += len(c)
        return cov, tot

    def full(self, kc):
        self.cache = [self.text(t, kc) for t in self.texts]
        cov = sum(x[0] for x in self.cache); tot = sum(x[1] for x in self.cache)
        return cov / tot

    def after(self, kc, signs):
        idx = set()
        for s in signs:
            idx.update(self.by_sign[s])
        new = {i: self.text(self.texts[i], kc) for i in idx}
        cov = tot = 0
        for i, c in enumerate(self.cache):
            c = new.get(i, c); cov += c[0]; tot += c[1]
        return cov / tot, new


# ------------------------------------------------------------------ nulls, planting, fitting
def class_bins(kc, freq, size=10):
    by = defaultdict(list)
    for s in kc:
        by[len(kc[s])].append(s)
    bins = []
    for ss in by.values():
        ss = sorted(ss, key=lambda s: (-freq[s], s))
        bins += [ss[i:i + size] for i in range(0, len(ss), size)]
    return bins


def permute(kc, bins, rng):
    k = dict(kc)
    for b in bins:
        v = [kc[s] for s in b]; rng.shuffle(v); k.update(zip(b, v))
    return k


def shuffle_class(kc, signs, rng):
    k = dict(kc); by = defaultdict(list)
    for s in signs:
        by[len(kc[s])].append(s)
    for ss in by.values():
        v = [kc[s] for s in ss]; rng.shuffle(v); k.update(zip(ss, v))
    return k


def n1_test(S, kc, bins, rng, n=NPERM):
    t = S.full(kc); null = np.array([S.full(permute(kc, bins, rng)) for _ in range(n)])
    return dict(ic=t, n1_mean=float(null.mean()), n1_p99=float(np.quantile(null, .99)),
                beats=bool(t > np.quantile(null, .99)), p=float((1 + (null >= t).sum()) / (n + 1)))


def rv_stream(inv, rng, shuffled=False):
    rev = {ch: sorted(v)[0] for ch, v in inv.items()}      # reading consonant -> one key letter (his class)
    st = []
    for l in open(LANG / "ext/eqstats/rv_names_epithets.txt", encoding="utf8"):
        st += [rev[ch] for ch in iast_to_slp(l) if ch in rev]
    if shuffled:
        rng.shuffle(st)
    return st


def plant(texts, pk, freq, stream, rng):
    """Rewrite each Indus text slot by slot: a slot whose sign carries c consonants gets a sign whose
    planted value equals the next c consonants of the stream (picked by Indus frequency)."""
    by_val = defaultdict(list); by_c = defaultdict(list)
    for s, v in pk.items():
        by_val[v].append(s); by_c[len(v)].append(s)
    pick = lambda ss: rng.choices(ss, weights=[freq[s] for s in ss])[0]
    out, miss, slots = [], 0, 0
    for t in texts:
        p = rng.randrange(len(stream)); nt = []
        for g in t:
            ng = []
            for s in g:
                c = len(pk[s]); slots += 1
                if c == 0:
                    ng.append(pick(by_c[0])); continue
                for _ in range(50):
                    v = tuple(stream[(p + i) % len(stream)] for i in range(c))
                    if by_val.get(v):
                        ng.append(pick(by_val[v])); p += c; break
                    p += 1
                else:
                    ng.append(pick(by_c[c])); miss += 1
            nt.append(ng)
        out.append(nt)
    return out, miss / slots


def unigram(texts, freq, rng):
    signs = list(freq); w = [freq[s] for s in signs]
    return [[rng.choices(signs, weights=w, k=len(g)) for g in t] for t in texts]


def fit(S, kc0, rng, iters=ITERS):
    kc = dict(kc0); cur = S.full(kc); by = defaultdict(list)
    for s in kc:
        by[len(kc[s])].append(s)
    pools = [v for v in by.values() if len(v) >= 2]; w = [len(v) for v in pools]
    for _ in range(iters):
        a, b = rng.sample(rng.choices(pools, weights=w)[0], 2)
        if kc[a] == kc[b]:
            continue
        kc[a], kc[b] = kc[b], kc[a]
        nc, new = S.after(kc, [a, b])
        if nc >= cur:
            cur = nc
            for i, c in new.items():
                S.cache[i] = c
        else:
            kc[a], kc[b] = kc[b], kc[a]
    return kc


# ------------------------------------------------------------------ jobs
G = {}


def init():
    G["key"] = load_key(KEYS["upstream_fc8813a"])
    G["texts"] = corpus(G["key"])
    G["kc"] = {s: cons(v) for s, v in G["key"].items() if readable(v)}
    G["freq"] = Counter(s for t in G["texts"] for g in t for s in g)
    G["kc"] = {s: G["kc"][s] for s in G["freq"]}            # signs that occur
    for name, cl in (("generous", GENEROUS), ("strict", STRICT)):
        lex, inv = build_lexicon(cl); G[name] = (lex, inv, lmin_of(lex))


def planted_job(args):
    j, matcher, shuffled = args
    rng = random.Random(SEED + 100 * j + (50 if shuffled else 0) + (7 if matcher == "strict" else 0))
    lex, inv, lmin = G[matcher]; kc, freq = G["kc"], G["freq"]
    pk = shuffle_class(kc, list(kc), rng)
    corp, miss = plant(G["texts"], pk, freq, rv_stream(inv, rng, shuffled), rng)
    pf = Counter(s for t in corp for g in t for s in g)
    pk = {s: pk[s] for s in pf}; bins = class_bins(pk, pf)
    S = IC(corp, lex, lmin); res = n1_test(S, pk, bins, rng)
    res.update(j=j, matcher=matcher, shuffled=shuffled, miss_rate=miss, lmin=lmin)
    if not shuffled:
        part = {}
        for f in (0.0, 0.25, 0.5, 0.75):
            v = []
            for _ in range(NPART):
                keep = set(rng.sample(list(pk), int(f * len(pk))))
                v.append(S.full(shuffle_class(pk, [s for s in pk if s not in keep], rng)))
            part[f] = float(np.mean(v))
        part[1.0] = res["ic"]; res["partial"] = part
    return res


def fitted_job(r):
    rng = random.Random(SEED + 9000 + r)
    lex, inv, lmin = G["generous"]; kc, freq = G["kc"], G["freq"]
    corp = unigram(G["texts"], freq, rng)
    pf = Counter(s for t in corp for g in t for s in g); k0 = shuffle_class({s: kc[s] for s in pf}, list(pf), rng)
    S = IC(corp, lex, lmin); fk = fit(S, k0, rng)
    return dict(r=r, **n1_test(IC(corp, lex, lmin), fk, class_bins(fk, pf), rng))


def real_job(args):
    keyname, matcher = args
    rng = random.Random(SEED + 777 + (7 if matcher == "strict" else 0))
    lex, inv, lmin = G[matcher]
    key = load_key(KEYS[keyname]); texts = corpus(key)
    freq = Counter(s for t in texts for g in t for s in g); kc = {s: cons(key[s]) for s in freq}
    res = n1_test(IC(texts, lex, lmin), kc, class_bins(kc, freq), rng)
    tot = sum(len(kc[s]) * freq[s] for s in freq)
    res.update(key=keyname, matcher=matcher, lmin=lmin, n_texts=len(texts), key_consonants=tot)
    return res


def describe():
    init()
    segs = [g for t in G["texts"] for g in t]; cc = [sum(len(G["kc"][s]) for s in g) for g in segs]
    cc = [c for c in cc if c]
    d = dict(n_texts=len(G["texts"]), n_signs=len(G["kc"]), key_consonants=sum(cc),
             cons_per_segment=float(np.mean(cc)),
             share_cons_in_segs_ge5=float(sum(c for c in cc if c >= 5) / sum(cc)))
    for name in ("generous", "strict"):
        lex = G[name][0]
        d[name] = dict(lmin=G[name][2], skeletons=len(lex),
                       density={L: round(sum(1 for t in lex if len(t) == L) / 16 ** L, 4) for L in range(1, 8)})
    return d


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    if mode == "lmin":
        t0 = time.time(); d = describe(); d["build_s"] = round(time.time() - t0, 1); print(json.dumps(d, indent=1))
        S = IC(G["texts"], G["generous"][0], G["generous"][2]); rng = random.Random(1)
        dummy = shuffle_class(G["kc"], list(G["kc"]), rng); t0 = time.time(); S.full(dummy)
        print(dict(one_scoring_s=round(time.time() - t0, 3)))       # timing on a shuffled key; score not printed
    elif mode == "kill":
        init(); r = planted_job((0, "generous", False)); print(json.dumps(r, indent=1))
        json.dump(r, open(HERE / "kill.json", "w"), indent=1)
    elif mode == "full":
        assert json.load(open(HERE / "kill.json"))["beats"], "kill test stopped the study"
        with Pool(4, initializer=init) as P:
            planted = P.map(planted_job, [(j, m, sh) for m in ("generous", "strict") for sh in (False, True)
                                          for j in range(1, NPLANT + 1)], chunksize=1)
            fitted = P.map(fitted_job, range(RESTARTS), chunksize=1)
            gate = {}
            for m in ("generous", "strict"):
                pl = [x for x in planted if x["matcher"] == m and not x["shuffled"]]
                sh = [x for x in planted if x["matcher"] == m and x["shuffled"]]
                pm = {f: float(np.mean([x["partial"][f] for x in pl])) for f in (0.0, 0.25, 0.5, 0.75, 1.0)}
                gate[m] = dict(planted_pass=sum(x["beats"] for x in pl), shuffled_pass=sum(x["beats"] for x in sh),
                               partial_means=pm, partial_rise=bool(pm[0.0] < pm[0.25] < pm[0.5] < pm[0.75] < pm[1.0]),
                               miss_rate=float(np.mean([x["miss_rate"] for x in pl])))
                gate[m]["ok"] = bool(gate[m]["planted_pass"] >= 16 and gate[m]["shuffled_pass"] <= 1 and gate[m]["partial_rise"])
            print(json.dumps(gate, indent=1), flush=True)
            real = P.map(real_job, [(k, m) for k in KEYS for m in ("generous", "strict")], chunksize=1)
        prim = {r["matcher"]: r for r in real if r["key"] == "upstream_fc8813a"}
        if not gate["generous"]["ok"]:
            verdict = "untestable with this lexicon"
        elif all(gate[m]["ok"] and not prim[m]["beats"] for m in ("generous", "strict")):
            verdict = "refuted at stated power"
        elif any(prim[m]["beats"] for m in prim):
            verdict = "not refuted; no support"
        else:
            verdict = "inconclusive (strict gate failed; generous does not beat shuffles)"
        out = dict(verdict=verdict, gate=gate, real=real, fitted_on_noise=fitted, planted=planted)
        print(json.dumps(dict(verdict=verdict, real=real, fitted_on_noise=fitted), indent=1))
        json.dump(out, open(HERE / "full.json", "w"), indent=1)
