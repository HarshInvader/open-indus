"""F6. Long-text parse: do long texts tile into several short-seal templates (list of labels) or show a single
extended template / new ordering among known signs (syntax)?

Usage: .venv/bin/python experiments/pair_numeral_long/f6_long.py dev|heldout

Long text = distinct text with >= 10 signs, or multi-line with >= 8 signs.  Grammar = frozen functional grammar
(fr.load_model(): lexicon, compounds and transition probabilities fit on dev only).
Per text statistics (lines parsed independently, break edges open):
  accept   all lines parse
  cuts     pieces the robust parser must cut the lines into, minus 1 per line, per 10 signs
  resets   within-line transitions from a closing role (J closer, B bracketed fish, P clitic) to any non-closing role
           in the robust Viterbi parse, per 10 signs (a label boundary marker)
  inner_O  opener-role signs not at line start, per 10 signs
  novel    share of within-line bigrams never seen (either order) in short dev texts, among bigrams of known signs
  reversed share of within-line bigrams seen in short dev texts only in the other order
Nulls:
  concat   each line refilled with whole random short texts (1-6 signs, single-line, same split, not long) up to
           exactly the same line lengths (simulated long label lists)
  shuffle  signs of the same text permuted within the text (line lengths kept)
"""
import sys, json, random
import numpy as np
from collections import Counter
from common import *
import fr

mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = random.Random(31)
dev, ho, dev_g, lex, comps, G = fr.load_model()
CLOSING = set("JBP")


def is_long(t):
    n = nsig(t)
    return n >= 10 or ("|" in t["seq"] and n >= 8)


def lines_of(t):
    return fr.clean_runs(t)   # (run, start_open, end_open)


short_dev = [t for t in dev if 1 <= nsig(t) <= 6 and "|" not in t["seq"] and "#" not in t["seq"]]
BIG = Counter()
for t in short_dev:
    for r in runs(t["seq"]):
        for a, b in zip(r, r[1:]): BIG[(a, b)] += 1
KNOWN = {s for t in short_dev for s in t["seq"]}


def text_stats(t):
    L = nsig(t); acc = True; cuts = resets = innerO = 0; nb = nov = rev = 0
    for (r, so, eo) in lines_of(t):
        p = G.viterbi(r, so, eo)
        if p is None:
            acc = False
        roles, cut = G.robust_parse(r, so, eo)
        cuts += len(cut)
        for k in range(1, len(roles)):
            if roles[k - 1] in CLOSING and roles[k] not in CLOSING and k not in cut:
                resets += 1
            if roles[k] == "O" and k not in cut:
                innerO += 1
        for k in cut:   # a cut is itself a boundary; count closing->new at a cut as a reset too
            if roles[k - 1] in CLOSING:
                resets += 1
            if roles[k] == "O":
                innerO += 1
        for a, b in zip(r, r[1:]):
            if a in KNOWN and b in KNOWN and a != b:
                nb += 1
                if BIG[(a, b)] == 0 and BIG[(b, a)] == 0: nov += 1
                elif BIG[(a, b)] == 0: rev += 1
    s = 10 / L
    return dict(accept=float(acc), cuts=cuts * s, resets=resets * s, inner_O=innerO * s,
                novel=nov / nb if nb else np.nan, reversed=rev / nb if nb else np.nan, L=L)


def concat_null(t, pool, r):
    """Same line lengths, each line filled with whole short texts (exact fill)."""
    bylen = {}
    for p in pool:
        bylen.setdefault(nsig(p), []).append(p["seq"])
    seq = []
    for k, (run, so, eo) in enumerate(lines_of(t)):
        need = len(run); line = []
        while need > 0:
            l = r.choice([x for x in bylen if x <= need])
            line += list(r.choice(bylen[l])); need -= l
        if k: seq.append("|")
        seq += line
    return dict(t, seq=seq)


def shuffle_null(t, r):
    seq = list(t["seq"]); pos = [i for i, s in enumerate(seq) if s not in ("|", "#")]
    vals = [seq[i] for i in pos]; r.shuffle(vals)
    for i, v in zip(pos, vals): seq[i] = v
    return dict(t, seq=seq)


KEYS = ["accept", "cuts", "resets", "inner_O", "novel", "reversed"]


def evaluate(longs, pool, label, nnull=200):
    real = [text_stats(t) for t in longs]
    R = {"n": len(longs), "mean_len": float(np.mean([s["L"] for s in real]))}
    rm = {k: float(np.nanmean([s[k] for s in real])) for k in KEYS}
    R["real"] = rm
    for nm in ("concat", "shuffle"):
        sims = []
        for _ in range(nnull):
            ts = [concat_null(t, pool, rng) if nm == "concat" else shuffle_null(t, rng) for t in longs]
            st = [text_stats(x) for x in ts]
            sims.append({k: float(np.nanmean([s[k] for s in st])) for k in KEYS})
        R[nm] = {}
        for k in KEYS:
            arr = np.array([s[k] for s in sims])
            lo = (np.sum(arr <= rm[k]) + 1) / (nnull + 1); hi = (np.sum(arr >= rm[k]) + 1) / (nnull + 1)
            R[nm][k] = dict(mean=float(arr.mean()), sd=float(arr.std()), p_real_le=float(lo), p_real_ge=float(hi))
    # bootstrap CI of real means (texts resampled)
    R["real_ci"] = {}
    for k in KEYS:
        v = np.array([s[k] for s in real], float); v = v[~np.isnan(v)]
        bs = [np.mean(v[np.random.default_rng(i).integers(0, len(v), len(v))]) for i in range(2000)]
        R["real_ci"][k] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    print(f"\n== {label}: n={len(longs)} mean length {R['mean_len']:.1f}")
    for k in KEYS:
        print(f"  {k:9s} real {rm[k]:.3f} [{R['real_ci'][k][0]:.3f},{R['real_ci'][k][1]:.3f}]   concat {R['concat'][k]['mean']:.3f}±{R['concat'][k]['sd']:.3f}"
              f" (p_le {R['concat'][k]['p_real_le']:.3f})   shuffle {R['shuffle'][k]['mean']:.3f}±{R['shuffle'][k]['sd']:.3f} (p_ge {R['shuffle'][k]['p_real_ge']:.3f})")
    R["per_text"] = [dict(text_no=t.get("text_no", t.get("id")), seq=" ".join(t["seq"]), **s) for t, s in zip(longs, real)]
    return R


def icit_new_long():
    icit = icit_texts(); seen = set(); out = []
    M77_SITES = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}
    devk = {" ".join(t["seq"]) for t in dev}
    for t in icit:
        k = " ".join(t["seq"])
        if k in seen: continue
        seen.add(k)
        if t["site"] in fr.FOREIGN_SITES or t["site"] in M77_SITES or t["site"] == "Unknown": continue
        m = dict(t, seq=fr.bridge_seq(t["seq"]))
        if " ".join(m["seq"]) in devk: continue   # OOV signs allowed as unknown nouns
        out.append(m)
    return out


R = {}
if mode == "dev":
    longs = [t for t in dev if is_long(t)]
    pool = [t for t in short_dev]
    R["dev"] = evaluate(longs, pool, "dev long texts (grammar in-sample)")
    R["dev_seal"] = evaluate([t for t in longs if t["object_type"] == "seal"], pool, "dev long seals")
    # descriptive: short dev texts parse rate, for orientation
    sh = [text_stats(t) for t in short_dev if nsig(t) >= 2]
    R["dev_short_reference"] = {k: float(np.nanmean([s[k] for s in sh])) for k in KEYS}
    print("dev short texts (2-6 signs):", {k: round(v, 3) for k, v in R["dev_short_reference"].items()})
    json.dump(R, open(HERE / "f6_dev.json", "w"), indent=1, default=float)
else:
    longs = [t for t in ho if is_long(t) and t["site"] != "West Asian finds"]
    pool = [t for t in ho if 1 <= nsig(t) <= 6 and "|" not in t["seq"] and "#" not in t["seq"]]
    R["heldout"] = evaluate(longs, pool, "held-out long texts", nnull=1000)
    sh = [text_stats(t) for t in pool if nsig(t) >= 2]
    R["heldout_short_reference"] = {k: float(np.nanmean([s[k] for s in sh])) for k in KEYS}
    print("held-out short texts:", {k: round(v, 3) for k, v in R["heldout_short_reference"].items()})
    ic = icit_new_long_all = icit_new_long()
    il = [t for t in ic if is_long(t)]
    ipool = [t for t in ic if 1 <= nsig(t) <= 6 and "|" not in t["seq"] and "#" not in t["seq"]]
    if il:
        R["icit_new_sites"] = evaluate(il, ipool, "ICIT new-site long texts (OOV = unknown noun)", nnull=1000)
    json.dump(R, open(HERE / "f6_heldout.json", "w"), indent=1, default=float)
