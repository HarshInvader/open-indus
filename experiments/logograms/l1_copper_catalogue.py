"""L1. Copper tablet catalogue (Mohenjo-daro): legend x other face (picture / one-sign face / text).

Sources (both read as data):
  * IM77 line file (Mahadevan 1977 + Input Data File 1980): one row per line; line 9 = a side with a
    field symbol and no text, so fs80 there is the PICTURE on that face. 135 copper text numbers.
  * ICIT (Wells/Fuls), type TAB:C: 230 objects incl. CISI vol. 2-3 tablets absent from M77; sides are
    the .1/.2 parts; the picture is only the coarse `symbol` field (unreliable on copper per paragorth).
ICIT legends are converted to Mahadevan numbers (bridge + copper parallels in common.W2M_EXTRA) only to
group copies of one legend into FAMILIES (edit distance <=1 or containment); evidence is then counted
per legend family, so the M77/ICIT overlap (same objects in both) cannot inflate counts.

Writes copper_tablets.csv (one row per tablet per source) and copper_tablet_types.csv (legend family x
other-face type, with tablet counts per source).
"""
from common import *

M77_PIC = {  # coarse classes of copper pictures (fs80)
    15: "unicorn", 45: "short-horned bull", 65: "buffalo", 75: "elephant", 91: "tiger", 101: "horned tiger",
    111: "rhinoceros", 113: "rhinoceros", 135: "goat-antelope (horns arching back)",
    137: "goat-antelope (twirled horns)", 139: "goat-antelope (twirled horns)", 141: "ox-antelope (short horns)",
    143: "ox-antelope (short horns)", 145: "ox-antelope (long curly horns)", 147: "ox-antelope (long curly horns)",
    163: "hare", 251: "composite animal", 290: "two-headed animal", 351: "uncertain bovine",
    520: "horned archer personage", 860: "endless knot", 950: "double-axe",
}
ICIT_PIC = {"Hare": "hare", "Anth": "horned archer personage", "Elep": "elephant", "Comp": "composite/two-headed (ICIT Comp)",
            "Gaur": "ox-antelope/gaur (ICIT Gaur)", "Loop": "endless knot", "Goat:8": "goat-antelope (twirled horns)",
            "Bull1:W": "unicorn", "Rhin": "rhinoceros", "Tigr": "tiger", "Bull": "bull (ICIT)", "Buff": "buffalo",
            "Hgls": "double-axe", "Othr": "other picture (ICIT Othr)", "Unknown": "unknown"}


def clean_m77(tok):
    t = tok.lstrip("*").lstrip("0")
    return "#" if t in ("", "0") else f"M{t}"


def m77_tablets():
    rows = [r for r in csv.DictReader(open(IM77)) if r["object_code"] == "5"]
    by = defaultdict(list)
    for r in rows:
        by[int(r["text_no"])].append(r)
    tabs = []
    for no, rs in sorted(by.items()):
        sides = defaultdict(list)
        for r in rs:
            sides[int(r["side"])].append(r)
        faces = []
        for sd, lines in sorted(sides.items()):
            pic = None; seq = []
            for r in sorted(lines, key=lambda r: int(r["line"])):
                fs = int(r["fs80"] or 0)
                if fs not in (0, 999):
                    pic = fs
                if r["line"] != "9" and r["signs_reading_order"].strip():
                    if seq: seq.append("|")
                    seq += [clean_m77(x) for x in r["signs_reading_order"].split()]
            faces.append(dict(side=sd, seq=seq, pic=pic))
        tabs.append(dict(source="M77", id=str(no), cisi="", faces=faces,
                         picture=next((M77_PIC.get(f["pic"], f"fs{f['pic']}") for f in faces if f["pic"]), None),
                         fs80=next((f["pic"] for f in faces if f["pic"]), None)))
    return tabs


def icit_tablets():
    I = [t for t in icit_texts() if t["type"] == "TAB:C"]
    by = defaultdict(list)
    for t in I:
        by[t["id"].split(".")[0]].append(t)
    tabs = []
    for k, parts in by.items():
        sym = parts[0]["symbol"]
        pic = None if sym in ("None", "-") else ICIT_PIC.get(sym, sym)
        faces = [dict(side=i + 1, seq=icit_to_m(p["seq"]), wseq=p["seq"], pic=None) for i, p in enumerate(parts)]
        tabs.append(dict(source="ICIT", id=k, cisi=parts[0]["cisi"], faces=faces, picture=pic, fs80=None, symbol=sym))
    return tabs


def classify(tab):
    """legend = longest text face (>=2 signs); other = picture / one-sign face / second text / none."""
    texts = [f for f in tab["faces"] if len(signs(f["seq"])) >= 2]
    ones = [f for f in tab["faces"] if len(signs(f["seq"])) == 1]
    texts.sort(key=lambda f: -len(signs(f["seq"])))
    legend = texts[0]["seq"] if texts else (ones[0]["seq"] if ones else [])
    second = texts[1]["seq"] if len(texts) > 1 else None
    sign_face = signs(ones[0]["seq"])[0] if (ones and texts) else None
    if tab["picture"] and sign_face:
        kind = "picture+sign"
    elif tab["picture"]:
        kind = "picture"
    elif sign_face:
        kind = "sign-face"
    elif second:
        kind = "second-text"
    elif len(tab["faces"]) >= 2:
        kind = "two-faced-other"
    else:
        kind = "one-face-only"
    return dict(legend=legend, second=second, sign_face=sign_face, kind=kind)


def families(legends):
    """Union legends that are copies/variants: edit distance <=1, or containment (>=3 signs);
    broken legends (with #) join a family when a break-free run of >=3 signs is contained in a member."""
    keys = sorted({" ".join(l) for l in legends if l})
    comp = [k for k in keys if "#" not in k.split()]
    par = {k: k for k in keys}
    def find(x):
        while par[x] != x: x = par[x]
        return x
    for i, a in enumerate(comp):
        A = signs(a.split())
        for b in comp[i + 1:]:
            B = signs(b.split())
            if len(A) < 2 or len(B) < 2:
                continue
            sa, sb = " ".join(A), " ".join(B)
            sr = " ".join(A[::-1])  # a left-to-right copy read in the other direction (MD 3375 / M-600)
            if lev(A, B) <= 1 or (min(len(A), len(B)) >= 3 and (sa in sb or sb in sa or (len(A) >= 4 and sr in sb))):
                par[find(a)] = find(b)
    for k in keys:
        if "#" in k.split() or "|" in k.split():
            rr = [r for r in runs(k.split()) if len(r) >= 3]
            hits = {find(c) for c in comp if c != k and any(" ".join(r) in c for r in rr)}
            if len(hits) == 1:  # join only an unambiguous family
                par[find(k)] = hits.pop()
    return {k: find(k) for k in keys}


def main():
    tabs = m77_tablets() + icit_tablets()
    for t in tabs:
        t.update(classify(t))
    fam = families([t["legend"] for t in tabs])
    # family label = most frequent complete member legend
    members = defaultdict(Counter)
    for t in tabs:
        k = " ".join(t["legend"])
        if k: members[fam[k]][k] += 1
    label = {}
    for root, c in members.items():
        comp = [(n, k) for k, n in c.items() if "#" not in k.split()]
        label[root] = max(comp)[1] if comp else max((n, k) for k, n in c.items())[1]
    fid = {root: f"F{i+1:02d}" for i, root in enumerate(sorted(label, key=lambda r: -sum(members[r].values())))}
    for t in tabs:
        k = " ".join(t["legend"])
        t["family"] = fid[fam[k]] if k else "F--"
        t["family_legend"] = label[fam[k]] if k else ""

    # per-tablet file
    with open(OUT / "copper_tablets.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "id", "cisi", "family", "family_legend", "legend", "kind", "picture", "fs80", "icit_symbol",
                    "sign_face", "second_text", "faces_raw"])
        for t in tabs:
            raw = " || ".join(" ".join(f.get("wseq", f["seq"])) + (f" [fs{f['pic']}]" if f["pic"] else "") for f in t["faces"])
            w.writerow([t["source"], t["id"], t["cisi"], t["family"], t["family_legend"], " ".join(t["legend"]), t["kind"],
                        t["picture"] or "", t["fs80"] or "", t.get("symbol", ""), t["sign_face"] or "",
                        " ".join(t["second"]) if t["second"] else "", raw])

    # type catalogue: family x other face
    types = defaultdict(lambda: dict(M77=[], ICIT=[]))
    for t in tabs:
        if t["kind"] in ("picture", "picture+sign"):
            other = ("picture", t["picture"])
        elif t["kind"] == "sign-face":
            sf = t["sign_face"]
            other = ("sign-face", sf + (" (horned-U family)" if sf in HORNED_U else ""))
        elif t["kind"] == "second-text":
            other = ("second-text", " ".join(t["second"]))
        else:
            other = (t["kind"], "")
        types[(t["family"], " ".join(t["legend"]), other)][t["source"]].append(t["cisi"] or t["id"] if t["source"] == "ICIT" else t["id"])
    with open(OUT / "copper_tablet_types.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "legend", "other_face_type", "other_face", "n_tablets_M77", "n_tablets_ICIT",
                    "M77_text_nos", "ICIT_ids"])
        for (f, lg, (ot, ov)), d in sorted(types.items(), key=lambda z: (z[0][0], z[0][2])):
            w.writerow([f, lg, ot, ov, len(d["M77"]), len(d["ICIT"]), " ".join(d["M77"]), " ".join(d["ICIT"])])

    # summary
    R = {}
    for src in ("M77", "ICIT"):
        R[f"kinds_{src}"] = dict(Counter(t["kind"] for t in tabs if t["source"] == src))
    print("tablet kinds:", R)
    fams = defaultdict(lambda: dict(pics=Counter(), signs=Counter(), n=0, seconds=Counter()))
    for t in tabs:
        F = fams[t["family"]]; F["n"] += 1; F["legend"] = t["family_legend"]
        if t["picture"]: F["pics"][t["picture"]] += 1
        if t["sign_face"]: F["signs"][t["sign_face"]] += 1
        if t["second"]: F["seconds"][" ".join(t["second"])] += 1
    print(f"\nlegend families: {len(fams)}")
    for f, F in sorted(fams.items()):
        if F["pics"] or F["signs"] or F["n"] >= 2:
            print(f"{f} n={F['n']:3d} {F['legend']:42s} pics={dict(F['pics'])} signs={dict(F['signs'])} 2nd={dict(F['seconds'])}")
    R["families"] = {f: dict(legend=F["legend"], n=F["n"], pictures=dict(F["pics"]), sign_faces=dict(F["signs"]),
                             second_texts=dict(F["seconds"])) for f, F in fams.items()}
    save_json("l1_catalogue", R)


if __name__ == "__main__":
    main()
