"""Descriptive add-on (not in the hashed run.py): mean d forward vs reversed on the 28 round texts with a
readable last sign. Uses the per-text table in results.json; no rescoring, no matched null.
    .venv/bin/python -I experiments/round_reverse/subset28.py"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts
R = json.load(open(Path(__file__).parent / "results.json"))
last_ok = {}
for t in icit_texts():
    raw = [s for s in t["seq"] if s != "|"]
    last_ok.setdefault(t["id"], bool(raw) and raw[-1] != "#")
out = {}
for m in ("KN", "GR", "POS"):
    rows = [t for t in R["texts"] if last_ok.get(t["id"]) and t[f"fwd_{m}"] is not None]
    f = sum(t[f"fwd_{m}"] for t in rows) / len(rows); r = sum(t[f"rev_{m}"] for t in rows) / len(rows)
    out[m] = dict(n_scorable=len(rows), mean_d_forward=round(f, 3), mean_d_reversed=round(r, 3),
                  n_lower_when_reversed=sum(t[f"rev_{m}"] < t[f"fwd_{m}"] for t in rows))
out["n_last_ok_round"] = sum(last_ok.get(t["id"], False) for t in R["texts"])
print(out)
json.dump(out, open(Path(__file__).parent / "subset28.json", "w"), indent=1)
