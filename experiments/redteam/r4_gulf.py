"""Claim 4 (context): Gulf/West Asian round-seal texts are order-anomalous (+2.17 bits/sign).
Independent reimplementation. Attacks:
 A. Leakage asymmetry: context scores native texts by plain 10-fold CV, so a native text's
    near-duplicates (variant copies, re-attestations) sit in its training fold; foreign texts
    never have that advantage. Here every comparison group is scored by a model trained with
    its WHOLE SITE held out ("site-held-out"), exactly the situation of the foreign texts.
 B. Small peripheral native sites with equally small samples (n matched to 18) as comparators.
 C. Smoothing variants (KN d=0.5/0.75/0.9; rare signs (<3) collapsed to UNK; add-k bigram).
 D. Order test that is immune to rare-sign smoothing: per-text percentile of the real order
    among all permutations (within-text), under the native bigram.
 E. Reading direction: are foreign texts better explained reversed?
 F. Breaks: context joins across '#'. Here only break-free texts are used.
"""
import itertools, math, random
from collections import Counter, defaultdict
import numpy as np
from rt_common import icit, KN, Uni, save

rng = np.random.default_rng(7)
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar",
           "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Kalba",
           "Gonur Depe", "Altyn Depe", "Shortughai"}


def load():
    rows, seen = [], set()
    for t in icit():
        if "#" in t["seq"]:
            continue
        s = tuple(x for x in t["seq"] if x != "|")
        if not s: continue
        fmt = "round" if t["type"] in ("SEAL:R", "SEAL:C", "SEAL:CY") else "square" if t["type"].startswith("SEAL") else "other"
        k = (t["site"], s)
        if k in seen: continue
        seen.add(k)
        rows.append(dict(seq=s, site=t["site"], fmt=fmt, dir=t["direction"], type=t["type"]))
    return rows


class Model:
    def __init__(self, texts, kind="kn75"):
        self.kind = kind
        if kind.startswith("unk"):
            c = Counter(x for t in texts for x in t)
            self.keep = {x for x, n in c.items() if n >= 3}
            texts = [self.m(t) for t in texts]
        d = {"kn50": .5, "kn75": .75, "kn90": .9, "unk3": .75}.get(kind, .75)
        self.kn = KN(texts, d=d)
        self.uni = Uni(texts, alpha=0.5)
        if kind == "addk":
            self.big = defaultdict(Counter)
            for t in texts:
                p = "<s>"
                for x in list(t) + ["</s>"]:
                    self.big[p][x] += 1; p = x

    def m(self, t):
        return tuple(x if x in self.keep else "<unk>" for x in t) if hasattr(self, "keep") else t

    def bits(self, t):
        t = self.m(t)
        if self.kind == "addk":
            p, b = "<s>", 0
            for x in list(t) + ["</s>"]:
                c = self.big[p]; n = sum(c.values())
                pr = 0.5 * (c.get(x, 0) + 0.1) / (n + 0.1 * len(self.uni.V)) + 0.5 * self.uni.p(x)
                b -= math.log2(pr); p = x
            return b / (len(t) + 1)
        return self.kn.bits(t) / (len(t) + 1)

    def ubits(self, t):
        t = self.m(t)
        return self.uni.bits(t) / (len(t) + 1)


def perm_pct(model, t, maxperm=720):
    t = tuple(t)
    if len(t) < 2: return None
    perms = set(itertools.permutations(t)) if math.factorial(len(t)) <= maxperm else \
        {tuple(rng.permutation(t)) for _ in range(maxperm)} | {t}
    b0 = model.bits(t)
    others = [model.bits(p) for p in perms if p != t]
    if not others: return None
    return float(np.mean([b0 < b for b in others]) + 0.5 * np.mean([b0 == b for b in others]))


def group_scores(rows, held_sites, kind, native_pool):
    """Train on native_pool minus held_sites; score rows."""
    tr = [r["seq"] for r in native_pool if r["site"] not in held_sites]
    m = Model(tr, kind)
    out = []
    for r in rows:
        if len(r["seq"]) < 2: continue
        out.append(dict(L=len(r["seq"]), bits=m.bits(r["seq"]), gain=m.ubits(r["seq"]) - m.bits(r["seq"]),
                        rev_bits=m.bits(r["seq"][::-1]), pct=perm_pct(m, r["seq"]), site=r["site"]))
    return out


def summarise(sc):
    if not sc: return None
    a = lambda k: float(np.mean([x[k] for x in sc if x[k] is not None]))
    return dict(n=len(sc), mean_len=round(a("L"), 2), bits=round(a("bits"), 3), bigram_gain=round(a("gain"), 3),
                reversed_minus_real=round(a("rev_bits") - a("bits"), 3), perm_pct=round(a("pct"), 3),
                best_order_share=round(float(np.mean([x["pct"] == 1.0 for x in sc if x["pct"] is not None])), 3))


def main():
    rows = load()
    native = [r for r in rows if r["site"] not in FOREIGN and r["site"] != "Unknown"]
    foreign_round = [r for r in rows if r["site"] in FOREIGN and r["fmt"] == "round"]
    foreign_sq = [r for r in rows if r["site"] in FOREIGN and r["fmt"] != "round"]
    print("foreign round", len(foreign_round), Counter(r["dir"] for r in foreign_round))
    res = {"n_native": len(native), "foreign_round_directions": Counter(r["dir"] for r in foreign_round)}
    small_sites = [s for s, n in Counter(r["site"] for r in native).items() if n >= 8 and s not in ("Harappa", "Mohenjo-daro")]
    for kind in ("kn75", "kn50", "kn90", "unk3", "addk"):
        R = {}
        R["foreign_round"] = summarise(group_scores(foreign_round, set(), kind, native))
        R["foreign_square_other"] = summarise(group_scores(foreign_sq, set(), kind, native))
        # peripheral native sites, each scored with its whole site held out; seals only, len>=2
        per = {}
        for s in small_sites:
            g = [r for r in native if r["site"] == s and r["fmt"] in ("round", "square")]
            if len([r for r in g if len(r["seq"]) >= 2]) >= 6:
                per[s] = summarise(group_scores(g, {s}, kind, native))
        R["native_sites_site_heldout_seals"] = per
        # home round seals at MD/Harappa, scored with their site held out (strict) -- n
        for s in ("Mohenjo-daro", "Harappa"):
            g = [r for r in native if r["site"] == s and r["fmt"] == "round"]
            R[f"home_round_{s}_site_heldout"] = summarise(group_scores(g, {s}, kind, native))
        res[kind] = R
        print(kind, R["foreign_round"], R["foreign_square_other"])
        for s, v in sorted(per.items(), key=lambda x: -x[1]["bits"]):
            print("   ", s, v)
        print("   home round MD", R["home_round_Mohenjo-daro_site_heldout"], "\n   home round H", R["home_round_Harappa_site_heldout"])
        if kind != "kn75":
            continue
        # B. matched-n resampling: 18 seals from one peripheral site at a time, length-matched to foreign
        flen = [len(r["seq"]) for r in foreign_round if len(r["seq"]) >= 2]
        dist = {}
        for s in small_sites:
            g = [r for r in native if r["site"] == s and r["fmt"] in ("round", "square") and len(r["seq"]) >= 2]
            if len(g) < 12: continue
            sc = group_scores(g, {s}, kind, native)
            bylen = defaultdict(list)
            for x in sc: bylen[min(x["L"], 6)].append(x)
            draws = []
            for _ in range(500):
                pick = [bylen[min(L, 6)][rng.integers(len(bylen[min(L, 6)]))] if bylen.get(min(L, 6)) else sc[rng.integers(len(sc))] for L in flen]
                draws.append((np.mean([x["bits"] for x in pick]), np.mean([x["gain"] for x in pick]), np.mean([x["pct"] for x in pick])))
            d = np.array(draws)
            dist[s] = dict(n_site=len(g), bits_mean=round(d[:, 0].mean(), 3), bits_95=round(np.quantile(d[:, 0], .95), 3),
                           gain_mean=round(d[:, 1].mean(), 3), gain_5=round(np.quantile(d[:, 1], .05), 3),
                           pct_mean=round(d[:, 2].mean(), 3), pct_5=round(np.quantile(d[:, 2], .05), 3))
        res["matched_n_peripheral"] = dist
        for s, v in dist.items(): print("  matched", s, v)
        # per-text listing for foreign round
        tr = Model([r["seq"] for r in native], kind)
        res["foreign_round_texts"] = [dict(site=r["site"], dir=r["dir"], seq=" ".join(r["seq"]),
                                           bits=round(tr.bits(r["seq"]), 2), rev=round(tr.bits(r["seq"][::-1]), 2),
                                           pct=perm_pct(tr, r["seq"])) for r in foreign_round]
        for x in res["foreign_round_texts"]: print("   ", x)
    save("r4_gulf", res)


main()
