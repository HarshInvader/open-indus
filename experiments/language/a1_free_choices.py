"""A1a. How many free choices does each Yajnadevam reading need?

For every inscription with an own reading (not 'ref:'), align the consonants of the reading
(SLP1) to the consonants of the concatenated key values (xlits.csv) by minimum edit distance,
and count:
  vowels      : vowels written in the reading (vowel quality/length is unconstrained by the key:
                key values contain almost only 'a' as vowel material)
  breaks      : word breaks (space or '-')
  subs        : consonant in reading differs from key consonant (n->R, s->h, t->T, ...)
  ins / dels  : consonants added / key consonants dropped
Run: .venv/bin/python experiments/language/a1_free_choices.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from yj_common import load_key, load_inscriptions, text_signs, SLP_VOW, SLP_CONS  # noqa

OUT = Path(__file__).resolve().parent


def align(a, b):
    """Levenshtein alignment of lists a (key consonants) and b (reading consonants)."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    i, j, ops = n, m, []
    while i or j:
        if i and j and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            ops.append(("eq" if a[i - 1] == b[j - 1] else "sub", a[i - 1], b[j - 1])); i -= 1; j -= 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            ops.append(("del", a[i - 1], None)); i -= 1
        else:
            ops.append(("ins", None, b[j - 1])); j -= 1
    return ops[::-1]


def main():
    key = load_key()
    keychars = Counter("".join(key.values()))
    rows = load_inscriptions()
    recs, subs, ins, dels = [], Counter(), Counter(), Counter()
    unknown_sign = 0
    for r in rows:
        rd = (r.get("sanskrit") or "").strip()
        if not rd or rd.startswith("ref"):
            continue
        signs = text_signs(r["text"])
        if None in signs or any(s not in key for s in signs):
            unknown_sign += 1
            continue
        kv = "".join(key[s] for s in signs)
        kcons = [c for c in kv if c not in "aeiou"]
        rclean = rd.replace("-", " ")
        words = rclean.split()
        letters = [c for c in rclean if c != " "]
        rcons = [c for c in letters if c in SLP_CONS and c not in "MH"]  # anusvara/visarga as choices
        vow = [c for c in letters if c in SLP_VOW]
        mh = [c for c in letters if c in "MH"]
        # map reading consonants to the key's plain alphabet before aligning (deaspirate etc. are 'subs')
        ops = align(kcons, rcons)
        ns = sum(o[0] == "sub" for o in ops); ni = sum(o[0] == "ins" for o in ops); nd = sum(o[0] == "del" for o in ops)
        for o in ops:
            if o[0] == "sub": subs[(o[1], o[2])] += 1
            if o[0] == "ins": ins[o[2]] += 1
            if o[0] == "del": dels[o[1]] += 1
        recs.append(dict(id=r["id"], n_signs=len(signs), key_cons=len(kcons), read_cons=len(rcons),
                         vowels=len(vow), a_vowels=sum(v in "aA" for v in vow), breaks=len(words) - 1,
                         subs=ns, ins=ni, dels=nd, mh=len(mh)))
    N = len(recs)
    tot = {k: sum(r[k] for r in recs) for k in ["n_signs", "key_cons", "read_cons", "vowels", "a_vowels", "breaks", "subs", "ins", "dels", "mh"]}
    # bits of freedom: vowel slot choice among ~5 qualities x2 length ~ log2(10)=3.3 bits if unconstrained;
    # we report the conservative count (each vowel = at least 1 binary choice a vs not-a).
    per_reading = {k: round(v / N, 2) for k, v in tot.items()}
    exact = sum(r["subs"] == 0 and r["ins"] == 0 and r["dels"] == 0 for r in recs)
    choices = [r["subs"] + r["ins"] + r["dels"] + r["breaks"] + r["mh"] for r in recs]
    res = dict(n_readings=N, skipped_unreadable_or_unkeyed=unknown_sign, totals=tot, per_reading=per_reading,
               share_consonants_exact=round(exact / N, 3),
               consonant_edits_per_key_consonant=round((tot["subs"] + tot["ins"] + tot["dels"]) / tot["key_cons"], 3),
               a_share_of_vowels=round(tot["a_vowels"] / max(1, tot["vowels"]), 3),
               nonvowel_choices_per_reading=round(sum(choices) / N, 2),
               choices_per_sign=round((sum(choices) + tot["vowels"]) / tot["n_signs"], 2),
               top_subs=[[f"{a}->{b}", c] for (a, b), c in subs.most_common(25)],
               top_ins=ins.most_common(12), top_dels=dels.most_common(12))
    json.dump(res, open(OUT / "out" / "a1_free_choices.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items()}, indent=1)[:4000])


if __name__ == "__main__":
    main()
