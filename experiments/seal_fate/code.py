"""Step 2: rule coder. Reads ONLY remarks.csv (no sign content) and writes fate.csv per CODING_SCHEME.md.
Run: .venv/bin/python -I experiments/seal_fate/code.py
"""
import csv, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda pat, t: 1 if re.search(pat, t, re.I) else 0

BROKEN = (r"\bbroken\b|\bfragment|\bbit of\b|\bpiece of\b|part (?:is )?(?:missing|lost|broken)|broken off|\bchipped|"
          r"\bdamaged|\bsplit\b|\bcracked|\bonly \[k\][^.;]{0,40}(?:surviv|left|remain)|surviving|\bextant\b|\btrace of\b|"
          r"\bmissing\b|\bincomplete\b")
CUT = r"\bsawn\b|deliberately broken|\bground down\b|\bcut (?:in two|across|off|down)\b"
BURNT = r"\b(?:burnt|burned|scorched|calcined|blackened)\b(?!\s+(?:steatite|clay|brick|bricks|earth|paste))"
WORN = r"\bworn\b|\brubbed\b|\bdefaced|\beffaced|\bblurred|\bindistinct|\bfaint\b|\bweathered|\bcorroded"
REUSED = r"re-?used|re-?cut\b|re-?engraved|inscription (?:was )?removed|\bconverted"
UNFIN = r"unfinished|process of manufacture|\bblank\b|\buncut\b"
OPEN = r"\bst\b|\bstreet|\blane\b|\balley|\bbet\.|\bbetween\b|\bdrain|\bwell\b(?! (?:cut|made|executed|finished|preserved|known|baked|polished))|\bgate|city wall|fortification"
DWG = r"\bdrain|\bwell\b(?! (?:cut|made|executed|finished|preserved|known|baked|polished))|\bgate|city wall|fortification"
ROOMW = r"\broom\b|\bchamber\b|\bhouse\b"
BURIAL = r"cemetery|\bgrave|\bburial|\bskeleton|\binterment|\bR\s?37\b"
HOARD = r"found (?:together )?with|together with|group of antiquities|\bhoard|in a (?:jar|pot|vase)|same mould were also found"


def depth_vats(t):
    m = re.search(r"Depth\s+(\d+)\s*(?:ft\.?|feet)\s*(?:(\d+)\s*in\.?)?", t, re.I)
    if not m:
        return None
    return int(m.group(1)) + (int(m.group(2)) / 12 if m.group(2) else 0)


def code_row(r):
    t = r["remark"]
    out = dict(source=r["source"], site=r["site"], serial=r["serial"])
    if r["source"].startswith("Vats"):
        body = t
        out["BROKEN"] = F(BROKEN, body)
        out["BROKEN_PROXY"] = ""
        out["CUT"] = F(CUT, body)
        out["BURNT"] = F(BURNT, body)
        out["WORN"] = F(WORN, body)
        out["REUSED"] = F(REUSED, body)
        out["UNFINISHED"] = F(UNFIN, body)
        # findspot words in Vats entries: only street/drain/well/gate words count; squares are not findspot types
        fs = re.sub(r"Square[^;]*;", "", body)
        out["OPEN"] = F(r"\bstreet|\blane\b|\balley|\bdrain|\bgate|city wall|fortification", fs)
        out["DRAIN_WELL_GATE"] = F(DWG, fs)
        out["ROOM"] = F(ROOMW, fs)
        out["BURIAL"] = F(BURIAL, body + " " + r["mound"])
        out["HOARD"] = F(HOARD, body)
        d = depth_vats(body)
        out["SURFACE"] = "" if d is None and not re.search(r"surface\.?\s*$", body, re.I) else (1 if d is None or d <= 1.0 else 0)
    else:  # FEM
        fsm = re.search(r"Findspot: (.*?)\. Level:", t)
        fs = fsm.group(1) if fsm else ""
        lev = re.search(r"Level: (.*?)\. Dims:", t)
        lev = lev.group(1) if lev else ""
        dims = re.search(r"Dims: (.*?)\.(?: Prose:|$)", t)
        dims = dims.group(1) if dims else ""
        prose = t.split("Prose:", 1)[1] if "Prose:" in t else ""
        out["BROKEN"] = F(BROKEN, prose) if prose else 0
        out["BROKEN_PROXY"] = 1 if "?" in dims else 0
        out["CUT"] = F(CUT, prose) if prose else 0
        out["BURNT"] = F(BURNT, prose) if prose else 0
        out["WORN"] = F(WORN, prose) if prose else 0
        out["REUSED"] = F(REUSED, prose) if prose else 0
        out["UNFINISHED"] = F(UNFIN, prose) if prose else 0
        fs_clean = fs.replace("/", " ").strip(" .")
        has_fs = bool(re.search(r"[A-Za-z0-9]", fs_clean))
        o = F(OPEN, fs_clean)
        out["OPEN"] = o if has_fs else ""
        out["DRAIN_WELL_GATE"] = F(DWG, fs_clean) if has_fs else ""
        parts = [p.strip() for p in fs.split("/")]
        room = 1 if (not o and len(parts) >= 2 and re.search(r"\d|\b[IVX]+\b", parts[-1])) else 0
        out["ROOM"] = room if has_fs else ""
        out["BURIAL"] = 0
        out["HOARD"] = 0
        out["SURFACE"] = 1 if re.search(r"surface", lev, re.I) else (0 if re.search(r"\d", lev) else "")
    return out


if __name__ == "__main__":
    rows = list(csv.DictReader(open(os.path.join(HERE, "remarks.csv"))))
    coded = [code_row(r) for r in rows]
    keys = list(coded[0].keys())
    with open(os.path.join(HERE, "fate.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(coded)
    for src in ("Vats1940_EH", "Mackay1938_FEM"):
        sub = [c for c in coded if c["source"] == src]
        print(src, len(sub), {k: Counter(str(c[k]) for c in sub).get("1", 0) for k in keys[3:]})
