"""Confirmatory replication (pre-registered in docs/prereg/substitution.md).

For every dev candidate equation (dev q<0.05; the system-consistent subset is the primary
family), count NEW independent frames: L-tier events mined on dev + new texts in which at
least one of the two texts is new. New = (a) M77 held-out (dev_heldout v2), (b) ICIT texts
from sites absent from M77, translated to Mahadevan numbers with the W->M bridge (texts kept
only if every sign maps to exactly one M sign).
p per equation: the same (slot, k)-stratified frame-unit permutation null, applied to the
new-text units only. BH within each family.
Usage: .venv/bin/python experiments/substitution/run_heldout.py [nperm]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import (bh, clean, distinct, icit_texts, load_m77, mine, perm_null, save_results,  # noqa: E402
                    stats, to_units, M77_SITES_ICIT)


def icit_new_in_M():
    b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    w2m = {int(k): "M%d" % v["M"][0] for k, v in b.items() if len(v["M"]) == 1}
    out, kept, total = set(), 0, 0
    for t in distinct(icit_texts()):
        if t["site"] in M77_SITES_ICIT or t["site"] in ("Unknown",):
            continue
        c = clean(t["seq"])
        if not c:
            continue
        total += 1
        try:
            m = tuple(w2m[int(x[1:])] for x in c)
        except (KeyError, ValueError):
            continue
        kept += 1
        out.add(m)
    return sorted(out), kept, total


def replicate(D, new, cands, nperm, seed):
    new = sorted(set(new) - set(D))
    T = D + new
    isnew = set(range(len(D), len(T)))
    ev = [e for e in mine(T, tier="L") if e["a"] in isnew or e["b"] in isnew]
    units = to_units(ev)
    st, eqs = stats(units)
    track = {c: max(eqs.get(c, 0), 1) for c in cands}
    _, eqp = perm_null(units, nperm=nperm, seed=seed, kmin=1, eq_track=track)
    rows = []
    for c in cands:
        k = eqs.get(c, 0)
        p = eqp[c]["p"] if k > 0 else 1.0
        rows.append(dict(X=c[0], Y=" ".join(c[1]), k_new=k, lam=eqp[c]["lam"], p=p))
    q = bh([r["p"] for r in rows])
    for r, qq in zip(rows, q):
        r["q"] = float(qq)
    return dict(n_new_texts=len(new), n_new_events=len(ev), n_new_units=len(units),
                n_replicated=sum(1 for r in rows if r["q"] < 0.05 and r["k_new"] > 0),
                n_attested=sum(1 for r in rows if r["k_new"] > 0), rows=rows)


if __name__ == "__main__":
    nperm = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    res = json.load(open(HERE / "results.json"))
    dev = res["indus_dev"]["L"]
    sce = [(r["X"], tuple(r["Y"].split())) for r in res["dev_sce"]["sce"]]
    allsig = [(r["X"], tuple(r["Y"].split())) for r in dev["sig"]]
    D, H = load_m77()
    I, kept, total = icit_new_in_M()
    out = {"icit_new_kept": kept, "icit_new_total": total}
    for name, new in (("heldout", H), ("icit_new", I)):
        for fam, cands in (("sce", sce), ("all_sig", allsig)):
            r = replicate(D, new, cands, nperm, seed=7)
            out["%s_%s" % (name, fam)] = r
            print(name, fam, {k: v for k, v in r.items() if k != "rows"})
            for row in sorted(r["rows"], key=lambda z: z["p"])[:8]:
                print("    %s = %s  k_new=%d lam=%.3f p=%.3g q=%.3g" % (row["X"], row["Y"], row["k_new"], row["lam"],
                                                                     row["p"], row["q"]))
    save_results("heldout", out)
