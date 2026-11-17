"""Shared pieces for the Pierson-key bench (task #5). Data only from keys/ (copied from the author's public repo)."""
import csv
import json
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from math import log
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, runs, m77_texts, distinct  # noqa

KEYS = HERE / "keys"
WIKT = ROOT / "experiments" / "language" / "ext" / "wikt"


def strip(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c) and c.isalpha())


def parse_reading(r):
    r = re.sub(r"\(.*?\)", "", r or "")
    alts = [a.strip() for a in r.split("/") if a.strip() and a.strip() not in ("?",)]
    return [a for a in alts if any(ch.isalpha() for ch in a)]


def mnum(s):
    m = re.fullmatch(r"M0*(\d+)", s)
    return int(m.group(1)) if m else None


def load_k185():
    a = json.load(open(KEYS / "anchors_bbecc1cd_20260527.json"))["anchors"]
    out = {}
    for s, v in a.items():
        n = mnum(s)
        if v.get("confidence") == "HIGH" and n and n <= 417:
            alts = parse_reading(v.get("reading", ""))
            if alts:
                out[f"M{n}"] = alts
    return out


def load_k161():
    out = {}
    for r in csv.DictReader(open(KEYS / "anchor_table_397.csv", encoding="utf-8")):
        n = mnum(r["Sign"])
        if r["Confidence"] in ("HIGH", "MEDIUM") and n and n <= 417:
            alts = parse_reading(r["Reading"])
            if alts:
                out[f"M{n}"] = alts
    return out


# ---------- Tamil script -> Latin ----------
CONS = {"க": "k", "ங": "ṅ", "ச": "c", "ஞ": "ñ", "ட": "ṭ", "ண": "ṇ", "த": "t", "ந": "n", "ப": "p", "ம": "m",
        "ய": "y", "ர": "r", "ல": "l", "வ": "v", "ழ": "ḻ", "ள": "ḷ", "ற": "ṟ", "ன": "ṉ", "ஜ": "j", "ஷ": "ṣ",
        "ஸ": "s", "ஹ": "h"}
VSIGN = {"ா": "ā", "ி": "i", "ீ": "ī", "ு": "u", "ூ": "ū", "ெ": "e", "ே": "ē", "ை": "ai", "ொ": "o", "ோ": "ō", "ௌ": "au"}
VIND = {"அ": "a", "ஆ": "ā", "இ": "i", "ஈ": "ī", "உ": "u", "ஊ": "ū", "எ": "e", "ஏ": "ē", "ஐ": "ai", "ஒ": "o",
        "ஓ": "ō", "ஔ": "au", "ஃ": "ḵ"}


def tamil_to_latin(w):
    out, i = [], 0
    while i < len(w):
        ch = w[i]
        if ch in CONS:
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if nxt == "்":
                out.append(CONS[ch]); i += 2
            elif nxt in VSIGN:
                out.append(CONS[ch] + VSIGN[nxt]); i += 2
            else:
                out.append(CONS[ch] + "a"); i += 1
        elif ch in VIND:
            out.append(VIND[ch]); i += 1
        else:
            i += 1  # ignore grantha clusters / punctuation
    return "".join(out)


def tamil_lemmas():
    d = {int(r["id"]): tamil_to_latin(r["lemma"]) for r in csv.DictReader(open(KEYS / "kee2u_tamil_lemmas.csv", encoding="utf-8"))}
    return {k: v for k, v in d.items() if v}  # bug fix 17:40Z: drop lemmas with no Tamil letters


def lexicon():
    words = set()
    for f in ["Proto-Dravidian_lemmas.txt", "Proto-Dravidian_nouns.txt"]:
        for line in open(WIKT / f, encoding="utf-8"):
            w = line.strip().split("/")[-1].strip("-*")
            words.add(strip(w))
    for w in tamil_lemmas().values():
        words.add(strip(w))
    lm = json.load(open(KEYS / "dravidian_tamil_lm.json"))
    for w in lm["vocab"]:
        words.add(strip(tamil_to_latin(w)))
    return {w for w in words if len(w) >= 3}


def lm_bigrams():
    lm = json.load(open(KEYS / "dravidian_tamil_lm.json"))
    raw = set()
    cnt = Counter()
    for k, c in lm["bigrams"].items():
        p = k.split("→") if "→" in k else k.split(",")
        if len(p) == 2:
            a, b = p[0].strip(), p[1].strip()
            raw.add((a, b))
            a2, b2 = strip(a), strip(b)
            if len(a2) == 1 and len(b2) == 1:
                cnt[(a2, b2)] += c
    letters = sorted({x for ab in cnt for x in ab})
    tot = Counter()
    for (a, b), c in cnt.items():
        tot[a] += c
    V = len(letters)
    logp = defaultdict(lambda: 0.0)
    for a in letters:
        for b in letters:
            logp[(a, b)] = log((cnt[(a, b)] + 1) / (tot[a] + V))
    floor = log(1 / (max(tot.values()) + V))
    return raw, logp, floor


# ---------- scorer with per-text caching ----------
class Bench:
    """runs: list of sign lists. key: sign -> list of alternatives. Scores S1,S2,S3."""

    def __init__(self, runs_, lex, bi_raw, logp, floor, maxspan=4):
        self.runs = [r for r in runs_ if len(r) >= 2]
        self.lex, self.bi_raw, self.logp, self.floor, self.maxspan = lex, bi_raw, logp, floor, maxspan
        self.by_sign = defaultdict(set)
        for i, r in enumerate(self.runs):
            for s in r:
                self.by_sign[s].add(i)

    def text_stats(self, r, key, which):
        if which in ("S1", "S2"):
            num = den = 0.0
            for a, b in zip(r, r[1:]):
                ka, kb = key.get(a), key.get(b)
                if ka and kb:
                    den += 1
                    if which == "S1":
                        num += (ka[0][0], kb[0][0]) in self.bi_raw
                    else:
                        x, y = strip(ka[0]), strip(kb[0])
                        num += self.logp.get((x[-1], y[0]), self.floor) if x and y else self.floor
            return num, den
        # S3: only keyed sub-runs count
        n_signs = n_words = 0
        seg = []
        for s in r + [None]:
            if s is not None and s in key:
                seg.append(s)
            else:
                if len(seg) >= 2:
                    n_signs += len(seg); n_words += self._fewest(seg, key)
                seg = []
        return n_signs, n_words

    def _fewest(self, seg, key):
        L = len(seg)
        best = [0] + [10 ** 9] * L
        for j in range(1, L + 1):
            best[j] = best[j - 1] + 1
            for i in range(max(0, j - self.maxspan), j - 1):
                if best[i] + 1 < best[j] and self._is_word(seg[i:j], key):
                    best[j] = best[i] + 1
        return best[L]

    def _is_word(self, span, key):
        cands = {""}
        for s in span:
            cands = {c + strip(a) for c in cands for a in key[s]}
            if len(cands) > 64:
                cands = set(list(cands)[:64])
        return any(c in self.lex for c in cands)

    def init(self, key, which):
        self.cache = [self.text_stats(r, key, which) for r in self.runs]
        self.tot = [sum(c[0] for c in self.cache), sum(c[1] for c in self.cache)]

    def value(self, which):
        n, d = self.tot
        return n / d if d else float("nan")

    def score(self, key, which):
        self.init(key, which)
        return self.value(which)

    def coverage(self, key):
        toks = [s for r in self.runs for s in r]
        return sum(s in key for s in toks) / len(toks)


def freq_bins(runs_, signs, nb=5):
    f = Counter(s for r in runs_ for s in r)
    order = sorted(signs, key=lambda s: f[s])
    k = len(order)
    return [order[i * k // nb:(i + 1) * k // nb] for i in range(nb)]


def permute_key(key, bins, rng):
    new = {}
    for b in bins:
        vals = [key[s] for s in b]
        rng.shuffle(vals)
        new.update(zip(b, vals))
    return new


def fit_key(bench, key, which, rng, iters=3000):
    """Greedy hill-climb: swap readings between two keyed signs, keep if score rises."""
    key = dict(key)
    signs = [s for s in key if s in bench.by_sign]
    bench.init(key, which)
    cur = bench.value(which)
    for _ in range(iters):
        a, b = rng.sample(signs, 2)
        aff = bench.by_sign[a] | bench.by_sign[b]
        key[a], key[b] = key[b], key[a]
        old = {i: bench.cache[i] for i in aff}
        for i in aff:
            ns = bench.text_stats(bench.runs[i], key, which)
            bench.tot[0] += ns[0] - bench.cache[i][0]; bench.tot[1] += ns[1] - bench.cache[i][1]
            bench.cache[i] = ns
        new = bench.value(which)
        if new >= cur:
            cur = new
        else:
            key[a], key[b] = key[b], key[a]
            for i, o in old.items():
                bench.tot[0] += o[0] - bench.cache[i][0]; bench.tot[1] += o[1] - bench.cache[i][1]
                bench.cache[i] = o
    return key, cur


def shuffle_corpus(runs_, rng):
    toks = [s for r in runs_ for s in r]
    rng.shuffle(toks)
    out, i = [], 0
    for r in runs_:
        out.append(toks[i:i + len(r)]); i += len(r)
    return out


def markov_corpus(runs_, rng):
    nxt = defaultdict(list)
    starts = []
    for r in runs_:
        starts.append(r[0])
        for a, b in zip(r, r[1:]):
            nxt[a].append(b)
    out = []
    for r in runs_:
        s = [rng.choice(starts)]
        while len(s) < len(r):
            c = nxt.get(s[-1])
            s.append(rng.choice(c) if c else rng.choice(starts))
        out.append(s)
    return out
