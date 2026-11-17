"""B3e. External-validity control: classify REAL corpora of known language with the classifier
trained on all simulator specs (A-E). If it cannot name the typology of real Latin and Mycenaean
Greek (both Indo-European, suffixing, closest class = IA), its Indus label is not evidence.
  Latin EDH (Italy) inscriptions of <= 5 words, written in the simulated script (10 script draws)
  Linear B (DAMOS) lines: real syllabic sign sequences + ideograms (numerals dropped)
  Ur III seal legends, real (not resampled), written in the simulated script
Run: .venv/bin/python experiments/language/b3_realcontrols.py
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from b3_sim import Script, features, indus_lengths, PG  # noqa

SPECS = ["b3_features.json", "b3_features_alt.json", "b3_features_open.json", "b3_features_under.json", "b3_features_sym.json"]
DROP = {"V", "logV", "ttr", "hapax", "heaps_ratio", "len_mean", "len_sd", "cls", "rep"}


def resample(texts, rng, tl, n=2300):
    by = {}
    for t in dict.fromkeys(map(tuple, texts)):
        if t:
            by.setdefault(len(t), []).append(t)
    out, lens = [], list(tl)
    rng.shuffle(lens)
    for L in lens[:n]:
        for d in [0, 1, -1, 2, -2, 3, -3, 4, 5]:
            if by.get(L + d):
                out.append(list(by[L + d].pop(rng.randrange(len(by[L + d]))))); break
    return out


def encode_words(legends, rng):
    """legends: list of word lists; each word one morpheme."""
    lg = [[[(w, "root")] for w in s] for s in legends]
    mf = Counter(m for l in lg for w in l for m in w)
    sc = Script(rng, mf)
    return [sc.write(l) for l in lg]


def main():
    rows = [r for f in SPECS for r in json.load(open(HERE / "out" / f))["sims"]]
    F = [k for k in rows[0] if k not in DROP]
    X = np.array([[r[f] for f in F] for r in rows]); y = np.array([r["cls"] for r in rows])
    models = {"RF": RandomForestClassifier(500, min_samples_leaf=2, random_state=0, n_jobs=2).fit(X, y),
              "LR": make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=5000)).fit(X, y)}
    tl = indus_lengths()
    lat = [json.loads(l)["seq"] for l in open(PG / "codelib" / "latin_edh.jsonl")]
    lat = [[w for w in s if not re.fullmatch(r"[ivxlcdm]+", w) or len(w) > 4] for s in lat]
    lat = [s for s in lat if 1 <= len(s) <= 5]
    linb = []
    for l in open(PG / "codelib" / "linear_b.jsonl"):
        s = json.loads(l)["seq"]
        toks = []
        for w in s:
            if w in ("NUM",) or w.startswith(".") or "↓" in w or "[" in w:
                continue
            if "-" in w or re.fullmatch(r"[a-z\d*]+", w):
                toks += [x for x in w.split("-") if x]
            else:
                toks.append(w)  # ideogram / logogram / measure sign
        if toks:
            linb.append(toks)
    ur3 = [json.loads(l)["seq"] for l in open(PG / "codelib" / "ur3_legends.jsonl")]
    ur3w = [[re.sub(r"[{}_]", "", w) for w in s] for s in ur3]
    res = {"n_latin_texts": len(lat), "n_linearb_lines": len(linb)}
    out = {}
    for name in ["latin", "linearb", "ur3_real"]:
        preds = {m: [] for m in models}
        probs = {m: [] for m in models}
        for draw in range(10):
            rng = random.Random(100 + draw)
            if name == "latin":
                c = encode_words(lat, rng)
            elif name == "ur3_real":
                # each hyphenated word: frequent words as one morpheme, else syllables
                legends = [[[(p, "syl") for p in re.split(r"[-.]", w) if p] if True else None for w in s] for s in ur3w]
                f = Counter(w for s in ur3w for w in s)
                lg = [[[(w, "title")] if f[w] >= 25 else [(p, "syl") for p in re.split(r"[-.]", w) if p] for w in s] for s in ur3w]
                mf = Counter(m for l in lg for w in l for m in w)
                sc = Script(rng, mf)
                c = [sc.write(l) for l in lg]
            else:
                c = linb
            corp = resample(c, rng, tl)
            ft = features(corp)
            x = np.array([[ft[f] for f in F]])
            for m, mod in models.items():
                p = mod.predict_proba(x)[0]
                probs[m].append(dict(zip(mod.classes_, p)))
                preds[m].append(mod.classes_[int(np.argmax(p))])
            if name == "linearb":
                break
        out[name] = {m: dict(argmax_counts=dict(Counter(preds[m])),
                             mean_probs={c: round(float(np.mean([d[c] for d in probs[m]])), 3) for c in models[m].classes_})
                     for m in models}
        print(name, json.dumps(out[name]))
    res["controls"] = out
    res["expected"] = {"latin": "IA (Indo-European suffixing)", "linearb": "IA (Indo-European suffixing)", "ur3_real": "SUM"}
    json.dump(res, open(HERE / "out" / "b3_realcontrols.json", "w"), indent=1)


if __name__ == "__main__":
    main()
