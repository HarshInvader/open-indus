"""Per-object findspot table for Harappa (Vats 1940), linked to M77 (text_no = 4000 + EH serial) and ICIT.

Run: .venv/bin/python -I experiments/reg_harappa/data.py   (after prose.py)
Writes findspots.csv and data_summary.json in experiments/reg_harappa/.

Sources
  register : experiments/old_registers/registers.csv rows Vats1940_EH (Mound/Area, find no., depth below surface)
  prose    : prose_refs.csv (citations of seal plates in the narrative chs. I-VI: square, find no., depth)
Rules (fixed before any sign was tabulated by findspot)
  * one citation per serial: a 'list' citation (No.; Square; Depth after the plate ref) beats a 'prose' one;
    among several of one kind the first is kept; conflicting squares are flagged.
  * a citation is ACCEPTED only if it is corroborated. If both find nos. are readable they must agree
    (after OCR normalisation S->8, O->0, I/l->1; one-character edit allowed); a conflict rejects.
    If either find no. is missing: the cited depth is within 1 ft of the register depth, or (prose kind)
    the page-header mound equals the register mound AND the square lies within 400 characters before.
  * square 'I 9/24' -> big square 'I9' (locus, primary unit) and sub-square 24 (5x5 grid of the big square).
  * mound: register mound; if missing, page-header mound of an accepted citation; 'P' header = OCR of 'F'.
  * depth: register depth below surface (ft); else accepted list depth; else M77 level.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa: E402

OUT = Path(__file__).resolve().parent


def nfind(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    s = str(s).replace(" ", "").replace("-", "").replace(".", "")
    s = re.sub(r"(?<=[A-Za-z])[lI](?=\d)", "1", s)
    s = re.sub(r"(?<=\d)[lI]", "1", s)
    s = re.sub(r"(?<=\d)[oO]", "0", s)
    s = re.sub(r"[oO](?=\d)", "0", s) if re.match(r"^[oO]\d", s) else s
    s = s.lower()
    if re.fullmatch(r"[0-9sSoOiIl]+[a-z]?", s) and re.search(r"\d", s):
        head, tail = (s[:-1], s[-1]) if s[-1] in "abcdefgh" and len(s) > 1 else (s, "")
        head = head.translate(str.maketrans("soil", "8011"))
        s = head + tail
    return s or None


def edit1(a, b):
    """Levenshtein distance <= 1."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def main():
    reg = pd.read_csv(ROOT / "experiments/old_registers/registers.csv", dtype=str)
    reg = reg[reg.source == "Vats1940_EH"].copy()
    reg["serial"] = reg.object_no.str.extract(r"(\d+)")[0].astype(int)
    reg["mound"] = reg.findspot.str.extract(r"Mound/Area\s+(\w+)")[0]
    reg["depth_reg"] = pd.to_numeric(reg.depth_ft, errors="coerce")
    reg = reg.drop_duplicates("serial", keep="first")
    pr = pd.read_csv(OUT / "prose_refs.csv", dtype=str)
    pr["seal_no"] = pr.seal_no.astype(int)
    pr["depth_list"] = pd.to_numeric(pr.depth_list, errors="coerce")
    pr["square_dist"] = pd.to_numeric(pr.square_dist, errors="coerce")
    pr["mound_hdr"] = pr.mound_hdr.replace({"P": "F"})
    regi = reg.set_index("serial")

    def accepted(c):
        if c.seal_no not in regi.index:
            return False, "no_register_row"
        r = regi.loc[c.seal_no]
        fr, fc = nfind(r.field_no), nfind(c.find_no)
        if fr and fc:
            if fr == fc:
                return True, "find_no"
            if edit1(fr, fc):
                return True, "find_no_ocr1"
            return False, "find_no_conflict"
        if pd.notna(c.depth_list) and pd.notna(r.depth_reg) and abs(abs(c.depth_list) - abs(r.depth_reg)) <= 1:
            return True, "depth"
        if c.kind == "prose" and isinstance(c.square, str) and c.square and c.square_dist <= 400 \
                and isinstance(r.mound, str) and r.mound == c.mound_hdr:
            return True, "mound+near_square"
        return False, "uncorroborated"

    acc = pr.apply(lambda c: accepted(c), axis=1)
    pr["accepted"] = [a for a, _ in acc]
    pr["accept_by"] = [b for _, b in acc]
    pr.to_csv(OUT / "prose_refs_checked.csv", index=False)
    good = pr[pr.accepted & pr.square.notna() & (pr.square != "")].copy()
    good["kord"] = (good.kind != "list").astype(int)
    good = good.sort_values(["seal_no", "kord", "line"])
    nsq = good.groupby("seal_no").square.nunique()
    best = good.drop_duplicates("seal_no", keep="first").set_index("seal_no")

    lines = [l for l in m77_lines() if 4000 < l["text_no"] < 5000]
    bytext = {}
    for l in lines:
        bytext.setdefault(l["text_no"], []).append(l)
    rows = []
    for s, r in regi.iterrows():
        tn = 4000 + s
        ls = sorted(bytext.get(tn, []), key=lambda l: (l["side"], l["line"]))
        sides = {}
        for l in ls:
            sides.setdefault(l["side"], []).extend(l["signs"] + ["|"])
        sides = {k: v[:-1] for k, v in sides.items()}
        seq0 = sides[min(sides)] if sides else []
        allsigns = [x for v in sides.values() for x in v if x not in ("|", "#")]
        lvl = None
        for l in ls:
            try:
                lvl = float(l["level"])
                break
            except (TypeError, ValueError):
                pass
        b = best.loc[s] if s in best.index else None
        sq = b.square if b is not None else None
        mound = r.mound if isinstance(r.mound, str) else (b.mound_hdr if b is not None else None)
        dep, dsrc = r.depth_reg, "register"
        if pd.isna(dep) and b is not None and pd.notna(b.depth_list):
            dep, dsrc = b.depth_list, "prose_list"
        if pd.isna(dep) and lvl is not None:
            dep, dsrc = -abs(lvl), "m77_level"
        if pd.isna(dep):
            dsrc = None
        m = re.match(r"([A-Z])\s?(\d{1,2})/(\d{1,2})", sq) if isinstance(sq, str) else None
        rows.append(dict(serial=s, m77_text_no=tn if ls else None, icit_ids=r.icit_ids, cisi=r.cisi,
                         field_no=r.field_no, mound=mound, mound_reg=r.mound,
                         square=sq, big_square=(m.group(1) + m.group(2)) if m else None,
                         sub_square=int(m.group(3)) if m else None,
                         square_src=(b.kind + ":" + b.accept_by) if b is not None else None,
                         square_conflict=bool(nsq.get(s, 1) > 1),
                         area_text=b.area if b is not None else None,
                         depth=-abs(dep) if pd.notna(dep) else None, depth_src=dsrc,
                         depth_list=b.depth_list if b is not None else None,
                         m77_level=lvl, m77_locus=ls[0]["locus"] if ls else None,
                         object_type=ls[0]["object_type"] if ls else None, n_sides=len(sides),
                         seq_side0=" ".join(seq0), signs_all=" ".join(allsigns),
                         seq_all=" / ".join(" ".join(v) for k, v in sorted(sides.items()))))
    df = pd.DataFrame(rows)
    df["band5"] = np.floor(-df.depth / 5)
    df["band3"] = np.floor(-df.depth / 3)
    df.to_csv(OUT / "findspots.csv", index=False)

    lk = df[df.signs_all != ""]
    lv = lk[lk.depth.notna() & lk.m77_level.notna() & (lk.depth_src == "register")]
    agree = int(((lv.depth.abs() - lv.m77_level.abs()).abs() <= 1).sum())
    ll = lk[lk.depth_list.notna() & lk.depth_src.eq("register")]
    agree_list = int(((ll.depth.abs() - ll.depth_list.abs()).abs() <= 1).sum())
    sqd = lk[lk.big_square.notna()]
    summ = dict(register_rows=len(df), with_m77_text=len(lk),
                object_types=lk.object_type.value_counts().to_dict(),
                mound=lk.mound.fillna("none").value_counts().to_dict(),
                prose_citations=len(pr), prose_citations_accepted=int(pr.accepted.sum()),
                accept_by=pr.accept_by.value_counts().to_dict(),
                with_square=len(sqd), with_square_by_mound=sqd.mound.fillna("none").value_counts().to_dict(),
                with_square_by_type=sqd.object_type.value_counts().to_dict(),
                square_src=sqd.square_src.value_counts().to_dict(), square_conflicts=int(sqd.square_conflict.sum()),
                big_squares=int(sqd.big_square.nunique()),
                big_square_sizes=sqd.big_square.value_counts().to_dict(),
                sub_squares=int((sqd.big_square + "/" + sqd.sub_square.astype(str)).nunique()),
                depth_src=lk.depth_src.value_counts(dropna=False).to_dict(),
                depth_register_vs_m77_within1ft=f"{agree}/{len(lv)}",
                depth_register_vs_prose_list_within1ft=f"{agree_list}/{len(ll)}",
                linked_icit=int(lk.icit_ids.notna().sum()))
    json.dump(summ, open(OUT / "data_summary.json", "w"), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main()
