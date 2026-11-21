"""Build the sign-blind bead / lapidary / shell / faience / jeweller workshop coding.

Rules: experiments/bead_workshops/CODING_RULES.md (written before coding).
Blindness: BLINDNESS.md. This script never reads sign content: corpus `seq` is only
tested for being non-empty, so object counts match the assemblage linkage.

Run from repo root (OCR is untrusted data, read-only):
  .venv/bin/python -I experiments/bead_workshops/build_units.py

Writes, in experiments/bead_workshops/:
  bead_evidence.csv  one row per piece of evidence, with a verified OCR quote and line
  bead_units.csv     one row per coded unit: crafts, confidence, counts, density proxy
  unit_density.csv   every unit at Mohenjo-daro, Harappa and Chanhu-daro with inscribed
                     counts and listed-find counts (pool for a density-matched null)
"""
import bisect
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "experiments/magnitude/raw"
SRC = {
    "mackay1938": RAW / "mackay1938_v1/ocr.txt",
    "marshall1931": next((RAW / "marshall1931_v2").glob("*_djvu.txt")),
    "vats1940": RAW / "vats1940_v1/ocr.txt",
    "mackay1943": RAW / "mackay1943/ocr.txt",
}
CITE = {
    "mackay1938": "Mackay 1938 vol. I",
    "marshall1931": "Marshall 1931 vol. II",
    "vats1940": "Vats 1940",
    "mackay1943": "Mackay 1943",
}
LINES = {k: Path(p).read_text(errors="replace").splitlines() for k, p in SRC.items()}


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def locate(src, approx, quote, span=60):
    """Return the OCR line (1-based) where `quote` starts, searching near `approx`."""
    L = LINES[src]
    lo, hi = max(0, approx - span), min(len(L), approx + span)
    q = norm(quote)
    for i in range(lo, hi):
        if q in norm(" ".join(L[i:i + 4])):
            # first line of the 4-line window that is needed
            for j in range(i, i + 4):
                if q in norm(" ".join(L[i:j + 1])):
                    return i + 1
    raise SystemExit(f"quote not found: {src} ~{approx}: {quote!r}")


# ------------------------------------------------------------------------------
# Hand-coded evidence (from reading the reports; see CODING_RULES.md).
# Fields: site, unit, craft, conf, src, approx_line, quote, note, joinable, role
# conf is the confidence of THIS piece of evidence under the rules.
# ------------------------------------------------------------------------------
E = []


def ev(site, unit, craft, conf, src, line, quote, note="", joinable="yes", role="new", item=None):
    """item: id of the physical find/feature this quote evidences (None = findspot or
    supporting quote, or speculative use). Rule (b) counts distinct items."""
    E.append(dict(site=site, unit=unit, craft=craft, conf=conf, src=src, approx=line,
                  quote=quote, note=note, joinable=joinable, role=role, item=item))


# ---- Mohenjo-daro, DK-G (Mackay 1938). Blocks 1-12A = DKG. (S), 13-29 = DKG. (N) ----
ev("Mohenjo-daro", "DKG. (N)|15|VI", "JEWELLER", "medium", "mackay1938", 102530,
   "pieces of lump silver which had been flattened out ready for working",
   "Jewellery hoard in copper canister, room 28 of House VI, Block 15, -7.1 ft; also a silver piece partly severed with a chisel", item="DK 11337")
ev("Mohenjo-daro", "DKG. (N)|15|VI", "JEWELLER", "medium", "mackay1938", 102517,
   "unearthed in room 28 of house VI, Bl. 15", "findspot of the same hoard")
ev("Mohenjo-daro", "DKG. (S)|1|I", "FAIENCE", "low", "mackay1938", 6433,
   "that the kilns were used for glazing",
   "Palace S. wing room 33, called 'his workshop' by Mackay; kiln use uncertain (crucible or glazing), no objects found near")
ev("Mohenjo-daro", "DKG. (S)|1|I", "LAPIDARY", "low", "mackay1938", 81300,
   "shaped for use by a jeweller",
   "single stone stand (DK 8994), locus Bl. 1 central corridor (14); Mackay's object list puts Central Corridor under Block 1, House I (OCR lines 11508-11568)", item="DK 8994")
ev("Mohenjo-daro", "DKG. (S)|1|VI", "FAIENCE", "low", "mackay1938", 114888,
   "used as a paint on objects to be glazed",
   "single slab of vitreous paste, locus Bl. 1, ho. VI, rm. 64", item="slab Bl.1 VI")
ev("Mohenjo-daro", "DKG. (S)|1|I", "SHELL", "low", "mackay1938", 103270,
   "Only partly smoothed down inside",
   "partly made shell bracelet DK 6183, locus Bl. 1, court I (81); Mackay's object list puts Court I under Block 1, House I (OCR lines 11508-11524)", item="DK 6183")
ev("Mohenjo-daro", "DKG. (S)|3|V", "LAPIDARY", "low", "mackay1938", 115335,
   "might be an unfinished spacer in which the holes had not",
   "single object DK 5108, locus Bl. 3, ho. V, rm. 10", item="DK 5108")
ev("Mohenjo-daro", "DKG. (N)|18|-", "SHELL", "low", "mackay1938", 20686,
   "Unfinished Shell Ladle", "object list, Block 18 (no houses)", item="shell ladle Bl.18")
ev("Mohenjo-daro", "DKG. (N)|18|-", "LAPIDARY", "low", "mackay1938", 101026,
   "the limestone piece appears to be unfinished",
   "composite bead DK 10942, limestone half unfinished; locus Bl. 18, rm. 17", item="DK 10942")

# ---- Mohenjo-daro, HR / DK / VS (Marshall 1931 vol. II) ----
ev("Mohenjo-daro", "HRB|2|VIII", "JEWELLER", "medium", "marshall1931", 25910,
   "this hoard was the property",
   "HR 4210-4212 jewellery hoard with waste pieces of metal; Marshall: property of a goldsmith awaiting re-melting", item="HR 4210")
ev("Mohenjo-daro", "HRB|2|VIII", "JEWELLER", "medium", "marshall1931", 25898,
   "in Room 8 of House", "findspot: Room 8, House VIII, Block 2, Section B, HR Area, 6 ft")
ev("Mohenjo-daro", "DKC|16|-", "JEWELLER", "low", "marshall1931", 25726,
   "belonged to a jeweller or a dealer in precious metals",
   "DK 1341 hoard with scrap metal; capped at low because the unit has no house (CODING_RULES)")
ev("Mohenjo-daro", "DKC|16|-", "JEWELLER", "low", "marshall1931", 23547,
   "Room 2, Block 16, Section C, DK Area", "findspot of DK 1341")
ev("Mohenjo-daro", "DK|Trench E (M)|I", "JEWEL_HOARD", "low", "marshall1931", 25741,
   "north-weslern corner of Room",
   "Hoard 2 (carnelian girdle), Room 1, House I, Trench E (M); same room gave a possible crucible fragment with slag (OCR ~23525)",
   joinable="no")
ev("Mohenjo-daro", "VS|?|XXII", "SHELL", "low", "marshall1931", 31052,
   "is unfinished and unperforated",
   "unfinished shell segment VS 2187, House XXII, VS Area; block not given", joinable="no")

# ---- Harappa (Vats 1940), grid squares ----
ev("Harappa", "J12", "SHELL", "high", "vats1940", 8138,
   "five cores and numerous other fragments of shell",
   "group No. 10460 on pavement in J 12/23, Stratum II; also shell inlay blanks and four unfinished steatite seals", item="group 10460")
ev("Harappa", "J12", "SHELL", "high", "vats1940", 8169,
   "may have been a shop or", "Vats: 'a shop or workshop'")
ev("Harappa", "J12", "BEAD", "low", "vats1940", 8142,
   "barrel-shaped unfinished bead of", "single unfinished steatite bead in the same group")
ev("Harappa", "M10", "BEAD", "low", "vats1940", 11896,
   "Barrel-shaped, unfinished bead of banded agate", "square M 10/21, 7 ft")
ev("Harappa", "M11", "LAPIDARY", "low", "vats1940", 10441,
   "unboted and unfinished pendent of banded agate", "square M 11/19, 9 ft, Stratum IV")
ev("Harappa", "K8", "LAPIDARY", "low", "vats1940", 5138,
   "Tapering steatite pendent, grooved at the head, unfinished", "No. 4274, square K 8/4")
ev("Harappa", "I14", "JEWEL_HOARD", "low", "vats1940", 80073,
   "comprising gold, silver, and other jewellery",
   "hoard No. 8060, courtyard of House 2, Trench IV, Mound F, square I 14/1; finished jewellery")
for sq in ("H14", "I13", "I14", "J13"):
    ev("Harappa", sq, "FAIENCE", "low", "vats1940", 83427, "for etching carnelian beads",
       "Trench IV furnaces Fa-Fp; Vats lists faience firing, glazing and carnelian etching among several possible uses")

# ---- Chanhu-daro (Mackay 1943): coded for completeness, role=seen (not confirmatory) ----
for sq in ("8/C", "9/C", "9/D", "9/F"):
    ev("Chanhu-daro", sq, "BEAD", "high", "mackay1943", 3818,
       "Large numbers of unfinished beads, together with the stone drills used for boring them",
       "bead-making squares", role="seen")
ev("Chanhu-daro", "9/D", "BEAD", "high", "mackay1943", 3188, "Bead Factory with Furnace",
   "building 215, 286, 287", role="seen")
ev("Chanhu-daro", "9/D", "SHELL", "low", "mackay1943", 3872, "univalve shells with marked protub",
   "raw shell in room 215", role="seen")
ev("Chanhu-daro", "9/E", "SHELL", "medium", "mackay1943", 3868, "Four unfinished bangles",
   "locus 181", role="seen")
ev("Chanhu-daro", "9/E", "FAIENCE", "medium", "mackay1943", 3877,
   "show signs of being used in the process of glazing", "white paste plaques near locus 137", role="seen")
for sq in ("7/D", "8/C", "8/D", "8/E", "9/C"):
    ev("Chanhu-daro", sq, "SHELL", "low", "mackay1943", 3869, "unfinished shell dishes came from",
       "", role="seen")

for e in E:
    e["line"] = locate(e["src"], e["approx"], e["quote"])

RANK = {"low": 0, "medium": 1, "high": 2}
TARGET = {"BEAD", "LAPIDARY", "SHELL", "FAIENCE", "JEWELLER"}

# unit confidence: max over evidence; rule (b): two or more independent qualifying finds of
# target crafts at medium-eligible level in a house-level unit -> medium. Evaluated on
# distinct (craft, object) items; here applied only where quotes are different objects.
units = {}
for e in E:
    k = (e["site"], e["unit"])
    u = units.setdefault(k, {"crafts": set(), "conf": "low", "src": set(), "joinable": e["joinable"],
                             "role": e["role"], "n_ev": 0})
    u["crafts"].add(e["craft"])
    u["src"].add(f'{CITE[e["src"]]} OCR line {e["line"]}')
    if RANK[e["conf"]] > RANK[u["conf"]]:
        u["conf"] = e["conf"]
    u["n_ev"] += 1
    if e["item"] and e["craft"] in TARGET:
        u.setdefault("items", set()).add(e["item"])

# rule (b): >= 2 distinct qualifying items in one house-level unit (Harappa/Chanhu: square)
for (s_, un), u in units.items():
    house_level = s_ != "Mohenjo-daro" or un.split("|")[-1] not in ("-",)
    if house_level and u["joinable"] == "yes" and len(u.get("items", ())) >= 2 and u["conf"] == "low":
        u["conf"] = "medium"


# ------------------------------------------------------------------------------
# Inscribed-object counts per unit (sign-blind: seq only tested non-empty)
# Unit keys copied from experiments/assemblage/test.py (md_unit, unit_of).
# ------------------------------------------------------------------------------
def md_unit(r):
    area = r["area-section"].strip()
    bh = r["block-house"].strip()
    m = re.match(r"^(\d+A?)([IVXL]+)?-?$", bh)
    if not m:
        return None, None
    if area in ("DKG. (S)", "DKG. (N)"):
        a = area
    elif area.startswith("VS"):
        a = "VS"
    elif area in ("HRA", "HRB"):
        a = area
    elif area.startswith("DK") and len(area) == 3 and area[2] in "ABCDE":
        a = area
    else:
        return None, None
    return f"{a}|{m.group(1)}|{m.group(2) or '-'}", f"{a}|{m.group(1)}"


def unit_of(r):
    s = r["site"]
    if s == "Harappa":
        m = re.match(r"^-?([A-Z])(\d+)/", r["room-grid"].strip())
        return (f"{m.group(1)}{int(m.group(2))}", None) if m else (None, None)
    if s == "Mohenjo-daro":
        return md_unit(r)
    if s == "Chanhu-daro":
        m = re.search(r"sq\.?\s*(\d+)\s*/\s*([A-Z])", r["room-grid"])
        return (f"{m.group(1)}/{m.group(2)}", None) if m else (None, None)
    return None, None


corpus = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json"))
n_ins = Counter()
n_seal = Counter()
n_block = Counter()
site_tot = Counter()
site_mapped = Counter()
for r in corpus:
    if r["site"] not in ("Mohenjo-daro", "Harappa", "Chanhu-daro", "Lothal"):
        continue
    if not any(x > 0 for x in r["seq"]):  # non-empty test only; sign values unused
        continue
    site_tot[r["site"]] += 1
    u, b = unit_of(r)
    if u is None:
        continue
    site_mapped[r["site"]] += 1
    n_ins[(r["site"], u)] += 1
    if r["type"].startswith("SEAL"):
        n_seal[(r["site"], u)] += 1
    if b:
        n_block[(r["site"], b)] += 1

# ------------------------------------------------------------------------------
# Listed-find density proxy from the same reports
# ------------------------------------------------------------------------------
ROMAN_OK = re.compile(r"^[IVXL]+$")


def clean_roman(s):
    s = s.upper().replace("T", "I").replace("F", "V").replace(" ", "").replace("1", "I").replace("L", "I")
    return s if re.fullmatch(r"[IVX]+", s) else None


finds = Counter()
L = LINES["mackay1938"]
for lo, hi, half in ((11503, 19334, "DKG. (S)"), (20341, 21400, "DKG. (N)")):
    block, house = None, None
    for i in range(lo - 1, min(hi, len(L))):
        ln = L[i].strip()
        mb = re.match(r"^Block\s+(\d+|l|lA|\d+A)\s*[A]?\.?\s*$", ln)
        if mb:
            b = mb.group(1).replace("l", "1")
            if ln.rstrip(".").endswith("A") and not b.endswith("A"):
                b += "A"
            block, house = b, None
            continue
        mh = re.match(r"^Hou\w*\.?\s*([IVXTFl1 ]+)[.,]?\s*$", ln)
        if mh:
            house = clean_roman(mh.group(1))
            continue
        if block and re.match(r"^[.,'•\s]*[\({]\s*P[lI1]", ln):
            finds[("Mohenjo-daro", f"{half}|{block}|{house or '-'}")] += 1

mtxt = "\n".join(LINES["marshall1931"])
pat = re.compile(r"House\s+([IVXLT\\]{1,7})\s*,\s*Block\s+(\d+)\s*,?\s*(?:S\w{2,6}ion\s+([A-E]))?\s*,?\s*(?:of\s+(?:the\s+)?)?(HR|DK)\s+Are", re.S)
for m in pat.finditer(mtxt):
    h = clean_roman(m.group(1).replace("\\", "V"))
    if h:
        finds[("Mohenjo-daro", f"{m.group(4)}{m.group(3) or ''}|{m.group(2)}|{h}")] += 1
pat_b = re.compile(r"(?<!House )Block\s+(\d+)\s*,\s*S\w{2,6}ion\s+([A-E])\s*,\s*(HR|DK)\s+Are")
for m in pat_b.finditer(mtxt):
    pre = mtxt[max(0, m.start() - 25):m.start()]
    if "House" in pre:
        continue
    finds[("Mohenjo-daro", f"{m.group(3)}{m.group(2)}|{m.group(1)}|-")] += 1

vtxt = "\n".join(LINES["vats1940"])
for m in re.finditer(r"[Ss]quares?\s+([A-Z1l])\s*\.{0,2}\s*(\d{1,2})\s*/", vtxt):
    letter = m.group(1).replace("1", "I").replace("l", "I")
    finds[("Harappa", f"{letter}{int(m.group(2))}")] += 1

# ------------------------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------------------------
with open(HERE / "bead_evidence.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["site", "unit", "craft", "evidence_confidence", "source", "ocr_line", "quote", "note", "joinable", "role"])
    for e in E:
        w.writerow([e["site"], e["unit"], e["craft"], e["conf"], CITE[e["src"]] + " OCR (" + str(SRC[e["src"]].relative_to(ROOT)) + ")",
                    e["line"], e["quote"], e["note"], e["joinable"], e["role"]])


def block_of(unit):
    p = unit.split("|")
    return "|".join(p[:2]) if len(p) == 3 else None


with open(HERE / "bead_units.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["site", "unit", "crafts", "target_craft", "confidence", "primary_set", "role", "joinable",
                "n_inscribed", "n_seal", "n_nonseal", "n_inscribed_block", "n_listed_finds", "n_evidence", "sources"])
    for (s, u), d in sorted(units.items()):
        k = (s, u)
        ni = n_ins[k] if d["joinable"] == "yes" else ""
        ns = n_seal[k] if d["joinable"] == "yes" else ""
        nn = (n_ins[k] - n_seal[k]) if d["joinable"] == "yes" else ""
        b = block_of(u)
        nb = n_block[(s, b)] if (b and s == "Mohenjo-daro" and d["joinable"] == "yes") else ""
        target = "yes" if d["crafts"] & TARGET else "no"
        primary = "yes" if (target == "yes" and d["conf"] in ("high", "medium") and d["joinable"] == "yes") else "no"
        w.writerow([s, u, ";".join(sorted(d["crafts"])), target, d["conf"], primary, d["role"], d["joinable"],
                    ni, ns, nn, nb, finds.get(k, 0), d["n_ev"], " | ".join(sorted(d["src"]))])

allk = set(n_ins) | set(finds) | set(units)
with open(HERE / "unit_density.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["site", "unit", "n_inscribed", "n_seal", "n_listed_finds", "coded_workshop", "workshop_confidence"])
    for k in sorted(allk):
        if k[0] not in ("Mohenjo-daro", "Harappa", "Chanhu-daro"):
            continue
        d = units.get(k)
        w.writerow([k[0], k[1], n_ins[k], n_seal[k], finds.get(k, 0), "yes" if d else "no", d["conf"] if d else ""])

print("evidence rows", len(E), "units", len(units))
print("inscribed (non-empty) per site", dict(site_tot), "mapped to a unit", dict(site_mapped))
for (s, u), d in sorted(units.items()):
    print(f'{s:13s} {u:22s} {";".join(sorted(d["crafts"])):24s} {d["conf"]:6s} {d["role"]:4s} join={d["joinable"]:3s} '
          f'ins={n_ins[(s,u)] if d["joinable"]=="yes" else "-"} finds={finds.get((s,u),0)}')
