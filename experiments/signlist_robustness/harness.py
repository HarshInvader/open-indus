"""Re-run the headline tests under each sign-list variant (pre-registered: docs/prereg/signlist_robustness.md).

    .venv/bin/python experiments/signlist_robustness/harness.py            # all variants, both units
    .venv/bin/python experiments/signlist_robustness/harness.py M77 ICIT   # selected variants

Tests reuse the logic of revalidation/revalidate.py (T1-T4), redteam/r8_direction.py (T5), the functional
grammar of functional_reading/fr.py (T6, T9) and core_semantics/h3_confirm.py + s2_classes.py (T7, T8).
Sign identities are abstracted through a Variant object, so the same code runs on every sign list.
Writes raw/<variant>.json; summarise.py builds the table.
"""
import sys, json, math, random, itertools, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import binomtest, norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "functional_reading"))
sys.path.insert(0, str(ROOT / "experiments" / "redteam"))
from corpus.load import m77_texts, m77_lines, icit_texts, dev_heldout, runs  # noqa
import fr  # noqa  (Grammar, HAND, NAMED_COMPOUNDS, positional_profile, clean_runs)
from rt_common import KN, edit1, near_dup_clusters  # noqa

VJ = json.load(open(HERE / "variants.json"))
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M_ALL = {f"W{int(k):03d}": [f"M{x}" for x in v["M"]] for k, v in BRIDGE.items()}

TICK_M = ["M60", "M66", "M68", "M71", "M73"]
PLAIN_M = ["M59", "M65", "M67", "M70", "M72"]
FISH_CORE6 = ["M59", "M65", "M67", "M70", "M72", "M75"]
FISH_ALL = fr.FISH_PLAIN + fr.FISH_BRACK          # core_semantics FISH (17)
TICK_W = ["W226", "W232", "W234", "W236", "W241"]
PLAIN_W = ["W220", "W231", "W233", "W235", "W240"]
REPS = 2000


# ===================================================================== variants
class Variant:
    """name; members(label) -> set of M signs; labels_of(m) -> set of labels; tok(m) -> label for a token."""

    def __init__(self, name):
        self.name = name
        self.icit = name == "ICIT"
        if self.icit:
            self.mem = {w: set(ms) for w, ms in W2M_ALL.items()}
            self.inv = defaultdict(set)
            for w, ms in W2M_ALL.items():
                for m in ms:
                    self.inv[m].add(w)
            for m, w in zip(TICK_M + PLAIN_M, TICK_W + PLAIN_W):   # font-verified codes override bridge
                self.inv[m] = {w}
            self.inv["M109"] = {"W016"}; self.inv["M342"] = {"W740"}
            return
        if name.startswith("split_"):
            self.spec = VJ["splits"][name]
            self.part = {m: m for m in VJ["partitions"]["M77"]}
            self.rng = np.random.default_rng(int(name[-1]) + 100)
        else:
            self.spec = {}
            self.part = VJ["partitions"][name]
        self.mem = defaultdict(set); self.inv = defaultdict(set)
        for m, l in self.part.items():
            k = self.spec.get(m, 0)
            labs = [f"{l}.{c}" for c in "abc"[:k]] if k else [l]
            for x in labs:
                self.mem[x].add(m); self.inv[m].add(x)

    def tok(self, s):
        if s in ("|", "#"):
            return s
        if self.icit:
            return s
        k = self.spec.get(s, 0)
        l = self.part.get(s, s)
        return f"{l}.{'abc'[self.rng.integers(k)]}" if k else l

    def labels_of(self, ms):
        return set().union(*[self.inv.get(m, set()) for m in ms])

    def members(self, lab):
        return self.mem.get(lab, set())


# ===================================================================== corpora
def icit_class(tp):
    if tp.startswith("SEAL"): return "seal"
    if tp == "TAB:B": return "moulded tablet"
    if tp == "TAB:I": return "incised tablet"
    if tp == "TAB:C": return "copper tablet"
    if tp.startswith("POT"): return "pottery graffito"
    return tp


def icit_split():
    """family split for ICIT (edit distance <= 1 clusters, 75/25, seed 0)."""
    flat = sorted({tuple(s for s in t["seq"] if s not in "|#") for t in icit_texts()} - {()})
    cl = near_dup_clusters(flat)
    r = random.Random(0); r.shuffle(cl)
    cut = int(0.75 * len(cl))
    ho = {s for c in cl[cut:] for s in c}
    return ho


def build_corpus(V):
    """-> dict(dev_tok, ho_tok, dev_type, ho_type, rl/lr lines tok/type, n_dropped)."""
    recs = []
    if V.icit:
        ho_flat = icit_split()
        for t in icit_texts():
            f = tuple(s for s in t["seq"] if s not in "|#")
            if not f: continue
            recs.append(dict(seq=list(t["seq"]), object_type=icit_class(t["type"]), site=t["site"],
                             complete=True, split="heldout" if f in ho_flat else "dev"))
    else:
        dev, ho = dev_heldout(version=2)
        hk = {" ".join(t["seq"]) for t in ho}
        for t in m77_texts():
            recs.append(dict(seq=[V.tok(s) for s in t["seq"]], object_type=t["object_type"], site=t["site"],
                             complete=t["complete"], split="heldout" if " ".join(t["seq"]) in hk else "dev"))
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
    ho_type0 = dist(ho_tok)
    ho_type = [r for r in ho_type0 if tuple(r["seq"]) not in dk]
    ho_tok2 = [r for r in ho_tok if tuple(r["seq"]) not in dk]
    # direction lines
    lines = []
    if V.icit:
        for t in icit_texts():
            d = {"R/L": "rl", "L/R": "lr"}.get(t["direction"])
            if d:
                for seg in t["segments"]:
                    if len(seg) >= 2: lines.append((d, tuple(seg)))
    else:
        for l in m77_lines():
            d = {"right-to-left": "rl", "left-to-right": "lr"}.get(l["direction"])
            if d:
                for seg in l["segments"]:
                    if len(seg) >= 2: lines.append((d, tuple(V.tok(s) for s in seg)))
    return dict(dev_token=dev_tok, ho_token=ho_tok2, dev_type=dev_type, ho_type=ho_type,
                lines=lines, n_ho_dropped_as_copies=len(ho_type0) - len(ho_type))


R_ = lambda ts: [r for t in ts for r in runs(t["seq"])]


# ===================================================================== T1 order
def t1_order(dev, ho):
    uni, big = Counter(), Counter()
    for r in R_(dev):
        seq = ["<s>"] + r + ["</s>"]
        uni.update(seq[:-1]); big.update(zip(seq, seq[1:]))
    Vn = len(uni) + 1

    def lp(r):
        seq = ["<s>"] + list(r) + ["</s>"]
        return sum(math.log((big[(a, b)] + 0.1) / (uni[a] + 0.1 * Vn)) for a, b in zip(seq, seq[1:]))
    best = 0; mu = var = 0.0; n = 0
    cache = {}
    for t in ho:
        if not t["complete"]: continue
        for r in runs(t["seq"]):
            if not (3 <= len(r) <= 7): continue
            key = tuple(r)
            if key not in cache:
                perms = set(itertools.permutations(r))
                if len(perms) < 6:
                    cache[key] = None; continue
                s0 = lp(r)
                cache[key] = (all(lp(p) < s0 for p in perms if p != key), 1 / len(perms))
            if cache[key] is None: continue
            b, q = cache[key]
            best += b; mu += q; var += q * (1 - q); n += 1
    z = (best - mu) / math.sqrt(var) if var else 0
    share, ch = best / max(n, 1), mu / max(n, 1)
    p = float(norm.sf(z))
    return dict(n_runs=n, share=round(share, 3), chance=round(ch, 3), ratio=round(share / ch, 2) if ch else None,
                p=p, survives=bool(share >= 2 * ch and p < 1e-3))


# ===================================================================== T2 ticked fish
def fish_sets(V):
    if V.icit:
        return set(TICK_W), set(PLAIN_W)
    tl = V.labels_of(TICK_M); pl = V.labels_of(PLAIN_M)
    tick = {l for l in tl if not (V.members(l) & set(PLAIN_M + ["M75"] + fr.FISH_PLAIN))}
    plain = {l for l in pl if not (V.members(l) & set(TICK_M))}
    return tick, plain


def final_share(ts, signs):
    tot = fin = 0
    for t in ts:
        for r in runs(t["seq"]):
            if len(r) < 2: continue
            for i, s in enumerate(r):
                if s in signs:
                    tot += 1; fin += (i == len(r) - 1)
    return fin, tot


def t2_tick(V, dev, ho, rng):
    tick, plain = fish_sets(V)
    if not tick or not plain:
        return dict(NT="ticked and plain fish share a label", survives=None)
    f, tt = final_share(ho, tick); fp, tp = final_share(ho, plain)
    if tt == 0:
        return dict(NT="no ticked fish in held-out", survives=None)
    freq = Counter(s for r in R_(dev) for s in r)
    band = [s for s in freq if 10 <= freq[s] <= 80 and s not in tick | plain]
    k = len(tick) if V.icit or len(tick) <= 5 else 5
    k = min(k, 5)
    null = []
    for _ in range(REPS):
        a, b = final_share(ho, set(rng.sample(band, k)))
        if b: null.append(a / b)
    obs = f / tt
    p = float((1 + sum(x >= obs for x in null)) / (1 + len(null)))
    return dict(final=f, tokens=tt, share=round(obs, 3), plain_share=round(fp / max(tp, 1), 3),
                null_mean=round(float(np.mean(null)), 3), p=p, survives=bool(p < 0.05 and obs > fp / max(tp, 1)))


# ===================================================================== T3 six + fish
def t3_sixfish(V, dev, ho):
    A = V.labels_of(["M109"]); B = V.labels_of(["M59"])
    if A & B:
        return dict(NT="six and fish share a label", survives=None)
    c = Counter()
    for r in R_(ho):
        for x, y in zip(r, r[1:]):
            if x in A: c[y in B] += 1
    toks = [s for r in R_(dev) for s in r]
    base = sum(s in B for s in toks) / len(toks)
    k, N = c[True], c[True] + c[False]
    p = binomtest(k, N, base, alternative="greater").pvalue if N else 1.0
    return dict(six_labels=sorted(A), fish_labels=sorted(B), n=N, k=k, base=round(base, 4), p=float(p),
                survives=bool(k >= 3 and p < 0.01))


# ===================================================================== T4 registers
def t4_registers(dev, ho, rng):
    types = sorted({t["object_type"] for t in dev + ho})
    cnt_d = Counter(t["object_type"] for t in dev)
    keep = [x for x in types if cnt_d[x] >= 20]

    def XY(ts):
        X = [set(s for s in t["seq"] if s not in "|#") for t in ts if t["object_type"] in keep]
        y = [t["object_type"] for t in ts if t["object_type"] in keep]
        return X, y
    Xd, yd = XY(dev); Xh, yh = XY(ho)
    vocab = sorted({s for x in Xd for s in x}); idx = {s: i for i, s in enumerate(vocab)}

    def M(X):
        A = np.zeros((len(X), len(vocab)))
        for i, x in enumerate(X):
            for s in x:
                if s in idx: A[i, idx[s]] = 1
        return A
    clf = LogisticRegression(max_iter=3000, C=0.5, class_weight="balanced").fit(M(Xd), yd)
    P = clf.predict_proba(M(Xh)); out = {}
    for j, cl in enumerate(clf.classes_):
        yy = np.array([y == cl for y in yh])
        if 5 <= yy.sum() < len(yy):
            obs = roc_auc_score(yy, P[:, j])
            nul = [roc_auc_score(rng.permutation(yy), P[:, j]) for _ in range(500)]
            out[cl] = dict(n=int(yy.sum()), auc=round(obs, 3), null95=round(float(np.quantile(nul, .95)), 3))
    above = sum(v["auc"] > v["null95"] for v in out.values())
    mean = float(np.mean([v["auc"] for v in out.values()]))
    return dict(classes=out, above=above, n_classes=len(out), mean_auc=round(mean, 3),
                survives=bool(above >= min(4, len(out)) and mean >= 0.65))


# ===================================================================== T5 direction
def t5_direction(lines, unit):
    if unit == "type":
        lines = list(dict.fromkeys(lines))
    rl = [s for d, s in lines if d == "rl"]; lr = [s for d, s in lines if d == "lr"]
    rlset = set(rl); bylen = defaultdict(list)
    for s in rlset: bylen[len(s)].append(s)
    clean = [s for s in lr if s not in rlset and not any(edit1(s, r) for L in (len(s) - 1, len(s), len(s) + 1) for r in bylen.get(L, []))]
    m = KN(rl)
    res = [m.bits(s) < m.bits(s[::-1]) for s in clean if s != s[::-1]]
    k, n = sum(res), len(res)
    p = binomtest(k, n, .5, alternative="greater").pvalue if n else 1.0
    return dict(n_rl=len(rl), n_lr=len(lr), n_clean=n, as_labelled=k, share=round(k / max(n, 1), 3), p=float(p),
                survives=bool(n and k / n >= 0.70 and p < 1e-3))


# ===================================================================== functional grammar under a variant
NONNAME = ("opener-class", "pre-jar title element", "post-closer element")


def mapped_hand(V, vocab):
    """label -> (roles, category, primary role) from hand roles of members."""
    out = {}
    for lab in vocab:
        mem = V.members(lab) if not V.icit else set(W2M_ALL.get(lab, [])[:1])
        hs = [fr.HAND[m] for m in sorted(mem) if m in fr.HAND]
        if not hs: continue
        roles = set().union(*[set(h[0]) for h in hs])
        prim = Counter(h[0][0] for h in hs).most_common(1)[0][0]
        out[lab] = (roles, hs[0][1], prim)
    return out


def build_lexicon_v(V, dev, thr=None):
    thr = thr or dict(n=5, init_only=0.6, init_mix=0.4, fin_only=0.7, fin_mix=0.45, post=0.5, prejar=0.5)
    pos, prev, nxt, ntext = fr.positional_profile(dev)
    hand = mapped_hand(V, list(pos))
    jar = V.labels_of(["M342"])
    closers = {s for s, v in hand.items() if "J" in v[0]}
    lex = {}
    for s in pos:
        c = pos[s]; tot = sum(c.values())
        if s in hand:
            roles, cat, prim = hand[s]
            lex[s] = dict(roles=roles, category=cat, prim=prim, grade="B", source="hand"); continue
        if ntext[s] < thr["n"]:
            lex[s] = dict(roles={"N"}, category="unknown noun", prim="N", grade="-", source="default"); continue
        pi = c["I"] / tot; pf = c["F"] / tot
        pp = sum(v for k, v in prev[s].items() if k in closers) / max(1, sum(prev[s].values()))
        pj = sum(nxt[s][j] for j in jar) / max(1, sum(nxt[s].values()))
        roles, cat = {"N"}, "unknown noun"
        if pp >= thr["post"] and pf >= 0.5: roles, cat = {"P", "J"}, "post-closer element"
        elif pf >= thr["fin_only"]: roles, cat = {"J"}, "closer-class word"
        elif pf >= thr["fin_mix"]: roles, cat = {"J", "N"}, "closer-class/core noun"
        elif pj >= thr["prejar"] and sum(nxt[s].values()) >= 5: roles, cat = {"I", "N"}, "pre-jar title element"
        elif pi >= thr["init_only"]: roles, cat = {"O"}, "opener-class word"
        elif pi >= thr["init_mix"]: roles, cat = {"O", "N"}, "opener-class/core noun"
        lex[s] = dict(roles=roles, category=cat, prim="N" if cat == "unknown noun" else "X", grade="C", source="dev")
    return lex


def strip_pairs(V):
    """label bigrams belonging to TITLE-BLOCK / REGISTER named compounds (stripped from cores)."""
    out = set()
    for (a, b), v in fr.NAMED_COMPOUNDS.items():
        if v[0] in ("TITLE-BLOCK", "REGISTER"):
            for x in V.labels_of([a]):
                for y in V.labels_of([b]):
                    out.add((x, y))
    return out


def core_ok(s, role, lex):
    if role not in ("N", "F"): return False
    e = lex.get(s)
    if e is None: return True
    if e["prim"] not in ("N", "F"): return False
    return not str(e["category"]).startswith(NONNAME)


def cores_of(G, lex, texts, sp):
    """core occurrences: dict(core, left, right, num_adj, text, object_type); one per record."""
    occ = []
    for ti, t in enumerate(texts):
        for (r, so, eo) in fr.clean_runs(t):
            roles = G.viterbi(r, so, eo)
            if roles is None:
                roles, _ = G.robust_parse(r, so, eo)
            ok = [core_ok(s, ro, lex) for s, ro in zip(r, roles)]
            for i in range(len(r) - 1):
                if (r[i], r[i + 1]) in sp: ok[i] = ok[i + 1] = False
            i, n = 0, len(r)
            while i < n:
                if not ok[i]:
                    i += 1; continue
                j = i
                while j < n and ok[j]: j += 1
                if not ((i == 0 and so) or (j == n and eo)):
                    L = r[i - 1] if i > 0 else "^"; Rr = r[j] if j < n else "$"
                    lr_ = roles[i - 1] if i > 0 else "^"; rr_ = roles[j] if j < n else "$"
                    occ.append(dict(core=tuple(r[i:j]), left=L, right=Rr, num_adj=lr_ in "ST" or rr_ in "ST",
                                    text=(ti, tuple(t["seq"])), object_type=t["object_type"]))
                i = j
    return occ


def incidence(occ):
    inc = Counter(); seen = set()
    for o in occ:
        k = (o["text"], o["core"])
        if k in seen: continue
        seen.add(k); inc[o["core"]] += 1
    return inc


def t6_cores(inc_ho):
    cores = list(inc_ho)          # distinct core types (as typology)
    one = {c[0] for c in cores if len(c) == 1}
    long_ = [c for c in cores if len(c) >= 2]
    tok = [s for c in long_ for s in c]
    l1 = sum(len(c) == 1 for c in cores) / len(cores)
    st = float(np.mean([s in one for s in tok])) if tok else float("nan")
    return dict(n_core_types=len(cores), len1_share=round(l1, 3), standalone_tok=round(st, 3),
                survives=bool(l1 >= 0.28 and st >= 0.22))


def adjacent_pairs(inc):
    by = defaultdict(lambda: [0, 0])
    for c, k in inc.items():
        for a, b in zip(c, c[1:]):
            if a == b: continue
            x, y = sorted((a, b))
            by[(x, y)][0 if (a, b) == (x, y) else 1] += k
    return by


def t7_pairorder(inc_tr, inc_te):
    tr = adjacent_pairs(inc_tr); te = adjacent_pairs(inc_te)
    agree = n = npairs = 0
    for p, (f, r) in tr.items():
        tot = f + r
        if tot < 2 or max(f, r) / tot < 2 / 3: continue
        if p in te:
            tf, trv = te[p]
            if tf + trv:
                npairs += 1; agree += tf if f >= r else trv; n += tf + trv
    p = binomtest(agree, n, 0.5, alternative="greater").pvalue if n else 1.0
    share = agree / n if n else None
    return dict(test_pairs=npairs, occurrences=n, agree=agree, share=round(share, 3) if n else None, p=float(p),
                survives=bool(n and share >= 0.75 and p < 1e-3))


def fish_labels_core(V):
    if V.icit:
        fam = {w for w, ms in W2M_ALL.items() if set(ms) & set(FISH_ALL)} | set(TICK_W) | set(PLAIN_W)
        return fam, len({w for w in fam if set(W2M_ALL.get(w, [])) & set(FISH_CORE6)} | set(PLAIN_W)) <= 1
    fam = V.labels_of(FISH_ALL)
    core_labels = {next(iter(V.labels_of([m]))) if len(V.labels_of([m])) == 1 else m for m in FISH_CORE6}
    collapsed = len({frozenset(V.labels_of([m])) for m in FISH_CORE6}) <= 1 and not V.spec
    return fam, collapsed


def t8_fish(V, inc_tr, inc_te, occ_te, numerals, rng):
    fam, collapsed = fish_labels_core(V)
    if collapsed:
        return dict(NT="fish family is one label", survives=None)
    # SC1: set coherence (frames + partners PPMI cosine), signs with >= 3 core occurrences
    def ctx(s): return "NUM" if s in numerals else s
    cnt = Counter(); frames = defaultdict(Counter); partners = defaultdict(Counter); seen = set()
    for o in occ_te:
        key = (o["text"], o["core"])
        if key in seen: continue
        seen.add(key); c = o["core"]
        for i, s in enumerate(c):
            cnt[s] += 1
            L = c[i - 1] if i > 0 else o["left"]; Rr = c[i + 1] if i < len(c) - 1 else o["right"]
            frames[s]["L:" + ctx(L)] += 1; frames[s]["R:" + ctx(Rr)] += 1
            for j, q in enumerate(c):
                if j != i: partners[s]["P:" + q] += 1
    signs = sorted([s for s, k in cnt.items() if k >= 3], key=lambda s: -cnt[s])
    feats = {s: frames[s] + partners[s] for s in signs}
    cols = sorted({f for s in signs for f in feats[s]}); ci = {f: i for i, f in enumerate(cols)}
    Mx = np.zeros((len(signs), len(cols)))
    for r_, s in enumerate(signs):
        for f, v in feats[s].items(): Mx[r_, ci[f]] = v
    tot = Mx.sum(); pr = Mx.sum(1, keepdims=True) / tot; pc = Mx.sum(0, keepdims=True) / tot
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.log((Mx / tot) / (pr * pc ** 0.75 / (pc ** 0.75).sum()))
    P[~np.isfinite(P)] = 0; P = np.maximum(P, 0)
    nrm = np.linalg.norm(P, axis=1, keepdims=True); nrm[nrm == 0] = 1
    X = P / nrm; S = X @ X.T
    idx = [i for i, s in enumerate(signs) if s in fam]
    sc1 = None
    if len(idx) >= 2:
        iu = np.triu_indices(len(idx), 1); obs = S[np.ix_(idx, idx)][iu].mean()
        others = [i for i in range(len(signs)) if signs[i] not in fam]
        logf = np.log([cnt[s] for s in signs]); null = []
        for _ in range(REPS):
            pick = []
            for i in idx:
                cand = [j for j in others if abs(logf[j] - logf[i]) < 0.5 and j not in pick] or others
                pick.append(rng.choice(cand))
            null.append(S[np.ix_(pick, pick)][iu].mean())
        sc1 = dict(members=[signs[i] for i in idx], obs=round(float(obs), 4), null=round(float(np.mean(null)), 4),
                   p=float((1 + (np.array(null) >= obs).sum()) / (1 + REPS)))
    # SC5 fish + fish
    cores = [c for c in inc_te if len(c) > 1]
    obs5 = np.mean([sum(s in fam for s in c) >= 2 for c in cores])
    toks = [s for c in cores for s in c]; lens = [len(c) for c in cores]; null = []
    for _ in range(REPS):
        p_ = rng.permutation(toks); i = 0; k = 0
        for L in lens:
            k += sum(s in fam for s in p_[i:i + L]) >= 2; i += L
        null.append(k / len(cores))
    sc5 = dict(obs=round(float(obs5), 4), null=round(float(np.mean(null)), 4),
               p=float((1 + (np.array(null) >= obs5).sum()) / (1 + REPS)))
    # SC7 partner set transfer
    def partners_of(inc):
        c = Counter()
        for core in inc:
            if len(core) > 1 and any(s in fam for s in core):
                for s in core:
                    if s not in fam: c[s] += 1
        return c
    Pset = [s for s, _ in partners_of(inc_tr).most_common(5)]
    tep = partners_of(inc_te); hit = sum(tep[s] for s in Pset); n = sum(tep.values())
    base_c = Counter(s for core in inc_te if len(core) > 1 for s in core if s not in fam)
    base = sum(base_c[s] for s in Pset) / max(1, sum(base_c.values()))
    p7 = binomtest(hit, n, base, alternative="greater").pvalue if n else 1.0
    sc7 = dict(partners=Pset, hits=hit, n=n, share=round(hit / max(n, 1), 3), base=round(base, 3), p=float(p7))
    ps = [x["p"] for x in (sc1, sc5, sc7) if x]
    npass = sum(p < 0.05 for p in ps)
    return dict(SC1=sc1, SC5=sc5, SC7=sc7, n_pass=npass, survives=bool(npass >= 2))


def shuffled(t, r):
    seq = list(t["seq"]); pos = [i for i, s in enumerate(seq) if s not in ("|", "#")]
    vals = [seq[i] for i in pos]; r.shuffle(vals)
    for i, v in zip(pos, vals): seq[i] = v
    return dict(t, seq=seq)


def t9_parse(G, ho, rng, nshuf=20):
    ts = [t for t in ho if sum(s not in "|#" for s in t["seq"]) >= 2]
    real = float(np.mean([G.accepts(t) for t in ts]))
    sh = np.array([np.mean([G.accepts(shuffled(t, rng)) for t in ts]) for _ in range(nshuf)])
    z = (real - sh.mean()) / (sh.std() + 1e-9)
    return dict(n=len(ts), coverage=round(real, 3), shuffle=round(float(sh.mean()), 3), shuffle_sd=round(float(sh.std()), 3),
                z=round(float(z), 1), survives=bool(real - sh.mean() >= 0.20 and z >= 5))


# ===================================================================== driver
def run_variant(name):
    t0 = time.time()
    V = Variant(name)
    C = build_corpus(V)
    out = {"variant": name, "n_labels": None, "n_ho_dropped_as_copies": C["n_ho_dropped_as_copies"]}
    all_signs = {s for r in C["dev_token"] + C["ho_token"] for s in r["seq"] if s not in "|#"}
    out["n_labels"] = len(all_signs)
    for unit in ("type", "token"):
        dev, ho = C[f"dev_{unit}"], C[f"ho_{unit}"]
        rng = random.Random(7); nrng = np.random.default_rng(7)
        res = {"n_dev": len(dev), "n_ho": len(ho)}
        res["T1"] = t1_order(dev, ho)
        res["T2"] = t2_tick(V, dev, ho, rng)
        res["T3"] = t3_sixfish(V, dev, ho)
        res["T4"] = t4_registers(dev, ho, nrng)
        res["T5"] = t5_direction(C["lines"], unit)
        dev_g = [t for t in dev if t["site"] != "West Asian finds"]
        lex = build_lexicon_v(V, dev_g)
        G = fr.Grammar(lex, "final").fit(dev_g)
        sp = strip_pairs(V)
        occ_tr = cores_of(G, lex, dev, sp); occ_te = cores_of(G, lex, ho, sp)
        inc_tr, inc_te = incidence(occ_tr), incidence(occ_te)
        numerals = {s for s, e in lex.items() if e["roles"] & {"S", "T"} and e["source"] == "hand"}
        res["T6"] = t6_cores(inc_te)
        res["T7"] = t7_pairorder(inc_tr, inc_te)
        res["T8"] = t8_fish(V, inc_tr, inc_te, occ_te, numerals, nrng)
        res["T9"] = t9_parse(G, ho, rng)
        out[unit] = res
        print(name, unit, {k: v.get("survives") for k, v in res.items() if isinstance(v, dict)}, f"{time.time()-t0:.0f}s", flush=True)
    (HERE / "raw").mkdir(exist_ok=True)
    json.dump(out, open(HERE / "raw" / f"{name}.json", "w"), indent=1, default=str)
    return out


ALL = ["M77", "ICIT", "parpola", "lump_fish", "lump_numerals", "lump_jar_man", "lump_all",
       "split_s1", "split_s2", "split_s3", "img_hi", "img_mid", "img_lo"]

if __name__ == "__main__":
    names = sys.argv[1:] or ALL
    if len(names) == 1:
        run_variant(names[0])
    else:
        from multiprocessing import Pool
        with Pool(2) as p:
            p.map(run_variant, names)
