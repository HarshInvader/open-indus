"""Build reference value distributions (counts of values 1..N) for each reference class.

usage: .venv/bin/python -I experiments/numeral_class/refs.py
Reads untrusted downloaded data as TEXT only:
  experiments/short_labels/raw/cdli/{cdliatf_unblocked.atf, cdli_cat.csv}   (CDLI open dump)
  sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl    (DAMOS Linear B)
  experiments/short_labels/raw/edh/p*.json                                   (Epigraphic Database Heidelberg)
  experiments/numeral_class/raw/gretil/rv.txt                                (Rigveda, Aufrecht, GRETIL)
  experiments/naming_sim names (Sanskrit MW persons, Chinese given names) via names.py (local code)
Writes data/refs.json : {subcorpus: {"class": X, "counts": {v: n}, "n": total, "note": ...}}
Rules are those frozen in docs/prereg/numeral_class.md.
"""
import csv, json, re, sys, glob
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CDLI = ROOT / "experiments/short_labels/raw/cdli"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)

# ------------------------------------------------------------------ CDLI number parsing
COUNT_UNITS = {"disz": 1, "asz": 1, "u": 10, "gesz2": 60, "gesz'u": 600, "geszu": 600, "szar2": 3600}
PROTO_UNITS = {"N01": 1, "N14": 10, "N34": 60, "N45": 600, "N48": 3600}
NUMTOK = re.compile(r"^(\d+)\(([^)]+)\)$")


def clean(line):
    s = re.sub(r"\(\$.*?\$\)", " ", line)
    s = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", s)
    return s.replace("_", " ")


def number_groups(toks, units):
    """maximal runs of n(UNIT) tokens with UNIT in units -> list of (value, index_after_run).
    A run containing any other n(X) token (other metrological system, fraction) is discarded."""
    out, i = [], 0
    while i < len(toks):
        m = NUMTOK.match(toks[i]) or (NUMTOK.match(toks[i].split("-")[0]) if "-" in toks[i] else None)
        if not m:
            i += 1; continue
        j, val, ok = i, 0, True
        while j < len(toks):
            t = toks[j]
            base = t.split("-")[0]
            m2 = NUMTOK.match(base)
            if not m2: break
            u = m2.group(2)
            if u in units: val += int(m2.group(1)) * units[u]
            else: ok = False
            j += 1
            if "-" in t: break      # n(disz)-kam etc. ends the group
        if ok and val > 0: out.append((val, j, toks[j - 1]))
        i = j
    return out


def load_cat():
    cat = {}
    with open(CDLI / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit():
                cat["P" + pid.zfill(6)] = dict(ot=(r.get("object_type") or "").lower().strip(),
                                               per=(r.get("period") or "").strip(),
                                               gen=(r.get("genre") or "").lower().strip())
    return cat


def cdli_texts():
    cur, lines = None, []
    with open(CDLI / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if raw.startswith("&P"):
                if cur: yield cur, lines
                cur, lines = raw[1:8], []
            elif cur and re.match(r"^\d+'?\.", raw):
                lines.append(raw.split(".", 1)[1])
    if cur: yield cur, lines


def build_cdli(R):
    cat = load_cat()
    C = defaultdict(Counter)
    for pid, lines in cdli_texts():
        meta = cat.get(pid)
        if not meta: continue
        per, ot, gen = meta["per"], meta["ot"], meta["gen"]
        is_admin = gen.startswith("administrative")
        tag = ot in ("tag", "bulla", "docket", "label") or ot.startswith("tag") or ot.startswith("bulla")
        for ln in lines:
            s = clean(ln)
            toks = s.split()
            low = " ".join(toks)
            # dates (all periods): u4 N-kam ; years: mu N-kam (MB and later)
            for k, t in enumerate(toks):
                if t in ("u4", "mu") and k + 1 < len(toks):
                    g = number_groups(toks[k + 1:k + 4], COUNT_UNITS)
                    if g and g[0][2].endswith("-kam") and g[0][1] <= 3:
                        v = g[0][0]
                        if t == "u4":
                            C["C_day_cdli"][v] += 1
                        elif per.startswith(("Middle Babylonian", "Neo-Babylonian", "Achaemenid", "Hellenistic",
                                             "Middle Assyrian", "Neo-Assyrian", "Middle Elamite", "Neo-Elamite")):
                            C["D_regnal_cdli"][v] += 1
            if "-kam" in low or " iti " in f" {low} " or low.startswith("mu ") or " mu " in f" {low} ":
                continue   # date lines are not commodity counts
            if per.startswith(("Proto-Elamite", "Uruk IV", "Uruk III")):
                vals = [g[0] for g in number_groups(toks, PROTO_UNITS)]
                key = "A3_proto_elamite" if per.startswith("Proto-Elamite") else "A4_proto_cuneiform"
                if is_admin or per.startswith("Proto-Elamite") or not gen:
                    C[key].update(vals)
                if tag: C["A6_tags_labels"].update(vals)
                continue
            vals = [g[0] for g in number_groups(toks, COUNT_UNITS)]
            if not vals: continue
            if is_admin and per.startswith("Ur III") and len(lines) <= 8: C["A1_ur3_admin_short"].update(vals)
            if is_admin and per.startswith(("Old Akkadian", "ED IIIb")): C["A2_old_akkadian_admin"].update(vals)
            if tag: C["A6_tags_labels"].update(vals)
    cls = {"C_day_cdli": "C", "D_regnal_cdli": "D"}
    for k, c in C.items():
        R[k] = dict(cls=cls.get(k, "A"), counts=dict(c), n=sum(c.values()))


# ------------------------------------------------------------------ Linear B (DAMOS)
def build_linb(R):
    src = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
    c = Counter()
    for l in open(src, encoding="utf-8"):
        d = json.loads(l)
        for line in (d.get("content") or "").split("\n"):
            toks = line.split()
            for k in range(1, len(toks)):
                t, prev = toks[k], toks[k - 1]
                if re.fullmatch(r"\d+", t) and re.fullmatch(r"[A-Z*][A-Z0-9*+±\[\]]*", prev.strip("[]")) \
                        and not re.search(r"[\[\]]", t):
                    c[int(t)] += 1
    R["A5_linear_b"] = dict(cls="A", counts=dict(c), n=sum(c.values()))


# ------------------------------------------------------------------ EDH (Latin)
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s):
    if not re.fullmatch(r"[IVXLC]+", s): return None
    tot, prev = 0, 0
    for ch in reversed(s):
        v = ROMAN[ch]
        tot = tot - v if v < prev else tot + v
        prev = max(prev, v)
    return tot if tot > 0 else None


LATNAME = [(1, r"Prim(?:us|i|o|um|a|ae|ia|ius|ianus|igenius)"), (2, r"Secund(?:us|i|o|um|a|ae|ina|inus|ius|ia)"),
           (3, r"Terti(?:us|i|o|um|a|ae|ia|ius|olus|ola)"), (4, r"Quart(?:us|i|o|um|a|ae|io|ius|ia|inus|ina)"),
           (5, r"Quint(?:us|i|o|um|a|ae|ius|ia|ii|ilius|ianus|illa)"), (6, r"Sext(?:us|i|o|um|a|ae|ius|ia|ilius|ianus)"),
           (7, r"Septim(?:us|i|o|um|a|ae|ius|ia|ii|ianus|ina)"), (8, r"Octav(?:us|i|o|um|a|ae|ius|ia|ii|ianus)"),
           (9, r"Non(?:ius|ia|ii|io|iae|ium|ianus)"), (10, r"Decim(?:us|i|o|um|a|ae|ius|ia|ii)")]


def build_edh(R):
    age, leg, nam = Counter(), Counter(), Counter()
    for fn in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        for it in json.load(open(fn, encoding="utf-8")).get("items", []):
            tr = it.get("transcription") or ""
            t = re.sub(r"[()\[\]{}<>?!/]", "", tr)
            for m in re.finditer(r"\bvix\w*\s+an\w*\s+([IVXLC]+)\b", t):
                v = roman(m.group(1));  age[v] += bool(v)
            for m in re.finditer(r"\bleg\w*\s+([IVXL]+)\b", t, flags=re.I):
                v = roman(m.group(1).upper()); leg[v] += bool(v)
            for v, pat in LATNAME:
                nam[v] += len(re.findall(r"\b" + pat + r"\b", t))
    age.pop(None, None); leg.pop(None, None)
    R["F_age_latin"] = dict(cls="F", counts={k: v for k, v in age.items() if v}, n=sum(age.values()))
    R["I_legion_latin"] = dict(cls="I", counts={k: v for k, v in leg.items() if v}, n=sum(leg.values()))
    R["E3_latin_numeral_names"] = dict(cls="E", counts={k: v for k, v in nam.items() if v}, n=sum(nam.values()))


# ------------------------------------------------------------------ names (Sanskrit, Chinese)
def build_names(R):
    sys.path.insert(0, str(ROOT / "experiments/naming_sim"))
    import names as N
    skt = {"eka": 1, "dvi": 2, "tri": 3, "catur": 4, "paYca": 5, "zaz": 6, "zaq": 6, "sapta": 7, "azwa": 8, "azwA": 8,
           "nava": 9, "daSa": 10, "ekAdaSa": 11, "dvAdaSa": 12}
    t, _ = N.load("sanskrit")
    c = Counter(skt[x[0]] for x in t if x and x[0] in skt)
    R["E1_sanskrit_names"] = dict(cls="E", counts=dict(c), n=sum(c.values()))
    zh = {ch: i + 1 for i, ch in enumerate("一二三四五六七八九十")}
    t, _ = N.load("chinese_given")
    c = Counter(zh[e] for x in t for e in x if e in zh)
    R["E2_chinese_given_names"] = dict(cls="E", counts=dict(c), n=sum(c.values()))


# ------------------------------------------------------------------ Rigveda numerals
RV_FORMS = {
    1: "eka ekaḥ ekam ekā ekena ekasya ekasmin ekasmāt ekasyāḥ ekayā ekām ekasmai eke ekān ekāḥ".split(),
    2: "dvā dvau dve dvābhyām dvayoḥ".split(),
    3: "trayaḥ trīṇi trī tisraḥ tribhiḥ trayāṇām tisṛbhiḥ tisṛṇām tribhyaḥ triṣu trīn".split(),
    4: "catvāraḥ catvāri catasraḥ caturbhiḥ caturaḥ caturṇām catasṛbhiḥ".split(),
    5: "pañca pañcabhiḥ pañcānām pañcasu".split(),
    6: "ṣaṭ ṣaḍ ṣaṇ ṣaḍbhiḥ ṣaṇṇām".split(),
    7: "sapta saptabhiḥ saptānām saptasu".split(),
    8: "aṣṭa aṣṭau aṣṭā aṣṭābhiḥ".split(),
    9: "nava navabhiḥ navānām".split(),
    10: "daśa daśabhiḥ daśānām daśasu".split(),
    11: "ekādaśa ekādaśāsaḥ ekādaśa".split(),
    12: "dvādaśa dvādaśam dvādaśāḥ".split(),
}
RV_PREFIX = {3: ("tri",), 4: ("catur", "catuṣ", "catuḥ"), 5: ("pañca",), 7: ("sapta",), 8: ("aṣṭā",),
             10: ("daśa",), 12: ("dvādaśa",), 2: ("dvi",)}
RV_PREFIX_EXCL = ("trita", "triṣṭubh", "daśasya", "daśasyat", "daśarāja")   # name/verb homographs


def build_rv(R):
    form2v = {f: v for v, fs in RV_FORMS.items() for f in fs}
    c = Counter()
    for line in open(HERE / "raw/gretil/rv.txt", encoding="utf-8", errors="ignore"):
        if "RV_" not in line and "|" not in line: continue
        line = re.sub(r"RV_\S+", " ", line)
        for w in re.findall(r"[^\s|'.,;:]+", line):
            w = w.strip("'")
            if w in form2v:
                c[form2v[w]] += 1; continue
            if w.startswith(RV_PREFIX_EXCL): continue
            for v, ps in RV_PREFIX.items():
                if any(w.startswith(p) and len(w) > len(p) + 2 for p in ps) and not w.startswith("dvādaśa" if v == 2 else "\0"):
                    if v == 10 and w.startswith("daśa") and w[4:5] in ("s",):  # daśasyati verb
                        break
                    c[v] += 1; break
    R["G_rigveda"] = dict(cls="G", counts=dict(c), n=sum(c.values()))


def main():
    R = {}
    build_linb(R); print("linb done")
    build_edh(R); print("edh done")
    build_names(R); print("names done")
    build_rv(R); print("rv done")
    build_cdli(R); print("cdli done")
    for k, d in R.items():
        d["counts"] = {int(a): int(b) for a, b in sorted(d["counts"].items()) if a is not None}
        lo = {v: d["counts"].get(v, 0) for v in range(1, 14)}
        print(f"{k:28s} n={d['n']:8d}  1-13: {lo}  >=13: {sum(n for v, n in d['counts'].items() if v >= 13)}")
    json.dump(R, open(OUT / "refs.json", "w"), indent=1)


if __name__ == "__main__":
    main()
