"""Independent red team of experiments/decipherability (board #46).

Written from the pre-registration docs/prereg/redteam_decipherability.md only.
No code from experiments/decipherability is imported or copied; its raw/ text
files are read as data.

Run from repo root:
  .venv/bin/python -I experiments/redteam_decipherability/rt.py gate
  .venv/bin/python -I experiments/redteam_decipherability/rt.py full
Results append to experiments/redteam_decipherability/out/runs.jsonl (resumable).
"""
import json
import math
import random
import re
import sys
import unicodedata
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "experiments" / "decipherability" / "raw"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

CONS = list("pbtdkgmnlrsfvhj")
VOWS = list("aeiou")
# value inventory: CV, bare C, bare V, plus LOGO and boundary
VALUES = [c + v for c in CONS for v in VOWS] + CONS + VOWS + ["LOGO", "#"]
VIDX = {v: i for i, v in enumerate(VALUES)}
SYL_VALUES = [v for v in VALUES if v not in ("LOGO", "#")]
NV = len(VALUES)
BND = VIDX["#"]
LOGO = VIDX["LOGO"]

PAIRS = {
    "lat": {"src": "caesar.txt", "rel": "wiki_it.txt", "wrong": "wiki_et.txt"},
    "fin": {"src": "kalevala.txt", "rel": "wiki_et.txt", "wrong": "wiki_it.txt"},
}


# ---------------------------------------------------------------- text prep
def strip_gutenberg(t):
    a = t.find("*** START")
    if a >= 0:
        t = t[t.find("\n", a) + 1:]
    b = t.find("*** END")
    if b >= 0:
        t = t[:b]
    return t


def fold_word(w):
    w = w.lower()
    w = unicodedata.normalize("NFKD", w)
    w = "".join(ch for ch in w if not unicodedata.combining(ch))
    w = w.replace("y", "i").replace("x", "ks").replace("z", "s").replace("w", "v")
    w = w.replace("c", "k").replace("q", "k")
    w = re.sub(r"[^a-z]", "", w)
    w = re.sub(r"(.)\1+", r"\1", w)  # collapse doubles (length/gemination unwritten)
    return "".join(ch for ch in w if ch in CONS or ch in VOWS)


def syllabify(w):
    units, cl = [], []
    for ch in w:
        if ch in VOWS:
            if cl:
                units.extend(cl[:-1])
                units.append(cl[-1] + ch)
            else:
                units.append(ch)
            cl = []
        else:
            cl.append(ch)
    units.extend(cl)
    return units


def paragraphs(fname):
    t = (RAW / fname).read_text(encoding="utf-8", errors="ignore")
    t = strip_gutenberg(t)
    paras = [p for p in re.split(r"\n\s*\n|\n", t) if p.strip()]
    out = []
    for p in paras:
        ws = [fold_word(w) for w in re.findall(r"[^\W\d_]+", p)]
        ws = [w for w in ws if w]
        if ws:
            out.append(ws)
    return out


def logo_set(words, q):
    if q <= 0:
        return set()
    c = Counter(words)
    total = sum(c.values())
    got, s = 0, set()
    for w, n in c.most_common():
        if got / total >= q:
            break
        s.add(w)
        got += n
    return s


def word_values(w, logos):
    if w in logos:
        return [LOGO]
    return [VIDX[u] for u in syllabify(w)]


# ---------------------------------------------------------------- language model
def train_lm(paras, q, alpha=0.1, max_words=None):
    """Bigram over values with boundary; training texts = 1-2 word chunks like the corpus."""
    words = [w for p in paras for w in p]
    if max_words:
        words = words[:max_words]
    logos = logo_set(words, q)
    C = np.full((NV, NV), alpha)
    # train on running text cut into short chunks, mirroring the genre
    rng = random.Random(7)
    i = 0
    while i < len(words):
        k = 1 if rng.random() < 0.5 else 2
        chunk = words[i:i + k]
        i += k
        seq = [BND]
        for w in chunk:
            seq += word_values(w, logos)
        seq.append(BND)
        for a, b in zip(seq, seq[1:]):
            C[a, b] += 1
    C[:, BND] += 0  # boundary can follow anything
    P = C / C.sum(axis=1, keepdims=True)
    return np.log(P)


# ---------------------------------------------------------------- planted corpus
def make_corpus(paras, ntok, q, rng, p_one):
    words = [w for p in paras for w in p]
    logos = logo_set(words, q)
    # candidate texts: consecutive 1-2 word chunks within paragraphs
    cands = []
    for p in paras:
        i = 0
        while i < len(p):
            k = 1 if rng.random() < p_one else 2
            cands.append(tuple(p[i:i + k]))
            i += k
    rng.shuffle(cands)
    seen, texts, n = set(), [], 0
    for c in cands:
        if c in seen:
            continue
        seen.add(c)
        vals = []
        for w in c:
            vals += word_values(w, logos) if w not in logos else [("W", w)]
        texts.append(vals)
        n += len(vals)
        if n >= ntok:
            break
    # assign signs: one sign per syllable value used; one sign per logogram word
    syl_used = sorted({v for t in texts for v in t if not isinstance(v, tuple)})
    logo_words = sorted({v[1] for t in texts for v in t if isinstance(v, tuple)})
    signs = [("S", v) for v in syl_used] + [("L", w) for w in logo_words]
    order = list(range(len(signs)))
    rng.shuffle(order)
    sid = {signs[i]: j for j, i in enumerate(order)}
    true_val = {}
    for s, j in sid.items():
        true_val[j] = s[1] if s[0] == "S" else LOGO
    seqs = []
    for t in texts:
        seqs.append([sid[("S", v)] if not isinstance(v, tuple) else sid[("L", v[1])] for v in t])
    return seqs, true_val, n


def collapse(seqs, true_val):
    """Merge all logogram signs into one fixed pseudo-sign (value LOGO); index syllabic signs 0..S-1."""
    syl = sorted(s for s, v in true_val.items() if v != LOGO)
    idx = {s: i for i, s in enumerate(syl)}
    S = len(syl)
    LG, B = S, S + 1  # pseudo-sign for logograms, boundary pseudo-sign
    N = np.zeros((S + 2, S + 2))
    cnt = np.zeros(S + 2)
    for t in seqs:
        m = [B] + [idx.get(s, LG) for s in t] + [B]
        for a, b in zip(m, m[1:]):
            N[a, b] += 1
        for x in m[1:-1]:
            cnt[x] += 1
    truth = np.array([true_val[s] for s in syl] + [LOGO, BND])
    return N, cnt, truth, S


# ---------------------------------------------------------------- scoring and search
def score(key, N, cnt, L, S):
    lm = float((N * L[np.ix_(key, key)]).sum())
    c = cnt[:S]
    cv = np.bincount(key[:S], weights=c, minlength=NV)
    ch = float((c[c > 0] * np.log(c[c > 0])).sum() - (cv[cv > 0] * np.log(cv[cv > 0])).sum())
    return lm + ch


def cond(s, key, N, cnt, L, S, cv):
    """Score change for every candidate value of syllabic sign s (vector over SYL value ids)."""
    others = key.copy()
    row = N[s].copy()
    col = N[:, s].copy()
    self_ = N[s, s]
    row[s] = 0
    col[s] = 0
    cand = np.arange(NV - 2)  # syllabic values only (exclude LOGO, #)
    vals = L[np.ix_(cand, others)] @ row + L[np.ix_(others, cand)].T @ col + self_ * L[cand, cand]
    c = cnt[s]
    if c > 0:
        base = cv.copy()
        base[key[s]] -= c
        def xlogx(x):
            return np.where(x > 0, x * np.log(np.maximum(x, 1e-300)), 0.0)
        new = base[cand] + c
        vals = vals - (xlogx(new) - xlogx(base[cand]))
    return vals


def search(N, cnt, L, S, rng, init=None, sweeps=300, t0=3.0, greedy_only=False):
    nprng = np.random.default_rng(rng.randrange(1 << 30))
    key = np.zeros(S + 2, dtype=int)
    key[S] = LOGO
    key[S + 1] = BND
    if init is None:
        key[:S] = nprng.integers(0, NV - 2, S)
    else:
        key[:S] = init[:S]
    temps = [0.0] * 10 if greedy_only else list(np.linspace(t0, 1.0, sweeps - 10)) + [0.0] * 10
    for T in temps:
        cv = np.bincount(key[:S], weights=cnt[:S], minlength=NV).astype(float)
        for s in nprng.permutation(S):
            if cnt[s] == 0:
                continue
            v = cond(s, key, N, cnt, L, S, cv)
            if T == 0:
                new = int(np.argmax(v))
            else:
                z = (v - v.max()) / T
                p = np.exp(z)
                p /= p.sum()
                new = int(nprng.choice(len(p), p=p))
            cv[key[s]] -= cnt[s]
            key[s] = new
            cv[new] += cnt[s]
    return key, score(key, N, cnt, L, S)


def accuracy(key, truth, cnt, S):
    c = cnt[:S]
    return float((c * (key[:S] == truth[:S])).sum() / c.sum())


# ---------------------------------------------------------------- experiment
def one_run(pair, ntok, q, model, rep, restarts=4, shuffles=0):
    cfg = PAIRS[pair]
    rng = random.Random(zlib.crc32(f"{pair}|{ntok}|{q}|{rep}".encode()))  # same corpus for K0/K2
    paras = paragraphs(cfg["src"])
    half_a = [p for i, p in enumerate(paras) if i % 2 == 0]
    half_b = [p for i, p in enumerate(paras) if i % 2 == 1]
    wl = np.mean([len(word_values(w, set())) for p_ in half_a for w in p_])
    p_one = float(min(1.0, max(0.0, 2.0 - 4.5 / wl)))  # mean words/text = 4.5 / mean signs per word
    seqs, true_val, n = make_corpus(half_a, ntok, q, rng, p_one)
    if model == "K0":
        L = train_lm(half_b, q)
    elif model == "K2":
        L = train_lm(paragraphs(cfg["rel"]), q)
    else:  # wrong (cross-pair)
        L = train_lm(paragraphs(cfg["wrong"]), q)
    N, cnt, truth, S = collapse(seqs, true_val)
    srng = random.Random(rep * 1000 + zlib.crc32(model.encode()) % 997)
    true_key = truth.copy()
    s_true = score(true_key, N, cnt, L, S)
    runs = []
    for r in range(restarts):
        k, sc = search(N, cnt, L, S, srng)
        runs.append((sc, accuracy(k, truth, cnt, S)))
    kt, sct = search(N, cnt, L, S, srng, init=true_key, greedy_only=True)
    climb = (sct, accuracy(kt, truth, cnt, S))
    best = max(runs)
    wrong = [r for r in runs + [climb] if r[1] < 0.5]
    best_wrong = max(wrong)[0] if wrong else None
    rec = {
        "pair": pair, "ntok": ntok, "q": q, "model": model, "rep": rep,
        "tokens": int(cnt[:S + 1].sum()), "texts": len(seqs),
        "mean_len": float(np.mean([len(t) for t in seqs])), "S_syl": int(S),
        "blind_acc": best[1], "blind_score": best[0], "restart_accs": [r[1] for r in runs],
        "true_score": s_true, "climb_acc": climb[1], "climb_score": climb[0],
        "wrong_beats_true": bool(best_wrong is not None and best_wrong > s_true),
        "gap_per_tok": ((max(r[0] for r in runs + [climb]) - s_true) / float(cnt[:S + 1].sum())),
    }
    if shuffles:
        sh = []
        for i in range(shuffles):
            flat = [s for t in seqs for s in t]
            srng.shuffle(flat)
            out, j = [], 0
            for t in seqs:
                out.append(flat[j:j + len(t)])
                j += len(t)
            N2, cnt2, truth2, S2 = collapse(out, true_val)
            sh.append(max(search(N2, cnt2, L, S2, srng)[1] for _ in range(2)))
        sh = np.array(sh)
        rec["shuffle_best"] = sh.tolist()
        rec["z_vs_shuffle"] = float((best[0] - sh.mean()) / (sh.std(ddof=1) + 1e-9))
    return rec


def done_keys():
    f = OUT / "runs.jsonl"
    if not f.exists():
        return set()
    ks = set()
    for line in f.read_text().splitlines():
        r = json.loads(line)
        ks.add((r["pair"], r["ntok"], r["q"], r["model"], r["rep"]))
    return ks


def main(mode):
    grid = []
    if mode == "gate":
        grid = [(p, 10000, 0.0, "K0", r, 0) for p in PAIRS for r in range(3)]
    elif mode == "full":
        for p in PAIRS:
            for n in (2500, 10000, 30000):
                for q in (0.0, 0.2):
                    for m in ("K0", "K2"):
                        for r in range(3):
                            grid.append((p, n, q, m, r, 0))
        for p in PAIRS:
            for r in range(3):
                grid.append((p, 10000, 0.0, "WRONG", r, 3))
    have = done_keys()
    with open(OUT / "runs.jsonl", "a") as f:
        for (p, n, q, m, r, sh) in grid:
            if (p, n, q, m, r) in have:
                continue
            rec = one_run(p, n, q, m, r, shuffles=sh)
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(p, n, q, m, r, "blind", round(rec["blind_acc"], 3), "climb", round(rec["climb_acc"], 3),
                  "wrong>true", rec["wrong_beats_true"], "len", round(rec["mean_len"], 2),
                  "z", rec.get("z_vs_shuffle"), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
