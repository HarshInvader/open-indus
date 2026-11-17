"""Build the finding x variant table, verdicts (pre-registered rules), results.json and ledger rows.
    .venv/bin/python experiments/signlist_robustness/summarise.py
"""
import json, csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VARS = ["M77", "ICIT", "parpola", "lump_fish", "lump_numerals", "lump_jar_man", "lump_all",
        "split_s1", "split_s2", "split_s3", "img_hi", "img_mid", "img_lo"]
FAMILY = {"ICIT": "ICIT", "parpola": "parpola", "lump_fish": "lump_fish", "lump_numerals": "lump_numerals",
          "lump_jar_man": "lump_jar_man", "lump_all": "lump_all", "split_s1": "splits", "split_s2": "splits",
          "split_s3": "splits", "img_hi": "images", "img_mid": "images", "img_lo": "images"}
TESTS = {"T1": "order beats permutations (#1)", "T2": "ticked fish -> final slot (#3)", "T3": "M109+M59 fixed (#5)",
         "T4": "object-type registers (#6)", "T5": "L-R reversals (#7)", "T6": "name cores 1-2 word signs (#10a)",
         "T7": "fixed pair order (#10b)", "T8": "fish lexical class (#11)", "T9": "functional parse vs shuffle (#9)"}


def stat(t, r):
    if r.get("NT"): return "NT", None, r["NT"]
    if t == "T1": return f"{r['share']:.3f} vs {r['chance']:.3f} (n={r['n_runs']})", r["p"], r["share"] - r["chance"]
    if t == "T2": return f"{r['final']}/{r['tokens']} final ({r['share']:.2f}); plain {r['plain_share']:.2f}; null {r['null_mean']:.2f}", r["p"], r["share"] - r["plain_share"]
    if t == "T3": return f"{r['k']}/{r['n']} vs base {r['base']:.3f}", r["p"], r["k"] / max(r["n"], 1) - r["base"]
    if t == "T4": return f"{r['above']}/{r['n_classes']} classes above null95; mean AUC {r['mean_auc']:.3f}", None, r["mean_auc"] - 0.5
    if t == "T5": return f"{r['as_labelled']}/{r['n_clean']} ({r['share']:.2f})", r["p"], r["share"] - 0.5
    if t == "T6": return f"len-1 {r['len1_share']:.2f}; standalone {r['standalone_tok']:.2f} ({r['n_core_types']} core types)", None, r["len1_share"] - 0.14
    if t == "T7": return f"{r['agree']}/{r['occurrences']} ({r['share']})", r["p"], (r["share"] or 0.5) - 0.5
    if t == "T8":
        f = lambda x: "-" if not x else f"{x['p']:.4f}"
        return f"SC1 p={f(r['SC1'])}, SC5 p={f(r['SC5'])}, SC7 p={f(r['SC7'])}; {r['n_pass']}/3 pass", min(x["p"] for x in (r["SC1"], r["SC5"], r["SC7"]) if x), r["n_pass"] - 0.5
    if t == "T9": return f"{r['coverage']:.3f} vs shuffle {r['shuffle']:.3f} (z={r['z']})", None, r["coverage"] - r["shuffle"]


def verdict(rows, unit):
    out = {}
    for t in TESTS:
        fam_res = {}
        for v in VARS[1:]:
            r = rows[v][unit][t]
            if r.get("survives") is None: continue
            fam_res.setdefault(FAMILY[v], []).append((r["survives"], r["dir"]))
        fails, rev = [], False
        for fam, xs in fam_res.items():
            ok = [s for s, _ in xs]
            if fam in ("splits", "images"):
                failed = sum(not s for s in ok) >= 2
            else:
                failed = not ok[0]
            if failed: fails.append(fam)
            rev |= any(d is not None and d < 0 for s, d in xs if not s)
        if not fails: v_ = "ROBUST"
        elif len(fails) <= 2 and not rev: v_ = "SENSITIVE"
        else: v_ = "FRAGILE"
        nt = [v for v in VARS[1:] if rows[v][unit][t].get("survives") is None]
        out[t] = dict(verdict=v_, failed_families=fails, reversed=rev, not_testable=nt)
    return out


def main():
    raw = {v: json.load(open(HERE / "raw" / f"{v}.json")) for v in VARS if (HERE / "raw" / f"{v}.json").exists()}
    rows = {}
    for v, d in raw.items():
        rows[v] = {}
        for unit in ("type", "token"):
            rows[v][unit] = {}
            for t in TESTS:
                r = d[unit][t]
                s, p, dr = stat(t, r)
                rows[v][unit][t] = dict(stat=s, p=p, dir=dr if not r.get("NT") else None, survives=r.get("survives"), raw=r)
    ver = {u: verdict(rows, u) for u in ("type", "token")} if len(raw) == len(VARS) else None
    # markdown table
    lines = []
    for unit in ("type", "token"):
        lines.append(f"\n### Unit = {unit.upper()}\n")
        lines.append("| finding | variant | statistic | p | survives? |")
        lines.append("|---|---|---|---|---|")
        for t, nm in TESTS.items():
            for v in raw:
                r = rows[v][unit][t]
                sv = "NT" if r["survives"] is None else ("yes" if r["survives"] else "**NO**")
                p = "" if r["p"] is None else f"{r['p']:.1e}"
                lines.append(f"| {t} {nm} | {v} | {r['stat']} | {p} | {sv} |")
    (HERE / "table.md").write_text("\n".join(lines) + "\n")
    # compact grid
    grid = ["| finding | " + " | ".join(raw) + " | verdict (type) | verdict (token) |", "|---" * (len(raw) + 3) + "|"]
    for t, nm in TESTS.items():
        cells = []
        for v in raw:
            a = rows[v]["type"][t]["survives"]; b = rows[v]["token"][t]["survives"]
            c = lambda x: "NT" if x is None else ("Y" if x else "N")
            cells.append(f"{c(a)}/{c(b)}")
        vt = ver["type"][t]["verdict"] if ver else "?"; vk = ver["token"][t]["verdict"] if ver else "?"
        grid.append(f"| {t} {nm} | " + " | ".join(cells) + f" | {vt} | {vk} |")
    (HERE / "grid.md").write_text("\n".join(grid) + "\n")
    meta = json.load(open(HERE / "variants.json"))["meta"]
    res = {"prereg": "docs/prereg/signlist_robustness.md", "variants_meta": meta,
           "n_labels_in_corpus": {v: raw[v]["n_labels"] for v in raw},
           "ho_dropped_as_copies": {v: raw[v]["n_ho_dropped_as_copies"] for v in raw},
           "verdicts": ver,
           "rows": {v: {u: {t: {k: x for k, x in rows[v][u][t].items() if k != "raw"} for t in TESTS} for u in ("type", "token")} for v in raw}}
    json.dump(res, open(HERE / "results.json", "w"), indent=1, default=str)
    print("\n".join(grid))
    if ver:
        for u in ver:
            for t, x in ver[u].items(): print(u, t, x)
    return rows, ver


if __name__ == "__main__":
    main()
