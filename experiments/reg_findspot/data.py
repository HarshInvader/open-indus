"""Normalise Mackay 1938 (FEM) findspots and join them to M77 texts.

Run: .venv/bin/python experiments/reg_findspot/data.py
Writes experiments/reg_findspot/findspots.csv (one row per linked FEM seal) and data_summary.json.
Uses only signs from M77 (corpus/load.py); reads experiments/old_registers/registers.csv read-only.

Normalisation rules (decided before any sign sharing was computed):
  block  : 'Bet.'/'Bis.'/'St.'/'Lane'/'Alley'/'of Bl.'/'Central'/'West'/'First' -> kind=street (no house);
           otherwise the block number = first token matching \\d+[A-Z]? after stripping OCR junk.
  house  : Roman numeral; OCR repairs rv->IV, HI/Ill/111/UI/ni->III, U/11/ll->II, vm/VUI/VIU/vni->VIII,
           l/1->I. '—', '--' -> no house (blocks whose rooms are numbered without houses).
           'HI 26' style (house and room merged) -> split.
  room   : leading integer of the room field (or of the merged house field). A trailing
           '- 17-7' pattern is the depth column spilled into the room column -> depth -17.7.
  depth  : Mackay's table is sorted by depth below datum; a leading '+' is an OCR misread of
           the minus sign (|depth| is monotone in serial). We use depth = -|depth|. Values that
           depart from the running median of serial neighbours by > 3 ft are flagged and
           replaced by the M77 level when available, else dropped.
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

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9,
         "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14}
OCR_ROMAN = {"RV": "IV", "HI": "III", "ILL": "III", "111": "III", "UI": "III", "NI": "III", "IIL": "III",
             "U": "II", "11": "II", "LL": "II", "IL": "II", "VM": "VIII", "VUI": "VIII", "VIU": "VIII",
             "VNI": "VIII", "VII[": "VII", "L": "I", "1": "I", "IV.": "IV", "XL": "XI", "VL": "VI"}
STREET_WORDS = ("bet", "bis", "st.", "street", "lane", "alley", "of bl", "central", "west", "east", "first")


def norm_roman(tok):
    t0 = tok.strip().strip(".,;:[]()'\"")
    if re.fullmatch(r"[VXI]?[Il]+[H]?|V[Il]*H", t0) and "l" in t0 or t0 in ("VIH", "VlH"):
        fixed = t0.replace("l", "I").replace("H", "II")
        if fixed.upper() in ROMAN:
            return fixed.upper(), True
    t = t0.upper()
    if t in ROMAN:
        return t, False
    if t in OCR_ROMAN:
        return OCR_ROMAN[t], True
    return None, False


def parse_row(r):
    flags = []
    blk = str(r["block"]) if pd.notna(r["block"]) else ""
    hou = str(r["house"]) if pd.notna(r["house"]) else ""
    room = str(r["room"]) if pd.notna(r["room"]) else ""
    fs = str(r["findspot"])
    spill_depth = None
    low = (blk + " " + hou).lower()
    if "surface" in (fs.lower()):
        return dict(kind="surface", block=None, house=None, room=None, flags="surface", spill=None)
    if any(w in low for w in STREET_WORDS):
        # streets / between-block lanes: key = normalised whole string
        key = re.sub(r"[^a-z0-9&]+", " ", (blk + " " + hou + " " + room).lower())
        key = re.sub(r"\s+", " ", key).strip()
        m = re.search(r"([-+])\s?(\d{1,2})-(\d)\s*;?\s*$", room)
        if m:
            spill_depth = -(int(m.group(2)) + 0.1 * int(m.group(3)))
        return dict(kind="street", block=None, house=None, room=None, street_key=key, flags="street", spill=spill_depth)
    # block number
    b = re.sub(r"[^0-9A-Za-z ]", " ", blk).split()
    b = [{"lo": "10", "lOA": "10A", "lA": "1A", "lO": "10"}.get(t, t) for t in b]
    bnum = None
    for tok in b:
        if re.fullmatch(r"\d{1,2}[A-Z]?", tok):
            bnum = tok
            break
    if bnum is None:
        flags.append("block_unreadable")
    if b and b[0] != bnum and bnum is not None:
        flags.append("block_junk_stripped")
    # house (maybe merged with room)
    house = None
    h = hou.strip()
    if h in ("", "nan", "—", "--", "•—", "-"):
        house = None
    else:
        parts = h.split()
        hr, rep = norm_roman(parts[0])
        if hr:
            house = hr
            if rep:
                flags.append("house_ocr_repaired")
            if len(parts) > 1 and re.fullmatch(r"\d+", parts[1]) and not room.strip():
                room = parts[1]
                flags.append("house_room_split")
            elif len(parts) > 1 and re.fullmatch(r"\d+", parts[1]):
                # e.g. '— 13' handled above; 'VI 61' with room present -> ambiguous
                room = parts[1] if not re.match(r"\d", room.strip()) else room
                flags.append("house_room_split")
        elif re.fullmatch(r"[—\-•]+\s*\d+", h):
            room = re.sub(r"[^0-9]", "", h)
        else:
            flags.append("house_unreadable")
    # room + spilled depth
    rm = re.match(r"\s*(\d{1,3})", room)
    rnum = rm.group(1) if rm else None
    m = re.search(r"([-+])\s?(\d{1,2})-(\d)\s*;?\s*$", room)
    if m:
        spill_depth = -(int(m.group(2)) + 0.1 * int(m.group(3)))
    if room.strip() and rnum is None:
        flags.append("room_unreadable")
    return dict(kind="house" if house else ("room_only" if rnum else "block_only"), block=bnum, house=house,
                room=rnum, flags=";".join(flags), spill=spill_depth)


def main():
    d = pd.read_csv(ROOT / "experiments/old_registers/registers.csv", dtype=str)
    f = d[(d.source == "Mackay1938_FEM")].copy()
    f["serial"] = f.object_no.str.extract(r"(\d+)")[0].astype(int)
    f = f.sort_values("serial")
    # M77 texts by text_no (all sides, reading order); level fallback
    lines = [l for l in m77_lines() if l["site"] == "Mohenjodaro"]
    bytext = {}
    for l in lines:
        bytext.setdefault(l["text_no"], []).append(l)
    rows = []
    for _, r in f.iterrows():
        p = parse_row(r)
        dep = pd.to_numeric(r["depth_ft"], errors="coerce")
        dep_src = "register"
        if pd.isna(dep) and p.get("spill") is not None:
            dep, dep_src = p["spill"], "register_spilled"
        if pd.notna(dep):
            dep = -abs(float(dep))
        tn = r["m77_text_no"]
        tn = int(float(tn)) if pd.notna(tn) else None
        ls = sorted(bytext.get(tn, []), key=lambda l: (l["side"], l["line"])) if tn else []
        lvl = None
        for l in ls:
            try:
                lvl = float(l["level"])
                break
            except (TypeError, ValueError):
                pass
        sides = {}
        for l in ls:
            sides.setdefault(l["side"], []).extend(l["signs"] + ["|"])
        sides = {k: v[:-1] for k, v in sides.items()}
        seq0 = sides[min(sides)] if sides else []
        allsigns = [s for v in sides.values() for s in v if s not in ("|", "#")]
        rows.append(dict(serial=r["serial"], field_no=r["field_no"], findspot_raw=r["findspot"], kind=p["kind"],
                         block=p.get("block"), house=p.get("house"), room=p.get("room"),
                         street_key=p.get("street_key"), parse_flags=p["flags"],
                         depth_raw=r["depth_ft"], depth=dep, depth_src=dep_src if pd.notna(dep) else None,
                         m77_level=lvl, m77_text_no=tn, object_type=ls[0]["object_type"] if ls else None,
                         n_sides=len(sides), seq_side0=" ".join(seq0), signs_all=" ".join(allsigns),
                         locus=ls[0]["locus"] if ls else None))
    df = pd.DataFrame(rows)
    # monotonic depth check against serial neighbours
    med = df["depth"].rolling(9, center=True, min_periods=3).median()
    bad = (df["depth"] - med).abs() > 3
    df["depth_flag"] = np.where(bad, "outlier", "")
    for i in df.index[bad]:
        if pd.notna(df.at[i, "m77_level"]) and abs(-abs(df.at[i, "m77_level"]) - med[i]) <= 3:
            df.at[i, "depth"] = -abs(df.at[i, "m77_level"])
            df.at[i, "depth_src"] = "m77_level(replaced outlier)"
        else:
            df.at[i, "depth"] = np.nan
            df.at[i, "depth_src"] = None
    miss = df["depth"].isna() & df["m77_level"].notna() & (df["depth_flag"] != "outlier")
    df.loc[miss, "depth"] = -df.loc[miss, "m77_level"].abs()
    df.loc[miss, "depth_src"] = "m77_level"
    df["house_key"] = np.where(df.kind == "house", df.block.astype(str) + "/" + df.house.astype(str), None)
    df["room_key"] = np.where(df.room.notna() & df.block.notna(),
                              df.block.astype(str) + "/" + df.house.fillna("-").astype(str) + "/" + df.room.astype(str), None)
    df["band5"] = np.floor(-df["depth"] / 5)
    df["band3"] = np.floor(-df["depth"] / 3)
    df.to_csv(OUT / "findspots.csv", index=False)
    lk = df[df.m77_text_no.notna() & (df.signs_all != "")]
    lv = lk[lk.depth.notna() & lk.m77_level.notna()]
    agree = int(((lv.depth.abs() - lv.m77_level.abs()).abs() <= 1).sum())
    hk = lk[lk.house_key.notna()].house_key.value_counts()
    rk = lk[lk.room_key.notna()].room_key.value_counts()
    summ = dict(fem_rows=len(df), linked_with_text=len(lk),
                kind=lk.kind.value_counts().to_dict(),
                flags={k: int(lk.parse_flags.fillna("").str.contains(k).sum()) for k in
                       ["house_ocr_repaired", "house_room_split", "block_junk_stripped", "block_unreadable",
                        "house_unreadable", "room_unreadable", "street", "surface"]},
                depth_src=lk.depth_src.value_counts(dropna=False).to_dict(),
                depth_outliers=int((lk.depth_flag == "outlier").sum()),
                depth_vs_m77_within1ft=f"{agree}/{len(lv)}",
                houses=int(len(hk)), houses_2plus=int((hk >= 2).sum()), seals_in_houses_2plus=int(hk[hk >= 2].sum()),
                rooms=int(len(rk)), rooms_2plus=int((rk >= 2).sum()), seals_in_rooms_2plus=int(rk[rk >= 2].sum()),
                blocks=lk[lk.block.notna()].block.value_counts().to_dict(),
                object_types=lk.object_type.value_counts().to_dict())
    json.dump(summ, open(OUT / "data_summary.json", "w"), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main()
