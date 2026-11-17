"""Task B core: matched-coarse slot segmentation, decision features, nearest-class classification, controls.

Matched-coarse segmentation (same rule on both sides): closed function classes are kept as their own slot labels,
all open content is merged into one CONTENT label, and the target class is kept.
  reference: SEAL_OF, SERV, KIN, CONJ kept (+ TITLE when TITLE is the target); OWNER/NAME/FATHER/LORD(/TITLE) -> CONTENT
  Indus:     OPEN, CONN, POST, CLOSER kept; everything else -> CONTENT
"""
import numpy as np
from co_lib import *

RELATORS = ("SEAL_OF", "SERV", "KIN", "CONJ")
TARGETS = ("SEAL_OF", "TITLE", "SERV", "KIN")
DEC = ["short", "nameonly", "longdiff", "occ", "edge_s"]       # position-free decision features (pre-registered)
REPORT = ["last", "first", "types20", "recur", "alone"]        # reported only


def ref_runs(C, target):
    out = []
    for c in C:
        lab = []
        for s in c["slot"]:
            if s in RELATORS or s == target: lab.append(s)
            else: lab.append("CONTENT")
        out.append(runs_of(lab, c["tok"]))
    return out


def indus_runs(texts, closer="set"):
    out = []
    for s in texts:
        lab = []
        for x in s:
            k = indus_class(x)
            if closer == "jar" and k == "CLOSER":
                k = "CLOSER" if x in ("M342", "W740") else "CONTENT"
            lab.append("CONTENT" if k == "CORE" else k)
        out.append(runs_of(lab, s))
    return out


def feats(LR, name, rng):
    f = slot_features(LR, name, rng, name_slot="CONTENT")
    return f


def ref_class_feats(C, rng, targets=TARGETS):
    out = {}
    for t in targets:
        f = feats(ref_runs(C, t), t, rng)
        if f is not None: out[t] = f
    return out


SD_FLOOR = 0.05


def scale_from(class_feats_list):
    X = np.array([[f[k] for k in DEC] for F in class_feats_list for f in F.values()])
    sd = X.std(0); sd = np.maximum(sd, SD_FLOOR)
    return sd


def nearest(f, F, sd):
    d = {k: float(np.linalg.norm((np.array([f[a] for a in DEC]) - np.array([v[a] for a in DEC])) / sd) / np.sqrt(len(DEC)))
         for k, v in F.items()}
    return min(d, key=d.get), d


def subsample(X, n, rng):
    if len(X) <= n: return list(X)
    idx = rng.choice(len(X), n, replace=False)
    return [X[i] for i in idx]


def boot(X, rng):
    idx = rng.integers(0, len(X), len(X))
    return [X[i] for i in idx]


def blind_word_slots(C, target_word, top_words):
    """Blind segmentation of a relabelled culture: each of the top frequent word types is its own closed label,
    everything else CONTENT. Labels never look at gold classes."""
    out = []
    for c in C:
        lab = [("W:" + w) if w in top_words else "CONTENT" for w in c["tok"]]
        out.append(runs_of(lab, c["tok"]))
    return out
