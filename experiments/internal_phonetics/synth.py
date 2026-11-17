"""Synthetic logo-syllabic seal-legend corpus at Indus size, with switchable spelling
mechanisms (the planted answers for the four tests).

Base language (always on):
  * ~300 logograms (L###), 50 syllabograms (S##, one per sound), openers O0-O4,
    connectives K0/K1, closers C0-C7, slot-optional post-closers P0/P1 and
    slot-optional initial "fish" F0-F3 (stand-ins for M176/M1 and initial fish).
  * 700 words, Zipfian frequency: logogram (55%), logogram+logogram (15%),
    syllabic 2-3 syllables (20%), logogram+syllable (10%). Every word has a sound
    (syllable string) so phonetic complements can be defined.
  * Legend = [F]? [O K?]? word{1,3} [C [P]?]?. Each "person" (legend type) is
    attested on 1+Geom objects; each attestation re-spells it with slot noise
    (fish/post-closer toggled, opener/closer swapped, one word swapped), which
    creates realistic near-copy families and slot-optional indels (the confounds).

Mechanisms (planted, each independently switchable):
  comp : 6 logogram words take a phonetic complement (syllabogram of their last
         sound) written AFTER the logogram with p=0.5.
  homo : 5 sounds get a second, homophonous syllabogram (H##), used with p=0.4 in
         every word containing the sound; 3 logogram words get an alternative
         logogram (A##) used with p=0.4. 8 planted equivalence pairs.
  lig  : 5 within-word sign pairs B C get a ligature sign G#, written in place of
         B C with p=0.35.
  det  : 4 words carry a determinative-marked sign D# that is silent: dropped
         (written as the plain base logogram) with p=0.3 per attestation. 4 other
         marked signs E# are lexical (never dropped). With det off, all 8 are
         lexical.
Returns distinct texts (tuples) and a dict of the planted truth.
"""
import random
from collections import Counter

import numpy as np


def zipf_choice(rng, items, s=1.0):
    w = np.array([1.0 / (i + 1) ** s for i in range(len(items))])
    w /= w.sum()
    return items[rng.choice(len(items), p=w)]


class Synth:
    def __init__(self, seed=0, mech=(), n_target=1675, mult_p=0.90, comp_n=6, comp_rmax=80, comp_p=0.5,
                 homo_p=0.4, lig_p=0.35, det_p=0.3):
        self.cfg = dict(comp_n=comp_n, comp_rmax=comp_rmax, comp_p=comp_p, homo_p=homo_p, lig_p=lig_p, det_p=det_p)
        self.rng = np.random.default_rng(seed)
        self.r = random.Random(seed)
        self.mech = set(mech)
        self.n_target = n_target
        self.mult_p = mult_p
        self._build()

    def _build(self):
        rng, r = self.rng, self.r
        self.logos = ["L%03d" % i for i in range(380)]
        self.sounds = list(range(50))
        self.syl = {k: "S%02d" % k for k in self.sounds}
        words = []
        for i in range(700):
            u = rng.random()
            nsyl = int(rng.integers(1, 4))
            sound = tuple(int(x) for x in rng.choice(50, nsyl))
            if u < 0.55:
                words.append({"type": "logo", "logos": [self.logos[int(rng.integers(380))]], "sound": sound})
            elif u < 0.70:
                words.append({"type": "ll", "logos": [self.logos[int(rng.integers(380))], self.logos[int(rng.integers(380))]],
                              "sound": sound})
            elif u < 0.90:
                s2 = tuple(int(x) for x in rng.choice(50, int(rng.integers(2, 4))))
                words.append({"type": "syl", "logos": [], "sound": s2})
            else:
                words.append({"type": "lsyl", "logos": [self.logos[int(rng.integers(380))]], "sound": sound})
        r.shuffle(words)
        self.words = words  # index = frequency rank
        w = np.array([1.0 / (i + 1) ** 1.05 for i in range(len(words))]); self.wp = w / w.sum()
        self.truth = {}
        # ---- comp
        logo_ranks = [i for i, x in enumerate(words) if x["type"] == "logo" and 4 <= i <= self.cfg["comp_rmax"]]
        self.comp_hosts = logo_ranks[:self.cfg["comp_n"]]
        self.truth["comp"] = [(words[i]["logos"][0], self.syl[words[i]["sound"][-1]]) for i in self.comp_hosts]
        # ---- homo
        snd_count = Counter(s for i, x in enumerate(words) for s in x["sound"] if x["type"] in ("syl", "lsyl"))
        hs = [s for s, _ in snd_count.most_common(25)][5:10]
        self.homo_sounds = {s: "H%02d" % s for s in hs}
        al = [i for i, x in enumerate(words) if x["type"] == "logo" and 10 <= i <= 120 and i not in self.comp_hosts][:3]
        self.alt_logo = {words[i]["logos"][0]: "A%03d" % k for k, i in enumerate(al)}
        self.truth["homo"] = [(self.syl[s], h) for s, h in self.homo_sounds.items()] + list(self.alt_logo.items())
        # ---- lig: pairs inside lsyl / syl / ll words of moderate rank
        pairs = []
        for i, x in enumerate(words[5:200]):
            sp = self._spell_plain(x)
            if len(sp) >= 2:
                bc = (sp[0], sp[1])
                if bc not in pairs and len(set(bc)) == 2:
                    pairs.append(bc)
            if len(pairs) == 5:
                break
        self.lig = {bc: "G%d" % k for k, bc in enumerate(pairs)}
        self.truth["lig"] = [(g, bc) for bc, g in self.lig.items()]
        # ---- det
        cand = [i for i, x in enumerate(words) if x["type"] == "logo" and 8 <= i <= 150
                and i not in self.comp_hosts and i not in al]
        self.det_silent = {}  # word index -> (marked sign, base logo)
        self.det_lex = {}
        for k, i in enumerate(cand[:8]):
            base = words[i]["logos"][0]
            # ensure the base logogram also exists as another word (so substitution is possible)
            j = cand[8 + k] if 8 + k < len(cand) else cand[-1]
            words[j] = {"type": "logo", "logos": [base], "sound": words[j]["sound"]}
            if k < 4:
                self.det_silent[i] = ("D%d" % k, base)
            else:
                self.det_lex[i] = ("E%d" % k, base)
        self.truth["det_silent"] = [(m, b) for m, b in self.det_silent.values()]
        self.truth["det_lex"] = [(m, b) for m, b in self.det_lex.values()]

    def _spell_plain(self, x):
        if x["type"] in ("logo", "ll"):
            return list(x["logos"])
        if x["type"] == "syl":
            return [self.syl[s] for s in x["sound"]]
        return list(x["logos"]) + [self.syl[x["sound"][-1]]]

    def spell(self, wi):
        rng, x = self.rng, self.words[wi]
        if wi in self.det_silent:
            m, b = self.det_silent[wi]
            if "det" in self.mech and rng.random() < self.cfg["det_p"]:
                out = [b]
            else:
                out = [m]
        elif wi in self.det_lex:
            out = [self.det_lex[wi][0]]
        elif x["type"] in ("logo", "ll"):
            out = list(x["logos"])
        elif x["type"] == "syl":
            out = [self.syl[s] for s in x["sound"]]
        else:
            out = list(x["logos"]) + [self.syl[x["sound"][-1]]]
        if "homo" in self.mech:
            o2 = []
            for s in out:
                if s.startswith("S") and int(s[1:]) in self.homo_sounds and rng.random() < self.cfg["homo_p"]:
                    o2.append(self.homo_sounds[int(s[1:])])
                elif s in self.alt_logo and rng.random() < self.cfg["homo_p"]:
                    o2.append(self.alt_logo[s])
                else:
                    o2.append(s)
            out = o2
        if "comp" in self.mech and wi in self.comp_hosts and rng.random() < self.cfg["comp_p"]:
            out = out + [self.syl[x["sound"][-1]]]
        if "lig" in self.mech and len(out) >= 2:
            o2, i = [], 0
            while i < len(out):
                if i + 1 < len(out) and (out[i], out[i + 1]) in self.lig and rng.random() < self.cfg["lig_p"]:
                    o2.append(self.lig[(out[i], out[i + 1])]); i += 2
                else:
                    o2.append(out[i]); i += 1
            out = o2
        return out

    def person(self):
        rng = self.rng
        p = {}
        p["fish"] = ("F%d" % int(rng.integers(4))) if rng.random() < 0.15 else None
        p["opener"] = zipf_choice(rng, ["O0", "O1", "O2", "O3", "O4"]) if rng.random() < 0.35 else None
        p["conn"] = ("K0" if rng.random() < 0.8 else "K1") if (p["opener"] and rng.random() < 0.8) else None
        n = 1 + int(rng.choice(3, p=[0.45, 0.38, 0.17]))
        p["words"] = [int(rng.choice(len(self.words), p=self.wp)) for _ in range(n)]
        p["closer"] = zipf_choice(rng, ["C%d" % i for i in range(8)], 1.3) if rng.random() < 0.72 else None
        p["post"] = (("P0" if rng.random() < 0.6 else "P1") if (p["closer"] and rng.random() < 0.12) else None)
        return p

    def attest(self, p):
        rng = self.rng
        q = dict(p); q["words"] = list(p["words"])
        if rng.random() < 0.25:
            q["fish"] = None if q["fish"] else "F%d" % int(rng.integers(4))
        if rng.random() < 0.25 and q["closer"]:
            q["post"] = None if q["post"] else ("P0" if rng.random() < 0.6 else "P1")
        if q["opener"] and rng.random() < 0.15:
            q["opener"] = zipf_choice(rng, ["O0", "O1", "O2", "O3", "O4"])
        if q["closer"] and rng.random() < 0.12:
            q["closer"] = zipf_choice(rng, ["C%d" % i for i in range(8)], 1.3)
        if rng.random() < 0.12:
            k = int(rng.integers(len(q["words"])))
            q["words"][k] = int(rng.choice(len(self.words), p=self.wp))
        t = []
        if q["fish"]: t.append(q["fish"])
        if q["opener"]:
            t.append(q["opener"])
            if q["conn"]: t.append(q["conn"])
        for w in q["words"]:
            t += self.spell(w)
        if q["closer"]:
            t.append(q["closer"])
            if q["post"]: t.append(q["post"])
        return tuple(t)

    def corpus(self, n=None):
        n = n or self.n_target
        seen, out = set(), []
        while len(out) < n:
            p = self.person()
            r = 1 + int(self.rng.geometric(self.mult_p)) - 1
            for _ in range(r):
                t = self.attest(p)
                if t not in seen:
                    seen.add(t); out.append(t)
        return out[:n]


SLOT_OPTIONAL = {"P0", "P1"}  # plus initial F*


def synth_excluded(x, pos):
    return x in SLOT_OPTIONAL or (x.startswith("F") and pos == 0)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    from common import edit1_pairs, load_split
    D, _ = load_split()
    s, i = edit1_pairs(D, 3)
    nb = lambda T: len({a for a, b, _ in edit1_pairs(T, 3)[0]} | {b for a, b, _ in edit1_pairs(T, 3)[0]}
                       | {a for a, b, _ in edit1_pairs(T, 2)[1]} | {b for a, b, _ in edit1_pairs(T, 2)[1]}) / len(T)
    print("Indus dev: n=%d len=%.2f types=%d subs/text=%.3f indels/text=%.3f nb-share=%.3f" % (
        len(D), np.mean([len(t) for t in D]), len({x for t in D for x in t}), len(s) / len(D),
        len(edit1_pairs(D, 2)[1]) / len(D), nb(D)))
    for mp in [0.85, 0.9]:
        for mech in [(), ("comp", "homo", "lig", "det")]:
            T = Synth(1, mech, mult_p=mp).corpus()
            s, i = edit1_pairs(T, 3)
            print("synth mult_p=%.2f %s: len=%.2f types=%d subs/text=%.3f indels/text=%.3f nb-share=%.3f" % (
                mp, "+".join(mech) or "none", np.mean([len(t) for t in T]), len({x for t in T for x in t}),
                len(s) / len(T), len(edit1_pairs(T, 2)[1]) / len(T), nb(T)))
