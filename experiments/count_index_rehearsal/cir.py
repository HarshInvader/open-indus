"""Count-likeness index rehearsal (plan 10, Route 1, step 1). Prereg: docs/prereg/count_index_rehearsal.md.

Usage (from repo root, through the compute gate):
  board/run.sh .venv/bin/python -I experiments/count_index_rehearsal/cir.py extract   # counts only, no index
  board/run.sh .venv/bin/python -I experiments/count_index_rehearsal/cir.py dedupcheck
  board/run.sh .venv/bin/python -I experiments/count_index_rehearsal/cir.py score

Index (frozen): for one head, the expected number of distinct numeral values in a random sub-sample of M = 4 of its
tokens drawn without replacement (rarefaction). Range 1 (one value) .. 4. Heads need >= 8 tokens.
No index is ever computed for a real Indus head: Indus data supplies only head sizes, stroke system and the pooled
numeral value distribution for the planted gate.
"""
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "corpus"))
sys.path.insert(0, str(ROOT / "experiments" / "fish_tick_closer_v2"))
sys.path.insert(0, str(ROOT / "experiments" / "protocuneiform"))
import load as L  # noqa: E402
import dedup  # noqa: E402  (non-chaining greedy; we reuse its near() and MIN_DROP)
from pc_classes import pc_class, COMMODITY  # noqa: E402

# ---------------- frozen parameters ----------------
M_RARE = 4          # rarefaction sample size
NMIN = 8            # minimum tokens per head
NMAX = 30           # per-draw cap per head
TARGET = 700        # tokens per draw
STRICT = 349        # secondary cut: real Indus dev size after greedy dedup (20 heads)
DRAWS = 1000
NPERM = 999
ALPHA = 0.05
TAU = 2.0           # head-level call: counted if index >= TAU
SEED = 20261121
PLANT_COUNTED_SHARE = 0.30
PLANT_FROZEN_SHARE = 0.70   # frozen planted head: fixed value on 70% of tokens, count draws on 30%


# ---------------- index ----------------
def rarefied_distinct(values, m=M_RARE):
    n = len(values)
    if n < m:
        return float("nan")
    tot = comb(n, m)
    return float(sum(1 - comb(n - k, m) / tot for k in Counter(values).values()))


# ---------------- de-duplication (exact equivalent of dedup.greedy, indexed for speed) ----------------
def _signs(t):
    return [s for s in t["seq"] if s not in ("|", "#")]


def greedy_fast(texts):
    """Same output as dedup.greedy: distinct by full seq, drop empty, longest first (ties lexicographic),
    drop a text of >= MIN_DROP signs that is within one edit of / contiguous in an already kept text.
    Candidate kept texts are found through a bigram index: if near(sg, k) holds then k contains the whole first
    half sg[:h] or the whole second half sg[h:] (h = len//2 >= 2), hence every bigram of that half; we take the
    rarest bigram of each half. Equivalence with dedup.greedy is checked by `dedupcheck`."""
    T = L.distinct(texts)
    T = [t for t in T if _signs(t)]
    T.sort(key=lambda t: (-len(_signs(t)), " ".join(t["seq"])))
    kept, ks, seen = [], [], set()
    idx = defaultdict(list)
    for t in T:
        sg = _signs(t)
        key = " ".join(sg)
        if key in seen:
            continue
        hit = False
        if len(sg) >= dedup.MIN_DROP:
            h = len(sg) // 2
            cands = set()
            for a, b in ((0, h), (h, len(sg))):
                bgs = [(sg[i], sg[i + 1]) for i in range(a, b - 1)]
                best = min(bgs, key=lambda g: len(idx.get(g, ())))
                cands.update(idx.get(best, ()))
            for j in sorted(cands):
                if dedup.near(sg, ks[j]):
                    hit = True
                    break
        seen.add(key)
        if hit:
            continue
        j = len(kept)
        kept.append(t); ks.append(sg)
        for g in set(zip(sg, sg[1:])):
            idx[g].append(j)
    return sorted(kept, key=lambda t: " ".join(t["seq"]))


# ---------------- proto-cuneiform / proto-Elamite ----------------
NUMRE = re.compile(r"^(\d+|n|N)\((N\d+[^)]*)\)$")


def _base(s):
    return re.sub(r"(~.*|@.*)$", "", s)


def cdli_texts(path):
    lines = json.load(open(path))
    by = defaultdict(list)
    for r in lines:
        by[r["pid"]].append(r)
    texts = []
    for pid, rs in by.items():
        rs.sort(key=lambda r: r["k"])
        seq, lns = [], []
        for r in rs:
            toks = [t for t in r["tokens"] if t != ","]
            if seq:
                seq.append("|")
            seq.extend(toks)
            lns.append(toks)
        texts.append(dict(pid=pid, seq=seq, lines=lns))
    return texts


def cdli_pairs(texts):
    """Per line: each maximal numeral group; head = first non-numeral sign directly after the group in the line,
    else the non-numeral sign directly before it. Value = the group as written (canonical string). Head key = base
    sign name (variant ~x and @x stripped)."""
    out = []
    for t in texts:
        for toks in t["lines"]:
            i, n = 0, len(toks)
            while i < n:
                if not NUMRE.match(toks[i]):
                    i += 1; continue
                j = i
                while j < n and NUMRE.match(toks[j]):
                    j += 1
                val = " ".join(toks[i:j])
                head = toks[j] if j < n else (toks[i - 1] if i > 0 else None)
                if head is not None:
                    out.append(dict(head=_base(head), value=val, text=t["pid"]))
                i = j
    return out


def pc_label(head):
    c = pc_class(head)
    if c == "UNKNOWN":
        return None
    return 1 if c in COMMODITY else 0


# ---------------- Latin (EDH) ----------------
ROMAN = re.compile(r"^[IVXLCDM]+$")
RV = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
COUNT_FORMS = {
    "annus": "annis annos anno annorum annum annus ann",
    "mensis": "mensibus menses mense mensis mensem mens",
    "dies": "diebus dies die diem",
    "hora": "horis horas hora horae",
    "stipendium": "stipendiorum stipendia stipendiis stipendis stipendio stip",
    "pes": "pedes pedum pedibus pede ped",
    "passus": "passuum passus",
    "sestertius": "sestertium sestertios sestertiis sestertia sestertiorum sesterti sestertius hs",
    "denarius": "denarios denarii denariis denarium denariorum denarius",
    "libra": "libras librae libris libram libra pondo",
    "modius": "modios modii modiis modium modius",
}
FORM2COUNT = {f: lem for lem, fs in COUNT_FORMS.items() for f in fs.split()}
UNIT_PREV = {**{f: "leg" for f in "legio legionis legioni legionem legiones legionum leg".split()},
             **{f: "coh" for f in "cohors cohortis cohorti cohortem coh".split()},
             **{f: "ala" for f in "ala alae alam".split()}}
VIR = re.compile(r"^([IVX]+)vir[a-z]*$")
# unit epithet must be >= 4 letters, not a count form, not in this function/formula-word stoplist (fixed before scoring)
EPI_STOP = set("""et hic haec ex qui quae quod in ad cum sub de item vixit vix militavit mil miles milit centurio
signifer sibi posuit fecit votum votis libens lubens merito filius filia annorum annis natione domo eques equites
optio tesserarius beneficiarius veteranus veterani missicius dis manibus""".split())


def roman(s):
    v = [RV[c] for c in s]
    return sum(-a if i + 1 < len(v) and a < v[i + 1] else a for i, a in enumerate(v))


def _clean(w):
    return w.replace("(", "").replace(")", "")


def edh_texts():
    texts = []
    for f in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        for it in json.load(open(f))["items"]:
            tr = it.get("transcription") or ""
            if (it.get("language") or "L") != "L":
                continue
            toks = [_clean(w) for w in tr.split() if w != "/"]
            toks = [w for w in toks if w]
            if toks:
                texts.append(dict(pid=it["id"], seq=toks))
    return texts


def _ok(w):
    return not any(c in w for c in "[]?{}<>+")


def edh_pairs(texts):
    """Frozen rule (prereg section 3c). Tokens with editorial restoration/uncertainty marks are skipped."""
    out = []
    for t in texts:
        s = t["seq"]
        for i, w in enumerate(s):
            if not _ok(w):
                continue
            m = VIR.match(w)
            if m:
                out.append(dict(head="vir", value=roman(m.group(1)), text=t["pid"], label=0)); continue
            if not ROMAN.match(w):
                continue
            val = roman(w)
            prev = s[i - 1] if i > 0 else None
            nxt = s[i + 1] if i + 1 < len(s) else None
            pl = prev.lower() if prev and _ok(prev) else None
            nl = nxt.lower() if nxt and _ok(nxt) else None
            if pl in FORM2COUNT:
                out.append(dict(head=FORM2COUNT[pl], value=val, text=t["pid"], label=1))
            elif (pl in UNIT_PREV and nl and re.fullmatch(r"[a-z]+", nl) and len(nl) >= 4
                  and nl not in EPI_STOP and nl not in FORM2COUNT):
                out.append(dict(head=UNIT_PREV[pl] + ":" + nl[:5], value=val, text=t["pid"], label=0))
            elif nl in FORM2COUNT:
                out.append(dict(head=FORM2COUNT[nl], value=val, text=t["pid"], label=1))
    return out


# ---------------- Indus (planted gate only) ----------------
def indus_tables():
    st = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
    short = {f"M{k}": v for k, v in st["short"].items() if f"M{k}" not in ("M99", "M101")}
    tall = {f"M{k}": v for k, v in st["tall"].items()}
    return short, tall


def indus_pairs(texts):
    """Numeral directly before a non-numeral head inside a break-free run (redteam_pnl rule, base tables)."""
    short, tall = indus_tables()
    isnum = lambda s: s in short or s in tall
    out = []
    for ti, t in enumerate(texts):
        for r in L.runs(t["seq"]):
            for i, s in enumerate(r):
                if isnum(s) and i + 1 < len(r) and not isnum(r[i + 1]):
                    sy = "short" if s in short else "tall"
                    out.append(dict(sys=sy, head=(sy, r[i + 1]), value=(short if sy == "short" else tall)[s], text=ti))
    return out


# ---------------- draws and tests ----------------
def heads_table(pairs, labeller):
    by = defaultdict(list)
    lab = {}
    for p in pairs:
        y = labeller(p)
        if y is None:
            continue
        by[p["head"]].append(p["value"]); lab[p["head"]] = y
    return {h: (v, lab[h]) for h, v in by.items() if len(v) >= NMIN}


def draw_sizes(rng, sizes, target=None):
    """sizes: dict head -> available tokens. Returns list of (head, n) per the frozen cut rule."""
    target = target or TARGET
    order = list(sizes); rng.shuffle(order)
    out, tot = [], 0
    for h in order:
        n = min(sizes[h], int(rng.integers(8, NMAX + 1)))
        out.append((h, n)); tot += n
        if tot >= target:
            break
    return out


def auc(x, y):
    x = np.asarray(x); y = np.asarray(y)
    a, b = x[y == 1], x[y == 0]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    return float(((a[:, None] > b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum()) / (len(a) * len(b)))


def perm_p(rng, x, y):
    """One-sided permutation p for AUC(counted > frozen): labels permuted across the heads of the draw.
    AUC is a monotone function of the midrank sum of the positives, so we permute the rank sum."""
    from scipy.stats import rankdata
    x = np.asarray(x, float); y = np.asarray(y)
    r = rankdata(x)  # midranks handle ties exactly as AUC's 0.5
    k = int(y.sum())
    obs = r[y == 1].sum()
    perms = np.argsort(rng.random((NPERM, len(x))), axis=1)[:, :k]
    null = r[perms].sum(1)
    return float((np.sum(null >= obs - 1e-9) + 1) / (NPERM + 1))


def run_corpus(table, rng, name, target=None):
    """table: head -> (values, label). Returns summary dict."""
    sizes = {h: len(v) for h, (v, _) in table.items()}
    labs = {h: y for h, (_, y) in table.items()}
    aucs, ps, ps_null, ntok, nh, n1, n0 = [], [], [], [], [], [], []
    calls = defaultdict(lambda: [0, 0])  # head -> [times called counted, times drawn]
    sens_hits = spec_hits = n_pos = n_neg = 0
    skipped = 0
    for d in range(DRAWS):
        sel = draw_sizes(rng, sizes, target)
        x, y = [], []
        for h, n in sel:
            vals = table[h][0]
            sub = [vals[i] for i in rng.choice(len(vals), n, replace=False)]
            ix = rarefied_distinct(sub)
            x.append(ix); y.append(labs[h])
            c = ix >= TAU
            calls[h][0] += c; calls[h][1] += 1
            if labs[h] == 1:
                n_pos += 1; sens_hits += c
            else:
                n_neg += 1; spec_hits += (not c)
        y = np.array(y)
        ntok.append(sum(n for _, n in sel)); nh.append(len(sel)); n1.append(int(y.sum())); n0.append(int((1 - y).sum()))
        if y.sum() < 3 or (1 - y).sum() < 3:
            skipped += 1; aucs.append(float("nan")); ps.append(1.0); ps_null.append(1.0)
            continue
        aucs.append(auc(x, y))
        ps.append(perm_p(rng, x, y))
        ps_null.append(perm_p(rng, x, rng.permutation(y)))
    aucs = np.array(aucs); ps = np.array(ps); ps_null = np.array(ps_null)
    maj = {h: c[0] / c[1] for h, c in calls.items() if c[1]}
    pos = [h for h in maj if labs[h] == 1]; neg = [h for h in maj if labs[h] == 0]
    maj_sens = float(np.mean([maj[h] >= 0.5 for h in pos])) if pos else float("nan")
    maj_spec = float(np.mean([maj[h] < 0.5 for h in neg])) if neg else float("nan")
    return dict(
        corpus=name, eligible_heads=len(table), eligible_counted=sum(labs.values()),
        eligible_frozen=len(labs) - sum(labs.values()), eligible_tokens=sum(sizes.values()),
        draws=DRAWS, skipped_draws=skipped,
        tokens_per_draw_mean=float(np.mean(ntok)), heads_per_draw_mean=float(np.mean(nh)),
        counted_heads_per_draw_mean=float(np.mean(n1)), frozen_heads_per_draw_mean=float(np.mean(n0)),
        power=float(np.mean(ps <= ALPHA)), false_alarm=float(np.mean(ps_null <= ALPHA)),
        separation_auc_mean=float(np.nanmean(aucs)), auc_p05=float(np.nanpercentile(aucs, 5)),
        auc_median=float(np.nanmedian(aucs)),
        draw_level_sensitivity=sens_hits / max(1, n_pos), draw_level_specificity=spec_hits / max(1, n_neg),
        head_majority_sensitivity=maj_sens, head_majority_specificity=maj_spec,
        head_majority_balanced_acc=float(np.nanmean([maj_sens, maj_spec])),
        head_call_share={str(h): round(v, 3) for h, v in sorted(maj.items(), key=lambda kv: -kv[1])},
        head_labels={str(h): labs[h] for h in labs},
    )


def run_planted(sizes, pool, rng, frozen_share=PLANT_FROZEN_SHARE, name="indus_planted"):
    """sizes: (sys, head) -> real dev token count (>= NMIN). pool: sys -> array of real pooled values.
    Per draw: same size cut; round(0.3 * heads drawn) heads planted counted (values iid from the pool of their
    system); the rest planted frozen (one value v* from the pool on each token with prob frozen_share, else a pool
    draw). Real head values are never read."""
    aucs, ps, ps_null, ntok, nh = [], [], [], [], []
    sens = spec = npos = nneg = 0
    for d in range(DRAWS):
        sel = draw_sizes(rng, sizes)
        k = max(1, int(round(PLANT_COUNTED_SHARE * len(sel))))
        lab = np.zeros(len(sel), int); lab[rng.choice(len(sel), k, replace=False)] = 1
        x = []
        for (h, n), y in zip(sel, lab):
            P = pool[h[0]]
            if y == 1:
                vals = list(rng.choice(P, n))
            else:
                vs = rng.choice(P)
                vals = [vs if rng.random() < frozen_share else rng.choice(P) for _ in range(n)]
            ix = rarefied_distinct(vals); x.append(ix)
            if y == 1:
                npos += 1; sens += ix >= TAU
            else:
                nneg += 1; spec += ix < TAU
        ntok.append(sum(n for _, n in sel)); nh.append(len(sel))
        if lab.sum() < 3 or (1 - lab).sum() < 3:
            aucs.append(float("nan")); ps.append(1.0); ps_null.append(1.0); continue
        aucs.append(auc(x, lab)); ps.append(perm_p(rng, x, lab)); ps_null.append(perm_p(rng, x, rng.permutation(lab)))
    aucs = np.array(aucs); ps = np.array(ps); ps_null = np.array(ps_null)
    return dict(corpus=name, frozen_share=frozen_share, eligible_heads=len(sizes), eligible_tokens=sum(sizes.values()),
                draws=DRAWS, tokens_per_draw_mean=float(np.mean(ntok)), heads_per_draw_mean=float(np.mean(nh)),
                power=float(np.mean(ps <= ALPHA)), false_alarm=float(np.mean(ps_null <= ALPHA)),
                separation_auc_mean=float(np.nanmean(aucs)), auc_p05=float(np.nanpercentile(aucs, 5)),
                draw_level_sensitivity=sens / max(1, npos), draw_level_specificity=spec / max(1, nneg))


def run_descriptive(table, rng, name):
    """PE: no reliable labels. Same size cut; report the index distribution and share called counted at TAU."""
    sizes = {h: len(v) for h, v in table.items()}
    allx, called = [], []
    for d in range(DRAWS):
        for h, n in draw_sizes(rng, sizes):
            vals = table[h]
            ix = rarefied_distinct([vals[i] for i in rng.choice(len(vals), n, replace=False)])
            allx.append(ix); called.append(ix >= TAU)
    allx = np.array(allx)
    return dict(corpus=name, eligible_heads=len(table), eligible_tokens=sum(sizes.values()),
                index_quartiles=[float(q) for q in np.percentile(allx, [25, 50, 75])],
                share_called_counted=float(np.mean(called)))


# ---------------- loaders ----------------
def load_all():
    pc = greedy_fast(cdli_texts(ROOT / "experiments/protocuneiform/pc_lines.json"))
    pe = greedy_fast(cdli_texts(ROOT / "experiments/protocuneiform/pe_lines.json"))
    la = greedy_fast(edh_texts())
    dev, _ = L.dev_heldout(version=2)
    ind = dedup.greedy(dev)
    pcp, pep, lap, inp = cdli_pairs(pc), cdli_pairs(pe), edh_pairs(la), indus_pairs(ind)
    return dict(pc_texts=len(pc), pe_texts=len(pe), la_texts=len(la), indus_dev_texts=len(ind)), pcp, pep, lap, inp


def tables(pcp, pep, lap, inp):
    PC = heads_table(pcp, lambda p: pc_label(p["head"]))
    LA = heads_table(lap, lambda p: p["label"])
    LA_novir = {h: v for h, v in LA.items() if h != "vir"}
    peby = defaultdict(list)
    for p in pep:
        peby[p["head"]].append(p["value"])
    PE = {h: v for h, v in peby.items() if len(v) >= NMIN}
    inby = Counter(p["head"] for p in inp)
    IS = {h: n for h, n in inby.items() if n >= NMIN}
    pool = {s: np.array([p["value"] for p in inp if p["sys"] == s]) for s in ("short", "tall")}
    return PC, LA, LA_novir, PE, IS, pool


def main():
    mode = sys.argv[1]
    if mode == "dedupcheck":
        import random
        random.seed(1)
        res = {}
        dev, _ = L.dev_heldout(version=2)
        res["indus_dev"] = [" ".join(t["seq"]) for t in greedy_fast(dev)] == [" ".join(t["seq"]) for t in dedup.greedy(dev)]
        la = edh_texts(); sub = random.sample(la, 3000)
        res["edh_3000"] = [" ".join(t["seq"]) for t in greedy_fast(sub)] == [" ".join(t["seq"]) for t in dedup.greedy(sub)]
        pc = cdli_texts(ROOT / "experiments/protocuneiform/pc_lines.json"); sub = random.sample(pc, 2000)
        res["pc_2000"] = [" ".join(t["seq"]) for t in greedy_fast(sub)] == [" ".join(t["seq"]) for t in dedup.greedy(sub)]
        print(res); json.dump(res, open(HERE / "dedupcheck.json", "w"), indent=1)
        return
    meta, pcp, pep, lap, inp = load_all()
    PC, LA, LA_novir, PE, IS, pool = tables(pcp, pep, lap, inp)
    if mode == "extract":
        # Sizes and labels only. No index values.
        out = dict(meta=meta,
                   pc=dict(pairs=len(pcp), heads=len(PC), counted=sum(y for _, y in PC.values()),
                           tokens=sum(len(v) for v, _ in PC.values()),
                           heads_list={h: [len(v), y] for h, (v, y) in sorted(PC.items(), key=lambda kv: -len(kv[1][0]))}),
                   latin=dict(pairs=len(lap), heads=len(LA), counted=sum(y for _, y in LA.values()),
                              tokens=sum(len(v) for v, _ in LA.values()),
                              heads_list={h: [len(v), y] for h, (v, y) in sorted(LA.items(), key=lambda kv: -len(kv[1][0]))}),
                   pe=dict(pairs=len(pep), heads=len(PE), tokens=sum(len(v) for v in PE.values())),
                   indus_gate=dict(pairs=len(inp), heads=len(IS), tokens=sum(IS.values()),
                                   pool_short=dict(sorted(Counter(pool["short"].tolist()).items())),
                                   pool_tall=dict(sorted(Counter(pool["tall"].tolist()).items()))))
        json.dump(out, open(HERE / "extract.json", "w"), indent=1, default=str)
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "heads_list"} if isinstance(v, dict) else v
                          for k, v in out.items()}, indent=1, default=str))
        return
    if mode == "score":
        rng = np.random.default_rng(SEED)
        R = {}
        R["indus_planted"] = run_planted(IS, pool, rng)
        R["indus_planted_frozen90"] = run_planted(IS, pool, rng, frozen_share=0.90, name="indus_planted_frozen90")
        R["protocuneiform"] = run_corpus(PC, rng, "protocuneiform")
        R["latin"] = run_corpus(LA, rng, "latin")
        R["latin_without_vir"] = run_corpus(LA_novir, rng, "latin_without_vir")
        R["protocuneiform_strict349"] = run_corpus(PC, rng, "protocuneiform_strict349", target=STRICT)
        R["latin_strict349"] = run_corpus(LA, rng, "latin_strict349", target=STRICT)
        R["protoelamite_descriptive"] = run_descriptive(PE, rng, "protoelamite")
        pc, la, g = R["protocuneiform"], R["latin"], R["indus_planted"]
        bars = {
            "B1_pc_power>=0.80": pc["power"] >= 0.80,
            "B2_pc_head_balanced_acc>=0.80": pc["head_majority_balanced_acc"] >= 0.80,
            "B3_latin_power>=0.80": la["power"] >= 0.80,
            "B4_latin_separation_auc>=0.90": la["separation_auc_mean"] >= 0.90,
            "B5_indus_planted_power>=0.80": g["power"] >= 0.80,
            "B6_false_alarm<=0.06_all": all(r["false_alarm"] <= 0.06 for r in (pc, la, g)),
        }
        R["bars"] = bars
        R["verdict"] = "GO" if all(bars.values()) else "NO-GO"
        json.dump(R, open(HERE / "results.json", "w"), indent=1, default=str)
        print(json.dumps({k: (v if k in ("bars", "verdict") else {kk: vv for kk, vv in v.items()
                                                                   if kk not in ("head_call_share", "head_labels")})
                          for k, v in R.items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
