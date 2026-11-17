"""Planted-answer corpora for the one-to-many substitution test.

Base: internal_phonetics' Synth (imported, not edited): Indus-genre seal legends,
~4.5 signs per text, Zipfian words (logogram 55%, logogram+logogram 15%, syllabic
20%, logogram+syllable 10%), openers/connectives/closers/post-closers, near-copy
families calibrated to Indus dev edit-1 neighbour rates (mult_p=0.9).

Planted mechanism "alt" (Maya / Luwian style logogram <-> phonetic spelling):
  a fraction p of LOGOGRAM SIGNS (those that stand alone as a word) gets a syllabic
  spelling of 2-3 syllables (the word's sound, resampled to 2-3 syllables if it had 1).
  Every time such a logogram would be written (alone or inside a compound), the scribe
  uses the syllabic spelling instead with probability q (default 0.5). The syllables are the same 50 syllabograms
  used by the ordinary syllabic words, so a true system shares syllables across
  equations.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "internal_phonetics"))
from synth import Synth  # noqa: E402


class AltSynth(Synth):
    def __init__(self, seed=0, p=0.0, q=0.5, n_target=1675, mult_p=0.90, kmax=3):
        self.alt_p, self.alt_q, self.kmax = p, q, kmax
        super().__init__(seed=seed, mech=(), n_target=n_target, mult_p=mult_p)
        rng = np.random.default_rng(seed + 10_000)
        self.alt = {}
        # alternation is a property of the logogram SIGN (one logogram = one word):
        # every occurrence of an alternating logogram may be written syllabically.
        signs = []
        for w in self.words:
            if w["type"] == "logo" and w["logos"][0] not in signs:
                signs.append(w["logos"][0])
        for i, w in enumerate(self.words):
            L = w["logos"][0] if w["type"] == "logo" else None
            if L is None or L in self.alt or L not in signs:
                continue
            signs.remove(L)
            if rng.random() < p:
                snd = w["sound"]
                if len(snd) < 2 or len(snd) > kmax:
                    snd = tuple(int(x) for x in rng.choice(50, int(rng.integers(2, kmax + 1))))
                self.alt[L] = tuple(self.syl[x] for x in snd)
        self.truth["alt"] = dict(self.alt)
        # realised share of word-sign tokens written with an alternating logogram
        wt = {}
        for i, w in enumerate(self.words):
            for L in w["logos"]:
                wt[L] = wt.get(L, 0) + self.wp[i]
        self.alt_token_share = float(sum(wt.get(L, 0) for L in self.alt) / sum(wt.values()))

    def spell(self, wi):
        out = []
        for x in super().spell(wi):
            if x in self.alt and self.rng.random() < self.alt_q:
                out += list(self.alt[x])
            else:
                out.append(x)
        return out


def corpus(seed, p, q=0.5, n=1675):
    s = AltSynth(seed=seed, p=p, q=q, n_target=n)
    return s.corpus(n), s


if __name__ == "__main__":
    for p in (0.0, 0.1, 0.3):
        T, s = corpus(1, p)
        print(p, len(T), np.mean([len(t) for t in T]), len({x for t in T for x in t}),
              len(s.truth["alt"]), "token share %.3f" % s.alt_token_share)
