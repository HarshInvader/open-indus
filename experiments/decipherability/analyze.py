"""Aggregate grid results -> tables, phase diagram, Indus placement, results.json.
usage: .venv/bin/python experiments/decipherability/analyze.py"""
import json, sys, numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LANGS = ["san", "tam", "sux", "lat", "fin"]
INDUS_TOK = 10005


def load(name):
    p = OUT / f"{name}.jsonl"
    if not p.exists(): return []
    R = [json.loads(l) for l in open(p)]
    return [r for r in R if "error" not in r]


def absname(lang, k):
    if k == "K1": return f"{lang}:K1"
    if k == "K2": return f"{lang}:K2"
    if k.startswith("W:"): return f"{k[2:]}:K1"
    if k.startswith("R:"): return f"{k[2:]}:K2"
    return None


def calibrate(R):
    """Leave-one-out calibrated z for every (corpus, LM): gain of LM m on corpus c versus the gains of m on
    corpora of OTHER languages in the same (genre, size, logo-target) group."""
    groups = defaultdict(list)
    for i, r in enumerate(R): groups[(r["genre"], r["ntok_target"], r["logo"])].append(i)
    for g, idx in groups.items():
        G = defaultdict(dict)      # m -> corpus index -> gain
        for i in idx:
            for k, v in R[i]["lms"].items():
                m = absname(R[i]["lang"], k)
                if m: G[m][i] = v["gain"]
        for i in idx:
            R[i]["cal"] = {}
            for m, d in G.items():
                if i not in d: continue
                null = [d[j] for j in d if R[j]["lang"] != m.split(":")[0] and j != i]
                if len(null) < 3: continue
                mu, sd = np.mean(null), np.std(null, ddof=1) + 1e-9
                z = (d[i] - mu) / sd
                crit = stats.t.ppf(0.99, len(null) - 1) * np.sqrt(1 + 1 / len(null))   # prediction interval
                R[i]["cal"][m] = dict(z=z, crit=crit, sig=bool(z > crit))
    for r in R:
        cal = r.get("cal", {}); lang = r["lang"]
        t1 = cal.get(f"{lang}:K1"); t2 = cal.get(f"{lang}:K2")
        wrong = [v["z"] for m, v in cal.items() if m.split(":")[0] != lang]
        wrong_k1 = [v["z"] for m, v in cal.items() if m.split(":")[0] != lang and m.endswith("K1")]
        r["id_K1"] = bool(t1 and t1["sig"] and all(t1["z"] > w for w in wrong)) if t1 else None
        r["id_K2"] = bool(t2 and t2["sig"] and all(t2["z"] > w for w in wrong)) if t2 else None
        allz = {m: v["z"] for m, v in cal.items()}
        r["rank1_cal_K1"] = bool(t1 and max(allz, key=allz.get) == f"{lang}:K1") if t1 else None
        noK1 = {m: z for m, z in allz.items() if m != f"{lang}:K1"}
        r["rank1_cal_K2"] = bool(t2 and max(noK1, key=noK1.get) == f"{lang}:K2") if t2 else None
        r["fp_wrong"] = [v["sig"] for m, v in cal.items() if m.split(":")[0] != lang]
        g = {absname(lang, k): v["gain"] for k, v in r["lms"].items() if absname(lang, k) and absname(lang, k).endswith("K1")}
        r["rank1_raw_K1"] = bool(g and max(g, key=g.get) == f"{lang}:K1")
    return R


def table(R, genre):
    rows = []
    keyf = lambda r: (r["ntok_target"], r["logo"])
    grp = defaultdict(list)
    for r in R:
        if r["genre"] == genre: grp[keyf(r)].append(r)
    for (nt, lg), rs in sorted(grp.items()):
        row = dict(ntok=nt, logo_target=lg, logo_achieved=float(np.mean([r["logo_share"] for r in rs])),
                   n=len(rs), S=float(np.mean([r["S"] for r in rs])), mean_len=float(np.mean([r["mean_len"] for r in rs])))
        for k in ["K0", "K1", "K2", "K3"]:
            v = [r["lms"][k] for r in rs if k in r["lms"]]
            if not v: continue
            row[f"acc_{k}"] = float(np.mean([x["acc_tok"] for x in v]))
            row[f"accmax_{k}"] = float(np.mean([x["acc_max"] for x in v]))
            row[f"wbt_{k}"] = float(np.mean([x["wrong_beats_true"] for x in v]))
            Hs = [-x["true"] / (r["ntok"] * np.log(2)) for x, r in zip(v, [r for r in rs if k in r["lms"]])]
            D = [np.log2(102) - h for h in Hs]
            row[f"H_{k}"] = float(np.mean(Hs))
            row[f"U_{k}"] = float(np.mean([r["S"] * np.log2(102) / d if d > 0 else np.inf
                                           for d, r in zip(D, [r for r in rs if k in r["lms"]])]))
            row[f"gap_{k}"] = float(np.mean([(x["best"] - x["true"]) / r["ntok"] for x, r in zip(v, [r for r in rs if k in r["lms"]])]))
        row["id_K1"] = float(np.mean([r["id_K1"] for r in rs if r["id_K1"] is not None]))
        k2 = [r["id_K2"] for r in rs if r["id_K2"] is not None]
        row["id_K2"] = float(np.mean(k2)) if k2 else float("nan")
        row["rank1_cal_K1"] = float(np.mean([r["rank1_cal_K1"] for r in rs if r["rank1_cal_K1"] is not None]))
        k2 = [r["rank1_cal_K2"] for r in rs if r["rank1_cal_K2"] is not None]
        row["rank1_cal_K2"] = float(np.mean(k2)) if k2 else float("nan")
        row["rank1_raw_K1"] = float(np.mean([r["rank1_raw_K1"] for r in rs]))
        fp = [x for r in rs for x in r["fp_wrong"]]
        row["fp_wrong"] = float(np.mean(fp)) if fp else float("nan")
        row["z_shuf_min_K1"] = float(min(r["lms"]["K1"]["z"] for r in rs))
        rows.append(row)
    return rows


def per_lang(R, genre, ntok, logo):
    out = {}
    for r in R:
        if r["genre"] == genre and r["ntok_target"] == ntok and r["logo"] == logo:
            d = out.setdefault(r["lang"], defaultdict(list))
            for k in ["K0", "K1", "K2", "K3"]:
                if k in r["lms"]: d[f"acc_{k}"].append(r["lms"][k]["acc_tok"]); d[f"accmax_{k}"].append(r["lms"][k]["acc_max"])
            d["id_K1"].append(r["id_K1"]); d["id_K2"].append(r["id_K2"])
    return {l: {k: (float(np.mean([x for x in v if x is not None])) if any(x is not None for x in v) else None)
                for k, v in d.items()} for l, d in out.items()}


def fmt(rows, cols):
    s = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows:
        s += "| " + " | ".join(("%.2f" % r[c]) if isinstance(r.get(c), float) else str(r.get(c, "")) for c in cols) + " |\n"
    return s


def threshold(rows, col, level=0.8):
    """smallest ntok at which col >= level, per logo target"""
    out = {}
    for lg in sorted({r["logo_target"] for r in rows}):
        rs = sorted([r for r in rows if r["logo_target"] == lg], key=lambda r: r["ntok"])
        hit = [r["ntok"] for r in rs if r.get(col, 0) >= level]
        out[lg] = hit[0] if hit else None
    return out


def indus_place(R):
    """compare Indus gains per LM with planted gains of that LM on its own-language vs other-language corpora
    at the Indus-like size (10k tokens), logo targets 0.2 and 0.4."""
    p = OUT / "indus_run.json"
    if not p.exists(): return None
    I = json.load(open(p))
    res = {}
    for name, v in I["lms"].items():
        m, q = name.split("@q"); q = float(q)
        lg = 0.2 if q == 0.2 else 0.4
        own, other = [], []
        for r in R:
            if r["genre"] != "names" or r["ntok_target"] != 10000 or r["logo"] != lg: continue
            for k, x in r["lms"].items():
                a = absname(r["lang"], k)
                if a == m: (own if m.split(":")[0] == r["lang"] else other).append(x["gain"])
        if not other:
            res[name] = dict(gain=v["gain"]); continue
        mu, sd = np.mean(other), np.std(other, ddof=1)
        res[name] = dict(gain=v["gain"], z_vs_wrong_planted=(v["gain"] - mu) / sd,
                         planted_wrong_mean=mu, planted_wrong_sd=sd,
                         planted_own_mean=float(np.mean(own)) if own else None)
    return I, res


def figure(rows_n, rows_p, anchors, indus):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 3, figsize=(16, 9.5))
    nts = sorted({r["ntok"] for r in rows_n}); lgs = sorted({r["logo_target"] for r in rows_n})
    def grid(col):
        Z = np.full((len(lgs), len(nts)), np.nan); Y = np.full(len(lgs), np.nan)
        for r in rows_n:
            Z[lgs.index(r["logo_target"]), nts.index(r["ntok"])] = r.get(col, np.nan)
        for i, lg in enumerate(lgs):
            Y[i] = np.mean([r["logo_achieved"] for r in rows_n if r["logo_target"] == lg])
        return Z, Y
    panels = [("rank1_cal_K1", "A. True language ranked FIRST of 9 candidate LMs\n(full lexicons; p<0.01 reached only for Finnish: 20%)"),
              ("rank1_cal_K2", "B. Related language ranked first (true lexicon absent)\n(p<0.01 reached only for Finnish)"),
              ("accmax_K1", "C. Sign values right, best-scoring key\nfull lexicon of the true language"),
              ("acc_K2", "D. Sign values right, blind search\nrelated language's lexicon only"),
              ("acc_K3", "E. Sign values right, blind search\nphonotactics only")]
    for ax, (col, title) in zip(axs.flat, panels):
        Z, Y = grid(col)
        im = ax.imshow(Z, origin="lower", aspect="auto", vmin=0, vmax=1, cmap="viridis")
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                if not np.isnan(Z[i, j]):
                    ax.text(j, i, "%.2f" % Z[i, j], ha="center", va="center", fontsize=8,
                            color="white" if Z[i, j] < 0.6 else "black")
        ax.set_xticks(range(len(nts))); ax.set_xticklabels([f"{n/1000:g}k" for n in nts])
        ax.set_yticks(range(len(lgs))); ax.set_yticklabels([f"{a:.2f}" for a in Y])
        ax.set_xlabel("corpus size, sign tokens (texts ~ tokens / 4.4 for Indus)")
        ax.set_ylabel("logogram share of word tokens (achieved)")
        ax.set_title(title, fontsize=10)
        # Indus: 10,005 tokens, logogram share unknown (plausibly 0.2-0.6)
        xi = np.interp(np.log(INDUS_TOK), np.log(nts), range(len(nts)))
        ax.plot([xi, xi], [0.5, len(lgs) - 1], color="red", lw=2.5)
        ax.text(xi, len(lgs) - 0.55, "Indus: 10k tokens, logogram share unknown", color="red", fontsize=8, ha="center", va="bottom",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
    ax = axs.flat[5]
    if anchors:
        Ks = sorted(anchors[0]["acc"].keys(), key=int) if False else sorted({int(k) for a in anchors for k in a["acc"]})
        for kn, c in [("K1", "C0"), ("K2", "C1"), ("K3", "C2")]:
            ys = [np.mean([a["acc"][str(K)][kn] for a in anchors if str(K) in a["acc"] and kn in a["acc"][str(K)]]) for K in Ks]
            ax.plot(Ks, ys, "o-", color=c, label={"K1": "full lexicon", "K2": "related language", "K3": "phonotactics"}[kn])
        ax.plot(Ks, [np.mean([a["f"][str(K)] for a in anchors]) for K in Ks], "k--", label="anchor tokens alone")
        ax.set_xscale("symlog", linthresh=5); ax.set_xticks(Ks); ax.set_xticklabels(Ks)
        ax.set_xlabel("anchors: number of sign values known (e.g. from a bilingual name)")
        ax.set_ylabel("share of syllabic sign tokens read right")
        ax.set_ylim(0, 1); ax.legend(fontsize=8)
        ax.set_title("F. Value of anchors at Indus size\n(10k tokens, logogram share 0.2-0.4)", fontsize=10)
    fig.suptitle("Decipherability phase diagram: planted real languages (Sanskrit, Tamil, Sumerian, Latin, Finnish) "
                 "in a simulated logo-syllabic script, name/title texts", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "phase_diagram.png", dpi=130)


def main():
    Rn = calibrate(load("names")); Rp = calibrate(load("prose")); Ra = load("anchors")
    rows_n = table(Rn, "names"); rows_p = table(Rp, "prose")
    cols = ["ntok", "logo_target", "logo_achieved", "n", "S", "mean_len", "acc_K0", "acc_K1", "accmax_K1", "acc_K2",
            "accmax_K2", "acc_K3", "accmax_K3", "wbt_K1", "wbt_K2", "wbt_K3", "gap_K1", "gap_K2", "gap_K3", "U_K0", "U_K1", "U_K2", "U_K3", "id_K1", "id_K2", "rank1_cal_K1", "rank1_cal_K2", "rank1_raw_K1", "fp_wrong", "z_shuf_min_K1"]
    txt = "## names\n" + fmt(rows_n, cols) + "\n## prose\n" + fmt(rows_p, cols)
    # anchors
    A = []
    for r in Ra:
        if "anchors" not in r: continue
        acc, f = {}, {}
        for K, d in r["anchors"].items():
            if K == "80": continue
            acc[K] = {k: v["acc_tok"] for k, v in d.items()}
            # share of syllabic tokens covered by the anchors themselves: acc = f + (1-f) acc_free
            f[K] = float(np.mean([(v["acc_tok"] - v["acc_free_tok"]) / (1 - v["acc_free_tok"])
                                  for v in d.values() if v["acc_free_tok"] < 1]))
        A.append(dict(lang=r["lang"], logo=r["logo"], acc=acc, f=f,
                      free={K: {k: v["acc_free_tok"] for k, v in d.items()} for K, d in r["anchors"].items() if K != "80"}))
    if A:
        Ks = sorted({int(k) for a in A for k in a["acc"]})
        txt += "\n## anchors (10k tokens, names; K known values drawn token-weighted)\n"
        txt += "| K | anchor tokens alone | total right K1 | K2 | K3 | non-anchor right K1 | K2 | K3 |\n|---|---|---|---|---|---|---|---|\n"
        for K in Ks:
            m = lambda kn, fld: np.mean([a[fld][str(K)][kn] for a in A if kn in a[fld].get(str(K), {})])
            txt += f"| {K} | %.2f | " % np.mean([a["f"][str(K)] for a in A]) + " | ".join(
                "%.2f" % m(kn, "acc") for kn in ["K1", "K2", "K3"]) + " | " + " | ".join(
                "%.2f" % m(kn, "free") for kn in ["K1", "K2", "K3"]) + " |\n"
        txt += "\nper language, total right (K1 / K2 / K3) at K=0, 10, 20, 40:\n"
        for l in LANGS:
            aa = [a for a in A if a["lang"] == l]
            if not aa: continue
            txt += l + ": " + "; ".join(f"K={K}: " + "/".join(
                ("%.2f" % np.mean([a["acc"][str(K)][kn] for a in aa])) if kn in aa[0]["acc"][str(K)] else "-"
                for kn in ["K1", "K2", "K3"]) + " (anchors alone %.2f)" % np.mean([a["f"][str(K)] for a in aa])
                for K in [0, 10, 20, 40]) + "\n"
    ind = indus_place(Rn)
    if ind:
        I, res = ind
        txt += "\n## Indus run (gain per token over shuffles; z vs the same LM's gains on planted WRONG-language corpora)\n"
        for k, v in sorted(res.items()):
            txt += f"{k}: gain={v['gain']:.3f} " + (f"z_vs_wrong={v['z_vs_wrong_planted']:.2f} own_planted_mean={v['planted_own_mean']}" if 'z_vs_wrong_planted' in v else "") + "\n"
    txt += "\n## thresholds (smallest token count with >=80% success)\n"
    for col in ["id_K1", "id_K2", "rank1_cal_K1", "rank1_cal_K2", "accmax_K1", "acc_K1", "acc_K2", "acc_K3"]:
        txt += f"names {col}: {threshold(rows_n, col)}\n"
        if rows_p: txt += f"prose {col}: {threshold(rows_p, col)}\n"
    txt += "\n## per language, names, 10k tokens\n"
    for lg in [0.0, 0.2, 0.4, 0.6]:
        txt += f"logo {lg}: {json.dumps(per_lang(Rn, 'names', 10000, lg))}\n"
    (OUT / "summary.md").write_text(txt)
    print(txt)
    figure(rows_n, rows_p, A, ind)
    res = dict(names=rows_n, prose=rows_p,
               thresholds={c: {"names": threshold(rows_n, c), "prose": threshold(rows_p, c)}
                           for c in ["id_K1", "id_K2", "accmax_K1", "acc_K1", "acc_K2", "acc_K3"]},
               indus=ind[1] if ind else None)
    json.dump(res, open(HERE / "results.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
