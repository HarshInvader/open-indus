"""Pre-registered check 2 (docs/prereg/s5_bench_cli.md): run the one-command bench on Pierson's K185, which
experiments/bench_pierson/ found does NOT beat its own shuffles. Writes the key and lexicon as the plain files a
submitter would give, then calls bench.py exactly as a user would.

    .venv/bin/python -I experiments/s5_bench_cli/validate_k185.py      -> k185_result.json
"""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "experiments" / "bench_pierson")]
import bench as B  # noqa: E402
from common import KEYS, load_k185, tamil_lemmas, tamil_to_latin  # noqa: E402

k = load_k185()
with open(HERE / "k185_key.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["sign", "value"])
    for s in sorted(k, key=lambda x: int(x[1:])): w.writerow([s, k[s][0]])
words = set(tamil_lemmas().values()) | {tamil_to_latin(x) for x in json.load(open(KEYS / "dravidian_tamil_lm.json"))["vocab"]}
(HERE / "k185_lexicon.txt").write_text("\n".join(sorted(w for w in words if w)) + "\n", encoding="utf-8")
B.main([str(HERE / "k185_key.csv"), "--lexicon", str(HERE / "k185_lexicon.txt"), "--out", str(HERE / "k185_result.json")])
