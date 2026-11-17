"""Real onomastica segmented into ELEMENTS (word-level name themes, not syllables). Unit = distinct name type.

Every loader returns (types, cls): types = list of distinct tuples of elements in reading order; cls = set of
elements forming a lexical 'animal' class (for the class self-compounding statistic; None if not definable).
Raw downloads (raw/) are untrusted and are read only as JSON/text; run with `python -I`.

Systems
  old_english, old_norse, old_high_german, greek : Wiktionary given-name entries; segmentation from the
      etymology templates {{af|..}} {{affix|..}} {{surf|..}} {{compound|..}} or 'X + Y' links. No compound
      template -> one-element name (the name itself, e.g. Offa). Germanic/Greek dithematic systems.
  sanskrit   : Monier-Williams (core_semantics/data/mw) entries glossed 'N. of a man/king/...'; members = key2
               compound members (separator —); 1, 2 and 3-member names.
  ur3        : Ur III seal-legend personal names (codelib), split at hyphens with {d}DN kept whole
               (core_semantics.cs_data.ur3_elements); logo-syllabic, so some 'elements' are syllables.
  chinese_given : two-character modern given names + one-character given names (typology/data).
  chinese_full  : surname + given (clan + name).
  tamil      : Wiktionary Tamil given names (modern, Sanskrit/Tamil compounds), etymology segmentation.
  egyptian   : Wiktionary Egyptian given names, etymology segmentation (theophoric).
  plains     : Lakota and other Plains nations' personal names in English translation (Wikipedia category
               titles), content words only; descriptive names (Sitting Bull, Spotted Elk).
  sangam     : Old Tamil Sangam poet names (Wikipedia list), word-level (place / father / epithet / name).
  mixtec     : RULE-BASED (no open list): calendar name = number (1-13) + day sign (20), optional personal
               name of 1-2 elements drawn from a Zipf stock. Flagged synthetic.
"""
import json, re, sys, unicodedata
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw"
sys.path.insert(0, str(ROOT / "experiments" / "core_semantics"))
sys.path.insert(0, str(ROOT / "experiments" / "typology"))


def norm(s):
    s = re.sub(r"<[^>]*>", "", s)
    s = s.replace("þ", "th").replace("ð", "th").replace("Þ", "th").replace("Ð", "th").replace("ǫ", "o")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower().strip().strip("*-").strip()
    return s


def _section(text, lang):
    i = text.find(f"=={lang}==")
    if i < 0:
        return None
    s = text[i + len(lang) + 4:]
    j = re.search(r"\n==[^=]", s)
    return s[:j.start()] if j else s


def _tpl_args(body):
    parts = [p for p in body.split("|")]
    pos = [p for p in parts[1:] if "=" not in p.split("<")[0]]
    return pos


def wiktionary_segment(text, lang, code):
    """-> tuple of elements, or None if the language section is missing."""
    s = _section(text, lang)
    if s is None:
        return None
    m = re.search(r"===\s*Etymology[^=]*===(.*?)(\n===|$)", s, re.S)
    ety = m.group(1) if m else ""
    best = None
    for tm in re.finditer(r"\{\{(af|affix|surf|compound|com|blend)\|([^{}]*)\}\}", ety):
        args = _tpl_args(tm.group(1) + "|" + tm.group(2))
        if not args:
            continue
        lc, el = args[0], [a for a in args[1:] if a.strip()]
        el = [norm(e) for e in el if norm(e)]
        el = [e for e in el if not e.startswith("-") and len(e) > 0]
        if len(el) < 2:
            continue
        score = (lc == code) * 2 + (tm.group(1) == "surf")
        if best is None or score > best[0]:
            best = (score, tuple(el))
    if best:
        return best[1]
    # 'From {{m|code|a}} + {{m|code|b}}'
    mm = re.findall(r"\{\{(?:m|l|mention)\|" + re.escape(code) + r"\|([^|{}]+)[^{}]*\}\}\s*\+\s*", ety)
    if mm:
        last = re.search(r"\+\s*\{\{(?:m|l|mention)\|" + re.escape(code) + r"\|([^|{}]+)", ety)
        el = [norm(x) for x in mm] + ([norm(last.group(1))] if last else [])
        if len(el) >= 2:
            return tuple(el)
    return None


def _stems(e):
    out = {e}
    if len(e) > 3 and e[-1] in "raeiou":
        out.add(e[:-1])
    if len(e) > 4 and e[-2:] in ("ir", "ur", "ar", "er", "us", "os", "es", "as"):
        out.add(e[:-2])
    return {x for x in out if len(x) >= 2}


def theme_split(word, first, second):
    """Split an unsegmented name into a known first theme + a known second theme (both attested in this
    language's template-segmented names). Longest second theme wins; None if no split."""
    fst = set()
    for e in first | second:
        fst |= _stems(e)
    best = None
    for i in range(2, len(word) - 1):
        a, b = word[:i], word[i:]
        if b in second and a in fst and (best is None or len(b) > len(best[1])):
            best = (a, b)
    return best


def _wkt(cats, lang, code, title_ok=None, split_unsegmented=True):
    """Template-segmented names; names without a template are split into attested themes when possible
    (deuterotheme matching), else kept as one-element names."""
    types, raw1 = set(), []
    for c in cats:
        f = RAW / "wiktionary" / f"{c}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        for title, text in d.items():
            if " " in title or title.startswith(("-", "Reconstruction")):
                continue
            seg = wiktionary_segment(text, lang, code)
            if seg is None:
                if _section(text, lang) is None:
                    continue
                raw1.append(norm(title))
                continue
            types.add(seg)
    first = {t[0] for t in types if len(t) >= 2}
    second = {t[-1] for t in types if len(t) >= 2 and len(t[-1]) >= 2}
    for w in raw1:
        sp = theme_split(w, first, second) if split_unsegmented else None
        types.add(sp if sp else (w,))
    return sorted(types)


ANIMAL = {
    "old_english": {"wulf", "eofor", "earn", "hraefn", "hors", "hengest", "swan", "beorn", "ulf", "wulfa", "hund",
                    "fugol", "fox", "hroc", "cran", "bera", "eafor"},
    "old_norse": {"ulfr", "ulf", "bjorn", "orn", "ari", "hrafn", "ormr", "hjortr", "bersi", "ulfi", "biorn", "hestr",
                  "uxi", "geir_x", "orm", "bjarn", "arn"},
    "old_high_german": {"wolf", "olf", "bero", "bern", "arn", "aro", "hraban", "hram", "ram", "ebur", "eber", "swan",
                        "hros", "hirz", "wulf", "bera", "ber", "ar", "wolfa"},
    "greek": {"ιππος", "ιππο", "ιππ", "λεων", "λεοντ", "λυκος", "λυκο", "λυκ", "ταυρος", "κοραξ", "αετος", "κυων",
              "μοσχος", "λαγως", "δρακων", "ελαφος", "ορνις", "βους", "κριος", "πωλος", "hippos", "leon", "lykos", "tauros", "korax", "aetos", "kyon", "moschos", "lagos", "drakon", "elaphos",
              "ornis", "chelidon", "bous", "mys", "aix", "kriobolos", "krios", "pōlos", "polos", "hippo", "leont"},
    "sanskrit": {"siMha", "vyAGra", "nAga", "gaja", "haMsa", "mfga", "aSva", "vfzaBa", "garuqa", "mIna", "matsya",
                 "kuYjara", "Sarabha", "hasti", "hastin", "vfza", "rzaBa", "kapi", "Sardula", "SArdUla", "mayUra",
                 "Suka", "kokila", "kUrma", "sarpa", "ahi", "uraga", "vAnara", "ulUka", "Syena", "go", "gava"},
    "chinese_given": set("龙虎凤鹏鹤鹰麟燕鸿马鹿雁鹃莺蝶狮豹熊鱼鲲鸾雀鸥骏驹牛羊犬蛟凰"),
    "chinese_full": set("龙虎凤鹏鹤鹰麟燕鸿马鹿雁鹃莺蝶狮豹熊鱼鲲鸾雀鸥骏驹牛羊犬蛟凰"),
    "plains": {"bull", "bear", "horse", "horses", "eagle", "elk", "wolf", "hawk", "crow", "buffalo", "dog", "fox",
               "owl", "deer", "otter", "badger", "rabbit", "turtle", "snake", "raven", "crane", "bird", "coyote", "cow",
               "swallow", "antelope", "weasel", "beaver", "calf", "mouse", "magpie", "eagles", "bears", "dogs", "wolves",
               "buffaloes", "bulls", "elks", "hawks", "crows", "lizard", "bird", "birds", "pony", "mule", "goose",
               "duck", "skunk", "porcupine", "mink", "wren", "lark", "hen", "cougar", "panther", "lion", "colt",
               "mare", "stallion"},
    "egyptian": {"bik", "msh", "nhs", "hor_x"},
}


def old_english():
    return _wkt(["Old_English_male_given_names", "Old_English_female_given_names"], "Old English", "ang"), ANIMAL["old_english"]


def old_norse():
    return _wkt(["Old_Norse_male_given_names", "Old_Norse_female_given_names"], "Old Norse", "non"), ANIMAL["old_norse"]


def old_high_german():
    return _wkt(["Old_High_German_male_given_names", "Old_High_German_female_given_names"], "Old High German", "goh"), ANIMAL["old_high_german"]


def greek():
    t = _wkt(["Ancient_Greek_male_given_names"], "Ancient Greek", "grc")
    return t, ANIMAL["greek"]


def tamil():
    return _wkt(["Tamil_male_given_names"], "Tamil", "ta"), None


def egyptian():
    return _wkt(["Egyptian_male_given_names", "Egyptian_female_given_names"], "Egyptian", "egy"), None


def germanic_pooled():
    a = set(old_english()[0]) | set(old_norse()[0]) | set(old_high_german()[0])
    return sorted(a), ANIMAL["old_english"] | ANIMAL["old_norse"] | ANIMAL["old_high_german"]


# ---------------------------------------------------------------- Sanskrit (Monier-Williams)
MW = ROOT / "experiments" / "core_semantics" / "data" / "mw" / "xml" / "mw.xml"
_PERS = re.compile(r"<ab>N\.</ab> of (a man|men|various men|a Brāhman|a king|a prince|a Ṛishi|a ṛishi|"
                   r"a teacher|a poet|an author|a Muni|a minister|a merchant|a son of|a pupil)")
_ENT = re.compile(r"<(H\d[A-Z]?)><h><key1>([^<]*)</key1><key2>(.*?)</key2>.*?<body>(.*?)</body>")


def sanskrit():
    types = set()
    for line in open(MW, encoding="utf-8"):
        m = _ENT.search(line)
        if not m or not _PERS.search(m.group(4)[:200]):
            continue
        k = re.sub(r"<[^>]+>", "", m.group(3)); k = re.sub(r"[/\^\\'~]", "", k)
        mem = [re.sub("[^A-Za-z]", "", p) for p in k.split("—") if re.sub("[^A-Za-z]", "", p)]
        if mem:
            types.add(tuple(mem))
    return sorted(types), ANIMAL["sanskrit"]


# ---------------------------------------------------------------- Ur III
def ur3():
    import cs_data as D, corpora as TY
    types = set()
    for l in open(D.UR):
        seq = [w.strip("_") for w in json.loads(l)["seq"]]
        for i, w in enumerate(seq):
            if not (i == 0 or seq[i - 1] in ("dumu", "dam", "dumu-munus")):
                continue
            if w in TY.UR_TITLES or "{ki}" in w:
                continue
            el = D.ur3_elements(w)
            if el:
                types.add(el)
    return sorted(types), None


# ---------------------------------------------------------------- Chinese
def chinese_given():
    import corpora as TY
    d = TY.chinese_names(given_only=True)
    return sorted(d), ANIMAL["chinese_given"]


def chinese_full():
    import corpora as TY
    d = TY.chinese_names(given_only=False)
    return sorted(d), ANIMAL["chinese_full"]


# ---------------------------------------------------------------- Plains nations (English translations)
STOP = {"of", "the", "his", "her", "in", "a", "an", "on", "at", "with", "and", "to", "who", "is", "their", "him",
        "by", "for", "from", "over", "among"}


def plains():
    f = RAW / "wikipedia" / "native_american_categories.json"
    if not f.exists():
        return [], ANIMAL["plains"]
    cats = json.loads(f.read_text())
    words = set()
    dic = Path("/usr/share/dict/words")
    lower = {w.strip() for w in dic.read_text().split() if w.strip().islower()} if dic.exists() else set()
    first = {w.strip().lower() for w in dic.read_text().split() if w.strip()[:1].isupper()} if dic.exists() else set()
    types = set()
    for c, titles in cats.items():
        for t in titles:
            t0 = re.sub(r"\s*\(.*?\)", "", t).strip()
            if t0.startswith(("List", "Category")) or "," in t0:
                continue
            w = [x.lower() for x in re.split(r"[\s\-]+", t0) if x]
            if not w or len(w) > 7:
                continue
            # descriptive names only: every word an ordinary lowercase English word, first word not a first name
            if not all(x in lower or x in STOP for x in w):
                continue
            if w[0] in first and w[0] not in lower:
                continue
            el = tuple(x for x in w if x not in STOP)
            if el:
                types.add(el)
    return sorted(types), ANIMAL["plains"]


# ---------------------------------------------------------------- Sangam poets
def sangam():
    f = RAW / "wikipedia" / "pages.json"
    if not f.exists():
        return [], None
    d = json.loads(f.read_text())
    txt = d.get("List of Sangam poets", "")
    types = set()
    for line in txt.split("\n"):
        # table rows: |N || Poet || Tamil || works || notes
        if not re.match(r"^\|\s*\d+\s*\|\|", line):
            continue
        cells = [c.strip() for c in line.split("||")]
        if len(cells) < 2:
            continue
        name = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", cells[1])
        name = re.sub(r"\(.*?\)|'''|''|<[^>]+>|\{\{.*?\}\}", "", name).strip()
        if not name or "anonymous" in name.lower() or re.search(r"\d", name):
            continue
        el = tuple(norm(x) for x in re.split(r"[\s\-]+", name) if norm(x))
        if el:
            types.add(el)
    return sorted(types), None


# ---------------------------------------------------------------- Mixtec (rule-based)
def mixtec(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    days = [f"day{i}" for i in range(20)]
    p = 1 / np.arange(1, 301); p /= p.sum()
    types = set()
    while len(types) < n:
        t = [f"num{rng.integers(1, 14)}", days[rng.integers(20)]]
        r = rng.random()
        if r < 0.6:
            t += [f"pn{rng.choice(300, p=p)}"]
        elif r < 0.8:
            t += [f"pn{rng.choice(300, p=p)}", f"pn{rng.choice(300, p=p)}"]
        types.add(tuple(t))
    return sorted(types), {f"day{i}" for i in (1, 2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15)}  # animal day signs


SYSTEMS = {"old_english": old_english, "old_norse": old_norse, "old_high_german": old_high_german,
           "germanic_pooled": germanic_pooled, "greek": greek, "sanskrit": sanskrit,
           "egyptian": egyptian, "ur3": ur3, "chinese_given": chinese_given, "chinese_full": chinese_full,
           "plains": plains, "sangam": sangam, "mixtec": mixtec}


def load(name):
    return SYSTEMS[name]()


if __name__ == "__main__":
    for nm, f in SYSTEMS.items():
        t, c = f()
        if not t:
            print(f"{nm:16s} EMPTY"); continue
        L = Counter(min(len(x), 4) for x in t)
        V = len({e for x in t for e in x})
        rng = np.random.default_rng(0)
        ex = [t[k] for k in rng.choice(len(t), min(6, len(t)), replace=False)]
        nc = sum(1 for x in t for e in x if c and e in c)
        print(f"{nm:16s} types {len(t):6d} elems {V:6d} len {dict(sorted(L.items()))} class-tok {nc}  e.g. {ex}")
