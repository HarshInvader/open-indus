"""Pre-registered tests (docs/prereg/copper_series.md): copper tablet types as calendrical series (H1),
tallies (H2) or amulets (H3). Run from repo root: .venv/bin/python experiments/copper_series/tests.py
Needs types.csv and tablets_typed.csv from build_types.py."""
import csv, json, sys, re, itertools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import networkx as nx
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa

OUT = ROOT / "experiments" / "copper_series"
RNG = np.random.default_rng(20261115)
KS = [6, 7, 12, 13, 27, 28]
FORMULA = {"M342", "M169", "M407"}
R = {}

types = list(csv.DictReader(open(OUT / "types.csv")))
tabs = list(csv.DictReader(open(OUT / "tablets_typed.csv")))
for t in types:
    for k in ("n_M77", "n_ICIT", "n_est", "n_sum"):
        t[k] = int(t[k])
    t["seq"] = [s for s in t["legend"].split() if s not in ("|", "#")]
    t["content"] = [s for s in t["seq"] if s not in FORMULA]

# numerals from the functional-reading lexicon
NUM = {}
for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
    if r["kind"] == "sign" and r["roles"].startswith("NUMERAL"):
        m = re.search(r"numeral (\d+)", r["meaning_category"])
        if m:
            NUM[r["item"]] = int(m.group(1))
UNIT = {"M190"}


def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum())) if n and x.sum() else 0.0


def chao1(counts):
    c = Counter(counts); S = len(counts); f1, f2 = c[1], c[2]
    if f2 > 0:
        est = S + f1 * f1 / (2 * f2)
        r = f1 / f2
        var = f2 * (r ** 4 / 4 + r ** 3 + r ** 2 / 2)
    else:
        est = S + f1 * (f1 - 1) / 2
        var = f1 * (f1 - 1) / 2 + f1 * (2 * f1 - 1) ** 2 / 4 - f1 ** 4 / (4 * est) if f1 else 0
    T = est - S
    if T <= 0 or var <= 0:
        return est, (S, S)
    K = np.exp(1.96 * np.sqrt(np.log(1 + var / T ** 2)))
    return float(est), (float(S + T / K), float(S + T * K))


def uniform_gini_sims(N, K, n=10000):
    g = np.empty(n)
    for i in range(n):
        c = RNG.multinomial(N, [1 / K] * K)
        g[i] = gini(c[c > 0])
    return g


def zipf_fit(counts, M=100):
    n = np.sort(np.asarray(counts))[::-1]; r = np.arange(1, len(n) + 1)
    best = None
    for s in np.linspace(0.0, 3.0, 301):
        p = np.arange(1, M + 1, dtype=float) ** -s; p /= p.sum()
        ll = float((n * np.log(p[: len(n)])).sum())
        if best is None or ll > best[1]:
            best = (float(s), ll)
    return best


def richness_evenness(counts, label):
    counts = [c for c in counts if c > 0]
    N, S = sum(counts), len(counts)
    f1 = sum(1 for c in counts if c == 1)
    cov = 1 - f1 / N
    est, ci = chao1(counts)
    g = gini(counts)
    ev = {}
    for K in KS:
        sims = uniform_gini_sims(N, K, 4000)
        lo, hi = np.percentile(sims, [2.5, 97.5])
        ev[K] = dict(sim_lo=float(lo), sim_hi=float(hi), inside=bool(lo <= g <= hi), above_975=bool(g > hi),
                     p_ge=float((sims >= g).mean()))
    s, llz = zipf_fit(counts)
    llu = {K: (N * np.log(1 / K) if K >= S else None) for K in KS}
    out = dict(label=label, N=N, S=S, f1=f1, f2=sum(1 for c in counts if c == 2), coverage=cov, chao1=est,
               chao1_ci=ci, ci_contains_K=[K for K in KS if ci[0] <= K <= ci[1]], gini=g, uniform=ev,
               zipf_s=s, zipf_ll=llz, uniform_ll={str(k): v for k, v in llu.items()},
               H1a=bool(cov >= 0.90 and any(ci[0] <= K <= ci[1] for K in KS)),
               H1b=bool(any(v["inside"] for v in ev.values())), H2b=bool(all(v["above_975"] for v in ev.values())))
    print(f"[{label}] N={N} S={S} f1={f1} f2={out['f2']} coverage={cov:.3f} chao1={est:.1f} CI=({ci[0]:.1f},{ci[1]:.1f}) "
          f"gini={g:.3f} zipf_s={s:.2f} | H1a={out['H1a']} H1b={out['H1b']} H2b={out['H2b']}")
    for K in KS:
        print(f"    K={K}: uniform Gini 95% [{ev[K]['sim_lo']:.3f},{ev[K]['sim_hi']:.3f}] P(G>=obs)={ev[K]['p_ge']:.4f}")
    return out


def accumulation(objs, reps=500):
    curves = np.zeros((reps, len(objs)))
    for i in range(reps):
        o = RNG.permutation(objs); seen = set()
        for j, x in enumerate(o):
            seen.add(x); curves[i, j] = len(seen)
    return curves.mean(0)


# ---------------- H1a / H1b / H2b ----------------
print("=== H1a/H1b/H2b richness and evenness ===")
full = [t["n_est"] for t in types]
core = [c for c in full if c >= 2]
RE = {"full": richness_evenness(full, "full n_est"), "core": richness_evenness(core, "core n_est>=2")}
sens = {}
sens["n_sum"] = richness_evenness([t["n_sum"] for t in types], "sens n_sum")
sens["M77"] = richness_evenness([t["n_M77"] for t in types], "sens M77 only")
sens["ICIT"] = richness_evenness([t["n_ICIT"] for t in types], "sens ICIT only")
lump = Counter()
for t in types:
    lump[t["lumped"]] += t["n_est"]
sens["lumped"] = richness_evenness(list(lump.values()), "sens lumped")
pics = Counter()
for t in tabs:
    if t["pic"] and t["source"] == "M77":
        pics[t["pic"]] += 1
sens["picture_classes_M77"] = richness_evenness(list(pics.values()), "sens picture classes (M77 fs80)")
R["richness_evenness"] = RE; R["richness_evenness_sensitivity"] = sens
H1a = RE["full"]["H1a"] or RE["core"]["H1a"]
H1b = RE["full"]["H1b"] or RE["core"]["H1b"]
H2b = RE["full"]["H2b"]

# accumulation curve (objects expanded from n_est, and M77 objects alone)
objs = [t["type"] for t in types for _ in range(t["n_est"])]
acc = accumulation(objs)
R["accumulation_n_est"] = [float(x) for x in acc[[0, 9, 19, 39, 59, 79, 99, 119, 139, len(acc) - 1] if len(acc) > 139 else range(len(acc))]]
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(np.arange(1, len(acc) + 1), acc, color="#3b5bdb", label="copper types (n_est)")
    for K in (12, 13, 27, 28):
        ax.axhline(K, color="#adb5bd", lw=0.8, ls="--")
        ax.text(2, K + 0.4, f"K={K}", fontsize=8, color="#868e96")
    ax.axhline(RE["full"]["chao1"], color="#e8590c", lw=1)
    ax.text(len(acc) * 0.55, RE["full"]["chao1"] + 0.6, f"Chao1 {RE['full']['chao1']:.0f}", fontsize=8, color="#e8590c")
    ax.set_xlabel("tablets examined (random order)"); ax.set_ylabel("distinct types seen")
    ax.set_title("Copper tablet type accumulation"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "accumulation.png", dpi=150)
except Exception as e:
    print("plot failed", e)

# power for evenness
N = RE["full"]["N"]
pw = {}
zp = np.arange(1, 41, dtype=float) ** -1.0; zp /= zp.sum()
lims = {K: np.percentile(uniform_gini_sims(N, K, 4000), [2.5, 97.5]) for K in KS}
rej = 0
for _ in range(1000):
    c = RNG.multinomial(N, zp); g = gini(c[c > 0])
    rej += all(g > lims[K][1] for K in KS)
pw["zipf1_40types_rejects_all_uniformK"] = rej / 1000
R["power_evenness"] = pw
print("power: Zipf(s=1, 40 types) rejected vs every uniform-K:", pw)

# ---------------- H1c ring ----------------
print("\n=== H1c shared-sign graph ===")
nodes = [t for t in types if t["n_est"] >= 2]


def graph(contents):
    G = nx.Graph(); G.add_nodes_from(range(len(contents)))
    sets = [set(c) for c in contents]
    for i, j in itertools.combinations(range(len(sets)), 2):
        if sets[i] & sets[j]:
            G.add_edge(i, j)
    return G


def deg_cv(G):
    d = np.array([x for _, x in G.degree()], float)
    return float(d.std() / d.mean()) if d.mean() > 0 else float("inf")


def has_hc(G, limit=200000):
    n = G.number_of_nodes()
    if n < 3 or min(dict(G.degree()).values()) < 2 or not nx.is_connected(G):
        return False
    adj = {u: set(G[u]) for u in G}
    start = min(adj, key=lambda u: len(adj[u]))
    calls = [0]

    def dfs(u, path, seen):
        calls[0] += 1
        if calls[0] > limit:
            raise TimeoutError
        if len(path) == n:
            return start in adj[u]
        for v in sorted(adj[u] - seen, key=lambda v: len(adj[v] - seen)):
            seen.add(v); path.append(v)
            if dfs(v, path, seen):
                return True
            seen.discard(v); path.pop()
        return False
    try:
        return dfs(start, [start], {start})
    except TimeoutError:
        return None


def modularity(G):
    if G.number_of_edges() == 0:
        return 0.0
    comms = nx.algorithms.community.greedy_modularity_communities(G)
    return float(nx.algorithms.community.modularity(G, comms))


def permute(contents):
    pool = [s for c in contents for s in c]
    pool = list(RNG.permutation(pool)); out = []; i = 0
    for c in contents:
        out.append(pool[i:i + len(c)]); i += len(c)
    return out


def ring_stats(contents, nperm=2000, hc_perm=200):
    G = graph(contents)
    obs = dict(n=G.number_of_nodes(), edges=G.number_of_edges(), density=nx.density(G), deg_cv=deg_cv(G),
               hc=has_hc(G), modularity=modularity(G), isolates=nx.number_of_isolates(G),
               triangles=sum(nx.triangles(G).values()) // 3)
    cvs, mods, dens, hcs = [], [], [], []
    for k in range(nperm):
        P = graph(permute(contents))
        cvs.append(deg_cv(P)); mods.append(modularity(P) if k < 500 else np.nan); dens.append(nx.density(P))
        if k < hc_perm:
            hcs.append(has_hc(P))
    cvs = np.array(cvs); mods = np.array(mods); mods = mods[~np.isnan(mods)]
    obs.update(p_degcv_lower=float((cvs <= obs["deg_cv"]).mean()), null_degcv_mean=float(cvs.mean()),
               p_mod_higher=float((mods >= obs["modularity"]).mean()), null_mod_mean=float(mods.mean()),
               null_density_mean=float(np.mean(dens)),
               null_hc_rate=float(np.mean([h is True for h in hcs])))
    return obs


contents = [t["content"] for t in nodes]
ring = ring_stats(contents)
G = graph(contents)
ring["degrees"] = {nodes[i]["type"]: d for i, d in G.degree()}
ring["components"] = [[nodes[i]["type"] for i in c] for c in nx.connected_components(G)]
H1c = bool(ring["hc"] is True and ring["p_degcv_lower"] < 0.05)
print({k: v for k, v in ring.items() if k not in ("degrees",)})

# planted ring power
pw_hits, plant_cvp = 0, []
for rep in range(100):
    order = list(RNG.permutation(len(contents)))
    pc = [list(c) for c in contents]
    for a, i in enumerate(order):
        j = order[(a + 1) % len(order)]
        tok = f"R{a}"
        for node in (i, j):
            if len(pc[node]) >= 2 + sum(1 for s in pc[node] if s.startswith("R")) and RNG.random() < 1.0:
                cand = [k for k, s in enumerate(pc[node]) if not s.startswith("R")]
                pc[node][RNG.choice(cand)] = tok
            else:
                pc[node].append(tok)
    st = ring_stats(pc, nperm=200, hc_perm=0)
    plant_cvp.append(st["p_degcv_lower"])
    pw_hits += bool(st["hc"] is True and st["p_degcv_lower"] < 0.05)
ring["planted_power"] = pw_hits / 100
ring["planted_median_p_degcv"] = float(np.median(plant_cvp))
print(f"H1c planted ring power={ring['planted_power']:.2f} (median degree-CV p {ring['planted_median_p_degcv']:.3f})")
R["H1c_ring"] = ring

# ---------------- H1d numerals as position / H2 ----------------
print("\n=== numerals ===")
numtypes = []
for t in types:
    vals = sorted({NUM[s] for s in t["seq"] if s in NUM})
    t["numvals"] = vals
    t["numtoks"] = [s for s in t["seq"] if s in NUM]
    if vals:
        numtypes.append(t)


def collisions(valsets):
    c = 0
    for a, b in itertools.combinations(valsets, 2):
        c += bool(set(a) & set(b))
    return c


obs_col = collisions([t["numvals"] for t in numtypes])
slots = [len(t["numtoks"]) for t in numtypes]
pool = [NUM[s] for t in numtypes for s in t["numtoks"]]
null = []
for _ in range(10000):
    p = list(RNG.permutation(pool)); i = 0; vs = []
    for k in slots:
        vs.append(sorted(set(p[i:i + k]))); i += k
    null.append(collisions(vs))
null = np.array(null)
allv = sorted({v for t in numtypes for v in t["numvals"]})
m = 0
while m + 1 in allv:
    m += 1
H1d_p = float((null <= obs_col).mean())
H1d = bool(H1d_p < 0.05 and m >= 4)
R["H1d_numerals"] = dict(types_with_numeral=len(numtypes), of_types=len(types), values=allv,
                         per_type={t["type"]: t["numtoks"] for t in numtypes}, collisions=obs_col,
                         null_mean=float(null.mean()), p_low=H1d_p, contiguous_run_from_1=m, pass_=H1d)
print(R["H1d_numerals"])

# H2a minimal pairs
pairs = []
leg = [(t["type"], t["seq"]) for t in types]
for (a, A), (b, B) in itertools.combinations(leg, 2):
    if len(A) == len(B):
        d = [(x, y) for x, y in zip(A, B) if x != y]
        if len(d) == 1:
            pairs.append((a, b, d[0]))
ctoks = [s for t in types for s in t["content"]]
pnum = np.mean([s in NUM or s in UNIT for s in ctoks])
pexp = 1 - (1 - pnum) ** 2
k = sum(1 for _, _, (x, y) in pairs if x in NUM or y in NUM or x in UNIT or y in UNIT)
H2a_p = float(stats.binomtest(k, len(pairs), pexp, alternative="greater").pvalue) if pairs else 1.0
R["H2a_minimal_pairs"] = dict(pairs=[f"{a}~{b}:{x}/{y}" for a, b, (x, y) in pairs], n_pairs=len(pairs),
                              numeral_pairs=k, p_numeral_token=float(pnum), expected_share=float(pexp), p=H2a_p)
H2a = bool(H2a_p < 0.05)
print(R["H2a_minimal_pairs"])

# H2c value vs frequency
vv = [(max(t["numvals"]), t["n_est"]) for t in numtypes]
rho, p = stats.spearmanr([a for a, _ in vv], [b for _, b in vv]) if len(vv) >= 4 else (np.nan, 1.0)
R["H2c_value_frequency"] = dict(n=len(vv), rho=float(rho), p=float(p), pairs=vv)
H2c = bool(p < 0.05)
print(R["H2c_value_frequency"])

# ---------------- H3 ----------------
print("\n=== H3 amulets ===")
m77pic = [(t["type"], t["pic"]) for t in tabs if t["source"] == "M77" and t["pic"] and t["type"]]


def modal_cov(pairs_):
    by = defaultdict(Counter)
    for ty, p in pairs_:
        by[ty][p] += 1
    num = den = 0
    for c in by.values():
        if sum(c.values()) >= 2:
            num += max(c.values()); den += sum(c.values())
    return num / den if den else np.nan, den


cov_obs, den = modal_cov(m77pic)
tys = [a for a, _ in m77pic]; ps = [b for _, b in m77pic]
nullc = np.array([modal_cov(list(zip(tys, RNG.permutation(ps))))[0] for _ in range(10000)])
H3a_p = float((nullc >= cov_obs).mean())
H3a = bool(cov_obs >= 0.80 and H3a_p < 0.05)
R["H3a_fixed_pairing"] = dict(modal_coverage=cov_obs, pictured_objects=den, null_mean=float(nullc.mean()), p=H3a_p,
                              pass_=H3a)
print(R["H3a_fixed_pairing"])


def seal_class(fs):
    d = fs // 10
    if fs in (131, 132, 133, 134, 135): return "goat-antelope arching"
    if fs in (136, 137, 138, 139): return "goat-antelope twirled"
    return {1: "unicorn", 3: "zebu", 4: "bull", 6: "buffalo", 7: "elephant", 9: "tiger", 10: "horned tiger",
            11: "rhinoceros", 14: "ox-antelope", 16: "hare", 25: "two-headed/composite", 29: "two-headed/composite",
            30: "two-headed/composite", 31: "two-headed/composite", 35: "bull", 52: "horned archer personage",
            86: "endless knot", 95: "double-axe"}.get(d)


seals = {}
for r in m77_lines():
    if r["object_type"] == "seal" and r.get("fs80"):
        seals[r["text_no"]] = r["fs80"]
seal_c = Counter(c for c in (seal_class(f) for f in seals.values()) if c)
cop_c = Counter(t["pic"] for t in tabs if t["source"] == "M77" and t["pic"])
classes = sorted(set(seal_c) | set(cop_c))
x = [cop_c[c] for c in classes]; y = [seal_c[c] for c in classes]
rho3, p3 = stats.spearmanr(x, y)
p3_one = float(p3 / 2 if rho3 > 0 else 1 - p3 / 2)
cl2 = [c for c in classes if c != "unicorn"]
rho3b, p3b = stats.spearmanr([cop_c[c] for c in cl2], [seal_c[c] for c in cl2])
uni_share = (cop_c["unicorn"] / sum(cop_c.values()), seal_c["unicorn"] / sum(seal_c.values()))
H3b = bool(rho3 > 0 and p3_one < 0.05)
R["H3b_popularity"] = dict(classes={c: dict(copper=cop_c[c], seals=seal_c[c]) for c in classes}, rho=float(rho3),
                           p_one_sided=p3_one, rho_without_unicorn=float(rho3b), p_without_unicorn=float(p3b),
                           unicorn_share_copper=uni_share[0], unicorn_share_seals=uni_share[1], pass_=H3b)
print(R["H3b_popularity"])

# H3c picture-text
pt = [t for t in types if t["picture"]]


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def same_diff(labels):
    s, d = [], []
    for i, j in itertools.combinations(range(len(pt)), 2):
        (s if labels[i] == labels[j] else d).append(jac(pt[i]["content"], pt[j]["content"]))
    return (np.mean(s) if s else np.nan) - np.mean(d), len(s)


labs = [t["picture"] for t in pt]
obs3, nsame = same_diff(labs)
null3 = np.array([same_diff(list(RNG.permutation(labs)))[0] for _ in range(5000)])
null3 = null3[~np.isnan(null3)]
H3c_p = float((null3 >= obs3).mean())
R["H3c_picture_text"] = dict(n_types=len(pt), same_pairs=nsame, diff_jaccard=float(obs3), null_mean=float(null3.mean()),
                             p=H3c_p)
H3c = bool(H3c_p < 0.05)
print(R["H3c_picture_text"])

# ---------------- verdicts ----------------
ps_ = dict(H1a=None, H1b=None, H1c=ring["p_degcv_lower"], H1d=H1d_p, H2a=H2a_p,
           H2b=min(v["p_ge"] for v in RE["full"]["uniform"].values()), H2c=float(p), H3a=H3a_p, H3b=p3_one, H3c=H3c_p)
passes = dict(H1a=H1a, H1b=H1b, H1c=H1c, H1d=H1d, H2a=H2a, H2b=H2b, H2c=H2c, H3a=H3a, H3b=H3b, H3c=H3c)
H1 = "supported" if (H1a and H1b and H1c) else ("refuted" if (not H1b and ring["p_degcv_lower"] >= 0.05 and
                                                              ring["planted_power"] >= 0.5) else "inconclusive")
H2_refute = (not H2a) and len(numtypes) / len(types) < 0.25
H2 = "supported" if (H2a and H2b) else ("refuted" if H2_refute else "inconclusive")
H3 = "supported" if (H3a and H3b) else ("type emblem (H3a only)" if H3a else "inconclusive")
R["tests"] = dict(passes=passes, p=ps_, bonferroni_alpha=0.005, verdicts=dict(H1=H1, H2=H2, H3=H3))
print("\nPASSES", passes); print("VERDICTS", R["tests"]["verdicts"])
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
