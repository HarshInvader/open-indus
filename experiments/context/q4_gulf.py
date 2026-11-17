"""Q4. Are texts found in the Gulf / Mesopotamia / Iran / Central Asia statistically anomalous under an
n-gram model of Indus-native texts?

Model: interpolated Kneser-Ney bigram over signs with <s> and </s>, signs seen once in training -> <UNK>.
Native texts are scored by 10-fold CV (never by a model that saw them); foreign texts by a model trained
on all native texts. Unit = distinct sequence (per corpus). Statistic = mean bits per sign (incl. </s>).
Comparison = foreign mean vs mean of length-matched native draws (10,000 draws, same length multiset);
95% CI by bootstrap over foreign texts. Controls: (1) home round/cylinder seals (format, not findspot);
(2) peripheral Indus sites; (3) planted positives: native texts with within-text shuffled order, and
native texts with a frequency-matched sign substitution (same signs, different 'language') to show the
test has power at n~30. Replication: M77 'West Asian finds'.
"""
from common import *

rng = np.random.default_rng(4)

FOREIGN_WEST = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar",
                "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Dilmun", "Kalba"}
FOREIGN_CA = {"Gonur", "Gonur Depe", "Altyn Depe", "Shortughai"}


class KN:
    def __init__(self, texts, d=0.75):
        c = Counter(s for t in texts for s in t)
        self.V = {s for s, n in c.items() if n >= 2} | {"<UNK>", "</s>"}
        self.d = d
        big = Counter(); uni_ctx = Counter(); cont = defaultdict(set)
        for t in texts:
            t = ["<s>"] + [self.m(s) for s in t] + ["</s>"]
            for a, b in zip(t, t[1:]):
                big[(a, b)] += 1; uni_ctx[a] += 1; cont[b].add(a)
        self.big, self.uni_ctx = big, uni_ctx
        self.ntypes_after = Counter(a for (a, b) in big)
        tot = sum(len(v) for v in cont.values())
        self.pcont = {b: len(v) / tot for b, v in cont.items()}
        self.floor = 1e-4

    def m(self, s):
        return s if s in self.V else "<UNK>"

    def p(self, a, b):
        pc = self.pcont.get(b, 0) * (1 - self.floor) + self.floor / len(self.V)
        ca = self.uni_ctx.get(a, 0)
        if ca == 0:
            return pc
        lam = self.d * self.ntypes_after[a] / ca
        return max(self.big.get((a, b), 0) - self.d, 0) / ca + lam * pc

    def bits(self, t):
        t = ["<s>"] + [self.m(s) for s in t] + ["</s>"]
        return -sum(np.log2(self.p(a, b)) for a, b in zip(t, t[1:])) / (len(t) - 1)


def clean(seq):
    """Contiguous text with breaks removed; line breaks ignored (lines read on)."""
    return [s for s in seq if s not in ("|", "#")]


def cv_bits(texts, k=10):
    idx = rng.permutation(len(texts)); out = np.zeros(len(texts))
    for f in range(k):
        te = idx[f::k]; tr = np.setdiff1d(idx, te)
        m = KN([texts[i] for i in tr])
        for i in te: out[i] = m.bits(texts[i])
    return out


def compare(fbits, flens, nbits, nlens, label, ndraw=10000):
    bylen = defaultdict(list)
    for b, L in zip(nbits, nlens): bylen[min(L, 9)].append(b)
    bylen = {k: np.array(v) for k, v in bylen.items()}
    keys = [min(L, 9) for L in flens]
    draws = np.array([np.mean([rng.choice(bylen[k]) for k in keys]) for _ in range(ndraw)])
    obs = float(np.mean(fbits))
    boot = np.array([np.mean(rng.choice(fbits, len(fbits))) for _ in range(5000)])
    p = (1 + (draws >= obs).sum()) / (ndraw + 1)
    r = dict(n=len(fbits), bits=obs, native_matched=float(draws.mean()), diff=obs - float(draws.mean()),
             ci95=[float(np.quantile(boot, .025) - draws.mean()), float(np.quantile(boot, .975) - draws.mean())], p=float(p))
    print(f"  {label:45s} n={r['n']:4d} bits/sign {obs:.3f} vs matched native {draws.mean():.3f}: "
          f"diff {r['diff']:+.3f} [95% CI {r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}] p={p:.4f}")
    return r


def main():
    R = {}
    I = icit_texts()
    gs = open(SRC / "paragorth_Indus-/data/gulf_seals.csv").read()
    seen, native, foreign, unknown = set(), [], [], []
    for t in I:
        s = clean(t["seq"])
        if len(s) < 1: continue
        key = (" ".join(s))
        site = t["site"]
        grp = "west" if site in FOREIGN_WEST else "ca" if site in FOREIGN_CA else "unknown" if site == "Unknown" else "native"
        fmt = "round" if t["type"] in ("SEAL:R", "SEAL:C", "SEAL:CY") else "square" if t["type"].startswith("SEAL") else "other"
        rec = dict(seq=s, site=site, fmt=fmt, type=t["type"], grp=grp)
        if (grp, key) in seen: continue
        seen.add((grp, key))
        (native if grp == "native" else foreign if grp in ("west", "ca") else unknown).append(rec)
    # remove from native any text identical to a foreign one (so foreign texts are truly unseen)
    fkeys = {" ".join(r["seq"]) for r in foreign}
    native = [r for r in native if " ".join(r["seq"]) not in fkeys]
    print(f"ICIT: native distinct {len(native)}, foreign {len(foreign)} ({Counter(r['grp'] for r in foreign)}), unknown-provenance {len(unknown)}")
    print("  foreign sites:", dict(Counter(r["site"] for r in foreign)))
    ntexts = [r["seq"] for r in native]
    nb = cv_bits(ntexts); nl = np.array([len(t) for t in ntexts])
    m_all = KN(ntexts)
    fb = np.array([m_all.bits(r["seq"]) for r in foreign]); fl = [len(r["seq"]) for r in foreign]
    R["icit_all_foreign"] = compare(fb, fl, nb, nl, "ICIT all foreign")
    for g in ("west", "ca"):
        sel = [i for i, r in enumerate(foreign) if r["grp"] == g]
        if len(sel) >= 3:
            R[f"icit_{g}"] = compare(fb[sel], [fl[i] for i in sel], nb, nl, f"ICIT foreign {g}")
    for fm in ("round", "square", "other"):
        sel = [i for i, r in enumerate(foreign) if r["fmt"] == fm]
        if len(sel) >= 3:
            R[f"icit_foreign_{fm}"] = compare(fb[sel], [fl[i] for i in sel], nb, nl, f"ICIT foreign, format={fm}")
    ub = np.array([m_all.bits(r["seq"]) for r in unknown])
    R["icit_unknown_prov"] = compare(ub, [len(r["seq"]) for r in unknown], nb, nl, "ICIT unknown provenance")
    # format control: home round seals (scored by CV), compared with home square seals
    sq = np.array([r["fmt"] == "square" for r in native])
    rd = np.array([r["fmt"] == "round" for r in native])
    R["home_round_vs_square"] = compare(nb[rd], nl[rd], nb[sq], nl[sq], "HOME round/cyl seals vs home square seals")
    R["foreign_round_vs_home_round"] = compare(fb[[i for i, r in enumerate(foreign) if r["fmt"] == "round"]],
                                               [fl[i] for i, r in enumerate(foreign) if r["fmt"] == "round"], nb[rd], nl[rd],
                                               "FOREIGN round vs HOME round seals")
    # peripheral sites as a regional baseline
    core = np.array([r["site"] in ("Harappa", "Mohenjo-daro") for r in native])
    R["core_sites"] = compare(nb[core], nl[core], nb, nl, "native core (MD+Harappa) vs all native")
    for site in ("Dholavira", "Lothal", "Kalibangan", "Chanhu-daro", "Banawali"):
        s = np.array([r["site"] == site for r in native])
        if s.sum() >= 10:
            R[f"site_{site}"] = compare(nb[s], nl[s], nb, nl, f"native {site} vs all native")
    # OOV rate
    oov_f = np.mean([np.mean([x not in m_all.V for x in r["seq"]]) for r in foreign])
    R["oov_foreign"] = float(oov_f)
    print(f"  OOV (sign unseen or hapax in native): foreign {oov_f:.3f}")
    # planted positives: power at n = len(foreign)
    n = len(foreign)
    sel = rng.choice(len(native), size=400, replace=False)
    shuf = [list(rng.permutation(native[i]["seq"])) for i in sel]
    tr = [native[i]["seq"] for i in range(len(native)) if i not in set(sel)]
    mtr = KN(tr)
    freq = Counter(s for t in tr for s in t)
    ranked = [s for s, _ in freq.most_common()]
    # frequency-matched substitution: swap each sign with a neighbour in the frequency ranking
    sub = {}
    for i in range(0, len(ranked) - 1, 2):
        sub[ranked[i]] = ranked[i + 1]; sub[ranked[i + 1]] = ranked[i]
    subst = [[sub.get(s, s) for s in native[i]["seq"]] for i in sel]
    # partial substitution: only 30% of signs swapped (a related dialect)
    part = [[sub.get(s, s) if rng.random() < 0.3 else s for s in native[i]["seq"]] for i in sel]
    real = [native[i]["seq"] for i in sel]
    planted = {}
    for name, texts in (("real_heldout", real), ("shuffled_order", shuf), ("freq_matched_substitution", subst), ("30pct_substitution", part)):
        b = np.array([mtr.bits(t) for t in texts])
        L = np.array([len(t) for t in texts])
        base = np.array([mtr.bits(t) for t in real])
        # power at foreign sample size, length-matched to foreign lengths
        hits = 0
        for _ in range(500):
            pick = [rng.choice(np.where(np.minimum(L, 9) == min(k, 9))[0]) if (np.minimum(L, 9) == min(k, 9)).any() else rng.integers(len(L)) for k in fl]
            pick_b = rng.choice(len(base), len(pick))
            # one-sided Welch-like comparison against held-out real texts of the same lengths
            d = b[pick].mean() - base[pick_b].mean()
            null = [base[rng.choice(len(base), len(pick))].mean() - base[rng.choice(len(base), len(pick))].mean() for _ in range(200)]
            hits += d > np.quantile(null, 0.95)
        planted[name] = dict(mean_bits=float(b.mean()), power_at_n=hits / 500)
        print(f"  planted {name:28s} mean bits {b.mean():.3f}; detection rate at n={n}: {hits/500:.2f}")
    R["planted"] = planted
    # decomposition: how much of the excess is rare signs (unigram) vs unusual order (bigram gain)?
    cu = Counter(x for t in ntexts for x in t); tot = sum(cu.values()) + len(ntexts)
    def ubits(t):
        return -np.mean([np.log2((cu.get(x, 0) + 0.5) / (tot + 0.5 * len(cu))) for x in t] + [np.log2(len(ntexts) / tot)])
    def decomp(texts, label, bits):
        u = np.array([ubits(t) for t in texts]); g = u - np.asarray(bits)
        print(f"  decomposition {label:30s} unigram bits {u.mean():.3f}; bigram gain over unigram {g.mean():+.3f}")
        return dict(unigram=float(u.mean()), bigram_gain=float(g.mean()))
    rdi = [i for i, r in enumerate(foreign) if r["fmt"] == "round"]
    R["decomp"] = {"foreign_round": decomp([foreign[i]["seq"] for i in rdi], "foreign round", fb[rdi]),
                   "home_round": decomp([r["seq"] for r, z in zip(native, rd) if z], "home round", nb[rd]),
                   "home_square": decomp([r["seq"] for r, z in zip(native, sq) if z], "home square", nb[sq]),
                   "planted_shuffled": decomp(shuf, "planted shuffled order", [mtr.bits(t) for t in shuf])}
    # sensitivity: drop texts flagged as pseudo-script / motif marks in gulf_seals.csv and paragorth
    pseudo = {"W091 W032 W001 W033", "W091", "W740 W740"}
    keep = [i for i in rdi if " ".join(foreign[i]["seq"]) not in pseudo]
    R["foreign_round_no_pseudo"] = compare(fb[keep], [fl[i] for i in keep], nb, nl, "foreign round minus pseudo-script")
    R["foreign_texts"] = [dict(site=r["site"], fmt=r["fmt"], seq=" ".join(r["seq"]), bits=float(b)) for r, b in zip(foreign, fb)]

    # M77 replication
    T = m77_texts()
    seen, mn, mf = set(), [], []
    for t in T:
        s = clean(t["seq"])
        if not s: continue
        g = t["site"] == "West Asian finds"
        k = (g, " ".join(s))
        if k in seen: continue
        seen.add(k); (mf if g else mn).append(s)
    fk = {" ".join(s) for s in mf}
    mn = [s for s in mn if " ".join(s) not in fk]
    nbm = cv_bits(mn); nlm = np.array([len(s) for s in mn])
    mm = KN(mn)
    fbm = np.array([mm.bits(s) for s in mf])
    print(f"M77: native {len(mn)}, West Asian {len(mf)}")
    R["m77_west_asian"] = compare(fbm, [len(s) for s in mf], nbm, nlm, "M77 West Asian finds")
    save_json("q4_gulf", R)


if __name__ == "__main__":
    main()
