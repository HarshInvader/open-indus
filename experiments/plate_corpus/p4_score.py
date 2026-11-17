"""P4: score the blind readings against M77 and against each other; apply the pre-registered gate.
Inputs: readers/out_{A,B}_{P,C}.json, work/reader_key.csv, crops.csv, sample.csv, M77 lines.
Output: results.json, scores.csv. Run: .venv/bin/python -I experiments/plate_corpus/p4_score.py"""
import csv, json, os, sys, statistics as S
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, REPO)
from corpus.load import m77_lines


def lev_matches(a, b):
    """max number of exact matches in an optimal edit alignment (unit costs)."""
    n, m = len(a), len(b)
    dp = [[(0, 0)] * (m + 1) for _ in range(n + 1)]  # (cost, -matches)
    for i in range(1, n + 1): dp[i][0] = (i, 0)
    for j in range(1, m + 1): dp[0][j] = (j, 0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            same = a[i - 1] == b[j - 1]
            c0, mm = dp[i - 1][j - 1]
            cand = [(c0 + (0 if same else 1), mm - (1 if same else 0)),
                    (dp[i - 1][j][0] + 1, dp[i - 1][j][1]), (dp[i][j - 1][0] + 1, dp[i][j - 1][1])]
            dp[i][j] = min(cand)
    return -dp[n][m][1]


def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** .5
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def main():
    sample = {r["m77_text_no"]: r for r in csv.DictReader(open(os.path.join(D, "sample.csv")))}
    crops = {r["key"]: r for r in csv.DictReader(open(os.path.join(D, "crops.csv")))}
    key = {r["reader_id"]: r for r in csv.DictReader(open(os.path.join(D, "work", "reader_key.csv")))}
    L = {}
    for l in m77_lines():
        L.setdefault(l["text_no"], []).append(l)
    truth = {}
    for k, c in crops.items():
        s = next(r for r in sample.values() if r["source"] == c["source"] and r["object_no"] == c["object_no"])
        lines = sorted(L[int(s["m77_text_no"])], key=lambda l: l["line"])
        truth[k] = dict(lines=[l["signs"] for l in lines], direction=lines[0]["direction"], text_no=s["m77_text_no"],
                        source=c["source"], ppmm=float(c["plate_px_per_mm"]),
                        cisi_ppmm=float(c["cisi_px_per_mm"]) if c["cisi_px_per_mm"] else None)
    R = {}
    for reader in "AB":
        for st in "PC":
            for e in json.load(open(os.path.join(D, "readers", f"out_{reader}_{st}.json"))):
                R[(reader, st, key[e["id"]]["key"])] = e
    rows = []
    for (reader, st, k), e in sorted(R.items()):
        t = truth[k]
        tl = t["lines"]; tn = sum(len(x) for x in tl)
        unread = bool(e.get("unreadable"))
        rl = [list(x) for x in e.get("lines", [])]
        rn = sum(len(x) for x in rl)
        # expected visual order: impression of an R-L text -> each line reversed when read left to right
        exp_vis = [list(reversed(x)) if t["direction"] == "right-to-left" else list(x) for x in tl]
        alt_vis = [list(x) for x in tl] if t["direction"] == "right-to-left" else [list(reversed(x)) for x in tl]
        flat = lambda ls: [s for l in ls for s in l]
        m_exp = 0 if unread else lev_matches(flat(rl), flat(exp_vis))
        m_alt = 0 if unread else lev_matches(flat(rl), flat(alt_vis))
        rows.append(dict(reader=reader, set=st, key=k, source=t["source"], text_no=t["text_no"], unreadable=unread,
                         face=e.get("face"), m77_n=tn, reader_n=rn, m77_lines=len(tl), reader_lines=e.get("n_lines"),
                         m77_spl=",".join(str(len(x)) for x in tl), reader_spl=",".join(str(len(x)) for x in rl),
                         count_exact=(not unread) and rn == tn, count_pm1=(not unread) and abs(rn - tn) <= 1,
                         lines_match=(not unread) and e.get("n_lines") == len(tl),
                         sign_matches_expected_order=m_exp, sign_matches_better_order=max(m_exp, m_alt),
                         sign_acc_expected=round(m_exp / tn, 3), sign_acc_better=round(max(m_exp, m_alt) / tn, 3)))
    with open(os.path.join(D, "scores.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    def summ(st, keys, by_source=False):
        rs = [r for r in rows if r["set"] == st and r["key"] in keys]
        n = len(rs); k1 = sum(r["count_exact"] for r in rs); k2 = sum(r["count_pm1"] for r in rs)
        kl = sum(r["lines_match"] for r in rs)
        acc = sum(r["sign_matches_expected_order"] for r in rs) / max(1, sum(r["m77_n"] for r in rs))
        accb = sum(r["sign_matches_better_order"] for r in rs) / max(1, sum(r["m77_n"] for r in rs))
        # two-reader layout agreement
        agree = 0; ks = sorted(keys)
        for k in ks:
            a = next((r for r in rs if r["key"] == k and r["reader"] == "A"), None)
            b = next((r for r in rs if r["key"] == k and r["reader"] == "B"), None)
            if a and b and not a["unreadable"] and not b["unreadable"] and a["reader_lines"] == b["reader_lines"] \
                    and a["reader_spl"] == b["reader_spl"]:
                agree += 1
        both_count_right = sum(1 for k in ks if all(r["count_exact"] for r in rs if r["key"] == k))
        per_reader = {rd: dict(count_exact=sum(r["count_exact"] for r in rs if r["reader"] == rd),
                               n=sum(1 for r in rs if r["reader"] == rd),
                               sign_acc=round(sum(r["sign_matches_expected_order"] for r in rs if r["reader"] == rd) /
                                              max(1, sum(r["m77_n"] for r in rs if r["reader"] == rd)), 3),
                               unreadable=sum(r["unreadable"] for r in rs if r["reader"] == rd)) for rd in "AB"}
        return dict(n_readings=n, n_seals=len(ks), count_exact=k1, count_exact_rate=round(k1 / n, 3),
                    count_exact_ci95=wilson(k1, n), count_pm1_rate=round(k2 / n, 3),
                    line_count_vs_m77_rate=round(kl / n, 3), layout_two_reader_agree=agree,
                    layout_two_reader_rate=round(agree / len(ks), 3), seals_both_readers_count_right=both_count_right,
                    sign_acc_expected_order=round(acc, 3), sign_acc_better_order=round(accb, 3),
                    unreadable=sum(r["unreadable"] for r in rs), per_reader=per_reader)

    allk = set(truth)
    ck = {k for k in truth if truth[k]["cisi_ppmm"]}
    pp = [truth[k]["ppmm"] for k in allk]
    res = dict(
        test="plate_corpus gate (docs/prereg/plate_corpus.md)",
        n_seals=len(allk),
        plate_px_per_mm=dict(median=round(S.median(pp), 2), p10=round(float(np.percentile(pp, 10)), 2),
                             p90=round(float(np.percentile(pp, 90)), 2),
                             by_volume={src: round(S.median([truth[k]["ppmm"] for k in allk if truth[k]["source"] == src]), 2)
                                        for src in sorted({truth[k]["source"] for k in allk})}),
        cisi_px_per_mm_paired=dict(n=len(ck), median=round(S.median([truth[k]["cisi_ppmm"] for k in ck]), 2),
                                   plate_median_same_seals=round(S.median([truth[k]["ppmm"] for k in ck]), 2)),
        plates_all=summ("P", allk),
        plates_paired=summ("P", ck),
        cisi_paired=summ("C", ck),
        plates_by_volume={src: summ("P", {k for k in allk if truth[k]["source"] == src})
                          for src in sorted({truth[k]["source"] for k in allk})},
    )
    g = res["plates_all"]
    res["gate"] = dict(
        layout=dict(median_ppmm_ge_12=res["plate_px_per_mm"]["median"] >= 12,
                    count_agreement_ge_0_90=g["count_exact_rate"] >= 0.90,
                    two_reader_layout_ge_0_85=g["layout_two_reader_rate"] >= 0.85),
        carver=dict(median_ppmm_ge_30=res["plate_px_per_mm"]["median"] >= 30),
        beat_cisi=dict(ppmm_ratio=round(res["cisi_px_per_mm_paired"]["plate_median_same_seals"] /
                                        res["cisi_px_per_mm_paired"]["median"], 2),
                       ppmm_ratio_ge_1_5=res["cisi_px_per_mm_paired"]["plate_median_same_seals"] >=
                       1.5 * res["cisi_px_per_mm_paired"]["median"],
                       plate_count_ge_cisi=res["plates_paired"]["count_exact_rate"] >= res["cisi_paired"]["count_exact_rate"]),
        secondary_sign_acc_ge_0_80=g["sign_acc_expected_order"] >= 0.80)
    res["gate"]["layout_PASS"] = all(res["gate"]["layout"].values())
    res["gate"]["carver_PASS"] = res["gate"]["layout_PASS"] and res["gate"]["carver"]["median_ppmm_ge_30"]
    res["gate"]["plates_beat_cisi"] = res["gate"]["beat_cisi"]["ppmm_ratio_ge_1_5"] and res["gate"]["beat_cisi"]["plate_count_ge_cisi"]
    json.dump(res, open(os.path.join(D, "results.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
