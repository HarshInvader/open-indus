"""Shared code for experiments/grammar: data units, class-bigram grammar, baselines, restoration.

The grammar is a hard class bigram ("class HMM with one class per sign"):
    P(text) = P(c1|BOS) P(s1|c1) * prod_i P(c_i|c_{i-1}) P(s_i|c_i) * P(EOS|c_L)
Classes are induced on dev by the exchange algorithm (Kneser & Ney 1993 / Brown et al. 1992),
initialised from the seed classes of earlier experiments, and then named with fixed positional rules
(opener / medial / connective / numeral / closer / post-closer / unclassified).

Units: DISTINCT texts. Line breaks '|' are dropped (lines read on). '#' breaks cut a text into runs.
A run carries BOS only if it starts a text whose beginning is preserved, EOS likewise; M77 texts
marked incomplete without '#' get neither (conservative). Perplexity is scored on complete texts only.
"""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, dev_heldout, distinct  # noqa: E402
from corpus.build import _close  # noqa: E402

UNK = "<UNK>"
LABELS = ["opener", "medial", "connective", "numeral", "closer", "post-closer", "unclassified"]

# ---------------------------------------------------------------- seeds (graphic numerals, connective)
NUM = {"M77": set(), "ICIT": set()}
CONN = {"M77": {"M99", "M123"}, "ICIT": {"W002"}}
for r in csv.DictReader(open(ROOT / "experiments/numeral_grammar/inventory.csv")):
    if r["cls"] in ("S", "T", "V", "D", "A"):
        NUM[r["corpus"]].add(r["sign"])
NUM["UR3"] = set(); CONN["UR3"] = set()
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": [f"M{m}" for m in v["M"]] for k, v in BRIDGE.items()}
M2W = defaultdict(list)
for w, ms in W2M.items():
    for m in ms:
        M2W[m].append(w)

M77_OLD_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar",
           "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Dilmun",
           "Kalba", "Gonur", "Gonur Depe", "Altyn Depe", "Shortughai"}


def m77_register(ot):
    return {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet", "copper tablet": "copper",
            "pottery graffito": "pottery"}.get(ot, "other")


def icit_register(tp):
    if tp in ("SEAL:R", "SEAL:C", "SEAL:CY"):
        return "round_seal"
    if tp.startswith("SEAL"):
        return "seal"
    if tp.startswith("TAG"):
        return "sealing"
    if tp == "TAB:C":
        return "copper"
    if tp.startswith("TAB"):
        return "tablet"
    if tp.startswith("PO"):
        return "pottery"
    return "other"


def make_runs(seq, complete):
    s = [x for x in seq if x != "|"]
    if "#" not in s:
        return [(tuple(s), bool(complete), bool(complete))] if s else []
    out, cur = [], []
    for x in s:
        if x == "#":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(x)
    if cur:
        out.append(cur)
    runs = []
    for i, r in enumerate(out):
        bos = i == 0 and s[0] != "#"
        eos = i == len(out) - 1 and s[-1] != "#"
        runs.append((tuple(r), bos, eos))
    return runs


def unit_from(seq, complete, **meta):
    runs = make_runs(seq, complete)
    full = len(runs) == 1 and runs[0][1] and runs[0][2]
    return dict(runs=runs, full=full, signs=tuple(x for x in seq if x not in ("|", "#")), **meta)


def m77_units(split="dev"):
    dev, ho = dev_heldout(version=2)
    src = {"dev": dev, "heldout": ho, "all": dev + ho}[split]
    out = []
    for t in src:
        u = unit_from(t["seq"], t["complete"], register=m77_register(t["object_type"]), site=t["site"],
                      key=" ".join(t["seq"]), split=split, n_lines=t.get("n_lines", 1))
        if u["runs"]:
            out.append(u)
    return out


def icit_units(sites=None, exclude_sites=None, types=None):
    """distinct ICIT inscriptions (distinct by sign sequence + site class)"""
    seen, out = set(), []
    for t in icit_texts():
        if sites is not None and t["site"] not in sites:
            continue
        if exclude_sites is not None and t["site"] in exclude_sites:
            continue
        reg = icit_register(t["type"])
        if types is not None and reg not in types:
            continue
        k = " ".join(t["seq"])
        if k in seen:
            continue
        seen.add(k)
        try:
            w, h = float(t.get("width_mm") or 0), float(t.get("height_mm") or 0)
        except ValueError:
            w = h = 0.0
        u = unit_from(t["seq"], t["complete"], register=reg, site=t["site"], key=k, type=t["type"],
                      width=w, height=h, period=t.get("period"), cisi=t.get("cisi"))
        if u["runs"]:
            out.append(u)
    return out


def to_m(w):
    ms = W2M.get(w)
    return ms[0] if ms else UNK


def bridge_unit(u):
    """map an ICIT unit to M77 signs (first listed M for each bridged W; unbridged -> UNK)"""
    v = dict(u)
    v["runs"] = [(tuple(to_m(x) for x in r), b, e) for r, b, e in u["runs"]]
    v["signs"] = tuple(to_m(x) for x in u["signs"])
    v["n_unbridged"] = sum(1 for x in u["signs"] if x not in W2M)
    return v


def icit_devlike(heldout_units):
    """ICIT texts at Indus sites with NO near-copy among M77 held-out texts (after bridging):
    used to induce Wells classes without touching held-out families."""
    ho = [list(u["signs"]) for u in heldout_units]
    ho_set = {tuple(s) for s in ho}
    by_len = defaultdict(list)
    for s in ho:
        by_len[len(s)].append(s)
    out = []
    for u in icit_units(exclude_sites=FOREIGN | {"Unknown"}):
        m = [to_m(x) for x in u["signs"]]
        if tuple(m) in ho_set:
            continue
        near = False
        for L in range(len(m) - 1, len(m) + 2):
            for s in by_len.get(L, []):
                if _close(m, s):
                    near = True; break
            if near:
                break
        if not near and len(m) >= 3:
            for L in range(len(m) + 2, 18):
                for s in by_len.get(L, []):
                    if _close(m, s):
                        near = True; break
                if near:
                    break
        if not near:
            out.append(u)
    return out


def families(units):
    """connected near-copy families (same rule as splits_v2) -> list of family index per unit.
    If every unit carries a 'fam' key (e.g. Ur III owner name), that grouping is used instead."""
    if units and all("fam" in u for u in units):
        roots = {}
        return [roots.setdefault(u["fam"], len(roots)) for u in units]
    sg = [list(u["signs"]) for u in units]
    parent = list(range(len(units)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    by_len = defaultdict(list)
    for i, s in enumerate(sg):
        by_len[len(s)].append(i)
    for i, s in enumerate(sg):
        if not s:
            continue
        for L in by_len:
            if L < len(s):
                continue
            if L > len(s) + 1 and len(s) < 3:
                continue
            for j in by_len[L]:
                if j <= i and L == len(s):
                    continue
                if _close(s, sg[j]):
                    parent[find(i)] = find(j)
    roots = {}
    return [roots.setdefault(find(i), len(roots)) for i in range(len(units))]


def family_folds(units, k=5, seed=0):
    fam = families(units)
    ids = sorted(set(fam))
    rng = random.Random(seed); rng.shuffle(ids)
    fold_of = {f: i % k for i, f in enumerate(ids)}
    return [fold_of[f] for f in fam]


# ---------------------------------------------------------------- vocabulary
def build_vocab(units, min_count=2):
    c = Counter(x for u in units for r, _, _ in u["runs"] for x in r)
    return {w for w, n in c.items() if n >= min_count}, c


def mapv(run, vocab):
    return tuple(x if x in vocab else UNK for x in run)


# ---------------------------------------------------------------- class bigram (the grammar)
def _g(x):
    x = np.asarray(x, float)
    return np.where(x > 0, x * np.log(np.where(x > 0, x, 1)), 0.0)


class ClassBigram:
    """hard class bigram; classes 0..K-1, BOS row index K, EOS column index K"""

    def __init__(self, K, alpha=0.5, min_count=2, disc=None):
        self.K, self.alpha, self.min_count, self.disc = K, alpha, min_count, disc

    # ---- statistics
    def _stats(self, units):
        self.vocab, self.raw_counts = build_vocab(units, self.min_count)
        self.vocab = set(self.vocab) | {UNK}
        words = sorted(self.vocab)
        self.words = words
        self.widx = {w: i for i, w in enumerate(words)}
        V = len(words)
        self.Nt = np.zeros(V)
        self.Nl = np.zeros(V)          # times word is a predecessor in a scored pair
        left = [Counter() for _ in range(V)]    # left neighbour word index (or -1 = BOS)
        right = [Counter() for _ in range(V)]   # right neighbour word index (or -2 = EOS)
        self.n_bos = 0
        for u in units:
            for r, b, e in u["runs"]:
                ids = [self.widx[x] for x in mapv(r, self.vocab)]
                for i in ids:
                    self.Nt[i] += 1
                if b and ids:
                    left[ids[0]][-1] += 1; self.n_bos += 1
                for a, c in zip(ids, ids[1:]):
                    right[a][c] += 1; left[c][a] += 1; self.Nl[a] += 1
                if e and ids:
                    right[ids[-1]][-2] += 1; self.Nl[ids[-1]] += 1
        self.left, self.right = left, right

    def _matrix(self, cls):
        K = self.K
        M = np.zeros((K + 1, K + 1))
        for a in range(len(self.words)):
            for c, n in self.right[a].items():
                M[cls[a], K if c == -2 else cls[c]] += n
            if -1 in self.left[a]:
                M[K, cls[a]] += self.left[a][-1]
        Nl = np.zeros(K + 1); Nt = np.zeros(K)
        np.add.at(Nl, cls, self.Nl); np.add.at(Nt, cls, self.Nt)
        Nl[K] = self.n_bos
        return M, Nl, Nt

    def _ll(self, M, Nl, Nt):
        return _g(M).sum() - _g(Nl).sum() - _g(Nt).sum()

    def _exchange(self, cls, max_sweeps=30, rng=None):
        K = self.K
        cls = np.array(cls)
        M, Nl, Nt = self._matrix(cls)
        order = list(range(len(self.words)))
        for sweep in range(max_sweeps):
            moved = 0
            if rng is not None:
                rng.shuffle(order)
            for w in order:
                a = cls[w]
                Lw = np.zeros(K + 1); Rw = np.zeros(K + 1); selfc = 0
                for x, n in self.left[w].items():
                    if x == w:
                        selfc += n
                    elif x == -1:
                        Lw[K] += n
                    else:
                        Lw[cls[x]] += n
                for y, n in self.right[w].items():
                    if y == w:
                        continue
                    Rw[K if y == -2 else cls[y]] += n
                # remove w from a
                M[:, a] -= Lw; M[a, :] -= Rw; M[a, a] -= selfc
                Nl[a] -= self.Nl[w]; Nt[a] -= self.Nt[w]
                R = M[:K, :]                      # rows b (K x K+1)
                C = M[:, :K]                      # cols b (K+1 x K)
                d = (_g(R + Rw[None, :]).sum(1) - _g(R).sum(1)) + (_g(C + Lw[:, None]).sum(0) - _g(C).sum(0))
                diag = np.diagonal(M)[:K]
                d -= (_g(diag + Rw[:K]) - _g(diag)) + (_g(diag + Lw[:K]) - _g(diag))
                d += _g(diag + Rw[:K] + Lw[:K] + selfc) - _g(diag)
                d -= (_g(Nl[:K] + self.Nl[w]) - _g(Nl[:K])) + (_g(Nt + self.Nt[w]) - _g(Nt))
                b = int(np.argmax(d))
                if d[a] >= d[b] - 1e-9:
                    b = a
                M[:, b] += Lw; M[b, :] += Rw; M[b, b] += selfc
                Nl[b] += self.Nl[w]; Nt[b] += self.Nt[w]
                if b != a:
                    cls[w] = b; moved += 1
            if moved == 0:
                break
        return cls, self._ll(*self._matrix(cls))

    def fit_fixed(self, units, assign, default):
        """fit transitions/emissions with a FIXED class assignment (dict word -> class index)"""
        self._stats(units)
        self.cls = np.array([assign.get(w, default) for w in self.words])
        self.train_ll = self._ll(*self._matrix(self.cls))
        self._finalize()
        return self

    def fit(self, units, init=None, restarts=3, seed=0):
        """init: dict word -> seed label (str); seeds are spread over K classes by frequency"""
        self._stats(units)
        V = len(self.words)
        rng = random.Random(seed)
        best = None
        for r in range(restarts):
            if init is not None and r == 0:
                cls = self._seed_init(init)
            else:
                order = sorted(range(V), key=lambda i: -self.Nt[i])
                cls = np.zeros(V, int)
                for j, i in enumerate(order):
                    cls[i] = j % self.K if j < self.K else rng.randrange(self.K)
            cls, ll = self._exchange(cls, rng=rng)
            if best is None or ll > best[1]:
                best = (cls, ll)
        self.cls = best[0]
        self.train_ll = best[1]
        self._finalize()
        return self

    def _seed_init(self, init):
        """seed labels -> classes: each seed label owns a block of classes; frequent words first"""
        K = self.K
        labs = sorted({init.get(w, "medial") for w in self.words})
        share = Counter(init.get(w, "medial") for w in self.words)
        alloc, rem = {}, K
        for i, l in enumerate(labs):
            alloc[l] = max(1, round(K * share[l] / len(self.words))) if i < len(labs) - 1 else max(1, rem)
            rem -= alloc[l]
        start, blocks = 0, {}
        for l in labs:
            n = max(1, alloc[l])
            blocks[l] = [min(K - 1, start + j) for j in range(n)]
            start += n
        cls = np.zeros(len(self.words), int)
        cnt = Counter()
        for i in sorted(range(len(self.words)), key=lambda i: -self.Nt[i]):
            l = init.get(self.words[i], "medial")
            cls[i] = blocks[l][cnt[l] % len(blocks[l])]; cnt[l] += 1
        return cls

    def _finalize(self):
        K, a = self.K, self.alpha
        M, Nl, Nt = self._matrix(self.cls)
        self.M, self.NlC, self.NtC = M, Nl, Nt
        if self.disc is None:
            T = (M + a) / (M.sum(1, keepdims=True) + a * (K + 1))
        else:   # absolute discounting, back-off to a smoothed class continuation distribution
            d = self.disc
            cont = (M > 0).sum(0) + a
            cont = cont / cont.sum()
            rs = M.sum(1, keepdims=True)
            ntyp = (M > 0).sum(1, keepdims=True)
            lam = np.where(rs > 0, d * ntyp / np.maximum(rs, 1e-12), 1.0)
            T = np.maximum(M - d, 0) / np.maximum(rs, 1e-12) + lam * cont[None, :]
            T = T / T.sum(1, keepdims=True)
        self.T = T                     # rows: classes + BOS ; cols: classes + EOS
        self.logT = np.log2(T)
        self.emit = np.array([self.Nt[i] / max(Nt[self.cls[i]], 1e-12) for i in range(len(self.words))])
        self.logE = np.log2(np.maximum(self.emit, 1e-300))
        self.cls_of = {w: int(self.cls[i]) for i, w in enumerate(self.words)}
        # class marginal for BOS-less starts
        self.pc = Nt / Nt.sum()

    def n_params(self):
        K = self.K
        if self.disc is None:
            return (K + 1) * K + (len(self.words) - K)
        # discounted model: observed class-pair cells + continuation distribution + emissions
        return int((self.M > 0).sum()) + K + (len(self.words) - K)

    def run_logp(self, r, b, e):
        r = mapv(r, self.vocab)
        if not r:
            return 0.0, 0
        lp, n = 0.0, 0
        prev = None
        for i, x in enumerate(r):
            wi = self.widx[x]; c = self.cls[wi]
            if i == 0:
                lp += self.logT[self.K, c] if b else math.log2(self.pc[c])
            else:
                lp += self.logT[prev, c]
            lp += self.logE[wi]; n += 1; prev = c
        if e:
            lp += self.logT[prev, self.K]; n += 1
        return lp, n

    def unit_logp(self, u):
        lp = n = 0
        for r, b, e in u["runs"]:
            a, m = self.run_logp(r, b, e); lp += a; n += m
        return lp, n

    # ---- restoration: log2 P(text with x at position j) for all vocab words x
    def fill_scores(self, toks, j, bos=True, eos=True):
        K = self.K
        t = list(mapv(toks, self.vocab))
        cands = self.words
        cl = self.cls
        lp_left = self.logT[K, :K] if (j == 0 and bos) else (self.logT[self.cls_of[t[j - 1]], :K] if j > 0 else np.log2(self.pc))
        if j == len(t) - 1:
            lp_right = self.logT[:K, K] if eos else np.zeros(K)
        else:
            lp_right = self.logT[:K, self.cls_of[t[j + 1]]]
        return np.array([lp_left[cl[i]] + self.logE[i] + lp_right[cl[i]] for i in range(len(cands))])


# ---------------------------------------------------------------- baselines
class KNBigram:
    """interpolated Kneser-Ney bigram with BOS/EOS on the same vocabulary as the grammar"""

    def __init__(self, d=0.75, min_count=2):
        self.d, self.min_count = d, min_count

    def fit(self, units):
        self.vocab, _ = build_vocab(units, self.min_count)
        self.vocab = set(self.vocab) | {UNK}
        big = Counter(); ctx = Counter(); cont = defaultdict(set); uni = Counter()
        for u in units:
            for r, b, e in u["runs"]:
                t = list(mapv(r, self.vocab))
                for x in t:
                    uni[x] += 1
                seq = (["<s>"] if b else []) + t + (["</s>"] if e else [])
                for a, c in zip(seq, seq[1:]):
                    big[(a, c)] += 1; ctx[a] += 1; cont[c].add(a)
        self.big, self.ctx = big, ctx
        self.ntypes_after = Counter(a for (a, c) in big)
        tot = sum(len(v) for v in cont.values())
        self.targets = sorted(self.vocab) + ["</s>"]
        floor = 1e-3
        pc = {c: len(cont.get(c, ())) / tot for c in self.targets}
        Z = len(self.targets)
        self.pcont = {c: pc[c] * (1 - floor) + floor / Z for c in self.targets}
        n = sum(uni.values())
        self.puni = {w: (uni.get(w, 0) + 0.5) / (n + 0.5 * len(self.vocab)) for w in self.vocab}
        return self

    def n_params(self):
        return len(self.big) + len(self.targets)

    def p(self, a, c):
        pc = self.pcont[c]
        ca = self.ctx.get(a, 0)
        if ca == 0:
            return pc
        lam = self.d * self.ntypes_after[a] / ca
        return max(self.big.get((a, c), 0) - self.d, 0) / ca + lam * pc

    def run_logp(self, r, b, e):
        t = list(mapv(r, self.vocab))
        if not t:
            return 0.0, 0
        lp = 0.0
        if b:
            seq = ["<s>"] + t
        else:
            lp += math.log2(self.puni[t[0]]); seq = t
        if e:
            seq = seq + ["</s>"]
        for a, c in zip(seq, seq[1:]):
            lp += math.log2(self.p(a, c))
        return lp, len(t) + (1 if e else 0)

    def unit_logp(self, u):
        lp = n = 0
        for r, b, e in u["runs"]:
            a, m = self.run_logp(r, b, e); lp += a; n += m
        return lp, n

    def fill_scores(self, toks, j, bos=True, eos=True, cands=None):
        t = list(mapv(toks, self.vocab))
        cands = cands or sorted(self.vocab)
        left = "<s>" if j == 0 else t[j - 1]
        right = "</s>" if j == len(t) - 1 else t[j + 1]
        out = []
        for x in cands:
            s = math.log2(self.p(left, x)) if (j > 0 or bos) else math.log2(self.puni[x])
            if j < len(t) - 1 or eos:
                s += math.log2(self.p(x, right))
            out.append(s)
        return np.array(out)


class PositionModel:
    """position-only: P(sign | position from start, capped) and P(EOS | length so far)"""

    def __init__(self, cap=4, k=0.5, min_count=2):
        self.cap, self.k, self.min_count = cap, k, min_count
        self.scap = max(cap, 1)

    def fit(self, units):
        self.vocab, _ = build_vocab(units, self.min_count)
        self.vocab = set(self.vocab) | {UNK}
        self.words = sorted(self.vocab)
        cp = defaultdict(Counter); stop = Counter(); go = Counter(); uni = Counter()
        for u in units:
            for r, b, e in u["runs"]:
                t = list(mapv(r, self.vocab))
                for x in t:
                    uni[x] += 1
                if not b:
                    continue
                for i, x in enumerate(t):
                    cp[min(i, self.cap)][x] += 1
                if e:
                    for i in range(1, len(t)):
                        go[min(i, self.scap)] += 1
                    stop[min(len(t), self.scap)] += 1
        n = sum(uni.values())
        self.puni = {w: (uni[w] + self.k) / (n + self.k * len(self.vocab)) for w in self.vocab}
        self.pp = {}
        for i in range(self.cap + 1):
            tot = sum(cp[i].values())
            lam = tot / (tot + 20.0)
            self.pp[i] = {w: lam * cp[i][w] / max(tot, 1) + (1 - lam) * self.puni[w] for w in self.vocab}
        self.pstop = {i: (stop[i] + 1) / (stop[i] + go[i] + 2) for i in range(1, self.scap + 1)}
        return self

    def n_params(self):
        return (self.cap + 1) * (len(self.vocab) - 1) + self.cap

    def run_logp(self, r, b, e):
        t = list(mapv(r, self.vocab))
        if not t:
            return 0.0, 0
        lp = 0.0
        for i, x in enumerate(t):
            p = self.pp[min(i, self.cap)][x] if b else self.puni[x]
            if b and i >= 1:
                p *= 1 - self.pstop[min(i, self.scap)]
            lp += math.log2(p)
        if e:
            lp += math.log2(self.pstop[min(len(t), self.scap)])
        return lp, len(t) + (1 if e else 0)

    def unit_logp(self, u):
        lp = n = 0
        for r, b, e in u["runs"]:
            a, m = self.run_logp(r, b, e); lp += a; n += m
        return lp, n

    def fill_scores(self, toks, j, bos=True, eos=True, cands=None):
        cands = cands or self.words
        return np.array([math.log2(self.pp[min(j, self.cap)][x]) for x in cands])


class Unigram(PositionModel):
    def __init__(self, min_count=2):
        super().__init__(cap=0, min_count=min_count)

    def n_params(self):
        return len(self.vocab)


# ---------------------------------------------------------------- evaluation helpers
def bits(model, units, full_only=True):
    lp = n = 0
    per = []
    for u in units:
        if full_only and not u["full"]:
            continue
        a, m = model.unit_logp(u)
        lp += a; n += m; per.append((-a, m))
    return (-lp / n if n else float("nan")), n, per


def train_ll(model, units):
    lp = n = 0
    for u in units:
        a, m = model.unit_logp(u); lp += a; n += m
    return lp * math.log(2), n           # natural log


def aic_bic(model, units):
    ll, n = train_ll(model, units)
    k = model.n_params()
    return dict(ll_nat=ll, n_events=n, k=k, AIC=2 * k - 2 * ll, BIC=k * math.log(n) - 2 * ll)


def shuffle_units(units, seed=0):
    rng = random.Random(seed)
    out = []
    for u in units:
        v = dict(u)
        rr = []
        for r, b, e in u["runs"]:
            r = list(r); rng.shuffle(r); rr.append((tuple(r), b, e))
        v["runs"] = rr
        v["signs"] = tuple(x for r, _, _ in rr for x in r)
        out.append(v)
    return out


# ---------------------------------------------------------------- functional naming of classes
def class_profiles(model, units, corpus="M77"):
    """positional profile of each class on complete texts (full units, length >= 2)"""
    K = model.K
    prof = np.zeros((K, 4))      # initial, medial, final, standalone
    prev_lab = defaultdict(Counter)
    nxt = defaultdict(Counter)
    num_share = np.zeros(K); conn_share = np.zeros(K); tot = np.zeros(K)
    for u in units:
        for r, b, e in u["runs"]:
            t = mapv(r, model.vocab)
            cs = [model.cls_of[x] for x in t]
            for i, (x, c) in enumerate(zip(r, cs)):
                tot[c] += 1
                if x in NUM[corpus]:
                    num_share[c] += 1
                if x in CONN[corpus]:
                    conn_share[c] += 1
                if not (b and e):
                    continue
                if len(cs) == 1:
                    prof[c, 3] += 1
                elif i == 0:
                    prof[c, 0] += 1
                elif i == len(cs) - 1:
                    prof[c, 2] += 1
                else:
                    prof[c, 1] += 1
                prev_lab[c]["BOS" if i == 0 else cs[i - 1]] += 1
                nxt[c]["EOS" if i == len(cs) - 1 else cs[i + 1]] += 1
    return prof, prev_lab, nxt, num_share / np.maximum(tot, 1), conn_share / np.maximum(tot, 1), tot


def name_classes(model, units, corpus="M77"):
    """fixed rules (decided before any held-out run):
       numeral     >= 50% of class tokens are graphic stroke numerals
       connective  >= 50% of tokens are the seed connective (two short strokes), or medial >= 80%
                   with >= 50% of predecessors opener-class (assigned in a second pass)
       opener      initial share >= 0.40 and initial > final
       closer      final share >= 0.40 and final > initial
       post-closer closer by position AND >= 50% of its tokens follow a closer-class token
       medial      medial share >= 0.50
       unclassified otherwise
    shares are over positions in complete texts of length >= 2 (standalone tokens excluded)."""
    prof, prev, nxt, num, conn, tot = class_profiles(model, units, corpus)
    K = model.K
    lab = ["unclassified"] * K
    sh = prof[:, :3] / np.maximum(prof[:, :3].sum(1, keepdims=True), 1)
    for c in range(K):
        if tot[c] == 0:
            continue
        if num[c] >= 0.5:
            lab[c] = "numeral"
        elif conn[c] >= 0.5:
            lab[c] = "connective"
        elif sh[c, 0] >= 0.40 and sh[c, 0] > sh[c, 2]:
            lab[c] = "opener"
        elif sh[c, 2] >= 0.40 and sh[c, 2] > sh[c, 0]:
            lab[c] = "closer"
        elif sh[c, 1] >= 0.50:
            lab[c] = "medial"
    # second pass: post-closers and connectives defined relative to first-pass labels
    for c in range(K):
        if lab[c] == "closer":
            n = sum(prev[c].values())
            after_closer = sum(v for k, v in prev[c].items() if k != "BOS" and lab[k] == "closer" and k != c)
            if n and after_closer / n >= 0.5:
                lab[c] = "post-closer"
        elif lab[c] == "medial" and sh[c, 1] >= 0.8:
            n = sum(prev[c].values())
            after_op = sum(v for k, v in prev[c].items() if k != "BOS" and lab[k] == "opener")
            if n and after_op / n >= 0.5:
                lab[c] = "connective"
    return lab, dict(profile=prof.tolist(), tokens=tot.tolist(), numeral_share=num.tolist(),
                     connective_share=conn.tolist())


def rare_posterior(model, units, sign, labels):
    """for a sign mapped to UNK: posterior over classes from its contexts, aggregated to labels"""
    K = model.K
    logp = np.zeros(K)
    n = 0
    for u in units:
        for r, b, e in u["runs"]:
            for i, x in enumerate(r):
                if x != sign:
                    continue
                n += 1
                t = mapv(r, model.vocab)
                if i > 0:
                    logp += model.logT[model.cls_of[t[i - 1]], :K]
                elif b:
                    logp += model.logT[K, :K]
                if i < len(r) - 1:
                    logp += model.logT[:K, model.cls_of[t[i + 1]]]
                elif e:
                    logp += model.logT[:K, K]
    logp = logp * math.log(2)
    p = np.exp(logp - logp.max()); p /= p.sum()
    agg = Counter()
    for c in range(K):
        agg[labels[c]] += p[c]
    return agg, n


# ---------------------------------------------------------------- register offsets
class RegisterGrammar:
    """pooled class grammar + per-register transitions/emissions shrunk toward the pooled ones:
         T_r(c'|c) = (N_r(c,c') + beta * T(c'|c)) / (N_r(c) + beta)
         E_r(w|c)  = (N_r(w)   + gamma * E(w|c)) / (N_r(c) + gamma)
    """

    def __init__(self, base, beta=20.0, gamma=20.0):
        self.base, self.beta, self.gamma = base, beta, gamma

    def fit(self, units):
        b = self.base
        K = b.K
        self.reg = {}
        regs = sorted({u["register"] for u in units})
        for r in regs:
            M = np.zeros((K + 1, K + 1)); Nw = np.zeros(len(b.words)); Nc = np.zeros(K)
            for u in units:
                if u["register"] != r:
                    continue
                for run, bo, eo in u["runs"]:
                    ids = [b.widx[x] for x in mapv(run, b.vocab)]
                    cs = [b.cls[i] for i in ids]
                    for i, c in zip(ids, cs):
                        Nw[i] += 1; Nc[c] += 1
                    if bo and cs:
                        M[K, cs[0]] += 1
                    for x, y in zip(cs, cs[1:]):
                        M[x, y] += 1
                    if eo and cs:
                        M[cs[-1], K] += 1
            T = (M + self.beta * b.T) / (M.sum(1, keepdims=True) + self.beta)
            E = (Nw + self.gamma * b.emit) / (Nc[b.cls] + self.gamma)
            self.reg[r] = dict(T=T, logT=np.log2(T), E=E, logE=np.log2(np.maximum(E, 1e-300)), n_texts=sum(
                u["register"] == r for u in units), M=M)
        return self

    def unit_logp(self, u):
        b = self.base
        R = self.reg.get(u["register"])
        if R is None:
            return b.unit_logp(u)
        lp = n = 0
        K = b.K
        for run, bo, eo in u["runs"]:
            t = mapv(run, b.vocab)
            prev = None
            for i, x in enumerate(t):
                wi = b.widx[x]; c = b.cls[wi]
                if i == 0:
                    lp += R["logT"][K, c] if bo else math.log2(b.pc[c])
                else:
                    lp += R["logT"][prev, c]
                lp += R["logE"][wi]; n += 1; prev = c
            if eo and t:
                lp += R["logT"][prev, K]; n += 1
        return lp, n
