"""Planted-answer control for exp3 T1/T2: create artificial allographs by
relabelling a random 8% of a sign's tokens as a new sign X' (freq ~ the real
derived signs, 5-60 tokens) and check that the PPMI-cosine test against
frequency-matched partners flags (base, X') at p<0.05. Also a negative
control: X' built from tokens of a DIFFERENT sign (should not be flagged)."""
from common import *
from exp3_sign_morphology import context_matrix, ppmi, cos


def test(texts, b, d, rng):
    freq = Counter(s for t in texts for s in t)
    signs = sorted(s for s in freq if freq[s] >= 3)
    si = {s: k for k, s in enumerate(signs)}
    P = ppmi(context_matrix(texts), signs)
    fr = np.array([freq[s] for s in signs], float)
    f = freq[d]
    cand = [k for k in np.where((fr >= f / 2) & (fr <= 2 * f))[0] if signs[k] not in (b, d)]
    obs = cos(P[si[b]], P[si[d]])
    nl = np.array([cos(P[si[b]], P[k]) for k in cand])
    return (1 + (nl >= obs).sum()) / (1 + len(nl))


def main():
    rng = np.random.default_rng(5)
    D, _ = load_split()
    bases = ["M342", "M99", "M59", "M267", "M87", "M391", "M211", "M162", "M336", "M65", "M67", "M72", "M176", "M89", "M343"]
    pos, neg = [], []
    for rep in range(3):
        for b in bases:
            # positive: split b
            T = [tuple((b + "'" if (s == b and rng.random() < 0.08) else s) for s in t) for t in D]
            if sum(s == b + "'" for t in T for s in t) >= 3:
                pos.append(test(T, b, b + "'", rng))
            # negative: X' drawn from another frequent sign
            o = bases[rng.integers(len(bases))]
            if o == b:
                continue
            T = [tuple((o + "'" if (s == o and rng.random() < 0.08) else s) for s in t) for t in D]
            if sum(s == o + "'" for t in T for s in t) >= 3:
                neg.append(test(T, b, o + "'", rng))
    pos, neg = np.array(pos), np.array(neg)
    res = dict(planted_allograph_detect_rate=float((pos < 0.05).mean()), n_pos=len(pos),
               false_positive_rate=float((neg < 0.05).mean()), n_neg=len(neg))
    print(res)
    save_json("exp3b_planted_control", res)


if __name__ == "__main__":
    main()
