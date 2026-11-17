"""Extract real short-label cuneiform registers from the CDLI open dump (github cdli-gh/data).

usage: .venv/bin/python -I experiments/short_labels/cdli_extract.py
reads  raw/cdli/cdliatf_unblocked.atf, raw/cdli/cdli_cat.csv  (untrusted data, parsed as text only)
writes data/<system>.jsonl  (one distinct text per line: {"id", "seq"})

Units (whole texts, never cut):
  seal legends  = @seal sections on tablets/envelopes + whole texts of seal / sealing objects
  tags          = whole texts of objects typed tag / bulla / docket
  bricks        = whole texts of objects typed brick (royal brick stamps and inscriptions)
  proto_cun     = one entry line (case) of Uruk IV/III proto-cuneiform (lang qpc)
Tokens = signs: words split at '-', '.', '+'; determinatives {x} are signs; a number written n(UNIT)
becomes the numeral sign 'N:UNIT' (count dropped, as in the Proto-Elamite codelib). Readings are
lower-cased (sumerograms and syllabic values of one sign stay distinct readings: documented caveat).
Texts containing broken signs (x, X, ...) are dropped. Duplicates (same seal rolled on many tablets)
are collapsed: one copy per distinct sequence.
"""
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw/cdli"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)

PERIOD_GROUP = [
    ("Ur III", "ur3"), ("Old Akkadian", "oakk"), ("Lagash II", "oakk"), ("ED IIIb", "oakk"),
    ("Early Old Babylonian", "ob"), ("Old Babylonian", "ob"), ("Old Assyrian", "ob"),
    ("Middle Babylonian", "late"), ("Middle Assyrian", "late"), ("Neo-Assyrian", "late"),
    ("Neo-Babylonian", "late"), ("Achaemenid", "late"), ("Middle Elamite", "late"), ("Neo-Elamite", "late"),
]


def pgroup(period):
    for k, g in PERIOD_GROUP:
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


NUM = re.compile(r"^(?:\d+(?:/\d+)?|n)\(([^)]+)\)$")


def tokenize(content):
    """returns list of sign tokens, or None if the line has broken/illegible signs"""
    s = content
    s = re.sub(r"\(\$.*?\$\)", " ", s)              # inline comments
    s = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", s)
    s = s.replace("_", " ").replace("…", " ... ")
    toks = []
    for w in s.split():
        if w in (",", ":", ";", "/", "|") or w.startswith("$"): continue
        w = re.sub(r"\{\+?([^}]*)\}", r"-\1-", w)    # determinatives / complements are signs
        for x in re.split(r"[-.+]", w):
            x = x.strip().lower()
            if not x: continue
            if x in ("x", "...") or re.fullmatch(r"x+", x) or "..." in x: return None
            m = NUM.match(x)
            if m: toks.append("N:" + m.group(1)); continue
            if re.fullmatch(r"\d+", x): toks.append("N:num"); continue
            toks.append(x)
    return toks


def parse(cat):
    """yield (pid, lang, kind, seq). kind in seal/tag/brick/protoline"""
    pid = None; lang = ""; insec = False; buf = []; objbuf = []
    def flush():
        res = []
        if pid is None: return res
        ot, period = cat.get(pid, ("", ""))
        if buf and insec_buf_ok[0]: res.append((pid, lang, "seal", list(buf), period))
        if objbuf is not None and objbuf:
            if ot.startswith("seal") or ot == "sealing": res.append((pid, lang, "seal", list(objbuf), period))
            elif ot in ("tag", "bulla", "docket"): res.append((pid, lang, "tag", list(objbuf), period))
            elif ot == "brick": res.append((pid, lang, "brick", list(objbuf), period))
        return res
    insec_buf_ok = [True]
    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                for r in flush(): yield r
                pid = line[1:8]; lang = ""; insec = False; buf = []; objbuf = []; insec_buf_ok[0] = True
                continue
            if pid is None: continue
            if line.startswith("#atf:") and "lang" in line:
                lang = line.split("lang", 1)[1].strip().split()[0] if line.split("lang", 1)[1].strip() else ""
                continue
            if line.startswith("@"):
                tag = line[1:].strip().split()[0] if line[1:].strip() else ""
                if tag == "seal":
                    if buf and insec_buf_ok[0]:
                        ot, period = cat.get(pid, ("", "")); yield (pid, lang, "seal", list(buf), period)
                    insec = True; buf = []; insec_buf_ok[0] = True
                elif tag in ("column",):
                    pass
                else:
                    if insec and buf and insec_buf_ok[0]:
                        ot, period = cat.get(pid, ("", "")); yield (pid, lang, "seal", list(buf), period)
                    insec = False; buf = []; insec_buf_ok[0] = True
                continue
            m = re.match(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$", line)
            if not m: continue
            toks = tokenize(m.group(2))
            if lang.startswith("qpc"):
                if toks: yield (pid, lang, "protoline", toks, cat.get(pid, ("", ""))[1])
                continue
            if insec:
                if toks is None: insec_buf_ok[0] = False
                else: buf += toks
            else:
                if toks is None or objbuf is None: objbuf = None
                else: objbuf += toks
        for r in flush(): yield r


def main():
    cat = load_cat()
    sysd = defaultdict(list); seen = defaultdict(set)
    for pid, lang, kind, seq, period in parse(cat):
        if not seq or lang.startswith(("qpe",)): continue
        if kind == "protoline":
            name = "proto_cun"
        elif kind == "seal":
            g = pgroup(period)
            if not g: continue
            name = "cun_seal_" + g
        elif kind == "tag":
            name = "cun_tag"
        else:
            name = "cun_brick"
        key = tuple(seq)
        if key in seen[name]: continue
        seen[name].add(key); sysd[name].append(seq)
    for name, X in sorted(sysd.items()):
        with open(OUT / f"{name}.jsonl", "w") as f:
            for i, s in enumerate(X): f.write(json.dumps({"id": i, "seq": s}) + "\n")
        L = [len(s) for s in X]
        print(f"{name:16s} distinct={len(X):6d} tokens={sum(L):7d} types={len({t for s in X for t in s}):5d} "
              f"mean_len={sum(L)/len(X):5.2f} n_len3-7={sum(3 <= l <= 7 for l in L)}")


if __name__ == "__main__":
    main()
