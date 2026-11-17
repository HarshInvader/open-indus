"""S4 identifier repulsion. Are texts co-found at one site+group (M77 locus / ICIT period) more mutually
distinct than (A) texts of the same site and class drawn into the same group sizes, (B) slot-matched
recombinations of the site's own frames and cores?

usage: .venv/bin/python experiments/identifiers/s4.py {dev|heldout|icit|icit_harp|power} [nperm]
"""
import sys, json, itertools
from collections import defaultdict, Counter
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from id_lib import *  # noqa

MINK = 3
M = ["nn", "pw", "shared", "sh_norm"]


def units_m77(subset, cls):
    U = []
    for o in m77_objects(subset):
        if o["cls"] != cls or not o["complete"] or not o["locus"]: continue
        U.append((o["site"], f"{o['site']}-L{o['locus']}", flat(o["sp"])))
    return U


def units_icit(cls, only_harp=False):
    U = []
    for o in icit_objects():
        if o["cls"] != cls or not o["complete"]: continue
        if only_harp and not harp(o): continue
        g = icit_group(o)
        if g is None: continue
        U.append((o["site"], g, flat(o["sp"])))
    return U


def dedupe(U):
    return sorted(set(U))


def group_stats(texts, cache):
    """texts: list of distinct flat tuples in one group -> (NN mean NED, pairwise mean NED, pairwise mean shared)."""
    k = len(texts)
    D = np.zeros((k, k)); S = np.zeros((k, k)); SN = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            key = (texts[i], texts[j]) if texts[i] < texts[j] else (texts[j], texts[i])
            v = cache.get(key)
            if v is None:
                v = (ned(*key), shared(*key), shared(*key) / min(len(key[0]), len(key[1]))); cache[key] = v
            D[i, j] = D[j, i] = v[0]; S[i, j] = S[j, i] = v[1]; SN[i, j] = SN[j, i] = v[2]
    iu = np.triu_indices(k, 1)
    Dn = D + np.eye(k) * 9
    return Dn.min(1).mean(), D[iu].mean(), S[iu].mean(), SN[iu].mean()


def pooled(groups, cache):
    """groups: dict g -> list of distinct texts (k>=MINK). Weighted by k."""
    W = 0; acc = np.zeros(4)
    for g, T in groups.items():
        T = sorted(set(T))
        if len(T) < MINK: continue
        acc += len(T) * np.array(group_stats(T, cache)); W += len(T)
    return acc / W if W else np.full(4, np.nan), W


def make_groups(U):
    G = defaultdict(list)
    for site, g, t in U: G[g].append(t)
    return {g: T for g, T in G.items() if len(set(T)) >= MINK}


def null_A(U, rng):
    """permute group labels among units of the same site (units = distinct (group,text) pairs)."""
    by = defaultdict(list)
    for i, (s, g, t) in enumerate(U): by[s].append(i)
    G = [u[1] for u in U]; G2 = list(G)
    for s, idx in by.items():
        perm = rng.permutation(idx)
        for a, b in zip(idx, perm): G2[a] = G[b]
    return [(U[i][0], G2[i], U[i][2]) for i in range(len(U))]


def null_B(U, rng):
    """slot-matched recombination: keep each text's frame skeleton, refill its core slots with core strings
    drawn (without replacement) from texts of the same site with the same number of slots."""
    out = list(U)
    dec = [decompose(t) for _, _, t in U]
    by = defaultdict(list)
    for i, (s, g, t) in enumerate(U): by[(s, len(dec[i][1]))].append(i)
    for (s, ns), idx in by.items():
        if ns == 0: continue
        perm = rng.permutation(idx)
        for a, b in zip(idx, perm):
            skel = dec[a][0]; cores = list(dec[b][1]); it = iter(cores); new = []
            for x in skel:
                new.extend(next(it) if x == "X" else (x,))
            out[a] = (U[a][0], U[a][1], tuple(new))
    return out


def run(U, nperm=1000, seed=1, label="", nulls=("A", "B")):
    U = dedupe(U)
    rng = np.random.default_rng(seed); cache = {}
    groups = make_groups(U)
    keep = set(groups)
    # only sites that have >=1 eligible group contribute units (null draws within site)
    sites = {u[0] for u in U if u[1] in keep}
    U = [u for u in U if u[0] in sites]
    obs, W = pooled(groups, cache)
    res = {"label": label, "n_units": len(U), "n_groups": len(groups), "weight": W,
           "groups": {g: len(set(T)) for g, T in groups.items()},
           "obs": dict(zip(M, obs.tolist()))}
    for name, fn in (("A", null_A), ("B", null_B)):
        if name not in nulls: continue
        vals = []
        for _ in range(nperm):
            U2 = fn(U, rng)
            G2 = defaultdict(list)
            for s, g, t in U2:
                if g in keep: G2[g].append(t)
            vals.append(pooled(G2, cache)[0])
        vals = np.array(vals)
        mu, sd = vals.mean(0), vals.std(0) + 1e-12
        # repulsion = larger distances (nn, pw) / fewer shared signs
        sgn = np.array([1, 1, -1, -1])  # repulsion = larger distance, fewer shared signs
        p_rep = [(1 + np.sum(sgn[c] * vals[:, c] >= sgn[c] * obs[c])) / (nperm + 1) for c in range(4)]
        p_clu = [(1 + np.sum(sgn[c] * vals[:, c] <= sgn[c] * obs[c])) / (nperm + 1) for c in range(4)]
        res[name] = {"null_mean": dict(zip(M, mu.tolist())),
                     "z": dict(zip(M, ((obs - mu) / sd).tolist())),
                     "d_rel": dict(zip(M, ((obs - mu) / mu).tolist())),
                     "p_repel": dict(zip(M, p_rep)),
                     "p_cluster": dict(zip(M, p_clu)),
                     "null_sd": dict(zip(M, sd.tolist()))}
    return res


def show(r):
    print(f"{r['label']}: units={r['n_units']} groups={r['n_groups']} weight={r['weight']}  obs nn={r['obs']['nn']:.3f} pw={r['obs']['pw']:.3f} sh={r['obs']['shared']:.3f}")
    for n in ("A", "B"):
        if n not in r: continue
        x = r[n]
        print(f"   null {n}: nn {x['null_mean']['nn']:.3f} z={x['z']['nn']:+.2f} p_rep={x['p_repel']['nn']:.3f} p_clu={x['p_cluster']['nn']:.3f} | "
              f"pw {x['null_mean']['pw']:.3f} z={x['z']['pw']:+.2f} | sh {x['null_mean']['shared']:.3f} z={x['z']['shared']:+.2f} p_rep={x['p_repel']['shared']:.3f} | shn z={x['z']['sh_norm']:+.2f} p_rep={x['p_repel']['sh_norm']:.3f}")


# ---------------------------------------------------------------- power (planted repulsion / clustering)
def planted(U, mode, strength, rng, d=0.5):
    """Rebuild each site's groups (same sizes) by sequential draws from the site's pool. 'repel': reject a
    candidate within NED<d of a current member with prob=strength; 'cluster': accept a candidate only if
    within NED<d of a member with prob=strength (first member free)."""
    by = defaultdict(list)
    for s, g, t in U: by[s].append((g, t))
    out = []
    for s, items in by.items():
        pool = [t for _, t in items]; sizes = Counter(g for g, _ in items)
        avail = list(rng.permutation(len(pool)))
        for g, k in sizes.items():
            mem = []
            tries = 0
            while len(mem) < k and avail:
                j = avail[tries % len(avail)]; t = pool[j]; tries += 1
                close = any(ned(t, m) < d for m in mem)
                if mode == "repel" and close and rng.random() < strength and tries < 50 * k: continue
                if mode == "cluster" and mem and not close and rng.random() < strength and tries < 50 * k: continue
                mem.append(t); avail.remove(j)
            out += [(s, g, t) for t in mem]
    return out


def power(U, label, reps=40, nperm=200, settings=(("repel", 0.5), ("repel", 1.0), ("cluster", 0.5))):
    out = {}
    for mode, st in settings:
        hits = 0; rng = np.random.default_rng(7)
        for r in range(reps):
            P = planted(dedupe(U), mode, st, rng)
            res = run(P, nperm=nperm, seed=100 + r, nulls=("A",))
            p = res["A"]["p_repel" if mode == "repel" else "p_cluster"]["nn"]
            hits += p < 0.05
        out[f"{mode}_{st}"] = hits / reps
        print(label, mode, st, "power", hits / reps, flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]; nperm = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    R = {}
    if mode in ("dev", "heldout"):
        for cls in ("seal", "moulded_tablet", "tablet", "sealing", "copper_tablet"):
            U = units_m77(mode, cls)
            if len(make_groups(dedupe(U))) == 0: continue
            r = run(U, nperm, label=f"M77-{mode}-{cls}"); show(r); R[r["label"]] = r
    elif mode in ("icit", "icit_harp"):
        for cls in ("seal", "moulded_tablet", "incised_tablet", "sealing", "copper_tablet"):
            U = units_icit(cls, only_harp=(mode == "icit_harp"))
            if len(make_groups(dedupe(U))) == 0: continue
            r = run(U, nperm, label=f"{mode}-{cls}"); show(r); R[r["label"]] = r
    elif mode == "power":
        # usage: s4.py power 200 <dataset M77dev|ICIT|ICITmt> <repel|cluster> <strength>
        ds, pm, st = sys.argv[3], sys.argv[4], float(sys.argv[5])
        U = {"M77dev": lambda: units_m77("dev", "seal"), "ICIT": lambda: units_icit("seal"),
             "ICITmt": lambda: units_icit("moulded_tablet")}[ds]()
        R[ds] = power(U, ds, reps=30, nperm=nperm, settings=((pm, st),))
        mode = f"power_{ds}_{pm}_{st}"
    json.dump(R, open(OUT / f"s4_{mode}.json", "w"), indent=1)
