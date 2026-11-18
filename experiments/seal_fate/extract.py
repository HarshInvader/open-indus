"""Step 1 of seal_fate: pull per-object REMARK text from the 1930s reports. No sign content is read here.

Sources (all already on disk in experiments/old_registers; read-only):
  Harappa  - Vats 1940 vol. I, the per-trench "lists of finds": numbered entries such as
             "9. Unicorn seal, upper part broken. Pl. LXXXIX, 127. 1 in. sq. No. 2476; Square N 9/9; Depth 15 ft. 10 in. b.s."
             The plate item number (127) is the EH tabulation serial; the field number (2476) is checked
             against eh_seals.csv find_no for that serial.
  Mohenjo-daro - Mackay 1938 (FEM) tabulation: findspot (block / house / room, or street / lane / alley /
             between blocks), level (incl. "Surface") and the dimensions cell ('?' = a dimension could not be
             measured). Plus sentences in the FEM seal chapter that name a seal number together with a
             condition word (broken, burnt, worn, re-used, re-cut...).
Masking: any "<n> pictogram(s)" phrase is replaced by "[k] pictogram(s)" so the coder (rules or human) never
sees how many signs a text has. Animal names are kept (field symbol, not sign content).
Output: experiments/seal_fate/remarks.csv  (one row per register object with any remark/findspot text)
Run: .venv/bin/python -I experiments/seal_fate/extract.py
"""
import csv, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OR = os.path.join(REPO, "experiments/old_registers")

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s):
    s = s.upper().replace("L", "L")
    tot, prev = 0, 0
    for ch in reversed(s):
        v = ROMAN.get(ch, 0)
        tot = tot - v if v < prev else tot + v
        prev = max(prev, v)
    return tot


NUMW = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|a|single)"


def mask(t):
    t = re.sub(r"picto-\s*grams?", "pictograms", t, flags=re.I)
    t = re.sub(r"pic-\s*tograms?", "pictograms", t, flags=re.I)
    t = re.sub(r"\b(?:pi)?ctogr\w*|\bpictogra\w*", "pictograms", t, flags=re.I)  # OCR variants
    t = re.sub(rf"\b{NUMW}(?:\s+or\s+{NUMW})?((?:\s+[a-z-]+){{0,2}}\s+(?:pictograms?|signs?|characters?))", r"[k]\1", t, flags=re.I)
    t = re.sub(r"\b(\d+)\s+(?=and\s+\[k\])", "[k] ", t)
    t = re.sub(rf"\b{NUMW}\s+(on the (?:other|third|reverse|obverse|back))", r"[k] \1", t, flags=re.I)
    return t


def norm_field(s):
    m = re.search(r"([A-Za-z]{0,2}\s*-?\s*\d{2,6})\s*$", (s or "").strip())
    return re.sub(r"\D", "", m.group(1)) if m else ""


# ---------------------------------------------------------------- Harappa: Vats 1940 finds lists
def vats():
    txt = open(os.path.join(OR, "raw/in.ernet.dli.2015.537391/ocr.txt"), errors="ignore").read()
    lines = txt.split("\n")
    eh = {r["serial"]: r for r in csv.DictReader(open(os.path.join(OR, "eh_seals.csv")))}
    # walk line by line, tracking headings, accumulating numbered entries
    out = []
    mound, stratum, section = "", "", ""
    cur, cur_start = [], 0

    def flush(buf, start):
        if not buf:
            return
        whole = re.sub(r"\s+", " ", " ".join(x.strip() for x in buf))
        # split run-together entries: a new "<n>. Capital" after a depth/surface ending
        parts = re.split(r"(?:(?<=b\.s\.)|(?<=b\.s,)|(?<=b\. s\.)|(?<=urface\.))\s*\S?\s*(?=\d{1,2}\.\s+[A-Z])", whole)
        for e in parts:
            one(e, start)

    def one(e, start):
        for m in re.finditer(r"\bP[lI1]\.?\s*([LXCVI]{2,9})\s*,\s*(\d{1,3})\b", e):
            if re.search(r"(similar to|cf\.|see also|like|compare)[^.]{0,40}$", e[max(0, m.start() - 60):m.start()], re.I):
                continue
            pl = roman(m.group(1).replace("1", "I"))
            if not (84 <= pl <= 102):
                continue
            serial = m.group(2)
            fm = re.search(r"N[o0]\.\s*([A-Z]?\s*-?\s*\d{2,6})", e[m.end():]) or re.search(r"N[o0]\.\s*([A-Z]?\s*-?\s*\d{2,6})", e)
            fno = norm_field(fm.group(1)) if fm else ""
            r = eh.get(serial)
            chk = ""
            if r is not None and fno:
                chk = "agree" if norm_field(r["find_no"]) == fno else "disagree"
            out.append(dict(source="Vats1940_EH", site="Harappa", serial=serial, plate=m.group(1),
                            field_no=fno, link_check=chk, mound=mound, stratum=stratum, section=section,
                            ocr_line=start + 1, remark=mask(e)))

    for i, ln in enumerate(lines):
        s = ln.strip()
        if re.match(r"^(MOUND|AREA|CEMETERY)\s+[A-Z0-9]", s) and len(s) < 40:
            flush(cur, cur_start); cur = []
            mound = s.rstrip(". ")
            continue
        if re.search(r"stratum\s*[—-]\s*$", s, re.I) or re.match(r"^(Surface|Upper|Lower|Middle)[\w ]{0,30}[—-]\s*$", s):
            flush(cur, cur_start); cur = []
            stratum = s.rstrip("— -")
            continue
        if len(s) < 60 and re.search(r"(Section|Trench|Portion|Digging|Area)[^.]{0,40}[—-]\s*$", s):
            flush(cur, cur_start); cur = []
            section = s.rstrip("— -")
            continue
        if re.match(r"^\d{1,3}\.\s+\S", s):
            flush(cur, cur_start)
            cur, cur_start = [s], i
            continue
        if cur:
            if s == "" and len(cur) > 0 and re.search(r"b\.\s?s\.|surface\.?\s*$", " ".join(cur[-2:])):
                flush(cur, cur_start); cur = []
            elif len(cur) > 12:
                flush(cur, cur_start); cur = []
            elif s:
                cur.append(s)
    flush(cur, cur_start)
    # one row per serial: keep the first entry whose field no agrees, else the first entry
    best = {}
    for r in out:
        k = r["serial"]
        if k not in best or (best[k]["link_check"] != "agree" and r["link_check"] == "agree"):
            best[k] = r
    return list(best.values()), out


# ---------------------------------------------------------------- Mohenjo-daro: Mackay 1938 FEM
def fem():
    rows = list(csv.DictReader(open(os.path.join(OR, "fem_seals.csv"))))
    txt = open(os.path.join(OR, "raw/in.ernet.dli.2015.70071/ocr.txt"), errors="ignore").read().split("\n")
    chapter = re.sub(r"\s+", " ", " ".join(txt[61202:64323]))
    sents = re.split(r"(?<=[.;])\s+(?=[A-Z])", chapter)
    prose = {}
    for s in sents:
        # only "seal(s) NNN" refers to a tabulation serial; bare "No. N" is a plate item number
        nums = re.findall(r"\b[Ss]eals?\s+(?:No\.\s*)?(\d{1,3})\b", s)
        if nums and re.search(r"broken|burnt|burned|re-?used|re-?cut|worn|chipped|damaged|fragment|split|unfinished", s, re.I):
            for n in nums:
                prose.setdefault(n, []).append(mask(s.strip()))
    out = []
    for r in rows:
        fs = " / ".join(x for x in [r["block"], r["house"], r["room"]] if x)
        rem = f"Findspot: {r['findspot']}. Level: {r['level_raw']}. Dims: {r['dims_raw']}."
        if r["serial"] in prose:
            rem += " Prose: " + " | ".join(prose[r["serial"]])
        out.append(dict(source="Mackay1938_FEM", site="Mohenjo-daro", serial=r["serial"], plate="",
                        field_no=norm_field(r["field_no"]), link_check="", mound="DK", stratum="",
                        section=fs, ocr_line="", remark=rem))
    return out


if __name__ == "__main__":
    v, allv = vats()
    f = fem()
    with open(os.path.join(HERE, "remarks.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(v[0].keys()))
        w.writeheader()
        for r in v + f:
            w.writerow(r)
    print("Vats entries with seal-plate refs:", len(allv), "distinct serials:", len(v),
          "link check:", Counter(r["link_check"] for r in v))
    print("FEM rows:", len(f), "with prose condition sentence:", sum("Prose:" in r["remark"] for r in f))
