"""Part B reference systems: real short-label genres (non-name), codes, and the naming_sim name lists.

Every system -> sorted list of DISTINCT units (tuples), numeral tokens removed, units of 1..LMAX elements
(LMAX = 8 = longest Indus core + 1). Raw inputs are read as text/JSON only (untrusted data).

Writing, non-name label genres (GENRES):
  ur3_legend_w    Ur III seal legends, word tokens (codelib ur3_legends; CDLI @seal)          name+title+patronym
  ur3_title_w     same legends with personal-name words removed (title / office / divine-owner skeleton)
  ur3_legend_s    Ur III seal legends, cuneiform SIGN tokens (short_labels cun_seal_ur3)
  ob_legend_s     Old Babylonian / Old Assyrian seal legends, sign tokens (cun_seal_ob)
  egy_phrase_l    Earlier Egyptian verbless phrases (titles, names, offering captions), LEMMA tokens (TLA v18)
  egy_title_l     same, phrases with no proper noun (title / epithet strings)
  heraldry_w      Rietstap blazons, content words (codelib heraldry)                              emblem + tincture
  linb_entry_w    Linear B tablet lines, sign-groups + ideograms (codelib linear_b)              commodity entries
  pe_entry_s      Proto-Elamite entry lines, signs (codelib proto_elamite)                       account headings
  pc_entry_s      Proto-cuneiform entry lines, signs (short_labels proto_cun)                    logographic entries
  cun_tag_s       cuneiform tags / bullae / dockets, signs (short_labels cun_tag)                 commodity labels
  lat_label_w     Latin stamps, owner/maker marks, labels (EDH, diplomatic words)                 stamps
  lina_label_s    Linear A nodules / roundels / sealings / vessels (short_labels lina_label)     labels (small)
Codes (CODES): khipu, chess_eco, chords, emoji, metar.
Names (NAMES): naming_sim lists (C.NAME_LISTS), whole names.
Not obtained: Chinese clan emblems (no machine-readable corpus), merchants'/masons' marks (none machine-readable),
  Pictish symbol pairs (database not public), Hawaii cattle brands (images only, no sequences).
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

LMAX = 8
CL = C.ROOT / "sources/paragorth_Indus-/data/codelib"
SL = C.ROOT / "experiments/short_labels/data"
HER_NUM = {"un", "une", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze",
           "treize", "quatorze", "quinze", "seize"}


def is_num(x):
    return (x.startswith("N:") or x in ("NUM", "num") or x in HER_NUM
            or bool(re.fullmatch(r"[IVXLCM]{2,}", x)) or bool(re.fullmatch(r"N\d\d.*", x)))


def _clean(units):
    out = set()
    for u in units:
        u = tuple(x for x in u if x and not is_num(x))
        if 1 <= len(u) <= LMAX:
            out.add(u)
    return sorted(out)


def _jl(path):
    return [json.loads(l)["seq"] for l in open(path, encoding="utf-8")]


def ur3_words():
    return [[w.strip("_") for w in s] for s in _jl(CL / "ur3_legends.jsonl")]


def ur3_titles():
    import corpora as TY
    out = []
    for s in ur3_words():
        out.append([w for w in s if w in TY.UR_TITLES or w.startswith("{d}")])
    return out


def egy(no_propn=False):
    out = []
    for l in open(C.ROOT / "experiments/short_labels/raw/tla/train.jsonl", encoding="utf-8"):
        d = json.loads(l)
        try:
            if int(d.get("dateNotAfter") or 0) > -1550:
                continue
        except ValueError:
            continue
        pos = d["UPOS"].split()
        if any(p in ("VERB", "AUX") for p in pos):
            continue
        if no_propn and "PROPN" in pos:
            continue
        lem = [x.split("|")[0] for x in d["lemmatization"].split()]
        lem = [("NUMERAL" if p == "NUM" else x) for x, p in zip(lem, pos)] if len(lem) == len(pos) else lem
        out.append([x for x in lem if x != "NUMERAL"])
    return out


GENRES = {
    "ur3_legend_w": lambda: ur3_words(),
    "ur3_title_w": ur3_titles,
    "ur3_legend_s": lambda: _jl(SL / "cun_seal_ur3.jsonl"),
    "ob_legend_s": lambda: _jl(SL / "cun_seal_ob.jsonl"),
    "egy_phrase_l": lambda: egy(False),
    "egy_title_l": lambda: egy(True),
    "heraldry_w": lambda: _jl(CL / "heraldry.jsonl"),
    "linb_entry_w": lambda: _jl(CL / "linear_b.jsonl"),
    "pe_entry_s": lambda: _jl(CL / "proto_elamite.jsonl"),
    "pc_entry_s": lambda: _jl(SL / "proto_cun.jsonl"),
    "cun_tag_s": lambda: _jl(SL / "cun_tag.jsonl"),
    "lat_label_w": lambda: _jl(SL / "lat_label.jsonl"),
    "lina_label_s": lambda: _jl(SL / "lina_label.jsonl"),
}
CODES = {
    "khipu": lambda: _jl(CL / "khipu.jsonl"),
    "chess_eco": lambda: _jl(SL / "chess_eco.jsonl"),
    "chords": lambda: _jl(SL / "chords.jsonl"),
    "emoji": lambda: _jl(SL / "emoji.jsonl"),
    "metar": lambda: _jl(SL / "metar.jsonl"),
}
GROUP = {**{g: "genre" for g in GENRES}, **{g: "code" for g in CODES}, **{g: "name" for g in C.NAME_LISTS}}
_cache = {}


def load(nm):
    if nm not in _cache:
        if nm in GENRES:
            _cache[nm] = _clean(GENRES[nm]())
        elif nm in CODES:
            _cache[nm] = _clean(CODES[nm]())
        else:
            _cache[nm] = _clean(C.N.load(nm)[0])
    return _cache[nm]


if __name__ == "__main__":
    from collections import Counter
    for nm in list(GENRES) + list(CODES) + C.NAME_LISTS:
        t = load(nm)
        V = Counter(e for x in t for e in x)
        L = Counter(min(len(x), 4) for x in t)
        print(f"{nm:14s} {GROUP[nm]:5s} units {len(t):6d} V {len(V):6d} len {dict(sorted(L.items()))} e.g. {t[len(t)//3]}")
