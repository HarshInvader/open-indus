"""Linear B (DAMOS) documents as token sequences for meaning_calibration (prereg docs/prereg/meaning_calibration.md).

Rules (fixed before sealing):
- one document = one DAMOS item with heading and content; site = heading prefix; class W = sealing, Z = vase, else tablet
- line labels (.1, .2a, ...) removed; quote marks removed but the quoted writing kept (it is text, e.g. 'ZE')
- erased text between the erasure brackets is dropped
- under-dots (uncertain readings) are stripped; the reading is kept
- metadata tokens (DROP list, any lowercase token ending in '.', Greek face labels) are dropped
- any token carrying [ or ] becomes a break '#' (consecutive breaks collapsed; leading/trailing breaks removed)
- whole words, ideograms (with qualifiers such as OVIS:m), measure signs and each numeral are tokens
- documents with no token are dropped
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
DROP = {"mut", "inf", "sup", "vac", "vest", "deest", "lat", "v", "r", "supra", "infra", "sigillum", "fragmentum",
        "vacat", "recto", "verso", "α", "β", "γ", "δ", "ε", "↓", "→", "←", "↑", "v.↓", "v.→", "v.←", "v.↑", "+", "-", "±"}
GREEK = re.compile(r"^[α-ω]+$")


def _clean(tok):
    tok = tok.replace("̣", "").replace("'", "")
    return tok


def tokens(content):
    content = re.sub(r"⟦[^⟧]*⟧", " ", content)
    out = []
    for line in content.split("\n"):
        line = re.sub(r"^\s*\.\S*", " ", line)
        for t in re.split(r"[\s,/]+", line):
            t = _clean(t)
            if not t:
                continue
            if "[" in t or "]" in t:
                if out and out[-1] != "#":
                    out.append("#")
                continue
            t = t.replace("⟦", "").replace("⟧", "")
            if not t:
                continue
            if t in DROP or t.rstrip(".") in DROP or GREEK.match(t) or re.fullmatch(r"[a-z]+\.\S*", t):
                continue
            if not re.search(r"[A-Za-z0-9*]", t):
                continue
            out.append(t)
    while out and out[0] == "#":
        out.pop(0)
    while out and out[-1] == "#":
        out.pop()
    return out


def obj_class(heading):
    h = heading.split()
    ser = h[1][:1] if len(h) > 1 else ""
    return "sealing" if ser == "W" else "vase" if ser == "Z" else "tablet"


def documents():
    docs = []
    for line in open(SRC, encoding="utf-8"):
        x = json.loads(line)
        if not x.get("heading") or not x.get("content"):
            continue
        seq = tokens(x["content"])
        if not any(s != "#" for s in seq):
            continue
        docs.append(dict(id=x["id"], heading=x["heading"], site=x["heading"].split()[0], cls=obj_class(x["heading"]), seq=seq))
    return docs


def length(seq):
    return sum(s != "#" for s in seq)


if __name__ == "__main__":
    from collections import Counter
    D = documents()
    print(len(D), Counter(d["cls"] for d in D), Counter(d["site"] for d in D).most_common(8))
    c = Counter(s for d in D for s in d["seq"] if s != "#")
    print(len(c), c.most_common(40))
    print([d["seq"] for d in D[:3]])
