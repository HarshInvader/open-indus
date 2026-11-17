"""Step 3 (exploratory, pre-declared): do detached-class signs occur inline, in which slot,
and do they co-occur with each other? Run after d2.
Run: .venv/bin/python -I experiments/detached_signs/d3_inline.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ds_lib import *  # noqa
from corpus.load import m77_texts, icit_texts, distinct, m77_lines  # noqa

OUT = Path(__file__).parent
CLASS_M = ["M242", "M374", "M93", "M326", "M393"]
rng = np.random.default_rng(7)
T = [t for t in distinct(m77_texts()) if any(s not in ("|", "#") for s in t["seq"])]
res = {}


def slot(signs, i):
    if len(signs) == 1:
        return "alone"
    return "first" if i == 0 else "last" if i == len(signs) - 1 else "medial"


# slot profile of every token on single-line, break-free texts
prof = defaultdict(Counter)
for t in T:
    if t["n_lines"] != 1 or "#" in t["seq"]:
        continue
    s = t["seq"]
    for i, x in enumerate(s):
        prof[x][slot(s, i)] += 1
cnt = Counter(x for t in T for x in t["seq"] if x not in ("|", "#"))
slots = ["alone", "first", "medial", "last"]
allp = Counter(); [allp.update(v) for v in prof.values()]
res["slot_all_tokens"] = {k: allp[k] for k in slots}
res["inline"] = {}
for s in CLASS_M:
    # frequency-matched controls: 20 nearest-count non-class signs with >=3 single-line tokens
    pool = sorted([x for x in cnt if x not in CLASS_M and sum(prof[x].values()) >= 3], key=lambda x: abs(cnt[x] - cnt[s]))[:20]
    ctrl = Counter(); [ctrl.update(prof[x]) for x in pool]
    tot = sum(ctrl.values())
    obs = prof[s]; n = sum(obs.values())
    res["inline"][s] = dict(total_tokens=cnt[s], single_line_breakfree_tokens=n, slots={k: obs[k] for k in slots},
                            expected_from_freq_matched={k: round(n * ctrl[k] / tot, 2) for k in slots} if tot else None,
                            controls=pool)

# where are class tokens in multi-line texts: detached (own line) vs inside a multi-sign line; which line
ml = defaultdict(Counter)
for t in T:
    ls = lines(t["seq"])
    if len(ls) < 2:
        continue
    for li, l in enumerate(ls):
        sg = [x for x in l if x != "#"]
        for i, x in enumerate(sg):
            if x in CLASS_M:
                if len(sg) == 1 and "#" not in l:
                    ml[x]["detached_line%d_of_%d" % (li + 1, len(ls))] += 1
                else:
                    ml[x]["inline_in_multisign_line:" + slot(sg, i)] += 1
res["multiline_positions"] = {k: dict(v) for k, v in ml.items()}

# co-occurrence of class signs in one text vs token-shuffle null (text lengths, sign freqs kept)
def n_co(texts):
    return sum(1 for sg in texts if len(set(sg) & set(CLASS_M)) >= 2)


toks = [[x for x in t["seq"] if x not in ("|", "#")] for t in T]
obs = n_co(toks)
flat = np.array([x for sg in toks for x in sg]); lens = [len(sg) for sg in toks]
null = []
for _ in range(2000):
    rng.shuffle(flat); i = 0; sh = []
    for L in lens:
        sh.append(list(flat[i:i + L])); i += L
    null.append(n_co(sh))
null = np.array(null)
pairs = Counter()
for sg in toks:
    c = sorted(set(sg) & set(CLASS_M))
    for a in range(len(c)):
        for b in range(a + 1, len(c)):
            pairs[c[a] + "+" + c[b]] += 1
res["cooccur"] = dict(observed_texts_with_2plus_class_signs=obs, null_mean=float(null.mean()),
                      p_ge=float((1 + np.sum(null >= obs)) / 2001), pairs=dict(pairs),
                      texts_with_any_class_sign=sum(1 for sg in toks if set(sg) & set(CLASS_M)))
# same in multi-line texts only (where most detached tokens sit)
mtoks = [[x for x in t["seq"] if x not in ("|", "#")] for t in T if t["n_lines"] > 1]
res["cooccur_multiline_only"] = dict(observed=n_co(mtoks), n_texts=len(mtoks),
                                     texts_with_any=sum(1 for sg in mtoks if set(sg) & set(CLASS_M)))
# catalogue of every class token (object, site, field, layout) for RESULTS
cat = []
for t in T:
    if set(t["seq"]) & set(CLASS_M):
        cat.append(dict(text_no=t["text_no"], side=t["side"], site=t["site"], type=t["object_type"],
                        fs=t.get("fs_category"), fs80=t.get("fs80"), seq=" ".join(t["seq"])))
res["catalogue_m77"] = cat
json.dump(res, open(OUT / "d3_inline.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k != "catalogue_m77"}, indent=1, default=float))
