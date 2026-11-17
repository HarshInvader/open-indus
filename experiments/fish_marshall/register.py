"""Build the re-read Marshall 1931 (MIC vol. II pp. 402-405) seal register with reliability flags and findspots.

Inputs (read only):
  manual_B.txt                                   manual transcription of scan B (this folder)
  experiments/old_registers/mic_seals.csv        djvu-layer parse of scan in.ernet.dli.2015.107493 (2nd reading)
  sources/field-cady_indus_valley_script_corpus/inscriptions.csv   ICIT raw: CISI excavation-idno, area/block/room, depth
  M77 via corpus.load (level = depth reference)
Output: register.csv, register_summary.json
Run: .venv/bin/python experiments/fish_marshall/register.py
Pre-registration: docs/prereg/fish_marshall.md (+ amendment A1).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa: E402

ROMAN = r"(?:[IVXL]+)"


def lev_ft(s):
    s = s.strip()
    if s == "Sur":
        return 0.0
    m = re.fullmatch(r"(\d+)'(\d+)", s)
    return int(m.group(1)) + int(m.group(2)) / 12 if m else np.nan


# ---------- reading 1: manual transcription ----------
rows = []
for ln in open(HERE / "manual_B.txt"):
    if ln.startswith("#") or not ln.strip():
        continue
    ser, lev, area, fld = [x.strip() for x in ln.split("|")]
    rows.append(dict(serial=ser, lev_raw=lev, depth_B=lev_ft(lev), prefix=area if area != "?" else "",
                     field=fld.rstrip("?") if fld != "?" else "", field_doubtful=fld.endswith("?")))
R = pd.DataFrame(rows)
R["serial_int"] = pd.to_numeric(R.serial, errors="coerce")
R["is_b"] = R.serial.str.endswith("b")

# ---------- reading 2: djvu layer (old parse) ----------
dj = pd.read_csv(ROOT / "experiments/old_registers/mic_seals.csv", dtype=str)
dj["s"] = pd.to_numeric(dj.serial, errors="coerce")
dj = dj.dropna(subset=["s"]).drop_duplicates("s")
djm = dj.set_index(dj.s.astype(int))


def norm_field(f):
    return "" if pd.isna(f) else re.sub(r"\s+", " ", str(f)).strip()


R["field_djvu"] = R.serial_int.map(lambda s: norm_field(djm.field_no.get(int(s), "")) if pd.notna(s) and not False else "")
R["depth_djvu"] = R.serial_int.map(lambda s: -float(djm.level_ft.get(int(s))) if pd.notna(s) and pd.notna(
    pd.to_numeric(djm.level_ft.get(int(s), np.nan), errors="coerce")) else np.nan)
R.loc[R.is_b, ["field_djvu", "depth_djvu"]] = ["", np.nan]
R["key"] = (R.prefix + " " + R.field).str.strip()
R["djvu_agree"] = np.where(R.field_djvu == "", np.nan, (R.field_djvu == R.key).astype(float))

# ---------- reading 3: ICIT excavation-idno (CISI basic data) ----------
I = pd.read_csv(ROOT / "sources/field-cady_indus_valley_script_corpus/inscriptions.csv", dtype=str)
I = I[I.site.str.contains("Mohenjo", na=False)].copy()
I["idn"] = I["excavation-idno"].fillna("").str.replace(r"\s+", "", regex=True)
I = I.drop_duplicates(subset=["cisi", "idn", "block-house", "room-grid"])


def icit_match(r):
    if not r.prefix or not r.field:
        return None
    pf = (r.prefix + r.field).replace(" ", "")
    ser = r.serial
    hits = []
    for i, x in I[I.idn.str.startswith(pf)].iterrows():
        rest = x.idn[len(pf):]
        parts = re.split(r"[/+]", rest)
        if ser in parts or rest == ser or rest.startswith(ser + "/"):
            hits.append(i)
    return hits[0] if hits else None


R["icit_row"] = R.apply(icit_match, axis=1)


def icit_field_for_serial(r):
    """Independent check: is there an ICIT idno ending in this serial whose field differs?"""
    if r.is_b or pd.isna(r.serial_int):
        return ""
    ser = r.serial
    c = I[I.idn.str.match(r"^(HR|VS|DK|SD|DM|BJ|MUS|C|E|L|D|B|A|F)\d+[a-z]?" + re.escape(ser) + r"$")]
    return ";".join(sorted(set(c.idn)))


R["icit_serial_hits"] = R.apply(icit_field_for_serial, axis=1)
R["icit_linked"] = R.icit_row.notna()
g = lambda c: R.icit_row.map(lambda i: I.loc[i, c] if pd.notna(i) else None)  # noqa: E731
R["icit_cisi"] = g("cisi")
R["icit_area"] = g("area-section")
R["icit_block_house"] = g("block-house")
R["icit_room"] = g("room-grid")
R["icit_depth"] = g("depth").map(lambda s: -float(re.match(r"(-?[\d.]+)", s).group(1)) if isinstance(s, str) and re.match(r"-?[\d.]+", s) else np.nan)

# ---------- M77 ----------
L = pd.DataFrame(m77_lines())
L = L[(L.text_no >= 1000) & (L.text_no < 2000)]
L["lev"] = pd.to_numeric(L.level, errors="coerce")
M = L.groupby("text_no").agg(object_type=("object_type", "first"), m77_level=("lev", "first"),
                             m77_locus=("locus", "first"), site=("site", "first"),
                             signs=("signs", lambda s: " ".join(x for l in s for x in l))).reset_index()
R["text_no"] = np.where(R.is_b | R.serial_int.isna(), np.nan, 1000 + R.serial_int)
R = R.merge(M, on="text_no", how="left")
R["m77_depth"] = -R.m77_level
R["dz"] = (R.depth_B - R.m77_depth).abs()

# ---------- reliability rule (prereg) ----------
# 1 serial read and in sequence: manual transcription read every serial in order (check below)
seq_ok = [int(s) for s in R.serial if s.isdigit()] == list(range(1, 558))
R["c1_serial"] = ~R.serial_int.isna() & seq_ok
# 2 area+field agree in >=2 readings, or read once with no conflicting reading.
# Other readings: Vision on scans A, B, C (vision_reads.csv), djvu layer, ICIT excavation-idno link.
V = pd.read_csv(HERE / "vision_reads.csv", dtype={"serial": str})
vp = V.pivot_table(index="serial", columns="scan", values="match", aggfunc="max")
for sc in ("A", "B", "C"):
    R["vision_" + sc] = R.serial.map(vp[sc]).fillna(False).astype(bool) if sc in vp else False
R["confirmed"] = R.vision_A | R.vision_B | R.vision_C | (R.djvu_agree == 1) | R.icit_linked
R["n_confirm"] = R[["vision_A", "vision_B", "vision_C", "icit_linked"]].sum(axis=1) + (R.djvu_agree == 1)
R["djvu_conflict"] = (R.djvu_agree == 0)
R["c2_field"] = (R.key != "") & ~R.field_doubtful & (R.confirmed | ~R.djvu_conflict)
# 3 depth within 1 ft of M77 when M77 has a level
R["c3_depth"] = np.where(R.m77_depth.notna() & R.depth_B.notna(), R.dz <= 1.0, True)
R["reliable"] = R.c1_serial & R.c2_field & R.c3_depth


# ---------- area labels (A1.3) ----------
def area_from_icit(a):
    if not isinstance(a, str):
        return None
    m = re.match(r"(HR|VS|DK|SD|L)", a)
    return m.group(1) if m else None


R["area_icit"] = R.icit_area.map(area_from_icit)
pref_map = {}
for p, grp in R[R.area_icit.notna()].groupby("prefix"):
    pref_map[p] = Counter(grp.area_icit).most_common(1)[0][0]
for p in ("HR", "VS", "DK", "SD", "L"):
    pref_map.setdefault(p, p)
R["area"] = R.area_icit.where(R.area_icit.notna(), R.prefix.map(pref_map)).fillna("other")


# ---------- findspot from ICIT (A1.1-2) ----------
def norm_section(a):
    if not isinstance(a, str) or a.strip("-") == "":
        return None
    a = a.replace(" ", "")
    m = re.match(r"(HR|VS|DK|SD|L)([A-G])?", a)
    if not m:
        return None
    return m.group(1) + ("-" + m.group(2) if m.group(2) else "")


def parse_block(bh, area):
    if not isinstance(bh, str):
        return None, None
    b = bh.strip()
    if b in ("--", "-", ""):
        return None, None
    if re.search(r"Street|Lane|Deadman", b, re.I):
        return f"street-{area}", None
    m = re.match(r"Trench\s*([A-Z])", b)
    if m:
        return f"trench{m.group(1)}", None
    if b.lower().startswith("betw"):
        return None, None
    m = re.match(r"(\d+)\s*(" + ROMAN + r")?", b)
    if m:
        return m.group(1), m.group(2)
    return None, None


sec = R.icit_area.map(norm_section)
bl = [parse_block(b, a) for b, a in zip(R.icit_block_house, R.area)]
R["block_icit"] = [b for b, h in bl]
R["house_icit"] = [h for b, h in bl]
R["section_icit"] = sec


def unit(r):
    if not isinstance(r.block_icit, str):
        return None
    if r.block_icit.startswith("street-"):
        return r.block_icit
    s = r.section_icit or r.area
    return f"{s}/{r.block_icit}"


R["block_unit_icit"] = R.apply(unit, axis=1)
R.to_csv(HERE / "register.csv", index=False)

# ---------- summary ----------
S = {}
S["rows"] = int(len(R))
S["serial_sequence_complete_1_557"] = bool(seq_ok)
S["b_rows"] = R[R.is_b].serial.tolist()
S["m77_linked"] = int(R.object_type.notna().sum())
S["m77_object_types"] = R.object_type.value_counts().to_dict()
both = R[R.m77_depth.notna() & R.depth_B.notna()]
S["depth_check_n"] = int(len(both))
S["depth_within_1ft"] = int((both.dz <= 1.0).sum())
S["depth_within_1ft_share"] = float((both.dz <= 1.0).mean())
S["depth_exact_floor_share"] = float((np.floor(both.depth_B) == both.m77_depth).mean())
bj = R[R.m77_depth.notna() & R.depth_djvu.notna()]
S["djvu_depth_within_1ft_share"] = float(((bj.depth_djvu - bj.m77_depth).abs() <= 1).mean())
S["djvu_depth_n"] = int(len(bj))
S["field_djvu_compared"] = int(R.djvu_agree.notna().sum())
S["field_djvu_agree"] = int((R.djvu_agree == 1).sum())
S["icit_linked"] = int(R.icit_linked.sum())
S["confirmed_by_other_reading"] = int(R.confirmed.sum())
S["confirmed_by"] = {k: int(R[k].sum()) for k in ("vision_A", "vision_B", "vision_C", "icit_linked")}
S["unconfirmed_djvu_conflict_dropped"] = int((~R.confirmed & R.djvu_conflict).sum())
bi = R[R.icit_depth.notna() & R.depth_B.notna()]
S["icit_depth_within_0p2ft_share"] = float(((bi.icit_depth - bi.depth_B).abs() <= 0.2).mean())
S["icit_depth_n"] = int(len(bi))
S["c1"] = int(R.c1_serial.sum()); S["c2"] = int(R.c2_field.sum()); S["c3"] = int(R.c3_depth.sum())
S["reliable"] = int(R.reliable.sum())
S["reliable_seals_m77"] = int((R.reliable & (R.object_type == "seal")).sum())
S["prefix_to_area"] = pref_map
S["area_counts_reliable_seals"] = R[R.reliable & (R.object_type == "seal")].area.value_counts().to_dict()
S["block_unit_icit_reliable_seals"] = int((R.reliable & (R.object_type == "seal") & R.block_unit_icit.notna()).sum())
json.dump(S, open(HERE / "register_summary.json", "w"), indent=1, default=str)
print(json.dumps(S, indent=1, default=str))
dis = R[(R.djvu_agree == 0) & ~R.confirmed][["serial", "key", "field_djvu"]]
print("djvu disagreements:", len(dis))
print(dis.to_string())
bad = both[both.dz > 1][["serial", "lev_raw", "depth_B", "m77_depth", "depth_djvu", "icit_depth", "key"]]
print("depth >1ft off:", len(bad))
print(bad.to_string())
