"""Corpora for genres_scratch: M77 (splits_v2), ICIT (own family split), known-answer corpora.
Labels are attached to units but never read by the models."""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "experiments/grammar"))
import glib  # noqa: E402
from corpus.load import dev_heldout  # noqa: E402

OBJ = {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet", "copper tablet": "copper",
       "pottery graffito": "pottery"}
SITES = {"Mohenjodaro", "Harappa", "Lothal", "Kalibangan", "Chanhudaro"}


def m77():
    dev, ho = dev_heldout(version=2)
    out = []
    for split, src in (("dev", dev), ("heldout", ho)):
        us = []
        for t in src:
            u = glib.unit_from(t["seq"], t["complete"], obj=OBJ.get(t["object_type"], "other"),
                               site=t["site"] if t["site"] in SITES else "other", key=" ".join(t["seq"]),
                               text_no=t["text_no"], fs=t.get("fs_category"))
            if u["runs"]:
                us.append(u)
        out.append(us)
    return out


def icit_reg(tp):
    if tp == "SEAL:S": return "seal_sq"
    if tp == "SEAL:R": return "seal_rect"
    if tp in ("SEAL:C", "SEAL:CY"): return "seal_round"
    if tp.startswith("SEAL"): return "seal_other"
    if tp == "TAB:I": return "tab_incised"
    if tp == "TAB:B": return "tab_basrelief"
    if tp == "TAB:C": return "tab_copper"
    if tp.startswith("TAG"): return "tag"
    if tp.startswith("PO"): return "pottery"
    return "other"


def icit():
    us = glib.icit_units()
    reg_sites = Counter(u["site"] for u in us)
    for u in us:
        u["reg"] = icit_reg(u["type"])
        u["shape"] = {"seal_sq": "S", "seal_rect": "R", "seal_round": "C"}.get(u["reg"])
        u["foreign"] = u["site"] in glib.FOREIGN
        s = u["site"]
        u["sitegrp"] = "foreign" if u["foreign"] else (s if reg_sites[s] >= 100 else "other")
    import gs
    return gs.family_split(us, 0.25, seed=34)


def _load(name):
    return [json.loads(l)["seq"] for l in open(ROOT / f"experiments/short_labels/data/{name}.jsonl")]


def known(corpus, total=2270, seed=34):
    if corpus == "cun":
        mix = [("ur3_seal", "cun_seal_ur3", .50), ("ob_seal", "cun_seal_ob", .25), ("tag", "cun_tag", .15),
               ("brick", "cun_brick", .10)]
    else:
        mix = [("label", "lat_label", .30), ("other", "lat_short", .70)]
    rng = random.Random(seed)
    units, seen = [], set()
    avail = {}
    for lab, f, w in mix:
        pool = []
        for s in _load(f):
            s = [x for x in s if x not in ("|", "#", "")]
            k = " ".join(s)
            if 1 <= len(s) <= 17 and k not in seen:
                seen.add(k); pool.append(s)
        rng.shuffle(pool)
        n = int(round(w * total))
        avail[lab] = (len(pool), n)
        for s in pool[:n]:
            units.append(glib.unit_from(s, True, genre=lab))
    import gs
    tr, te = gs.family_split(units, 0.25, seed=seed)
    return tr, te, avail
