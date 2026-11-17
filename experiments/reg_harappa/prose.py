"""Extract per-seal findspots from the narrative chapters of Vats 1940 (EH vol. I, chs. I-VI).

The tabulation of seals (pp. 337-356) gives only Mound/Area, find no. and depth below surface.
The narrative chapters cite seals as '(No. <find no.>, Pl. <roman>, <seal no.>)' inside a
description of a trench / extension / square / stratum. This script finds every citation of a
seal plate (Pls. LXXXV-CI; plate number = EH seal serial) and records the context:
  mound    : running page header (MOUND F / MOUND AB / AREA J / AREA G / AREA H)
  square   : nearest preceding grid square '<Letter> <n>/<m>' within the same paragraph
             (paragraph = text since the previous blank line run; side-notes may interleave)
  area     : nearest preceding trench/pit/extension/block/area name within WINDOW chars
  stratum  : nearest preceding 'Stratum <roman>' / 'Intermediate'/'Late' level within the sentence
  find_no  : 'No. X' inside the same parenthesis or immediately before it
Run: .venv/bin/python -I experiments/reg_harappa/prose.py  -> prose_refs.csv
Reads experiments/old_registers/raw/in.ernet.dli.2015.537391/ocr.txt (data only, never executed).
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCR = HERE.parents[1] / "experiments/old_registers/raw/in.ernet.dli.2015.537391/ocr.txt"
ROMAN_PL = ["LXXXV", "LXXXVI", "LXXXVII", "LXXXVIII", "LXXXIX", "XC", "XCI", "XCII", "XCIII", "XCIV", "XCV",
            "XCVI", "XCVII", "XCVIII", "XCIX", "CI", "C"]
PL = re.compile(r"P[lILl1][.,]?\s*(" + "|".join(ROMAN_PL) + r")\s*[,.]\s*(\d{1,3})((?:\s*(?:,|and)\s*\d{1,3}(?!\s*(?:in|ft)))*)")
SQUARE = re.compile(r"\b([A-Z1l])\s?(\d{1,2})\s?/\s?(\d{1,2})\b")
SQ_AFTER = re.compile(r"Sq(?:uare|\.)?\s*([A-Z1l])\s?(\d{1,2})\s?/\s?(\d{1,2})")
DEP_AFTER = re.compile(r"Depth\s*(\d{1,2})\s*ft\.?\s*(?:(\d{1,2})\s*in)?")
AREA = re.compile(r"\b(Trench\s+[IVXl1]+[a-z]?|Pits?\s+[IVXl1]+|Extension\s+[A-Z][a-z]?|[Aa]rea\s+[A-Z][a-z]?\b|"
                  r"Block\s+[IVXl1]+|(?:Eastern|Western)\s+Block|Great\s+Granary|Workmen.s\s+Quarters|"
                  r"Working\s+Floors?|Cemetery\s+[A-Z]|Cemetery\s+R\s?37|Hall\s+[IVX]+)")
STRAT = re.compile(r"(Stratum\s+[IVXl1]+[a-z]?|[IVXl1]+(?:st|nd|rd|th)\s+stratum|Intermediate\s+[IVXl1]+|Late\s+(?:I|II|III|Period)|Early\s+Period|Mature)", re.I)
FINDNO = re.compile(r"No[s]?\.?\s*([A-Za-z]{0,4}\s?\d{1,5}[a-z]?)")
HEAD = re.compile(r"^\s*(MOUND|AREA)\s+([A-Z][A-Z]?)\b", re.M)
WINDOW = 3000
NARR_END_LINE = 24106  # CHAPTER VII (pottery etc.) starts here; chs. I-VI are the excavation narrative
NARR_START_LINE = 1951


def norm_find(s):
    s = s.replace(" ", "")
    s = re.sub(r"(?<=[A-Za-z])l(?=\d)", "1", s)
    s = s.replace("O", "0") if re.fullmatch(r"[\dO]+", s) else s
    return s


def main():
    t = OCR.read_text(errors="replace")
    lines = t.split("\n")
    start = sum(len(l) + 1 for l in lines[:NARR_START_LINE - 1])
    end = sum(len(l) + 1 for l in lines[:NARR_END_LINE - 1])
    heads = [(m.start(), m.group(2)) for m in HEAD.finditer(t)]
    paras = [m.end() for m in re.finditer(r"\n\s*\n", t)]
    out = []
    for m in PL.finditer(t, start, end):
        nums = [int(m.group(2))] + [int(x) for x in re.findall(r"\d{1,3}", m.group(3) or "")]
        pos = m.start()
        # mound from page header: header lines are printed at the top of each page
        mound = None
        for hp, hm in heads:
            if hp < pos:
                mound = hm
            else:
                break
        # paragraph start
        pstart = max([p for p in paras if p <= pos] + [start])
        seg = t[pstart:pos]
        sq = list(SQUARE.finditer(seg))
        win = t[max(start, pos - WINDOW):pos]
        ar = list(AREA.finditer(win))
        # sentence (back to the last full stop not inside 'No.' / 'Pl.' / 'ft.' / 'in.')
        sent = re.split(r"(?<!No)(?<!Nos)(?<!Pl)(?<!PI)(?<!PL)(?<!ft)(?<!in)(?<!sq)(?<!cf)(?<!p)\.\s", t[max(start, pos - 600):pos])[-1]
        st = list(STRAT.finditer(sent))
        st_par = list(STRAT.finditer(seg))
        paren = t[t.rfind("(", 0, pos):pos]
        fn = FINDNO.findall(paren) or FINDNO.findall(t[pos - 40:pos])
        # does the parenthesis name a seal/sealing/tablet? (descriptor before the paren)
        desc = t[max(start, pos - 200):pos]
        # formal find lists: 'Pl. XCVI, 429. Size .. No. 10359; Square I 8/10; Depth 15 ft. 6 in. b.s.'
        after = t[m.end():m.end() + 260]
        cut = re.search(r"\n\s*\d{1,2}\.\s|P[lIL1][.,]?\s*[CLXVI]{1,8}\s*,\s*\d", after)
        after = after[:cut.start()] if cut else after
        sa = SQ_AFTER.search(after)
        fa = FINDNO.search(after)
        da = DEP_AFTER.search(after)
        lst = bool(sa)
        def fixl(c):
            return "I" if c in "1l" else c
        for n in nums:
            out.append(dict(seal_no=n, plate=m.group(1), line=t[:pos].count("\n") + 1, mound_hdr=mound,
                            kind="list" if lst else "prose",
                            square=(f"{fixl(sa.group(1))} {sa.group(2)}/{sa.group(3)}" if lst else
                                    (f"{fixl(sq[-1].group(1))} {sq[-1].group(2)}/{sq[-1].group(3)}" if sq else "")),
                            square_dist=0 if lst else (pos - (pstart + sq[-1].end()) if sq else ""),
                            depth_list=(-(int(da.group(1)) + (int(da.group(2)) if da.group(2) else 0) / 12) if (lst and da) else ""),
                            area=re.sub(r"\s+", " ", ar[-1].group(1)) if ar else "",
                            area_dist=pos - (max(start, pos - WINDOW) + ar[-1].end()) if ar else "",
                            stratum=re.sub(r"\s+", " ", st[-1].group(1)) if st else "",
                            stratum_par=re.sub(r"\s+", " ", st_par[-1].group(1)) if st_par else "",
                            find_no=(norm_find(fa.group(1)) if (lst and fa) else (norm_find(fn[-1]) if fn and len(nums) == 1 else "")),
                            context=re.sub(r"\s+", " ", desc[-160:]) + " [" + re.sub(r"\s+", " ", m.group(0)) + "]"))
    with open(HERE / "prose_refs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(out), "citations;", len({o['seal_no'] for o in out}), "distinct seal numbers")


if __name__ == "__main__":
    main()
