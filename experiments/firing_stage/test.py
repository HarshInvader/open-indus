"""Pre-registered test (docs/prereg/firing_stage.md). Run once:
.venv/bin/python -I experiments/firing_stage/test.py
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261115)
NPERM = 10000

DEV_SITES = {"Harappa", "Mohenjo-daro", "Chanhu-daro", "Balakot", "Bala-kot", "Gumla", "Kot-Diji", "Nausharo", "Amri",
             "Allahdino", "Lakhanjo-daro", "Naru-Waro-dharo", "Nuhato", "Rodji", "Hissam-dheri", "Bakkar Buthi",
             "Tarkhanewala-dera", "Rappwala Ther", "Guddal A", "Derawar Ther", "Murda Sang"}
bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))


def m_of(w):
    v = bridge.get(str(int(w[1:])), {}).get("M")
    return "/".join(f"M{x}" for x in v) if v else "-"


def site_norm(s):
    return "Balakot" if s == "Bala-kot" else s


def load(variant, drop_dup=False, drop_uncertain=False):
    rows = list(csv.DictReader(open(HERE / "vessel_marks.csv")))
    units = {}
    for r in rows:
        if r["vessel"] != "yes" or r["firing"] in ("mixed",):
            continue
        if drop_dup and r["icit_id"] == "5548.1":
            continue
        if drop_uncertain and ("uncertain" in r["note"] or "questionable" in r["note"] or "no known" in r["note"]):
            continue
        tech, fir = r["technique"], r["firing"]
        if fir == "pre":
            if variant == "P2" and tech != "painted":
                continue
            cls = "pre"
        elif fir == "post" or (fir == "unknown" and tech == "incised"):
            cls = "post"
        else:
            continue
        signs = tuple(s for s in r["text_wells"].split() if s.startswith("W"))
        if not signs:
            continue
        site = site_norm(r["site"])
        key = (site, cls, r["text_wells"])
        if key not in units:
            units[key] = dict(site=site, cls=cls, signs=set(signs), seq=r["text_wells"], form=r["vessel_form"],
                              split="dev" if site in DEV_SITES else "ho", n=len(signs), tech=tech)
    return list(units.values())


def ratio(a, npre, b, npost):
    return ((a + 0.5) / (npre + 1)) / ((b + 0.5) / (npost + 1))


def dev_set(units, amin):
    dev = [u for u in units if u["split"] == "dev"]
    pre = [u for u in dev if u["cls"] == "pre"]; post = [u for u in dev if u["cls"] == "post"]
    cp = Counter(s for u in pre for s in u["signs"]); cq = Counter(s for u in post for s in u["signs"])
    tab = []
    for s in set(cp) | set(cq):
        tab.append(dict(sign=s, M=m_of(s), pre=cp[s], post=cq[s], r=ratio(cp[s], len(pre), cq[s], len(post))))
    tab.sort(key=lambda d: (-d["pre"], -d["r"]))
    S = sorted(d["sign"] for d in tab if d["r"] >= 5 and d["pre"] >= amin)
    return S, tab, len(pre), len(post)


def perm_test(units, S, nperm=NPERM, rng=RNG):
    ho = [u for u in units if u["split"] == "ho"]
    has = np.array([bool(u["signs"] & set(S)) for u in ho])
    lab = np.array([u["cls"] == "pre" for u in ho])
    sites = np.array([u["site"] for u in ho])
    obs = int((has & lab).sum())
    npre, npost = int(lab.sum()), int((~lab).sum())
    R = ratio(obs, npre, int((has & ~lab).sum()), npost)
    groups = [np.where(sites == s)[0] for s in set(sites)]
    cnt = 0
    for _ in range(nperm):
        perm = lab.copy()
        for g in groups:
            perm[g] = rng.permutation(lab[g])
        if (has & perm).sum() >= obs:
            cnt += 1
    p = (cnt + 1) / (nperm + 1)
    return dict(ho_pre=npre, ho_post=npost, ho_pre_with_S=obs, ho_post_with_S=int((has & ~lab).sum()),
                R_ho=R, p=p, mixed_sites=sorted({u["site"] for u in ho if u["cls"] == "pre"} &
                                                  {u["site"] for u in ho if u["cls"] == "post"}))


def power(units, rate_pre, rate_post, n=1000):
    """Plant a fresh sign 'WPLANT' at dev rates in held-out units, rerun the held-out test."""
    if rate_pre <= 0:
        return None
    rng = np.random.default_rng(7)
    ok = 0
    for _ in range(n):
        uu = []
        for u in units:
            if u["split"] != "ho":
                continue
            v = dict(u); v["signs"] = set(u["signs"])
            if rng.random() < (rate_pre if u["cls"] == "pre" else rate_post):
                v["signs"].add("WPLANT")
            uu.append(v)
        t = perm_test(uu, ["WPLANT"], nperm=500, rng=rng)
        ok += (t["R_ho"] >= 2 and t["p"] < 0.025)
    return ok / n


def verdict(S, t):
    if not S or t["ho_pre"] < 10:
        return "INCONCLUSIVE"
    return "PASS" if (t["R_ho"] >= 2 and t["p"] < 0.025) else "FAIL"


def form_test(units, S):
    pre = [u for u in units if u["cls"] == "pre" and u["form"]]
    def fc(f):
        f = f.lower()
        if "goblet" in f: return "goblet"
        if "dish" in f or "bowl" in f: return "dish/bowl"
        if "jar" in f: return "jar"
        return None
    pre = [(fc(u["form"]), bool(u["signs"] & set(S))) for u in pre if fc(u["form"])]
    if not S or not pre:
        return dict(verdict="INCONCLUSIVE", n=len(pre), reason="S empty" if not S else "no forms")
    forms = np.array([f for f, _ in pre]); has = np.array([h for _, h in pre])
    cats = sorted(set(forms))
    def stat(h):
        chi = 0.0
        for c in cats:
            m = forms == c
            for val in (True, False):
                o = ((h == val) & m).sum(); e = m.sum() * (h == val).mean()
                chi += (o - e) ** 2 / e if e > 0 else 0
        return chi
    obs = stat(has)
    cnt = sum(stat(RNG.permutation(has)) >= obs - 1e-12 for _ in range(NPERM))
    p = (cnt + 1) / (NPERM + 1)
    table = {c: [int(((forms == c) & has).sum()), int((forms == c).sum())] for c in cats}
    return dict(verdict="PASS" if p < 0.05 else "FAIL", n=len(pre), table=table, chi2=obs, p=p)


def describe(units):
    out = {}
    for cls in ("pre", "post"):
        for sp in ("dev", "ho"):
            uu = [u for u in units if u["cls"] == cls and u["split"] == sp]
            out[f"{cls}_{sp}"] = dict(n=len(uu), mean_len=float(np.mean([u["n"] for u in uu])) if uu else None,
                                      **{k: sum(1 for u in uu if w in u["signs"]) for k, w in
                                         [("M342_W740", "W740"), ("M267_W861", "W861"), ("M391_W820", "W820"), ("M343_W741", "W741")]})
    return out


def main():
    log, res = [], {}
    def say(*a):
        s = " ".join(str(x) for x in a); print(s); log.append(s)
    for variant, amin in (("P1", 3), ("P2", 2)):
        say(f"\n===== {variant} =====")
        units = load(variant)
        S, tab, npre, npost = dev_set(units, amin)
        say(f"dev units: pre {npre}, post {npost}; held-out pre {sum(1 for u in units if u['split']=='ho' and u['cls']=='pre')}, post {sum(1 for u in units if u['split']=='ho' and u['cls']=='post')}")
        say("top dev signs by pre count:")
        for d in tab[:15]:
            say(f"  {d['sign']} {d['M']:>10} pre {d['pre']:3d} post {d['post']:3d} r {d['r']:.2f}")
        say("S =", [(s, m_of(s)) for s in S])
        t = perm_test(units, S) if S else dict(ho_pre=sum(1 for u in units if u['split']=='ho' and u['cls']=='pre'))
        if S:
            say(f"held-out: pre {t['ho_pre_with_S']}/{t['ho_pre']} vs post {t['ho_post_with_S']}/{t['ho_post']}; R_ho {t['R_ho']:.2f}; within-site perm p {t['p']:.4f}; sites with both classes {t['mixed_sites']}")
            best = max((d for d in tab if d["sign"] in S), key=lambda d: d["pre"])
            pw = power(units, best["pre"] / npre, best["post"] / npost)
            t["power_at_strongest_dev_rate"] = pw
            say(f"power (plant at {best['sign']} dev rates {best['pre']}/{npre} vs {best['post']}/{npost}): {pw}")
        v = verdict(S, t)
        say("VERDICT", variant, v)
        ft = form_test(units, S)
        say("secondary (form):", ft)
        sens = {}
        for name, kw in (("drop_dup", dict(drop_dup=True)), ("drop_uncertain", dict(drop_uncertain=True))):
            u2 = load(variant, **kw)
            S2, _, _, _ = dev_set(u2, amin)
            t2 = perm_test(u2, S2, nperm=2000) if S2 else {}
            sens[name] = dict(S=S2, R_ho=t2.get("R_ho"), p=t2.get("p"), verdict=verdict(S2, t2) if S2 else "INCONCLUSIVE")
            say("sensitivity", name, sens[name])
        res[variant] = dict(S=[(s, m_of(s)) for s in S], dev_pre=npre, dev_post=npost, dev_top=tab[:15], heldout=t,
                            verdict=v, secondary_form=ft, sensitivity=sens, describe=describe(units))
        say("describe:", json.dumps(res[variant]["describe"]))
    json.dump(res, open(HERE / "tests.json", "w"), indent=1, default=float)
    open(HERE / "tests.log", "w").write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
