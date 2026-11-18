"""Rerun the nine headline tests (assumption_audit/sens.py approach: harness.py T1-T9, type unit, M77 sign
space, split v2, frozen bars) on the consensus / either-edition corpora and under structured noise at the
measured M77-ICIT disagreement rate. Pre-registered: docs/prereg/consensus_corpus.md.

Conditions
  corpora (out/corpora/<name>.json, built by corpora.py):
     base cons_sign_reg cons_sign_ext cons_text_ext icit_reg icit_ext match_m77 match_icit
  structured noise (error structure from out/error_model.json, scaled by f):
     struct100_s1..s10 (f=1.0, PRIMARY), struct50_s1..s5 (f=0.5), struct150_s1..s5 (f=1.5)
  uniform comparison: unif100_s1..s5 = sens.py noiseR at the same total sign rate (no structure)

    board/run.sh .venv/bin/python -I experiments/consensus_corpus/run.py            # all, resumable
Appends to out/runs.jsonl; skips conditions already there.
"""
import sys, json, random, time
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
sys.path.insert(0, str(ROOT / "experiments" / "assumption_audit"))
import harness as H  # noqa
import sens as S  # noqa  (seeded, draw_random, draw_look, perturb_seq: imported, not edited)
from corpus.load import dev_heldout, m77_texts  # noqa
from corpora import inverse, conc  # noqa

OUT = HERE / "out"
CORP = ["base", "cons_sign_reg", "cons_sign_ext", "cons_text_ext", "icit_reg", "icit_ext", "match_m77", "match_icit"]
K_SHRINK = 10


def conditions():
    c = list(CORP)
    c += [f"struct100_s{s}" for s in range(1, 11)]
    c += [f"struct50_s{s}" for s in range(1, 6)] + [f"struct150_s{s}" for s in range(1, 6)]
    c += [f"unif100_s{s}" for s in range(1, 6)]
    return c


# ------------------------------------------------------------------ structured noise model
def calibration():
    """c such that Noise(f=1) realises the measured total disagreement rate as edit distance / M77 tokens
    on the whole M77 corpus (seeds 0-1, bisection). Cached in out/noise_calib.json. Fixes an input, not an outcome."""
    fp = OUT / "noise_calib.json"
    if fp.exists():
        return json.load(open(fp))["c"]
    sys.path.insert(0, str(ROOT / "experiments" / "audit_followups"))
    import b_editor_agreement as B
    texts = m77_texts(); target = total_rate()

    def realised(c):
        N = Noise(1.0, c=c); tot = dis = 0
        for sd in (0, 1):
            for i, t in enumerate(texts):
                s = N.apply(t["seq"], random.Random(f"{sd}-{i}"))
                a = B.flat(t["seq"]); b = B.flat(s)
                dis += B.align([(x, frozenset([x])) for x in a], [(x, frozenset([x])) for x in b], B.eq)[0]; tot += len(a)
        return dis / tot
    lo, hi = 0.8, 2.0
    for _ in range(10):
        mid = (lo + hi) / 2
        if realised(mid) < target: lo = mid
        else: hi = mid
    c = (lo + hi) / 2
    json.dump(dict(c=c, target=target, realised=realised(c)), open(fp, "w"), indent=1)
    return c


class Noise:
    def __init__(self, f, c=None):
        em = json.load(open(OUT / "error_model.json"))
        f = f * (calibration() if c is None else c)
        self.f = f
        mp, dbl = conc()
        freq = Counter(s for t in m77_texts() for s in t["seq"] if s not in "|#")
        inv = inverse(mp, dbl, freq)
        nT = em["n_texts"]; tok = em["mean_len"] * nT
        r = em["rates"]
        self.p_rev = r["direction_texts"] * f
        pd, pi = em["pos_del"], em["pos_ins"]
        self.del_ = dict(initial=pd.get("initial", 0) / nT * f, final=pd.get("final", 0) / nT * f,
                         medial=pd.get("medial", 0) / max(tok - 2 * nT, 1) * f)
        self.ins = dict(initial=pi.get("initial", 0) / nT * f, final=pi.get("final", 0) / nT * f,
                        medial=pi.get("medial", 0) / max(tok - nT, 1) * f)
        self.p_tr = r["order"] * f
        pbar = r["identity"]
        self.sub_p = {}; self.sub_t = {}
        for m, n in em["n_by_m"].items():
            if "+" in m: continue
            s = sum(em["sub_by_m"].get(m, {}).values())
            self.sub_p[m] = (s + K_SHRINK * pbar) / (n + K_SHRINK)
        self.pbar = pbar
        for m, ws in em["sub_by_m"].items():
            if "+" in m: continue
            tg = Counter()
            for w, c in ws.items():
                tg[tuple(inv.get(w, [w]))] += c
            self.sub_t[m] = tg
        ins = Counter()
        for w, c in em["inserted_w"].items(): ins[tuple(inv.get(w, [w]))] += c
        self.ins_t = ins

    def psub(self, x):
        return min(0.9, self.sub_p.get(x, self.pbar) * self.f)

    def target(self, r, x):
        tg = self.sub_t.get(x)
        if tg:
            s = sum(tg.values())
            if r.random() < s / (s + 1):
                k = r.choices(list(tg), weights=list(tg.values()))[0]
                return list(k)
        return [S.draw_look(r, x)]

    def insert(self, r):
        if self.ins_t and r.random() < 0.5:
            return list(r.choices(list(self.ins_t), weights=list(self.ins_t.values()))[0])
        return [S.draw_random(r, None)]

    def apply(self, seq, r):
        flat_n = sum(s not in ("|", "#") for s in seq)
        out = []; fi = 0
        if flat_n and r.random() < self.ins["initial"]:
            out += self.insert(r)
        for s in seq:
            if s in ("|", "#"):
                out.append(s); continue
            pos = "initial" if fi == 0 else ("final" if fi == flat_n - 1 else "medial")
            fi += 1
            if r.random() < self.del_[pos]:
                continue
            if r.random() < self.psub(s):
                out += self.target(r, s)
            else:
                out.append(s)
            if fi < flat_n and r.random() < self.ins["medial"]:
                out += self.insert(r)
        if flat_n and r.random() < self.ins["final"]:
            out += self.insert(r)
        # adjacent transpositions inside break-free runs
        for i in range(len(out) - 1):
            if out[i] not in ("|", "#") and out[i + 1] not in ("|", "#") and r.random() < self.p_tr:
                out[i], out[i + 1] = out[i + 1], out[i]
        return out


def total_rate():
    em = json.load(open(OUT / "error_model.json"))
    r = em["rates"]
    return r["identity"] + r["m77_only"] + r["icit_only"] + r["order"]


# ------------------------------------------------------------------ build
def load_corpus(name):
    c = json.load(open(OUT / "corpora" / f"{name}.json"))
    return c["recs"], [(d, tuple(s)) for d, s in c["lines"]]


def build(cond):
    _, ho0 = dev_heldout(version=2)
    hk = {" ".join(t["seq"]) for t in ho0}
    if cond in CORP:
        recs, lines = load_corpus(cond)
    else:
        recs, lines = load_corpus("base")
        kind, seed = cond.rsplit("_s", 1); seed = int(seed)
        recs = [dict(r) for r in recs]
        if kind.startswith("struct"):
            N = Noise(int(kind[6:]) / 100)
            nl = []
            for i, r in enumerate(recs):
                rr = S.seeded("struct", kind, seed, r["key0"], i)
                rev = S.seeded("srev", kind, seed, r["key0"]).random() < N.p_rev
                s = N.apply(r["seq"], rr)
                r["seq"] = s[::-1] if rev else s
            for j, (d, sg) in enumerate(lines):
                rr = S.seeded("structL", kind, seed, j, sg)
                s = N.apply(list(sg), rr)
                if rr.random() < N.p_rev: s = s[::-1]
                if len(s) >= 2: nl.append((d, tuple(s)))
            lines = nl
        elif kind == "unif100":
            a = total_rate()
            for i, r in enumerate(recs):
                r["seq"] = S.perturb_seq(r["seq"], (r["key0"], i), "noiseR", a, seed, "text")
            lines = [(d, tuple(S.perturb_seq(list(sg), (j, sg), "noiseR", a, seed, "line"))) for j, (d, sg) in enumerate(lines)]
        else:
            raise ValueError(cond)
    for r in recs:
        r["split"] = "heldout" if r["key0"] in hk else "dev"
        r["seq"] = [x for x in r["seq"]]

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
    return dev, ho, lines, dict(n_dev=len(dev), n_ho=len(ho), n_lines=len(lines),
                                n_tokens=sum(x not in "|#" for r in recs for x in r["seq"]))


def run(cond):
    t0 = time.time()
    V = H.Variant("M77")
    dev, ho, lines, info = build(cond)
    rng = random.Random(7); nrng = np.random.default_rng(7)
    res = dict(cond=cond, **info)
    for k, fn in (("T1", lambda: H.t1_order(dev, ho)), ("T2", lambda: H.t2_tick(V, dev, ho, rng)),
                  ("T3", lambda: H.t3_sixfish(V, dev, ho)), ("T4", lambda: H.t4_registers(dev, ho, nrng)),
                  ("T5", lambda: H.t5_direction(lines, "type"))):
        try:
            res[k] = fn()
        except Exception as e:  # small corpora can make a test undefined; recorded as NT
            res[k] = dict(NT=f"error: {e!r}"[:200], survives=None)
    try:
        dev_g = [t for t in dev if t["site"] != "West Asian finds"]
        lex = H.build_lexicon_v(V, dev_g)
        G = H.fr.Grammar(lex, "final").fit(dev_g)
        sp = H.strip_pairs(V)
        occ_tr = H.cores_of(G, lex, dev, sp); occ_te = H.cores_of(G, lex, ho, sp)
        inc_tr, inc_te = H.incidence(occ_tr), H.incidence(occ_te)
        numerals = {s for s, e in lex.items() if e["roles"] & {"S", "T"} and e["source"] == "hand"}
        for k, fn in (("T6", lambda: H.t6_cores(inc_te)), ("T7", lambda: H.t7_pairorder(inc_tr, inc_te)),
                      ("T8", lambda: H.t8_fish(V, inc_tr, inc_te, occ_te, numerals, nrng)),
                      ("T9", lambda: H.t9_parse(G, ho, rng))):
            try:
                res[k] = fn()
            except Exception as e:
                res[k] = dict(NT=f"error: {e!r}"[:200], survives=None)
    except Exception as e:
        for k in ("T6", "T7", "T8", "T9"):
            res[k] = dict(NT=f"grammar error: {e!r}"[:200], survives=None)
    res["secs"] = round(time.time() - t0, 1)
    print(cond, {k: v.get("survives") for k, v in res.items() if isinstance(v, dict)}, f"{res['secs']}s", flush=True)
    return res


if __name__ == "__main__":
    f = OUT / "runs.jsonl"
    done = set()
    if f.exists():
        done = {json.loads(l)["cond"] for l in open(f) if l.strip()}
    todo = [c for c in (sys.argv[1:] or conditions()) if c not in done]
    for c in todo:
        r = run(c)
        with open(f, "a") as fh:
            fh.write(json.dumps(r, default=str) + "\n")
