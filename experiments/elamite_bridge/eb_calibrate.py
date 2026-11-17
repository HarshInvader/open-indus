"""Calibration (planted known answer) for metric D: does neighbour diversity separate phonetic signs
from logograms in real scripts at Indus size? Uses NO Indus sign identities, only the run-length
distribution of M77 dev texts (to cut the reference corpora into Indus-length pieces).

Corpora (already built by the short_labels agent, text only):
  Linear B whole documents (DAMOS): syllabograms (lower case) vs logograms (upper case: ideograms,
    measure signs). NUM and undeciphered *NN signs are kept in the text but in neither class.
  Egyptian verbless phrases (TLA): the 26 uniliteral phonograms vs all other signs (biliterals,
    logograms, determinatives: a mixed 'rest', so this is a harder, conservative check).
Run: .venv/bin/python experiments/elamite_bridge/eb_calibrate.py
"""
import json, random, sys
from collections import Counter
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from corpus.load import dev_heldout, runs as split_runs
from experiments.elamite_bridge.eb_core import (ROOT, diversity_residuals, auc, set_vs_rest_perm,
                                                 freq_strata, jl, MIN_TOK)

SL = ROOT / "experiments/short_labels/data"
UNILIT = set("\U0001313F\U000131CB\U000133ED\U0001309D\U00013171\U000133F2\U000130C0\U000132AA\U00013191"
             "\U00013153\U00013216\U0001308B\U00013254\U0001339B\U0001340D\U00013121\U000132C3\U000132F4"
             "\U00013219\U0001320E\U000133A1\U000133BC\U000133CF\U0001337F\U000130A7\U00013193")

dev, _ = dev_heldout(version=2)
LENS = [len(r) for t in dev for r in split_runs(t["seq"])]
N_TOK_INDUS = None  # set below from ICIT distinct break-free token count (count only, no identities)


def icit_token_count():
    from corpus.load import icit_texts, distinct
    return sum(len(r) for t in distinct(icit_texts()) for r in split_runs(t["seq"]))


def chunk(docs, rng):
    out = []
    for d in docs:
        i = 0
        while i < len(d):
            k = rng.choice(LENS); out.append(d[i:i + k]); i += k
    return out


def subsample(runs_, n_tok, rng):
    idx = list(range(len(runs_))); rng.shuffle(idx); out = []; n = 0
    for i in idx:
        if n >= n_tok: break
        out.append(runs_[i]); n += len(runs_[i])
    return out


def classes_linb(s):
    if s == "NUM" or s.startswith("*"): return None
    if any(c.isupper() for c in s): return "logo"
    if any(c.isalpha() for c in s): return "phon"
    return None


def classes_egy(s):
    return "phon" if s in UNILIT else "logo"


def evaluate(name, docs, cls, n_tok, k_set=12, n_rep=30, n_power=200, seed=0):
    rng = random.Random(seed)
    res = {"corpus": name}
    # full corpus, whole documents
    D, tok = diversity_residuals(docs)
    ph = [D[s] for s in D if cls(s) == "phon"]; lg = [D[s] for s in D if cls(s) == "logo"]
    res["full_docs"] = {"auc": auc(ph, lg), "n_phon": len(ph), "n_logo": len(lg), "tokens": sum(map(len, docs))}
    # Indus-length chunks, subsampled to the Indus token count, repeated
    aucs, powers = [], []
    for rep in range(n_rep):
        r = subsample(chunk(docs, rng), n_tok, rng)
        D, tok = diversity_residuals(r)
        ph_s = [s for s in D if cls(s) == "phon"]; lg_s = [s for s in D if cls(s) == "logo"]
        aucs.append(auc([D[s] for s in ph_s], [D[s] for s in lg_s]))
        if rep < 5 and len(ph_s) >= k_set:
            st = freq_strata(tok, list(D))
            hits = 0
            for j in range(n_power // 5):
                test = rng.sample(ph_s, k_set)
                _, p, _ = set_vs_rest_perm(D, test, n_perm=1000, seed=rng.randint(0, 10**9), strata=st)
                hits += p < 0.05
            powers.append(hits / (n_power // 5))
    res["indus_size_chunks"] = {"auc_mean": float(np.mean(aucs)), "auc_p05": float(np.percentile(aucs, 5)),
                                "auc_p95": float(np.percentile(aucs, 95)), "n_rep": n_rep,
                                "power_k%d_vs_mixed_rest" % k_set: float(np.mean(powers)) if powers else None}
    return res


if __name__ == "__main__":
    n_tok = icit_token_count()
    print("ICIT distinct break-free tokens (size target):", n_tok)
    linb = [d["seq"] for d in jl(SL / "linb_doc.jsonl")] + [d["seq"] for d in jl(SL / "linb_label.jsonl")]
    egy = [d["seq"] for d in jl(SL / "egy_nom.jsonl")]
    out = {"min_tok": MIN_TOK, "size_target_tokens": n_tok}
    for name, docs, cls in [("linear_b", linb, classes_linb), ("egyptian_uniliterals", egy, classes_egy)]:
        tot = sum(map(len, docs))
        r = evaluate(name, docs, cls, min(n_tok, tot))
        print(json.dumps(r, indent=1)); out[name] = r
    json.dump(out, open(ROOT / "experiments/elamite_bridge/calibration.json", "w"), indent=1)
