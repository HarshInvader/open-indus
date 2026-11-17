"""Score the frozen lead predictions L1-L7 (docs/prereg/2026-11-15_leads_predictions.md) on new_texts.csv.
    .venv/bin/python experiments/new_finds/score_leads.py [path/to/new_texts.csv]
Same rows and sets as score.py: primary = scored == yes; sensitivity = status new/possible_known with any
readable sign ('?' stripped). Optional columns: width_mm, height_mm (seal face) for L7.
Writes results_leads.json next to this file. Thresholds are copied from the frozen file; do not edit."""
import csv
import json
import re
import sys
from pathlib import Path

from scipy.stats import binomtest, fisher_exact, mannwhitneyu

OUT = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "new_texts.csv"
rows = list(csv.DictReader(open(SRC)))

ROOFED = {"M65", "M66", "M92", "M138", "M159", "M163", "M334", "M203", "M196", "M14"}
ROOF_BASE = {"M59", "M60", "M89", "M137", "M158", "M162", "M333", "M202", "M195", "M12"}
TICK = {"M60", "M66", "M68", "M71", "M73"}
PLAIN = {"M59", "M65", "M67", "M70", "M72", "M75"}
OVAL = {"M373", "M374"}
TALL = {"M86": 1, "M87": 2, "M88": 3, "M89": 3, "M92": 3, "M93": 3, "M94": 3, "M95": 4, "M96": 5}
SHORT = {"M97": 1, "M98": 1, "M102": 3, "M103": 3, "M104": 4, "M105": 4, "M106": 5, "M107": 5, "M108": 6,
         "M109": 6, "M110": 7, "M111": 7, "M112": 7, "M114": 8, "M115": 9, "M116": 9, "M117": 9,
         "M118": 10, "M121": 12, "M122": 5}
LEX = {"M211": ("tall", 3), "M59": ("tall", 2), "M342": ("tall", 2), "M60": ("tall", 2), "M197": ("short", 7),
       "M15": ("short", 3), "M194": ("short", 7), "M403": ("short", 3), "M25": ("short", 1), "M284": ("tall", 2),
       "M190": ("short", 3)}


def toks(r):
    """Sign tokens with '|' kept; '?' stripped; anything not M### or '|' dropped."""
    out = []
    for s in r["seq_M"].split():
        s = s.rstrip("?")
        if re.fullmatch(r"M\d+", s) or s == "|":
            out.append(s)
    return out


def signs(t):
    return [s for s in t if s != "|"]


def num(s):
    if s in TALL:
        return ("tall", TALL[s])
    if s in SHORT:
        return ("short", SHORT[s])
    return None


def verdict(n, minn, passed, failed):
    if n < minn:
        return "inconclusive (n<min)"
    return "pass" if passed else ("fail" if failed else "neither (between bars)")


def score(S):
    R = {}
    T = [toks(r) for r in S]
    comp = [signs(t) for t in T if len(signs(t)) >= 2]
    # L1 roof initial
    ri = rn = bi = bn = 0
    for s in comp:
        for i, x in enumerate(s):
            if x in ROOFED:
                rn += 1; ri += i == 0
            elif x in ROOF_BASE:
                bn += 1; bi += i == 0
    rs = ri / rn if rn else None; bs = bi / bn if bn else None
    p = fisher_exact([[ri, rn - ri], [bi, bn - bi]], alternative="greater")[1] if rn and bn else None
    R["L1"] = dict(roofed=f"{ri}/{rn}", base=f"{bi}/{bn}", p=p,
                   verdict=verdict(min(rn, bn), 8, rn and bn and rs >= bs + 0.10 and p < 0.05, rn and bn and rs <= bs))
    # L2 oval on bangles
    bang = [signs(t) for t, r in zip(T, S) if "bangle" in r["object_type"].lower() and signs(t)]
    k = sum(bool(OVAL & set(s)) for s in bang); n = len(bang)
    p = binomtest(k, n, 0.01, alternative="greater").pvalue if n else None
    R["L2"] = dict(k=k, n=n, p=p, verdict=verdict(n, 10, n and k / n >= 0.08 and p < 0.05, n >= 15 and k / n < 0.03))
    R["L2b_M403_exploratory"] = dict(k=sum("M403" in s for s in bang), n=n)
    # L3 ticked fish final
    tk = [i == len(s) - 1 for s in comp for i, x in enumerate(s) if x in TICK]
    pl = [i == len(s) - 1 for s in comp for i, x in enumerate(s) if x in PLAIN]
    ts = sum(tk) / len(tk) if tk else None; ps = sum(pl) / len(pl) if pl else 0.0
    R["L3"] = dict(ticked=f"{sum(tk)}/{len(tk)}", plain=f"{sum(pl)}/{len(pl)}",
                   verdict=verdict(len(tk), 5, tk and ts >= 0.5 and ts > ps, tk and ts <= ps))
    # L4 / L6 numerals: numeral directly before a non-numeral, within a line
    pairs = []
    for t in T:
        for a, b in zip(t, t[1:]):
            if "|" in (a, b):
                continue
            na = num(a)
            if na and not num(b):
                pairs.append((na, b))
    p59 = [na for na, b in pairs if b == "M59"]
    k = sum(na == ("tall", 2) for na in p59); n = len(p59)
    R["L4"] = dict(k=k, n=n, verdict=verdict(n, 5, n and k / n >= 0.40, n and k / n < 0.20))
    lx = [(na, b) for na, b in pairs if b in LEX and LEX[b][0] == na[0]]
    k = sum(na[1] == LEX[b][1] for na, b in lx); n = len(lx)
    p = binomtest(k, n, 0.325, alternative="greater").pvalue if n else None
    R["L6"] = dict(k=k, n=n, p=p, verdict=verdict(n, 8, n and k / n >= 0.6 and p < 0.05, n and k / n <= 0.40))
    lx2 = [(na, b) for na, b in lx if b not in ("M59", "M60")]
    k2 = sum(na[1] == LEX[b][1] for na, b in lx2)
    R["L6b_no_fish"] = dict(k=k2, n=len(lx2), verdict=verdict(len(lx2), 6, lx2 and k2 / len(lx2) >= 0.5, lx2 and k2 / len(lx2) <= 0.33))
    # L5 M93
    m93 = [(t, r) for t, r in zip(T, S) if "M93" in t]
    k = sum("chanhu" in r["site"].lower() for t, r in m93); n = len(m93)
    R["L5"] = dict(k=k, n=n, verdict=verdict(n, 3, n and k / n >= 0.5, n and k / n < 0.2))
    lf = []
    for t, r in m93:
        i = t.index("M93")
        lf.append(i == len(t) - 1 or t[i + 1] == "|")
    R["L5b_position"] = dict(k=sum(lf), n=len(lf), verdict=verdict(len(lf), 3, lf and sum(lf) / len(lf) >= 0.7, lf and sum(lf) / len(lf) < 0.4))
    # L7 no-animal seals smaller
    none, anim = [], []
    for r in S:
        if not r["object_type"].lower().startswith("seal") or "sealing" in r["object_type"].lower():
            continue
        try:
            sz = max(float(r.get("width_mm") or 0), float(r.get("height_mm") or 0))
        except ValueError:
            continue
        if sz <= 0:
            continue
        fs = (r.get("field_symbol") or "").strip().lower()
        if fs in ("none", "no animal", "text only"):
            none.append(sz)
        elif fs and fs not in ("-", "unknown", "?"):
            anim.append(sz)
    if none and anim:
        import statistics
        ratio = statistics.median(none) / statistics.median(anim)
        p = mannwhitneyu(none, anim, alternative="less").pvalue
    else:
        ratio = p = None
    ok = len(none) >= 4 and len(anim) >= 8
    R["L7"] = dict(n_none=len(none), n_animal=len(anim), ratio=ratio, p=p,
                   verdict=verdict(1 if ok else 0, 1, ok and ratio <= 0.90 and p < 0.10, ok and ratio >= 1.0))
    return R


def readable(r):
    return any(re.fullmatch(r"M\d+", s.rstrip("?")) for s in r["seq_M"].split())


prim = [r for r in rows if r["scored"] == "yes"]
sens = [r for r in rows if r["status"] in ("new", "possible_known") and readable(r)]
out = {"source": str(SRC), "n_rows": len(rows)}
for name, S in (("primary", prim), ("sensitivity_all_readable", sens)):
    out[name] = dict(n_texts=len(S), scores=score(S))
ev = [k for k, v in out["primary"]["scores"].items() if k[1:].isdigit() and not v["verdict"].startswith("inconclusive")]
out["evaluable_predictions"] = ev
out["n_pass"] = sum(out["primary"]["scores"][k]["verdict"] == "pass" for k in ev)
json.dump(out, open(OUT / "results_leads.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
