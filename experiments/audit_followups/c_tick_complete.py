"""Check C: README #3 (ticked fish -> final) on complete single-line texts only.

Same test as signlist_robustness/harness.py t2_tick (M77, split v2, type unit, frozen bar p<0.05 and ticked
share > plain share), but held-out texts are restricted to complete texts with no line break '|' and no
break '#', so a sign before a break or a line end can never count as text-final.
Pre-registration: docs/prereg/audit_followups.md (section C).

    board/run.sh .venv/bin/python -I experiments/audit_followups/c_tick_complete.py
"""
import sys, json, random
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness as H  # noqa


def single_complete(ts):
    return [t for t in ts if t["complete"] and "|" not in t["seq"] and "#" not in t["seq"]]


def main():
    out = {}
    for vname in ("M77", "ICIT"):
        V = H.Variant(vname)
        C = H.build_corpus(V)
        if vname == "ICIT":   # harness forces complete=True for ICIT; use ICIT's own flag for this check
            flag = {}
            for t in H.icit_texts():
                flag.setdefault(tuple(t["seq"]), []).append(t["complete"])
            for k in ("dev_type", "ho_type", "dev_token", "ho_token"):
                for r in C[k]:
                    r["complete"] = all(flag.get(tuple(r["seq"]), [True]))
        for unit in ("type", "token"):
            dev, ho = C[f"dev_{unit}"], C[f"ho_{unit}"]
            base = H.t2_tick(V, dev, ho, random.Random(7))
            ho1 = single_complete(ho)
            res = H.t2_tick(V, dev, ho1, random.Random(7))
            out[f"{vname}_{unit}"] = dict(n_ho=len(ho), n_ho_single_complete=len(ho1), base=base, single_complete=res)
            print(vname, unit, len(ho), "->", len(ho1), "base", base, "\n   single", res, flush=True)
    (HERE / "out").mkdir(exist_ok=True)
    json.dump(out, open(HERE / "out" / "c_tick_complete.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
