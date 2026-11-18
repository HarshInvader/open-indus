"""Hand recode (coder 2 = N1 reading recode_sheet.csv in shuffled order, codes taken in reverse table order),
done after the prereg hash and before any outcome. Codes typed here from reading; not derived from code.py.
Writes recode.csv and kappa.json (agreement vs code.py's fate.csv)."""
import csv, json, os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sheet = pd.read_csv(os.path.join(HERE, "recode_sheet.csv"), dtype=str)
# ---- Harappa (Vats) items: exceptions to all-zero
V_BROKEN = {23, 26, 34, 52, 68, 90, 97, 109, 117, 133, 144, 156, 159, 162, 170, 179, 191}
V_UNFIN = {68, 97, 136, 150, 184}
V_WORN = {154}
V_HOARD = {154}
V_BURIAL = {45, 81, 195}
V_SURF1 = {51, 138, 145, 147, 154, 184}
V_SURF_BLANK = {45, 68, 141}
# ---- Mohenjo-daro (FEM) items
M_OPEN = {3, 4, 7, 9, 11, 14, 25, 27, 30, 49, 62, 67, 71, 80, 83, 87, 98, 103, 108, 111, 112, 128, 131, 140, 160,
          163, 166, 173, 181, 194, 197}
M_NOFS = {74, 105}          # no findspot: OPEN/ROOM blank
M_NOROOM = {57, 126}        # findspot without a room: ROOM 0 (block only / house only)
M_PROXY = {15, 30, 114, 125, 130, 157, 165}
M_SURF1 = {105}
rows = []
for r in sheet.itertuples():
    i = int(r.item)
    d = dict(item=i, source=r.source, serial=r.serial)
    if r.source.startswith("Vats"):
        d.update(BROKEN=int(i in V_BROKEN), UNFINISHED=int(i in V_UNFIN), WORN=int(i in V_WORN), HOARD=int(i in V_HOARD),
                 BURIAL=int(i in V_BURIAL), SURFACE="" if i in V_SURF_BLANK else int(i in V_SURF1))
    else:
        o = "" if i in M_NOFS else int(i in M_OPEN)
        rm = "" if i in M_NOFS else int(i not in M_OPEN and i not in M_NOROOM)
        d.update(OPEN=o, ROOM=rm, BROKEN_PROXY=int(i in M_PROXY), SURFACE=int(i in M_SURF1))
    rows.append(d)
rec = pd.DataFrame(rows)
rec.to_csv(os.path.join(HERE, "recode.csv"), index=False)
rec = pd.read_csv(os.path.join(HERE, "recode.csv"), dtype=str).fillna("")
rec = rec.apply(lambda c: c.str.replace(r"\.0$", "", regex=True))
fate = pd.read_csv(os.path.join(HERE, "fate.csv"), dtype=str).drop_duplicates(["source", "serial"])
m = rec.merge(fate, on=["source", "serial"], suffixes=("_h", "_r"))


def kappa(a, b):
    a, b = list(a), list(b)
    n = len(a)
    if n == 0:
        return None, 0, None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (None if pe == 1 else round((po - pe) / (1 - pe), 3)), n, round(po, 3)


out = {}
for src, codes in [("Vats1940_EH", ["BROKEN", "UNFINISHED", "WORN", "HOARD", "BURIAL", "SURFACE"]),
                   ("Mackay1938_FEM", ["OPEN", "ROOM", "BROKEN_PROXY", "SURFACE"])]:
    g = m[m.source == src]
    for c in codes:
        h = g[c + "_h"].astype(str); r_ = g[c + "_r"].astype(str)
        ok = h.isin(["0", "1"]) & r_.isin(["0", "1"])
        k, n, po = kappa(h[ok].astype(int), r_[ok].astype(int))
        out[f"{src}:{c}"] = dict(kappa=k, n_both=n, agreement=po, hand_pos=int((h[ok] == "1").sum()),
                                 rule_pos=int((r_[ok] == "1").sum()), missing_mismatch=int((~ok & (h.isin(['0','1']) | r_.isin(['0','1']))).sum()),
                                 disagree_items=g[ok & (h != r_)]["item"].tolist())
json.dump(out, open(os.path.join(HERE, "kappa.json"), "w"), indent=1, default=str)
for k, v in out.items():
    print(k, v)
