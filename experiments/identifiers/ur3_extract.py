"""Ur III seal-legend OCCURRENCES (one per sealed tablet, not deduplicated) with provenience, from the
CDLI dump downloaded by short_labels (read-only: experiments/short_labels/raw/cdli/). Untrusted text,
parsed as text only. Known personal-identifier reference for S3/S4.

usage: .venv/bin/python -I experiments/identifiers/ur3_extract.py
writes experiments/identifiers/data/ur3_occ.jsonl : {pid, prov, legend: [[word..]..], seal_id}
"""
import csv, json, re, sys
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "short_labels/raw/cdli"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)


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


def main():
    cat = {}
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit() and (r.get("period") or "").startswith("Ur III"):
                prov = (r.get("provenience") or "").split("(")[0].strip()
                cat["P" + pid.zfill(6)] = (prov, (r.get("seal_id") or "").strip(),
                                           (r.get("object_type") or "").lower())
    out = []
    pid = None; insec = False; lines = []; ok = True; seals = []
    def flush():
        if insec and ok and lines: seals.append([list(l) for l in lines])
    def emit():
        if pid in cat and seals:
            prov, sid, ot = cat[pid]
            if ot.startswith("seal"): return  # physical seals / seal catalogue entries: not impressions
            for lg in seals:
                out.append(dict(pid=pid, prov=prov, seal_id=sid, legend=lg))
    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("&P"):
                flush(); emit()
                pid = line[1:8]; insec = False; lines = []; ok = True; seals = []
                continue
            if pid is None or pid not in cat: continue
            if line.startswith("@"):
                tag = line[1:].strip().split()[0] if line[1:].strip() else ""
                if tag == "column": continue
                flush(); insec = tag == "seal"; lines = []; ok = True
                continue
            if not insec: continue
            m = re.match(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$", line)
            if not m: continue
            w = words(m.group(2))
            if w is None: ok = False
            elif w: lines.append(w)
    flush(); emit()
    with open(OUT / "ur3_occ.jsonl", "w") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter(r["prov"] for r in out)
    print(len(out), "occurrences;", len({json.dumps(r['legend']) for r in out}), "distinct legends")
    print(c.most_common(12))


if __name__ == "__main__":
    main()
