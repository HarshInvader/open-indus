"""Q3. Sealings (clay impressions = texts actually used on goods/doors). Which texts recur across sites?

ICIT TAG* = true sealings. (M77 'sealing' at Harappa/Mohenjo-daro is mostly moulded tablets = ICIT TAB:B,
so for M77 only Lothal/Kalibangan/other-site sealings are treated as sealings.)
1. For every distinct complete sealing text (no break): is the same text on a SEAL at the same site? at
   another site? on any object at another site?
2. Baseline: same rates for distinct complete seal texts, compared within length strata (exact stratified
   hypergeometric = permuting the sealing/seal label within length bins).
3. Texts found at >= 2 sites (any object; distinct per site): which signs / bigrams are enriched relative to
   single-site texts of the same length (exact stratified test, BH)? Replication on M77.
"""
from common import *

rng = np.random.default_rng(3)


def complete(seq):
    return "#" not in seq and len(signs(seq)) >= 2


def key(seq):
    return " ".join(signs(seq))


def site_index(recs, kind_fn):
    idx = defaultdict(lambda: defaultdict(set))  # text -> site -> kinds
    for r in recs:
        if "#" in r["seq"]: continue
        idx[key(r["seq"])][r["site"]].add(kind_fn(r))
    return idx


def main():
    R = {}
    I = icit_texts()
    kind = lambda r: "sealing" if r["type"].startswith("TAG") else "seal" if r["type"].startswith("SEAL") else "tablet" if r["type"].startswith("TAB") else "other"
    idx = site_index(I, kind)
    # 1-2: per distinct (site, text) unit
    units = {}
    for r in I:
        if not complete(r["seq"]): continue
        k = kind(r)
        if k not in ("sealing", "seal"): continue
        units.setdefault((k, r["site"], key(r["seq"])), r)
    rows = []
    for (k, site, txt), r in units.items():
        occ = idx[txt]
        same_seal = "seal" in occ[site] if k == "sealing" else False
        other = {s: v for s, v in occ.items() if s != site}
        rows.append(dict(kind=k, site=site, text=txt, L=len(txt.split()), same_site_seal=same_seal,
                         other_site=bool(other), other_site_seal=any("seal" in v for v in other.values()), other_sites=sorted(other)))
    sl = [r for r in rows if r["kind"] == "sealing"]
    se = [r for r in rows if r["kind"] == "seal"]
    print(f"ICIT complete distinct sealing texts (site-level): {len(sl)}; seal texts: {len(se)}")
    print(f"  sealing text also on a seal at the same site: {sum(r['same_site_seal'] for r in sl)} / {len(sl)}")
    print(f"  sealing text at another site (any object): {sum(r['other_site'] for r in sl)}; seal text at another site: {sum(r['other_site'] for r in se)} / {len(se)}")
    allr = sl + se
    x = np.array([r["other_site"] for r in allr], int); y = np.array([r["kind"] == "sealing" for r in allr], int)
    st = np.array([lenbin(r["L"]) for r in allr])
    obs, exp, ph, pl = strat_hypergeom_p(x, y, st)
    print(f"  cross-site recurrence, sealings vs seals (length-stratified exact): obs {obs} vs exp {exp:.1f}, p_hi={ph:.4f}, p_lo={pl:.4f}")
    R["icit_sealing_crosssite"] = dict(n_sealing=len(sl), n_seal=len(se), sealing_same_site_seal=sum(r["same_site_seal"] for r in sl),
                                       sealing_other_site=int(obs), expected=float(exp), p_hi=float(ph), p_lo=float(pl),
                                       seal_other_site=sum(r["other_site"] for r in se))
    R["icit_sealing_crosssite_list"] = [dict(site=r["site"], text=r["text"], other_sites=r["other_sites"]) for r in sl if r["other_site"]]
    for r in sl:
        if r["other_site"]: print(f"    sealing {r['site']:12s} {r['text']:35s} also at {r['other_sites']}")
    by_site = Counter(r["site"] for r in sl)
    R["icit_sealing_by_site"] = {s: dict(n=n, same_site_seal=sum(r["same_site_seal"] for r in sl if r["site"] == s),
                                         other_site=sum(r["other_site"] for r in sl if r["site"] == s)) for s, n in by_site.items()}
    print("  by site:", R["icit_sealing_by_site"])

    # 3. multi-site texts vs single-site: enrichment
    def multisite(recs, label, min_texts=6):
        idx = site_index(recs, lambda r: 1)
        txts = [(t, len(v)) for t, v in idx.items() if len(t.split()) >= 1]
        U = [dict(seq=t.split(), ms=int(n >= 2), L=len(t.split())) for t, n in txts]
        print(f"\n[{label}] distinct complete-text units {len(U)}, multi-site {sum(u['ms'] for u in U)}")
        ms_list = sorted([(t, sorted(idx[t].keys())) for t, n in txts if n >= 2], key=lambda z: -len(z[1]))
        for t, s in ms_list[:25]: print(f"    {t:40s} {s}")
        c = Counter(f for u in U for f in set(u["seq"]) | {" ".join(p) for p in zip(u["seq"], u["seq"][1:])})
        fs = [f for f, n in c.items() if n >= min_texts]
        fi = {f: i for i, f in enumerate(fs)}
        X = np.zeros((len(U), len(fs)))
        for i, u in enumerate(U):
            for f in set(u["seq"]) | {" ".join(p) for p in zip(u["seq"], u["seq"][1:])}:
                if f in fi: X[i, fi[f]] = 1
        y = np.array([u["ms"] for u in U]); st = np.array([lenbin(u["L"]) for u in U])
        obs, exp, ph, pl = strat_hyper_matrix(X, y, st, 2)
        p = np.minimum(1, 2 * np.minimum(ph[1], pl[1])); q = bh(p)
        out = []
        for b in np.argsort(p)[:20]:
            out.append(dict(feat=fs[b], obs=int(obs[1, b]), exp=float(exp[1, b]), total=int(X[:, b].sum()), p=float(p[b]), q=float(q[b])))
        print(f"  {len(fs)} features tested; BH q<0.05: {int((q < 0.05).sum())}")
        for o in out[:12]:
            print(f"    {o['feat']:12s} in multi-site texts {o['obs']:3d} vs exp {o['exp']:5.1f} (in {o['total']} texts) p={o['p']:.2g} q={o['q']:.2g}")
        return dict(n=len(U), n_multi=int(y.sum()), n_tests=len(fs), top=out, multi_texts=[dict(text=t, sites=s) for t, s in ms_list])

    R["icit_multisite"] = multisite([r for r in I if r["site"] != "Unknown"], "ICIT")
    R["m77_multisite"] = multisite([r for r in m77_texts() if r["site"] not in ("Other sites", "West Asian finds")], "M77")
    save_json("q3_sealings", R)


if __name__ == "__main__":
    main()
