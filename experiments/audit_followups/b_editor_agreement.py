"""Check B: how often do Mahadevan (M77) and Wells/Fuls (ICIT) read the same object differently, sign by sign?

Objects are matched WITHOUT using their sign sequences: experiments/old_registers/registers.csv links a 1930s
register row to an M77 text number (Mahadevan's App. V serial rule) and to an ICIT record (register field
number -> CISI basic data -> ICIT cisi). Signs are compared on the Wells list through the Wells-Mahadevan
bridge (sources/shaunmortal_indus/data/bridge_WM.json, with harness.py's font-verified overrides); two
tokens agree if their Wells label sets overlap.
Pre-registration: docs/prereg/audit_followups.md (section B).

    board/run.sh .venv/bin/python -I experiments/audit_followups/b_editor_agreement.py
"""
import sys, json, random, itertools
from pathlib import Path
from collections import Counter, defaultdict
import csv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness as H  # noqa
from corpus.load import m77_texts, m77_lines, icit_texts  # noqa

LINK_ERR = 0.8      # normalised distance above this = probable link error (pre-registered)
BOOT = 2000


def wset(V, m):
    s = V.inv.get(m)
    return frozenset(s) if s else None          # None = sign has no bridge entry


def align(a, b, eq):
    """Optimal string alignment (Levenshtein + adjacent transposition). a, b lists. -> (dist, ops Counter)."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = 0 if eq(a[i - 1], b[j - 1]) else 1
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + c)
            if i > 1 and j > 1 and eq(a[i - 1], b[j - 2]) and eq(a[i - 2], b[j - 1]) and c:
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
    ops = Counter(); i, j = n, m
    while i or j:
        if i and j:
            c = 0 if eq(a[i - 1], b[j - 1]) else 1
            if D[i][j] == D[i - 1][j - 1] + c:
                if c: ops["sub_unmapped" if (a[i - 1][1] is None or b[j - 1][1] is None) else "sub"] += 1
                else: ops["match"] += 1
                i -= 1; j -= 1; continue
            if i > 1 and j > 1 and eq(a[i - 1], b[j - 2]) and eq(a[i - 2], b[j - 1]) and D[i][j] == D[i - 2][j - 2] + 1:
                ops["transpose"] += 1; i -= 2; j -= 2; continue
        if i and D[i][j] == D[i - 1][j] + 1:
            ops["m77_extra"] += 1; i -= 1; continue
        ops["icit_extra"] += 1; j -= 1
    return D[n][m], ops


def eq(x, y):
    # x = ("M12", frozenset({"W..."}) or None), y = ("W123", frozenset({"W123"}))
    return x[1] is not None and bool(x[1] & y[1])


def flat(seq):
    return [s for s in seq if s not in ("|", "#")]


def main():
    V = H.Variant("ICIT")
    m77 = defaultdict(list)
    for t in m77_texts():
        m77[t["text_no"]].append(t)
    icit = {t["id"]: t for t in icit_texts()}
    mdir = defaultdict(set)
    for l in m77_lines():
        d = {"right-to-left": "rl", "left-to-right": "lr"}.get(l["direction"])
        if d: mdir[(l["text_no"], l["side"])].add(d)
    links = []
    with open(ROOT / "experiments/old_registers/registers.csv") as f:
        for r in csv.DictReader(f):
            if r["m77_text_no"] and r["icit_ids"]:
                links.append(r)
    seen, pairs = set(), []
    n_nom77 = n_noicit = 0
    for r in links:
        tn = int(float(r["m77_text_no"]))
        ids = [x for x in r["icit_ids"].replace(",", ";").replace(" ", ";").split(";") if x]
        if tn in seen: continue
        seen.add(tn)
        Ms = [t for t in m77[tn] if flat(t["seq"])]
        Is = [icit[i] for i in ids if i in icit and flat(icit[i]["seq"])]
        if not Ms: n_nom77 += 1; continue
        if not Is: n_noicit += 1; continue
        for mt in Ms:          # each M77 side vs its best-matching ICIT record (pre-registered)
            a = [(s, wset(V, s)) for s in flat(mt["seq"])]
            best = None
            for it in Is:
                b = [(s, frozenset([s])) for s in flat(it["seq"])]
                d, ops = align(a, b, eq)
                drev, opsrev = align(a[::-1], b, eq)
                # line order: try permutations of M77 lines (<=3 lines)
                lines = H.runs([s for s in mt["seq"] if s != "#"])
                dline = d
                if 1 < len(lines) <= 3:
                    for p in itertools.permutations(lines):
                        if list(p) == lines: continue
                        aa = [(s, wset(V, s)) for l in p for s in l]
                        dline = min(dline, align(aa, b, eq)[0])
                norm = d / max(len(a), len(b))
                cand = dict(text_no=tn, side=mt["side"], icit=it["id"], n_m77=len(a), n_icit=len(b), dist=d, norm=norm,
                            ops=dict(ops), dist_rev=drev, dist_lineperm=dline, n_unbridged=sum(x[1] is None for x in a),
                            dir_m77=sorted(mdir.get((tn, mt["side"]), [])),
                            dir_icit={"R/L": "rl", "L/R": "lr", "R/l": "rl"}.get(it["direction"]), source=r["source"],
                            object_type=mt["object_type"], site=mt["site"])
                if best is None or d < best["dist"]: best = cand
            pairs.append(best)
    # random-pair baseline for the link-error threshold
    rng = random.Random(0)
    allM = [t for ts in m77.values() for t in ts if flat(t["seq"])]
    allI = [t for t in icit.values() if flat(t["seq"])]
    rand = []
    for _ in range(500):
        mt, it = rng.choice(allM), rng.choice(allI)
        a = [(s, wset(V, s)) for s in flat(mt["seq"])]; b = [(s, frozenset([s])) for s in flat(it["seq"])]
        rand.append(align(a, b, eq)[0] / max(len(a), len(b)))
    ok = [p for p in pairs if p["norm"] <= LINK_ERR]
    bad = [p for p in pairs if p["norm"] > LINK_ERR]

    def rates(ps):
        tok = sum(p["n_m77"] for p in ps)
        c = Counter()
        for p in ps:
            c.update(p["ops"])
        unm = c["sub_unmapped"]
        den = tok - unm
        dis = c["sub"] + c["m77_extra"] + c["icit_extra"] + c["transpose"]
        return dict(texts=len(ps), m77_tokens=tok, unmapped_subs=unm, compared_tokens=den, sub=c["sub"],
                    missing_or_extra=c["m77_extra"] + c["icit_extra"], m77_extra=c["m77_extra"], icit_extra=c["icit_extra"],
                    transpose=c["transpose"], rate_total=dis / den if den else None,
                    rate_sub=c["sub"] / den if den else None,
                    rate_indel=(c["m77_extra"] + c["icit_extra"]) / den if den else None,
                    rate_transpose=c["transpose"] / den if den else None,
                    texts_any_disagreement=sum(1 for p in ps if p["dist"] - p["ops"].get("sub_unmapped", 0) > 0) / max(len(ps), 1),
                    texts_reversal_better=sum(1 for p in ps if p["dist_rev"] < p["dist"]) / max(len(ps), 1),
                    texts_lineorder_better=sum(1 for p in ps if p["dist_lineperm"] < p["dist"]) / max(len(ps), 1))

    def boot(ps, key):
        r = random.Random(1); vals = []
        for _ in range(BOOT):
            s = [r.choice(ps) for _ in ps]
            v = rates(s)[key]
            if v is not None: vals.append(v)
        vals.sort()
        return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]

    prim = rates(ok)
    ci = {k: boot(ok, k) for k in ("rate_total", "rate_sub", "rate_indel", "rate_transpose", "texts_reversal_better")}
    both_dir = [p for p in ok if p["dir_icit"] and len(p["dir_m77"]) == 1]
    dir_dis = sum(p["dir_icit"] != p["dir_m77"][0] for p in both_dir)
    lr_m77 = [p for p in both_dir if p["dir_m77"][0] == "lr"]
    res = dict(n_register_links=len(links), n_objects=len(seen), n_no_m77_text=n_nom77, n_no_icit_text=n_noicit,
               n_pairs=len(pairs), n_link_error=len(bad), link_err_threshold=LINK_ERR,
               random_pair_norm_median=sorted(rand)[250], random_pair_share_le_thr=sum(x <= LINK_ERR for x in rand) / len(rand),
               primary=prim, ci95=ci, all_pairs=rates(pairs),
               direction_labels=dict(n=len(both_dir), disagree=dir_dis, rate=dir_dis / max(len(both_dir), 1),
                                     m77_lr=len(lr_m77), m77_lr_icit_rl=sum(p["dir_icit"] == "rl" for p in lr_m77)),
               by_source={s: rates([p for p in ok if p["source"] == s]) for s in sorted({p["source"] for p in ok})},
               by_type=Counter(p["object_type"] for p in ok), by_site=Counter(p["site"] for p in ok),
               len_mean_linked=sum(p["n_m77"] for p in ok) / max(len(ok), 1),
               len_mean_m77_all=sum(len(flat(t["seq"])) for t in allM) / len(allM))
    print(json.dumps({k: v for k, v in res.items() if k not in ("by_source",)}, indent=1, default=str))
    (HERE / "out").mkdir(exist_ok=True)
    json.dump(dict(summary=res, pairs=pairs), open(HERE / "out" / "b_editor_agreement.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
