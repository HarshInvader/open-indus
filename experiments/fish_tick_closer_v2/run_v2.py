"""fish_tick_closer_v2 runner. Prereg: docs/prereg/fish_tick_closer_v2.md.

Same tests, bars, seeds and gate as v1 (functions imported from experiments/fish_tick_closer/run.py);
only the de-duplication unit changes (dedup.py). Stages, in the frozen order:
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer_v2/run_v2.py counts
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer_v2/run_v2.py gate
    # only if the gate is not a full failure (prereg section "Stop rule"):
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer_v2/run_v2.py real      # DEV, HELD, NEW
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer_v2/run_v2.py redteam
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dedup  # noqa: E402

_spec = importlib.util.spec_from_file_location("ftc_v1_run", HERE.parent / "fish_tick_closer" / "run.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)


def dump(name, obj):
    json.dump(obj, open(HERE / f"out_{name}.json", "w"), indent=1, default=float)
    print(json.dumps(obj, default=float)[:3000], flush=True)


def gate_stop(g):
    """Stop rule: the DEV gate fails for BOTH P1 and P2."""
    return not (g["DEV"]["p1_gate_pass"] or g["DEV"]["p2_gate_pass"])


def main():
    stage = sys.argv[1]
    t0 = time.time()
    if stage == "counts":
        raw = dedup.raw_sets()
        out = {}
        for name, texts in raw.items():
            _, info = dedup.greedy(texts, return_info=True)
            out[name] = dict(v2=info, v1=dedup.v1_family_stats(texts))
        dump(stage, out)
        return
    sets = dedup.load_sets()
    print({k: len(v[0]) for k, v in sets.items()}, flush=True)
    if stage == "gate":
        g = v1.gate(sets)
        g["STOP"] = gate_stop(g)
        dump(stage, g)
    elif stage == "real":
        g = json.load(open(HERE / "out_gate.json"))
        if g["STOP"]:
            sys.exit("gate failed on DEV for P1 and P2: stop (prereg)")
        dump(stage, v1.real(sets, ["DEV", "HELD", "NEW"]))
    elif stage == "redteam":
        g = json.load(open(HERE / "out_gate.json"))
        if g["STOP"]:
            sys.exit("gate failed: stop (prereg)")
        dump(stage, v1.redteam(sets))
    print("seconds", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
