"""Extract cuneiform seal legends at WORD level, keeping lines, from the CDLI open dump that the
short_labels agent downloaded (read-only reuse: experiments/short_labels/raw/cdli/).

usage: .venv/bin/python -I experiments/genre_alignment/ga_extract.py
writes experiments/genre_alignment/data/seals_<group>.jsonl : {"pid","period","lines":[[word,...],...]}
Untrusted input, parsed as text only. One record per DISTINCT legend (same seal rolled on many
tablets is collapsed). Legends with any broken/illegible word (x, ..., [...]) are dropped.
"""
import csv, json, re
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "short_labels/raw/cdli"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)

GROUPS = [("Ur III", "ur3"), ("Old Akkadian", "oakk"), ("Lagash II", "lag2"), ("ED IIIb", "ed3b"),
          ("Early Old Babylonian", "ob"), ("Old Babylonian", "ob"), ("Old Assyrian", "oa"),
          ("Middle Babylonian", "mb"), ("Middle Assyrian", "ma"), ("Neo-Assyrian", "na"),
          ("Neo-Babylonian", "nb"), ("Achaemenid", "nb"), ("Old Elamite", "oelam"),
          ("Middle Elamite", "elam"), ("Neo-Elamite", "elam")]


def group(period):
    for k, g in GROUPS:
        if period.startswith(k): return g
    return None


def load_cat():
    cat = {}
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit():
                cat["P" + pid.zfill(6)] = ((r.get("object_type") or "").lower().strip(), r.get("period") or "")
    return cat


def words(content):
    s = re.sub(r"\(\$.*?\$\)", " ", content)
    s = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", s)
    s = s.replace("_", " ").replace("…", " ... ")
    out = []
    for w in s.split():
        if w in (",", ":", ";", "/", "|") or w.startswith("$"): continue
        w = w.lower().strip()
        if not w: continue
        parts = re.split(r"[-.]", re.sub(r"\{[^}]*\}", "", w))
        if "..." in w or any(p == "x" or re.fullmatch(r"x+", p) for p in parts if p): return None
        out.append(w)
    return out


def parse(cat):
    pid = None; insec = False; lines = []; ok = True; objlines = []; objok = True
    def emit_obj():
        if pid is None: return None
        ot, period = cat.get(pid, ("", ""))
        if (ot.startswith("seal") or ot == "sealing") and objok and objlines:
            return (pid, period, list(objlines))
    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n").rstrip()
            if line.startswith("&P"):
                if insec and ok and lines: yield (pid, cat.get(pid, ("", ""))[1], list(lines))
                r = emit_obj()
                if r: yield r
                pid = line[1:8]; insec = False; lines = []; ok = True; objlines = []; objok = True
                continue
            if pid is None: continue
            if line.startswith("@"):
                tag = line[1:].strip().split()[0] if line[1:].strip() else ""
                if tag == "column": continue
                if insec and ok and lines: yield (pid, cat.get(pid, ("", ""))[1], list(lines))
                insec = (tag == "seal"); lines = []; ok = True
                continue
            m = re.match(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$", line)
            if not m: continue
            w = words(m.group(2))
            if insec:
                if w is None: ok = False
                elif w: lines.append(w)
            else:
                if w is None: objok = False
                elif w: objlines.append(w)
        if insec and ok and lines: yield (pid, cat.get(pid, ("", ""))[1], list(lines))
        r = emit_obj()
        if r: yield r


def main():
    cat = load_cat()
    by = defaultdict(list); seen = defaultdict(set)
    for pid, period, lines in parse(cat):
        g = group(period)
        if not g: continue
        key = tuple(tuple(l) for l in lines)
        if key in seen[g]: continue
        seen[g].add(key); by[g].append({"pid": pid, "period": period, "lines": lines})
    for g, X in sorted(by.items()):
        with open(OUT / f"seals_{g}.jsonl", "w") as f:
            for r in X: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        nw = [sum(len(l) for l in r["lines"]) for r in X]
        print(f"{g:6s} distinct={len(X):6d} mean_words={sum(nw)/len(X):5.2f}")


if __name__ == "__main__":
    main()
