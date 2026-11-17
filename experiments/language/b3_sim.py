"""B3. Planted-language simulations: can corpus-level typological statistics tell the candidate
languages apart once they are written in a logo-syllabic seal script? (POWER first.)

Classes: DRA (Proto-Dravidian/South Dravidian), IA (Vedic/Old Indo-Aryan), MUN (Munda), BUR
(Burushaski), ELA (Elamite), SUM (Sumerian, resampled real Ur III seal legends), NONLING (slot-based
emblem system, no language).
Each simulated corpus: ~2,300 distinct seal legends (name + optional title / kin / case), written
with a simulated script (logograms for the commonest morphemes, CV syllabograms for the rest,
random script conventions), lengths resampled to the Indus length distribution. Nuisance
parameters (rates of titles, kin phrases, case endings, logogram share, script conventions,
title order within the language's attested range) are redrawn for every corpus, so the classifier
can only win on what survives that variation.
Run: .venv/bin/python experiments/language/b3_sim.py [--n 30]
"""
import json
import math
import zlib
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, icit_texts, distinct, runs  # noqa

SYM = "--sym" in sys.argv  # spec E: equal name-ending rates across suffixing languages
UNDER = "--underspell" in sys.argv  # spec D: scribes may omit grammatical affixes
OPEN = "--opener" in sys.argv  # spec C: every language may use a fixed genre opener word
ALT = "--alt" in sys.argv  # specification B: alternative plausible grammar/genre choices
PG = ROOT / "sources" / "paragorth_Indus-" / "data"
WK = HERE / "ext" / "wikt"
VOW = set("aeiouAEIOU")


# ------------------------------------------------------------------ vocabularies
def norm(w):
    w = w.split("/")[-1].strip().strip("-")
    rep = {"ɨ": "i", "ə": "a", "ɔ": "o", "ɛ": "e", "ŋ": "ng", "ɲ": "ny", "ʔ": "", "ː": "", "ɗ": "d", "ɓ": "b",
           "ɕ": "s", "ʃ": "s", "ẓ": "z", "ḻ": "l", "ṯ": "t", "ñ": "ny", "ċ": "c", "ġ": "g", "ż": "z", "ś": "s",
           "ṣ": "s", "ṭ": "t", "ḍ": "d", "ṇ": "n", "ḷ": "l", "ṅ": "ng", "ā": "A", "ī": "I", "ū": "U", "ē": "E", "ō": "O"}
    w = unicodedata.normalize("NFC", w)
    w = "".join(rep.get(ch, ch) for ch in w)
    w = unicodedata.normalize("NFKD", w)
    w = "".join(ch for ch in w if ch.isascii() and ch.isalpha())
    w = w.replace("V", "a").replace("C", "").replace("H", "h")
    out = "".join(ch.lower() if ch not in "AIUEO" else ch for ch in w)
    return out


def slp_ascii(w):
    m = {"A": "A", "I": "I", "U": "U", "f": "ri", "F": "ri", "x": "li", "e": "E", "o": "O", "E": "ai", "O": "au",
         "K": "kh", "G": "gh", "N": "n", "C": "ch", "J": "jh", "Y": "n", "w": "t", "W": "th", "q": "d", "Q": "dh",
         "R": "n", "T": "th", "D": "dh", "P": "ph", "B": "bh", "S": "s", "z": "s", "M": "m", "H": "h"}
    return "".join(m.get(ch, ch) for ch in w)


_UR = {"ا": "a", "آ": "a", "ب": "b", "پ": "p", "ت": "t", "ٹ": "t", "ث": "s", "ج": "j", "چ": "c", "ح": "h",
       "خ": "kh", "د": "d", "ڈ": "d", "ذ": "z", "ر": "r", "ڑ": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh",
       "ص": "s", "ض": "z", "ط": "t", "ظ": "z", "ع": "", "غ": "gh", "ف": "f", "ق": "q", "ک": "k", "ك": "k",
       "گ": "g", "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "u", "ہ": "h", "ھ": "h", "ه": "h", "ی": "i",
       "ي": "i", "ے": "e", "ݸ": "ts", "ݳ": "sh", "ݴ": "zh", "ݣ": "ng", "ݺ": "ts", "ݼ": "s", "ݽ": "c"}


def urdu_translit(w):
    """Crude transliteration of Burushaski Urdu-script lemmas; short vowels are unwritten, so an
    'a' is inserted between adjacent consonants."""
    seq = [_UR.get(ch) for ch in w if _UR.get(ch) is not None]
    if not seq:
        return ""
    out = ""
    for x in seq:
        if out and out[-1] not in "aeiou" and x[0] not in "aeiou":
            out += "a"
        out += x
    return out


def lines(p):
    return [l.strip() for l in open(p, encoding="utf8") if l.strip() and not l.startswith("#")]


def load_vocab():
    v = {}
    dra = [norm(w) for w in lines(WK / "Proto-Dravidian_lemmas.txt")]
    dra += lines(PG / "derived" / "lex_malayalam.txt") + lines(PG / "derived" / "lex_kannada.txt")
    v["DRA"] = dra
    mw = [slp_ascii(w) for w in lines(HERE / "ext" / "skt" / "mw_headwords.txt")]
    random.Random(0).shuffle(mw)
    from yj_common import iast_to_slp  # noqa
    rv = [slp_ascii(iast_to_slp(l.split()[0])) for l in lines(HERE / "ext" / "eqstats" / "rv_names_epithets_lemmas.txt")]
    v["IA"] = rv + mw[:8000]
    v["MUN"] = lines(PG / "derived" / "lex_santali.txt") + [norm(w) for w in lines(WK / "Proto-Austroasiatic_lemmas.txt")]
    bur = [norm(w) for w in lines(WK / "Burushaski_lemmas.txt")]
    bur += [urdu_translit(w) for w in lines(WK / "Burushaski_lemmas.txt")]
    bur += [w.split("_")[0] for w in lines(WK / "burushaski_words_raw.txt")]
    v["BUR"] = bur
    v["ELA"] = lines(PG / "derived" / "lex_elamite.txt")
    for k in v:
        v[k] = [w for w in dict.fromkeys(v[k]) if 2 <= len(w) <= 9 and any(c in VOW for c in w)]
    return v


sys.path.insert(0, str(HERE))


# ------------------------------------------------------------------ grammars
# A legend = list of words; a word = list of (morpheme, kind) with kind in {root, pre, suf, inf, kin, title, dn}

class Lang:
    def __init__(self, code, vocab, rng):
        self.code, self.rng = code, rng
        r = rng
        self.p_title = r.uniform(0.15, 0.7)
        self.p_kin = r.uniform(0.05, 0.5)
        self.p_case = r.uniform(0.2, 0.9)
        self.p_comp = r.uniform(0.1, 0.6)
        self.p_theo = r.uniform(0.0, 0.4)
        self.rng_end = r.uniform(0.3, 0.95)
        roots = list(vocab)
        r.shuffle(roots)
        self.titles = roots[:r.randint(20, 120)]
        self.dns = roots[200:200 + r.randint(5, 30)]
        self.roots = roots[300:300 + r.randint(400, 1500)] if len(roots) > 900 else roots
        # Zipfian root use
        self.rw = np.array([1 / (i + 1) ** r.uniform(0.6, 1.1) for i in range(len(self.roots))])
        self.rw /= self.rw.sum()
        self.tw = np.array([1 / (i + 1) ** r.uniform(0.8, 1.3) for i in range(len(self.titles))]); self.tw /= self.tw.sum()

    def root(self):
        return self.roots[np.searchsorted(np.cumsum(self.rw), self.rng.random())]

    def title(self):
        return self.titles[np.searchsorted(np.cumsum(self.tw), self.rng.random())]


class DRA(Lang):  # strictly suffixing, modifier-head; Tamil-Brahmi style legends
    def setup(self):
        self.p_tf = self.rng.uniform(0.4, 0.95) if not ALT else self.rng.uniform(0.0, 0.6)  # title precedes name
        self.gsuf = ["an", "An", "i", "ar", "an", "an"] if not ALT else ["an", "ar", "al", "i", "an"]
        self.case = ["a", "atu", "kku", "in"] if not ALT else ["kku", "ai", "il", "otu"]
        self.son = "makan"

    def name(self):
        w = [(self.root(), "root")]
        if self.rng.random() < self.p_comp:
            w.append((self.root(), "root"))
        if self.rng.random() < (self.rng_end if SYM else 0.85):
            w.append((self.rng.choice(self.gsuf), "suf"))
        return w

    def legend(self):
        r = self.rng; out = []
        nm = self.name()
        if r.random() < self.p_kin:
            kp = [self.name() + [(r.choice(["a", "in"]), "suf")], [(self.son, "kin")]]
            out += kp
        t = [(self.title(), "title")] + ([("an", "suf")] if r.random() < 0.3 else [])
        if r.random() < self.p_title and r.random() < self.p_tf:
            out = [t] + out
        out.append(nm)
        if r.random() < self.p_title * (1 - self.p_tf):
            out.append(t)
        if r.random() < self.p_case:
            out[-1] = out[-1] + [(r.choice(self.case), "suf")]
        if ALT and len(out) > 2 and r.random() < 0.5 and out[-1][0][1] == "root":  # name first, then 'son of X'
            out = [out[-1]] + out[:-1]
        return out


class IA(Lang):  # suffixing + some name prefixes; vrddhi patronymics (initial vowel change)
    def setup(self):
        self.p_pref = self.rng.uniform(0.05, 0.3) if not ALT else self.rng.uniform(0.0, 0.15)
        self.pref = ["su", "a", "pra", "vi", "sam", "upa", "dur", "abhi", "nir"]
        self.p_tf = self.rng.uniform(0.2, 0.7) if not ALT else self.rng.uniform(0.5, 1.0)
        self.case = ["sya", "sya", "h", "asya"] if not ALT else ["sya", "asya", "ah", "ena"]

    def name(self):
        r = self.rng; w = []
        if r.random() < self.p_pref:
            w.append((r.choice(self.pref), "pre"))
        if r.random() < self.p_theo:
            w += [(r.choice(self.dns), "dn"), (r.choice(["datta", "mitra", "gupta", "raksita", "deva", "pAla"]), "root")]
        else:
            w.append((self.root(), "root"))
            if r.random() < self.p_comp:
                w.append((self.root(), "root"))
        if SYM and self.rng.random() < self.rng_end:  # stem/nominative ending, as obligatory as DRA -an
            w.append((self.rng.choice(["a", "ah", "i", "u", "am"]), "suf"))
        return w

    def vrddhi(self, w):
        m, k = w[0]
        m2 = re.sub(r"[aiu]", lambda x: {"a": "A", "i": "ai", "u": "au"}[x.group()], m, count=1)
        return [(m2, k)] + w[1:] + [(self.rng.choice(["i", "Ayana", "a"]), "suf")]

    def legend(self):
        r = self.rng; out = []
        nm = self.name()
        out.append(nm + [(r.choice(self.case), "suf")] if r.random() < self.p_case else nm)
        if r.random() < self.p_kin:
            if r.random() < (0.5 if not ALT else 0.0):
                out.append(self.vrddhi(self.name()))
            else:
                out += [self.name() + [("sya", "suf")], [("putra", "kin"), ("sya", "suf")]]
        if r.random() < self.p_title:
            t = [(self.title(), "title")]
            out = [t] + out if r.random() < self.p_tf else out + [t]
        if r.random() < 0.2:
            out = [[("zrI", "title")]] + out
        return out


class MUN(Lang):  # prefixes + infix + suffixes (Proto-Munda / Para-Munda names)
    def setup(self):
        self.p_pref = self.rng.uniform(0.25, 0.7) if not ALT else self.rng.uniform(0.05, 0.35)
        self.p_inf = self.rng.uniform(0.03, 0.2) if not ALT else self.rng.uniform(0.0, 0.05)
        self.pref = ["ka", "ki", "ko", "ma", "a", "se", "pa"]
        self.p_tf = self.rng.uniform(0.3, 0.8) if not ALT else self.rng.uniform(0.0, 0.6)
        self.case = ["ren", "ak", "ko", "re"] if not ALT else ["ren", "ak", "rak", "te"]

    def name(self):
        r = self.rng; w = []
        if r.random() < self.p_pref:
            w.append((r.choice(self.pref), "pre"))
        rt = self.root()
        if r.random() < self.p_inf and len(rt) > 2 and rt[0] not in VOW:
            w += [(rt[0], "root"), ("an", "inf"), (rt[1:], "root")]
        else:
            w.append((rt, "root"))
        if r.random() < self.p_comp * 0.5:
            w.append((self.root(), "root"))
        return w

    def legend(self):
        r = self.rng; out = []
        if r.random() < self.p_kin:
            out += [self.name() + [(r.choice(["ren", "ak"]), "suf")], [("hopon", "kin")]]
        nm = self.name()
        if r.random() < self.p_title:
            t = [(self.title(), "title")]
            if r.random() < self.p_tf:
                out = [t] + out + [nm]
            else:
                out = out + [nm, t]
        else:
            out.append(nm)
        if r.random() < self.p_case:
            out[-1] = out[-1] + [(r.choice(self.case), "suf")]
        return out


class BUR(Lang):  # pronominal possessor prefixes on kin terms; suffixing case
    def setup(self):
        self.p_tf = self.rng.uniform(0.2, 0.7) if not ALT else self.rng.uniform(0.4, 0.9)
        self.case = ["e", "mo", "ar", "e"] if not ALT else ["e", "mo", "ate", "cum"]
        self.p_kpref = 1.0 if not ALT else 0.5

    def name(self):
        w = [(self.root(), "root")]
        if self.rng.random() < self.p_comp * 0.5:
            w.append((self.root(), "root"))
        return w

    def legend(self):
        r = self.rng; out = []
        if r.random() < self.p_kin:
            kin = r.choice(["i", "ai", "ri", "ing"])
            kw = [(r.choice(["i", "mu", "a", "gu", "u"]), "pre"), (kin, "kin")] if r.random() < self.p_kpref else [("ilji", "kin")]
            out += [self.name() + [("e", "suf")], kw]
        nm = self.name()
        if r.random() < self.p_title:
            t = [(self.title(), "title")]
            out = ([t] + out + [nm]) if r.random() < self.p_tf else (out + [nm, t])
        else:
            out.append(nm)
        if r.random() < self.p_case:
            out[-1] = out[-1] + [(r.choice(self.case), "suf")]
        return out


class ELA(Lang):  # suffixing class markers with agreement (Suffixaufnahme); head-first
    def setup(self):
        self.cls = ["k", "r", "t", "p", "me", "ri", "ra"]

    def name(self):
        r = self.rng
        if r.random() < 0.3 + self.p_theo:
            return [(self.root(), "root"), (r.choice(self.dns), "dn")]
        return [(self.root(), "root")] + ([(r.choice(self.cls), "suf")] if r.random() < (self.rng_end if SYM else 0.5) else [])

    def legend(self):
        r = self.rng
        out = [self.name()]
        agr = r.choice(["ri", "r", "ra"])
        use_agr = (not ALT) or r.random() < 0.5
        A = [(agr, "suf")] if use_agr else []
        if r.random() < self.p_kin:
            out += [[("sak", "kin")] + A, self.name() + A]
        if r.random() < self.p_title:
            if ALT and r.random() < 0.4:
                out = [[(self.title(), "title")] + A] + out
            else:
                out.append([(self.title(), "title")] + A)
        if r.random() < self.p_case:
            out[-1] = out[-1] + [(r.choice(["na", "ni", "me"]), "suf")]
        return out


class SUM:
    """Resample real Ur III seal legends (CDLI, via paragorth codelib) with name substitution:
    words seen >= 25 times are kept (titles/kin/deities), other words are replaced by random names."""
    data = None

    def __init__(self, code, vocab, rng):
        self.rng = rng
        if SUM.data is None:
            L = [json.loads(l)["seq"] for l in open(PG / "codelib" / "ur3_legends.jsonl")]
            f = Counter(w for s in L for w in s)
            SUM.data = (L, f)
        L, f = SUM.data
        self.L, self.f = L, f
        self.thr = rng.randint(15, 40) if not ALT else rng.randint(8, 60)
        self.names = [w for w in f if f[w] < self.thr]

    def setup(self):
        pass

    def word(self, w):
        out = []
        for part in re.split(r"[-.]", w):
            p = re.sub(r"[{}_\d]", "", part).lower().replace("sz", "s")
            if p:
                out.append((p, "root" if w.startswith("_") else "syl"))
        return out

    def legend(self):
        s = self.rng.choice(self.L)
        out = []
        for w in s:
            ww = w if self.f[w] >= self.thr else self.rng.choice(self.names)
            m = self.word(ww)
            if self.f[w] >= self.thr:  # frequent word: keep as one morpheme (logogram candidate)
                m = [("".join(x for x, _ in m), "title")]
            if m:
                out.append(m)
        return out or [[("lugal", "title")]]


class NONLING:
    """Slot grammar without language: k ordered slots, each filled (optionally) by an emblem from a
    slot-specific Zipfian class; some emblems are drawn as fixed 2-sign groups."""

    def __init__(self, code, vocab, rng):
        self.rng = rng
        k = rng.randint(3, 7) if not ALT else rng.randint(2, 9)
        nid = 0
        self.slots = []
        for _ in range(k):
            size = rng.randint(3, 120)
            ems = []
            for _ in range(size):
                if rng.random() < rng.uniform(0, 0.3):
                    ems.append((f"e{nid}", f"e{nid+1}")); nid += 2
                else:
                    ems.append((f"e{nid}",)); nid += 1
            w = np.array([1 / (i + 1) ** rng.uniform(0.5, 1.4) for i in range(size)]); w /= w.sum()
            self.slots.append((rng.uniform(0.2, 0.95), ems, np.cumsum(w)))
        self.p_rep = rng.uniform(0, 0.15) if not ALT else rng.uniform(0, 0.3)

    def setup(self):
        pass

    def legend(self):
        out = []
        for p, ems, cw in self.slots:
            if self.rng.random() < p:
                e = ems[min(len(ems) - 1, np.searchsorted(cw, self.rng.random()))]
                out.append([(x, "emblem") for x in e])
                if self.rng.random() < self.p_rep:
                    out.append([(x, "emblem") for x in e])
        return out or [[(ems[0][0], "emblem")]]


CLASSES = {"DRA": DRA, "IA": IA, "MUN": MUN, "BUR": BUR, "ELA": ELA, "SUM": SUM, "NONLING": NONLING}


# ------------------------------------------------------------------ script
def syllabify(m):
    """morpheme -> list of (onset, vowel) open syllables + coda markers (C, None)."""
    toks = re.findall(r"[aeiouAEIOU]+|[^aeiouAEIOU]+", m)
    syl, onset = [], ""
    for i, t in enumerate(toks):
        if t[0] in VOW:
            syl.append((onset[-1:] if onset else "", t[0]))
            onset = ""
        else:
            if i == len(toks) - 1:  # final consonants
                syl += [(c, None) for c in t[:1]]
            elif syl and len(t) >= 2:
                syl.append((t[0], None)); onset = t[1:]
            else:
                onset = t
    return syl


class Script:
    def __init__(self, rng, morph_freq):
        self.rng = rng
        self.n_logo = rng.randint(80, 450)
        self.p_coda = rng.uniform(0, 1)  # write codas with dead-vowel signs
        self.mark_length = rng.random() < 0.5
        self.p_homo = rng.uniform(0, 0.3)  # alternative signs for the same syllable
        self.affix_logo = rng.random() < 0.4
        self.p_omit = rng.uniform(0, 0.8) if UNDER else 0.0
        ranked = [m for m, _ in morph_freq.most_common()]
        self.logo = {}
        for m in ranked:
            if len(self.logo) >= self.n_logo:
                break
            mm, kind = m
            if kind in ("suf", "pre", "inf") and not self.affix_logo:
                continue
            if kind == "syl":
                continue
            self.logo[m] = f"L{len(self.logo)}"
        self.syl = {}

    def sig(self, s):
        if s not in self.syl:
            self.syl[s] = [f"S{len(self.syl)}"]
            if self.rng.random() < self.p_homo:
                self.syl[s].append(f"S{len(self.syl)}x")
        return self.rng.choice(self.syl[s])

    def write(self, legend):
        out = []
        for w in legend:
            for m in w:
                if m[1] == "emblem":
                    out.append(m[0]); continue
                if m[1] in ("suf", "pre", "inf") and self.rng.random() < self.p_omit:
                    continue
                if m in self.logo:
                    out.append(self.logo[m]); continue
                for c, v in syllabify(m[0]):
                    if v is None:
                        if self.rng.random() < self.p_coda:
                            out.append(self.sig((c, "a")))
                        continue
                    if not self.mark_length:
                        v = v.lower()
                    out.append(self.sig((c, v)))
        return out


# ------------------------------------------------------------------ corpus generation
def indus_lengths():
    dev, ho = dev_heldout()
    return [len(r) for t in dev + ho for r in runs(t["seq"])][:]


def make_corpus(code, vocab, rng, target_lengths, n_texts=2300):
    L = CLASSES[code](code, vocab.get(code, []), rng)
    L.setup()
    raw = [L.legend() for _ in range(25000)]
    if OPEN and code != "NONLING":
        p_open = rng.uniform(0.05, 0.5)
        pool = vocab.get(code) or ["kisib", "mu", "na"]
        openers = [rng.choice(pool) for _ in range(rng.randint(1, 3))]
        raw = [([[(rng.choice(openers), "title")]] + lg) if rng.random() < p_open else lg for lg in raw]
    mf = Counter(m for lg in raw for w in lg for m in w)
    sc = Script(rng, mf)
    texts = list(dict.fromkeys(tuple(sc.write(lg)) for lg in raw))
    by_len = defaultdict(list)
    for t in texts:
        if t:
            by_len[len(t)].append(t)
    # resample to the Indus length distribution (distinct texts); fall back to nearest length
    out = []
    lens = list(target_lengths); rng.shuffle(lens)
    used = set()
    for n in lens[:n_texts]:
        for d in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, 6, 7, 8]:
            pool = by_len.get(n + d)
            if pool:
                t = pool.pop(rng.randrange(len(pool)))
                if t not in used:
                    used.add(t); out.append(list(t)); break
    return out


# ------------------------------------------------------------------ features
def H(c):
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v)


def features(texts):
    texts = [t for t in texts if t]
    toks = [s for t in texts for s in t]
    f = Counter(toks)
    V = len(f)
    N = len(toks)
    lens = np.array([len(t) for t in texts])
    multi = [t for t in texts if len(t) >= 2]
    first = Counter(t[0] for t in multi); last = Counter(t[-1] for t in multi)
    big = Counter((a, b) for t in texts for a, b in zip(t, t[1:]))
    ctx = defaultdict(Counter)
    for (a, b), c in big.items():
        ctx[a][b] += c
    h_cond = sum(sum(c.values()) * H(c) for c in ctx.values()) / max(1, sum(big.values()))
    top = [s for s, _ in f.most_common(10)]
    relpos = defaultdict(list)
    for t in multi:
        for i, s in enumerate(t):
            relpos[s].append(i / (len(t) - 1))
    # alternation asymmetry: texts identical except last sign vs except first sign
    pre, suf = defaultdict(set), defaultdict(set)
    for t in set(map(tuple, multi)):
        pre[t[:-1]].add(t[-1]); suf[t[1:]].add(t[0])
    a_end = sum(len(v) - 1 for v in pre.values()); a_start = sum(len(v) - 1 for v in suf.values())
    # 2-sign version
    pre2, suf2 = defaultdict(set), defaultdict(set)
    for t in set(map(tuple, [x for x in multi if len(x) >= 3])):
        pre2[t[:-2]].add(t[-2:]); suf2[t[2:]].add(t[:2])
    a2e = sum(len(v) - 1 for v in pre2.values()); a2s = sum(len(v) - 1 for v in suf2.values())
    # branching entropy of frequent signs: right vs left
    lctx = defaultdict(Counter)
    for (a, b), c in big.items():
        lctx[b][a] += c
    fr = [s for s, c in f.most_common(50)]
    be_r = np.mean([H(ctx[s]) for s in fr if ctx[s]]); be_l = np.mean([H(lctx[s]) for s in fr if lctx[s]])
    rep_adj = sum(c for (a, b), c in big.items() if a == b) / max(1, sum(big.values()))
    rep_any = np.mean([len(t) > len(set(t)) for t in texts if len(t) >= 3])
    heaps_half = len(set(s for t in texts[: len(texts) // 2] for s in t))
    ranks = np.arange(1, min(V, 100) + 1)
    freqs = np.array([c for _, c in f.most_common(100)], float)
    zipf = np.polyfit(np.log(ranks), np.log(freqs), 1)[0]
    pos_top = [np.mean(relpos[s]) for s in top if relpos[s]]
    feat = dict(
        V=V, logV=math.log(V), ttr=V / N, hapax=sum(1 for c in f.values() if c == 1) / V,
        heaps_ratio=V / max(1, heaps_half), zipf=zipf, top10_share=sum(f[s] for s in top) / N,
        H1=H(f) / math.log2(V), Hcond=h_cond / max(1e-9, H(f)),
        H_first=H(first) / math.log2(V), H_last=H(last) / math.log2(V),
        first_minus_last=(H(first) - H(last)) / math.log2(V),
        top5_last_share=sum(c for _, c in last.most_common(5)) / max(1, len(multi)),
        top5_first_share=sum(c for _, c in first.most_common(5)) / max(1, len(multi)),
        pos_top10_mean=float(np.mean(pos_top)), pos_top10_sd=float(np.std(pos_top)),
        pos_top1=float(np.mean(relpos[top[0]])) if relpos[top[0]] else 0.5,
        alt_asym=math.log((a_end + 1) / (a_start + 1)), alt_asym2=math.log((a2e + 1) / (a2s + 1)),
        alt_rate=(a_end + a_start) / max(1, len(multi)),
        be_asym=be_r - be_l, rep_adj=rep_adj, rep_any=float(rep_any),
        bigram_ttr=len(big) / max(1, sum(big.values())), len_mean=float(lens.mean()), len_sd=float(lens.std()),
    )
    return feat


def indus_corpora():
    dev, ho = dev_heldout()
    m77 = [r for t in dev + ho for r in runs(t["seq"])]
    icit = [r for t in distinct(icit_texts()) for r in t.get("segments") or runs(t["seq"])]
    return {"M77_all": m77, "M77_dev": [r for t in dev for r in runs(t["seq"])], "ICIT_all": icit}


def main():
    nper = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 30
    vocab = load_vocab()
    print({k: len(v) for k, v in vocab.items()})
    tl = indus_lengths()
    rows = []
    for code in CLASSES:
        for i in range(nper):
            rng = random.Random(zlib.crc32(f"{code}{i}{ALT}{OPEN}{UNDER}{SYM}".encode()))
            np.random.seed(i)
            c = make_corpus(code, vocab, rng, tl)
            ft = features(c)
            ft["cls"] = code; ft["rep"] = i
            rows.append(ft)
            if i == 0:
                print(code, len(c), "texts; V=", ft["V"], "len", round(ft["len_mean"], 2), "eg:", c[:3], flush=True)
    ind = {k: features(v) for k, v in indus_corpora().items()}
    json.dump(dict(sims=rows, indus=ind), open(HERE / "out" / ("b3_features_sym.json" if SYM else "b3_features_under.json" if UNDER else "b3_features_open.json" if OPEN else "b3_features_alt.json" if ALT else "b3_features.json"), "w"), indent=0, default=float)
    print("Indus:", json.dumps(ind["M77_all"], default=float))


if __name__ == "__main__":
    main()
