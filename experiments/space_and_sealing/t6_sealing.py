"""T6: seals vs sealings (ICIT). Pre-registered in docs/prereg/space_and_sealing.md.
Run: .venv/bin/python experiments/space_and_sealing/t6_sealing.py   -> t6.json (stdout = t6.log)."""
import json, sys
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sas_lib import icit_texts, signs, nsigns, T6_CLOSERS, T6_FRAME, has_any, HERE

NPERM = 10000
RNG = np.random.default_rng(20261116)
OUT = {}


def log(*a):
    print(*a, flush=True)


def band(n):
    return "1-2" if n <= 2 else ("3-4" if n <= 4 else "5+")


# ---- distinct (site, object class, text) rows, all legible texts, with end/start flags ----
groups = defaultdict(list)
for t in icit_texts():
    ty = t["type"]
    oc = "seal" if ty.startswith("SEAL") else ("sealing" if ty.startswith("TAG") else None)
    if oc is None or not signs(t["seq"]):
        continue
    groups[(t["site"], oc, " ".join(t["seq"]))].append(t)
ROWS = []
for (site, oc, k), ts in groups.items():
    seq = ts[0]["seq"]
    sg = nsigns(seq)
    ROWS.append(dict(site=site, oc=oc, key=k, seq=seq, signs=sg, length=len(sg), band=band(len(sg)),
                     end_ok=seq[-1] != "#", start_ok=seq[0] != "#",
                     complete=all(t["complete"] for t in ts) and "#" not in seq,
                     objects=sorted({t["id"].split(".")[0] for t in ts})))
log(f"T6 rows: {sum(r['oc']=='sealing' for r in ROWS)} distinct sealing texts, {sum(r['oc']=='seal' for r in ROWS)} distinct seal texts")


def unit_rows(cls_kind, complete_only=False):
    """closers: end preserved; opener: start preserved; others: all legible."""
    if complete_only:
        return [r for r in ROWS if r["complete"]]
    if cls_kind == "closer":
        return [r for r in ROWS if r["end_ok"]]
    if cls_kind == "opener":
        return [r for r in ROWS if r["start_ok"]]
    return ROWS


def mh(rows, ws, strata_fn, exclude_sites=(), nperm=NPERM, rng=RNG, only_sites=None):
    rows = [r for r in rows if r["site"] not in exclude_sites and (only_sites is None or r["site"] in only_sites)]
    st = defaultdict(list)
    for r in rows:
        st[strata_fn(r)].append(r)
    st = {k: v for k, v in st.items() if any(r["oc"] == "sealing" for r in v) and any(r["oc"] == "seal" for r in v)}
    if not st:
        return None
    lab, y, sidx = [], [], []
    for j, v in enumerate(st.values()):
        for r in v:
            lab.append(r["oc"] == "sealing"); y.append(has_any(r["signs"], ws)); sidx.append(j)
    lab, y, sidx = np.array(lab), np.array(y, float), np.array(sidx)
    num = den = 0.0
    for j in range(len(st)):
        m = sidx == j; n = m.sum()
        a = (lab[m] & (y[m] > 0)).sum(); b = (lab[m] & (y[m] == 0)).sum()
        c = (~lab[m] & (y[m] > 0)).sum(); d = (~lab[m] & (y[m] == 0)).sum()
        num += a * d / n; den += b * c / n
    OR = num / den if den > 0 else (np.inf if num > 0 else np.nan)
    a_obs = (lab & (y > 0)).sum()
    # permutation: shuffle sealing labels within strata
    cnt = 0; cnt_lo = 0; nulls = np.empty(nperm)
    groups_idx = [np.where(sidx == j)[0] for j in range(len(st))]
    for i in range(nperm):
        tot = 0
        for g in groups_idx:
            k = lab[g].sum()
            pick = rng.choice(len(g), k, replace=False)
            tot += y[g][pick].sum()
        nulls[i] = tot
    p_hi = float(((nulls >= a_obs).sum() + 1) / (nperm + 1))
    p_lo = float(((nulls <= a_obs).sum() + 1) / (nperm + 1))
    n_sl = int(lab.sum()); n_se = int((~lab).sum())
    return dict(OR=float(OR), sealing_with=int(a_obs), sealing_n=n_sl, expected=float(nulls.mean()),
                seal_with=int(((~lab) & (y > 0)).sum()), seal_n=n_se, p_enriched=p_hi, p_depleted=p_lo,
                n_strata=len(st), sites=sorted({k.split("#")[0] for k in st}))


def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


SB = lambda r: f"{r['site']}#{r['band']}"
SITE = lambda r: f"{r['site']}#"

# ---------------- primary: closer classes ----------------
log("\nPrimary: closer classes, end-preserved texts, MH over site x length band; one-sided p for enrichment on sealings")
prim = {}
for k, ws in T6_CLOSERS.items():
    prim[k] = mh(unit_rows("closer"), ws, SB)
ph = holm([prim[k]["p_enriched"] for k in T6_CLOSERS])
for (k, v), h in zip(prim.items(), ph):
    v["p_holm"] = float(h)
    log(f"  {k:15s} sealings {v['sealing_with']}/{v['sealing_n']} (exp {v['expected']:.1f}) seals {v['seal_with']}/{v['seal_n']}  "
        f"MH OR {v['OR']:.2f}  p_enr={v['p_enriched']:.4g} Holm={h:.4g}  p_depl={v['p_depleted']:.4g}")
OUT["primary_closers"] = prim

# leave-Lothal-out and leave-Dholavira-out, and Lothal alone, for every closer class
log("\nReplication: leave-Lothal-out (and leave-Dholavira-out, Lothal alone)")
rep = {}
for k, ws in T6_CLOSERS.items():
    rep[k] = dict(no_lothal=mh(unit_rows("closer"), ws, SB, exclude_sites=("Lothal",)),
                  no_dholavira=mh(unit_rows("closer"), ws, SB, exclude_sites=("Dholavira",)),
                  lothal_only=mh(unit_rows("closer"), ws, SB, only_sites=("Lothal",)))
    f = lambda d: "-" if d is None else f"OR {d['OR']:.2f} ({d['sealing_with']}/{d['sealing_n']} vs {d['seal_with']}/{d['seal_n']}) p_enr={d['p_enriched']:.3g}"
    log(f"  {k:15s} noLothal {f(rep[k]['no_lothal'])} | noDholavira {f(rep[k]['no_dholavira'])} | Lothal {f(rep[k]['lothal_only'])}")
OUT["replication"] = rep
supported = [k for k in T6_CLOSERS if prim[k]["p_holm"] < 0.05 and prim[k]["OR"] > 1
             and rep[k]["no_lothal"] and rep[k]["no_lothal"]["OR"] > 1 and rep[k]["no_lothal"]["p_enriched"] < 0.05]
OUT["support_closers"] = supported
log("  SUPPORTED closer classes:", supported or "none")

# leave-one-site-out OR range (descriptive)
loso = {}
sites_with = sorted({r["site"] for r in ROWS if r["oc"] == "sealing"})
for k, ws in T6_CLOSERS.items():
    ors = {}
    for s in sites_with:
        d = mh(unit_rows("closer"), ws, SB, exclude_sites=(s,), nperm=200)
        if d:
            ors[s] = d["OR"]
    loso[k] = ors
OUT["leave_one_site_out_OR"] = loso

# sensitivities: complete texts only; site-only strata
sens = {}
for k, ws in T6_CLOSERS.items():
    sens[k] = dict(complete_only=mh(unit_rows("closer", True), ws, SB, nperm=4000),
                   site_strata=mh(unit_rows("closer"), ws, SITE, nperm=4000),
                   final_sign_only=None)
# closer as the FINAL sign (not anywhere) among end-preserved texts
for k, ws in T6_CLOSERS.items():
    rows = [dict(r, signs=r["signs"][-1:]) for r in unit_rows("closer")]
    sens[k]["final_sign_only"] = mh(rows, ws, SB, nperm=4000)
OUT["sensitivity_closers"] = sens
log("\nSensitivity (OR, p_enr): complete-only | site strata | final sign only")
for k in T6_CLOSERS:
    g = lambda d: "-" if d is None else f"{d['OR']:.2f} ({d['p_enriched']:.3g}; {d['sealing_with']}/{d['sealing_n']})"
    log(f"  {k:15s} {g(sens[k]['complete_only'])} | {g(sens[k]['site_strata'])} | {g(sens[k]['final_sign_only'])}")

# ---------------- secondary: frame classes (two-sided) ----------------
log("\nSecondary: frame classes (opener: start preserved; others: all legible texts), MH site x band, two-sided")
sec = {}
for k, ws in T6_FRAME.items():
    d = mh(unit_rows("opener" if k == "opener" else "other"), ws, SB)
    d["p_two_sided"] = float(min(1, 2 * min(d["p_enriched"], d["p_depleted"])))
    d["no_lothal"] = mh(unit_rows("opener" if k == "opener" else "other"), ws, SB, exclude_sites=("Lothal",), nperm=4000)
    sec[k] = d
ph2 = holm([sec[k]["p_two_sided"] for k in T6_FRAME])
for (k, v), h in zip(sec.items(), ph2):
    v["p_holm"] = float(h)
    nl = v["no_lothal"]
    log(f"  {k:12s} sealings {v['sealing_with']}/{v['sealing_n']} (exp {v['expected']:.1f}) seals {v['seal_with']}/{v['seal_n']} "
        f"OR {v['OR']:.2f} p2={v['p_two_sided']:.4g} Holm={h:.4g} | noLothal OR {nl['OR']:.2f}")
OUT["secondary_frame"] = sec

# ---------------- power: planted enrichment ----------------
log("\nPower (planted OR on sealings, real strata margins; 300 reps, 400 perms each; one-sided alpha 0.05 and Holm-6 bar 0.0083)")


def power(ws, OR_true, exclude=(), reps=300):
    rows = [r for r in unit_rows("closer") if r["site"] not in exclude]
    st = defaultdict(list)
    for r in rows:
        st[SB(r)].append(r)
    st = {k: v for k, v in st.items() if any(r["oc"] == "sealing" for r in v) and any(r["oc"] == "seal" for r in v)}
    rng = np.random.default_rng(5)
    hits05 = hitsH = 0
    for _ in range(reps):
        lab, y, sidx = [], [], []
        for j, v in enumerate(st.values()):
            se = [has_any(r["signs"], ws) for r in v if r["oc"] == "seal"]
            p = (sum(se) + 0.5) / (len(se) + 1)
            od = p / (1 - p) * OR_true; ps = od / (1 + od)
            for r in v:
                if r["oc"] == "seal":
                    lab.append(False); y.append(has_any(r["signs"], ws))
                else:
                    lab.append(True); y.append(rng.random() < ps)
                sidx.append(j)
        lab, y, sidx = np.array(lab), np.array(y, float), np.array(sidx)
        a = (lab & (y > 0)).sum()
        gi = [np.where(sidx == j)[0] for j in range(len(st))]
        nulls = np.empty(400)
        for i in range(400):
            tot = 0
            for g in gi:
                k = lab[g].sum(); tot += y[g][rng.choice(len(g), k, replace=False)].sum()
            nulls[i] = tot
        p = ((nulls >= a).sum() + 1) / 401
        hits05 += p < 0.05; hitsH += p < 0.05 / 6
    return hits05 / reps, hitsH / reps


pw = {}
for k in ["jar_M342", "M211", "M169_family", "ticked_fish"]:
    pw[k] = {}
    for OR_true in (2, 3):
        a, h = power(T6_CLOSERS[k], OR_true)
        b, hb = power(T6_CLOSERS[k], OR_true, exclude=("Lothal",))
        pw[k][f"OR{OR_true}"] = dict(all_alpha05=a, all_holm=h, noLothal_alpha05=b)
        log(f"  {k:12s} OR {OR_true}: all sites {a:.2f} (Holm bar {h:.2f}); leave-Lothal-out {b:.2f}")
OUT["power"] = pw

# ---------------- die matches ----------------
log("\nDie matches: identical normalised text on a seal object from the same site")
seal_by_site = defaultdict(Counter)    # site -> text -> number of seal objects
for r in ROWS:
    if r["oc"] == "seal" and r["complete"]:
        seal_by_site[r["site"]][tuple(r["signs"])] += len(r["objects"])
seal_texts_any = Counter()
for s, c in seal_by_site.items():
    seal_texts_any.update(c)


def frag_match(r, site):
    """all legible runs of the fragment appear contiguously, in order, in one seal text at the site"""
    runs, cur = [], []
    for x in r["seq"]:
        if x in ("|", "#"):
            if x == "#" and cur:
                runs.append(cur); cur = []
            continue
        cur.append(x)
    if cur:
        runs.append(cur)
    from sas_lib import norm
    runs = [[norm(x) for x in ru] for ru in runs]
    for txt in seal_by_site[site]:
        pos = 0; ok = True
        for ru in runs:
            L = len(ru); found = False
            for i in range(pos, len(txt) - L + 1):
                if list(txt[i:i + L]) == ru:
                    pos = i + L; found = True; break
            if not found:
                ok = False; break
        if ok:
            return True
    return False


dm = {}
comp_sl = [r for r in ROWS if r["oc"] == "sealing" and r["complete"]]
frag_sl = [r for r in ROWS if r["oc"] == "sealing" and not r["complete"] and r["length"] >= 3]
for s in sorted({r["site"] for r in comp_sl + frag_sl}):
    cs = [r for r in comp_sl if r["site"] == s]
    fs = [r for r in frag_sl if r["site"] == s]
    m_exact = sum(1 for r in cs if tuple(r["signs"]) in seal_by_site[s])
    m_frag = sum(1 for r in fs if frag_match(r, s))
    # seal-seal recurrence: share of seal objects at the site whose text is on another seal object there
    c = seal_by_site[s]; nobj = sum(c.values())
    rec = (sum(v for v in c.values() if v >= 2) / nobj) if nobj else None
    dm[s] = dict(sealing_complete=len(cs), exact_matches=m_exact, sealing_frag3=len(fs), frag_matches=m_frag,
                 seal_objects_complete=nobj, seal_seal_recurrence=rec)
tot_c = sum(d["sealing_complete"] for d in dm.values()); tot_m = sum(d["exact_matches"] for d in dm.values())
tot_f = sum(d["sealing_frag3"] for d in dm.values()); tot_fm = sum(d["frag_matches"] for d in dm.values())
# pooled recurrence rate r, weighted by sealing texts per site (sites with seals only)
w = [(d["sealing_complete"] + d["sealing_frag3"], d["seal_seal_recurrence"]) for d in dm.values() if d["seal_seal_recurrence"] is not None]
r_bar = sum(a * b for a, b in w) / max(1, sum(a for a, _ in w))
m_rate = (tot_m + tot_fm) / max(1, tot_c + tot_f)
f_hat = (m_rate - r_bar) / (1 - r_bar) if r_bar < 1 else None
# bootstrap over sealing texts
pairs = [(1.0 if tuple(r["signs"]) in seal_by_site[r["site"]] else 0.0) for r in comp_sl] + \
        [(1.0 if frag_match(r, r["site"]) else 0.0) for r in frag_sl]
rng = np.random.default_rng(3)
bs = [(np.mean(rng.choice(pairs, len(pairs))) - r_bar) / (1 - r_bar) for _ in range(5000)]
cross = sum(1 for r in comp_sl if tuple(r["signs"]) not in seal_by_site[r["site"]] and tuple(r["signs"]) in seal_texts_any)
OUT["die_matches"] = dict(by_site=dm, complete_sealings=tot_c, exact_matches=tot_m, fragments_3plus=tot_f,
                          fragment_matches=tot_fm, match_rate=m_rate, seal_seal_recurrence_weighted=r_bar,
                          survival_fraction_hat=f_hat, survival_ci95=[float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                          complete_sealings_matching_seal_at_other_site_only=cross)
for s, d in dm.items():
    log(f"  {s:18s} complete {d['exact_matches']}/{d['sealing_complete']}  frag(3+) {d['frag_matches']}/{d['sealing_frag3']}  "
        f"seal objects {d['seal_objects_complete']}  seal-seal recurrence {d['seal_seal_recurrence'] if d['seal_seal_recurrence'] is None else round(d['seal_seal_recurrence'],3)}")
log(f"  pooled match rate {m_rate:.3f} ({tot_m + tot_fm}/{tot_c + tot_f}); recurrence baseline {r_bar:.3f}; "
    f"die-survival estimate f = {f_hat:.3f} (95% CI {np.quantile(bs,0.025):.3f} to {np.quantile(bs,0.975):.3f}); "
    f"complete sealing texts matching a seal only at another site: {cross}")

json.dump(OUT, open(HERE / "t6.json", "w"), indent=1, default=float)
