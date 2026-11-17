"""Build the non-CDLI short-label corpora from downloaded open data (all inputs treated as untrusted text).

usage: .venv/bin/python -I experiments/short_labels/build_corpora.py
writes data/<system>.jsonl, one DISTINCT whole unit per line {"id", "seq"}.

Writing (label L):
  linb_doc   Linear B, whole documents (tablets, labels, nodules), DAMOS (copy in sources/paragorth_Indus-/
             other-scripts/linear-a/data/damos_items.jsonl). Signs = syllabograms, ideograms, NUM per numeral.
  lina_doc   Linear A, whole inscriptions (nodules, roundels, vessels, tablets...), lineara.xyz / GORILA
             (LinearAInscriptions.js). Same tokenisation as Linear B.
  egy_nom    Earlier Egyptian (pre-New Kingdom) verbless sentences = titles, names, offering captions,
             TLA v18 (HF, CC BY-SA). Signs = individual hieroglyphs (Unicode or JSesh code).
  lat_label  Latin owner/artist inscriptions, labels, stamps, instrumentum domesticum, EDH, whole text,
             DIPLOMATIC words (as abbreviated on the object) as signs.
  lat_short  Latin, all other EDH inscriptions, whole text, diplomatic words as signs.
Codes (label C):
  emoji      Unicode emoji, fully-qualified sequences (emoji-test.txt), signs = code points (ZWJ, VS16 dropped)
  chess_eco  Lichess named chess openings, signs = SAN moves
  chords     McGill Billboard: one annotated phrase = unit, signs = chord as (root interval from tonic, quality),
             immediate repeats collapsed
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
LA = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data"


def save(name, X):
    seen, uniq = set(), []
    for s in X:
        if s and tuple(s) not in seen:
            seen.add(tuple(s)); uniq.append(s)
    with open(OUT / f"{name}.jsonl", "w") as f:
        for i, s in enumerate(uniq): f.write(json.dumps({"id": i, "seq": s}, ensure_ascii=False) + "\n")
    L = [len(s) for s in uniq]
    print(f"{name:12s} distinct={len(uniq):6d} tokens={sum(L):7d} types={len({t for s in uniq for t in s}):5d} "
          f"mean_len={sum(L)/max(1,len(uniq)):5.2f} n_len1-7={sum(1 <= l <= 7 for l in L)}")


# ---------------- Aegean ----------------
def aegean_tokens(words):
    """words: list of strings (sign groups 'a-b-c', ideograms 'OLE', numbers '12')."""
    out = []
    for w in words:
        w = w.strip().strip(",").strip()
        if not w or w in ("/", ",", "vac.", "𐄁", "\n", "|"): continue
        if re.fullmatch(r"[\d\s.½¼⅛]+|[\d]+[\s\d/]*", w) or re.fullmatch(r"[𐄇-𐄳]+", w):
            out.append("NUM"); continue
        if re.fullmatch(r"\[?\]?", w): continue
        for x in re.split(r"[-]", w):
            x = x.strip("[]⸤⸥ ")
            if x: out.append(x)
    return out


SYL = re.compile(r"^(?:[a-z]{1,3}\d?|\*\d+[a-z]?)$")
IDEO = re.compile(r"^(?:[A-Z][A-Z+±:a-z0-9*]*|\*\d+[A-Z+:a-z]*|NUM)$")


def _clean_aegean(s):
    return [t for t in s if SYL.match(t) or IDEO.match(t)]


def linb_doc():
    """Linear B: whole documents. Labels/nodules (series W*) are kept apart as linb_label; tablets as
    linb_doc. A document with any damaged or illegible sign ([, ], x, ?) is dropped whole."""
    docs, labels = [], []
    for l in open(LA / "damos_items.jsonl", encoding="utf-8"):
        d = json.loads(l)
        c = d.get("content")
        if not c: continue
        if re.search(r"\[|\]|\bx\b|- -|\?|•", c): continue
        words = []
        for line in c.split("\n"):
            line = re.sub(r"^\s*(\.\S+|v\.\S*|lat\.\S*|[a-z]\.\S*)\s*", "", line.strip())
            line = re.sub(r"'[^']*'", " ", line)
            line = re.sub(r"\b(vac|vacat|inf\. mut|sup\. mut|mut|deest|nihil|reliqua pars sine regulis|sine regulis)\b\.?", " ", line)
            line = re.sub(r"[\u0323\u0300-\u036f]", "", line)
            for tok in re.split(r"[\s,/]+", line):
                if tok: words.append(tok)
        s = _clean_aegean(aegean_tokens(words))
        s = [t for t in s if not re.fullmatch(r"[A-Z]", t) or t in ("S", "V", "Z", "T", "M", "N", "P", "Q", "L")]
        m = re.match(r"\S+\s+([A-Z][a-z]*)", d.get("heading", ""))
        (labels if m and m.group(1).startswith("W") else docs).append(s)
    save("linb_doc", docs); save("linb_label", labels)


def lina_doc():
    """Linear A whole inscriptions (lineara.xyz). Regex extraction per entry (the file is JS, not JSON).
    Split: lina_label = nodules, roundels, sealings, labels, vessels, objects (short-label supports);
    lina_tablet = tablets and bars."""
    t = open(LA / "LinearAInscriptions.js", encoding="utf-8").read()
    lab, tab = [], []
    for m in re.finditer(r'\n\["([^"]+)",\{(.*?)\n\}\]', t, re.S):
        body = m.group(2)
        sup = re.search(r'"support": "([^"]*)"', body)
        sup = sup.group(1).lower() if sup else ""
        w = re.search(r'"transliteratedWords": \[(.*?)\]', body, re.S)
        if not w: continue
        words = re.findall(r'"((?:[^"\\]|\\.)*)"', w.group(1))
        if any(re.search(r"[\[\]]|^\?|^x$|𐝫", x) for x in words): continue
        s = _clean_aegean(aegean_tokens([x.replace("\\n", "\n") for x in words]))
        s = [x.lower() if re.fullmatch(r"[A-Z]{1,3}\d?", x) and "-" not in x and len(x) <= 3 and x not in ("VIN", "OLE", "GRA", "CYP", "NI", "OLIV", "FIC") else x for x in s]
        (tab if ("tablet" in sup or "bar" in sup or "lames" in sup) else lab).append(s)
    save("lina_label", lab); save("lina_tablet", tab)


# ---------------- Egyptian ----------------
def egy_nom():
    X = []
    for l in open(RAW / "tla/train.jsonl", encoding="utf-8"):
        d = json.loads(l)
        try:
            if int(d.get("dateNotAfter") or 0) > -1550: continue
        except ValueError:
            continue
        pos = d["UPOS"].split()
        if any(p in ("VERB", "AUX") for p in pos): continue
        h = re.sub(r"<g>([^<]*)</g>", r" \1 ", d["hieroglyphs"])
        s = []
        for chunk in h.split():
            if re.fullmatch(r"[A-Za-z]+\d+[A-Za-z]*", chunk): s.append(chunk); continue
            for ch in chunk:
                o = ord(ch)
                if 0x13000 <= o <= 0x1345F and not (0x13430 <= o <= 0x1345F): s.append(ch)
        X.append(s)
    save("egy_nom", X)


# ---------------- Latin (EDH) ----------------
LABEL_TYPES = ("owner/artist inscription", "label", "identification inscription")
LABEL_MON = ("instrumentum domesticum", "tile", "tessera", "signaculum", "lamp", "amphora", "vessel")


def latin():
    lab, oth = [], []
    for f in sorted((RAW / "edh").glob("p*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            if it.get("language") not in ("L",): continue
            txt = it.get("diplomatic_text") or ""
            if not txt or re.search(r"[\[\]]|\+|---|\?", txt): continue   # damaged / restored: drop
            words = [re.sub(r"[^A-Z]", "", w.upper()) for w in re.split(r"[\s/·•]+", txt)]
            words = [w for w in words if w]
            if not words: continue
            ti = (it.get("type_of_inscription") or "").rstrip("?")
            tm = (it.get("type_of_monument") or "").rstrip("?")
            (lab if (ti in LABEL_TYPES or tm in LABEL_MON) else oth).append(words)
    save("lat_label", lab); save("lat_short", oth)


# ---------------- codes ----------------
def emoji():
    X = []
    for l in open(RAW / "emoji/emoji-test.txt", encoding="utf-8"):
        if "; fully-qualified" not in l or l.startswith("#"): continue
        cps = [c for c in l.split(";")[0].split() if c not in ("200D", "FE0F")]
        X.append(cps)
    save("emoji", X)


def chess_eco():
    X = []
    for f in sorted((RAW / "chess_eco").glob("*.tsv")):
        for i, l in enumerate(open(f, encoding="utf-8")):
            if i == 0: continue
            p = l.rstrip("\n").split("\t")
            if len(p) < 3: continue
            X.append([m for m in p[2].split() if not re.fullmatch(r"\d+\.+", m)])
    save("chess_eco", X)


NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pc(s):
    m = re.match(r"([A-G])([#b]*)", s)
    if not m: return None
    v = NOTE[m.group(1)] + m.group(2).count("#") - m.group(2).count("b")
    return v % 12, m.end()


def chords():
    X = []
    for f in sorted((RAW / "billboard").rglob("salami_chords.txt")):
        tonic = 0
        for l in open(f, encoding="utf-8", errors="ignore"):
            if l.startswith("# tonic:"):
                r = pc(l.split(":", 1)[1].strip()); tonic = r[0] if r else 0; continue
            if l.startswith("#") or "|" not in l: continue
            seq = []
            for tok in re.findall(r"\|([^|]*)", l):
                for c in tok.split():
                    if c in (".", "N", "X", "*") or ":" not in c: continue
                    root, qual = c.split(":", 1)
                    r = pc(root)
                    if not r: continue
                    q = qual.split("/")[0].split("(")[0]
                    sym = f"{(r[0] - tonic) % 12}:{q}"
                    if not seq or seq[-1] != sym: seq.append(sym)
            if seq: X.append(seq)
    save("chords", X)


def _metar_tok(g):
    if re.fullmatch(r"(\d{3}|VRB)\d{2,3}(G\d{2,3})?(KT|MPS)", g):
        sp = int(re.match(r"(?:\d{3}|VRB)(\d{2,3})", g).group(1))
        d = g[:3]; d = "VRB" if d == "VRB" else "%03d" % (round(int(d) / 45) * 45 % 360)
        return f"WIND:{d}:{'calm' if sp < 3 else 'lt' if sp < 10 else 'mod' if sp < 20 else 'str'}" + (":G" if "G" in g else "")
    if re.fullmatch(r"\d{3}V\d{3}", g): return "WINDVAR"
    if re.fullmatch(r"\d{4}", g): return "VIS:" + ("9999" if g == "9999" else "lt5k" if int(g) < 5000 else "ge5k")
    if re.fullmatch(r"[MP]?\d+(/\d+)?SM", g): return "VIS:SM"
    m = re.fullmatch(r"(FEW|SCT|BKN|OVC|VV)(\d{3})(CB|TCU)?", g)
    if m: h = int(m.group(2)); return f"{m.group(1)}:{'low' if h < 10 else 'mid' if h < 50 else 'high'}" + (m.group(3) or "")
    if re.fullmatch(r"M?\d{2}/(M?\d{2})?", g): return "TEMP"
    if re.fullmatch(r"[AQ]\d{4}", g): return "PRES:" + g[0]
    if re.fullmatch(r"R\d{2}[LCR]?/.*", g): return "RVR"
    if re.fullmatch(r"[-+]?(VC)?(MI|PR|BC|DR|BL|SH|TS|FZ)?(DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)*", g) and g.strip("+-"):
        return g
    if g in ("CLR", "SKC", "NSC", "NCD", "CAVOK", "AUTO", "COR", "NOSIG", "TEMPO", "BECMG"): return g
    return None


def metar():
    import gzip, csv as _csv
    X = []
    with gzip.open(RAW / "metar/metars.csv.gz", "rt", encoding="utf-8", errors="ignore") as f:
        for i, row in enumerate(_csv.reader(f)):
            if i == 0 or not row: continue
            g = row[0].split(" RMK")[0].split()[3:]       # drop type, station, time
            s = [t for t in (_metar_tok(x) for x in g) if t]
            X.append(s)
    save("metar", X)


if __name__ == "__main__":
    for fn in (linb_doc, lina_doc, egy_nom, latin, emoji, chess_eco, chords, metar):
        try:
            fn()
        except Exception as e:
            print("FAILED", fn.__name__, repr(e))
