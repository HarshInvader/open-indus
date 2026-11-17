"""Short crib lists as spellings in a simulated CV syllabary (task #26, H10).

The CV spelling rule is copied from experiments/crib_attack/names.py (task #3, H3) so the
frozen method does not depend on another agent's folder: a consonant before a vowel joins it
(CV sign); a lone vowel is a V sign; any other consonant (cluster, coda) is either dropped or
written C + echo vowel (the next vowel, else the previous one).

Lists (all local, built by #2 and #24): short_gulf_core, short_Elamite_core, short_Akkadian_top150,
short_Sumerian_top150 (attacker lists) and short_Amorite_top150 (wrong-language plant source).
Each list is capped at MAX_SPELLINGS spellings of 2-6 signs, taking names in file order.
"""
import csv, itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTS = {
    "gulf": ROOT / "experiments/onomasticon/short_gulf_core.csv",
    "elamite": ROOT / "experiments/elamite_names/short_Elamite_core.csv",
    "akkadian": ROOT / "experiments/onomasticon/short_Akkadian_top150.csv",
    "sumerian": ROOT / "experiments/onomasticon/short_Sumerian_top150.csv",
    "amorite": ROOT / "experiments/onomasticon/short_Amorite_top150.csv",
}
MAX_SPELLINGS = 200
V = set("aeiou")
MAP = {"š": "S", "ṣ": "Z", "ṭ": "T"}


def load_units(name):
    """List of unit tuples (one per row, duplicates removed, file order)."""
    out, seen = [], set()
    for r in csv.DictReader(open(LISTS[name], encoding="utf-8")):
        s = "".join(MAP.get(c, c) for c in r["syllables"].strip())
        u = tuple(x for x in s.split(".") if x)
        if u and all(x.isalpha() for x in u) and u not in seen:
            seen.add(u); out.append(u)
    return out


def _items(units):
    ph = list("".join(units)); n = len(ph)
    vi = [i for i, p in enumerate(ph) if p in V]
    if not vi:
        return None
    items, i = [], 0
    while i < n:
        p = ph[i]
        if p in V:
            items.append(("fix", p)); i += 1
        elif i + 1 < n and ph[i + 1] in V:
            items.append(("fix", p + ph[i + 1])); i += 2
        else:
            nxt = [j for j in vi if j > i]; prv = [j for j in vi if j < i]
            items.append(("free", p + (ph[nxt[0]] if nxt else ph[prv[-1]]))); i += 1
    return items


def cv_variants(units, max_free=4):
    items = _items(units)
    if items is None:
        return []
    free = [j for j, (k, _) in enumerate(items) if k == "free"]
    if len(free) > max_free:
        return []
    out = set()
    for mask in itertools.product((0, 1), repeat=len(free)):
        keep = dict(zip(free, mask))
        out.add(tuple(v for j, (k, v) in enumerate(items) if k == "fix" or keep[j]))
    return sorted(out)


def write_cv(units, rng, p_drop=0.5):
    items = _items(units)
    if items is None:
        return None
    return tuple(v for k, v in items if k == "fix" or rng.random() > p_drop)


def capped_list(name, kmin=2, kmax=6, cap=MAX_SPELLINGS):
    """(units kept, set of spellings) with at most `cap` spellings."""
    units, sp = [], set()
    for u in load_units(name):
        vs = {v for v in cv_variants(u) if kmin <= len(v) <= kmax}
        if not vs:
            continue
        if len(sp | vs) > cap:
            break
        units.append(u); sp |= vs
    return units, sp


if __name__ == "__main__":
    for nm in LISTS:
        u, sp = capped_list(nm)
        print(nm, "names", len(u), "spellings", len(sp), "k>=3", sum(len(s) >= 3 for s in sp),
              "values", len({x for s in sp for x in s}))
