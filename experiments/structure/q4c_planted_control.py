"""Q4c. Planted-answer control for segmentation: corpora with KNOWN word boundaries, sub-sampled to the Indus size
(~2,300 texts, ~10k sign tokens). Linear B (syllabograms, words = hyphenated sign groups; logograms as 1-sign words)
and Sumerian Ur III seal legends (sign readings, words = name/title/patronym units).
Measures boundary F1 of DP / PMI / BE against the truth, and the held-out bits/sign comparison used on Indus.
"""
import json
import random
import re

import numpy as np

from common import ROOT, save_json
from q4_segment import (DPSeg, be_boundaries, bigram_bits, f1, f1_null, pmi_boundaries, unigram_bits, word_model_bits)

PG = ROOT / "sources/paragorth_Indus-/data/codelib"
rng = random.Random(11)


def load_lb():
    syl = re.compile(r"^(?:[a-z]{1,3}[23]?|\*\d+)$")
    out = []
    for l in open(PG / "linear_b.jsonl"):
        seq = json.loads(l)["seq"]; words = []
        for w in seq:
            w = re.sub(r"[̣⸢⸣⌜⌝⌞⌟\[\]?<>]", "", w)
            if "-" in w or re.fullmatch(r"[a-z0-9*]+", w):
                p = [x for x in w.split("-") if syl.match(x)]
                if p:
                    words.append(p)
        if words:
            out.append(words)
    return out


def load_ur():
    out = []
    for l in open(PG / "ur3_legends.jsonl"):
        seq = json.loads(l)["seq"]; words = []
        for w in seq:
            w = w.replace("_", "").lower()
            w = re.sub(r"\{([^}]*)\}", r"-\1-", w)
            p = [x for x in re.split(r"[-.\s]+", w) if x and x not in ("x", "...")]
            if p:
                words.append(p)
        if words:
            out.append(words)
    return out


def sample(texts, ntok=10000):
    rng.shuffle(texts); out = []; n = 0
    for t in texts:
        if n >= ntok:
            break
        out.append(t); n += sum(map(len, t))
    return out


def evaluate(name, texts):
    texts = sample(texts)
    rng.shuffle(texts)
    k = int(len(texts) * 0.75)
    tr_w, te_w = texts[:k], texts[k:]
    tr = [sum(t, []) for t in tr_w]; te = [sum(t, []) for t in te_w]
    truth = []
    for t in tr_w:
        b = []
        for i, w in enumerate(t):
            b += [False] * (len(w) - 1) + ([True] if i < len(t) - 1 else [])
        truth.append(b)
    m = DPSeg(tr, seed=0).fit(120)
    dp_b = m.boundaries()
    pmi_b = pmi_boundaries(tr, tr); be_b = be_boundaries(tr, tr)
    res = {"texts": len(texts), "tokens": sum(map(len, tr + te)), "mean_text_len": float(np.mean([len(x) for x in tr + te])),
           "mean_word_len_true": float(np.mean([len(w) for t in tr_w for w in t])), "true_boundary_rate": float(np.mean([x for b in truth for x in b]))}
    for nm, b in (("DP", dp_b), ("PMI", pmi_b), ("BE", be_b)):
        mu, sd = f1_null(truth, b)
        res[f"F1_{nm}_vs_truth"] = {"F1": f1(truth, b), "null_mean": mu, "null_sd": sd, "rate": float(np.mean([x for bb in b for x in bb]))}
    res["F1_DP_vs_PMI"] = f1(dp_b, pmi_b)
    res["heldout_bits"] = {"sign_unigram": unigram_bits(tr, te), "sign_bigram": bigram_bits(tr, te),
                           "DP_word_unigram": word_model_bits(m.lexicon(), tr, te)}
    # true-lexicon word model (upper reference)
    from collections import Counter
    tl = Counter(tuple(w) for t in tr_w for w in t)
    res["heldout_bits"]["TRUE_word_unigram"] = word_model_bits(tl, tr, te)
    print(name, json.dumps(res, indent=1))
    return res


out = {"Linear B": evaluate("Linear B", load_lb()), "Ur III seal legends": evaluate("Ur III", load_ur())}
save_json("q4c_planted_control", out)
