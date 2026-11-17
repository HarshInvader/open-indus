"""Name lists as sound strings and as spellings in two simulated scripts.

Script A ("CV"): a Linear-B-like CV syllabary. A consonant before a vowel joins it (CV sign);
a vowel with no consonant before it is a V sign; any other consonant (cluster, coda) is
either dropped or written C + echo vowel (the next vowel, else the previous one).
Script B ("CVC"): cuneiform-like units; each transliterated sign value (index digits and
determinatives removed) is one sign (CV, VC, CVC or V).

Sources (local, already in the repo): Ur III seal-legend personal names (paragorth codelib,
via experiments/typology/corpora.py) and Linear B personal names (DAMOS, same loader).
"""
import re, sys, itertools
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments" / "typology"))
from corpora import ur3_names, linear_b_names  # noqa

V = set("aeiou")
BAD = set("x(|.+:@…&*")


def _unit(s):
    s = s.replace("sz", "S").replace("t,", "T").replace("s,", "Z")
    s = re.sub(r"[0-9]", "", s)
    return s


def ur3_units():
    """{tuple(units): count}; determinatives dropped, damaged names dropped."""
    out = {}
    for k, c in ur3_names().items():
        if any(ch in BAD for s in k for ch in s):
            continue
        u = tuple(_unit(s) for s in k if not s.startswith("{"))
        if not u or any(not x or not re.fullmatch(r"[a-zA-Z]+", x) for x in u):
            continue
        out[u] = out.get(u, 0) + c
    return out


def linb_units():
    out = {}
    for k, c in linear_b_names().items():
        if any(ch in BAD or ch.isdigit() for s in k for ch in s):
            continue
        out[k] = out.get(k, 0) + c
    return out


def phonemes(units):
    return list("".join(units))


def cv_variants(units, max_free=4):
    """All script-A spellings of a name: list of tuples of CV/V values."""
    ph = phonemes(units)
    n = len(ph)
    vowel_idx = [i for i, p in enumerate(ph) if p in V]
    if not vowel_idx:
        return []
    items = []  # (kind, value): kind 'fix' or 'free'
    i = 0
    while i < n:
        p = ph[i]
        if p in V:
            items.append(("fix", p)); i += 1
        elif i + 1 < n and ph[i + 1] in V:
            items.append(("fix", p + ph[i + 1])); i += 2
        else:
            nxt = [j for j in vowel_idx if j > i]
            prv = [j for j in vowel_idx if j < i]
            ev = ph[nxt[0]] if nxt else ph[prv[-1]]
            items.append(("free", p + ev)); i += 1
    free = [j for j, (k, _) in enumerate(items) if k == "free"]
    if len(free) > max_free:
        return []
    out = set()
    for mask in itertools.product((0, 1), repeat=len(free)):
        keep = dict(zip(free, mask))
        out.add(tuple(v for j, (k, v) in enumerate(items) if k == "fix" or keep[j]))
    return sorted(out)


def write_cv(units, rng, p_drop=0.5):
    ph = phonemes(units)
    vs = cv_variants(units, max_free=99)
    if not vs:
        return None
    # sample: rebuild with random choices (same rule as cv_variants)
    n = len(ph); vowel_idx = [i for i, p in enumerate(ph) if p in V]
    out, i = [], 0
    while i < n:
        p = ph[i]
        if p in V:
            out.append(p); i += 1
        elif i + 1 < n and ph[i + 1] in V:
            out.append(p + ph[i + 1]); i += 2
        else:
            nxt = [j for j in vowel_idx if j > i]; prv = [j for j in vowel_idx if j < i]
            ev = ph[nxt[0]] if nxt else ph[prv[-1]]
            if rng.random() > p_drop:
                out.append(p + ev)
            i += 1
    return tuple(out)


def spellings(units_dict, script, kmin=2, kmax=6):
    """Attacker's candidate list: {spelling tuple} over all names (all variants for script A)."""
    out = set()
    for u in units_dict:
        vs = cv_variants(u) if script == "A" else [tuple(u)]
        for v in vs:
            if kmin <= len(v) <= kmax:
                out.add(v)
    return out


if __name__ == "__main__":
    u = ur3_units(); l = linb_units()
    print("ur3 names", len(u), "linb names", len(l))
    for s in "AB":
        su = spellings(u, s); sl = spellings(l, s)
        vals = {x for v in su for x in v}
        print(s, "ur3 spellings", len(su), "values", len(vals), "| linb spellings", len(sl),
              "values", len({x for v in sl for x in v}), "shared", len(vals & {x for v in sl for x in v}))
