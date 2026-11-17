"""Build the onomasticon for the M1 crib attack (board task #2).

Sources (all parsed as text/JSON data, nothing executed):
  raw/epsd2-names.zip          ORACC epsd2/names gloss-qpn (CC0): ED IIIb, Old Akkadian, Lagash II, Ur III, OB names
  raw/epsd2-admin-oldbab.zip   ORACC epsd2/admin/oldbab gloss-qpn (CC0): Old Babylonian admin names (4,208 PN)
  raw/rimanum.zip              ORACC rimanum gloss-qpn (CC0): OB Akkadian archive with many foreign (Amorite) names
  experiments/identifiers/data/ur3_occ.jsonl   Ur III seal legends from the CDLI dump (read only)
  experiments/short_labels/raw/cdli/*          CDLI catalogue + ATF dump (read only): Gulf co-text names
  experiments/meluhha/catalogue.csv            named Meluhhan / Magan / Dilmun persons (read only)
  gulf_manual.csv                              hand-entered Gulf legends, deities, rulers with literature refs

Writes names.csv, deities_formulas.csv, stats.json.
usage: .venv/bin/python -I experiments/onomasticon/build_names.py
"""
import csv
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw"
CDLI = ROOT / "experiments/short_labels/raw/cdli"
csv.field_size_limit(10**9)

# ---------------------------------------------------------------- phonetics
SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
ACC = {"á": "a", "à": "a", "é": "e", "è": "e", "í": "i", "ì": "i", "ú": "u", "ù": "u",
       "ā": "a", "ē": "e", "ī": "i", "ū": "u", "â": "a", "ê": "e", "î": "i", "û": "u"}
LOGO = {  # common logograms inside personal names -> Akkadian/Sumerian phonetic value
    "dingir": "il", "an": "an", "utu": "šamaš", "amar.utu": "marduk", "en.zu": "suen", "iškur": "adad",
    "arad": "warad", "arad2": "warad", "dumu": "mar", "ah": "ah", "šeš": "ah", "lugal": "lugal",
    "inanna": "ištar", "mùš": "ištar", "nin.šubur": "ilabrat", "nanna": "nanna", "suen": "suen",
    "nin": "nin", "en": "en", "ur": "ur", "lu2": "lu", "geme2": "geme", "mu": "mu", "kalam": "kalam",
}
VOW = set("aeiu")
DET = re.compile(r"\{[^}]*\}")


def cdli2uni(s):
    """CDLI ASCII ATF -> ORACC-style unicode."""
    s = s.replace("sz", "š").replace("SZ", "Š").replace("s,", "ṣ").replace("t,", "ṭ").replace("j", "ŋ")
    return s


def sign_values(written):
    """'{d}su-mu-el₃' -> ['su','mu','el']; returns None if unreadable."""
    w = written.translate(SUB)
    w = DET.sub("-", w)
    w = re.sub(r"[\[\]⸢⸣<>#!?*˹˺()|]", "", w)
    out = []
    for p in re.split(r"[-.+ ]", w):
        if not p:
            continue
        if p.lower() in ("x", "...") or "x" == p.lower().strip("0123456789"):
            return None
        low = p.lower()
        low = "".join(ACC.get(ch, ch) for ch in low)
        low = re.sub(r"[0-9]+$", "", low)
        low = low.replace("ʾ", "").replace("'", "").replace("ĝ", "ŋ").replace("ḫ", "h").replace("ŋ", "g")
        if p.isupper() or low in LOGO and p[0].isupper():
            low = LOGO.get(low, None)
            if low is None:
                return None
        if not low or not re.fullmatch(r"[a-zšṣṭ]+", low):
            return None
        out.append(low)
    return out or None


def sign_syllables(vals, akk=False):
    """Syllables that respect sign boundaries: each sign value is syllabified on its own, then a
    V-final syllable plus a following VC sign with the same vowel is merged (sa-ar -> sar).
    'ia' -> 'ya'; in Akkadian/Amorite names dingir/an -> il."""
    out = []
    for v in vals:
        if akk and v == "dingir":
            v = "il"
        if v.startswith("ia"):
            v = "ya" + v[2:]
        parts = syllabify(v)
        for q in parts:
            if out and out[-1][-1] in VOW and len(q) == 2 and q[0] == out[-1][-1] and q[1] not in VOW:
                out[-1] = out[-1] + q[1]
            else:
                out.append(q)
    return out


def phon_string(vals):
    """Concatenate sign values, merging CV-VC overlaps (sa-ar -> sar, ia-ah -> iah)."""
    s = ""
    for v in vals:
        if s and s[-1] in VOW and v[0] in VOW and (v[0] == s[-1] or len(v) > 1 and v[1] not in VOW):
            if v[0] == s[-1]:
                v = v[1:]
        s += v
    return s


def syllabify(s):
    """Greedy CV(C) syllabification; 'i'/'u' between vowels stay vowels (hiatus)."""
    segs = []
    i = 0
    while i < len(s):
        segs.append(s[i]); i += 1
    syl, cur = [], ""
    n = len(segs)
    for k, ch in enumerate(segs):
        isv = ch in VOW
        if isv:
            if any(c in VOW for c in cur):
                syl.append(cur); cur = ch
            else:
                cur += ch
        else:
            nxt = segs[k + 1] if k + 1 < n else None
            if not any(c in VOW for c in cur):
                cur += ch  # onset (allow clusters only word-initially, rare)
            elif nxt is None or nxt not in VOW:
                cur += ch  # coda
            else:
                syl.append(cur); cur = ch
    if cur:
        if syl and not any(c in VOW for c in cur):
            syl[-1] += cur
        else:
            syl.append(cur)
    return syl


# ---------------------------------------------------------------- language heuristic
AMORITE = [r"^(ia|ya|i-a)-", r"^su-mu-", r"^ha-am-mu", r"^zi-im-ri", r"^am-mi-", r"-el3?$", r"-e-el$",
           r"-ra-pi", r"-ha-ad-du", r"-a-du$", r"^ab-di-", r"-li-im$", r"^ia-ah", r"^ia-as", r"-da-gan",
           r"^bu-nu-", r"^mu-ut-", r"^ha-ab-du-", r"-e-pu-uh", r"^ia-ri-im", r"-ha-nu-un"]
AKK = [r"(^|-)i3?-li2?(-|$)", r"(^|-)i-lum", r"dingir", r"(^|-)a-hu", r"(^|-)a-hi", r"(^|-)a-bi", r"(^|-)a-bu",
       r"(^|-)szu-", r"^š[u]-", r"i-din", r"id-di-na", r"ib-ni", r"ip-qu", r"pu-zur", r"szar-ru", r"šar-ru",
       r"be-li", r"be-el", r"e-ri-ib", r"e-ri-isz", r"e-riš", r"ta-ab", r"da-mi-iq", r"na-ra-am", r"la-ma-sa",
       r"-tum$", r"-tum-", r"(^|-)ma-ar-", r"ummi|um-mi", r"nu-ur-", r"mu-sza|mu-ša", r"-szu$|-šu$", r"-ia$",
       r"ri-isz|ri-iš", r"ku-bu-ru", r"ki-ma", r"ma-li-ik", r"a-wi-il", r"-ga-mil", r"utu", r"amar\.utu|marduk",
       r"en\.zu", r"iškur|iszkur", r"-um$", r"-im$"]
SUX = [r"^ur-", r"^lu2-", r"^lú-", r"^lugal-", r"^nin-", r"^geme2-", r"^ab-ba-", r"-ki-ag2", r"-ki-aŋ2",
       r"-zi$", r"-mu$", r"-ŋu10$", r"-gu10$", r"-ka$", r"-ke4$", r"^e2-", r"^en-", r"^szesz-", r"^šeš-",
       r"-kam$", r"-ta$", r"-sa6-ga", r"-du10$", r"-ki-du10", r"-he2-gal2", r"-i3-sa6", r"-gal-zu", r"-ba-ti",
       r"-mu-ba-al", r"^a-tu$", r"^ba-ba", r"^igi-", r"-ma-an-sum", r"-al-sa6", r"-uru-na", r"-ga$"]


def classify(written):
    w = written.lower().translate(SUB)
    w = DET.sub("", w)
    a = sum(bool(re.search(p, w)) for p in AMORITE)
    k = sum(bool(re.search(p, w)) for p in AKK)
    s = sum(bool(re.search(p, w)) for p in SUX)
    # mimation/-tum only counts as Akkadian if nothing Sumerian matched
    strong = re.search(r"^(ia|ya)-|^su-mu-|^ha-am-mu|^zi-im-ri|^am-mi-|^ab-di-|^mu-ut-|^bu-nu-", w)
    if strong or (a and not k):
        return "Amorite"
    if s and not k:
        return "Sumerian"
    if k and not s:
        return "Akkadian"
    if s and k:
        return "Sumerian" if s > k else ("Akkadian" if k > s else "unknown")
    return "unknown"


# ---------------------------------------------------------------- sources
rows = []


CANON = {"non-Sumerian non-Akkadian": "Meluhhan?", "non-Sumerian non-Akkadian?": "Meluhhan?",
         "Akkadian-looking": "Akkadian", "Amorite/Akkadian": "Amorite", "Sumerian?": "Sumerian",
         "Sumerian rendering": "Sumerian", "Lallname": "unknown", "unclear": "unknown", "ethnonym": "unknown",
         "Akkadian?": "Akkadian"}


def add(name, written, language, src, text_id, date, role, lang_basis, gulf=""):
    if re.match(r"^[0-9]", written) or written in ("ugula", "dumu") or re.fullmatch(r"\{d\}[^-]+", written):
        return
    language = CANON.get(language, language)
    vals = sign_values(written)
    syl = sign_syllables(vals, akk=language in ("Akkadian", "Amorite")) if vals else None
    rows.append(dict(name=name, written=written,
                     syllables=".".join(syl) if syl else "",
                     n_syll=len(syl) if syl else "",
                     language=language, lang_basis=lang_basis, source=src, source_text_id=text_id,
                     date=date, role=role, gulf_link=gulf))


def oracc(zipname, prefix):
    z = zipfile.ZipFile(RAW / zipname)
    g = json.loads(z.read(prefix + "gloss-qpn.json"))
    return g


GULF_GN = {"Dilmun": "Dilmun", "Magan": "Magan", "Meluhha": "Meluhha"}


def from_oracc(zipname, prefix, project):
    g = oracc(zipname, prefix)
    inst = g["instances"]
    gn_texts = defaultdict(set)
    for e in g["entries"]:
        if e["pos"] in ("GN", "PN") and e["cf"] in GULF_GN:
            for s in e.get("senses", []) + [e]:
                for ref in inst.get(e["xis"], []):
                    gn_texts[ref.split(":")[1].split(".")[0]].add(e["cf"])
    n = 0
    for e in g["entries"]:
        if e["pos"] != "PN":
            continue
        forms = e.get("forms", [])
        if not forms:
            continue
        written = max(forms, key=lambda f: int(f.get("icount", 0)))["n"]
        texts = sorted({r.split(":")[1].split(".")[0] for r in inst.get(e["xis"], [])})
        per = ";".join(p["p"] for p in e.get("periods", []))
        gl = sorted({gn for t in texts for gn in gn_texts.get(t, ())})
        lang = classify(written)
        basis = "heuristic"
        if project == "rimanum" and lang == "unknown":
            lang, basis = "Akkadian?", "corpus=akk-x-oldbab, no marker"
        add(e["cf"], written, lang, f"ORACC {project}", ";".join(texts[:5]) + (f";+{len(texts)-5}" if len(texts) > 5 else ""),
            per, "co-text with " + "/".join(gl) if gl else "general stock", basis, "/".join(gl))
        n += 1
    return n, {k: sorted(v) for k, v in gn_texts.items()}


counts = {}
counts["epsd2_names"], gn1 = from_oracc("epsd2-names.zip", "epsd2/names/", "epsd2/names")
counts["oldbab"], gn2 = from_oracc("epsd2-admin-oldbab.zip", "epsd2/admin/oldbab/", "epsd2/admin/oldbab")
counts["rimanum"], gn3 = from_oracc("rimanum.zip", "rimanum/", "rimanum")

# Ur III seal-legend owner names (first legend line), one row per distinct name, count of seals
ur = Counter(); urtext = {}
for l in open(ROOT / "experiments/identifiers/data/ur3_occ.jsonl"):
    d = json.loads(l)
    if not d["legend"] or not d["legend"][0]:
        continue
    w = d["legend"][0][0]
    if re.fullmatch(r"\{d\}[^-]+", w) or "{ki}" in w or w in ("lugal", "dub-sar", "ensi2"):
        continue
    w = cdli2uni(w)
    ur[w] += 1; urtext.setdefault(w, d["pid"])
for w, c in ur.items():
    add(w, w, classify(w), "CDLI Ur III seal legends (identifiers/ur3_occ)", urtext[w], "Ur III",
        f"seal owner (x{c})", "heuristic")
counts["ur3_seals"] = len(ur)

# CDLI ATF: names in Ur III / Old Akkadian / Lagash II / (Early) OB texts that mention Dilmun, Magan or Meluhha
cat = {}
with open(CDLI / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f):
        pid = (r.get("id_text") or "").strip()
        if pid.isdigit():
            cat["P" + pid.zfill(6)] = ((r.get("period") or "").split("(")[0].strip(),
                                        (r.get("provenience") or "").split("(")[0].strip(),
                                        (r.get("designation") or ""))
KEEP = ("Ur III", "Old Akkadian", "Lagash II", "Early Old Babylonian", "Old Babylonian", "ED IIIb")
GULF_RE = {"Dilmun": re.compile(r"(dilmun|tilmun|ni-tuk)"), "Magan": re.compile(r"ma2?-gan"),
           "Meluhha": re.compile(r"me-luh-ha")}
known_pn = set(ur)  # validation set: a co-text token counts as a PN only if it is a known name elsewhere
for r in rows:
    known_pn.add(r["written"])
CTX = re.compile(r"(?:^|\s)(?:ki|giri3|kiszib3|dumu|szu-i3|igi|mu-kux\(du\)|ARAD2?|arad2?)\s+(\S+)")
atf_hits = []
cur, buf = None, []


def flush(pid, lines):
    if pid not in cat or not cat[pid][0].startswith(KEEP) or "Literary" in cat[pid][2]:
        return
    txt = "\n".join(lines)
    gl = [g for g, rx in GULF_RE.items() if rx.search(txt)]
    if not gl:
        return
    toks = set()
    for line in lines:
        if not re.match(r"^\d", line):
            continue
        body = line.split(".", 1)[1] if "." in line else line
        for m in CTX.finditer(body):
            toks.add(m.group(1))
        # 'X szu ba-ti' : receiver
        m = re.search(r"(\S+)\s+szu\s+ba-(?:an-)?ti", body)
        if m:
            toks.add(m.group(1))
    for t in toks:
        t2 = re.sub(r"-(ta|sze3|ra|ke4|e)$", "", re.sub(r"[#!?\[\]]", "", t))
        u = cdli2uni(t2)
        if u in known_pn and not GULF_RE["Dilmun"].search(t2) and not re.search(r"ma2?-gan|me-luh", t2):
            atf_hits.append((u, pid, cat[pid], "/".join(gl)))


with open(CDLI / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.startswith("&P"):
            if cur:
                flush(cur, buf)
            cur, buf = line[1:8], []
        else:
            buf.append(line.rstrip("\n"))
    if cur:
        flush(cur, buf)
seen = set()
for u, pid, (per, prov, des), gl in atf_hits:
    if (u, pid) in seen:
        continue
    seen.add((u, pid))
    add(u, u, classify(u), "CDLI ATF co-text (context pattern, validated against known names)", pid, per,
        f"named in a {prov or 'unprovenanced'} text mentioning {gl} ({des})", "heuristic", gl)
counts["cdli_gulf_cotext"] = len(seen)

# Meluhhan / Magan / Dilmun persons from the meluhha catalogue (explicit links)
for r in csv.DictReader(open(ROOT / "experiments/meluhha/catalogue.csv")):
    if r["category"] != "person":
        continue
    w = r["transliteration"].split(";")[0].split(" ")[0].strip()
    lang = r["name_language"].split(" (")[0]
    gl = "Meluhha" if "me-luh" in r["transliteration"] + r["explicitly_meluhhan"] or "Meluh" in r["notes"] else ""
    for k in ("Dilmun", "Magan"):
        if k in r["item"]:
            gl = k
    if "Gulf" in r["explicitly_meluhhan"] or "sea" in r["explicitly_meluhhan"]:
        gl = gl or "Gulf"
    add(r["item"], w, lang, "experiments/meluhha/catalogue.csv", r["text_id"], r["period"] + " " + r["date"],
        r["explicitly_meluhhan"] + "; " + r["gloss"], "catalogue (literature)", gl)

# hand-entered Gulf rows
for r in csv.DictReader(open(HERE / "gulf_manual.csv")):
    if r["kind"] == "person":
        add(r["name"], r["written"], r["language"], r["source"], r["text_id"], r["date"], r["role"],
            "literature", r["gulf_link"])

# ---------------------------------------------------------------- write names.csv
cols = ["name", "written", "syllables", "n_syll", "language", "lang_basis", "source", "source_text_id",
        "date", "role", "gulf_link"]
with open(HERE / "names.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# deities and legend formulas
with open(HERE / "deities_formulas.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["kind", "name", "written", "syllables", "language", "role", "source", "text_id", "date", "verified"])
    for r in csv.DictReader(open(HERE / "gulf_manual.csv")):
        if r["kind"] == "person":
            continue
        vals = sign_values(r["written"]) if r["written"] else None
        syl = ".".join(sign_syllables(vals)) if vals else ""
        w.writerow([r["kind"], r["name"], r["written"], syl, r["language"], r["role"], r["source"], r["text_id"],
                    r["date"], r["verified"]])

# ---------------------------------------------------------------- statistics
def stats(sub):
    # distinct by syllable string
    d = {}
    for r in sub:
        if r["syllables"]:
            d.setdefault(r["syllables"], r)
    syls = [s.split(".") for s in d]
    if not syls:
        return {"n_distinct": 0}
    L = Counter(len(s) for s in syls)
    fr = Counter(x for s in syls for x in s)
    tot = sum(fr.values())
    rep_any = sum(len(set(s)) < len(s) for s in syls)
    rep_adj = sum(any(a == b for a, b in zip(s, s[1:])) for s in syls)
    rep_init = sum(len(s) > 1 and s[0] == s[1] for s in syls)
    shape = Counter(re.sub(r"[aeiu]", "V", re.sub(r"[^aeiu]", "C", x)) for s in syls for x in s)
    # expected repeat rate under independent syllables with these frequencies (analytic, per name)
    p = {k: v / tot for k, v in fr.items()}
    import itertools
    def p_no_rep(n):
        # P(all distinct) for n i.i.d. draws, approximated by Monte Carlo
        return None
    import random
    rnd = random.Random(7); keys = list(p); wts = [p[k] for k in keys]
    # permutation null: shuffle all syllable tokens across names of this group, keeping name lengths
    pool = [x for s in syls for x in s]; sim = 0; m = 0
    for _ in range(50):
        rnd.shuffle(pool); i = 0
        for s in syls:
            dr = pool[i:i + len(s)]; i += len(s); sim += len(set(dr)) < len(dr); m += 1
    return {"n_distinct": len(syls), "n_rows": len(sub),
            "len_dist": {k: L[k] for k in sorted(L)}, "mean_len": round(sum(len(s) for s in syls) / len(syls), 3),
            "n_syllable_types": len(fr),
            "top_syllables": [[k, v, round(v / tot, 4)] for k, v in fr.most_common(40)],
            "syllable_shapes": dict(shape.most_common()),
            "frac_any_repeated_syllable": round(rep_any / len(syls), 4),
            "frac_adjacent_repeat": round(rep_adj / len(syls), 4),
            "frac_initial_doubling": round(rep_init / len(syls), 4),
            "frac_any_repeat_perm_null": round(sim / m, 4)}


by = defaultdict(list)
for r in rows:
    by[r["language"]].append(r)
    if r["gulf_link"]:
        by["GULF_LINKED(all languages)"].append(r)
out = {"source_counts": counts, "rows_total": len(rows),
       "rows_with_syllables": sum(bool(r["syllables"]) for r in rows),
       "by_language": {k: stats(v) for k, v in sorted(by.items())},
       "by_source": {k: stats([r for r in rows if r["source"] == k]) for k in sorted({r["source"] for r in rows})}}
(HERE / "stats.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({k: out[k] for k in ("source_counts", "rows_total", "rows_with_syllables")}, indent=1))
for k, v in out["by_language"].items():
    print(k, {x: v.get(x) for x in ("n_distinct", "mean_len", "len_dist", "frac_any_repeated_syllable",
                                     "frac_any_repeat_perm_null", "frac_initial_doubling")})
