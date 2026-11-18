"""Indus test (board #42). Runs ONLY if the known-answer gate in out/control.json passed.
Consensus corpus cons_sign_ext, break-free distinct texts, line breaks dropped.
Pool = all such texts; hosts = dev or held-out (dev_heldout v2 via key0).
Run: board/run.sh .venv/bin/python -I experiments/m99_relator/rel_indus.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rel_lib as R  # noqa: E402

ROOT = HERE.parents[1]
OUT = HERE / "out"
N_SHUF = 1000
TARGETS = ["M99", "M123"]


def build(types=None):
    recs = json.load(open(ROOT / "experiments/consensus_corpus/out/corpora/cons_sign_ext.json"))["recs"]
    ho = set(json.load(open(ROOT / "data/splits_v2.json"))["heldout"])
    split = {}
    for r in recs:
        if types and r["object_type"] not in types:
            continue
        t = tuple(s for s in r["seq"] if s != "|")
        if "#" in t or not t:
            continue
        split.setdefault(t, set()).add("ho" if r["key0"] in ho else "dev")
    texts = sorted(split)
    dev = [i for i, t in enumerate(texts) if split[t] == {"dev"}]
    hol = [i for i, t in enumerate(texts) if split[t] == {"ho"}]
    return texts, dev, hol


def strip(res):
    out = {k: v for k, v in res.items() if k != "summ"}
    out["top_signs_by_d2"] = sorted(((s, round(v["d2"], 3), v["n"]) for s, v in res["summ"].items()),
                                    key=lambda x: -x[1])[:15]
    return out


def main():
    ctrl = json.load(open(OUT / "control.json"))
    if not ctrl.get("gate_pass"):
        print("Known-answer gate failed: Indus test not run (verdict: untestable).")
        return
    results = {}
    for label, types in (("all", None), ("seal_sealing", {"seal", "sealing"})):
        texts, dev, hol = build(types)
        for split, idx in (("heldout", hol), ("dev", dev)):
            res = R.run_test(texts, idx, TARGETS, n_shuffle=N_SHUF, seed=42)
            results[f"{label}_{split}"] = strip(res)
            print(label, split, json.dumps({t: {k: res[t].get(k) for k in
                  ("n_occ", "d2", "a", "pct_d2", "pct_a", "n_matched", "shuffle_mean", "p_shuffle", "flag")}
                  for t in TARGETS}))
    json.dump(results, open(OUT / "indus.json", "w"), indent=1)


if __name__ == "__main__":
    main()
