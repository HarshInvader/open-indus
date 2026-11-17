"""A1c. Are the words in Yajnadevam's own readings Monier-Williams headwords (or stem + simple ending)?
Also: vowel profile vs real Sanskrit (Equationist baseline: a+A = 60-68% of vowels in Vedic/epigraphic Sanskrit).
Run: .venv/bin/python experiments/language/a1_reading_words.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from yj_common import load_inscriptions, SLP_VOW  # noqa

mw = set(w.strip() for w in open(HERE / "ext" / "skt" / "mw_headwords.txt"))
END = ["", "H", "m", "M", "s", "sya", "t", "n", "A", "AH", "am", "e", "AyAH", "ena", "Am", "aH", "an", "in", "i", "I"]
words, found, vow = [], 0, Counter()
for r in load_inscriptions():
    rd = (r.get("sanskrit") or "").strip()
    if not rd or rd.startswith("ref"):
        continue
    for w in rd.replace("-", " ").split():
        words.append(w)
        vow.update(c for c in w if c in SLP_VOW)
uniq = sorted(set(words))


def in_mw(w):
    for e in END:
        if e and w.endswith(e) and w[: -len(e)] in mw:
            return True
        for stem_end in ["", "a", "an", "in", "as", "i", "u", "f"]:
            base = (w[: -len(e)] if e else w)
            if base + stem_end in mw or (stem_end and base.endswith("a") and base[:-1] + stem_end in mw):
                return True
    return False


hit = [w for w in uniq if in_mw(w)]
lens = Counter(len([c for c in w if c not in SLP_VOW]) for w in uniq)
res = dict(word_tokens=len(words), word_types=len(uniq), types_matching_MW_stem_or_ending=len(hit),
           share=round(len(hit) / len(uniq), 3), a_share_of_vowels=round((vow["a"] + vow["A"]) / sum(vow.values()), 3),
           vowel_counts=dict(vow.most_common()), consonants_per_word_type=dict(sorted(lens.items())),
           unmatched_examples=[w for w in uniq if w not in hit][:40])
json.dump(res, open(HERE / "out" / "a1_reading_words.json", "w"), indent=1)
print(json.dumps(res, indent=1))
