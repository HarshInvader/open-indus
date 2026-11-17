"""Part A: red team of the naming_sim outlier claim (standalone 0.91, pol_ex 0.14, both_pos 0.71, numerals 41%).

A1 inventory: real name lists at Indus inventory and Zipf profile
    raw       : n = min(800, #types) distinct types (naming_sim setting)
    trunc     : only types whose elements are all among the K most frequent elements (K = Indus dev core inventory, 286)
    merge     : elements randomly merged onto K classes with the Indus core-sign frequency profile (homography model:
                a logographic script with ~300 signs writing a name stock of thousands of elements)
    merge_slot: same, but merging only within slot-preference groups (first-only / second-only / other)
A2 core definition: Indus statistics on grammar-free units (whole texts, numerals removed, edge-stripped segments,
    top-10-stripped segments) vs the grammar cores.
A3 segmentation: real names re-segmented into SYLLABLES (one sign = one syllable model), raw and at Indus inventory.
A4 numerals: share of distinct texts with a numeral, Indus by object type, vs whole-legend short-label corpora
    (seal legends, tags, Linear B labels, Latin labels, Egyptian phrases) where numerals are possible in the frame.
Usage: .venv/bin/python -I experiments/core_genre/partA_redteam.py  -> partA.json
"""
import sys, json, re
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

B = 30
NCAP = 800


# ---------------------------------------------------------------- syllabification
VOW = {
    "sanskrit": set("aAiIuUfFxXeEoO"),
    "old_english": set("aeiouyæ"), "old_high_german": set("aeiouy"), "old_norse": set("aeiouyæø"),
    "greek": set("αεηιουω"),
}


def syllabify(w, V):
    """Onset-maximal-lite: each syllable = (consonants) vowel-run (+ one coda consonant if >= 2 consonants follow)."""
    out, i, n = [], 0, len(w)
    if not any(c in V for c in w):
        return [w]
    cur = ""
    while i < n:
        while i < n and w[i] not in V:
            cur += w[i]; i += 1
        while i < n and w[i] in V:
            cur += w[i]; i += 1
        j = i
        while j < n and w[j] not in V:
            j += 1
        ncons = j - i
        if j == n:  # word end: all remaining consonants are coda
            cur += w[i:j]; i = j
        elif ncons >= 2:
            cur += w[i]; i += 1
        out.append(cur); cur = ""
    if cur:
        out[-1] += cur
    return out


def syll_types(nm):
    t, _ = C.N.load(nm)
    if nm == "ur3":     # sign level: split every element at hyphens, {d} determinative separate
        out = set()
        for x in t:
            s = []
            for e in x:
                s += [p for p in re.split(r"[-]|(?<=\})", e.replace("{d}", "{d}-")) if p]
            out.add(tuple(s))
        return sorted(out)
    if nm == "chinese_given":   # already one character = one syllable
        return t
    V = VOW[nm]
    return sorted({tuple(s for e in x for s in syllabify(e, V)) for x in t})


# ---------------------------------------------------------------- jobs
def job(a):
    kind, nm, seed = a
    rng = np.random.default_rng(seed)
    q = C.indus_profile("dev")
    K = len(q)
    if kind.startswith("syll"):
        types = syll_types(nm); cls = None
    else:
        types, cls = C.N.load(nm)
    n = min(NCAP, len(types))
    rows = []
    for b in range(B):
        if kind in ("raw", "syll"):
            s = C.sample_types(types, n, rng)
        elif kind == "trunc":
            f = Counter(e for t in types for e in t)
            top = {e for e, _ in f.most_common(K)}
            pool = [t for t in types if all(e in top for e in t)]
            if len(pool) < 50:
                return a, None
            s = C.sample_types(pool, min(n, len(pool)), rng)
        elif kind in ("merge", "merge_slot", "syll_merge"):
            s0 = C.sample_types(types, n, rng)
            s = C.merge_inventory(s0, q, rng, slot_preserving=(kind == "merge_slot"))
            cls = None
        rows.append(C.S.compute(s, rng, cls, 20))
    return a, rows


def summarize(rows):
    out = {}
    for k in C.PRIMARY6 + ["tpt"]:
        v = np.array([r[k] for r in rows], float); v = v[np.isfinite(v)]
        out[k] = None if len(v) == 0 else dict(mean=round(float(v.mean()), 3), lo=round(float(np.percentile(v, 2.5)), 3),
                                               hi=round(float(np.percentile(v, 97.5)), 3))
    return out


def indus_rows(types, n, seed=0, Bi=B):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(Bi):
        s = C.sample_types(types, min(n, len(types)), rng)
        rows.append(C.S.compute(s, rng, None, 20))
    return rows


def numerals():
    from corpus.load import dev_heldout
    num = C.numeral_signs()
    out = {}
    for split in ("dev", "heldout"):
        T = dev_heldout(version=2)[0 if split == "dev" else 1]
        by = Counter(); hit = Counter()
        for t in T:
            ot = t.get("object_type") or "?"
            h = any(s in num for s in t["seq"])
            for g in ("all", ot):
                by[g] += 1; hit[g] += h
        out[f"indus_{split}"] = {g: dict(n=by[g], share=round(hit[g] / by[g], 3)) for g in by if by[g] >= 20}
    # whole-legend corpora: share of distinct units with any numeral token
    D = C.ROOT / "experiments/short_labels/data"
    isnum = {
        "cun_seal_ur3": lambda x: x.startswith("N:"), "cun_seal_ob": lambda x: x.startswith("N:"),
        "cun_seal_oakk": lambda x: x.startswith("N:"), "cun_tag": lambda x: x.startswith("N:"),
        "linb_label": lambda x: x in ("NUM", "num"), "lina_label": lambda x: x == "num",
        "lat_label": lambda x: bool(re.fullmatch(r"[IVXLC]+", x)) and len(x) >= 2,
        "egy_nom": lambda x: x in set("𓏺𓏻𓏼𓏽𓏾𓏿𓐀𓐁𓐂𓎆𓎇𓎈𓍢𓆼"),
    }
    for nm, f in isnum.items():
        T = C.jl_types(D / f"{nm}.jsonl")
        out[nm] = dict(n=len(T), share=round(float(np.mean([any(f(x) for x in t) for t in T])), 3))
    T = C.jl_types(C.ROOT / "sources/paragorth_Indus-/data/codelib/linear_b.jsonl")
    out["linear_b_lines"] = dict(n=len(T), share=round(float(np.mean([any(x == "NUM" for x in t) for t in T])), 3))
    T = C.jl_types(C.ROOT / "sources/paragorth_Indus-/data/codelib/heraldry.jsonl")
    hn = {"deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze"}
    out["heraldry"] = dict(n=len(T), share=round(float(np.mean([any(x in hn for x in t) for t in T])), 3))
    return out


if __name__ == "__main__":
    res = {}
    # Indus targets
    ti, _ = C.indus_cores("dev"); th, _ = C.indus_cores("heldout")
    res["indus_core_dev"] = summarize(indus_rows(ti, 800, Bi=1))
    res["indus_core_heldout"] = summarize(indus_rows(th, 423, Bi=1))
    res["indus_inventory"] = dict(K=len(C.indus_profile("dev")), tokens=sum(len(x) for x in ti), types=len(ti))
    print("indus", res["indus_core_dev"], flush=True)

    # A2 grammar-free units
    a2 = {}
    for split, n in (("dev", 800), ("heldout", 423)):
        for mode in ("whole", "nonum", "edge", "top10"):
            r = C.indus_texts(split, mode)
            types, dropped = (r, []) if mode in ("whole", "nonum") else r
            a2[f"{split}_{mode}"] = dict(n_types=len(types), dropped_signs=dropped,
                                         stats=summarize(indus_rows(types, n, seed=1, Bi=10 if len(types) > n else 1)))
            print("A2", split, mode, len(types), {k: v["mean"] if v else None for k, v in a2[f'{split}_{mode}']["stats"].items()}, flush=True)
    res["A2_core_definition"] = a2

    # A1 + A3
    jobs = [(k, nm, 7) for nm in C.NAME_LISTS for k in ("raw", "trunc", "merge", "merge_slot")]
    jobs += [(k, nm, 9) for nm in ("sanskrit", "old_english", "greek", "ur3", "chinese_given") for k in ("syll", "syll_merge")]
    with Pool(2) as p:
        out = p.map(job, jobs)
    a1, a3 = {}, {}
    for (kind, nm, _), rows in out:
        tgt = a3 if kind.startswith("syll") else a1
        tgt.setdefault(nm, {})[kind] = None if rows is None else summarize(rows)
        if rows:
            print(kind, nm, {k: summarize(rows)[k]["mean"] if summarize(rows)[k] else None for k in C.PRIMARY6}, flush=True)
    res["A1_inventory"] = a1; res["A3_syllables"] = a3

    # range tables and Indus z vs the real range per variant
    rng_tab = {}
    for variant in ("raw", "trunc", "merge", "merge_slot"):
        rng_tab[variant] = {}
        for k in C.PRIMARY6:
            vals = [a1[nm][variant][k]["mean"] for nm in a1 if a1[nm].get(variant) and a1[nm][variant][k]]
            his = [a1[nm][variant][k]["hi"] for nm in a1 if a1[nm].get(variant) and a1[nm][variant][k]]
            los = [a1[nm][variant][k]["lo"] for nm in a1 if a1[nm].get(variant) and a1[nm][variant][k]]
            rng_tab[variant][k] = dict(min_mean=min(vals), max_mean=max(vals), max_hi=max(his), min_lo=min(los))
    res["A1_ranges"] = rng_tab
    res["A4_numerals"] = numerals()
    print(json.dumps(res["A4_numerals"], indent=0), flush=True)
    json.dump(res, open(C.HERE / "partA.json", "w"), indent=1, ensure_ascii=False)
