"""H1: re-run the 9 signlist_robustness headline tests under the greedy shape+context partition.
The harness is imported read-only; its output directory is redirected to this folder (out/raw/).
    board/run.sh .venv/bin/python -I experiments/signlist_shape/headline.py
"""
import sys, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/signlist_robustness"))
import harness  # noqa

harness.HERE = HERE / "out"
part = json.load(open(HERE / "out/partition_both.json"))
harness.VJ["partitions"]["shape_ctx"] = part
r = harness.run_variant("shape_ctx")
base = json.load(open(ROOT / "experiments/signlist_robustness/raw/M77.json"))
rows = []
for unit in ("type", "token"):
    for t in ("T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"):
        a = base[unit][t].get("survives"); b = r[unit][t].get("survives") if isinstance(r[unit][t], dict) else None
        rows.append({"unit": unit, "test": t, "M77": a, "shape_ctx": b})
        print(unit, t, a, b, flush=True)
json.dump({"n_labels": r["n_labels"], "rows": rows}, open(HERE / "out/headline.json", "w"), indent=1)
