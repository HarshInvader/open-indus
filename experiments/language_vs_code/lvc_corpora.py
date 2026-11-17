"""Corpora for the language-vs-code calibration.

Every corpus is a list of natural units (texts), each a list of sign tokens.
label: 'L' = writes language, 'C' = non-linguistic code, '?' = unlabelled reference, 'I' = Indus.

Language corpora are written at the level of the writing unit (sign):
  ur3      Ur III seal legends (CDLI), words split at hyphens into cuneiform signs (logo-syllabic, real)
  linb     Linear B tablet lines (DAMOS), sign groups split into syllabograms + ideograms + NUM (real)
  lat_edh  Latin EDH inscriptions, simulated logo-syllabic writing (real text)
  lat_cae  Caesar BG clauses, simulated logo-syllabic writing
  fin_kal  Kalevala verse lines, simulated logo-syllabic writing
  san_wiki Sanskrit Wikipedia clauses, simulated logo-syllabic writing
  tam_wiki Tamil Wikipedia clauses, simulated logo-syllabic writing
Code corpora:
  heraldry Rietstap blazons (words, function words removed; real, a controlled register)
  khipu    Open Khipu Repository cord clusters (colour:magnitude; real, non-linguistic)
  icd10    ICD-10-CM codes as character strings (real code list)
  plates   Indian licence plates, character level (synthetic, state->district dependency)
  sigil    rebuild of Raghavendra 2026 SIGIL emblem generator from the paper's description
  slot     slot-independent emblem code (5 optional slots, independent Zipf choices)
  indus_bigram  paragorth's bigram generator trained on ICIT (non-linguistic by construction; Indus-derived)
Unlabelled: proto_elamite (CDLI entry lines; status disputed).
"""
import json, re, random, sys, csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/decipherability"))
from corpus.load import dev_heldout  # noqa: E402
import langdata as ld  # noqa: E402  (pure text-normalisation functions, read-only use)

CODELIB = ROOT / "sources/paragorth_Indus-/data/codelib"
RAW = ROOT / "experiments/decipherability/raw"
HERE = Path(__file__).resolve().parent


def _jl(name):
    return [json.loads(l)["seq"] for l in open(CODELIB / name)]


# ---------------- Indus ----------------
def indus(split):
    dev, ho = dev_heldout(version=2)
    X = dev if split == "dev" else ho
    return [[s for s in t["seq"] if s != "|"] for t in X if "#" not in t["seq"] and len(t["seq"]) > 0
            and any(s != "|" for s in t["seq"])]


# ---------------- real language, native signs ----------------
def ur3():
    out = []
    for t in _jl("ur3_legends.jsonl"):
        s = []
        for w in t:
            w = w.replace("_", "")
            w = re.sub(r"\{([^}]*)\}", r"-\1-", w)  # determinatives are signs
            s += [x for x in w.split("-") if x]
        if s: out.append(s)
    return out


def linb():
    out = []
    for t in _jl("linear_b.jsonl"):
        s = []
        for w in t:
            s += [x for x in w.split("-") if x and x != "."]
        if s: out.append(s)
    return out


# ---------------- simulated logo-syllabic writing of real text ----------------
def wordlevel(word_texts, seed=8, maxsigns=14):
    """Pure logographic writing: one sign per word (inflected form). Long units chunked as in logosyll."""
    rng = random.Random(seed); out = []
    for t in word_texts:
        if not t: continue
        if len(t) <= maxsigns: out.append(list(t)); continue
        i = 0
        while i < len(t):
            k = rng.randint(2, 6); out.append(list(t[i:i + k])); i += k
    return out


_WT = {}


def _words(name):
    """word-level source texts behind each simulated corpus (cached)"""
    if name in _WT: return _WT[name]
    if name == "lat_edh":
        w = [[ld.norm_latin(x) for x in t if ld.norm_latin(x)] for t in _jl("latin_edh.jsonl")]
    elif name == "lat_cae":
        t = open(RAW / "caesar.txt").read().replace("\n", " ")
        w = _clauses(t, norm=ld.norm_latin, seps=r"[.,;:!?()\[\]\"]")
    elif name == "fin_kal":
        lines = [l.strip() for l in open(RAW / "kalevala.txt", encoding="utf-8") if l.strip()]
        w = [[x for x in (ld.norm_finnic(y) for y in re.findall(r"[^\W\d_]+", l)) if x] for l in lines]
    elif name in ("san_wiki", "tam_wiki"):
        f = {"san_wiki": "wiki_sa.txt", "tam_wiki": "wiki_ta.txt"}[name]
        lines = [l for l in open(RAW / f, encoding="utf-8") if not l.startswith(("{", "|", "[", "=", "*", "<"))]
        w = _clauses(" ".join(lines), indic=True)
    elif name == "ur3":
        w = [[x.replace("_", "") for x in t] for t in _jl("ur3_legends.jsonl")]
    elif name == "linb":
        w = _jl("linear_b.jsonl")
    _WT[name] = [x for x in w if x]
    return _WT[name]


def logosyll(word_texts, logo_share=0.3, cap=300, seed=7, maxsigns=14):
    """Top word types become logograms (to logo_share of tokens, cap types); the rest are written
    with CV syllable signs. Units longer than maxsigns signs are cut into word-aligned chunks of
    2-6 words so that Indus-length units exist (documented caveat)."""
    rng = random.Random(seed)
    cnt = Counter(w for t in word_texts for w in t)
    tot = sum(cnt.values()); acc = 0; logos = set()
    for w, c in cnt.most_common():
        if acc / tot >= logo_share or len(logos) >= cap: break
        logos.add(w); acc += c
    def write(ws):
        s = []
        for w in ws:
            s += ["LG_" + w] if w in logos else ld.syllabify(w)
        return s
    out = []
    for t in word_texts:
        s = write(t)
        if not s: continue
        if len(s) <= maxsigns:
            out.append(s); continue
        i = 0
        while i < len(t):
            k = rng.randint(2, 6); c = write(t[i:i + k]); i += k
            if c: out.append(c)
    return out


def _clauses(text, norm=None, indic=False, seps=r"[.,;:!?।॥()\[\]\"\n]"):
    out = []
    for c in re.split(seps, text):
        ws = ld.indic_words(c) if indic else [w for w in (norm(x) for x in re.findall(r"[^\W\d_]+", c)) if w]
        if ws: out.append(ws)
    return out


def lat_edh():
    return logosyll([[ld.norm_latin(w) for w in t if ld.norm_latin(w)] for t in _jl("latin_edh.jsonl")])


def lat_cae():
    t = ld._gutenberg_body(RAW / "caesar.txt") if hasattr(ld, "_gutenberg_body") else open(RAW / "caesar.txt").read()
    t = t.replace("\n", " ")
    return logosyll(_clauses(t, norm=ld.norm_latin, seps=r"[.,;:!?()\[\]\"]"))


def fin_kal():
    lines = [l.strip() for l in open(RAW / "kalevala.txt", encoding="utf-8") if l.strip()]
    wt = [[w for w in (ld.norm_finnic(x) for x in re.findall(r"[^\W\d_]+", l)) if w] for l in lines]
    return logosyll([w for w in wt if w])


def _wiki(name):
    lines = [l for l in open(RAW / name, encoding="utf-8") if not l.startswith(("{", "|", "[", "=", "*", "<"))]
    return logosyll(_clauses(" ".join(lines), indic=True))


def san_wiki(): return _wiki("wiki_sa.txt")
def tam_wiki(): return _wiki("wiki_ta.txt")


# ---------------- real codes ----------------
def heraldry(): return _jl("heraldry.jsonl")
def khipu(): return _jl("khipu.jsonl")
def proto_elamite(): return _jl("proto_elamite.jsonl")
def indus_bigram(): return _jl("indus_bigram.jsonl")


def icd10():
    out = []
    for row in csv.reader(open(HERE / "ext/icd/codes.csv", encoding="utf-8", errors="ignore")):
        if len(row) > 2 and row[2]:
            out.append(list(row[2]))
    return out


# ---------------- synthetic codes ----------------
def plates(n=20000, seed=1):
    rng = random.Random(seed)
    letters = "ABCDEFGHJKLMNPRSTUVWXYZ"
    states = ["MH", "UP", "TN", "KA", "DL", "GJ", "RJ", "WB", "AP", "TS", "KL", "MP", "HR", "PB", "BR", "OD",
              "AS", "JH", "CG", "UK", "HP", "JK", "GA", "TR", "ML", "MN", "NL", "AR", "MZ", "SK", "CH", "PY"]
    sw = [1 / (i + 1) ** 0.8 for i in range(len(states))]
    ndist = {s: rng.randint(5, 99) for s in states}
    out = []
    for _ in range(n):
        s = rng.choices(states, sw)[0]
        d = rng.randint(1, ndist[s])
        ser = "".join(rng.choice(letters) for _ in range(rng.choice([1, 2, 2, 2])))
        num = rng.randint(1, 9999)
        out.append(list(s) + list(f"{d:02d}") + list(ser) + list(str(num)))
    return out


def _zipf_choice(rng, vocab, a=1.0):
    w = [1 / (i + 1) ** a for i in range(len(vocab))]
    return rng.choices(vocab, w)[0]


def slot(n=6000, seed=2):
    """Slot-independent code: 5 slots, disjoint vocabularies, each optional, independent choices."""
    rng = random.Random(seed)
    sizes = [15, 120, 150, 60, 10]; probs = [0.5, 0.9, 0.8, 0.65, 0.7]
    vocab = [[f"S{k}_{i}" for i in range(m)] for k, m in enumerate(sizes)]
    out = []
    for _ in range(n):
        t = []
        for k in range(5):
            if rng.random() < probs[k]:
                t.append(_zipf_choice(rng, vocab[k], 1.0))
                if k in (1, 2) and rng.random() < 0.5:   # second filler in open slots, independent
                    t.append(_zipf_choice(rng, vocab[k], 1.0))
        if t: out.append(t)
    return out


class _PYUrn:
    """Finite-pool Pitman-Yor urn: new types beyond the pool redirect to existing ones."""
    def __init__(self, rng, prefix, pool, d=0.5, theta=8.0):
        self.rng, self.prefix, self.pool, self.d, self.theta = rng, prefix, pool, d, theta
        self.counts = []

    def draw(self):
        n = sum(self.counts); K = len(self.counts)
        p_new = (self.theta + self.d * K) / (self.theta + n) if n else 1.0
        if self.rng.random() < p_new and K < self.pool:
            self.counts.append(1); return f"{self.prefix}{K}"
        w = [c - self.d for c in self.counts]
        i = self.rng.choices(range(K), w)[0]; self.counts[i] += 1
        return f"{self.prefix}{i}"


def sigil(n=3000, seed=3):
    """Rebuild of SIGIL (Raghavendra 2026, arXiv 2608.02999) from its published description:
    optional opener / dedication / office / ledger / terminal blocks; region-specific patrons and
    slot conventions; PY urns for deities, epithets, guilds, commodities; deity epithet licences;
    tallies, emphatic doubling, issue marks before the last primary sign, ligatures for pairs seen
    >= 25 times in the first 1200 texts (p=0.25). Exact urn parameters are not published."""
    rng = random.Random(seed)
    regions = [0.38, 0.27, 0.20, 0.15]
    deity = _PYUrn(rng, "DE", 70); guild = _PYUrn(rng, "GU", 80); comm = _PYUrn(rng, "CO", 90)
    epi = _PYUrn(rng, "EP", 90)
    openers = [f"OP{i}" for i in range(12)]; ranks = [f"RK{i}" for i in range(8)]
    tallies = [f"TA{i}" for i in range(1, 10)]; terms = [f"TE{i}" for i in range(5)]
    issue = [f"IS{i}" for i in range(20)]
    licences = {}
    reg_conf = []
    for r in range(4):
        order = ["ded", "off", "led"]; rng.shuffle(order)
        reg_conf.append(dict(order=order, patron=f"DE{r}", op=rng.sample(openers, 4),
                             term=rng.sample(terms, 2), p_open=rng.uniform(0.35, 0.6)))
    texts = []
    for ti in range(n):
        r = rng.choices(range(4), regions)[0]; c = reg_conf[r]
        blocks = {}
        if rng.random() < c["p_open"]:
            blocks["op"] = [rng.choice(c["op"]) if rng.random() < 0.7 else rng.choice(openers)]
        if rng.random() < 0.75:
            d = c["patron"] if rng.random() < 0.3 else deity.draw()
            if d not in licences:
                k = rng.choices([1, 2, 3, 4, 5], [105, 65, 26, 18, 27])[0]
                licences[d] = [epi.draw() for _ in range(k)]
            b = [d]
            if rng.random() < 0.05: b.append(d)
            if rng.random() < 0.65: b.append(rng.choice(licences[d]))
            blocks["ded"] = b
        if rng.random() < 0.65:
            b = [guild.draw()]
            if rng.random() < 0.4: b.append(_zipf_choice(rng, ranks))
            blocks["off"] = b
        if rng.random() < 0.6:
            b = []
            if rng.random() < 0.45: b.append(_zipf_choice(rng, tallies, 1.2))
            co = comm.draw(); b.append(co)
            if rng.random() < 0.05: b.append(co)
            blocks["led"] = b
        mid = [x for x in c["order"] if x in blocks]
        for i in range(len(mid) - 1):
            if rng.random() < 0.06: mid[i], mid[i + 1] = mid[i + 1], mid[i]
        t = blocks.get("op", []) + [s for x in mid for s in blocks[x]]
        if not t or rng.random() < 0.65:
            t.append(rng.choice(c["term"]) if rng.random() < 0.8 else rng.choice(terms))
        if rng.random() < 0.05 and len(t) >= 2:
            t.insert(len(t) - 1, rng.choice(issue))
        texts.append(t)
    # ligatures
    pc = Counter((a, b) for t in texts[:1200] for a, b in zip(t, t[1:]))
    elig = {p for p, k in pc.items() if k >= 25}
    out = texts[:1200]
    for t in texts[1200:]:
        u, i = [], 0
        while i < len(t):
            if i + 1 < len(t) and (t[i], t[i + 1]) in elig and rng.random() < 0.25:
                u.append(t[i] + "+" + t[i + 1]); i += 2
            else:
                u.append(t[i]); i += 1
        out.append(u)
    return out


CORPORA = {
    "ur3": ("L", ur3), "linb": ("L", linb), "lat_edh": ("L", lat_edh), "lat_cae": ("L", lat_cae),
    "fin_kal": ("L", fin_kal), "san_wiki": ("L", san_wiki), "tam_wiki": ("L", tam_wiki),
    "heraldry": ("C", heraldry), "khipu": ("C", khipu), "icd10": ("C", icd10), "plates": ("C", plates),
    "sigil": ("C", sigil), "slot": ("C", slot), "indus_bigram": ("C*", indus_bigram),
    "proto_elamite": ("?", proto_elamite),
}
for _n in ("lat_edh", "lat_cae", "fin_kal", "san_wiki", "tam_wiki", "ur3", "linb"):
    CORPORA["W_" + _n] = ("L", (lambda n=_n: wordlevel(_words(n))))


def load_all():
    return {k: (lab, f()) for k, (lab, f) in CORPORA.items()}


if __name__ == "__main__":
    import numpy as np
    for k, (lab, X) in load_all().items():
        L = [len(t) for t in X]
        print(f"{k:14s} {lab:3s} texts={len(X):6d} tokens={sum(L):7d} types={len(set(s for t in X for s in t)):6d} "
              f"meanlen={np.mean(L):5.2f} share_len<=14={np.mean(np.array(L) <= 14):.2f}")
    for s in ("dev", "heldout"):
        X = indus(s); print(s, len(X), sum(map(len, X)))
