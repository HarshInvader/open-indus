"""Seed labels from earlier experiments (initialisation of the class induction only).
M77: functional_reading lexicon first role (OPENER, CONNECTIVE, NUMERAL, CLOSER, BRACKETED-FISH, POST-CLOSER;
everything else medial), with structure/sign_table opener/closer overriding a 'medial' default.
Wells: the M77 seed of the bridged M sign(s), plus graphic Wells numerals and the connective W002."""
import csv
from collections import Counter
from glib import ROOT, W2M, NUM


def seeds_m77():
    st = {r["sign"]: r["class"] for r in csv.DictReader(open(ROOT / "experiments/structure/sign_table.csv"))}
    out = {}
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
        if r["kind"] != "sign" or not r["roles"]:
            continue
        role = r["roles"].split(" ")[0]
        lab = {"OPENER": "opener", "CONNECTIVE": "connective", "NUMERAL(short)": "numeral",
               "NUMERAL(tall)": "numeral", "UNIT/MEASURE": "numeral", "CLOSER": "closer",
               "BRACKETED-FISH": "closer", "POST-CLOSER": "post-closer"}.get(role, "medial")
        if lab == "medial" and st.get(r["item"]) in ("opener", "closer"):
            lab = st[r["item"]]
        out[r["item"]] = lab
    return out


SEED_M = seeds_m77()
SEED_W = {}
for w, ms in W2M.items():
    labs = [SEED_M[m] for m in ms if m in SEED_M]
    if labs:
        SEED_W[w] = Counter(labs).most_common(1)[0][0]
for w in NUM["ICIT"]:
    SEED_W[w] = "numeral"
SEED_W["W002"] = "connective"
