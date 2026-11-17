"""Planted-answer control corpora with known consonant x vowel grids.

All corpora are returned as (texts, truth_c, truth_v, info) where texts are tuples of OPAQUE sign ids
(random integers as strings, e.g. 'S0417'), truth_c / truth_v map those ids to the hidden consonant /
vowel of syllabograms (logograms and unclassifiable signs are absent from truth).
"""
import json, re, random, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAMOS = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
MAL = ROOT / "sources/paragorth_Indus-/data/derived/lex_malayalam.txt"

LB_STD = re.compile(r"^([djkmnpqrstwz]?)([aeiou])$")


def _clean(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _damos_rows():
    rows = [json.loads(l) for l in open(DAMOS)]
    return [r for r in rows if r.get("content")]


def _opaque(texts, seed):
    """Replace every sign by a random opaque id; return mapping too."""
    rng = random.Random(seed)
    signs = sorted({s for t in texts for s in t})
    ids = rng.sample(range(10000), len(signs))
    m = {s: f"S{i:04d}" for s, i in zip(signs, ids)}
    return [tuple(m[s] for s in t) for t in texts], m


def _truth_from(mapping, cons_of, vow_of):
    tc, tv = {}, {}
    for s, o in mapping.items():
        c, v = cons_of(s), vow_of(s)
        if c is not None:
            tc[o] = c; tv[o] = v
    return tc, tv


def _lb_c(s):
    m = LB_STD.match(s); return (m.group(1) or "V") if m else None


def _lb_v(s):
    m = LB_STD.match(s); return m.group(2) if m else None


# ------------------------------------------------------------------ Linear B (real, DAMOS)
def linear_b_words(n=None, seed=0, logo_share=0.0):
    """Distinct, complete (no brackets) Linear B sign groups from DAMOS, one word = one text."""
    words = Counter()
    for r in _damos_rows():
        for tok in re.split(r"[\s,/]+", _clean(r["content"])):
            if "-" in tok and re.fullmatch(r"[a-z0-9\*\-]+", tok):
                sy = tuple(x for x in tok.split("-") if x)
                if len(sy) >= 2:
                    words[sy] += 1
    W = sorted(words)
    rng = random.Random(seed)
    if n and n < len(W):
        W = rng.sample(W, n)
    if logo_share > 0:
        W = _logoize_words(W, logo_share, rng)
    lg = sum(1 for t in W for s in t if s.startswith("LOGO")) / sum(len(t) for t in W)
    texts, m = _opaque(W, seed)
    tc, tv = _truth_from(m, _lb_c, _lb_v)
    return texts, tc, tv, dict(name="LinearB-words", n=len(texts), mean_len=_ml(texts), logo_share=round(lg, 3))


def linear_b_lines(n=None, seed=0, keep_ideograms=True, minlen=2, maxlen=9):
    """Distinct tablet lines, word dividers REMOVED (Indus has none), ideograms kept as logograms,
    numerals and fragments dropped. Lines with any damaged word are skipped."""
    lines = set()
    for r in _damos_rows():
        for line in _clean(r["content"]).split("\n"):
            toks = [t for t in re.split(r"[\s,/]+", line.strip()) if t]
            if not toks or any(("[" in t or "]" in t or "?" in t) for t in toks):
                continue
            seq = []
            for t in toks:
                if re.fullmatch(r"\.?[0-9a-z]+\.?", t) and "-" not in t and t.startswith("."):
                    continue  # line label like .1 .A
                if re.fullmatch(r"[0-9]+", t):
                    continue
                if "-" in t and re.fullmatch(r"[a-z0-9\*\-]+", t):
                    seq += [x for x in t.split("-") if x]
                elif re.fullmatch(r"[A-Z][A-Z0-9\+\:\*a-z]*", t) and keep_ideograms:
                    if len(t) > 1 or t in ("V", "S", "Z", "T", "M", "N", "P", "Q", "L"):
                        seq.append("LOGO_" + t)
            if minlen <= len(seq) <= maxlen:
                lines.add(tuple(seq))
    L = sorted(lines)
    rng = random.Random(seed)
    if n and n < len(L):
        L = rng.sample(L, n)
    texts, m = _opaque(L, seed)
    tc, tv = _truth_from(m, _lb_c, _lb_v)
    logo = sum(1 for t in L for s in t if s.startswith("LOGO_")) / max(sum(len(t) for t in L), 1)
    return texts, tc, tv, dict(name="LinearB-lines", n=len(texts), mean_len=_ml(texts), logo_share=round(logo, 3))


def _logoize_words(W, share, rng):
    """Write a random set of lemmas (word minus last sign) with one logogram each: LOGO + last sign
    (phonetic complement / ending) half the time, LOGO alone otherwise. Stops when logogram tokens
    reach `share` of all tokens in the output."""
    lem = defaultdict(list)
    for i, w in enumerate(W):
        lem[w[:-1] if len(w) >= 3 else w].append(i)
    keys = list(lem); rng.shuffle(keys)
    syl = sum(len(w) for w in W); logo = 0; out = list(W); k = 0
    while logo / (syl + logo) < share and k < len(keys):
        lm = keys[k]; k += 1
        for i in lem[lm]:
            w = W[i]
            if len(w) >= 3 and rng.random() < 0.5:
                out[i] = ("LOGO_%d" % k, w[-1]); syl -= len(w) - 1
            else:
                out[i] = ("LOGO_%d" % k,); syl -= len(w)
            logo += 1
    return list(dict.fromkeys(out))


def _ml(texts):
    return round(sum(len(t) for t in texts) / max(len(texts), 1), 2)


# ------------------------------------------------------------------ synthetic generator
CONS = list("ptkmnrlsvcdy")
VOWS = list("aeiou")


def syllabify_cv(ph):
    """Phoneme string (letters) -> CV syllabograms, Linear-B style: a consonant without a following
    vowel is dropped word-finally and written with the next vowel's sign otherwise (clusters simplified
    to the last consonant)."""
    out = []; c = ""
    for ch in ph:
        if ch in VOWS:
            out.append((c or "V") + ch); c = ""
        else:
            c = ch
    return out


def make_lang(seed, n_names=1500, n_titles=40, cfinal=0.75, prefixing=False, morph=True):
    rng = random.Random(seed)

    def syl():
        return rng.choice(CONS) + rng.choice(VOWS)
    names = set()
    while len(names) < n_names:
        k = rng.choice([2, 2, 3, 3, 3, 4])
        if prefixing:
            w = rng.choice(VOWS) + "".join(syl() for _ in range(k - 1))  # vowel-initial stems
        else:
            w = ("" if rng.random() < 0.8 else rng.choice(VOWS)) + "".join(syl() for _ in range(k))
            if rng.random() < cfinal:
                w = w[:-1]  # consonant-final stem
        names.add(w)
    names = sorted(names); rng.shuffle(names)
    titles = set()
    while len(titles) < n_titles:
        titles.add("".join(syl() for _ in range(rng.choice([2, 3]))))
    titles = sorted(titles)
    if prefixing:
        affixes = [("", .35), ("m", .15), ("k", .15), ("n", .1), ("t", .1), ("pa", .08), ("so", .07)]
    else:
        affixes = [("a", .35), ("e", .15), ("uku", .15), ("ina", .15), ("ile", .1), ("odu", .1)]
    if not morph:
        affixes = [("a" if not prefixing else "", 1.0)]
    return dict(names=names, titles=titles, affixes=affixes, prefixing=prefixing)


def inflect(stem, aff, prefixing):
    if prefixing:
        return aff + stem
    if stem[-1] in VOWS and aff and aff[0] in VOWS:
        return stem + "v" + aff  # glide
    return stem + aff


def synthetic(N=2300, zipf=1.0, logo_share=0.0, seed=0, prefixing=False, morph=True,
              p_title_before=0.25, p_title_after=0.25, n_names=1500, lang_seed=None, complement=True, p_noise=0.0):
    """Indus-shaped corpus of N distinct texts: [title] name+case [title]. Names drawn Zipf(zipf)."""
    L = make_lang(lang_seed if lang_seed is not None else seed, n_names=n_names, prefixing=prefixing, morph=morph)
    rng = random.Random(seed + 7)
    nn = len(L["names"])
    wts = [1 / (r + 1) ** zipf for r in range(nn)]
    affs, aw = zip(*L["affixes"])
    lexs = set(); tries = 0
    while len(lexs) < N and tries < N * 200:
        tries += 1
        name = rng.choices(range(nn), weights=wts)[0]
        aff = rng.choices(range(len(affs)), weights=aw)[0]
        u = rng.random()
        tb = rng.randrange(len(L["titles"])) if u < p_title_before else None
        ta = rng.randrange(len(L["titles"])) if p_title_before <= u < p_title_before + p_title_after else None
        lexs.add((tb, name, aff, ta))
    lexs = sorted(lexs, key=lambda x: str(x)); rng.shuffle(lexs)
    # choose logographic lexemes until token share reached
    logo_names, logo_titles = set(), set()
    if logo_share > 0:
        cand = [("n", i) for i in range(nn)] + [("t", i) for i in range(len(L["titles"]))]
        rng.shuffle(cand)
        tok = Counter(); occ = Counter()
        for tb, nm, af, ta in lexs:
            tok[("n", nm)] += len(syllabify_cv(L["names"][nm])); occ[("n", nm)] += 1
            if tb is not None: tok[("t", tb)] += len(syllabify_cv(L["titles"][tb])); occ[("t", tb)] += 1
            if ta is not None: tok[("t", ta)] += len(syllabify_cv(L["titles"][ta])); occ[("t", ta)] += 1
        syl = sum(len(syllabify_cv(inflect(L["names"][nm], affs[af], L["prefixing"]))) for _, nm, af, _ in lexs)
        syl += sum(tok[c] for c in tok if c[0] == "t")
        logo = 0
        for c in cand:
            if logo / (syl + logo) >= logo_share:
                break
            if tok[c] == 0:
                continue
            syl -= tok[c]; logo += occ[c]
            (logo_names if c[0] == "n" else logo_titles).add(c[1])
    texts = []; suffix_signs = Counter(); stem_signs = Counter(); title_signs = Counter()
    for tb, nm, af, ta in lexs:
        seq = []
        if tb is not None:
            seq += ["LOGO_T%d" % tb] if tb in logo_titles else syllabify_cv(L["titles"][tb])
        stem = L["names"][nm]; aff = affs[af]
        word = syllabify_cv(inflect(stem, aff, L["prefixing"]))
        if nm in logo_names and not complement:
            seq += ["LOGO_N%d" % nm]  # word sign for the whole inflected word: ending not written
        elif nm in logo_names:
            ns = len(syllabify_cv(stem)) if not L["prefixing"] else 0
            if L["prefixing"]:
                seq += syllabify_cv(aff + stem[0]) + ["LOGO_N%d" % nm]
            else:
                # logogram for the stem + phonetic spelling of the fused ending (bridge + suffix signs)
                seq += ["LOGO_N%d" % nm] + word[ns:]
        else:
            seq += word
        if ta is not None:
            seq += ["LOGO_T%d" % ta] if ta in logo_titles else syllabify_cv(L["titles"][ta])
        texts.append(tuple(seq))
    if p_noise > 0:
        # replace a share of texts by uninflected strings of other vocabulary (no paradigm relation)
        nr = random.Random(seed + 99)
        vocab = ["".join(nr.choice(CONS) + nr.choice(VOWS) for _ in range(nr.choice([2, 3, 4]))) for _ in range(3000)]
        vw = [1 / (r + 1) for r in range(len(vocab))]
        for i in range(len(texts)):
            if nr.random() < p_noise:
                k = nr.choice([1, 2])
                texts[i] = tuple(x for w in nr.choices(vocab, weights=vw, k=k) for x in syllabify_cv(w))
    texts = list(dict.fromkeys(texts))
    logo = sum(1 for t in texts for s in t if s.startswith("LOGO")) / sum(len(t) for t in texts)
    raw = texts
    texts, m = _opaque(raw, seed)
    tc, tv = _truth_from(m, lambda s: None if s.startswith("LOGO") else s[:-1],
                         lambda s: None if s.startswith("LOGO") else s[-1])
    info = dict(name=f"synthetic{'-prefix' if prefixing else ''}{'' if morph else '-nomorph'}", n=len(texts),
                mean_len=_ml(texts), logo_share=round(logo, 3), zipf=zipf)
    return texts, tc, tv, info, raw, m, L


# ------------------------------------------------------------------ Dravidian-like (Malayalam lemmas)
MAL_CASES = [("", .35), ("e", .15), ("inte", .15), ("inu", .1), ("il", .1), ("ode", .08), ("al", .07)]


def akshara(word):
    """Latin-transliterated word -> Brahmic aksharas: (cluster)+vowel, independent vowel at word start
    or after a vowel, consonant(+cluster)+virama when no vowel follows."""
    V = "aeiou"; out = []; c = ""
    for ch in word:
        if ch in V:
            out.append((c or "V") + "|" + ch); c = ""
        elif ch.isalpha():
            c += ch
    if c:
        out.append(c + "|_")  # virama
    return out


def mal_inflect(stem, suf):
    if not suf:
        return stem
    if stem.endswith("am"):
        return stem[:-2] + "att" + suf
    if stem.endswith("u"):
        return stem[:-1] + suf
    if stem[-1] in "aeio":
        return stem + "y" + suf
    return stem + suf


def dravidian(N=2300, zipf=1.0, seed=0, n_names=1500):
    rng = random.Random(seed)
    lem = [w.strip() for w in open(MAL) if 4 <= len(w.strip()) <= 9 and w.strip().isalpha()]
    names = rng.sample(sorted(set(lem)), n_names)
    titles = rng.sample(sorted(set(lem) - set(names)), 40)
    wts = [1 / (r + 1) ** zipf for r in range(n_names)]
    sufs, sw = zip(*MAL_CASES)
    seen = set(); tries = 0
    while len(seen) < N and tries < N * 200:
        tries += 1
        nm = rng.choices(range(n_names), weights=wts)[0]
        sf = rng.choices(range(len(sufs)), weights=sw)[0]
        u = rng.random()
        t = rng.randrange(40)
        lx = (t if u < .25 else None, nm, sf, t if .25 <= u < .5 else None)
        seen.add(lx)
    texts = []
    for tb, nm, sf, ta in sorted(seen, key=str):
        seq = []
        if tb is not None: seq += akshara(titles[tb])
        seq += akshara(mal_inflect(names[nm], sufs[sf]))
        if ta is not None: seq += akshara(titles[ta])
        texts.append(tuple(seq))
    texts = list(dict.fromkeys(texts))
    o, m = _opaque(texts, seed)
    tc, tv = _truth_from(m, lambda s: s.split("|")[0], lambda s: s.split("|")[1])
    return o, tc, tv, dict(name="Dravidian-like (Malayalam lemmas + case)", n=len(o), mean_len=_ml(o), zipf=zipf)


# ------------------------------------------------------------------ agglutinative, morpheme signs
def synthetic_agglut(N=1700, zipf=1.0, seed=0, n_names=1500):
    """Calibration corpus for 'suffix vs separate word': names spelt CV (vowel-final, no fusion),
    case suffixes written each with ONE dedicated sign (nominative = zero), titles written each with
    ONE word sign, placed before (25%) or after (25%) the name.  Returns texts and a role per sign:
    'suffix' (bound to the preceding name), 'word' (separate word), 'syllable'."""
    rng = random.Random(seed)
    def syl(): return rng.choice(CONS) + rng.choice(VOWS)
    names = set()
    while len(names) < n_names:
        names.add(tuple(syl() for _ in range(rng.choice([2, 2, 3, 3, 4]))))
    names = sorted(names); rng.shuffle(names)
    wts = [1 / (r + 1) ** zipf for r in range(n_names)]
    cases = [(None, .35), ("SUF_gen", .2), ("SUF_dat", .15), ("SUF_loc", .1), ("SUF_abl", .1), ("SUF_soc", .1)]
    cs, cw = zip(*cases)
    seen = set(); tries = 0
    while len(seen) < N and tries < N * 200:
        tries += 1
        nm = rng.choices(range(n_names), weights=wts)[0]
        cz = rng.choices(range(len(cs)), weights=cw)[0]
        u = rng.random(); tt = rng.randrange(30)
        seq = list(names[nm]) + ([cs[cz]] if cs[cz] else [])
        if u < .25: seq = ["WORD_%d" % tt] + seq
        elif u < .5: seq = seq + ["WORD_%d" % tt]
        seen.add(tuple(seq))
    texts = sorted(seen); rng.shuffle(texts)
    role = {}
    for t in texts:
        for s in t:
            role[s] = "suffix" if s.startswith("SUF") else "word" if s.startswith("WORD") else "syllable"
    return texts, role
