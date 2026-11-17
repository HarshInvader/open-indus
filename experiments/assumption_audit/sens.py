"""Assumption-audit sensitivity checks (pre-registered: docs/prereg/assumption_audit.md).

Re-runs the nine headline tests of experiments/signlist_robustness/harness.py (T1-T9, type unit,
Mahadevan M77 sign list, split v2) on deliberately damaged copies of the corpus:

  base                 no perturbation (reproduces harness M77/type)
  rev10/rev25/rev50_sK reading direction flipped for 10/25/50% of objects (whole object reversed)
  lineshuf_sK          line order shuffled inside every multi-line object
  noiseR{2,5,10}_sK    p% of sign tokens replaced by a random sign drawn by corpus frequency
  noiseV{2,5,10}_sK    p% of sign tokens replaced by a look-alike (same img_mid drawing cluster),
                       falling back to random when the sign has no look-alike
  dedup                texts of >=3 signs: held-out restricted to texts more than 1 edit (3 signs) or
                       2 edits (>=4 signs) from every dev text, one per held-out family; dev collapsed
                       to one text per family by the same rule
  nodoubt              every object with a sign Mahadevan marked doubtful removed (dev and held-out)

Perturbations are applied to dev and held-out alike (a wrong assumption would affect the whole corpus);
held-out membership is fixed from the unperturbed text, so the split itself never changes.

    board/run.sh .venv/bin/python -I experiments/assumption_audit/sens.py            # all conditions
    board/run.sh .venv/bin/python -I experiments/assumption_audit/sens.py base rev50_s1

Appends one JSON line per condition to out/runs.jsonl and skips conditions already there (resumable).
"""
import sys, json, random, time, hashlib
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness as H  # noqa: E402
from corpus.load import m77_texts, m77_lines, dev_heldout  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
SEEDS = (1, 2, 3)


def conditions():
    c = ["base", "dedup", "nodoubt"]
    for s in SEEDS:
        c += [f"rev10_s{s}", f"rev25_s{s}", f"rev50_s{s}", f"lineshuf_s{s}"]
        c += [f"noiseR{p}_s{s}" for p in (2, 5, 10)]
        c += [f"noiseV{p}_s{s}" for p in (2, 5, 10)]
    return c


def seeded(*key):
    return random.Random(int(hashlib.sha256(repr(key).encode()).hexdigest()[:12], 16))


# ------------------------------------------------------------------ look-alike table (img_mid clusters)
def lookalikes():
    part = H.VJ["partitions"]["img_mid"]
    grp = defaultdict(list)
    for m, l in part.items():
        grp[l].append(m)
    return {m: [x for x in grp[l] if x != m] for m, l in part.items()}


LOOK = lookalikes()
UNI = Counter(s for t in m77_texts() for s in t["seq"] if s not in "|#")
UNI_S, UNI_W = list(UNI), np.array(list(UNI.values()), float)
UNI_W /= UNI_W.sum()


def draw_random(r, avoid):
    while True:
        x = UNI_S[int(np.searchsorted(np.cumsum(UNI_W), r.random()))]
        if x != avoid:
            return x


def draw_look(r, s):
    cand = LOOK.get(s, [])
    if not cand:
        return draw_random(r, s)
    w = [UNI[c] + 1 for c in cand]
    return r.choices(cand, weights=w)[0]


# ------------------------------------------------------------------ perturbations
def parse(cond):
    if cond in ("base", "dedup", "nodoubt"):
        return cond, None, 0
    kind, s = cond.rsplit("_s", 1)
    s = int(s)
    if kind.startswith("rev"):
        return "rev", int(kind[3:]) / 100, s
    if kind == "lineshuf":
        return "lineshuf", None, s
    if kind.startswith("noiseR"):
        return "noiseR", int(kind[6:]) / 100, s
    if kind.startswith("noiseV"):
        return "noiseV", int(kind[6:]) / 100, s
    raise ValueError(cond)


def reversed_obj(key, frac, seed):
    return seeded("rev", seed, key).random() < frac


def perturb_seq(seq, key, kind, a, seed, scope):
    seq = list(seq)
    if kind == "rev":
        return seq[::-1] if reversed_obj(key, a, seed) else seq
    if kind == "lineshuf":
        if scope == "line":
            return seq
        parts, cur = [], []
        for x in seq:
            if x == "|":
                parts.append(cur); cur = []
            else:
                cur.append(x)
        parts.append(cur)
        if len(parts) < 2:
            return seq
        seeded("ls", seed, key).shuffle(parts)
        out = []
        for i, p in enumerate(parts):
            if i: out.append("|")
            out += p
        return out
    if kind in ("noiseR", "noiseV"):
        r = seeded("noise", kind, seed, scope, key)
        out = []
        for x in seq:
            if x not in "|#" and r.random() < a:
                x = draw_random(r, x) if kind == "noiseR" else draw_look(r, x)
            out.append(x)
        return out
    return seq


def edit_le(a, b, k):
    """Levenshtein(a, b) <= k (banded)."""
    if abs(len(a) - len(b)) > k:
        return False
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        lo = max(1, i - k); hi = min(len(b), i + k)
        for j in range(1, len(b) + 1):
            if j < lo or j > hi:
                cur[j] = k + 1; continue
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        if min(cur) > k:
            return False
        prev = cur
    return prev[-1] <= k


def tol(f):
    return 2 if len(f) >= 4 else 1


def build(cond):
    kind, a, seed = parse(cond)
    V = H.Variant("M77")
    dev0, ho0 = dev_heldout(version=2)
    hk = {" ".join(t["seq"]) for t in ho0}
    lines_raw = m77_lines()
    doubt = {(l["text_no"], l["side"]) for l in lines_raw if l["doubtful"]}
    recs = []
    for t in m77_texts():
        key = (t["text_no"], t["side"])
        if kind == "nodoubt" and key in doubt:
            continue
        seq = perturb_seq(t["seq"], key, kind, a, seed, "text")
        recs.append(dict(seq=seq, object_type=t["object_type"], site=t["site"], complete=t["complete"],
                         split="heldout" if " ".join(t["seq"]) in hk else "dev"))
    dev_tok = [r for r in recs if r["split"] == "dev"]
    ho_tok = [r for r in recs if r["split"] == "heldout"]

    def dist(rs):
        seen, out = set(), []
        for r in rs:
            k = tuple(r["seq"])
            if k not in seen:
                seen.add(k); out.append(r)
        return out
    dev_type = dist(dev_tok)
    dk = {tuple(r["seq"]) for r in dev_type}
    ho_type = [r for r in dist(ho_tok) if tuple(r["seq"]) not in dk]
    info = dict(n_dev=len(dev_type), n_ho=len(ho_type))
    if kind == "dedup":
        flat = lambda r: tuple(s for s in r["seq"] if s not in "|#")
        # greedy family collapse: a text of length >= 3 is dropped if it is within tol() edits of a text
        # already kept (dev) or of any dev text / kept held-out text (held-out). Texts of 1-2 signs are
        # never treated as near-copies (any two short texts are within 1-2 edits).
        def collapse(rs, ref_bylen):
            kept_bylen = defaultdict(list); out = []
            for r in sorted(rs, key=lambda r: " ".join(r["seq"])):
                f = flat(r)
                if not f: continue
                if len(f) >= 3:
                    k = tol(f)
                    near = lambda B: any(edit_le(f, g, k) for L in range(len(f) - k, len(f) + k + 1) for g in B.get(L, []))
                    if near(kept_bylen) or (ref_bylen is not None and near(ref_bylen)):
                        continue
                kept_bylen[len(f)].append(f); out.append(r)
            return out
        dev_bylen = defaultdict(list)
        for r in dev_type:
            dev_bylen[len(flat(r))].append(flat(r))
        dev2 = collapse(dev_type, None)
        ho2 = collapse(ho_type, dev_bylen)
        info.update(n_dev_dedup=len(dev2), n_ho_dedup=len(ho2))
        dev_type, ho_type = dev2, ho2
    # direction lines (T5)
    lines = []
    for l in lines_raw:
        d = {"right-to-left": "rl", "left-to-right": "lr"}.get(l["direction"])
        if not d:
            continue
        key = (l["text_no"], l["side"])
        if kind == "nodoubt" and key in doubt:
            continue
        for seg in l["segments"]:
            if len(seg) >= 2:
                s2 = perturb_seq(seg, key + (l["line"], tuple(seg)), kind, a, seed, "line") if kind.startswith("noise") \
                    else perturb_seq(seg, key, kind, a, seed, "line")
                lines.append((d, tuple(V.tok(s) for s in s2)))
    return V, dev_type, ho_type, lines, info


def run(cond):
    t0 = time.time()
    V, dev, ho, lines, info = build(cond)
    rng = random.Random(7); nrng = np.random.default_rng(7)
    res = dict(cond=cond, **info)
    res["T1"] = H.t1_order(dev, ho)
    res["T2"] = H.t2_tick(V, dev, ho, rng)
    res["T3"] = H.t3_sixfish(V, dev, ho)
    res["T4"] = H.t4_registers(dev, ho, nrng)
    res["T5"] = H.t5_direction(lines, "type")
    dev_g = [t for t in dev if t["site"] != "West Asian finds"]
    lex = H.build_lexicon_v(V, dev_g)
    G = H.fr.Grammar(lex, "final").fit(dev_g)
    sp = H.strip_pairs(V)
    occ_tr = H.cores_of(G, lex, dev, sp); occ_te = H.cores_of(G, lex, ho, sp)
    inc_tr, inc_te = H.incidence(occ_tr), H.incidence(occ_te)
    numerals = {s for s, e in lex.items() if e["roles"] & {"S", "T"} and e["source"] == "hand"}
    res["T6"] = H.t6_cores(inc_te)
    res["T7"] = H.t7_pairorder(inc_tr, inc_te)
    res["T8"] = H.t8_fish(V, inc_tr, inc_te, occ_te, numerals, nrng)
    res["T9"] = H.t9_parse(G, ho, rng)
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
