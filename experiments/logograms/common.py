"""Shared helpers for experiments/logograms. Run scripts from the repo root."""
import csv, json, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa

OUT = ROOT / "experiments" / "logograms"
SRC = ROOT / "sources"
IM77 = SRC / "paragorth_Indus-/data/im77/im77_corpus_lines.csv"   # read as DATA only
FONT = SRC / "paragorth_Indus-/tools/indus_font.ttf"              # Wells glyphs at U+E000+n (data)

BRIDGE = json.load(open(SRC / "shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}
# Copper-specific Wells->Mahadevan equivalences, read off parallel copies of the same copper legend
# in M77 and ICIT (each listed with the parallel that fixes it). Used only to group copies into
# legend families, never as evidence.
W2M_EXTRA = {
    "W617": "M245 M245",    # 345 341 18 252 97 25 245 245  ~  W747 341 18 252 97 25 W617
    "W597": "M97 M252 M97",  # 295 87 97 252 97 25 245 245  ~  W905 87 W597 25 W617
    "W905": "M295", "W747": "M345", "W744": "M345",
    "W321": "M183",          # hare legend 65 336 89 407 169 183 169
    "W071": "M155",          # 87 155 169
    "W063": "M124",
    "W422": "M190", "W423": "M190", "W424": "M190",
    "W408": "M169",
    "W326": "M201",          # 201 99 48 342 67 138
    "W806": "M389",          # M77 reads 389 where the bridge gives 387 on copper legends
    "W017": "M112",          # bridge 110/112; M77 copper reads 112
    "W850": "M373",          # horned-personage legend: M77 ...169 373 287 342, bridge gives 261
    # one-sign faces (pictorial signs), from the parallel tablets:
    "W341": "M184", "W343": "M184",          # 204 245 342 + M184 (MD 3334/3398 = M-516/517)
    "W749": "M346",                           # 389 72 326 342 + M346
    "W753": "M355",                           # horned U with wheel (Mahadevan M355)
    "W781": "M363", "W782": "M362", "W777": "M364", "W780": "M362",  # horned-U family
    "W797": "M364",                           # MD 3375 (M364) = M-600 (W797, damaged)
    "W841": "M405", "W957": "M51",
}
HORNED_U = {"M362", "M363", "M364"}          # Mahadevan's horned 'shield' family (+ W777/780/781/782)


def wtok(w):
    if w in ("|", "#"):
        return [w]
    if w in W2M_EXTRA:
        return W2M_EXTRA[w].split()
    return [W2M.get(w, w)]


def icit_to_m(seq):
    out = []
    for w in seq:
        out += wtok(w)
    return out


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def lev(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]


def bh(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    if n == 0:
        return p
    o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


def save_json(name, obj):
    path = OUT / "results.json"
    allr = json.load(open(path)) if path.exists() else {}
    allr[name] = obj
    json.dump(allr, open(path, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
