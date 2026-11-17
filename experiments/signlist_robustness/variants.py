"""Sign-list variants for the robustness test.

Every M77-based variant is a map  M sign -> label  (a partition of the 417 M77 signs), except the random
allograph splits, which relabel tokens. ICIT native is a separate corpus (Wells numbering).

    .venv/bin/python experiments/signlist_robustness/variants.py   # writes variants.json + prints a summary

Variants (frozen in docs/prereg/signlist_robustness.md):
  M77              identity (baseline)
  ICIT             Wells/Fuls native W numbering, own corpus (built in harness.py)
  parpola          M77 relabelled with every lump Parpola makes relative to Mahadevan, as observed in an
                   alignment of 150 CISI Mohenjo-daro seals (Parpola P codes, joyboseroy export) with ICIT
                   (same objects, Wells codes) and the Wells->Mahadevan bridge. Partial: signs absent from those
                   seals keep Mahadevan's split.
  lump_fish        all plain fish one sign, all corner-ticked fish one sign
  lump_numerals    stroke numerals lumped by (system, value) regardless of layout (e.g. M108+M109 = short 6)
  lump_jar_man     jar M342 with jar+stroke signs M343-M345; man variants; bearer; man+stick; man+jar; birds
  lump_all         all of the above + trees, rakes, ovals, leaf-in-oval, arcs, U-shapes, M347/M348 and the
                   Mahadevan-Wells unified clusters (shaunmortal unified_signs_v1)
  split_s1..s3     every sign with >= 50 M77 tokens split into 2 or 3 allographs, token by token at random
  img_hi/mid/lo    agglomerative clusters of Mahadevan's drawings (data/sign_images) at three cut heights
"""
import json, csv, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "sources"
ALL_M = [f"M{i}" for i in range(1, 418)]

FISH_PLAIN = ["M59", "M61", "M62", "M63", "M64", "M65", "M67", "M69", "M70", "M72", "M74", "M75"]
FISH_TICK = ["M60", "M66", "M68", "M71", "M73"]
FISH_CORE6 = ["M59", "M65", "M67", "M70", "M72", "M75"]       # README #11 fish family


def rng_list(a, b):
    return [f"M{i}" for i in range(a, b + 1)]


def strokes_groups():
    st = json.load(open(SRC / "shaunmortal_indus/data/stroke_signs.json"))
    g = defaultdict(list)
    for sysname in ("short", "tall"):
        for k, v in st[sysname].items():
            if k in ("99", "101"):      # M99 connective / M101 are not numerals in the lexicon
                continue
            g[f"{sysname}{v}"].append(f"M{k}")
    return {k: v for k, v in g.items() if len(v) > 1}


G_FISH = {"FISH": FISH_PLAIN, "TICKFISH": FISH_TICK}
G_JARMAN = {
    "JAR": ["M342", "M343", "M344", "M345"],
    "MAN": ["M1", "M3", "M4", "M5", "M6", "M7", "M8", "M18", "M19", "M20", "M21", "M22", "M23", "M24",
            "M38", "M39", "M40", "M41"],
    "BEARER": rng_list(12, 16),
    "MANSTICK": rng_list(25, 31),
    "MANJAR": ["M32", "M33", "M34", "M35", "M44"],
    "BIRD": rng_list(76, 81),
}
G_OTHER = {
    "TREE": ["M161", "M162", "M163", "M164", "M165", "M166", "M167", "M168", "M169"],
    "RAKE": ["M171", "M172", "M173", "M174"],
    "OVAL": ["M373", "M374"],
    "OVALBAR": ["M375", "M376", "M377", "M378"],
    "LEAFOVAL": ["M386", "M387", "M388", "M389", "M390"],
    "ARC": ["M287", "M288", "M293"],
    "UCUP": ["M328", "M329", "M330", "M331"],
    "HORNJAR": ["M347", "M348"],
    "INTERSECT": ["M403", "M404", "M405", "M406"],
}


def partition_from_groups(groups):
    lab = {m: m for m in ALL_M}
    for name, mem in groups.items():
        for m in mem:
            lab[m] = name
    return lab


def merge_groups(*gs):
    """Union several group dicts into one partition (transitive closure)."""
    par = {m: m for m in ALL_M}

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for g in gs:
        for mem in g.values():
            mem = [m for m in mem if m in par]
            for m in mem[1:]:
                par[f(m)] = f(mem[0])
    comp = defaultdict(list)
    for m in ALL_M:
        comp[f(m)].append(m)
    lab = {}
    for root, mem in comp.items():
        name = mem[0] if len(mem) == 1 else "G_" + "_".join(sorted(mem, key=lambda s: int(s[1:]))[:3]) + (f"_{len(mem)}" if len(mem) > 3 else "")
        for m in mem:
            lab[m] = name
    return lab


def unified_groups():
    u = json.load(open(SRC / "shaunmortal_indus/data/unified_signs_v1.json"))["clusters"]
    return {k: [x for x in v if x.startswith("M")] for k, v in u.items() if sum(x.startswith("M") for x in v) > 1}


# ------------------------------------------------------------------ Parpola (partial, from alignment)
def parpola_concordance():
    ic = [json.loads(l) for l in open(ROOT / "data/icit_texts.jsonl")]
    by = defaultdict(list)
    for r in ic:
        by[r["cisi"]].append(r)
    P = list(csv.DictReader(open(SRC / "joyboseroy_indus_decipher/data/cisi_real_corpus.csv")))
    B = json.load(open(SRC / "shaunmortal_indus/data/bridge_WM.json"))
    W2M = {f"W{int(k):03d}": [f"M{x}" for x in v["M"]] for k, v in B.items()}
    pairs = Counter(); aligned = 0
    for p in P:
        cid = p["inscription_id"].rstrip("ABCDEFabcdef")
        ps = p["sign_sequence"].split()[::-1]        # export is display order; reverse = reading order
        rs = by.get(cid, [])
        if not rs:
            continue
        w = [s for s in rs[0]["seq"] if s not in "|#"]
        if len(w) == len(ps):
            aligned += 1
            for a, b in zip(ps, w):
                if len(W2M.get(b, [])) == 1:
                    pairs[(a, W2M[b][0])] += 1
    pm = defaultdict(Counter)
    for (a, m), k in pairs.items():
        pm[a][m] += k
    groups, splits = {}, defaultdict(set)
    for a, c in pm.items():
        tot = sum(c.values())
        ms = [m for m, k in c.items() if k >= 2 and k / tot >= 0.2]
        for m in ms:
            splits[m].add(a)
        if len(ms) > 1:
            groups[a] = ms
    par_splits = {m: sorted(v) for m, v in splits.items() if len(v) > 1}
    purity = sum(c.most_common(1)[0][1] for c in pm.values()) / max(1, sum(pairs.values()))
    return groups, par_splits, dict(aligned_seals=aligned, aligned_tokens=sum(pairs.values()),
                                    P_signs=len(pm), purity=round(purity, 3),
                                    M_signs_covered=len({m for (_, m) in pairs}))


# ------------------------------------------------------------------ image clusters
def image_features(size=32):
    from PIL import Image, ImageFilter
    feats = []
    for m in ALL_M:
        im = Image.open(ROOT / f"data/sign_images/{m}.png").convert("L")
        a = np.array(im) < 128
        ys, xs = np.nonzero(a)
        a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = a.shape; s = max(h, w)
        pad = np.zeros((s, s), bool); pad[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = a
        im2 = Image.fromarray((pad * 255).astype(np.uint8)).resize((size, size), Image.BILINEAR)
        im2 = im2.filter(ImageFilter.GaussianBlur(1.5))
        v = np.array(im2, float).ravel()
        v /= np.linalg.norm(v) + 1e-9
        feats.append(np.concatenate([v, [0.5 * np.log(w / h)]]))
    return np.array(feats)


def image_partitions(targets=(360, 300, 240)):
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    X = image_features()
    Z = linkage(pdist(X, "euclidean"), "average")
    out = {}
    for name, k in zip(("img_hi", "img_mid", "img_lo"), targets):
        cl = fcluster(Z, k, criterion="maxclust")
        comp = defaultdict(list)
        for m, c in zip(ALL_M, cl):
            comp[c].append(m)
        lab = {}
        for mem in comp.values():
            nm = mem[0] if len(mem) == 1 else "I_" + "_".join(mem[:3]) + (f"_{len(mem)}" if len(mem) > 3 else "")
            for m in mem:
                lab[m] = nm
        out[name] = lab
    return out


# ------------------------------------------------------------------ random allograph splits
def split_spec(seed, min_tokens=50):
    sys.path.insert(0, str(ROOT))
    from corpus.load import m77_texts
    c = Counter(s for t in m77_texts() for s in t["seq"] if s not in "|#")
    r = np.random.default_rng(seed)
    return {s: int(r.choice([2, 3])) for s, n in sorted(c.items()) if n >= min_tokens}


def build_all():
    V = {"M77": {m: m for m in ALL_M}}
    pg, psplits, pinfo = parpola_concordance()
    V["parpola"] = merge_groups(pg)
    V["lump_fish"] = partition_from_groups(G_FISH)
    V["lump_numerals"] = partition_from_groups(strokes_groups())
    V["lump_jar_man"] = partition_from_groups(G_JARMAN)
    V["lump_all"] = merge_groups(G_FISH, strokes_groups(), G_JARMAN, G_OTHER, unified_groups())
    V.update(image_partitions())
    splits = {f"split_s{i}": split_spec(i) for i in (1, 2, 3)}
    meta = {"parpola_alignment": pinfo, "parpola_groups": pg, "parpola_splits_not_applied": psplits,
            "n_labels": {k: len(set(v.values())) for k, v in V.items()},
            "split_signs": {k: len(v) for k, v in splits.items()}}
    return V, splits, meta


if __name__ == "__main__":
    V, S, meta = build_all()
    json.dump({"partitions": V, "splits": S, "meta": meta}, open(HERE / "variants.json", "w"), indent=0)
    print(json.dumps(meta, indent=1))
    for k in ("img_hi", "img_mid", "img_lo"):
        grp = defaultdict(list)
        for m, l in V[k].items():
            grp[l].append(m)
        big = sorted([g for g in grp.values() if len(g) > 1], key=len, reverse=True)
        print(k, "multi-member clusters", len(big), "largest:", big[:6])
        for probe in ("M342", "M59", "M60", "M109", "M99", "M267", "M391"):
            print("   ", probe, "->", grp[V[k][probe]][:10])
