"""Task #17 (H10): the frozen crib method of #26 (experiments/crib_attack_v2/method.py, unchanged)
run on REAL Linear Elamite, where the answer (Desset et al. 2022 values, as HLED transliteration
tokens) is known.  Pre-registered in docs/prereg/crib_le_known_answer.md.

Units = distinct LE words (space/line delimited) of 2-9 fully legible signs.  Sign identity = HLED
token (e.g. 'k' and 'k2' are different signs); true value = token without index digit.
All values are normalised s/š/ṣ -> s, ṭ -> t on both sides (attacker list and truth).
Run: board/run.sh .venv/bin/python -I experiments/crib_le_known_answer/le_run.py
"""
import sys, json, re, csv, itertools, time
from pathlib import Path
import numpy as np
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "crib_attack_v2"))
from method import NameIndex, Attack, shuffle_texts  # noqa  (frozen #26 method)
from names2 import capped_list  # noqa

HLED = ROOT / "sources/paragorth_Indus-/data/derived/linear-elamite-corpus-hled.json"
CAP = 30
NS = [20, 30, 45]
ANCHORS = [0, 3]
RULES = ["CV", "C"]           # attacker spelling rule: frozen CV rule (primary) / bare-C coda signs
SAMPLING = ["random", "seal"]  # random distinct words / 75% name-bearing (best case)
SUBSETS, SHUFFLES = 6, 20
V = set("aeiou")
TOK = re.compile(r"^[a-zšṣṭ]+[0-9]?$")


def norm(v):
    return re.sub(r"[0-9]", "", v).replace("š", "s").replace("ṣ", "s").replace("ṭ", "t")


def le_words():
    d = json.load(open(HLED))
    words = []
    for doc in d:
        for w in re.split(r"[\s|]+", doc["translit"]):
            if not w:
                continue
            parts = [re.sub(r"[⸢⸣\[\]]", "", p) for p in w.split("-")]
            if all(TOK.match(p) for p in parts) and 2 <= len(parts) <= 9:
                words.append(tuple(parts))
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); out.append(w)
    return out


def spell_items(units):
    ph = list(norm("".join(units)))
    items, i, n = [], 0, len(ph)
    vi = [j for j, p in enumerate(ph) if p in V]
    while i < n:
        p = ph[i]
        if p in V:
            items.append(("fix", p)); i += 1
        elif i + 1 < n and ph[i + 1] in V:
            items.append(("fix", p + ph[i + 1])); i += 2
        else:
            nxt = [j for j in vi if j > i]; prv = [j for j in vi if j < i]
            items.append(("free", p, p + (ph[nxt[0]] if nxt else ph[prv[-1]]))); i += 1
    return items


def spellings(units, rule, max_free=4):
    items = spell_items(units)
    free = [j for j, it in enumerate(items) if it[0] == "free"]
    if len(free) > max_free:
        return set()
    out = set()
    for mask in itertools.product((0, 1), repeat=len(free)):
        keep = dict(zip(free, mask)); sp = []
        for j, it in enumerate(items):
            if it[0] == "fix":
                sp.append(it[1])
            elif keep[j]:
                sp.append(it[1] if rule == "C" else it[2])
        out.add(tuple(sp))
    return {s for s in out if 2 <= len(s) <= 9}


def crib_list(path, rule, cap=CAP, col="syllables"):
    sp = set()
    for r in csv.DictReader(open(path, encoding="utf-8")):
        u = tuple(x for x in r[col].split(".") if x)
        vs = spellings(u, rule)
        if not vs:
            continue
        if len(sp | vs) > cap:
            break
        sp |= vs
    return sp


_C = {}


def setup():
    if _C:
        return _C
    words = le_words()
    signs = sorted({s for w in words for s in w})
    sid = {s: i for i, s in enumerate(signs)}
    lists = {}
    for rule in RULES:
        lists[(rule, "elamite")] = crib_list(HERE / "crib_names.csv", rule)
        lists[(rule, "akkadian")] = crib_list(ROOT / "experiments/onomasticon/short_Akkadian_top150.csv", rule,
                                              cap=len(lists[(rule, "elamite")]))
    vals = sorted({norm(s) for s in signs} | {x for sp in lists.values() for s in sp for x in s})
    vid = {v: i for i, v in enumerate(vals)}
    tk = np.array([vid[norm(s)] for s in signs], dtype=np.int32)
    ni = {k: NameIndex(sp, vid) for k, sp in lists.items()}
    wid = [[sid[s] for s in w] for w in words]
    # name-bearing words under the TRUE key, per rule (used only to compose the 'seal' sample)
    named = {}
    for rule in RULES:
        a = Attack(wid, ni[(rule, "elamite")], len(signs), len(vals), np.random.default_rng(0))
        named[rule] = [i for i in range(len(wid)) if a.windows[i] and a.text_hit(i, tk)]
    _C.update(words=words, signs=signs, wid=wid, tk=tk, vals=vals, ni=ni, lists=lists, named=named)
    return _C


def sample(rule, samp, n, sub):
    C = setup()
    rng = np.random.default_rng([17, RULES.index(rule), SAMPLING.index(samp), n, sub])
    allidx = np.arange(len(C["wid"]))
    if samp == "random":
        idx = rng.choice(allidx, size=n, replace=False)
    else:
        nm = np.array(C["named"][rule]); k = min(len(nm), int(round(0.75 * n)))
        a = rng.choice(nm, size=k, replace=False) if k else np.array([], int)
        rest = np.setdiff1d(allidx, nm)
        idx = np.concatenate([a, rng.choice(rest, size=n - k, replace=False)])
    return [C["wid"][i] for i in idx], rng


def job(args):
    rule, samp, n, a, sub, kind, rep = args
    C = setup()
    texts, rng = sample(rule, samp, n, sub)
    rng = np.random.default_rng([17, RULES.index(rule), SAMPLING.index(samp), n, a, sub,
                                 ["real", "wrong", "shuffle"].index(kind), rep])
    tk = C["tk"]
    toks = np.concatenate([np.asarray(t) for t in texts])
    cnt = np.bincount(toks, minlength=len(tk))
    present = np.flatnonzero(cnt > 0)
    anchors = {int(s): int(tk[s]) for s in present[np.argsort(-cnt[present], kind="stable")][:a]}
    if kind == "shuffle":
        texts = shuffle_texts(texts, rng)
    ni = C["ni"][(rule, "akkadian" if kind == "wrong" else "elamite")]
    att = Attack(texts, ni, len(tk), len(C["vals"]), rng, anchors=anchors)
    t0 = time.time()
    E, key = att.run(1500 + 60 * n, restarts=3)
    used = att.reading(key)
    corr = [s for s in used if key[s] == tk[s]]
    return dict(rule=rule, samp=samp, n=n, a=a, sub=sub, kind=kind, rep=rep, E=int(E),
                E_true=int(att.score(tk)) if kind != "shuffle" else None,
                n_matchable=len(att.matchable), n_used=len(used), n_correct=len(corr),
                n_signs=int(len(set(present.tolist()) - set(anchors))),
                correct_signs=[C["signs"][s] for s in corr], secs=round(time.time() - t0, 2))


def all_jobs():
    J = []
    for rule in RULES:
        for samp in SAMPLING:
            for n in NS:
                for a in ANCHORS:
                    for sub in range(SUBSETS):
                        J.append((rule, samp, n, a, sub, "real", 0))
                        J.append((rule, samp, n, a, sub, "wrong", 0))
                        J += [(rule, samp, n, a, sub, "shuffle", r) for r in range(SHUFFLES)]
    return J


if __name__ == "__main__":
    if "--describe" in sys.argv:  # corpus/list sizes only; no search, no E
        C = setup()
        print("distinct words 2-9 signs", len(C["words"]), "signs", len(C["signs"]))
        for k, sp in C["lists"].items():
            print(k, "spellings", len(sp))
        sys.exit()
    jl = HERE / "out" / "runs.jsonl"
    done = set()
    if jl.exists():
        for l in open(jl):
            r = json.loads(l); done.add((r["rule"], r["samp"], r["n"], r["a"], r["sub"], r["kind"], r["rep"]))
    jobs = [j for j in all_jobs() if j not in done]
    print("jobs left", len(jobs), flush=True)
    with Pool(2) as p, open(jl, "a") as fh:  # laptop limit: 2 workers
        for i, res in enumerate(p.imap_unordered(job, jobs, chunksize=4)):
            fh.write(json.dumps(res, ensure_ascii=False) + "\n"); fh.flush()
            if i % 500 == 0:
                print(i, flush=True)
    print("done", flush=True)
