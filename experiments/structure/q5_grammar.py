"""Q5. Text grammar: templates over positional classes, class precedence, order vs bag-of-words (permutation test on
held-out), multiset order variability, longest repeated substrings vs a bigram-generated null corpus.
"""
import itertools
import json
import math
import random
from collections import Counter, defaultdict

import numpy as np

from common import (Bigram, ROOT, distinct, icit_texts, is_clean, m77_split, m77_texts, runs, save_json, signs)

rng = random.Random(20261114)
POSJ = json.load(open(ROOT / "experiments/structure/positional.json"))
ABBR = {"opener": "O", "closer": "C", "medial-core": "M"}


def cls_map(key):
    return {x: ABBR.get(v["class"], "?") for x, v in POSJ[key]["per_sign"].items()}


def template(s, cm, jar):
    out = []
    for x in s:
        c = "J" if x == jar else cm.get(x, "x")
        out.append(c)
    # collapse runs of M/x into a single core token
    col = []
    for c in out:
        c2 = "K" if c in ("M", "x") else c
        if col and col[-1] == c2 == "K":
            continue
        col.append(c2)
    return "".join(col)


def precedence(texts, cm):
    """P(class A before class B) over all ordered sign pairs co-occurring in a text (distinct texts)."""
    cnt = Counter()
    for s in texts:
        cs = [cm.get(x, "x") for x in s]
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                cnt[(cs[i], cs[j])] += 1
    out = {}
    for a in "OMC":
        for b in "OMC":
            if a < b or (a, b) in (("O", "M"), ("M", "C"), ("O", "C")):
                ab, ba = cnt[(a, b)], cnt[(b, a)]
                if a != b:
                    out[f"{a}<{b}"] = ab / (ab + ba) if ab + ba else None
    return out


def sign_pair_order(texts, minco=10):
    """For sign pairs co-occurring (distinct positions) in >= minco texts: share with a before b. Null: within-text shuffle."""
    def tab(T):
        c = Counter(); co = Counter()
        for s in T:
            seen = set()
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    a, b = s[i], s[j]
                    if a == b:
                        continue
                    key = tuple(sorted((a, b)))
                    if (key, i, j) in seen:
                        continue
                    seen.add((key, i, j))
                    co[key] += 1
                    if (a, b) == key:
                        c[key] += 1
        return c, co
    c, co = tab(texts)
    keys = [k for k in co if co[k] >= minco]
    cons = [abs(c[k] / co[k] - 0.5) * 2 for k in keys]
    nulls = []
    for r in range(20):
        sh = [rng.sample(s, len(s)) for s in texts]
        cn, con = tab(sh)
        nulls.append(np.mean([abs(cn[k] / con[k] - 0.5) * 2 for k in keys if con[k]]))
    return {"pairs": len(keys), "mean_order_consistency": float(np.mean(cons)),
            "share_pairs_ge90pct_one_order": float(np.mean([x >= 0.8 for x in cons])),
            "null_mean_consistency": float(np.mean(nulls)), "null_sd": float(np.std(nulls))}


def perm_test(train_runs, test_texts, nperm=200):
    """Held-out texts (break-free, len>=3, >=3 distinct orders): percentile of the real order's bigram log-prob
    among random permutations of the same signs."""
    bg = Bigram(train_runs)
    pct = []; best = 0; n = 0; best_null = 0.0
    for s in test_texts:
        if len(s) < 3 or len(set(itertools.permutations(s))) < 3 if len(s) <= 6 else len(s) < 3:
            continue
        lp = bg.logprob(s)
        perms = set()
        if len(s) <= 6:
            allp = list(set(itertools.permutations(s)))
            others = [list(p) for p in allp if list(p) != s]
        else:
            others = []
            while len(others) < nperm:
                p = rng.sample(s, len(s))
                if p != s:
                    others.append(p)
        sc = [bg.logprob(p) for p in others]
        pct.append(np.mean([lp > x for x in sc]) + 0.5 * np.mean([lp == x for x in sc]))
        best += all(lp > x for x in sc); n += 1
        best_null += 1 / (len(others) + 1)
    return {"texts": n, "mean_percentile_of_real_order": float(np.mean(pct)), "share_real_is_best": best / n,
            "expected_share_best_under_null": best_null / n, "share_real_above_median": float(np.mean([p > 0.5 for p in pct]))}


def multiset_orders(objects, maxlen=5):
    """Object-level: multisets (len 2..maxlen) attested on >=3 objects; distinct orders observed vs random-order null."""
    ms = defaultdict(list)
    for s in objects:
        if 2 <= len(s) <= maxlen and len(set(s)) > 1:
            ms[tuple(sorted(s))].append(tuple(s))
    obs = []; exp = []
    single = 0; tot = 0
    for k, v in ms.items():
        if len(v) < 3:
            continue
        tot += 1
        no = len(set(v)); obs.append(no); single += no == 1
        # null: each object gets a random order
        e = []
        for _ in range(50):
            e.append(len({tuple(rng.sample(list(k), len(k))) for _ in v}))
        exp.append(np.mean(e))
    return {"multisets_ge3_objects": tot, "mean_distinct_orders": float(np.mean(obs)), "null_mean_distinct_orders": float(np.mean(exp)),
            "share_single_order": single / tot}


def repeated_substrings(texts_runs, minlen=2):
    """Count distinct substrings occurring in >=2 distinct texts (by run membership), by length; longest ones."""
    occ = defaultdict(set)
    for ti, rs in enumerate(texts_runs):
        for r in rs:
            for L in range(minlen, len(r) + 1):
                for i in range(len(r) - L + 1):
                    occ[tuple(r[i:i + L])].add(ti)
    rep = {k: v for k, v in occ.items() if len(v) >= 2}
    bylen = Counter(len(k) for k in rep)
    # maximal: not contained in a longer repeated substring with the same text set
    longest = sorted(rep, key=lambda k: (-len(k), -len(rep[k])))[:15]
    return bylen, longest, rep


def bigram_sample(bg, length, rng):
    """sample a run of fixed length from the bigram (renormalised, excluding </s>)."""
    out = []; prev = "<s>"
    vocab = [v for v in bg.uni if v != "</s>"]
    for _ in range(length):
        c = bg.big.get(prev)
        if c:
            items = [(k, n) for k, n in c.items() if k != "</s>"]
        else:
            items = []
        if not items:
            k = rng.choices(vocab, weights=[bg.uni[v] for v in vocab])[0]
        else:
            k = rng.choices([a for a, _ in items], weights=[n for _, n in items])[0]
        out.append(k); prev = k
    return out


def run_all(label, texts, clean_texts, jar, cm, dev_runs=None, ho_texts=None, objects=None):
    out = {"label": label}
    tm = Counter(template(s, cm, jar) for s in clean_texts)
    n = sum(tm.values())
    out["templates_top"] = [(k, c, c / n) for k, c in tm.most_common(15)]
    # canonical template families
    fam = Counter()
    for k, c in tm.items():
        core = k.replace("J", "C")
        o = core.startswith("O"); cl = core.endswith("C")
        fam[("O" if o else "-") + "K" + ("C" if cl else "-")] += c
    out["template_families(O?K+C?)"] = {k: v / n for k, v in fam.items()}
    # how many texts conform to O* K* C* (no opener after core, no closer before core)?
    import re
    conform = sum(c for k, c in tm.items() if re.fullmatch(r"O*K?[CJ]*", k))
    out["share_conforming_O*_K_C*"] = conform / n
    # null for conformity: within-text shuffle
    nulls = []
    for r in range(50):
        tmn = Counter(template(rng.sample(s, len(s)), cm, jar) for s in clean_texts)
        nulls.append(sum(c for k, c in tmn.items() if re.fullmatch(r"O*K?[CJ]*", k)) / n)
    out["conform_null_mean"] = float(np.mean(nulls)); out["conform_null_sd"] = float(np.std(nulls))
    out["class_precedence"] = precedence(clean_texts, cm)
    out["sign_pair_order"] = sign_pair_order(clean_texts)
    if dev_runs is not None:
        out["heldout_perm_test"] = perm_test(dev_runs, ho_texts)
    if objects is not None:
        out["multiset_orders_objects"] = multiset_orders(objects)
    # repeated substrings
    tr = [runs(t) for t in texts]
    bylen, longest, rep = repeated_substrings(tr)
    out["repeated_substrings_by_len"] = dict(sorted(bylen.items()))
    out["longest_repeated"] = [(" ".join(k), len(rep[k])) for k in longest]
    # families: maximal repeats of length >= 6 grouped by the set of texts sharing them
    fams = defaultdict(list)
    for k, v in rep.items():
        if len(k) >= 6:
            fams[frozenset(v)].append(k)
    def ed(a, b):
        d = list(range(len(b) + 1))
        for i, x in enumerate(a, 1):
            p, d[0] = d[0], i
            for j, y in enumerate(b, 1):
                p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
        return d[-1]
    flat = [signs(t) for t in texts]
    famlist = []
    for ts, ks in fams.items():
        k = max(ks, key=len); tl = sorted(ts)
        eds = [ed(flat[a], flat[b]) for a, b in itertools.combinations(tl, 2)]
        famlist.append({"substring": " ".join(k), "len": len(k), "n_texts": len(ts), "texts": [" ".join(texts[i]) for i in tl][:4],
                        "min_whole_text_edit_distance": min(eds)})
    famlist.sort(key=lambda f: -f["len"])
    out["families_len_ge6"] = famlist
    out["n_families_len_ge6"] = len(famlist)
    out["n_families_len_ge6_not_near_duplicates(edit>2)"] = sum(f["min_whole_text_edit_distance"] > 2 for f in famlist)
    # null: bigram-generated corpus with identical run lengths
    allruns = [r for rs in tr for r in rs]
    bg = Bigram(allruns)
    nl = defaultdict(list); nmax = []
    for rep_i in range(5):
        g = random.Random(rep_i)
        syn = [[bigram_sample(bg, len(r), g) for r in rs] for rs in tr]
        bl, lg, _ = repeated_substrings(syn)
        for L in range(2, 12):
            nl[L].append(bl.get(L, 0))
        nmax.append(max(bl) if bl else 0)
    out["null_bigram_repeated_by_len"] = {L: (float(np.mean(v)), float(np.std(v))) for L, v in nl.items()}
    out["null_bigram_longest"] = nmax
    return out


if __name__ == "__main__":
    T = distinct(m77_texts())
    texts = [t["seq"] for t in T]
    clean = [signs(t["seq"]) for t in T if is_clean(t)]
    dev, ho = m77_split()
    dev_runs = [r for t in dev for r in runs(t["seq"])]
    ho_texts = [signs(t["seq"]) for t in ho if "#" not in t["seq"] and "|" not in t["seq"]]
    objects = [signs(t["seq"]) for t in m77_texts() if "#" not in t["seq"]]
    r = run_all("M77", texts, clean, "M342", cls_map("M77_full"), dev_runs, ho_texts, objects)
    save_json("q5_grammar_M77", r)
    print(json.dumps(r, indent=1, default=str)[:7000])
