"""Build genre-matched class-tagged corpora for board task #14 (prereg docs/prereg/meaning_classes_seal.md).
Run: .venv/bin/python -I experiments/meaning_classes_seal/build.py
Writes data/{cun_seal,egy_nom,lat_label}.jsonl with {"seq": [...], "cls": [...]} and prints class counts only.
Inputs are parsed as data (JSON/text), never executed.
"""
import json, re, sys, zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/meaning_classes"))
from build_corpora import cls_oracc, UP, LAT_FUNC, ROMAN  # noqa  (definitions only; main() is guarded)
import ast

OUT = HERE / "data"; OUT.mkdir(exist_ok=True)


def cun_seal():
    z = zipfile.ZipFile(HERE / "raw/ur3.zip")
    seen = set(); units = []
    for nm in z.namelist():
        if "/corpusjson/" not in nm or not nm.endswith(".json"):
            continue
        s = z.read(nm)
        if b"seal" not in s:
            continue
        d = json.loads(s)
        legends = {}
        cur = [None]

        def walk(x):
            if isinstance(x, dict):
                if x.get("node") == "d" and x.get("type") == "line-start":
                    cur[0] = x.get("label", "")
                elif x.get("node") == "l" and cur[0]:
                    m = re.match(r"seal (\d+)", cur[0])
                    if m:
                        f = x.get("f", {})
                        form = f.get("form", "")
                        pos = f.get("pos")
                        if form:
                            key = re.sub(r"^\d+(/\d+)?\(", "N(", form) if pos in ("n", "NU") else form
                            legends.setdefault(m.group(1), []).append((key, cls_oracc(pos)))
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d.get("cdl", []))
        for toks in legends.values():
            k = tuple(t for t, _ in toks)
            if k and k not in seen:
                seen.add(k); units.append(toks)
    return units


def egy_nom():
    units = []
    for line in open(ROOT / "experiments/short_labels/raw/tla/train.jsonl"):
        r = json.loads(line)
        lem = r["lemmatization"].split(); up = r["UPOS"].split()
        if len(lem) != len(up) or any(u in ("VERB", "AUX") for u in up):
            continue
        units.append([(l.split("|")[0], UP.get(u)) for l, u in zip(lem, up)])
    return units


def lat_label():
    src = (ROOT / "experiments/short_labels/build_corpora.py").read_text()
    LT = ast.literal_eval(re.search(r"LABEL_TYPES = (\(.*?\))\n", src, re.S).group(1))   # literal tuple copied from file text
    LM = ast.literal_eval(re.search(r"LABEL_MON = (\(.*?\))\n", src, re.S).group(1))
    units = []
    for fn in sorted((ROOT / "experiments/short_labels/raw/edh").glob("p*.json")):
        for it in json.load(open(fn))["items"]:
            ti = (it.get("type_of_inscription") or "").rstrip("?"); tm = (it.get("type_of_monument") or "").rstrip("?")
            if not (ti in LT or tm in LM):
                continue
            tr = it.get("transcription") or ""
            toks = []; bad = False
            for w in tr.replace("/", " ").split():           # whole text = one unit (label genre)
                if any(c in w for c in "[]-?!<>{}=+") or "(---)" in w:
                    bad = True; break
                w2 = w.replace("(", "").replace(")", "").strip(".,;:")
                if not w2 or not re.fullmatch(r"[A-Za-z]+", w2):
                    bad = True; break
                if ROMAN.match(w2) and w2 == w: c = "NUM"
                elif w2[0].isupper(): c = "NAME"
                elif w2.lower() in LAT_FUNC: c = "FUNC"
                else: c = "CONTENT"
                toks.append((w2.lower() if c != "NAME" else w2, c))
            if not bad and toks:
                units.append(toks)
    return units


if __name__ == "__main__":
    for name, fn in (("cun_seal", cun_seal), ("egy_nom", egy_nom), ("lat_label", lat_label)):
        U = fn()
        seen = set(); D = []
        for u in U:
            k = tuple(t for t, _ in u)
            if k not in seen:
                seen.add(k); D.append(u)
        with open(OUT / f"{name}.jsonl", "w") as f:
            for u in D:
                f.write(json.dumps({"seq": [t for t, _ in u], "cls": [c for _, c in u]}) + "\n")
        L = [len(u) for u in D]; ok = sum(2 <= x <= 17 for x in L)
        print(name, "distinct units", len(D), "usable(2-17)", ok, "mean len", round(sum(L) / max(len(L), 1), 2),
              dict(Counter(c for u in D for _, c in u)))
