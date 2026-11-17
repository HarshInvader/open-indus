"""Build the shared machine-readable Indus corpus.

Inputs (cloned read-only into sources/):
  - M77: Mahadevan 1977 concordance, exported from indusscript.in (paragorth/Indus- data/im77).
    Verified: 13,372 sign tokens (= Mahadevan's published total), sign 342 = 1,395 tokens.
  - ICIT: Wells/Fuls Interactive Corpus of Indus Texts via yajnadevam/lipi (field-cady export).
    Stored end-first (jar sign 740 first in 1,195 of 1,214 R/L texts and 53/56 L/R texts),
    so reading order = reversed string. The 'sanskrit'/'translation' columns are one
    researcher's proposed readings and are deliberately dropped.

Outputs (data/):
  m77_lines.jsonl   one record per line of text, reading order, metadata
  m77_texts.jsonl   one record per object side (lines joined with '|')
  icit_texts.jsonl  one record per ICIT inscription, reading order, segments split at breaks
  splits.json       fixed dev / held-out split over DISTINCT texts (seed 1977)

Conventions: sign tokens are strings ('M342', 'W740'). A break/illegible sign is never a
token: sequences are cut into 'segments' at breaks, and 'complete' marks lines with no break.
"""
import csv, json, random, re, hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "sources"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)


def m77():
    rows = list(csv.DictReader(open(SRC / "paragorth_Indus-/data/im77/im77_corpus_lines.csv")))
    lines = []
    for r in rows:
        raw = r["signs_clean"].split()
        if not raw:
            continue
        segs, cur = [], []
        for s in raw:
            if s == "0":
                if cur:
                    segs.append(cur)
                cur = []
            else:
                cur.append("M" + s)
        if cur:
            segs.append(cur)
        signs = ["M" + s for s in raw if s != "0"]
        lines.append(dict(
            text_no=int(r["text_no"]), side=int(r["side"]), line=int(r["line"]),
            site=r["site"], object_type=r["object_type"], direction=r["direction"],
            fs80=int(r["fs80"] or 0), fs_category=r["fs_category"], fs_description=r["fs_description"],
            level=r["level"], locus=r["locus"],
            signs=signs, segments=segs, complete="0" not in raw,
            doubtful=[int(x) for x in r["doubtful_positions"].split(";") if x.strip().isdigit()] if r["doubtful_positions"] else [],
        ))
    with open(OUT / "m77_lines.jsonl", "w") as f:
        for l in lines:
            f.write(json.dumps(l) + "\n")
    # object-side texts: join lines in line order with a '|' marker
    by = defaultdict(list)
    for l in lines:
        by[(l["text_no"], l["side"])].append(l)
    texts = []
    for (tn, side), ls in sorted(by.items()):
        ls.sort(key=lambda x: x["line"])
        seq = []
        for i, l in enumerate(ls):
            if i:
                seq.append("|")
            for g, segm in enumerate(l["segments"]):
                if g: seq.append("#")  # break / illegible passage
                seq += segm
        texts.append(dict(text_no=tn, side=side, site=ls[0]["site"], object_type=ls[0]["object_type"],
                          fs80=ls[0]["fs80"], fs_category=ls[0]["fs_category"],
                          seq=seq, complete=all(l["complete"] for l in ls), n_lines=len(ls)))
    with open(OUT / "m77_texts.jsonl", "w") as f:
        for t in texts:
            f.write(json.dumps(t) + "\n")
    return lines, texts


def icit():
    rows = list(csv.DictReader(open(SRC / "field-cady_indus_valley_script_corpus/inscriptions.csv")))
    out = []
    for r in rows:
        t = r["text"].strip()
        if not re.search(r"\d{3}", t):
            continue
        # reverse to reading order; '/' line breaks become '|'
        toks = re.findall(r"\d{3}|[\[\]/+]", t)[::-1]
        seq, segs, cur, complete = [], [], [], True
        for k in toks:
            if k in "[]":
                complete = False
                continue
            if k == "+":
                continue
            if k == "/":
                seq.append("|"); continue
            if k in ("000", "999"):
                complete = False
                seq.append("#")
                if cur:
                    segs.append(cur)
                cur = []
                continue
            seq.append("W" + k); cur.append("W" + k)
        if cur:
            segs.append(cur)
        out.append(dict(id=r["id"], cisi=r["cisi"], site=r["site"], region=r["region"],
                        type=r["type"], material=r["material"], symbol=r["symbol"],
                        direction=r["dir."].strip(), period=r["period"], phase=r["phase"],
                        seq=seq, segments=segs, complete=complete,
                        width_mm=r["horizontal(mm)"], height_mm=r["vertical(mm)"]))
    with open(OUT / "icit_texts.jsonl", "w") as f:
        for t in out:
            f.write(json.dumps(t) + "\n")
    return out


def splits(texts):
    """Held-out split over DISTINCT sign sequences, stratified by site.
    All objects carrying the same sequence fall on the same side (mould rule)."""
    rng = random.Random(1977)
    key2site = {}
    for t in texts:
        k = " ".join(t["seq"])
        key2site.setdefault(k, t["site"])
    by_site = defaultdict(list)
    for k, s in key2site.items():
        by_site[s].append(k)
    held = set()
    for s, ks in sorted(by_site.items()):
        ks.sort(); rng.shuffle(ks)
        held.update(ks[: round(0.25 * len(ks))])
    res = dict(seed=1977, unit="distinct M77 side-sequence", heldout_fraction=0.25,
               heldout=sorted(held), n_distinct=len(key2site))
    res["sha256"] = hashlib.sha256("\n".join(res["heldout"]).encode()).hexdigest()
    json.dump(res, open(OUT / "splits.json", "w"), indent=0)
    return res


def _close(a, b):
    """True if sign lists a, b differ by <=1 edit, or the shorter (>=3 signs) is a
    contiguous part of the longer (a broken copy of the same legend).
    Edit links need both texts >= 4 signs, otherwise short texts chain the corpus together."""
    if len(a) > len(b):
        a, b = b, a
    la, lb = len(a), len(b)
    if la >= 3 and lb - la >= 1:
        for i in range(lb - la + 1):
            if b[i:i + la] == a:
                return True
    if lb - la > 1 or la < 4:
        return False  # one edit on a 1-3 sign text is too weak to call it a copy
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def splits_v2(texts):
    """Held-out split over TEXT FAMILIES (red-team fix, 2026-11-14).
    v1 put near-copies on both sides: 251 of 554 held-out texts were within one sign
    of a dev text. Here distinct sequences are linked when within one edit or one is a
    contiguous part of the other; whole connected families go to one side."""
    rng = random.Random(1977)
    key2site, key2signs = {}, {}
    for t in texts:
        k = " ".join(t["seq"])
        key2site.setdefault(k, t["site"])
        key2signs[k] = [s for s in t["seq"] if s not in ("|", "#")]
    keys = sorted(key2site)
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    sg = [key2signs[k] for k in keys]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if sg[i] and sg[j] and _close(sg[i], sg[j]):
                parent[find(keys[i])] = find(keys[j])
    fam = defaultdict(list)
    for k in keys:
        fam[find(k)].append(k)
    by_site = defaultdict(list)
    for root, ks in fam.items():
        site = max(sorted(set(key2site[k] for k in ks)), key=lambda s: sum(key2site[k] == s for k in ks))
        by_site[site].append(sorted(ks))
    held, nfam_held = set(), 0
    for s, fams in sorted(by_site.items()):
        fams.sort(); rng.shuffle(fams)
        target, n = 0.25 * sum(len(f) for f in fams), 0
        for f in fams:
            if n >= target:
                break
            held.update(f); n += len(f); nfam_held += 1
    res = dict(seed=1977, unit="M77 text family (<=1 edit or contained copy)", heldout_fraction=0.25,
               heldout=sorted(held), n_distinct=len(keys), n_families=len(fam), n_families_heldout=nfam_held)
    res["sha256"] = hashlib.sha256("\n".join(res["heldout"]).encode()).hexdigest()
    json.dump(res, open(OUT / "splits_v2.json", "w"), indent=0)
    return res


if __name__ == "__main__":
    lines, texts = m77()
    it = icit()
    sp = splits(texts)
    import sys
    if (OUT / "splits_v2.json").exists() and "--force-split" not in sys.argv:
        sp2 = json.load(open(OUT / "splits_v2.json"))  # frozen; the original build was hash-seed dependent
    else:
        sp2 = splits_v2(texts)
    print(f"split v2: {len(sp2['heldout'])} of {sp2['n_distinct']} distinct sequences in "
          f"{sp2['n_families_heldout']} of {sp2['n_families']} families held out, sha256 {sp2['sha256'][:16]}")
    ntok = sum(len(l["signs"]) for l in lines)
    print(f"M77: {len(lines)} lines, {len(texts)} object-sides, {ntok} sign tokens, "
          f"{len({s for l in lines for s in l['signs']})} sign types")
    print(f"ICIT: {len(it)} inscriptions, {sum(len(t['segments']) for t in it)} segments")
    print(f"split: {len(sp['heldout'])} of {sp['n_distinct']} distinct M77 sequences held out, sha256 {sp['sha256'][:16]}")
