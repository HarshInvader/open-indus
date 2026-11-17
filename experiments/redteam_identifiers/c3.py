"""Red team C3: is the S4 'no repulsion' null informative?
C3a detectable effect, C3b planted repulsion among small sets of contemporaries inside each bin,
C3c positive control: same statistic + null A on Ur III personal seal legends (bins prov+reign; exploratory
prov+reign+year).

usage: .venv/bin/python experiments/redteam_identifiers/c3.py {a|b5|b10|c} [reps] [nperm]
"""
import sys, os, json, csv, re
from collections import Counter, defaultdict
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "experiments/identifiers"))
from id_lib import *  # noqa
import s4  # read-only import of identifiers' S4 code

HERE = os.path.dirname(os.path.abspath(__file__))


def c3a():
    U = s4.dedupe(s4.units_icit("seal")); G = s4.make_groups(U)
    r = json.load(open(os.path.join(ROOT, "experiments/identifiers/s4_icit.json")))["icit-seal"]
    mu, sd = r["A"]["null_mean"]["nn"], r["A"]["null_sd"]["nn"]
    near = []; nn = []
    for g, T in G.items():
        T = sorted(set(T))
        for i, a in enumerate(T):
            d = min(ned(a, b) for j, b in enumerate(T) if j != i); nn.append(d); near.append(d < 0.5)
    sizes = sorted((len(set(T)) for T in G.values()), reverse=True)
    out = dict(null_mean_nn=mu, null_sd_nn=sd, mde_abs=2.5 * sd, mde_rel=2.5 * sd / mu,
               share_nn_below_0p5=float(np.mean(near)), n_units=len(nn),
               max_effect_if_all_near_pairs_pushed_to_0p5=float(np.mean(np.maximum(nn, 0.5)) - np.mean(nn)),
               top2_weight=sum(sizes[:2]) / sum(sizes), sizes=sizes,
               observed_shift=r["obs"]["nn"] - mu)
    print("C3a", out)
    return out


def planted_local(U, h, rng, d=0.5):
    """Each bin is split at random into 'contemporary sets' of size h; members of a set are redrawn from the
    site pool rejecting any candidate within NED<d of a member of the same set (strength 1). Bins keep sizes."""
    by = defaultdict(list)
    for s, g, t in U: by[s].append((g, t))
    out = []
    for s, items in by.items():
        pool = [t for _, t in items]; sizes = Counter(g for g, _ in items)
        avail = list(rng.permutation(len(pool)))
        for g, k in sizes.items():
            mem_all = []
            while len(mem_all) < k and avail:
                m = min(h, k - len(mem_all)); setm = []; tries = 0
                while len(setm) < m and avail:
                    j = avail[tries % len(avail)]; t = pool[j]; tries += 1
                    if any(ned(t, x) < d for x in setm) and tries < 50 * m: continue
                    setm.append(t); avail.remove(j)
                mem_all += setm
            out += [(s, g, t) for t in mem_all]
    return out


def c3b(h, reps=30, nperm=200):
    U = s4.dedupe(s4.units_icit("seal")); rng = np.random.default_rng(17); hits = 0; ps = []
    for r in range(reps):
        P = planted_local(U, h, rng)
        res = s4.run(P, nperm=nperm, seed=300 + r, nulls=("A",))
        p = res["A"]["p_repel"]["nn"]; ps.append(p); hits += p < 0.05
        print(f"h={h} rep {r} p={p:.3f} z={res['A']['z']['nn']:+.2f}", flush=True)
    out = dict(h=h, reps=reps, nperm=nperm, power=hits / reps, p=ps)
    print("C3b", out)
    return out


# ------------------------------------------------------------------ C3c Ur III positive control
def cun_signs(word):
    dets = re.findall(r"\{[^}]*\}", word)
    rest = re.sub(r"\{[^}]*\}", "-", word)
    return dets + [p for p in re.split(r"[-.+]", rest) if p]


REIGN = {"šū-suen": "SS", "su-suen": "SS", "shu-suen": "SS", "amar-suen": "AS", "amar-sin": "AS", "šulgi": "SH",
         "shulgi": "SH", "ibbi-suen": "IS", "ibbi-sin": "IS", "ibb-suen": "IS", "ibbisuen": "IS"}


def ur3_units(fine=False, cap=250, seed=0, nameline=False):
    csv.field_size_limit(10**9)
    date = {}
    with open(os.path.join(ROOT, "experiments/short_labels/raw/cdli/cdli_cat.csv"), encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit() and (r.get("period") or "").startswith("Ur III"):
                d = (r.get("date_of_origin") or "").strip().split(".")
                rg = REIGN.get(d[0].lower())
                if rg:
                    yr = d[1] if len(d) > 1 and d[1].isdigit() and int(d[1]) > 0 else None
                    date["P" + pid.zfill(6)] = (rg, yr)
    occ = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/identifiers/data/ur3_occ.jsonl"))]
    KINGS = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}szul-gi", "{d}i-bi2-{d}suen", "ur-{d}namma", "{d}szul-gi-ra"}
    royal = lambda lg: any(w in KINGS or w == "lugal" for l in lg for w in l)
    seen = set(); B = defaultdict(set)
    for u in occ:
        if u["pid"] not in date or not u["seal_id"] or u["prov"] in ("uncertain", ""): continue
        rg, yr = date[u["pid"]]
        if fine and yr is None: continue
        if nameline and royal(u["legend"]): continue
        g = f"{u['prov']}-{rg}" + (f"-{yr}" if fine else "")
        sid = u["seal_id"].split()[0].split(".")[0]
        if (g, sid) in seen: continue
        seen.add((g, sid))
        lines = u["legend"][:1] if nameline else u["legend"]
        B[(u["prov"], g)].add(tuple(s for l in lines for w in l for s in cun_signs(w)))
    rng = np.random.default_rng(seed); U = []
    for (p, g), T in B.items():
        T = sorted(T)
        if len(T) > cap: T = [T[i] for i in sorted(rng.choice(len(T), cap, replace=False))]
        U += [(p, g, t) for t in T]
    return U


def c3c(nperm=500):
    out = {}
    for label, kw in (("reign_legend", {}), ("year_legend", {"fine": True}),
                      ("reign_nameline", {"nameline": True}), ("year_nameline", {"fine": True, "nameline": True})):
        U = ur3_units(**kw)
        r = s4.run(U, nperm=nperm, seed=5, label="UrIII-" + label, nulls=("A",))
        s4.show(r); out[label] = r
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    nperm = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    if mode == "a": res = c3a()
    elif mode.startswith("b"): res = c3b(int(mode[1:]), reps, nperm)
    elif mode == "c": res = c3c(nperm if len(sys.argv) > 3 else 500)
    json.dump(res, open(os.path.join(HERE, f"c3_{mode}.json"), "w"), indent=1, default=float)
