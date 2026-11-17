"""Test 2 (context check for commodity candidates): are 'counted item' signs that could stand for
Meluhhan exports over-represented on Indus-inscribed objects found in the West (where goods arrived)?

Candidates (Wells): W390 tree-unit (timber? ab-ba / mes wood), W405 tree, W220 plain fish,
W700 cup (measure), W740 jar. Null: home texts of the same object class and length, 20,000 draws.
Run: .venv/bin/python experiments/meluhha/goods.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts  # noqa: E402

HERE = Path(__file__).resolve().parent
WEST = {"Ur", "Kish", "Susa", "Nippur", "Tell Umma", "Tello", "Girsu", "Failaka", "Karzakan",
        "Qala'at al-Bahrain", "Saar", "Janabiyah", "Tepe Yahya", "Luristan", "Hajar", "Ra's al-Junayz",
        "Salut", "Kalba"}
CAND = ["W390", "W405", "W220", "W700", "W740"]
rng = np.random.default_rng(7)

T = icit_texts()
seen, foreign, home = set(), [], []
for x in T:
    s = tuple(t for t in x["seq"] if t not in ("|", "#"))
    if not s:
        continue
    key = (x["site"], s)
    if key in seen:
        continue
    seen.add(key)
    (foreign if x["site"] in WEST else home).append((len(s), set(s), x["type"] or ""))

bylen = {}
for L, s, ty in home:
    bylen.setdefault(min(L, 8), []).append(s)
res = {"n_foreign": len(foreign), "n_home": len(home)}
for c in CAND:
    obs = sum(c in s for _, s, _ in foreign)
    sims = np.zeros(20000)
    for L, _, _ in foreign:
        pool = bylen[min(L, 8)]
        idx = rng.integers(0, len(pool), 20000)
        sims += np.array([c in pool[i] for i in idx])
    res[c] = {"obs": int(obs), "exp": float(sims.mean()),
              "p_enriched": float((sims >= obs).mean()), "p_depleted": float((sims <= obs).mean())}
print(json.dumps(res, indent=1))
out = HERE / "results.json"
allr = json.loads(out.read_text()) if out.exists() else {}
allr["goods_foreign_enrichment"] = res
out.write_text(json.dumps(allr, indent=1))
