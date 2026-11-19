"""POST HOC (not pre-registered): is the sealed size control a lucky draw?

KN-3 is deterministic, so we can redo the size control many times: drop 177 random train/val texts
NOT related to the test set (as in `sizectl`, but with new seeds), refit their KN-3 (their code,
NgramLM 'kn_interp' order 3 on train+val) and score the same 303 test texts. Compares with the purge
split, which drops the 177 related texts.
Run: .venv-torch/bin/python -I experiments/bench_restoration/posthoc_kn_draws.py [n_draws]
"""
import json, random, runpy, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "raw/dep/zenodo_deposit/code/scripts"
sys.path.insert(0, str(SCRIPTS))
g = runpy.run_path(str(SCRIPTS / "restore_transformer_ebuds.py"), run_name="not_main")
NgramLM, ngram_posterior, eval_positions, metrics = g["NgramLM"], g["ngram_posterior"], g["eval_positions"], g["metrics"]


def load(name):
    return [json.loads(l) for l in open(HERE / "out/splits" / f"{name}.jsonl")]


def kn_hit1(trva, te):
    _, meta = eval_positions(te)
    p = ngram_posterior(NgramLM(trva, 3, "kn_interp"), te, meta)
    return metrics(p, meta, 1, 0)["exhaustive"]["hit1"]


orig, purge = load("orig"), load("purge")
te = [t["signs"] for t in orig if t["split"] == "test"]
kept = {t["id"] for t in purge}
related = [t for t in orig if t["split"] != "test" and t["id"] not in kept]
unrelated = [t for t in orig if t["split"] != "test" and t["id"] in kept]
res = {"purge": kn_hit1([t["signs"] for t in purge if t["split"] != "test"], te), "draws": []}
print("purge KN-3 hit1", res["purge"], "dropped", len(related), flush=True)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
for k in range(n):
    gone = {t["id"] for t in random.Random(1000 + k).sample(unrelated, len(related))}
    res["draws"].append(kn_hit1([t["signs"] for t in orig if t["split"] != "test" and t["id"] not in gone], te))
    print(k, res["draws"][-1], flush=True)
d = np.array(res["draws"])
res["summary"] = {"mean": round(float(d.mean()), 2), "min": float(d.min()), "max": float(d.max()),
                  "gap_vs_purge_min": round(float(d.min() - res["purge"]), 2)}
print(res["summary"])
(HERE / "out/posthoc_kn_draws.json").write_text(json.dumps(res, indent=1))
