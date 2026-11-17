"""Calibration registry for the short-label experiment.

Each system: name -> (label, family, set, loader)
  label  L = writes language, C = non-linguistic code, ? = unlabelled reference
  family systems sharing a source/language/script are held out together in leave-one-family-out
  set    'genre' = real whole short units (never cut), the primary calibration set
         'synth' = synthetic code (sensitivity only)
         'old'   = language_vs_code comparators built from chunked prose (sensitivity only)
Pools: only whole units of length 1..MAXLEN (17 = longest distinct Indus text) are sampled; no unit is
ever cut. Built by cdli_extract.py and build_corpora.py (data/*.jsonl); old comparators are imported
read-only from experiments/language_vs_code/lvc_corpora.py.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/language_vs_code"))
import lvc_corpora as lc  # noqa: E402

MAXLEN = 17
DATA = HERE / "data"


def _d(name):
    return lambda: [json.loads(l)["seq"] for l in open(DATA / f"{name}.jsonl", encoding="utf-8")]


REG = {
    # ---- writing, real whole short units ----
    "cun_seal_ur3": ("L", "cuneiform_seal", "genre", _d("cun_seal_ur3")),   # Ur III seal legends, signs
    "cun_seal_ob":  ("L", "cuneiform_seal", "genre", _d("cun_seal_ob")),    # Old Babylonian/Old Assyrian seal legends
    "cun_seal_oakk": ("L", "cuneiform_seal", "genre", _d("cun_seal_oakk")),  # Old Akkadian/ED/Lagash II seals
    "linb_line":    ("L", "aegean", "genre", lc.linb),                       # Linear B entry lines (DAMOS), signs
    "lina_label":   ("L", "aegean", "genre", _d("lina_label")),              # Linear A nodules/roundels/vessels
    "egy_nom":      ("L", "egyptian", "genre", _d("egy_nom")),               # Middle Kingdom verbless phrases, hieroglyphs
    "lat_label":    ("L", "latin", "genre", _d("lat_label")),                # Latin stamps/owner marks/labels, words
    "lat_short":    ("L", "latin", "genre", _d("lat_short")),                # Latin whole inscriptions, words
    # ---- codes, real ----
    "heraldry":  ("C", "heraldry", "genre", lc.heraldry),
    "khipu":     ("C", "khipu", "genre", lc.khipu),
    "icd10":     ("C", "icd10", "genre", lc.icd10),
    "emoji":     ("C", "emoji", "genre", _d("emoji")),
    "chess_eco": ("C", "chess", "genre", _d("chess_eco")),
    "chords":    ("C", "chords", "genre", _d("chords")),
    "metar":     ("C", "metar", "genre", _d("metar")),
    # ---- synthetic codes ----
    "plates": ("C", "plates", "synth", lc.plates),
    "slot":   ("C", "slot", "synth", lc.slot),
    "sigil":  ("C", "sigil", "synth", lc.sigil),
    # ---- unlabelled ----
    "proto_cun":     ("?", "proto_cun", "ref", _d("proto_cun")),
    "proto_elamite": ("?", "proto_elamite", "ref", lc.proto_elamite),
    "indus_bigram":  ("?", "indus_bigram", "ref", lc.indus_bigram),
}
# old chunked-prose comparators (language_vs_code), sensitivity only
for _n, _fam in (("lat_edh", "latin"), ("lat_cae", "latin"), ("fin_kal", "finnish"), ("san_wiki", "sanskrit"),
                 ("tam_wiki", "tamil")):
    REG["old_" + _n] = ("L", _fam, "old", getattr(lc, _n))
    REG["old_W_" + _n] = ("L", _fam, "old", (lambda n=_n: lc.wordlevel(lc._words(n))))
REG["old_W_ur3"] = ("L", "cuneiform_seal", "old", lambda: lc.wordlevel(lc._words("ur3")))
REG["old_W_linb"] = ("L", "aegean", "old", lambda: lc.wordlevel(lc._words("linb")))


def pool(name):
    lab, fam, st, f = REG[name]
    return [t for t in f() if 1 <= len(t) <= MAXLEN]


indus = lc.indus

if __name__ == "__main__":
    import numpy as np
    for k, (lab, fam, st, f) in REG.items():
        P = pool(k); L = [len(t) for t in P]
        print(f"{k:18s} {lab} {fam:15s} {st:6s} pool={len(P):6d} mean_len={np.mean(L):5.2f} "
              f"types={len({s for t in P for s in t}):6d}")
