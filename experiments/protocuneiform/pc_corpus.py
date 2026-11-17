"""Parse CDLI ATF (untrusted data, read as text only) into proto-cuneiform (Uruk IV-III administrative)
and Proto-Elamite (administrative) line records. No Indus data is touched here.

Output: pc_lines.json, pe_lines.json  ->  list of {pid, period, surface, lineno, tokens, has_num, first_entry}
Run: .venv/bin/python -I experiments/protocuneiform/pc_corpus.py
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw/cdli_atf"
csv.field_size_limit(10**9)

NUM = re.compile(r"^(\d+|n|N)\((N\d+[^)]*)\)$")


def clean(tok):
    tok = re.sub(r"[\[\]#?!<>*]", "", tok)
    return tok.strip()


def tokenize(body):
    body = re.sub(r"\{[^}]*\}", "", body)      # determinatives/glosses rarely used
    body = body.replace(",", " , ")
    out = []
    for t in body.split():
        t = clean(t)
        if not t or t in (",", "...", "x", "X", "N", "n", "[...]") or t.startswith("$"):
            if t == ",":
                out.append(",")
            continue
        out.append(t)
    return out


def is_num(t):
    return bool(NUM.match(t))


def main():
    meta = {}
    with open(RAW / "cdli_cat.csv", newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            try:
                meta[int(r["id_text"])] = (r["period"] or "", (r["genre"] or "").lower())
            except ValueError:
                pass
    txt = open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="replace").read()
    pc, pe = [], []
    for b in re.split(r"\n(?=&P)", txt):
        m = re.match(r"&P(\d+)", b)
        if not m:
            continue
        pid = int(m.group(1))
        period, genre = meta.get(pid, ("", ""))
        if genre != "administrative":
            continue
        if period.startswith("Uruk IV") or period.startswith("Uruk III"):
            dest = pc
        elif period.startswith("Proto-Elamite"):
            dest = pe
        else:
            continue
        surface, k = "", 0
        for line in b.split("\n"):
            line = line.strip()
            if line.startswith("@"):
                surface = line[1:].split()[0] if len(line) > 1 else surface
                continue
            lm = re.match(r"^([0-9a-z'.]+)\.\s+(.*)$", line)
            if not lm or line.startswith("#") or line.startswith("&"):
                continue
            toks = tokenize(lm.group(2))
            signs = [t for t in toks if t != ","]
            if not signs:
                continue
            k += 1
            dest.append({"pid": pid, "period": period, "surface": surface, "line": lm.group(1),
                         "k": k, "tokens": toks, "has_num": any(is_num(t) for t in signs)})
    json.dump(pc, open(HERE / "pc_lines.json", "w"))
    json.dump(pe, open(HERE / "pe_lines.json", "w"))
    print("PC lines", len(pc), "texts", len({r["pid"] for r in pc}))
    print("PE lines", len(pe), "texts", len({r["pid"] for r in pe}))


if __name__ == "__main__":
    main()
