"""Check A (board #28): does README #1's order test (harness T1) separate grammar from a fixed format?

Runs signlist_robustness/harness.py t1_order, unchanged, on the short_labels calibration corpora
(real short-label writing, real codes, synthetic codes) and on Indus (M77, split v2, type unit).
Pre-registration: docs/prereg/audit_followups.md (section A).

    board/run.sh .venv/bin/python -I experiments/audit_followups/a_order_formats.py
"""
import sys, json, random
from pathlib import Path
from collections import Counter, defaultdict
import itertools

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
sys.path.insert(0, str(ROOT / "experiments" / "short_labels"))
import harness as H  # noqa
import sl_corpora as SL  # noqa
from rt_common import near_dup_clusters  # noqa  (path added by harness)

SEEDS = [0, 1, 2, 3, 4]
N_DEV, N_HO = 1699, 571          # Indus split v2 distinct-text sizes (dev, held-out)
LENS = range(3, 8)
PRIMARY_L = ["cun_seal_ur3", "cun_seal_ob", "linb_line", "egy_nom", "lat_label", "lat_short"]
PRIMARY_C = ["heraldry", "khipu", "icd10", "emoji", "chess_eco", "chords", "metar"]
SENS = ["cun_seal_oakk", "lina_label", "plates", "slot", "sigil"]


def qualifying(r):
    return 3 <= len(r) <= 7 and len(set(itertools.permutations(r))) >= 6


def per_length(dev, ho):
    """t1_order run separately on held-out runs of each length -> {L: (n, share, chance)}."""
    out = {}
    for L in LENS:
        sub = [t for t in ho if any(len(r) == L for r in H.runs(t["seq"]))]
        # keep only runs of length L: rebuild texts as single runs
        sub = [dict(seq=r, complete=True) for t in sub if t["complete"] for r in H.runs(t["seq"]) if len(r) == L]
        res = H.t1_order(dev, sub)
        out[L] = (res["n_runs"], res["share"], res["chance"])
    return out


def standardise(pl, w):
    num = den = cnum = 0.0
    for L, wl in w.items():
        n, s, c = pl.get(L, (0, 0, 0))
        if n == 0: continue
        num += wl * s; cnum += wl * c; den += wl
    return (num / den, cnum / den) if den else (None, None)


def family_split(units, seed):
    cl = near_dup_clusters(units)
    r = random.Random(seed); r.shuffle(cl)
    cut = int(0.75 * len(cl))
    dev = [s for c in cl[:cut] for s in c]
    ho = [s for c in cl[cut:] for s in c]
    return dev, ho


def run_corpus(name, w):
    pool = sorted({tuple(t) for t in SL.pool(name)})
    rows = []
    for seed in SEEDS:
        r = random.Random(1000 + seed)
        samp = r.sample(pool, min(len(pool), N_DEV + N_HO))
        dev, ho = family_split(samp, seed)
        dev = [dict(seq=list(s), complete=True) for s in dev]
        ho = [dict(seq=list(s), complete=True) for s in ho]
        raw = H.t1_order(dev, ho)
        pl = per_length(dev, ho)
        S, C = standardise(pl, w)
        rows.append(dict(seed=seed, pool=len(pool), n_sample=len(samp), n_dev=len(dev), n_ho=len(ho), raw=raw,
                         per_length={L: list(v) for L, v in pl.items()}, S=S, S_chance=C))
    Ss = [x["S"] for x in rows if x["S"] is not None]
    return dict(name=name, label=SL.REG[name][0], set=SL.REG[name][2], seeds=rows,
                S_median=sorted(Ss)[len(Ss) // 2] if Ss else None, S_min=min(Ss) if Ss else None, S_max=max(Ss) if Ss else None,
                raw_share_median=sorted(x["raw"]["share"] for x in rows)[len(rows) // 2],
                raw_ratio_median=sorted((x["raw"]["ratio"] or 0) for x in rows)[len(rows) // 2])


def main():
    out_p = HERE / "out" / "a_order_formats.json"
    out_p.parent.mkdir(exist_ok=True)
    V = H.Variant("M77")
    C = H.build_corpus(V)
    dev, ho = C["dev_type"], C["ho_type"]
    ind_raw = H.t1_order(dev, ho)
    # Indus held-out qualifying run-length mix = the standardisation weights
    cnt = Counter(len(r) for t in ho if t["complete"] for r in H.runs(t["seq"]) if qualifying(r))
    tot = sum(cnt.values())
    w = {L: cnt[L] / tot for L in LENS if cnt[L]}
    ind_pl = per_length(dev, ho)
    S_I, C_I = standardise(ind_pl, w)
    res = dict(indus=dict(raw=ind_raw, per_length={L: list(v) for L, v in ind_pl.items()}, S=S_I, S_chance=C_I, weights=w),
               corpora={})
    print("Indus", ind_raw, "S", S_I, flush=True)
    for name in PRIMARY_L + PRIMARY_C + SENS:
        res["corpora"][name] = run_corpus(name, w)
        c = res["corpora"][name]
        print(name, c["label"], "S med", c["S_median"], "range", c["S_min"], c["S_max"], "raw", c["raw_share_median"],
              "ratio", c["raw_ratio_median"], flush=True)
    # pre-registered decision rule
    thr_hi, thr_lo = 0.75 * S_I, 0.5 * S_I
    codes = {n: res["corpora"][n]["S_median"] for n in PRIMARY_C}
    langs = {n: res["corpora"][n]["S_median"] for n in PRIMARY_L}
    n_codes_hi = sum(v is not None and v >= thr_hi for v in codes.values())
    all_codes_lo = all(v is not None and v < thr_lo for v in codes.values())
    n_lang_hi = sum(v is not None and v >= thr_hi for v in langs.values())
    if n_codes_hi >= 2:
        verdict = "cannot separate: >=2 real codes reach 0.75 x Indus"
    elif all_codes_lo and n_lang_hi >= 4:
        verdict = "separates: every real code < 0.5 x Indus and >=4 of 6 writing corpora >= 0.75 x Indus"
    else:
        verdict = "undecided"
    res["decision"] = dict(S_I=S_I, thr_hi=thr_hi, thr_lo=thr_lo, n_codes_hi=n_codes_hi, all_codes_lo=all_codes_lo,
                           n_lang_hi=n_lang_hi, verdict=verdict)
    print(res["decision"], flush=True)
    json.dump(res, open(out_p, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
