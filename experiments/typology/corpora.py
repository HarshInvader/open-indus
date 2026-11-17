"""Name-core corpora for the typology test (Q1).

Every builder returns a dict  core(tuple of signs) -> incidence (number of distinct texts/legends/lines
in which that core occurs; 1 when the source gives no frequencies).  Unit = distinct core types.

Indus cores: maximal runs of tokens whose functional-reading role is N (unknown noun) or F (fish-class
noun), not inside a TITLE-BLOCK / REGISTER / OPENER / CLOSER constituent, not crossing a line break, and
not touching a '#' break.  Openers, connectives, numerals, units, titles, closers, clitics are stripped.
Split by dev_heldout(version=2) on the distinct full-text sequence.
Run from repo root.  Data from sources/ are read as data only.
"""
import json, re, sys, unicodedata
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, distinct, dev_heldout  # noqa

FR = ROOT / "experiments" / "functional_reading"
CODELIB = ROOT / "sources" / "paragorth_Indus-" / "data" / "codelib"
DAMOS = ROOT / "sources" / "paragorth_Indus-" / "other-scripts" / "linear-a" / "data" / "damos_items.jsonl"
HERE = Path(__file__).resolve().parent

STRIP_CONST = {"TITLE-BLOCK", "REGISTER", "OPENER", "CLOSER", "CLOSER(jar)", "DOC-TYPE CLITIC", "CONNECTIVE",
               "NUMERAL", "COUNT+MEASURE", "TITLE"}
LEX = pd.read_csv(FR / "lexicon.csv")
LEX = LEX[LEX.kind == "sign"].set_index("item")
NONNAME_MEANING = ("opener-class word", "pre-jar title element", "post-closer element")


def _constituents(reading):
    """[(label, [signs])...] in order, '||' as a separator label."""
    out = []
    for part in re.split(r"(\|\|)", reading):
        if part == "||":
            out.append(("||", []))
            continue
        for lab, sg in re.findall(r"\[([^:\]]+):\s*([^\]]+)\]", part):
            out.append((lab.strip(), sg.strip().split("+")))
    return out


def indus_cores_by_text(strict=False, loose=False):
    """-> {tuple(full seq): [core tuples]} for each distinct M77 text side in readings.csv."""
    d = pd.read_csv(FR / "readings.csv")
    out = {}
    for _, r in d.iterrows():
        if not isinstance(r.parse_roles, str):
            continue
        signs = r.signs.split()
        key = tuple(signs)
        if key in out:
            continue
        # role per token (parse_roles excludes | and #)
        toks = [t for t in r.parse_roles.split() if "/" in t]
        roles = [t.split("/")[1] for t in toks]
        tsig = [t.split("/")[0] for t in toks]
        # constituent label per token
        labs = []
        for lab, sg in _constituents(r.reading):
            labs += [lab] * len(sg)
        if len(labs) != len(toks):
            labs = ["?"] * len(toks)
        cores, cur, left = [], [], "^"
        k = 0
        for s in signs + ["$"]:
            if s in ("|", "#", "$"):
                if cur and left != "#" and s != "#":
                    cores.append(tuple(cur))
                cur, left = [], s
                continue
            assert tsig[k] == s, (r.text_no, s, tsig[k])
            ok = roles[k] in ("N", "F") and labs[k] not in STRIP_CONST
            if loose:
                ok = roles[k] in ("N", "F", "S", "T", "U", "I")
            elif ok and s in LEX.index:
                prim = str(LEX.loc[s, "roles"]).split(";")[0].rsplit(" ", 1)[0]
                if prim not in ("NOUN", "FISH-CLASS NOUN"):
                    ok = False
                mc = str(LEX.loc[s, "meaning_category"])
                if mc.startswith(NONNAME_MEANING):
                    ok = False
                if strict and not mc.startswith(("unknown noun", "fish-class name element", "handled-jar")):
                    ok = False
            if ok:
                cur.append(s)
            else:
                if cur and left != "#":
                    cores.append(tuple(cur))
                cur, left = [], "x"
            k += 1
        out[key] = cores
    return out


def indus_cores(split="dev", strict=False, loose=False):
    bytext = indus_cores_by_text(strict, loose)
    dev, ho = dev_heldout(version=2)
    keys = {"dev": dev, "heldout": ho, "all": dev + ho}[split]
    inc = Counter()
    missing = 0
    for t in keys:
        sq = tuple(s for s in t["seq"])
        if sq not in bytext:
            missing += 1
            continue
        for c in set(bytext[sq]):
            inc[c] += 1
    return dict(inc)


# ------------------------------------------------------------------ Ur III seal-legend personal names
UR_TITLES = set("""dumu dub-sar lugal arad2 arad2-zu arad lu2 ensi2 ugula nu-banda3 gudu4 dam-gar3 lunga sipa szabra
sagi kal-ga aga3-us2 kuruszda muhaldim nu-banda3-gu4 dumu-munus u3 szusz3 sa12-du5 ma2-lah5 dam sanga nin
geme2 geme2-zu szu-i ka-guru7 sukkal sukkal-mah gala ni3 nar zabar-dab5 ensi2-ka dub-sar-zu x x-x x-x-x
ur3-ra lu2-kin-gi4-a szar2-ra-ab-du igi-du8 um-mi-a i3-du8 gal-zu kuszx dumu-zu ugula-e2""".split())


def _ur_signs(word):
    w = word.strip("_").replace("#", "").replace("!", "").replace("?", "")
    out = []
    for part in w.split("-"):
        for m in re.finditer(r"\{[^}]+\}|[^{}]+", part):
            s = m.group(0)
            if s:
                out.append(s)
    return tuple(out)


def ur3_names():
    inc = Counter()
    for l in open(CODELIB / "ur3_legends.jsonl"):
        seq = [w.strip("_") for w in json.loads(l)["seq"]]
        names = set()
        for i, w in enumerate(seq):
            if i == 0 or seq[i - 1] in ("dumu", "dam", "dumu-munus"):
                if w in UR_TITLES or "{ki}" in w or "x" in w.split("-") or w.startswith("lugal-") and False:
                    continue
                if re.fullmatch(r"\{d\}[^-{}]+", w):   # bare divine name
                    continue
                names.add(_ur_signs(w))
        for n in names:
            if n:
                inc[n] += 1
    return dict(inc)


# ------------------------------------------------------------------ Linear B personal names (DAMOS)
def _lb_clean(w):
    w = unicodedata.normalize("NFD", w)
    w = "".join(ch for ch in w if unicodedata.category(ch) != "Mn")
    return w


def linear_b_names():
    inc = Counter()
    for l in open(DAMOS):
        r = json.loads(l)
        if not r.get("content") or not r.get("heading"):
            continue
        ser = r["heading"].split()
        dser = len(ser) > 1 and ser[0] == "KN" and ser[1].startswith("D")
        for line in r["content"].split("\n"):
            toks = line.split()
            if not toks:
                continue
            if toks[0].startswith("."):
                toks = toks[1:]
            if not toks:
                continue
            person = any(t.startswith(("VIR", "MUL")) for t in toks)
            if not (person or dser):
                continue
            w = _lb_clean(toks[0])
            if not re.fullmatch(r"(\*?[a-z0-9]+)(-\*?[a-z0-9]+)+", w):  # >=2 syllables, undamaged
                if not re.fullmatch(r"[a-z][a-z0-9]?", w):
                    continue
            inc[tuple(w.split("-"))] += 1
    return dict(inc)


def linear_b_words():
    """All undamaged syllabic sign-groups (names + vocabulary) - sensitivity corpus."""
    inc = Counter()
    for l in open(CODELIB / "linear_b.jsonl"):
        for w in set(json.loads(l)["seq"]):
            if re.fullmatch(r"(\*?[a-z0-9]+)(-\*?[a-z0-9]+)*", w):
                inc[tuple(w.split("-"))] += 1
    return dict(inc)


# ------------------------------------------------------------------ Proto-Elamite entry headings
def proto_elamite():
    inc = Counter()
    for l in open(CODELIB / "proto_elamite.jsonl"):
        seq = json.loads(l)["seq"]
        cur, cores = [], []
        for s in seq + ["N00"]:
            if re.match(r"N\d", s) or s.startswith(("X", "[")):
                if cur:
                    cores.append(tuple(cur))
                cur = []
            else:
                cur.append(re.sub(r"~\w+", "", s))
        for c in set(cores):
            inc[c] += 1
    return dict(inc)


# ------------------------------------------------------------------ Chinese personal names (characters)
def chinese_names(given_only=False, n_max=60000, seed=0):
    lines = [l.strip().lstrip("﻿") for l in open(HERE / "data" / "chinese_names_modern.txt", encoding="utf-8")]
    lines = [l for l in lines if 2 <= len(l) <= 3 and all("一" <= ch <= "鿿" for ch in l)]
    sur = Counter(l[0] for l in lines)
    top = {s for s, _ in sur.most_common(150)} - {"阿", "小"}
    lines = [l for l in lines if l[0] in top]
    rng = np.random.default_rng(seed)
    if len(lines) > n_max:
        lines = list(rng.choice(lines, n_max, replace=False))
    inc = Counter()
    for l in lines:
        inc[tuple(l[1:] if given_only else l)] += 1
    return dict(inc)


# ------------------------------------------------------------------ synthetic codes
def _zipf(n, a, rng):
    p = 1 / np.arange(1, n + 1) ** a
    return p / p.sum()


def synthetic(kind, n_cores=3000, len_dist=None, seed=0):
    """kind: 'logo_slot' (fixed-position whole-word elements), 'logo_free' (same elements, free order),
    'syll' (names spelled with a 70-sign syllabary).  len_dist: {L: prob}."""
    rng = np.random.default_rng(seed)
    len_dist = len_dist or {1: .45, 2: .40, 3: .12, 4: .03}
    Ls = np.array(list(len_dist)); pL = np.array(list(len_dist.values())); pL = pL / pL.sum()
    inc = Counter()
    if kind == "syll":
        V = 70; p = _zipf(V, 0.9, rng)
        # names are 2-4 syllables long; a core of L signs is an L-syllable name (no slot constraint)
        for _ in range(n_cores):
            L = rng.choice(Ls, p=pL)
            inc[tuple(f"s{i}" for i in rng.choice(V, L, p=p))] += 1
        return dict(inc)
    # whole-word elements: 4 slots (e.g. clan / theophoric / quality / suffix-like), each its own lexicon
    nslot = 4; per = 90
    p = _zipf(per, 1.0, rng)
    for _ in range(n_cores):
        L = int(rng.choice(Ls, p=pL))
        slots = sorted(rng.choice(nslot, min(L, nslot), replace=False))
        core = [f"e{sl}_{rng.choice(per, p=p)}" for sl in slots]
        if kind == "logo_free":
            core = list(rng.permutation(core))
        inc[tuple(core)] += 1
    return dict(inc)


if __name__ == "__main__":
    for name, f in [("indus dev", lambda: indus_cores("dev")), ("indus heldout", lambda: indus_cores("heldout")),
                    ("ur3", ur3_names), ("linb names", linear_b_names), ("linb words", linear_b_words),
                    ("proto-elamite", proto_elamite), ("chinese", chinese_names), ("chinese given", lambda: chinese_names(True))]:
        d = f()
        L = Counter(min(len(c), 5) for c in d)
        V = len({s for c in d for s in c})
        print(f"{name:15s} types {len(d):6d} signs {V:5d} len dist {dict(sorted(L.items()))}  e.g. {list(d)[:4]}")
