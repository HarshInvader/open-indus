"""Open Indus sound-key bench: score a proposed key in one command.

    .venv/bin/python -I experiments/s5_bench_cli/bench.py KEY.csv --lexicon WORDS.txt [--signlist M77|ICIT]
                                                         [--out result.json] [--quick] [--seed N]

KEY.csv    columns `sign,value`; one value per sign (M1..M417 for --signlist M77, W numbers for ICIT).
WORDS.txt  the dictionary to score against: one word per line, in Latin letters (diacritics are stripped).

What it does (pre-registration: docs/prereg/s5_bench_cli.md):
  1. Prints the key's SHA-256 before any score is computed.
  2. Scores the key on HELD-OUT texts (split v2) with two scores:
       W  signs per dictionary word: fewest words that spell each run of consecutive keyed signs
       J  junction log-probability: letter bigram (learned from the lexicon) across adjacent keyed signs
  3. N1: the key's own values shuffled among its signs within 5 frequency bins (1,000 times).
  4. N2: keys with the same values, hill-climbed to fit unigram-shuffled and Markov noise (3 restarts each),
     scored on noise held-out texts built the same way. (Keys fitted on real dev are reported too.)
  5. A score PASSES if N1 p < 0.025 and the key beats every N2 key. The key passes if any score passes.

The bench can refute a key. It cannot confirm one: in this project's simulations a wrong key often beats the true
key, so a pass only means "worth a red team", never "deciphered".
"""
import argparse, csv, hashlib, json, random, sys, unicodedata
from collections import Counter, defaultdict
from math import log
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORES = ("W", "J")
ALPHA = 0.025  # Bonferroni over the two scores
MAXSPAN = 4


# ===================================================================== inputs
def strip(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c) and c.isalpha())


def load_key(path, signlist="M77"):
    raw = Path(path).read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or not {"sign", "value"} <= set(rows[0]):
        raise SystemExit("key CSV needs a header with columns: sign,value")
    pre = "M" if signlist == "M77" else "W"
    key, problems = {}, []
    for n, r in enumerate(rows, 2):
        s = (r["sign"] or "").strip().upper()
        if s.isdigit(): s = f"{pre}{int(s)}" if pre == "M" else f"W{int(s):03d}"
        if not s.startswith(pre): problems.append(f"line {n}: sign {r['sign']!r} is not a {signlist} number"); continue
        if pre == "W" and s[1:].isdigit(): s = f"W{int(s[1:]):03d}"
        if pre == "M" and s[1:].isdigit(): s = f"M{int(s[1:])}"
        v = strip(r["value"])
        if not v: problems.append(f"line {n}: value {r['value']!r} has no letters"); continue
        if s in key: problems.append(f"line {n}: {s} appears twice (one value per sign)"); continue
        key[s] = v
    return key, hashlib.sha256(raw).hexdigest(), problems


def load_lexicon(path, minlen=3):
    words = {strip(l.split("\t")[0]) for l in open(path, encoding="utf-8")}
    return {w for w in words if len(w) >= minlen}


def letter_model(lex):
    cnt, tot = Counter(), Counter()
    for w in lex:
        for a, b in zip(w, w[1:]):
            cnt[(a, b)] += 1; tot[a] += 1
    letters = sorted({c for w in lex for c in w})
    V = max(1, len(letters))
    lp = {(a, b): log((cnt[(a, b)] + 1) / (tot[a] + V)) for a in letters for b in letters}
    return lp, log(1 / (max(tot.values(), default=0) + V))


# ===================================================================== corpora
def m77_split():
    sys.path.insert(0, str(ROOT))
    from corpus.load import dev_heldout, runs
    dev, ho = dev_heldout(version=2)
    f = lambda T: [r for t in T if t["site"] != "West Asian finds" for r in runs(t["seq"]) if len(r) >= 2]
    return f(dev), f(ho)


def icit_split():
    sys.path[:0] = [str(ROOT), str(ROOT / "experiments" / "redteam")]
    from corpus.load import icit_texts, distinct, runs
    from rt_common import near_dup_clusters
    nonnative = ("Persian Gulf", "Mesopotamia", "Iranian Plateau", "Central Asia", "Other")
    T = distinct([t for t in icit_texts() if t["region"] not in nonnative])
    flat = sorted({tuple(s for s in t["seq"] if s not in "|#") for t in T} - {()})
    cl = near_dup_clusters(flat); r = random.Random(0); r.shuffle(cl)
    ho = {s for c in cl[int(0.75 * len(cl)):] for s in c}
    dev_r, ho_r = [], []
    for t in T:
        k = tuple(s for s in t["seq"] if s not in "|#")
        (ho_r if k in ho else dev_r).extend(x for x in runs(t["seq"]) if len(x) >= 2)
    return dev_r, ho_r


def shuffle_corpus(R, rng):
    toks = [s for r in R for s in r]; rng.shuffle(toks); out, i = [], 0
    for r in R: out.append(toks[i:i + len(r)]); i += len(r)
    return out


def markov_corpus(R, rng):
    nxt, starts = defaultdict(list), []
    for r in R:
        starts.append(r[0])
        for a, b in zip(r, r[1:]): nxt[a].append(b)
    out = []
    for r in R:
        s = [rng.choice(starts)]
        while len(s) < len(r):
            c = nxt.get(s[-1]); s.append(rng.choice(c) if c else rng.choice(starts))
        out.append(s)
    return out


# ===================================================================== scoring
class Scorer:
    """Score W or J of a key on a list of runs, with per-run caching for fast swaps."""

    def __init__(self, R, lex, lp, floor):
        self.R = [r for r in R if len(r) >= 2]; self.lex, self.lp, self.floor = lex, lp, floor
        self.by_sign = defaultdict(set)
        for i, r in enumerate(self.R):
            for s in r: self.by_sign[s].add(i)

    def run_stats(self, r, key, which):
        if which == "J":
            num = den = 0.0
            for a, b in zip(r, r[1:]):
                x, y = key.get(a), key.get(b)
                if x and y: den += 1; num += self.lp.get((x[-1], y[0]), self.floor)
            return num, den
        n_signs = n_words = 0; seg = []
        for s in list(r) + [None]:
            if s is not None and s in key: seg.append(key[s])
            else:
                if len(seg) >= 2: n_signs += len(seg); n_words += self.fewest(seg)
                seg = []
        return n_signs, n_words

    def fewest(self, seg):
        L = len(seg); best = [0] + [10 ** 9] * L
        for j in range(1, L + 1):
            best[j] = best[j - 1] + 1
            for i in range(max(0, j - MAXSPAN), j - 1):
                if best[i] + 1 < best[j] and "".join(seg[i:j]) in self.lex: best[j] = best[i] + 1
        return best[L]

    def init(self, key, which):
        self.cache = [self.run_stats(r, key, which) for r in self.R]
        self.tot = [sum(c[0] for c in self.cache), sum(c[1] for c in self.cache)]

    def value(self):
        n, d = self.tot
        return n / d if d else float("nan")

    def score(self, key, which):
        self.init(key, which); return self.value()

    def coverage(self, key):
        toks = [s for r in self.R for s in r]
        return sum(s in key for s in toks) / max(1, len(toks))


def freq_bins(R, signs, nb=5):
    f = Counter(s for r in R for s in r)
    order = sorted(signs, key=lambda s: (f[s], s)); k = len(order)
    return [order[i * k // nb:(i + 1) * k // nb] for i in range(nb)]


def permute_key(key, bins, rng):
    new = dict(key)
    for b in bins:
        vals = [key[s] for s in b]; rng.shuffle(vals); new.update(zip(b, vals))
    return new


def fit_key(sc, key, which, rng, iters):
    """Hill-climb: swap the values of two keyed signs, keep the swap if the score does not fall."""
    key = dict(key); signs = sorted(s for s in key if s in sc.by_sign)
    sc.init(key, which); cur = sc.value()
    if len(signs) < 2: return key, cur
    for _ in range(iters):
        a, b = rng.sample(signs, 2); aff = sc.by_sign[a] | sc.by_sign[b]
        key[a], key[b] = key[b], key[a]; old = {i: sc.cache[i] for i in aff}
        for i in aff:
            ns = sc.run_stats(sc.R[i], key, which)
            sc.tot[0] += ns[0] - sc.cache[i][0]; sc.tot[1] += ns[1] - sc.cache[i][1]; sc.cache[i] = ns
        new = sc.value()
        if new == new and (cur != cur or new >= cur): cur = new
        else:
            key[a], key[b] = key[b], key[a]
            for i, o in old.items():
                sc.tot[0] += o[0] - sc.cache[i][0]; sc.tot[1] += o[1] - sc.cache[i][1]; sc.cache[i] = o
    return key, cur


def bench(key, lex, dev, ho, nperm=1000, iters=3000, restarts=3, seed=1977, log=print):
    lp, floor = letter_model(lex)
    rng = random.Random(seed)
    keyed = {s: v for s, v in key.items() if any(s in r for r in dev + ho)}
    bins = freq_bins(dev, sorted(keyed))
    S_ho, S_dev = Scorer(ho, lex, lp, floor), Scorer(dev, lex, lp, floor)
    out = dict(n_signs_in_key=len(key), n_signs_in_corpus=len(keyed), n_dev_runs=len(S_dev.R), n_heldout_runs=len(S_ho.R),
               lexicon_size=len(lex), coverage_heldout_tokens=round(S_ho.coverage(keyed), 4), nperm=nperm, fit_iters=iters,
               restarts=restarts, seed=seed, scores={})
    noise = {"unigram": shuffle_corpus, "markov": markov_corpus}
    noise_corpora = {n: (f(dev, random.Random(f"{seed}:{n}:dev")), f(ho, random.Random(f"{seed}:{n}:ho"))) for n, f in noise.items()}
    for w in SCORES:
        obs = S_ho.score(keyed, w)
        null = [S_ho.score(permute_key(keyed, bins, rng), w) for _ in range(nperm)]
        valid = [x for x in null if x == x]
        p1 = (1 + sum(x >= obs for x in valid)) / (len(valid) + 1) if obs == obs and valid else 1.0
        n2 = {}
        for n, (nd, nh) in noise_corpora.items():
            vals = []
            for k in range(restarts):
                start = permute_key(keyed, [sorted(keyed)], rng)
                fk, _ = fit_key(Scorer(nd, lex, lp, floor), start, w, rng, iters)
                vals.append(Scorer(nh, lex, lp, floor).score(fk, w))
            n2[n] = vals
        real_fit = []
        for k in range(restarts):
            fk, _ = fit_key(Scorer(dev, lex, lp, floor), permute_key(keyed, [sorted(keyed)], rng), w, rng, iters)
            real_fit.append(S_ho.score(fk, w))
        n2_all = [x for v in n2.values() for x in v if x == x]
        beats_n2 = bool(obs == obs and n2_all and obs > max(n2_all))
        out["scores"][w] = dict(heldout=obs, N1_mean=sum(valid) / len(valid) if valid else None, N1_p=p1,
                                N2_noise_fitted_heldout=n2, N2_max=max(n2_all) if n2_all else None,
                                fitted_on_real_dev_scored_on_heldout=real_fit, beats_all_N2=beats_n2,
                                passes=bool(p1 < ALPHA and beats_n2))
        log(f"  {w}: held-out {obs:.4f} | own values shuffled mean {out['scores'][w]['N1_mean']:.4f}, p={p1:.4g} | "
            f"best noise-fitted key {out['scores'][w]['N2_max']} | {'PASS' if out['scores'][w]['passes'] else 'fail'}")
    out["warnings"] = []
    if min((len(b) for b in bins), default=0) < 2:
        out["warnings"].append("a frequency bin holds fewer than 2 signs, so N1 cannot shuffle it; keys under about 10 "
                               "signs cannot be tested against their own shuffled values")
    if out["coverage_heldout_tokens"] < 0.05:
        out["warnings"].append("the key covers under 5% of held-out tokens; the scores rest on very few junctions")
    for x in out["warnings"]: log("  warning:", x)
    out["passes"] = any(v["passes"] for v in out["scores"].values())
    out["verdict"] = ("passes the bench: send it to the red team (a pass is not a decipherment)" if out["passes"]
                      else "does not pass the bench: no score beats both its own shuffled values and noise-fitted keys")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("key"); ap.add_argument("--lexicon", required=True)
    ap.add_argument("--signlist", choices=["M77", "ICIT"], default="M77")
    ap.add_argument("--out"); ap.add_argument("--quick", action="store_true", help="200 shuffles, 800 swaps (trial runs only)")
    ap.add_argument("--seed", type=int, default=1977)
    a = ap.parse_args(argv)
    key, sha, problems = load_key(a.key, a.signlist)
    print(f"key {a.key}: sha256 {sha}  ({len(key)} signs)")
    for p in problems: print("  warning:", p)
    if not key: raise SystemExit("no usable rows in the key")
    lex = load_lexicon(a.lexicon)
    print(f"lexicon {a.lexicon}: {len(lex)} words of 3+ letters, sha256 {hashlib.sha256(Path(a.lexicon).read_bytes()).hexdigest()}")
    dev, ho = m77_split() if a.signlist == "M77" else icit_split()
    res = bench(key, lex, dev, ho, nperm=200 if a.quick else 1000, iters=800 if a.quick else 3000, seed=a.seed)
    res.update(key_file=str(a.key), key_sha256=sha, key_warnings=problems, lexicon_file=str(a.lexicon), signlist=a.signlist,
               quick=a.quick, note="The bench can refute a key, not confirm one.")
    print("verdict:", res["verdict"])
    if a.out:
        with open(a.out, "w") as fh: json.dump(res, fh, indent=1)
        print("written", a.out)
    return res


if __name__ == "__main__":
    main()
