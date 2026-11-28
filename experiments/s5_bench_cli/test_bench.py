"""Planted-key checks for the bench (pre-registered in docs/prereg/s5_bench_cli.md, check 1).

    .venv/bin/python -I -m unittest discover -s experiments/s5_bench_cli -p "test_*.py" -v

A synthetic language with a known key is written in signs at the size of the real corpus (2,300 texts). The bench
must pass the true key on W, must not pass a deranged key, and must give the same numbers twice.
"""
import json, random, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bench as B  # noqa: E402

CONS, VOW = "ptkmnslrvh", "aiu"


def planted_language(seed=7, n_words=300, n_texts=2300):
    rng = random.Random(seed)
    syll = sorted({c + v for c in CONS for v in VOW} | {v for v in VOW})[:40]
    signs = [f"M{i}" for i in range(1, len(syll) + 1)]
    true_key = dict(zip(signs, syll))
    inv = {v: s for s, v in true_key.items()}
    words = set()
    while len(words) < n_words:
        words.add(tuple(rng.choice(syll) for _ in range(rng.choice((2, 2, 3)))))
    words = sorted(words)
    zipf = [1 / (i + 1) for i in range(len(words))]
    texts = []
    for _ in range(n_texts):
        ws = rng.choices(words, weights=zipf, k=rng.choice((1, 2)))
        texts.append([inv[s] for w in ws for s in w])
    rng.shuffle(texts); cut = int(0.75 * len(texts))
    lex = {"".join(w) for w in words}
    return true_key, lex, texts[:cut], texts[cut:]


def derange(key, seed=3):
    rng = random.Random(seed); s = sorted(key); v = [key[x] for x in s]
    while True:
        p = v[:]; rng.shuffle(p)
        if all(a != b for a, b in zip(p, v)): return dict(zip(s, p))


class PlantedKey(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key, cls.lex, cls.dev, cls.ho = planted_language()
        kw = dict(nperm=300, iters=1500, restarts=2, seed=11, log=lambda *a: None)
        cls.true = B.bench(cls.key, cls.lex, cls.dev, cls.ho, **kw)
        cls.wrong = B.bench(derange(cls.key), cls.lex, cls.dev, cls.ho, **kw)
        cls.again = B.bench(cls.key, cls.lex, cls.dev, cls.ho, **kw)
        with open(HERE / "planted_check.json", "w") as fh:
            json.dump(dict(true_key=cls.true, deranged_key=cls.wrong), fh, indent=1)

    def test_a_true_key_passes_on_W(self):
        self.assertTrue(self.true["scores"]["W"]["passes"], self.true["scores"]["W"])

    def test_b_deranged_key_does_not_pass(self):
        self.assertFalse(self.wrong["scores"]["W"]["passes"], self.wrong["scores"]["W"])
        self.assertFalse(self.wrong["scores"]["J"]["passes"], self.wrong["scores"]["J"])

    def test_c_deterministic(self):
        self.assertEqual(json.dumps(self.true, sort_keys=True), json.dumps(self.again, sort_keys=True))

    def test_key_csv_round_trip(self):
        p = HERE / "_tmp_key.csv"
        p.write_text("sign,value\nM1,pa\n2,ki\nM1,su\nM3,\n", encoding="utf-8")
        try:
            key, sha, problems = B.load_key(p)
        finally:
            p.unlink()
        self.assertEqual(key, {"M1": "pa", "M2": "ki"})
        self.assertEqual(len(problems), 2)
        self.assertEqual(len(sha), 64)


if __name__ == "__main__":
    unittest.main()
