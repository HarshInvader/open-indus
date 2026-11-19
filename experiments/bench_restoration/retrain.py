"""Board #18 follow-up: retrain the deposit's own transformer + KN-3 on leakage-fixed splits.

Prereg: docs/prereg/bench_restoration_retrain.md. Their code is run unchanged from the deposit
(read in full first); this file only builds input files and compares outputs.

  build    write out/splits/{orig,purge,family}.jsonl in their ebuds.jsonl format
  run X    run their restore_transformer_ebuds.py on split X (via runpy, since -I drops the script dir)
  compare  read out/runs/*/metrics.json and write out/compare.json

Run: .venv-torch/bin/python -I experiments/bench_restoration/retrain.py build|run orig|compare
"""
import csv, json, random, runpy, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
DEP = HERE / "raw/dep/zenodo_deposit"
SCRIPTS = DEP / "code/scripts"
OUT = HERE / "out"
SPL = OUT / "splits"


def texts():
    from corpus.load import m77_texts
    seqs = {}
    for t in m77_texts():
        k = str(t["text_no"]) if t["side"] == 0 else f"{t['text_no']}.{t['side']}"
        seqs.setdefault(k, [s for s in t["seq"] if s != "|"])
    fa = list(csv.DictReader(open(DEP / "data/fold_assignments.csv")))
    return seqs, fa


def related(a, b):
    """bench.py leak rule: exact copy, or corpus.build._close in either direction."""
    from corpus.build import _close
    return a == b or (abs(len(a) - len(b)) <= 20 and (_close(a, b) or _close(b, a)))


def tok(s):
    return [x[1:] for x in s]  # "M123" -> "123", their SIGNS format


def write(name, rows):
    SPL.mkdir(parents=True, exist_ok=True)
    with open(SPL / f"{name}.jsonl", "w") as f:
        for tid, s, sp in rows:
            f.write(json.dumps({"id": tid, "signs": tok(s), "split": sp}) + "\n")
    print(name, Counter(sp for _, _, sp in rows))


def build():
    seqs, fa = texts()
    ids = [r["text_id"] for r in fa]
    sp0 = {r["text_id"]: ("val" if r["split"] in ("val", "validation") else r["split"]) for r in fa}
    assert all(i in seqs for i in ids)
    bad = [s for i in ids for s in seqs[i] if not (s.startswith("M") and 1 <= int(s[1:]) <= 417)]
    assert not bad, bad[:5]
    # (a) orig: their folds, our readings
    write("orig", [(i, seqs[i], sp0[i]) for i in ids])
    # (b) purge: same test set; drop every train/val text related to any test text
    test = [seqs[i] for i in ids if sp0[i] == "test"]
    rows, dropped = [], 0
    for i in ids:
        if sp0[i] != "test" and any(related(seqs[i], t) for t in test):
            dropped += 1
            continue
        rows.append((i, seqs[i], sp0[i]))
    print("purge dropped", dropped)
    write("purge", rows)
    # (b') size control: drop the same number of UNrelated train/val texts, so purge vs orig
    # separates "less leakage" from "less training data"
    keep = {i for i, _, _ in rows}
    pool = [i for i in ids if sp0[i] != "test" and i in keep]
    gone = set(random.Random(18).sample(pool, dropped))
    write("sizectl", [(i, seqs[i], sp0[i]) for i in ids if i not in gone])
    # (c) family: union-find over all related pairs; whole families go to one split
    par = {i: i for i in ids}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            if related(seqs[ids[a]], seqs[ids[b]]):
                par[find(ids[a])] = find(ids[b])
    fam = {}
    for i in ids:
        fam.setdefault(find(i), []).append(i)
    fams = sorted(fam.values(), key=lambda f: min(f))
    random.Random(18).shuffle(fams)
    n_test, n_val = Counter(sp0.values())["test"], Counter(sp0.values())["val"]
    rows, c = [], Counter()
    for f in fams:
        sp = "test" if c["test"] < n_test else ("val" if c["val"] < n_val else "train")
        c[sp] += len(f)
        rows += [(i, seqs[i], sp) for i in f]
    sizes = sorted((len(f) for f in fams), reverse=True)
    print("families", len(fams), "largest", sizes[:5])
    write("family", rows)


def run(name):
    extra = sys.argv[3:]
    tag = extra.pop(0) if extra and not extra[0].startswith("--") else name
    out = OUT / ("runs" if tag == name else "scratch") / tag
    sys.path.insert(0, str(SCRIPTS))
    sys.argv = ["restore_transformer_ebuds.py", "--data", str(SPL / f"{name}.jsonl"), "--output", str(out)] + extra
    runpy.run_path(str(SCRIPTS / "restore_transformer_ebuds.py"), run_name="__main__")


def compare():
    res = {}
    for d in sorted((OUT / "runs").glob("*/metrics.json")):
        m = json.loads(d.read_text())
        res[d.parent.name] = {k: {x: m[k]["exhaustive"][x] for x in ("n", "hit1", "hit5", "mrr")}
                              for k in ("test_ngram_kn", "test_transformer", "test_blend")}
        res[d.parent.name]["alpha"] = m.get("blend_alpha_ngram")
    print(json.dumps(res, indent=1))
    (OUT / "compare.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"build": build, "compare": compare}.get(sys.argv[1], lambda: run(sys.argv[2]))()
