"""S3 unseen-species estimation of how many distinct texts existed (seals vs tablets), with out-of-sample
calibration of the estimator. Species = distinct object text (also: its core, its frame skeleton).

usage: .venv/bin/python experiments/identifiers/s3.py {dev|confirm}
  dev     : M77 dev objects only (exploration; written before the prereg).
  confirm : M77 held-out, ICIT (full), ICIT-only checks (HARP vs Vats Harappa; new sites vs old), Ur III.
"""
import sys, json
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from id_lib import *  # noqa

CLASSES = ("seal", "sealing", "moulded_tablet", "tablet", "incised_tablet", "copper_tablet")
MIN_N = 20
OLD_SITES = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}


def keyfn(kind):
    if kind == "text": return lambda o: o["sp"]
    if kind == "core": return lambda o: core_key(flat(o["sp"]))
    if kind == "frame": return lambda o: frame_key(flat(o["sp"]))


def table(objs, label, kinds=("text", "core", "frame"), boot=True):
    rows = []
    cells = defaultdict(list)
    for o in objs:
        if o["complete"] and o["cls"] in CLASSES: cells[(o["site"], o["cls"])].append(o)
    for (site, cls), X in sorted(cells.items(), key=lambda kv: -len(kv[1])):
        if len(X) < MIN_N: continue
        for kind in kinds:
            if kind != "text" and cls != "seal": continue
            f = keyfn(kind)
            d = summarize(list(Counter(f(o) for o in X).values()), boot=boot)
            d.update(dataset=label, site=site, cls=cls, kind=kind)
            rows.append({k: (float(v) if isinstance(v, (np.floating, np.integer)) else v) for k, v in d.items()})
    return rows


def show(rows):
    for d in rows:
        ci = d.get("cov_ci", [np.nan, np.nan])
        print(f"{d['dataset']:10s} {d['site']:13s} {d['cls']:15s} {d['kind']:5s} n={d['n']:5.0f} S={d['S']:5.0f} f1={d['f1']:5.0f} f2={d['f2']:4.0f} "
              f"chao1={d['chao1']:8.0f} ace={d['ace']:8.0f} S2n/S={d['S_2n']/d['S']:.2f} new_rate={d['new_rate']:.3f} cov=[{ci[0]:.2f},{ci[1]:.2f}]")


def seal_vs_tablet(rows, dataset):
    """P1: within a site, seal new-text rate minus tablet new-text rate, bootstrap CI."""
    out = []
    by = {(d["site"], d["cls"]): d for d in rows if d["dataset"] == dataset and d["kind"] == "text"}
    for (site, cls), d in by.items():
        if cls == "seal" or (site, "seal") not in by: continue
        s = by[(site, "seal")]
        out.append(dict(dataset=dataset, site=site, control=cls, seal_new=s["new_rate"], ctrl_new=d["new_rate"],
                        diff=s["new_rate"] - d["new_rate"],
                        separated=bool((1 - s["cov_ci"][1]) > (1 - d["cov_ci"][0])) if "cov_ci" in s and "cov_ci" in d else None))
    return out


def match_test(ref_objs, tgt_objs, kind, label, B=500, seed=0):
    """Out-of-sample prediction: P(target object's species already in reference) predicted = coverage of the
    reference (if target is a fresh draw from the same population). Returns observed vs predicted + 95% PI
    (bootstrap of reference coverage + binomial sampling of targets)."""
    f = keyfn(kind)
    ref = [f(o) for o in ref_objs]; tgt = [f(o) for o in tgt_objs]
    if len(ref) < 5 or len(tgt) < 5: return None
    ab = list(Counter(ref).values()); C = coverage(ab)
    seen = set(ref); obs = sum(t in seen for t in tgt) / len(tgt)
    rng = np.random.default_rng(seed)
    lo_hi = boot_ci(ab, coverage, B=200, seed=seed)
    sims = []
    cs = rng.uniform(lo_hi[0], lo_hi[1], B)
    for c in cs: sims.append(rng.binomial(len(tgt), min(max(c, 0), 1)) / len(tgt))
    pi = np.percentile(sims, [2.5, 97.5]).tolist()
    return dict(label=label, kind=kind, n_ref=len(ref), n_tgt=len(tgt), pred_match=C, pred_new=1 - C,
                obs_match=obs, obs_new=1 - obs, pi_match=pi, R=obs / C if C > 0 else float("nan"),
                calibrated=bool(pi[0] <= obs <= pi[1]))


def species_subset_pi(dev_ab, n_target, B=1000, seed=0):
    """V1: held-out = random subset of species (family split). PI of its new-text rate (1 - coverage) from
    random species subsets of the dev abundance list with about n_target objects."""
    rng = np.random.default_rng(seed); ab = np.array(dev_ab); vals = []
    for _ in range(B):
        perm = rng.permutation(len(ab)); cs = np.cumsum(ab[perm]); k = int(np.searchsorted(cs, n_target)) + 1
        vals.append(1 - coverage(ab[perm[:k]]))
    return np.percentile(vals, [2.5, 97.5]).tolist(), float(np.mean(vals))


def ur3():
    U = [json.loads(l) for l in open(OUT / "data/ur3_occ.jsonl")]
    KINGS = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}szul-gi", "{d}i-bi2-{d}suen", "ur-{d}namma", "{d}szul-gi-ra"}
    def royal(lg): return any(w in KINGS or w == "lugal" for l in lg for w in l)
    rows = []
    provs = [p for p, c in Counter(u["prov"] for u in U).most_common() if c >= 100 and p != "uncertain"]
    for p in provs:
        X = [u for u in U if u["prov"] == p]
        imp = Counter(json.dumps(u["legend"]) for u in X)
        d = summarize(list(imp.values())); d.update(dataset="UrIII", site=p, cls="impression", kind="legend"); rows.append(d)
        # one record per catalogued seal (base S-number): physical-seal analog (partly circular: CDLI numbers seals by legend)
        seals = {}
        for u in X:
            sid = u["seal_id"].split()[0].split(".")[0] if u["seal_id"] else None
            if sid: seals[sid] = u["legend"]
        d = summarize(list(Counter(json.dumps(v) for v in seals.values()).values()))
        d.update(dataset="UrIII", site=p, cls="seal(base id)", kind="legend"); rows.append(d)
        nr = [v for v in seals.values() if not royal(v)]
        d = summarize(list(Counter(json.dumps(v[0]) for v in nr).values()))
        d.update(dataset="UrIII", site=p, cls="seal(base id)", kind="name line"); rows.append(d)
    rows = [{k: (float(v) if isinstance(v, (np.floating, np.integer)) else v) for k, v in d.items()} for d in rows]
    # cross-archive locality (P3 reference). Impression level, catalogued-seal level, non-royal name line.
    cross = []
    recs = {}
    for p in provs:
        seals = {}
        for u in U:
            if u["prov"] != p or not u["seal_id"]: continue
            seals[u["seal_id"].split()[0].split(".")[0]] = u["legend"]
        recs[p] = {"imp": [{"sp": json.dumps(u["legend"])} for u in U if u["prov"] == p],
                   "seal": [{"sp": json.dumps(v)} for v in seals.values()],
                   "name": [{"sp": json.dumps(v[0])} for v in seals.values() if not royal(v)]}
    for lvl in ("imp", "seal", "name"):
        for a in provs:
            for b in provs:
                if a == b: continue
                r = match_test(recs[b][lvl], recs[a][lvl], "text", f"UrIII {lvl} {a}->{b}")
                if r: r["level"] = lvl; cross.append(r)
    return rows, cross


def main(mode):
    R = {}
    if mode == "dev":
        rows = table(m77_objects("dev"), "M77dev"); show(rows)
        R["table"] = rows; R["p1"] = seal_vs_tablet(rows, "M77dev")
        for x in R["p1"]: print("P1", x)
        O = [o for o in m77_objects("dev") if o["complete"] and o["cls"] == "seal"]
        R["cross"] = []
        for kind in ("text", "core", "frame"):
            for ref_site in ("Mohenjo-daro", "Harappa"):
                for t in ("Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro"):
                    if t == ref_site: continue
                    r = match_test([o for o in O if o["site"] == ref_site], [o for o in O if o["site"] == t], kind,
                                   f"M77dev seal {t}->{ref_site}")
                    if r: R["cross"].append(r); print(f"{r['label']:40s} {kind:5s} obs_match={r['obs_match']:.3f} pred={r['pred_match']:.3f} PI={r['pi_match'][0]:.3f}-{r['pi_match'][1]:.3f} R={r['R']:.2f}")
    else:
        # ---- tables
        rows = table(m77_objects("heldout"), "M77ho") + table(m77_objects(), "M77all") + table(icit_objects(), "ICIT")
        show(rows); R["table"] = rows
        R["p1"] = seal_vs_tablet(rows, "M77ho") + seal_vs_tablet(rows, "ICIT")
        for x in R["p1"]: print("P1", x)
        # ---- V1 dev -> held-out (species-subset prediction of the held-out new-text rate)
        dev = m77_objects("dev"); ho = m77_objects("heldout"); R["v1"] = []
        for site in ("Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"):
            for cls in CLASSES:
                Xd = [o for o in dev if o["complete"] and o["site"] == site and o["cls"] == cls]
                Xh = [o for o in ho if o["complete"] and o["site"] == site and o["cls"] == cls]
                if len(Xd) < MIN_N or len(Xh) < 10: continue
                pi, mu = species_subset_pi(list(Counter(o["sp"] for o in Xd).values()), len(Xh))
                obs = 1 - coverage(list(Counter(o["sp"] for o in Xh).values()))
                v = dict(site=site, cls=cls, n_dev=len(Xd), n_ho=len(Xh), pred_new=mu, pi=pi, obs_new=obs,
                         calibrated=bool(pi[0] <= obs <= pi[1]))
                R["v1"].append(v); print("V1", v)
        # ---- V2 ICIT-only by date: HARP Harappa objects vs pre-1977 (Vats/Wheeler) Harappa objects
        I = [o for o in icit_objects() if o["complete"]]
        R["v2"] = []
        for cls in ("seal", "moulded_tablet", "incised_tablet"):
            ref = [o for o in I if o["site"] == "Harappa" and not harp(o) and o["cls"] == cls]
            tgt = [o for o in I if harp(o) and o["cls"] == cls]
            for kind in (("text", "core", "frame") if cls == "seal" else ("text",)):
                r = match_test(ref, tgt, kind, f"V2 HARP<-Vats {cls}")
                if r: R["v2"].append(r); print(r)
        # ---- V3 / P2 ICIT-only sites: new-site seals vs the five old sites' seals (one shared population?)
        R["v3"] = []
        old = [o for o in I if o["site"] in OLD_SITES and o["cls"] == "seal"]
        new = [o for o in I if o["site"] not in OLD_SITES and o["site"] != "Unknown" and o["cls"] == "seal"]
        for kind in ("text", "core", "frame"):
            r = match_test(old, new, kind, "V3 newsites<-oldsites seal")
            if r: R["v3"].append(r); print(r)
            for t in ("Dholavira",):
                r = match_test(old, [o for o in new if o["site"] == t], kind, f"V3 {t}<-oldsites seal")
                if r: R["v3"].append(r); print(r)
        # ---- P2 cross-site among old sites (ICIT): target site vs reference MD / Harappa, seals
        R["cross"] = []
        S = [o for o in I if o["cls"] == "seal"]
        for kind in ("text", "core", "frame"):
            for ref_site in ("Mohenjo-daro", "Harappa"):
                for t in ("Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira"):
                    if t == ref_site: continue
                    r = match_test([o for o in S if o["site"] == ref_site], [o for o in S if o["site"] == t], kind,
                                   f"ICIT seal {t}->{ref_site}")
                    if r: R["cross"].append(r); print(f"{r['label']:40s} {kind:5s} obs={r['obs_match']:.3f} pred={r['pred_match']:.3f} PI={r['pi_match'][0]:.3f}-{r['pi_match'][1]:.3f} R={r['R']:.2f}")
        # ---- Ur III reference
        rows3, cross3 = ur3(); show(rows3); R["ur3"] = rows3; R["ur3_cross"] = cross3
        for r in cross3: print(f"{r['label']:40s} obs={r['obs_match']:.3f} pred={r['pred_match']:.3f} R={r['R']:.2f}")
    json.dump(R, open(OUT / f"s3_{mode}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1])
