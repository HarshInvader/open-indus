"""Shared data for the rank-ladder experiment (Baer's method on Indus title/frame signs).

Native Wells (W) numbering on ICIT, because the physical metadata (width, height,
material, emblem, site, phase) lives in ICIT. M77 equivalents (via
sources/shaunmortal_indus/data/bridge_WM.json) are used only for the transitivity
test on Mahadevan's transcription.

Unit: DISTINCT texts. Physical variables of all objects carrying one distinct text are
pooled (mean log area, modal emblem/material/site), so repeated title strings on many
seals (STATE F27) count once.

Held-out: an ICIT family split built here (same rule as corpus splits_v2: texts within
one edit, or one contained in the other, are one family). Whole families go to one
side, site-stratified, seed 2026, 30% of distinct texts held out.
"""
import json, math, random, sys, hashlib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts, dev_heldout, distinct  # noqa: E402
from corpus.build import _close  # noqa: E402  (pure function, no side effects)

HERE = Path(__file__).resolve().parent
SPLIT = HERE / "icit_family_split.json"

# ---- frame signs (pre-registered list; roles from functional_reading/lexicon.csv) ----
# feature name -> set of W signs.  M equivalents in comments (bridge_WM.json).
FRAME = {
    "OP_W817": {"W817"},          # M267 opener
    "OP_W861": {"W861"},          # M267 opener (Wells split)
    "OP_W820": {"W820"},          # M391 opener
    "OP_W920": {"W920"},          # M293 opener
    "CN_W002": {"W002"},          # M99 connective
    "CN_W060": {"W060"},          # M123 connective
    "TI_W760": {"W760"},          # M347 pre-jar title element
    "TI_W100": {"W100"},          # M8 pre-jar title element
    "TI_W176": {"W176"},          # M48 pre-jar title element?
    "TB_W70x": {"W704", "W705", "W706"},  # M336 title block head
    "TB_W033": {"W033"},          # M89 tall-3 (M336-M89-M211 block)
    "TB_W255": {"W255"},          # M51 block (M51-M130-M149)
    "TB_W590": {"W590"},          # M249 block (M249-M161)
    "MJ_W741": {"W741"},          # M343 handled jar (F12 small-seal sign; reference)
    "CL_W740": {"W740"},          # M342 jar closer
    "CL_W520": {"W520"},          # M211 closer
    "CL_W390": {"W390"},          # M162/M169 family closer
    "CL_W405": {"W405"},          # M162/M169 family closer
    "CL_W407": {"W407"},          # M169 closer (round/copper)
    "CL_W527": {"W527"},          # closer-class (final 83%)
    "CL_W368": {"W368"},          # closer-class
    "CL_W151": {"W151"},          # M12 closer (swaps with M342 M176)
    "CL_W15x": {"W154", "W156"},  # M15 closer
    "PC_W400": {"W400"},          # M176 post-closer clitic
    "PC_W090": {"W090"},          # M1 post-closer
}
W2F = {w: f for f, ws in FRAME.items() for w in ws}

# M77 equivalents for the transitivity replication on Mahadevan's corpus
FRAME_M = {
    "OP_M267": "M267", "OP_M391": "M391", "OP_M293": "M293", "CN_M99": "M99", "CN_M123": "M123",
    "TI_M347": "M347", "TI_M8": "M8", "TI_M48": "M48", "TB_M336": "M336", "TB_M89": "M89",
    "TB_M51": "M51", "TB_M249": "M249", "MJ_M343": "M343", "CL_M342": "M342", "CL_M211": "M211",
    "CL_M162": "M162", "CL_M169": "M169", "CL_M12": "M12", "CL_M15": "M15", "PC_M176": "M176",
    "PC_M1": "M1",
}
M2F = {v: k for k, v in FRAME_M.items()}


def emblem(sym):
    s = (sym or "-").split(":")[0]
    if s == "Bull1":
        return "unicorn"
    m = {"Gaur": "gaur", "Zebu": "zebu", "Elep": "elephant", "Rhin": "rhino", "Tigr": "tiger",
         "Buff": "buffalo", "Goat": "goat", "Bull": "shorthorn", "None": "none", "-": "unknown",
         "?": "unknown", "Unknown": "unknown"}
    return m.get(s, "other")


RARE_MAT = {"faience", "silver", "copper", "terracotta", "agate", "paste", "shell", "ivory", "bone",
            "gold", "stone", "limestone", "metal", "kaolinite", "gypsum"}


def material(m):
    m = (m or "-").lower().strip()
    if m in ("steatite", "soft stone"):
        return "steatite"
    if m in ("-", "", "clay"):
        return "unknown" if m != "clay" else "clay"
    return m


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def lines(seq):
    out, cur = [], []
    for s in seq:
        if s == "|":
            out.append(cur); cur = []
        else:
            cur.append(s)
    out.append(cur)
    return [l for l in out if any(x != "#" for x in l)]


def num(x):
    try:
        return float(x)
    except Exception:
        return 0.0


# ---------------- ICIT family split ----------------
def build_split():
    T = icit_texts()
    key2site, key2signs = {}, {}
    for t in T:
        k = " ".join(t["seq"])
        key2site.setdefault(k, t["site"])
        key2signs[k] = signs(t["seq"])
    keys = sorted(key2site)
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    sg = [key2signs[k] for k in keys]
    # index by length to avoid useless comparisons (|la-lb| > 1 only via containment)
    for i in range(len(keys)):
        a = sg[i]
        if not a:
            continue
        for j in range(i + 1, len(keys)):
            b = sg[j]
            if b and _close(a, b):
                parent[find(keys[i])] = find(keys[j])
    fam = defaultdict(list)
    for k in keys:
        fam[find(k)].append(k)
    rng = random.Random(2026)
    by_site = defaultdict(list)
    for root, ks in fam.items():
        site = Counter(key2site[k] for k in ks).most_common(1)[0][0]
        by_site[site].append(sorted(ks))
    held, nfh = set(), 0
    for s, fams in sorted(by_site.items()):
        fams.sort(); rng.shuffle(fams)
        target, n = 0.30 * sum(len(f) for f in fams), 0
        for f in fams:
            if n >= target:
                break
            held.update(f); n += len(f); nfh += 1
    res = dict(seed=2026, unit="ICIT text family (<=1 edit or contained copy)", heldout_fraction=0.30,
               heldout=sorted(held), n_distinct=len(keys), n_families=len(fam), n_families_heldout=nfh)
    res["sha256"] = hashlib.sha256("\n".join(res["heldout"]).encode()).hexdigest()
    json.dump(res, open(SPLIT, "w"), indent=0)
    return res


def heldout_keys():
    if not SPLIT.exists():
        build_split()
    return set(json.load(open(SPLIT))["heldout"])


# ---------------- distinct-text seal table ----------------
def seal_table(split="dev", types=("SEAL:S",)):
    """One row per distinct text among seals of the given types.
    split: 'dev', 'heldout' or 'all'."""
    held = heldout_keys()
    groups = defaultdict(list)
    for t in icit_texts():
        if types and t["type"] not in types:
            continue
        sg = signs(t["seq"])
        if not sg:
            continue
        groups[" ".join(t["seq"])].append(t)
    rows = []
    for k, objs in groups.items():
        side = "heldout" if k in held else "dev"
        if split != "all" and side != split:
            continue
        areas = [num(o["width_mm"]) * num(o["height_mm"]) for o in objs]
        areas = [a for a in areas if a > 20]
        em = Counter(emblem(o["symbol"]) for o in objs).most_common()
        em = next((e for e, _ in em if e != "unknown"), "unknown")
        mats = Counter(material(o["material"]) for o in objs).most_common()
        mat = next((m for m, _ in mats if m != "unknown"), "unknown")
        seq = objs[0]["seq"]
        sg = signs(seq)
        feats = Counter(W2F[s] for s in sg if s in W2F)
        rows.append(dict(
            key=k, seq=seq, signs=sg, length=len(sg), n_lines=len(lines(seq)),
            complete=all(o["complete"] for o in objs), site=Counter(o["site"] for o in objs).most_common(1)[0][0],
            phase=objs[0]["phase"], type=objs[0]["type"], n_obj=len(objs),
            log_area=(sum(math.log(a) for a in areas) / len(areas)) if areas else None,
            emblem=em, material=mat, feats=set(feats), split=side))
    return rows


def strata(rows, with_length=True):
    """site x length-bin x n_lines stratum label (length capped at 7)."""
    out = []
    for r in rows:
        L = min(r["length"], 7)
        out.append((r["site"], L if with_length else 0, min(r["n_lines"], 2)))
    return out


def resid_by_strata(y, st):
    """Residual of y from its stratum mean (fixed-effect control)."""
    g = defaultdict(list)
    for i, s in enumerate(st):
        g[s].append(i)
    res = [0.0] * len(y)
    for s, idx in g.items():
        m = sum(y[i] for i in idx) / len(idx)
        for i in idx:
            res[i] = y[i] - m
    return res


def strat_perm(labels, st, rng):
    """Permute labels within strata."""
    g = defaultdict(list)
    for i, s in enumerate(st):
        g[s].append(i)
    out = list(labels)
    for s, idx in g.items():
        vals = [labels[i] for i in idx]
        rng.shuffle(vals)
        for i, v in zip(idx, vals):
            out[i] = v
    return out


if __name__ == "__main__":
    r = build_split()
    print({k: v for k, v in r.items() if k != "heldout"}, len(r["heldout"]))


# ---------------- glyph footprint (sensitivity control) ----------------
_FP = None


def footprint(sg):
    """Sum of glyph widths (Mahadevan drawing bounding-box width / 107 px, the common glyph
    height) for a W-sign sequence; unbridged signs get the median width. Controls for
    'wide signs need a bigger seal' instead of sign count."""
    global _FP
    if _FP is None:
        import numpy as np
        from PIL import Image
        b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
        w = {}
        for k, v in b.items():
            p = ROOT / f"data/sign_images/M{v['M'][0]}.png"
            if p.exists():
                im = np.array(Image.open(p).convert("L")) < 128
                xs = np.where(im.any(0))[0]
                w["W%03d" % int(k)] = (xs.max() - xs.min() + 1) / 107 if len(xs) else None
        vals = sorted(x for x in w.values() if x)
        _FP = (w, vals[len(vals) // 2])
    w, med = _FP
    return sum(w.get(s) or med for s in sg)
