"""Word-level seal legends from the CDLI open dump (untrusted; parsed as text only).
Independent of genre_alignment code. Run: .venv/bin/python -I experiments/closer_ownership/co_extract.py
Writes data/legends_all.jsonl: {pid, period, lang, otype, words}  (distinct legends per period group, no broken word)
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[0] / "short_labels/raw/cdli"
csv.field_size_limit(10**9)


def load_cat():
    cat = {}
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit():
                cat["P" + pid.zfill(6)] = ((r.get("object_type") or "").lower().strip(),
                                           (r.get("period") or "").strip(),
                                           (r.get("provenience") or "").strip(),
                                           (r.get("genre") or "").strip())
    return cat


def words(content):
    s = re.sub(r"\(\$.*?\$\)", " ", content)
    s = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", s)
    s = s.replace("_", " ").replace("…", " ... ")
    out = []
    for w in s.split():
        if w in (",", ":", ";", "/", "|") or w.startswith("$"): continue
        w = w.lower()
        parts = re.split(r"[-.+]", re.sub(r"\{[^}]*\}", "-", w))
        if any(p in ("x", "...") or re.fullmatch(r"x+", p or "") or "..." in p for p in parts): return None
        if "..." in w: return None
        out.append(w)
    return out


def parse(cat):
    pid = None; lang = ""; insec = False; buf = []; ok = True; objbuf = []
    def emit(seq, src):
        ot, per, prov, gen = cat.get(pid, ("", "", "", ""))
        return dict(pid=pid, period=per, lang=lang, otype=ot, prov=prov, src=src, words=seq)
    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                if pid:
                    if insec and buf and ok: yield emit(buf, "seal_section")
                    ot = cat.get(pid, ("",))[0]
                    if objbuf and (ot.startswith("seal") or ot == "sealing"): yield emit(objbuf, "seal_object")
                pid = line[1:8]; lang = ""; insec = False; buf = []; ok = True; objbuf = []
                continue
            if pid is None: continue
            if line.startswith("#atf:") and "lang" in line:
                rest = line.split("lang", 1)[1].strip(); lang = rest.split()[0] if rest else ""; continue
            if line.startswith("@"):
                tag = (line[1:].strip().split() or [""])[0]
                if tag == "column": continue
                if insec and buf and ok: yield emit(buf, "seal_section")
                insec = (tag == "seal"); buf = []; ok = True
                continue
            m = re.match(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$", line)
            if not m: continue
            w = words(m.group(2))
            if insec:
                if w is None: ok = False
                elif ok: buf += w
            else:
                if w is None or objbuf is None: objbuf = None
                else: objbuf += w
    if pid:
        if insec and buf and ok: yield emit(buf, "seal_section")


GROUPS = [  # period-prefix -> group
    ("ED IIIb", "ed3b"), ("ED IIIa", "ed3a"), ("Old Akkadian", "oakk"), ("Lagash II", "lag2"),
    ("Ur III", "ur3"), ("Early Old Babylonian", "ob"), ("Old Babylonian", "ob"), ("Old Assyrian", "oa"),
    ("Middle Babylonian", "mb"), ("Middle Assyrian", "ma"), ("Neo-Assyrian", "na"), ("Neo-Babylonian", "nb"),
    ("Achaemenid", "ach"), ("Middle Elamite", "me"), ("Neo-Elamite", "ne"), ("Old Elamite", "oe"),
    ("Hellenistic", "hel"),
]


def group(period):
    for k, g in GROUPS:
        if period.startswith(k): return g
    return None


def main():
    cat = load_cat()
    seen = defaultdict(set); out = []; prov = defaultdict(Counter)
    for r in parse(cat):
        g = group(r["period"])
        if not g or not r["words"]: continue
        if r["lang"].startswith(("qpc", "qpe")): continue
        key = tuple(r["words"])
        if key in seen[g]: continue
        seen[g].add(key); r["group"] = g; out.append(r); prov[g][r["prov"].split("(")[0].strip()] += 1
    with open(HERE / "data/legends_all.jsonl", "w") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter(r["group"] for r in out)
    for g, n in c.most_common():
        print(f"{g:6s} {n:6d}  top prov: {prov[g].most_common(4)}")


if __name__ == "__main__":
    main()
