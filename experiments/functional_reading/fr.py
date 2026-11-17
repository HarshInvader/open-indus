"""Functional/semantic grammar for Indus texts (no phonetics).

A probabilistic finite-state grammar over FUNCTIONAL ROLES. Each sign may only be emitted by
the roles its lexicon entry allows (hand-assigned from other teams' evidence, or dev-derived
positional class, else 'unknown noun'). Transition probabilities are learned on DEV only by EM;
transitions not allowed by the template are structural zeros, so a text either parses or not.

Roles (one letter each):
  O opener          C connective (M99/M123)    S short-stroke numeral   T tall-stroke numeral
  U unit/measure    F fish-class noun          B bracketed fish (closer slot)
  N unknown noun    I pre-closer title element J closer (jar etc.)      P post-closer clitic
Run from repo root. Imported by the experiment scripts in this folder.
"""
import json, sys, math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa

OUT = ROOT / "experiments" / "functional_reading"
SRC = ROOT / "sources" / "shaunmortal_indus" / "data"

STROKES = json.load(open(SRC / "stroke_signs.json"))
SHORT = {f"M{k}": v for k, v in STROKES["short"].items() if k not in ("99", "101")}
TALL = {f"M{k}": v for k, v in STROKES["tall"].items()}
BRIDGE = json.load(open(SRC / "bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}

ROLES = list("OCSTUFBNIJP")
RI = {r: i for i, r in enumerate(ROLES)}
ROLE_NAME = {"O": "OPENER", "C": "CONNECTIVE", "S": "NUMERAL(short)", "T": "NUMERAL(tall)",
             "U": "UNIT/MEASURE", "F": "FISH-CLASS NOUN", "B": "BRACKETED-FISH CLOSER",
             "N": "NOUN", "I": "TITLE ELEMENT", "J": "CLOSER", "P": "POST-CLOSER CLITIC"}

FISH_PLAIN = ["M59", "M61", "M62", "M63", "M64", "M65", "M67", "M69", "M70", "M72", "M74", "M75"]
FISH_BRACK = ["M60", "M66", "M68", "M71", "M73"]
FOREIGN_SITES = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan",
                 "Hajar", "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah",
                 "Tell Umma", "Dilmun", "Kalba", "Gonur", "Gonur Depe", "Altyn Depe", "Shortughai"}

# ---------------------------------------------------------------- hand lexicon (evidence-based)
# sign -> (allowed roles, meaning category, evidence, grade of role, grade of meaning)
HAND = {
    "M267": ("O", "opening-formula word", "initial 76% dev; K=3 opener class replicated held-out+ICIT (structure §3); M267-M99 top segment", "A", "-"),
    "M391": ("O", "opening-formula word (seal register)", "opener class (structure §3); seal-enriched, replicated ICIT W820 (context Q2)", "A", "B"),
    "M293": ("ON", "opening-formula word (with M123)", "initial 57% dev; M293-M123(-M343) formula (structure §4)", "B", "-"),
    "M150": ("O", "opening-formula word (with M123)", "initial 86% dev; M150-M123 segment", "B", "-"),
    "M99": ("C", "connective after opener (personal-seal grammar)", "91% medial, after M267/M391; never dropped (phonetic_grid §5); seal-enriched, absent from copper/tablets, replicated ICIT (context Q2)", "A", "B"),
    "M123": ("CN", "connective after opener", "92% medial; follows M293 42x, M150 32x in dev; HMM connective slot (novel_methods exp2)", "B", "-"),
    "M328": ("UN", "measure/commodity unit (docket formula)", "counted only by tall strokes (shaunmortal F2/F5/F8); tablet reverses F15; seal-depleted, tablet-enriched (context Q2)", "A", "B"),
    "M190": ("U", "measure word of the short-stroke system?", "preceded by a numeral 95% (shaunmortal F2); 12/14 after M102 in dev", "B", "C"),
    "M342": ("J", "closing word (jar); marks title/office-type legends", "final 72% dev, also in L-R texts (structure §1); texts with jar recur across cities, replicated (context Q3)", "A", "B"),
    "M176": ("P", "document-type clitic (tablet/rod register)", "optional post-closer (novel_methods exp1, phonetic_grid); rods/tablets enriched, seals 0.2x, replicated ICIT W400 (context Q2)", "A", "B"),
    "M1": ("PJ", "suffix after the closer", "after M342 in 52/66 dev; closer class", "A", "-"),
    "M211": ("J", "closer of a title block", "final 80% dev; tall-stroke counted (F8); closes title block M59-M336-M89 (F28)", "A", "B"),
    "M169": ("JN", "closer (copper-tablet / round-seal register)", "final 68%; copper-enriched replicated ICIT W407 (context Q2); round-seal closer (F19)", "A", "B"),
    "M162": ("JN", "closer-class word (counted by short strokes)", "final 42%; counted by short strokes (F2)", "B", "-"),
    "M15": ("J", "closer-class word", "final 70% dev", "B", "-"),
    "M254": ("J", "closer of M216/M222/M226 formulae", "final 82%; follows M216/M222/M226", "B", "-"),
    "M12": ("JP", "closer/post-closer", "final 88% dev; probable allograph M14 (structure §2c)", "B", "-"),
    "M347": ("I", "title element before the jar", "followed by M342 in 63/69 dev; M347-M342 top segment", "B", "C"),
    "M8": ("I", "title element before the jar", "followed by M342 in 51/59 dev", "B", "C"),
    "M343": ("N", "handled-jar noun (distinct from the jar closer)", "mid-text 86%, contexts at null vs M342 (novel_methods exp3); square only (F19); smaller seals (F12, suggestive)", "A", "C"),
    "M344": ("N", "jar+2 strokes: medial name element", "mid-text (F16); not a jar variant (novel_methods exp3)", "A", "-"),
    "M345": ("N", "jar+3 strokes: medial name element", "mid-text (F16); not a jar variant (novel_methods exp3)", "A", "-"),
    "M403": ("N", "noun bound to M103 (3 as 2-over-1)", "M103->M403 27/28 (shaunmortal F7, replicated per site)", "A", "-"),
    "M407": ("N", "copper-tablet register element", "copper 9 vs 0.8 exp, replicated ICIT W845 (context Q2)", "B", "B"),
    "M18": ("NO", "copper-tablet register element", "copper-enriched, replicated ICIT W095 (context Q2)", "B", "B"),
    "M387": ("NO", "round-seal-favoured noun", "round seals 3x (F19)", "B", "C"),
    "M362": ("N", "emblem logogram (copper one-sign face)?", "stands where the picture would be on 2-faced copper tablets (context Q2b, n=6)", "C", "C"),
    "M363": ("N", "emblem logogram (copper one-sign face)?", "context Q2b, n=6", "C", "C"),
    "M346": ("N", "emblem logogram (copper one-sign face)?", "context Q2b", "C", "C"),
    "M184": ("N", "emblem logogram (copper one-sign face)?", "context Q2b", "C", "C"),
}
for s in FISH_PLAIN:
    HAND[s] = ("F", "fish-class name element",
               "fish paradigm: M65/67/70/72 swap with M59 in identical frames 10 vs 2.4 (novel_methods exp1/3)",
               "B" if s in ("M59", "M65", "M67", "M70", "M72") else "C", "C")
for s in FISH_BRACK:
    HAND[s] = ("BF", "fish-class element in the closer slot (bracketed fish)",
               "final 60% vs 5% for plain fish; replicated held-out p=0.03 (novel_methods T6)", "B", "C")
for s, v in SHORT.items():
    if s not in HAND:
        HAND[s] = ("S", f"short-stroke numeral {v}",
                   "two stroke systems with complementary heads (shaunmortal F2/F5/F8, ICIT replicated); numeral precedes head",
                   "A", "B")
HAND["M100"] = ("SC", "short-2 variant (not M99)", "look-alike but distinct from M99 (structure §2c)", "C", "-")
HAND["M103"] = ("S", "numeral 3 (2-over-1 layout), bound to M403", "M103->M403 fixed compound (F7)", "A", "B")
for s, v in TALL.items():
    HAND[s] = ("T", f"tall-stroke numeral {v}",
               "tall strokes count M328/M211/M60 only (F2/F8); side-2 docket formula (F15); values 2-3 favoured", "A", "B")

# fixed compounds with an external meaning category (others are discovered on dev)
NAMED_COMPOUNDS = {
    ("M109", "M59"): ("NUMBER-NAME", "6 + fish compound (Parpola 'Pleiades' reading untested)",
                      "12/28 six-stroke tokens followed by fish vs 13% base, p=1e-4, held-out 4/7 (language A2)", "A", "C"),
    ("M336", "M89"): ("TITLE-BLOCK", "title/office block shared across unrelated names",
                      "M59-M336-M89+M211 ends 21 unique names at 5 sites (shaunmortal F28)", "A", "B"),
    ("M51", "M130"): ("TITLE-BLOCK", "title/office block (M51-M130-M149 + jar)", "10 unique names incl. Kalibangan, Rakhigarhi (F28)", "A", "B"),
    ("M249", "M162"): ("TITLE-BLOCK", "title/office block (M249-M162/M169 + jar)", "M249-M162-M342 / M249-M169-M342 segments (structure §4)", "B", "C"),
    ("M249", "M169"): ("TITLE-BLOCK", "title/office block", "structure §4", "B", "C"),
    ("M249", "M161"): ("TITLE-BLOCK", "title/office block (M59-M249-M161 + jar), reaches Kish", "F28", "B", "B"),
    ("M103", "M403"): ("NUMBER-NAME", "fixed numeral compound 3(2-over-1)+M403", "F7", "A", "-"),
    ("M112", "M194"): ("NUMBER-NAME", "7(4-over-3)+M194, copper-tablet formula", "F7 (copper 10/10)", "B", "B"),
    ("M112", "M197"): ("NUMBER-NAME", "7(4-over-3)+M197", "F7", "B", "-"),
    ("M97", "M25"): ("REGISTER", "copper-tablet formula", "context Q2, replicated ICIT W001-W142", "B", "B"),
    ("M252", "M97"): ("REGISTER", "copper-tablet formula", "context Q2, replicated", "B", "B"),
    ("M407", "M169"): ("REGISTER", "copper-tablet closing formula", "context Q2", "B", "B"),
    ("M342", "M176"): ("REGISTER", "tablet/rod ending (jar + document-type clitic)", "rods 9 vs 0.5; ICIT tablets 99 vs 59 (context Q2)", "A", "B"),
}

GRADE_W = {"A": 1.0, "B": 0.7, "C": 0.4, "D": 0.3, "-": 0.1}


def clean_runs(t):
    """Lines/runs of a text. Returns list of (run, start_open, end_open) where *_open marks a break edge."""
    out, cur, prev_break = [], [], False
    seq = t["seq"] if isinstance(t, dict) else t
    for s in list(seq) + ["|"]:
        if s in ("|", "#"):
            if cur:
                out.append((cur, prev_break, s == "#"))
            cur = []
            prev_break = (s == "#")
        else:
            cur.append(s)
    return out


def has_break(t):
    return "#" in t["seq"]


# ---------------------------------------------------------------- dev-derived lexicon
def positional_profile(texts):
    pos = defaultdict(Counter); prev = defaultdict(Counter); nxt = defaultdict(Counter); ntext = Counter()
    for t in texts:
        for r in runs(t["seq"]):
            for i, s in enumerate(r):
                k = "A" if len(r) == 1 else "I" if i == 0 else "F" if i == len(r) - 1 else "M"
                pos[s][k] += 1
                if i > 0: prev[s][r[i - 1]] += 1
                if i < len(r) - 1: nxt[s][r[i + 1]] += 1
        for s in set(x for x in t["seq"] if x not in "|#"):
            ntext[s] += 1
    return pos, prev, nxt, ntext


def build_lexicon(dev, thr=None):
    thr = thr or dict(n=5, init_only=0.6, init_mix=0.4, fin_only=0.7, fin_mix=0.45, post=0.5, prejar=0.5)
    pos, prev, nxt, ntext = positional_profile(dev)
    lex = {}
    closers = {s for s, v in HAND.items() if "J" in v[0]}
    for s in pos:
        c = pos[s]; tot = sum(c.values())
        if s in HAND:
            roles, cat, ev, g, gm = HAND[s]
            lex[s] = dict(roles=set(roles), category=cat, evidence=ev, grade=g, mgrade=gm, source="hand")
            continue
        if ntext[s] < thr["n"]:
            lex[s] = dict(roles={"N"}, category="unknown noun", evidence=f"rare in dev ({ntext[s]} texts)",
                          grade="-", mgrade="-", source="default")
            continue
        pi = (c["I"]) / tot; pf = (c["F"]) / tot
        pp = sum(v for k, v in prev[s].items() if k in closers) / max(1, sum(prev[s].values()))
        pj = nxt[s]["M342"] / max(1, sum(nxt[s].values()))
        roles, cat = {"N"}, "unknown noun"
        ev = f"dev n={ntext[s]} texts; initial {pi:.2f} final {pf:.2f}"
        if pp >= thr["post"] and pf >= 0.5:
            roles, cat = {"P", "J"}, "post-closer element (unknown meaning)"; ev += f"; after closer {pp:.2f}"
        elif pf >= thr["fin_only"]:
            roles, cat = {"J"}, "closer-class word (unknown meaning)"
        elif pf >= thr["fin_mix"]:
            roles, cat = {"J", "N"}, "closer-class/core noun (unknown meaning)"
        elif pj >= thr["prejar"] and sum(nxt[s].values()) >= 5:
            roles, cat = {"I", "N"}, "pre-jar title element? (unknown meaning)"; ev += f"; before jar {pj:.2f}"
        elif pi >= thr["init_only"]:
            roles, cat = {"O"}, "opener-class word (unknown meaning)"
        elif pi >= thr["init_mix"]:
            roles, cat = {"O", "N"}, "opener-class/core noun (unknown meaning)"
        lex[s] = dict(roles=roles, category=cat, evidence=ev, grade="C" if cat != "unknown noun" else "-",
                      mgrade="-", source="dev-positional")
    return lex


def discover_compounds(dev, min_n=6, min_p=0.5):
    big = Counter(); uni = Counter()
    for t in dev:
        for r in runs(t["seq"]):
            uni.update(r)
            for a, b in zip(r, r[1:]):
                big[(a, b)] += 1
    comp = {}
    for (a, b), n in big.items():
        if n >= min_n and max(n / uni[a], n / uni[b]) >= min_p:
            comp[(a, b)] = n
    for k in NAMED_COMPOUNDS:
        comp.setdefault(k, big.get(k, 0))
    return comp


# ---------------------------------------------------------------- the grammar (PFSA)
FROZEN_EDGES = [("N", "C"), ("N", "P")]   # chosen by the dev design step (g1_design_dev.py), then frozen here


def allowed_matrix(variant="final", extra=None):
    A = {r: set() for r in ROLES + ["^"]}
    A["^"] = set("OSTUFNIJB")
    A["O"] = set("OCSTFNIJU") | {"$"}
    A["C"] = set("CSTFNIJBO")
    A["S"] = set("SFTNIUJBC")
    A["T"] = set("STFNIUJB")
    A["U"] = set("USTFNIJP") | {"$"}
    A["F"] = set("SFTNIUJB") | {"$"}
    A["N"] = set("SFTNIUJB") | {"$"}
    A["I"] = set("ISTFNJ") | {"$"}
    A["J"] = set("JP") | {"$"}
    A["B"] = set("PJ") | {"$"}
    A["P"] = set("P") | {"$"}
    if variant == "strict":
        return A
    edges = FROZEN_EDGES if extra is None else extra
    for a, b in edges:
        A[a].add(b)
    return A


class Grammar:
    def __init__(self, lex, variant="final", alpha=0.5, extra=None):
        self.lex = lex; self.variant = variant; self.alpha = alpha
        self.A = allowed_matrix(variant, extra)
        K = len(ROLES)
        self.start = np.zeros(K); self.trans = np.zeros((K, K)); self.end = np.zeros(K)
        self.mask_start = np.array([r in self.A["^"] for r in ROLES], float)
        self.mask_trans = np.array([[b in self.A[a] for b in ROLES] for a in ROLES], float)
        self.mask_end = np.array([("$" in self.A[a]) for a in ROLES], float)
        self.emit = defaultdict(lambda: np.zeros(K))   # sign -> P(sign|role) vector
        self.role_tot = np.ones(K)

    def allowed(self, s):
        e = self.lex.get(s)
        return e["roles"] if e else {"N"}

    def emis_vec(self, s):
        v = np.zeros(len(ROLES))
        for r in self.allowed(s):
            k = RI[r]
            v[k] = (self.ecount.get((s, r), 0) + self.alpha) / (self.role_tot[k] + self.alpha * self.vocab_per_role[k])
        return v

    def fit(self, dev, iters=15):
        lines = [r for t in dev if not has_break(t) for (r, a, b) in clean_runs(t)]
        self.vocab = sorted({s for r in lines for s in r})
        K = len(ROLES)
        vpr = np.ones(K)
        for s in self.vocab:
            for r in self.allowed(s): vpr[RI[r]] += 1
        self.vocab_per_role = vpr + 50  # room for unseen signs
        # init uniform over allowed
        self.start = self.mask_start / self.mask_start.sum()
        self.trans = self.mask_trans / np.maximum(1, self.mask_trans.sum(1, keepdims=True))
        self.end = self.mask_end * 0.3
        self.ecount = {}; self.role_tot = np.ones(K)
        for it in range(iters):
            cs = np.zeros(K); ct = np.zeros((K, K)); ce = np.zeros(K); ec = Counter(); rt = np.zeros(K)
            for r in lines:
                g = self._fb(r)
                if g is None: continue
                gam, xi = g
                cs += gam[0]; ce += gam[-1]; ct += xi
                for i, s in enumerate(r):
                    for k in np.nonzero(gam[i])[0]:
                        ec[(s, ROLES[k])] += gam[i][k]; rt[k] += gam[i][k]
            self.ecount = ec; self.role_tot = rt + 1e-9
            sm = 0.1
            self.start = (cs + sm) * self.mask_start; self.start /= self.start.sum()
            out_tot = ct.sum(1) + ce
            self.trans = (ct + sm) * self.mask_trans
            self.end = (ce + sm) * self.mask_end
            z = self.trans.sum(1) + self.end
            self.trans /= z[:, None]; self.end /= z
        self.n_lines_fit = len(lines)
        return self

    def _fb(self, r, open_start=False, open_end=False):
        E = np.array([self.emis_vec(s) for s in r])
        st = np.ones(len(ROLES)) / len(ROLES) if open_start else self.start
        en = np.ones(len(ROLES)) if open_end else self.end
        n = len(r); K = len(ROLES)
        a = np.zeros((n, K)); c = np.zeros(n)
        a[0] = st * E[0]; c[0] = a[0].sum()
        if c[0] == 0: return None
        a[0] /= c[0]
        for i in range(1, n):
            a[i] = (a[i - 1] @ self.trans) * E[i]; c[i] = a[i].sum()
            if c[i] == 0: return None
            a[i] /= c[i]
        fin = (a[-1] * en).sum()
        if fin == 0: return None
        b = np.zeros((n, K)); b[-1] = en / fin
        for i in range(n - 2, -1, -1):
            b[i] = (self.trans @ (E[i + 1] * b[i + 1])) / c[i + 1]
        gam = a * b; gam /= gam.sum(1, keepdims=True)
        xi = np.zeros((K, K))
        for i in range(n - 1):
            m = a[i][:, None] * self.trans * (E[i + 1] * b[i + 1])[None, :] / c[i + 1]
            s = m.sum()
            if s > 0: xi += m / s
        return gam, xi

    def logprob(self, r, open_start=False, open_end=False):
        """log2 P(run) under the grammar; -inf if it does not parse."""
        st = np.ones(len(ROLES)) / len(ROLES) if open_start else self.start
        en = np.ones(len(ROLES)) if open_end else self.end
        a = st * self.emis_vec(r[0]); lp = 0.0
        for s in r[1:]:
            z = a.sum()
            if z == 0: return -np.inf
            lp += math.log2(z); a = (a / z) @ self.trans * self.emis_vec(s)
        z = (a * en).sum()
        if z == 0: return -np.inf
        return lp + math.log2(z)

    def viterbi(self, r, open_start=False, open_end=False):
        st = np.ones(len(ROLES)) / len(ROLES) if open_start else self.start
        en = np.ones(len(ROLES)) if open_end else self.end
        with np.errstate(divide="ignore"):
            lT = np.log(self.trans); lE = [np.log(self.emis_vec(s)) for s in r]
            d = np.log(st) + lE[0]; back = []
            for i in range(1, len(r)):
                m = d[:, None] + lT
                back.append(m.argmax(0)); d = m.max(0) + lE[i]
            d = d + np.log(en)
        if not np.isfinite(d.max()):
            return None
        k = int(d.argmax()); path = [k]
        for bk in reversed(back):
            k = int(bk[k]); path.append(k)
        return [ROLES[k] for k in reversed(path)]

    def parse_text(self, t):
        """Return list of lines: (signs, roles or None, start_open, end_open); and accepted flag."""
        lines = []
        ok = True
        for (r, so, eo) in clean_runs(t):
            p = self.viterbi(r, so, eo)
            if p is None:
                ok = False
                p = self.viterbi(r, True, True)  # relaxed fallback for display only
            lines.append((r, p, so, eo))
        return lines, ok

    def robust_parse(self, r, so=False, eo=False):
        """Viterbi roles; if the line does not parse, cut it greedily into the longest parsable pieces
        (pieces after a cut get an open start). Returns (roles, cut_positions)."""
        p = self.viterbi(r, so, eo)
        if p is not None:
            return p, []
        roles, cuts, i, first = [], [], 0, True
        while i < len(r):
            for j in range(len(r), i, -1):
                q = self.viterbi(r[i:j], so if first else True, eo if j == len(r) else True)
                if q is not None:
                    break
            if q is None:
                q, j = ["N"], i + 1
            if not first: cuts.append(i)
            roles += q; i = j; first = False
        return roles, cuts

    def accepts(self, t, relax_breaks=True):
        for (r, so, eo) in clean_runs(t):
            if not np.isfinite(self.logprob(r, so and relax_breaks, eo and relax_breaks)):
                return False
        return True


# ---------------------------------------------------------------- bigram baseline (interpolated KN)
class KNBigram:
    def __init__(self, d=0.75):
        self.d = d

    def fit(self, seqs):
        self.big = Counter(); self.ctx = Counter(); self.cont = defaultdict(set); self.fol = defaultdict(set)
        for r in seqs:
            r = ["<s>"] + list(r) + ["</s>"]
            for a, b in zip(r, r[1:]):
                self.big[(a, b)] += 1; self.ctx[a] += 1; self.cont[b].add(a); self.fol[a].add(b)
        self.nbt = len(self.big)
        self.V = len(self.cont) + 1
        return self

    def p(self, b, a):
        pc = (len(self.cont.get(b, ())) + 0.5) / (self.nbt + 0.5 * self.V)
        ca = self.ctx.get(a, 0)
        if ca == 0: return pc
        lam = self.d * len(self.fol[a]) / ca
        return max(self.big.get((a, b), 0) - self.d, 0) / ca + lam * pc

    def logprob(self, r):
        r = ["<s>"] + list(r) + ["</s>"]
        return sum(math.log2(self.p(b, a)) for a, b in zip(r, r[1:]))


# ---------------------------------------------------------------- reading layer
def compound_at(signs, i, comps):
    """Longest dev compound starting at i (2 or 3 signs). Returns length (1 if none)."""
    if i + 2 < len(signs) and (signs[i], signs[i + 1]) in comps and (signs[i + 1], signs[i + 2]) in comps:
        return 3
    if i + 1 < len(signs) and (signs[i], signs[i + 1]) in comps:
        return 2
    return 1


def sign_label(s, lex):
    e = lex.get(s)
    return e["category"] if e else "unknown noun (unseen in dev)"


def read_line(signs, roles, lex, comps):
    """Group a role-tagged line into constituents: list of dicts(label, signs, gloss, grade)."""
    out = []; i = 0; n = len(signs)
    while i < n:
        s, r = signs[i], roles[i]
        two = tuple(signs[i:i + 2])
        if two in NAMED_COMPOUNDS and not (two == ("M342", "M176")):
            kind, cat, ev, g, gm = NAMED_COMPOUNDS[two]
            L = 2
            if two in (("M336", "M89"), ("M51", "M130")) and i + 2 < n and signs[i + 2] in ("M211", "M149"):
                L = 3
            out.append(dict(label=kind, signs=signs[i:i + L], gloss=cat, grade=g)); i += L; continue
        if r == "O":
            j = i + 1
            while j < n and roles[j] in ("O", "C") and j - i < 3:
                j += 1
            out.append(dict(label="OPENER", signs=signs[i:j], gloss="opening formula" + (" + connective" if "C" in roles[i:j] else ""),
                            grade=lex.get(s, {}).get("grade", "-"))); i = j; continue
        if r in ("S", "T"):
            j = i + 1
            while j < n and roles[j] in ("S", "T") and tuple(signs[j:j + 2]) not in NAMED_COMPOUNDS:
                j += 1
            if j < n and tuple(signs[j:j + 2]) in NAMED_COMPOUNDS:
                vals = "+".join(str(TALL.get(signs[k]) or SHORT.get(signs[k]) or "?") for k in range(i, j))
                out.append(dict(label="NUMERAL", signs=signs[i:j], gloss=f"number {vals} qualifying the next unit", grade="A")); i = j; continue
            if j < n and roles[j] in ("F", "N", "U", "I", "J", "B"):
                head = signs[j]; hr = roles[j]
                if hr == "U":
                    lab, gl = "COUNT+MEASURE", "number + measure/commodity unit (docket formula)"
                elif hr == "F":
                    lab, gl = "NUMBER-NAME", "number + fish-class name element"
                elif hr in ("J", "B"):
                    lab, gl = "NUMBER+CLOSER", "number + closer-class word"
                else:
                    lab, gl = "NUMBER+NOUN", "number + noun (counted or name element)"
                sys_ = "tall" if all(roles[k] == "T" for k in range(i, j)) else "short" if all(roles[k] == "S" for k in range(i, j)) else "mixed"
                gl = f"{gl}; {sys_}-stroke value {'+'.join(str((TALL.get(signs[k]) or SHORT.get(signs[k]) or '?')) for k in range(i, j))}"
                out.append(dict(label=lab, signs=signs[i:j + 1], gloss=gl, grade="A")); i = j + 1; continue
            out.append(dict(label="NUMERAL", signs=signs[i:j], gloss="bare number (no head)", grade="A")); i = j; continue
        L = compound_at(signs, i, comps)
        if L > 1 and all(roles[k] in "NFI" for k in range(i, i + L)):
            out.append(dict(label="FORMULA", signs=signs[i:i + L], gloss="recurrent fixed unit (dev); meaning unknown", grade="B"))
            i += L; continue
        lab = {"C": "CONNECTIVE", "U": "UNIT/MEASURE", "F": "FISH-NOUN", "B": "BRACKETED-FISH CLOSER", "N": "NOUN",
               "I": "TITLE", "J": "CLOSER", "P": "POST-CLOSER"}[r]
        gl = sign_label(s, lex)
        if s == "M176": lab = "DOC-TYPE CLITIC"
        if s == "M342": lab = "CLOSER(jar)"
        out.append(dict(label=lab, signs=[s], gloss=gl, grade=lex.get(s, {}).get("grade", "-")))
        i += 1
    return out


def fmt_reading(lines_consts):
    parts = []
    for li, cs in enumerate(lines_consts):
        if li: parts.append("||")
        for c in cs:
            parts.append(f"[{c['label']}: {'+'.join(c['signs'])}]")
    return " ".join(parts)


def gloss_text(lines_consts):
    g = []
    for li, cs in enumerate(lines_consts):
        if li: g.append("/ next line:")
        g.append("; ".join(c["gloss"] for c in cs))
    return " ".join(g)


def confidence(signs_roles_lines, lex, accepted):
    ws = []
    for signs, roles in signs_roles_lines:
        for s in signs:
            e = lex.get(s)
            ws.append(GRADE_W[e["grade"]] if e else 0.1)
    c = float(np.mean(ws)) if ws else 0.0
    if not accepted: c *= 0.5
    return c


def bridge_seq(seq):
    """ICIT W-seq -> M-seq through the bridge; unbridged signs become 'OOV:Wxxx'."""
    return [s if s in ("|", "#") else W2M.get(s, "OOV:" + s) for s in seq]


def icit_class(tp):
    if tp.startswith("SEAL"): return "seal"
    if tp in ("TAB:B", "TAB:I") or tp.startswith("TAG"): return "tablet"
    if tp == "TAB:C": return "copper"
    if tp.startswith("POT"): return "pottery"
    return None


def m77_class(ot):
    return {"seal": "seal", "sealing": "tablet", "miniature tablet": "tablet", "copper tablet": "copper",
            "pottery graffito": "pottery"}.get(ot)


def load_model(variant="final"):
    dev, ho = dev_heldout()
    dev_g = [t for t in dev if t["site"] != "West Asian finds"]
    lex = build_lexicon(dev_g)
    comps = discover_compounds(dev_g)
    G = Grammar(lex, variant).fit(dev_g)
    return dev, ho, dev_g, lex, comps, G
