"""Red team of signlist_shape greedy_shape (board #40). Prereg: docs/prereg/redteam_signlist_shape.md
    board/run.sh .venv/bin/python -I experiments/redteam_signlist_shape/rt.py
Own scoring code: class n-gram (KN or Witten-Bell) x within-class emission, scores ORIGINAL sign sequence.
Writes out/results.json."""
import sys, json, math, random, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, runs, icit_texts, distinct  # noqa

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
BOS, EOS, UNK = "<s>", "</s>", "<unk>"
POST1977 = {"Dholavira", "Nausharo", "Banawali", "Rakhigarhi", "Farmana", "Bhirrana", "Gola Dhoro (Bagasra)",
            "Karanpura", "Khirsara", "Kanmer", "Shikarpur", "Lakhanjo-daro", "Tarkhanewala-dera", "Naru-Waro-dharo"}
ALLM = [f"M{i}" for i in range(1, 418)]


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ language model
class LM:
    def __init__(self, cls, order=3, smooth="kn", d=0.75):
        self.cls, self.o, self.sm, self.d = cls, order, smooth, d

    def fit(self, seqs):
        o = self.o
        self.n = Counter(s for q in seqs for s in q)
        self.cn, self.ck = Counter(), Counter()
        for s, c in self.n.items():
            k = self.cls.get(s, s); self.cn[k] += c; self.ck[k] += 1
        self.ng = [None] + [Counter() for _ in range(o)]
        for q in seqs:
            p = [BOS] * (o - 1) + [self.cls.get(s, s) for s in q] + [EOS]
            for i in range(o - 1, len(p)):
                for m in range(1, o + 1):
                    self.ng[m][tuple(p[i - m + 1:i + 1])] += 1
        # per-order: counts used (top order raw counts, lower orders continuation counts for KN)
        self.cnt = [None] + [Counter() for _ in range(o)]
        self.cnt[o] = self.ng[o]
        for m in range(1, o):
            if self.sm == "kn":
                for g in self.ng[m + 1]:
                    self.cnt[m][g[1:]] += 1
            else:
                self.cnt[m] = self.ng[m]
        self.htot = [None] + [Counter() for _ in range(o)]
        self.htyp = [None] + [Counter() for _ in range(o)]
        for m in range(1, o + 1):
            for g, c in self.cnt[m].items():
                self.htot[m][g[:-1]] += c; self.htyp[m][g[:-1]] += 1
        self.V = len(self.cn) + 1
        self.cache = {}
        return self

    def p(self, g):
        m = len(g)
        key = g
        if key in self.cache:
            return self.cache[key]
        h = g[:-1]
        if m == 1:
            r = (self.cnt[1][g] + 1.0) / (self.htot[1][()] + self.V)
        else:
            low = self.p(g[1:])
            tot = self.htot[m][h]
            if tot == 0:
                r = low
            elif self.sm == "kn":
                r = max(self.cnt[m][g] - self.d, 0) / tot + self.d * self.htyp[m][h] / tot * low
            else:  # Witten-Bell
                t = self.htyp[m][h]
                r = (self.cnt[m][g] + t * low) / (tot + t)
        self.cache[key] = r
        return r

    def score_tokens(self, q):
        """-> list of (sign, logp) for scored tokens (signs seen in train) + EOS."""
        o = self.o
        p = [BOS] * (o - 1) + [self.cls.get(s, s) if s in self.n else UNK for s in q] + [EOS]
        raw = [None] * (o - 1) + list(q) + [EOS]
        out = []
        for i in range(o - 1, len(p)):
            if p[i] == UNK:
                continue
            lp = math.log(self.p(tuple(p[i - o + 1:i + 1])))
            if raw[i] != EOS:
                c = p[i]
                lp += math.log((self.n[raw[i]] + 0.5) / (self.cn[c] + 0.5 * self.ck[c]))
            out.append((raw[i], lp))
        return out


def score(cls, train, test_texts, order=3, smooth="kn"):
    """test_texts: list of list-of-runs. -> list per text of list of (sign, lp)."""
    m = LM(cls, order, smooth).fit(train)
    return [[t for r in runs_ for t in m.score_tokens(r)] for runs_ in test_texts]


def diff(A, B, ntr=None, band=None, Bn=2000, seed=0):
    """per-token LL difference A-B, bootstrap over texts; band: None | 'freq' | 'rare' (by train count >=10)."""
    def keep(s):
        if band is None:
            return True
        if s == EOS:
            return False
        f = ntr[s] >= 10
        return f if band == "freq" else not f
    da = np.array([sum(lp for s, lp in a if keep(s)) - sum(lp for s, lp in b if keep(s)) for a, b in zip(A, B)])
    n = np.array([sum(1 for s, _ in a if keep(s)) for a in A])
    r = np.random.default_rng(seed)
    bs = []
    for _ in range(Bn):
        i = r.integers(0, len(da), len(da))
        bs.append(da[i].sum() / max(n[i].sum(), 1))
    return {"d": float(da.sum() / n.sum()), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "n_tok": int(n.sum())}


def tot(A):
    return sum(lp for a in A for _, lp in a)


# ------------------------------------------------------------------ partitions
class UF:
    def __init__(self):
        self.p = {}

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x

    def u(self, a, b):
        self.p[self.f(a)] = self.f(b)


def from_pairs(pairs, signs=ALLM):
    uf = UF()
    for a, b in pairs:
        uf.u(a, b)
    return {s: uf.f(s) for s in signs}


def classes(part):
    g = defaultdict(list)
    for s, c in part.items():
        g[c].append(s)
    return [sorted(v, key=lambda x: int(x[1:])) for v in g.values() if len(v) > 1]


def numeral_table():
    st = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
    t = {}
    for sysn in ("short", "tall"):
        for k, v in st[sysn].items():
            if k not in ("99", "101"):
                t[f"M{k}"] = (sysn, v)
    return t


def constrained(pairs, ntr, num, no_hapax):
    """rebuild in order, skipping pairs that would mix numeral values (or numeral+non-numeral) or use hapaxes."""
    uf = UF(); kept, skipped = [], []
    members = defaultdict(set)
    for s in ALLM:
        members[s] = {s}
    for a, b in pairs:
        ra, rb = uf.f(a), uf.f(b)
        if ra == rb:
            continue
        why = None
        if no_hapax and (ntr[a] <= 1 or ntr[b] <= 1):
            why = "hapax"
        if num:
            vals = {num.get(s, "non") for s in members[ra] | members[rb]}
            if len(vals) > 1 and any(v != "non" for v in vals):
                why = why or "numeral"
        if why:
            skipped.append((a, b, why)); continue
        uf.u(a, b); rn = uf.f(a)
        members[rn] = members[ra] | members[rb]
        kept.append((a, b))
    return {s: uf.f(s) for s in ALLM}, kept, skipped


def band_of(n):
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 9 else 3 if n <= 49 else 4


def permuted(part, ntr, rng):
    """relabel signs by a random permutation within training-count bands, keep class structure."""
    by = defaultdict(list)
    for s in ALLM:
        by[band_of(ntr[s])].append(s)
    pi = {}
    for b, ss in by.items():
        sh = ss[:]; rng.shuffle(sh)
        pi.update(zip(ss, sh))
    # new: s's class = class of pi(s) in part
    return {s: part[pi[s]] for s in ALLM}


def unk_part(ntr, k):
    return {s: ("RARE" if ntr[s] <= k and ntr[s] > 0 else s) for s in ALLM}


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    R = {}
    dev, ho = dev_heldout(version=2)
    train = [r for t in dev for r in runs(t["seq"])]
    test = [runs(t["seq"]) for t in ho]
    test = [x for x in test if x]
    ntr = Counter(s for q in train for s in q)
    PC = json.load(open(ROOT / "experiments/signlist_shape/out/partition_controls.json"))
    I1 = json.load(open(ROOT / "experiments/signlist_shape/out/i1.json"))
    pairs = [(a, b) for a, b, *_ in I1["accepted_shape"]]
    L0 = {s: PC["greedy_shape"].get(s, s) for s in ALLM}
    assert from_pairs(pairs) == {s: from_pairs(pairs)[s] for s in ALLM}
    # check pairs reproduce L0 partition
    same = all((L0[a] == L0[b]) == (from_pairs(pairs)[a] == from_pairs(pairs)[b]) for a in ALLM for b in ALLM[:60])
    num = numeral_table()
    Lnum, kn_, sk_num = constrained(pairs, ntr, num, False)
    Lstr, ks_, sk_str = constrained(pairs, ntr, num, True)
    Lfreq = from_pairs([(a, b) for a, b in pairs if ntr[a] >= 10 and ntr[b] >= 10])
    Lrare = from_pairs([(a, b) for a, b in pairs if ntr[a] < 10 or ntr[b] < 10])
    M77 = {s: s for s in ALLM}
    used = set(ntr)
    lists = {"L0": L0, "L_num": Lnum, "L_strict": Lstr, "L_freq": Lfreq, "L_rare": Lrare}
    R["setup"] = {"n_train_runs": len(train), "n_test_texts": len(test), "pairs_reproduce_L0": same,
                  "labels_all417": {k: len(set(v.values())) for k, v in lists.items()},
                  "labels_used_train": {k: len({v[s] for s in used}) for k, v in lists.items()},
                  "skipped_num": sk_num, "skipped_strict": sk_str,
                  "classes_L0": classes(L0), "classes_strict": classes(Lstr)}
    log("setup", R["setup"]["labels_all417"], "pairs reproduce", same)

    # P0 planted control
    rng = random.Random(1)
    freq = sorted(s for s in ntr if ntr[s] >= 10)
    P0 = []
    for seed in range(3):
        rng = random.Random(seed)
        split = rng.sample(freq, 30)
        def sp(q, r=random.Random(seed + 100)):
            return [s + ".b" if s in split and r.random() < 0.5 else s for s in q]
        rr = random.Random(seed + 100)
        tr2 = [[s + ".b" if s in split and rr.random() < 0.5 else s for s in q] for q in train]
        te2 = [[[s + ".b" if s in split and rr.random() < 0.5 else s for s in q] for q in t] for t in test]
        fine = {}
        back = {s + ".b": s for s in split}
        others = [s for s in freq if s not in split]
        rp = rng.sample(others, 60)
        rnd = {rp[2 * i]: rp[2 * i + 1] for i in range(30)}
        tr_ = {}
        A = score(fine, tr2, te2); Bk = score(back, tr2, te2); C = score(rnd, tr2, te2)
        P0.append({"seed": seed, "true_merge": diff(Bk, A), "random_merge": diff(C, A)})
        log("P0", seed, P0[-1])
    R["P0"] = P0

    base = {}
    models = [("kn", 3), ("kn", 2), ("kn", 4), ("wb", 3)]
    for sm, o in models:
        base[(sm, o)] = score(M77, train, test, o, sm)
    # T1
    T1 = {}
    for name, L in lists.items():
        T1[name] = {}
        for sm, o in models:
            S = score(L, train, test, o, sm)
            T1[name][f"{sm}{o}"] = diff(S, base[(sm, o)])
            if (sm, o) == ("kn", 3):
                T1[name]["T2_freq"] = diff(S, base[(sm, o)], ntr, "freq")
                T1[name]["T2_rare"] = diff(S, base[(sm, o)], ntr, "rare")
        log("T1", name, {k: round(v["d"], 4) for k, v in T1[name].items()})
    R["T1"] = T1
    B0 = base[("kn", 3)]

    # T3a band-matched null
    T3 = {}
    for name in ("L_strict", "L0", "L_num"):
        obs = T1[name]["kn3"]["d"]
        rng = random.Random(7)
        nulls = []
        ntok = T1[name]["kn3"]["n_tok"]
        btot = tot(B0)
        for i in range(300):
            P = permuted(lists[name], ntr, rng)
            nulls.append((tot(score(P, train, test)) - btot) / ntok)
        nulls = np.array(nulls)
        T3[name] = {"obs": obs, "null_mean": float(nulls.mean()), "null_q95": float(np.percentile(nulls, 95)),
                    "null_max": float(nulls.max()), "p": float((1 + (nulls >= obs).sum()) / (1 + len(nulls)))}
        log("T3a", name, T3[name])
    T3["unk"] = {}
    for k in (1, 2, 4, 9):
        P = unk_part(ntr, k)
        S = score(P, train, test)
        T3["unk"][k] = {"n_lumped": sum(1 for s in ntr if ntr[s] <= k), "all": diff(S, B0),
                        "freq": diff(S, B0, ntr, "freq"), "rare": diff(S, B0, ntr, "rare")}
        log("T3b unk", k, {a: round(b["d"], 4) if isinstance(b, dict) else b for a, b in T3["unk"][k].items()})
    R["T3"] = T3

    # T5 attribution
    T5 = {}
    for name in ("L_strict", "L0"):
        rows = []
        for cl in classes(lists[name]):
            P = dict(M77)
            for s in cl:
                P[s] = cl[0]
            d = diff(score(P, train, test), B0, Bn=500)
            rows.append({"class": cl, "train_n": [ntr[s] for s in cl], **d})
        rows.sort(key=lambda r: -r["d"])
        T5[name] = rows
        log("T5", name, [(r["class"], round(r["d"], 4)) for r in rows[:8]])
    R["T5"] = T5

    # path (descriptive)
    path = []
    for k in range(0, len(ks_) + 1, 4):
        P = from_pairs(ks_[:k])
        path.append((k, len({P[s] for s in used}), (tot(score(P, train, test)) - tot(B0)) / T1["L0"]["kn3"]["n_tok"]))
    R["path_strict"] = path
    log("path", path)

    # T4 ICIT
    C = json.load(open(ROOT / "experiments/consensus_corpus/out/concordance.json"))["primary"]
    I = distinct(icit_texts())
    tr_i = [r for t in I if t["site"] not in POST1977 for r in runs(t["seq"])]
    te_i = [runs(t["seq"]) for t in I if t["site"] in POST1977]
    te_i = [x for x in te_i if x]
    Ws = sorted({s for q in tr_i for s in q} | {s for t in te_i for r in t for s in r})
    ntrw = Counter(s for q in tr_i for s in q)
    Wfine = {w: w for w in Ws}
    BW = score(Wfine, tr_i, te_i)
    T4 = {"n_train_runs": len(tr_i), "n_test_texts": len(te_i), "test_sites": Counter(t["site"] for t in I if t["site"] in POST1977)}
    for name in ("L0", "L_num", "L_strict"):
        uf = UF(); n_m = 0
        for cl in classes(lists[name]):
            ws = [w for m in cl for w in C.get(m, [])]
            mapped_m = [m for m in cl if C.get(m)]
            if len(mapped_m) >= 2:
                n_m += 1
                # merge across M signs: union first W of each M; keep Wells' own splits of one M apart
                firsts = [C[m][0] for m in mapped_m]
                for w in firsts[1:]:
                    uf.u(firsts[0], w)
        P = {w: uf.f(w) for w in Ws}
        S = score(P, tr_i, te_i)
        T4[name] = {"n_classes_mapped": n_m, "all": diff(S, BW), "freq": diff(S, BW, ntrw, "freq"),
                    "rare": diff(S, BW, ntrw, "rare")}
        log("T4", name, n_m, T4[name]["all"])
    R["T4"] = T4
    R["sec"] = time.time() - t0
    json.dump(R, open(OUT / "results.json", "w"), indent=1, default=str)
    log("done", R["sec"])


if __name__ == "__main__":
    main()
