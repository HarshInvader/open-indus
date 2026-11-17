"""Build class-tagged short-unit corpora from three read scripts (data prep only, no outcomes).
Cuneiform: ORACC epsd2/admin/oakk (CC0), line units, ORACC POS.
Egyptian: TLA Earlier Egyptian v18 (CC BY-SA, local copy in short_labels/raw/tla), sentence units, UPOS.
Latin: EDH transcriptions (local copy in short_labels/raw/edh), line units ('/'), editor capitalisation.
Classes: NUM, NAME, CONTENT, FUNC (None = unlabeled, kept as context).
usage: .venv/bin/python -I experiments/meaning_classes/build_corpora.py
writes experiments/meaning_classes/data/{cun,egy,lat}.jsonl : {"seq": [type..], "cls": [class..]}
"""
import json, glob, re
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)

NAME_POS = {"PN", "DN", "GN", "SN", "MN", "TN", "FN", "WN", "RN", "ON", "EN", "CN", "AN", "LN", "QN", "YN"}
CONTENT_POS = {"N", "AJ", "AV", "V/i", "V/t", "V", "MA"}
FUNC_POS = {"CNJ", "PRP", "DP", "IP", "XP", "RP", "QP", "MOD", "J", "REL", "SBJ", "PP"}


def cls_oracc(pos):
    if pos in ("n", "NU"): return "NUM"
    if pos in NAME_POS: return "NAME"
    if pos in CONTENT_POS: return "CONTENT"
    if pos in FUNC_POS: return "FUNC"
    return None


def cuneiform():
    units = []
    for fn in sorted(glob.glob(str(HERE / "raw/oracc/epsd2/admin/oakk/corpusjson/*.json"))):
        d = json.load(open(fn))
        cur = []

        def flush():
            if cur: units.append(list(cur))
            cur.clear()

        def walk(x):
            if isinstance(x, dict):
                if x.get("node") == "d" and x.get("type") == "line-start":
                    flush()
                elif x.get("node") == "l":
                    f = x.get("f", {})
                    form = f.get("form")
                    if form and "x" not in form.split("-") and "..." not in form:
                        # numerals: type is the counted unit without the count, e.g. 1(barig@c) -> N(barig@c)
                        key = re.sub(r"^\d+(/\d+)?\(", "N(", form) if f.get("pos") in ("n", "NU") else form
                        cur.append((key, cls_oracc(f.get("pos"))))
                    else:
                        cur.append(("<BRK>", None))
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(d); flush()
    return units


UP = {"NUM": "NUM", "PROPN": "NAME", "NOUN": "CONTENT", "VERB": "CONTENT", "ADJ": "CONTENT", "ADV": "CONTENT",
      "ADP": "FUNC", "PRON": "FUNC", "DET": "FUNC", "PART": "FUNC", "CCONJ": "FUNC", "SCONJ": "FUNC", "AUX": "FUNC"}


def egyptian():
    units = []
    for line in open(ROOT / "experiments/short_labels/raw/tla/train.jsonl"):
        r = json.loads(line)
        lem = r["lemmatization"].split(); up = r["UPOS"].split()
        if len(lem) != len(up): continue
        units.append([(l.split("|")[0], UP.get(u)) for l, u in zip(lem, up)])
    return units


LAT_FUNC = set("""et ac atque que in ex e ab a cum de ad per pro sub post ante inter ob sine qui quae quod cuius cui quem quam
quibus quos quas hic haec hoc huius huic hunc hanc eius eorum earum eis ei is ea id sibi se suis suo suae sua suus suum
sui nec neque non vel aut sive si ut ne""".split())
ROMAN = re.compile(r"^[IVXLCDM]+$")


def latin():
    units = []
    for fn in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        for it in json.load(open(fn))["items"]:
            tr = it.get("transcription") or ""
            for ln in re.split(r"/+", tr):
                toks = []
                bad = False
                for w in ln.split():
                    if any(c in w for c in "[]-?!<>{}=+") or "(---)" in w:
                        bad = True; break
                    w2 = w.replace("(", "").replace(")", "").strip(".,;:")
                    if not w2 or not re.fullmatch(r"[A-Za-z]+", w2): bad = True; break
                    if ROMAN.match(w2) and w2 == w: c = "NUM"
                    elif w2[0].isupper(): c = "NAME"
                    elif w2.lower() in LAT_FUNC: c = "FUNC"
                    else: c = "CONTENT"
                    toks.append((w2.lower() if c != "NAME" else w2, c))
                if not bad and toks: units.append(toks)
    return units


def main():
    for name, fn in (("cun", cuneiform), ("egy", egyptian), ("lat", latin)):
        U = fn()
        with open(OUT / f"{name}.jsonl", "w") as f:
            for u in U:
                f.write(json.dumps({"seq": [t for t, _ in u], "cls": [c for _, c in u]}) + "\n")
        L = [len(u) for u in U]
        cc = Counter(c for u in U for _, c in u)
        print(name, "units", len(U), "mean len", round(sum(L) / len(L), 2), dict(cc))


if __name__ == "__main__":
    main()
