"""Red team C2: are Indus seal cores more novel than Ur III personal names once units, length and
inventory are matched?  C2a same-recipe Ur III core, C2b length strata, C2c inventory matching.

usage: .venv/bin/python experiments/redteam_identifiers/c2.py
"""
import sys, os, json
from collections import Counter, defaultdict
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "experiments/identifiers")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from id_lib import *  # noqa
from c1 import ur3_seals, cun_signs, I, texts  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
M = 100
KINGS = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}szul-gi", "{d}i-bi2-{d}suen", "ur-{d}namma", "{d}szul-gi-ra"}
royal = lambda lg: any(w in KINGS or w == "lugal" for l in lg for w in l)
nr = lambda keys: 1 - coverage(list(Counter(keys).values()), M) if len(keys) >= M else float("nan")


def main():
    out = {}
    by = defaultdict(list)
    for o, t in zip(I, texts): by[o["site"]].append(t)
    big = [s for s in by if len(by[s]) >= M]
    # Indus reproduction + frame token share
    tok = [s for t in texts for s in t]
    f_share = np.mean([is_frame(s) for s in tok])
    out["indus_frame_token_share"] = float(f_share)
    out["indus"] = {s: dict(text=nr(by[s]), core=nr([core_key(t) for t in by[s]]), n=len(by[s])) for s in big}
    seals = ur3_seals()
    provs = [p for p in seals if len(seals[p]) >= M]
    allleg = [v for p in provs for v in seals[p].values()]
    wc = Counter(w for v in allleg for l in v for w in l)
    tot = sum(wc.values()); cum = 0; frame = set()
    for w, c in wc.most_common():
        if cum / tot >= f_share: break
        frame.add(w); cum += c
    out["ur3_frame_words"] = {"n": len(frame), "share": cum / tot, "top": [w for w, _ in wc.most_common(len(frame))][:25]}
    ucore = lambda v: tuple(w for l in v for w in l if w not in frame)
    out["ur3"] = {}
    for p in provs:
        V = list(seals[p].values()); W = [v for v in V if not royal(v)]
        out["ur3"][p] = dict(legend=nr([json.dumps(v) for v in V]), core_same_recipe=nr([ucore(v) for v in V]),
                             core_same_recipe_nonroyal=nr([ucore(v) for v in W]),
                             name_line=nr([json.dumps(v[0]) for v in W]), n=len(V))
    # C2b length strata (written signs): Indus core length vs Ur III name line length
    icore = defaultdict(list)
    for t in texts: icore[len(core_key(t))].append(core_key(t))
    names = [v[0] for p in provs for v in seals[p].values() if not royal(v)]
    nlen = defaultdict(list)
    for nm in names: nlen[sum(len(cun_signs(w)) for w in nm)].append(json.dumps(nm))
    # MD-only Indus and Umma-only Ur III, plus pooled
    md = defaultdict(list)
    for t in by["Mohenjo-daro"]: md[len(core_key(t))].append(core_key(t))
    um = defaultdict(list)
    for v in seals["Umma"].values():
        if not royal(v): um[sum(len(cun_signs(w)) for w in v[0])].append(json.dumps(v[0]))
    rows = []
    for k in range(0, 12):
        rows.append(dict(len=k, indus_pooled_n=len(icore[k]), indus_pooled=nr(icore[k]), indus_md_n=len(md[k]), indus_md=nr(md[k]),
                         ur3_pooled_n=len(nlen[k]), ur3_pooled=nr(nlen[k]), ur3_umma_n=len(um[k]), ur3_umma=nr(um[k])))
    out["C2b"] = rows
    # length distributions
    out["indus_core_len_mean"] = float(np.mean([len(core_key(t)) for t in texts]))
    out["ur3_nameline_len_mean_signs"] = float(np.mean([sum(len(cun_signs(w)) for w in nm) for nm in names]))
    # C2c inventory: quantile-map Ur III name-line signs onto Indus core-sign mass profile
    ic = Counter(s for t in texts for s in core_key(t))
    itypes = [s for s, _ in ic.most_common()]; imass = np.cumsum([ic[s] for s in itypes]) / sum(ic.values())
    uc = Counter(s for nm in names for w in nm for s in cun_signs(w))
    utypes = [s for s, _ in uc.most_common()]; um_ = np.cumsum([uc[s] for s in utypes]) / sum(uc.values())
    mid = um_ - np.array([uc[s] for s in utypes]) / sum(uc.values()) / 2
    mp = {s: itypes[min(int(np.searchsorted(imass, m)), len(itypes) - 1)] for s, m in zip(utypes, mid)}
    out["inventory"] = dict(indus_core_types=len(itypes), ur3_name_sign_types=len(utypes),
                            indus_core_entropy=float(-sum((c / sum(ic.values())) * np.log2(c / sum(ic.values())) for c in ic.values())),
                            ur3_name_entropy=float(-sum((c / sum(uc.values())) * np.log2(c / sum(uc.values())) for c in uc.values())),
                            mapped_types=len(set(mp.values())))
    recode = lambda nm: tuple(mp[s] for w in nm for s in cun_signs(w))
    out["C2c"] = {}
    for p in provs:
        W = [v for v in seals[p].values() if not royal(v)]
        out["C2c"][p] = dict(name_line=nr([json.dumps(v[0]) for v in W]), name_line_signs=nr([tuple(s for w in v[0] for s in cun_signs(w)) for v in W]),
                             name_line_mapped=nr([recode(v[0]) for v in W]), core_same_recipe_mapped=nr([tuple(mp.get(s, s) for w in ucore(v) for s in cun_signs(w)) for v in W]))
    # Indus core that is a single run (one slot) -- closest to "one name"
    out["indus_single_slot_core"] = {s: nr([core_key(t) for t in by[s] if len(decompose(t)[1]) == 1]) for s in big}
    json.dump(out, open(os.path.join(HERE, "c2.json"), "w"), indent=1, default=float)
    for k, v in out.items():
        if k == "C2b":
            for r in v: print("C2b", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in r.items()})
        else: print(k, v)


if __name__ == "__main__":
    main()
