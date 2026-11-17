"""Red team claim C: long texts (10+ signs, or multi-line 8+) are one stretched seal template.
Reuses the FROZEN functional grammar (experiments/functional_reading/fr.py, fit on dev) as the parser, but
re-implements the long-text selection, nulls and statistics independently, and adds stronger nulls:
  concat_exact : each line refilled with whole random held-out short texts (1-6 signs, 1 line) summing EXACTLY to
                 the line length (the claimed null).
  concat_trunc : same, but the last text is truncated to fit (a weaker variant some implementations use).
  bigram       : KN-free add-k bigram over DEV short-text lines, sampled EXACTLY conditioned on line length
                 (backward DP), i.e. a local Markov model that knows nothing about a template.
  bigram_long  : same bigram but trained on DEV lines of ALL lengths.
  grammar      : sampled from the grammar itself (role PFSA + emissions) conditioned on length = upper bound.
Usage: .venv/bin/python experiments/redteam_pnl/c_long.py
"""
import sys, math
import numpy as np
from collections import Counter, defaultdict
from rt_common import *  # noqa
sys.path.insert(0, str(ROOT / "experiments" / "functional_reading"))
import fr  # noqa

rng = np.random.default_rng(11)
NDRAW = 300


def nsigns(t):
    return sum(1 for s in t["seq"] if s not in ("|", "#"))


def is_long(t):
    n = nsigns(t); nl = len(runs([s if s != "#" else "|" for s in t["seq"]]))
    return n >= 10 or ("|" in t["seq"] and n >= 8)


def lines_of(t):
    return [r for (r, a, b) in fr.clean_runs(t)]


def closer_set(lex):
    return {s for s, e in lex.items() if e["roles"] <= {"J", "P", "B"}}


def resets(lines, CL):
    """closer-class sign followed (same line) by a sign that cannot be closer/post-closer."""
    n = 0; tot = 0
    for r in lines:
        tot += len(r)
        for a, b in zip(r, r[1:]):
            if a in CL and b not in CL:
                n += 1
    return n, tot


class Bigram:
    def __init__(self, lines, k=0.01):
        V = sorted({s for r in lines for s in r}); self.V = V; self.ix = {s: i for i, s in enumerate(V)}
        n = len(V); self.n = n
        C = np.full((n + 1, n + 1), k)  # row n = start, col n = end
        for r in lines:
            idx = [self.ix[s] for s in r]
            C[n, idx[0]] += 1
            for a, b in zip(idx, idx[1:]): C[a, b] += 1
            C[idx[-1], n] += 1
        C[n, n] = 0
        self.P = C / C.sum(1, keepdims=True)
        self.cache = {}

    def sample(self, L, m):
        """m sequences of exactly L tokens, conditioned on the end token after L."""
        n = self.n; T = self.P[:n, :n]; end = self.P[:n, n]
        if L not in self.cache:
            beta = [end]  # beta[j][a] = P(end after exactly j more tokens | at a)
            for j in range(1, L):
                beta.append(T @ beta[-1])
            self.cache[L] = beta
        beta = self.cache[L]
        out = []
        for _ in range(m):
            w = self.P[n, :n] * beta[L - 1]; w /= w.sum()
            a = rng.choice(n, p=w); seq = [a]
            for j in range(L - 2, -1, -1):
                w = T[a] * beta[j]; w /= w.sum(); a = rng.choice(n, p=w); seq.append(a)
            out.append([self.V[i] for i in seq])
        return out


def grammar_sample(G, L, m, vocab):
    """Sample role paths of length L from the PFSA conditioned on length, then signs from emissions."""
    K = len(fr.ROLES); T = G.trans; end = G.end
    beta = [end]
    for j in range(1, L): beta.append(T @ beta[-1])
    E = np.array([G.emis_vec(s) for s in vocab])  # V x K
    Ecol = E / np.maximum(E.sum(0, keepdims=True), 1e-300)
    out = []
    for _ in range(m):
        w = G.start * beta[L - 1]; w /= w.sum(); k = rng.choice(K, p=w); path = [k]
        for j in range(L - 2, -1, -1):
            w = T[k] * beta[j]; w /= w.sum(); k = rng.choice(K, p=w); path.append(k)
        out.append([vocab[rng.choice(len(vocab), p=Ecol[:, k])] for k in path])
    return out


def concat_fill(L, shorts, trunc):
    """Fill length L with whole short texts. exact: rejection until sum == L."""
    for _ in range(2000):
        out = []
        while len(out) < L:
            out += shorts[rng.integers(len(shorts))]
        if len(out) == L:
            return out
        if trunc:
            return out[:L]
    return out[:L]


def accept_lines(G, lines):
    return all(np.isfinite(G.logprob(r)) for r in lines)


def main():
    dev, ho, dev_g, lex, comps, G = fr.load_model()
    CL = closer_set(lex)
    R = {}
    for split, texts in (("dev", dev), ("heldout", ho)):
        L = [t for t in texts if is_long(t)]
        shorts_pool = [lines_of(t)[0] for t in texts
                       if "|" not in t["seq"] and "#" not in t["seq"] and 1 <= nsigns(t) <= 6]
        real_lines = [lines_of(t) for t in L]
        multi = [t for t in L if "|" in t["seq"]]
        brk = [t for t in L if "#" in t["seq"]]
        acc = [G.accepts(t) for t in L]
        acc_single = [G.accepts(t) for t in L if "|" not in t["seq"]]
        acc_multi = [G.accepts(t) for t in L if "|" in t["seq"]]
        # multi-line texts parsed as ONE run (line breaks ignored)
        joined = [accept_lines(G, [[s for s in t["seq"] if s not in ("|",)]]) if "#" not in t["seq"] else G.accepts(t)
                  for t in L]
        rs, tot = zip(*[resets(ls, CL) for ls in real_lines])
        real_reset = 10 * sum(rs) / sum(tot)
        # short texts acceptance (same split)
        sh = [t for t in texts if not is_long(t)]
        short_acc = float(np.mean([G.accepts(t) for t in sh]))
        # nulls: per text, per line
        dev_short_lines = [lines_of(t)[0] for t in dev_g if "|" not in t["seq"] and "#" not in t["seq"]
                           and 1 <= nsigns(t) <= 6]
        dev_all_lines = [r for t in dev_g if "#" not in t["seq"] for r in lines_of(t)]
        BG = Bigram(dev_short_lines); BGL = Bigram(dev_all_lines)
        vocab = sorted({s for r in dev_all_lines for s in r})
        nulls = {}
        for name in ("concat_exact", "concat_trunc", "bigram_short", "bigram_all", "grammar"):
            accs, rss = [], []
            # pre-sample per line length
            need = Counter(len(r) for ls in real_lines for r in ls)
            bank = {}
            for Ln, c in need.items():
                m = c * NDRAW
                if name == "bigram_short": bank[Ln] = BG.sample(Ln, m)
                elif name == "bigram_all": bank[Ln] = BGL.sample(Ln, m)
                elif name == "grammar": bank[Ln] = grammar_sample(G, Ln, m, vocab)
                else: bank[Ln] = [concat_fill(Ln, shorts_pool, name == "concat_trunc") for _ in range(m)]
            ptr = Counter()
            for d in range(NDRAW):
                a, rr, tt = [], 0, 0
                for ls in real_lines:
                    sim = []
                    for r in ls:
                        sim.append(bank[len(r)][ptr[len(r)]]); ptr[len(r)] += 1
                    a.append(accept_lines(G, sim))
                    x, y = resets(sim, CL); rr += x; tt += y
                accs.append(np.mean(a)); rss.append(10 * rr / tt)
            accs, rss = np.array(accs), np.array(rss)
            nulls[name] = dict(accept_mean=float(accs.mean()), accept_p_null_ge_real=float((1 + (accs >= np.mean(acc)).sum()) / (NDRAW + 1)),
                               accept_p_null_le_real=float((1 + (accs <= np.mean(acc)).sum()) / (NDRAW + 1)),
                               reset_mean=float(rss.mean()), reset_p_null_le_real=float((1 + (rss <= real_reset).sum()) / (NDRAW + 1)))
        # baseline: what share of short texts END in a closer-class sign (drives concat failure)
        end_closer = float(np.mean([r[-1] in CL for r in shorts_pool]))
        # length-matched comparison: acceptance of real lines vs line length
        bylen = defaultdict(list)
        for t in texts:
            if "#" in t["seq"]: continue
            for r in lines_of(t):
                bylen[min(len(r), 10)].append(np.isfinite(G.logprob(r)))
        R[split] = dict(n_long=len(L), n_multiline=len(multi), n_with_break=len(brk),
                        accept=float(np.mean(acc)), accept_single_line=(float(np.mean(acc_single)), len(acc_single)),
                        accept_multiline=(float(np.mean(acc_multi)), len(acc_multi)) if acc_multi else None,
                        accept_multiline_joined_as_one_run=float(np.mean(joined)),
                        resets_per10=real_reset, short_text_accept=short_acc,
                        short_texts_ending_in_closer=end_closer, nulls=nulls,
                        line_accept_by_length={k: (round(float(np.mean(v)), 3), len(v)) for k, v in sorted(bylen.items())},
                        long_line_lengths=[[len(r) for r in ls] for ls in real_lines])
        print(f"\n===== {split}: long n={len(L)} (multi-line {len(multi)}, with break {len(brk)})")
        for k, v in R[split].items():
            if k not in ("nulls", "long_line_lengths"): print(f"  {k}: {v}")
        for k, v in nulls.items(): print(f"  null {k}: {v}")
    dump(R, "c_results.json")


if __name__ == "__main__":
    main()
