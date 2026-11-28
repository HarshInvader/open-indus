"""S3: independent re-implementation of README finding #3 (ticked fish close texts), written from the
finding's description only. Pre-registration: docs/prereg/s3_ticked_fish_reimpl.md (sealed before running).

Run from the repo root:  .venv/bin/python -I experiments/s3_ticked_fish_reimpl/run.py
Writes experiments/s3_ticked_fish_reimpl/results.json. Deterministic: no set is iterated where order
matters, and every random draw comes from a named, seeded NumPy stream.
"""
import json, sys, zlib
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout

HERE = Path(__file__).resolve().parent
SEED = 20261128
TICKED = ("M60", "M66", "M68", "M71", "M73")
PLAIN = ("M59", "M65", "M67", "M70", "M72")
# bridge_WM.json: W226->M60, W236->M66, W241->M68, W232->M71 (M73 has no W number); plain W220,W235,W240,W231,W233
W_TICKED = ("W226", "W236", "W241", "W232")
W_PLAIN = ("W220", "W235", "W240", "W231", "W233")
NONNATIVE_REGIONS = ("Persian Gulf", "Mesopotamia", "Iranian Plateau", "Central Asia", "Other")
M77_SITE_KEYS = ("mohenjo", "harappa", "lothal", "kalibangan", "chanhu")
N_SHUF, N_PLANT = 100_000, 2_000


def rng(tag):
    return np.random.default_rng([SEED, zlib.crc32(tag.encode())])


def clean_m77(texts):
    return [t["seq"] for t in texts
            if t["site"] != "West Asian finds" and t["complete"] and t["n_lines"] == 1
            and "#" not in t["seq"] and "|" not in t["seq"] and t["seq"]]


def tokens(seqs, S):
    """(text index, position, length, is_final) for every token of a sign in S."""
    return [(i, j, len(s), j == len(s) - 1) for i, s in enumerate(seqs) for j, x in enumerate(s) if x in S]


def fisher(tk, pl):
    k1, n1 = sum(t[3] for t in tk), len(tk); k0, n0 = sum(t[3] for t in pl), len(pl)
    p = stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]], alternative="greater")[1] if n1 and n0 else None
    return dict(ticked=[k1, n1], plain=[k0, n0], ticked_rate=round(k1 / n1, 3) if n1 else None,
                plain_rate=round(k0 / n0, 3) if n0 else None, p_fisher=None if p is None else float(p))


def poisson_binomial_sf(probs, k):
    """Exact P(X >= k) for a sum of independent Bernoullis."""
    dist = np.zeros(len(probs) + 1); dist[0] = 1.0
    for q in probs:
        dist[1:] = dist[1:] * (1 - q) + dist[:-1] * q; dist[0] *= (1 - q)
    return float(dist[k:].sum())


def length_matched(tk):
    tk = [t for t in tk if t[2] >= 2]
    probs = [1 / t[2] for t in tk]; k = sum(t[3] for t in tk)
    return dict(n=len(tk), final=k, expected=round(sum(probs), 2), expected_rate=round(sum(probs) / max(1, len(tk)), 3),
                p=poisson_binomial_sf(probs, k) if tk else None)


def within_text_shuffle(seqs, T, P, n, g):
    """Null: shuffle signs within each text. Statistic: ticked final rate minus plain final rate."""
    rel = [s for s in seqs if any(x in T or x in P for x in s)]
    L = np.array([len(s) for s in rel])
    def stat(arrs):
        kt = nt = kp = np_ = 0
        for s in arrs:
            last = len(s) - 1
            for j, x in enumerate(s):
                if x in T: nt += 1; kt += j == last
                elif x in P: np_ += 1; kp += j == last
        return kt / nt - kp / np_
    obs = stat(rel)
    # vectorised: for each text, which position is last after a shuffle = a uniform random index of the
    # original signs; so per shuffle, each text's final sign is one of its own signs chosen uniformly.
    cls = [np.array([1 if x in T else 2 if x in P else 0 for x in s]) for s in rel]
    nt = sum(int((c == 1).sum()) for c in cls); np_ = sum(int((c == 2).sum()) for c in cls)
    null = np.empty(n); B = 10_000
    for b0 in range(0, n, B):
        b = min(B, n - b0)
        kt = np.zeros(b); kp = np.zeros(b)
        for c, l in zip(cls, L):
            pick = c[g.integers(l, size=b)]
            kt += pick == 1; kp += pick == 2
        null[b0:b0 + b] = kt / nt - kp / np_
    return dict(n_texts=len(rel), obs_diff=round(obs, 4), null_mean=round(float(null.mean()), 4),
                p=(1 + int((null >= obs - 1e-12).sum())) / (n + 1))


def planted(seqs, n_ticked, n, g):
    """Relabel fish tokens into a pseudo-ticked class of the real ticked size. (i) uniform; (ii) final-weighted
    so the expected planted final rate is 0.5. Report how often T1 (and T3, on a subsample) passes."""
    fish = tokens(seqs, set(TICKED) | set(PLAIN))
    fin = np.array([t[3] for t in fish]); idx = np.arange(len(fish))
    def run(weights, k3):
        pass1 = pass3 = 0
        w = weights / weights.sum()
        for r in range(n):
            pick = g.choice(idx, size=n_ticked, replace=False, p=w)
            m = np.zeros(len(fish), bool); m[pick] = True
            k1, n1 = int(fin[m].sum()), n_ticked; k0, n0 = int(fin[~m].sum()), int((~m).sum())
            p = stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]], alternative="greater")[1]
            pass1 += p < 0.05
            if r < k3:  # T3 is slower: run it on the first k3 replicates with 2,000 shuffles each
                lab = {}
                for t, mm in zip(fish, m): lab[(t[0], t[1])] = mm
                Tseqs = [[("T" if lab.get((i, j)) else "P") if (i, j) in lab else x for j, x in enumerate(s)]
                         for i, s in enumerate(seqs)]
                pass3 += within_text_shuffle(Tseqs, {"T"}, {"P"}, 2_000, g)["p"] < 0.05
        return dict(reps=n, t1_pass_rate=round(pass1 / n, 3), t3_reps=k3, t3_pass_rate=round(pass3 / k3, 3))
    uni = run(np.ones(len(fish)), 200)
    # final-weighted: choose weight w_f on final tokens so that expected share of finals in the pick is 0.5
    nf = fin.sum(); nn = len(fin) - nf; wf = nn / nf  # equal total weight on finals and non-finals
    eff = run(np.where(fin, wf, 1.0), 200)
    return dict(n_fish_tokens=len(fish), n_final_fish=int(nf), uniform_null=uni, planted_50pct_final=eff)


def holm(ps):
    o = np.argsort(ps); m = len(ps); out = np.empty(m); run = 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (m - r) * ps[i])); out[i] = run
    return out


def main():
    OUT = dict(seed=SEED, ticked=TICKED, plain=PLAIN)
    dev, ho = dev_heldout(version=2)
    cd, ch = clean_m77(dev), clean_m77(ho)
    OUT["n_clean_texts"] = dict(dev=len(cd), heldout=len(ch))
    tk_h, pl_h = tokens(ch, set(TICKED)), tokens(ch, set(PLAIN))
    OUT["per_sign_heldout"] = {s: [sum(t[3] for t in tokens(ch, {s})), len(tokens(ch, {s}))] for s in TICKED + PLAIN}
    OUT["T1_heldout_fisher"] = fisher(tk_h, pl_h)
    OUT["T1_heldout_fisher"]["ticked_texts"] = len({t[0] for t in tk_h})
    OUT["T2_heldout_length_matched"] = length_matched(tk_h)
    OUT["T3_heldout_within_text_shuffle"] = within_text_shuffle(ch, set(TICKED), set(PLAIN), N_SHUF, rng("T3"))
    OUT["T4_dev_fisher"] = fisher(tokens(cd, set(TICKED)), tokens(cd, set(PLAIN)))
    OUT["T4_dev_length_matched"] = length_matched(tokens(cd, set(TICKED)))

    I = distinct([t for t in icit_texts() if t["region"] not in NONNATIVE_REGIONS])
    ci = [t["seq"] for t in I if t["complete"] and len(t["segments"]) == 1 and "#" not in t["seq"]
          and "|" not in t["seq"] and t["seq"]]
    tk_i, pl_i = tokens(ci, set(W_TICKED)), tokens(ci, set(W_PLAIN))
    OUT["T5_icit_native"] = dict(n_clean_texts=len(ci), length_matched=length_matched(tk_i), fisher=fisher(tk_i, pl_i))
    new = [t["seq"] for t in I if t["complete"] and len(t["segments"]) == 1 and "#" not in t["seq"]
           and "|" not in t["seq"] and t["seq"] and not any(k in t["site"].lower().replace("-", "") for k in M77_SITE_KEYS)]
    tk_n = tokens(new, set(W_TICKED))
    OUT["T5b_icit_sites_not_in_M77"] = dict(n_clean_texts=len(new), length_matched=length_matched(tk_n),
                                            fisher=fisher(tk_n, tokens(new, set(W_PLAIN))),
                                            sites=sorted({t["site"] for t in I if t["seq"] in new and any(x in W_TICKED for x in t["seq"])}))

    ps = [OUT["T1_heldout_fisher"]["p_fisher"], OUT["T2_heldout_length_matched"]["p"],
          OUT["T3_heldout_within_text_shuffle"]["p"], OUT["T5_icit_native"]["length_matched"]["p"]]
    OUT["holm"] = dict(zip(["T1", "T2", "T3", "T5"], [float(x) for x in holm(np.array(ps))]))
    OUT["planted_control"] = planted(ch, len(tk_h), N_PLANT, rng("plant"))
    json.dump(OUT, open(HERE / "results.json", "w"), indent=1)
    print(json.dumps(OUT, indent=1))


if __name__ == "__main__":
    main()
