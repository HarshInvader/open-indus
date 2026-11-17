"""Red team of board #30 (README #3: ticked fish close the text), independent of harness.py.

Built from corpus/load.py only. Attacks: (1) completeness/doubtful readings, (2) genre and length
(short texts make 'final' cheap), (3) choice of null, (4) small n (CI, leave-one-out, splits),
(5) replication on ICIT texts from sites that are not in M77 at all.
    board/run.sh .venv/bin/python -I experiments/redteam_tick_complete/run.py
"""
import sys, json, random
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import fisher_exact, binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "corpus"))
import load as L  # noqa

TICK_M = {"M60", "M66", "M68", "M71", "M73"}
PLAIN_M = {"M59", "M65", "M67", "M70", "M72"}
TICK_W = {"W226", "W232", "W234", "W236", "W241"}
PLAIN_W = {"W220", "W231", "W233", "W235", "W240"}
RNG = np.random.default_rng(31)
REPS = 20000
OUT = {}


def single_complete(ts):
    return [t for t in ts if t["complete"] and "|" not in t["seq"] and "#" not in t["seq"] and len(t["seq"]) >= 2]


def tokens(ts, S):
    """(is_final, text_len, text_index) for each token of a sign in S."""
    out = []
    for j, t in enumerate(ts):
        n = len(t["seq"])
        for i, s in enumerate(t["seq"]):
            if s in S:
                out.append((i == n - 1, n, j))
    return out


def summary(ts, S):
    tk = tokens(ts, S)
    k = sum(f for f, _, _ in tk); n = len(tk)
    exp = sum(1 / L_ for _, L_, _ in tk)          # final by chance if position were uniform
    return k, n, exp


def perm_within_text(ts, S):
    """Shuffle sign order inside each text (keeps length and inventory). p of >= observed finals."""
    tk = tokens(ts, S)
    k = sum(f for f, _, _ in tk)
    # number of S-signs in each text and length
    per = Counter(j for _, _, j in tk)
    lens = {j: len(ts[j]["seq"]) for j in per}
    sims = np.zeros(REPS)
    for j, m in per.items():
        # P(final sign is one of the m S-tokens) = m/L ; final count per text is 0/1
        sims += RNG.random(REPS) < m / lens[j]
    return k, float(sims.mean()), float((1 + (sims >= k).sum()) / (1 + REPS))


def length_matched_band(ts, S, exclude, dev_freq, lo=10, hi=80):
    """Null: for each S token, draw a random token of a band sign from a text of the SAME length."""
    by_len = defaultdict(list)
    band = {s for s, c in dev_freq.items() if lo <= c <= hi and s not in exclude}
    for t in ts:
        n = len(t["seq"])
        for i, s in enumerate(t["seq"]):
            if s in band:
                by_len[n].append(i == n - 1)
    tk = tokens(ts, S)
    k = sum(f for f, _, _ in tk)
    sims = np.zeros(REPS)
    for _, n, _ in tk:
        pool = by_len.get(n) or by_len[min(by_len, key=lambda x: abs(x - n))]
        sims += RNG.random(REPS) < np.mean(pool)
    return k, float(sims.mean()), float((1 + (sims >= k).sum()) / (1 + REPS))


def all_signs_rate_by_len(ts, exclude):
    by_len = defaultdict(list)
    for t in ts:
        n = len(t["seq"])
        for i, s in enumerate(t["seq"]):
            if s not in exclude:
                by_len[n].append(i == n - 1)
    return by_len


def block(name, ts, tick, plain, dev_freq):
    k, n, exp = summary(ts, tick)
    kp, np_, expp = summary(ts, plain)
    r = dict(texts=len(ts), tick_final=k, tick_n=n, tick_share=round(k / n, 3) if n else None,
             tick_expected_uniform=round(exp, 2), plain_final=kp, plain_n=np_,
             plain_share=round(kp / np_, 3) if np_ else None)
    if n:
        ci = binomtest(k, n).proportion_ci(method="exact")
        r["tick_ci95"] = [round(ci.low, 3), round(ci.high, 3)]
        r["fisher_tick_vs_plain_p"] = float(fisher_exact([[k, n - k], [kp, np_ - kp]], alternative="greater")[1])
        r["perm_within_text"] = perm_within_text(ts, tick)
        r["length_matched_band"] = length_matched_band(ts, tick, tick | plain, dev_freq)
        r["length_matched_allsigns"] = length_matched_band(ts, tick, tick | plain, dev_freq, 1, 10 ** 9)
    OUT[name] = r
    print(name, json.dumps(r), flush=True)
    return r


def main():
    dev, ho = L.dev_heldout(version=2)
    dev_freq = Counter(s for t in dev for s in t["seq"] if s not in "|#")
    lines = L.m77_lines()
    doubt = {(l["text_no"], l["side"]) for l in lines if l["doubtful"]}
    sites = Counter(t["site"] for t in ho)

    H1 = single_complete(ho)
    block("A0_reproduce_heldout_single_complete", H1, TICK_M, PLAIN_M, dev_freq)
    # (1) completeness: drop any text with a doubtful reading anywhere
    H1d = [t for t in H1 if (t["text_no"], t["side"]) not in doubt]
    block("A1_no_doubtful_readings", H1d, TICK_M, PLAIN_M, dev_freq)
    # list the ticked-fish texts for inspection
    OUT["A1_ticked_texts"] = [dict(text_no=t["text_no"], side=t["side"], site=t["site"], obj=t["object_type"],
                                   seq=t["seq"], doubtful=(t["text_no"], t["side"]) in doubt)
                              for t in H1 if set(t["seq"]) & TICK_M]
    # (2) genre: seals only; length >= 3; length >= 4
    block("A2_seals_only", [t for t in H1 if t["object_type"] == "seal"], TICK_M, PLAIN_M, dev_freq)
    block("A2_len_ge3", [t for t in H1 if len(t["seq"]) >= 3], TICK_M, PLAIN_M, dev_freq)
    block("A2_len_ge4", [t for t in H1 if len(t["seq"]) >= 4], TICK_M, PLAIN_M, dev_freq)
    # also: multi-line complete texts, final of the WHOLE text (last line's last sign)
    ML = [dict(t, seq=[s for s in t["seq"] if s != "|"]) for t in ho
          if t["complete"] and "|" in t["seq"] and "#" not in t["seq"]]
    block("A2_multiline_whole_text_final", ML, TICK_M, PLAIN_M, dev_freq)
    # (4) sites
    block("A4_mohenjodaro", [t for t in H1 if t["site"] == "Mohenjodaro"], TICK_M, PLAIN_M, dev_freq)
    block("A4_harappa", [t for t in H1 if t["site"] == "Harappa"], TICK_M, PLAIN_M, dev_freq)
    block("A4_other_sites", [t for t in H1 if t["site"] not in ("Mohenjodaro", "Harappa")], TICK_M, PLAIN_M, dev_freq)
    # leave-one-text-out on the ticked texts: worst-case p (length-matched null)
    tick_idx = [j for j, t in enumerate(H1) if set(t["seq"]) & TICK_M]
    loo = []
    for j in tick_idx:
        sub = [t for i, t in enumerate(H1) if i != j]
        loo.append(length_matched_band(sub, TICK_M, TICK_M | PLAIN_M, dev_freq)[2])
    OUT["A4_loo_worst_p"] = max(loo)
    print("LOO worst p", max(loo))
    # dev (where #3 was found; not independent) for scale
    block("A4_dev_single_complete_not_independent", single_complete(dev), TICK_M, PLAIN_M, dev_freq)
    # (5) ICIT: sites with no M77 texts at all = true out-of-corpus replication
    m77_sites = {t["site"].lower().replace("-", "").replace(" ", "") for t in L.m77_texts()}
    I = L.distinct(L.icit_texts())
    def norm(s): return s.lower().replace("-", "").replace(" ", "")
    alias = {"mohenjodaro", "harappa", "chanhudaro", "lothal", "kalibangan"}
    new = [t for t in I if norm(t["site"]) not in m77_sites and norm(t["site"]) not in alias]
    OUT["A5_new_sites"] = Counter(t["site"] for t in new).most_common()
    icit_freq = Counter(s for t in I if norm(t["site"]) in m77_sites | alias for s in t["seq"] if s not in "|#")
    block("A5_icit_new_sites_single_complete", single_complete(new), TICK_W, PLAIN_W, icit_freq)
    block("A5_icit_new_sites_all_runs_any",
          [dict(t, seq=r) for t in new for r in L.runs(t["seq"]) if t["complete"]], TICK_W, PLAIN_W, icit_freq)
    json.dump(OUT, open(HERE / "results.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
