"""Red team #38, part C3/D: rerun #3 (harness T2), #7 (T5), #10b (T7) on my own consensus corpora and under three
noise structures N3 did not try (rare-sign, clustered-by-text, site-weighted). Frozen bars from harness.py.
Pre-registered: docs/prereg/redteam_consensus.md.

    board/run.sh .venv/bin/python -I experiments/redteam_consensus/tests.py        # resumable (out/tests.jsonl)
"""
import sys, json, random, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
sys.path.insert(0, str(ROOT / "experiments" / "assumption_audit"))
import harness as H  # noqa
import sens as S  # noqa  (draw_look, draw_random, seeded)
from corpus.load import dev_heldout, m77_texts, m77_lines, icit_texts  # noqa
from measure import pairs_all, n3_map, tokens, nw, flat  # noqa

OUT = HERE / "out"
DIRM = {"right-to-left": "rl", "left-to-right": "lr"}
DIRI = {"R/L": "rl", "L/R": "lr", "R/l": "rl"}
MIX = dict(sub=0.073, dele=0.040, ins=0.010, swap=0.006)   # measured per-token mix (N3 primary), total 12.9%
TEXT_SHARE = 0.345                                         # measured share of texts with any difference


# ------------------------------------------------------------------ links and masking (own aligner)
def links():
    mp, dbl, _ = n3_map()
    icit = {t["id"]: t for t in icit_texts()}
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    reg = {(mt["text_no"], mt["side"]): it for p, mt, it in pairs_all() if p["norm"] <= 0.8}
    seq = {tuple(json.loads(k)): icit[v["icit"]] for k, v in
           json.load(open(ROOT / "experiments/consensus_corpus/out/seq_links.json")).items()}
    return mp, dbl, m77, reg, seq


def masked(mt, it, mp, dbl):
    a, b = tokens(mt["seq"], it["seq"], mp, dbl, "cond")
    ops = nw(a, b, swap=None)                                # v1: unit Levenshtein, no swap
    bad = set(); before = set()
    for k, ia, ib in ops:
        if k in ("sub", "m_extra"): bad.add(ia)
        elif k == "i_extra": before.add(ia)
    # token index -> flat positions
    pos, j = [], 0
    for t in a:
        pos.append(list(range(j, j + t[2]))); j += t[2]
    badf = {x for i in bad for x in pos[i]}
    bef = {pos[i][0] if i < len(pos) else j for i in before}
    out, f = [], 0
    for s in mt["seq"]:
        if s in ("|", "#"): out.append(s); continue
        if f in bef: out.append("#")
        out.append("#" if f in badf else s); f += 1
    if j in bef: out.append("#")
    clean = []
    for s in out:
        if s == "#" and clean and clean[-1] == "#": continue
        clean.append(s)
    return clean, bool(badf or bef), ops, a


def lines_by():
    L = defaultdict(list)
    for l in m77_lines():
        d = DIRM.get(l["direction"])
        if d:
            for sg in l["segments"]:
                if len(sg) >= 2: L[(l["text_no"], l["side"])].append((d, tuple(sg)))
    return L


def split_lines(d, seq):
    out, cur = [], []
    for s in list(seq) + ["#"]:
        if s in ("|", "#"):
            if len(cur) >= 2: out.append((d, tuple(cur)))
            cur = []
        else: cur.append(s)
    return out


# ------------------------------------------------------------------ corpora
def rec(t, seq):
    return dict(seq=list(seq), object_type=t["object_type"], site=t["site"], complete=t["complete"],
                key0=" ".join(t["seq"]), tk=(t["text_no"], t["side"]))


def corpus(name):
    mp, dbl, m77, reg, seq = links()
    LB = lines_by()
    T = m77_texts()
    allL = [x for t in T for x in LB.get((t["text_no"], t["side"]), [])]
    rl_base = [x for x in allL if x[0] == "rl"]
    if name == "base":
        return [rec(t, t["seq"]) for t in T], allL
    if name in ("D1", "D2"):
        L = {**seq, **reg} if name == "D1" else reg
        recs, lines = [], []
        for t in T:
            k = (t["text_no"], t["side"])
            if k in L:
                s, bad, _, _ = masked(t, L[k], mp, dbl); recs.append(rec(t, s))
                same_dir = {d for d, _ in LB.get(k, [])} == {DIRI.get(L[k]["direction"])}
                if same_dir and not bad: lines += LB.get(k, [])
            elif name == "D2":
                recs.append(rec(t, t["seq"])); lines += LB.get(k, [])
        return recs, lines
    if name in ("C3_linked", "C3_unlinked"):
        L = {**seq, **reg}
        keep = (lambda k: k in L) if name == "C3_linked" else (lambda k: k not in L)
        ks = [t for t in T if keep((t["text_no"], t["side"]))]
        return [rec(t, t["seq"]) for t in ks], [x for t in ks for x in LB.get((t["text_no"], t["side"]), [])]
    if name in ("D3a", "D3b"):
        # #7 only: R-L training lines = all M77 R-L lines; L-R test lines from linked objects
        L = {**seq, **reg}
        lr = []
        inv = defaultdict(Counter)
        for m, ws in mp.items():
            for w in ws: inv[w][m] += 1
        freq = Counter(s for t in T for s in flat(t["seq"]))
        invb = {w: max(c, key=lambda m: freq[m]) for w, c in inv.items()}
        for t in T:
            k = (t["text_no"], t["side"])
            if k not in L: continue
            it = L[k]; di = DIRI.get(it["direction"])
            if name == "D3a":
                dm = {d for d, _ in LB.get(k, [])}
                if dm == {"lr"} and di == "lr":
                    s, bad, _, _ = masked(t, it, mp, dbl)
                    lr += split_lines("lr", s)
            else:
                if di == "lr":
                    for sg in it["segments"]:
                        if len(sg) >= 2: lr.append(("lr", tuple(invb.get(w, w) for w in sg)))
        return [rec(t, t["seq"]) for t in T], rl_base + lr
    raise ValueError(name)


# ------------------------------------------------------------------ noise (own generator)
class Noise:
    def __init__(self, kind, f):
        T = m77_texts()
        self.kind, self.f = kind, f
        freq = Counter(s for t in T for s in flat(t["seq"]))
        ntok = sum(freq.values())
        if kind == "rare":
            raw = {s: c ** -0.5 for s, c in freq.items()}
            z = sum(raw[s] * c for s, c in freq.items()) / ntok
            self.msign = {s: v / z for s, v in raw.items()}
        if kind == "site":
            meas = json.load(open(OUT / "measure.json"))["B_sensitivity"]["v6_strata"]
            mean = 0.129
            sr = {k[5:]: v["rate"] / mean for k, v in meas.items() if k.startswith("site:")}
            w = Counter();
            for t in T: w[t["site"]] += len(flat(t["seq"]))
            raw = {s: sr.get(s, 1.0) for s in w}
            z = sum(raw[s] * w[s] for s in w) / sum(w.values())
            self.msite = {s: v / z for s, v in raw.items()}

    def text_mult(self, key, site, seed):
        if self.kind == "text":
            return (1 / TEXT_SHARE) if S.seeded("rt-text", seed, key).random() < TEXT_SHARE else 0.0
        if self.kind == "site":
            return self.msite.get(site, 1.0)
        return 1.0

    def apply(self, seq, tm, r):
        out = []
        n = sum(s not in ("|", "#") for s in seq)
        for s in seq:
            if s in ("|", "#"): out.append(s); continue
            m = tm * self.f * (self.msign.get(s, 1.0) if self.kind == "rare" else 1.0)
            u = r.random()
            pd, ps, pi = min(.9, MIX["dele"] * m), min(.9, MIX["sub"] * m), min(.9, MIX["ins"] * m)
            if u < pd: continue
            if u < pd + ps: out.append(S.draw_look(r, s))
            else: out.append(s)
            if r.random() < pi: out.append(S.draw_random(r, None))
        for i in range(len(out) - 1):
            if out[i] not in ("|", "#") and out[i + 1] not in ("|", "#") and r.random() < MIX["swap"] * tm * self.f:
                out[i], out[i + 1] = out[i + 1], out[i]
        return out


def noisy(cond):
    kind, f, seed = cond.split("_")
    f = int(f) / 100; seed = int(seed[1:])
    N = Noise(kind, f)
    recs, lines = corpus("base")
    LB = lines_by()
    out = []
    for i, r in enumerate(recs):
        tm = N.text_mult(r["tk"], r["site"], seed)
        r = dict(r); r["seq"] = N.apply(r["seq"], tm, S.seeded("rt", cond, i)); out.append(r)
    nl = []
    T = m77_texts()
    for t in T:
        k = (t["text_no"], t["side"]); tm = N.text_mult(k, t["site"], seed)
        for j, (d, sg) in enumerate(LB.get(k, [])):
            s = N.apply(list(sg), tm, S.seeded("rtL", cond, k, j))
            if len(s) >= 2: nl.append((d, tuple(s)))
    return out, nl


def realised_rate(cond):
    """edit distance per original token, as a check of the noise level"""
    recs0, _ = corpus("base"); recs, _ = noisy(cond)
    d = n = 0
    for a, b in zip(recs0, recs):
        A, Bb = flat(a["seq"]), flat(b["seq"])
        aa = [(x, frozenset([x]), 1) for x in A]
        ops = nw(aa, Bb)
        d += sum(o[0] in ("sub", "m_extra", "i_extra", "swap") for o in ops); n += len(A)
    return d / n


# ------------------------------------------------------------------ run
def build(recs):
    _, ho0 = dev_heldout(version=2)
    hk = {" ".join(t["seq"]) for t in ho0}
    for r in recs: r["split"] = "heldout" if r["key0"] in hk else "dev"
    def dist(rs):
        seen, out = set(), []
        for r in rs:
            k = tuple(r["seq"])
            if k and k not in seen and any(x not in "|#" for x in k):
                seen.add(k); out.append(r)
        return out
    dev = dist([r for r in recs if r["split"] == "dev"])
    dk = {tuple(r["seq"]) for r in dev}
    ho = [r for r in dist([r for r in recs if r["split"] == "heldout"]) if tuple(r["seq"]) not in dk]
    return dev, ho


def run(cond):
    t0 = time.time()
    recs, lines = noisy(cond) if cond.split("_")[0] in ("rare", "text", "site") else corpus(cond)
    dev, ho = build(recs)
    V = H.Variant("M77"); rng = random.Random(7)
    res = dict(cond=cond, n_dev=len(dev), n_ho=len(ho), n_lines=len(lines))
    try: res["T2_#3"] = H.t2_tick(V, dev, ho, rng)
    except Exception as e: res["T2_#3"] = dict(NT=repr(e)[:150], survives=None)
    try: res["T5_#7"] = H.t5_direction(lines, "type")
    except Exception as e: res["T5_#7"] = dict(NT=repr(e)[:150], survives=None)
    if not cond.startswith("D3"):
        try:
            dev_g = [t for t in dev if t["site"] != "West Asian finds"]
            lex = H.build_lexicon_v(V, dev_g)
            G = H.fr.Grammar(lex, "final").fit(dev_g)
            sp = H.strip_pairs(V)
            res["T7_#10b"] = H.t7_pairorder(H.incidence(H.cores_of(G, lex, dev, sp)), H.incidence(H.cores_of(G, lex, ho, sp)))
        except Exception as e:
            res["T7_#10b"] = dict(NT=repr(e)[:150], survives=None)
    res["secs"] = round(time.time() - t0, 1)
    print(cond, {k: (v.get("survives"), v.get("share"), v.get("p")) for k, v in res.items() if isinstance(v, dict)}, res["secs"], flush=True)
    return res


def conditions():
    c = ["base", "D1", "D2", "D3a", "D3b", "C3_linked", "C3_unlinked"]
    for kind in ("rare", "text", "site"):
        for f in (100, 150):
            c += [f"{kind}_{f}_s{s}" for s in range(1, 6)]
    return c


if __name__ == "__main__":
    fp = OUT / "tests.jsonl"
    done = {json.loads(l)["cond"] for l in open(fp)} if fp.exists() else set()
    if "--rates" in sys.argv:
        rr = {c: round(realised_rate(c), 4) for c in ("rare_100_s1", "text_100_s1", "site_100_s1", "rare_150_s1")}
        json.dump(rr, open(OUT / "noise_rates.json", "w"), indent=1); print(rr); sys.exit()
    for c in [c for c in conditions() if c not in done]:
        r = run(c)
        with open(fp, "a") as fh: fh.write(json.dumps(r, default=str) + "\n")
