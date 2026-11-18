"""Append every experiments/*/ledger_rows.csv row not yet in docs/test_ledger.csv, then recompute the
q-value columns over the whole ledger with the same rules as build_ledger.py (BH with unlisted family
members padded at p = 1; global, per area, hierarchical, all).

Run from the repo root:  .venv/bin/python -I experiments/ledger/merge_rows.py [--dry]
Prints the added ids and which confirmatory tests gain or lose q_global < 0.05.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "test_ledger.csv"
COLS = ["id", "claim", "area", "file", "statistic", "p_value", "p_source", "ci", "n", "distinct_text_unit", "split", "mode",
        "family", "family_size", "replicated_independently", "readme_claim", "q_global", "q_area", "q_hier", "q_all", "note"]


def num(v):
    try:
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)
    q = p[o] * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(q, 1); return out


def padded(rows):
    items = [(i, num(r["p_value"])) for i, r in rows if num(r["p_value"]) is not None]
    listed = defaultdict(int); fsize = {}
    for i, r in rows:
        listed[r["family"]] += 1
        fsize[r["family"]] = max(fsize.get(r["family"], 0), int(num(r["family_size"]) or 0))
    for f, n in listed.items():
        items += [(None, 1.0)] * max(0, fsize[f] - n)
    return items


def correct(rows):
    ix = list(enumerate(rows))
    conf = [(i, r) for i, r in ix if r["mode"].strip() == "confirmatory"]
    for r in rows:
        r.update(q_global="", q_area="", q_hier="", q_all="")
    it = padded(conf); q = bh([p for _, p in it])
    for (i, _), qq in zip(it, q):
        if i is not None: rows[i]["q_global"] = qq
    for area in sorted({r["area"] for _, r in conf}):
        sub = [(i, r) for i, r in conf if r["area"] == area]
        it = padded(sub); q = bh([p for _, p in it])
        for (i, _), qq in zip(it, q):
            if i is not None: rows[i]["q_area"] = qq
    fams = defaultdict(list)
    for i, r in conf: fams[r["family"]].append((i, r))
    simes, within = {}, {}
    for f, sub in fams.items():
        it = padded(sub)
        if all(i is None for i, _ in it): continue
        ps = np.array([p for _, p in it]); m = len(ps)
        simes[f] = float(min(1.0, np.min(np.sort(ps) * m / np.arange(1, m + 1))))
        within[f] = list(zip([i for i, _ in it], bh(ps)))
    fl = sorted(simes); fq = bh([simes[f] for f in fl]); F = len(fl)
    sel = {f for f, qq in zip(fl, fq) if qq <= 0.05}; R = len(sel)
    for f in fl:
        for i, qw in within[f]:
            if i is None: continue
            rows[i]["q_hier"] = min(1.0, qw * F / max(R, 1)) if f in sel else 1.0
    it = padded(ix); q = bh([p for _, p in it])
    for (i, _), qq in zip(it, q):
        if i is not None: rows[i]["q_all"] = qq


def main():
    rows = list(csv.DictReader(open(LEDGER, newline="")))
    before = {r["id"]: num(r["q_global"]) for r in rows}
    have = {r["id"] for r in rows}
    added = []
    for f in sorted(ROOT.glob("experiments/*/ledger_rows.csv")):
        for r in csv.DictReader(open(f, newline="")):
            if r.get("id") and r["id"] not in have:
                rows.append({c: r.get(c, "") or "" for c in COLS}); have.add(r["id"]); added.append(r["id"])
    correct(rows)
    gained = [r["id"] for r in rows if isinstance(r["q_global"], float) and r["q_global"] < .05
              and r["id"] in before and not (before[r["id"]] is not None and before[r["id"]] < .05)]
    lost = [r["id"] for r in rows if r["id"] in before and before[r["id"]] is not None and before[r["id"]] < .05
            and not (isinstance(r["q_global"], float) and r["q_global"] < .05)]
    new_sig = [r["id"] for r in rows if r["id"] in added and isinstance(r["q_global"], float) and r["q_global"] < .05]
    print(f"added {len(added)} rows; ledger now {len(rows)}")
    print("new rows with q_global < 0.05:", new_sig)
    print("existing rows that now pass q_global:", gained)
    print("existing rows that no longer pass q_global:", lost)
    if "--dry" in sys.argv:
        return
    with open(LEDGER, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.3g}" if isinstance(r[k], float) else r[k]) for k in COLS})


if __name__ == "__main__":
    main()
