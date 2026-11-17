"""Score the frozen predictions (docs/prereg/2026-11-14_new_finds_predictions.md) on new_texts.csv.
    .venv/bin/python experiments/new_finds/score.py
Primary set: scored == yes. Sensitivity set: also texts with any readable sign (scored no but seq present,
status new or possible_known), uncertain marks '?' stripped. Writes results.json."""
import csv, json, sys, re
from pathlib import Path
from math import sqrt
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "new_finds"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments" / "functional_reading"))
from scipy.stats import binomtest
REF = json.load(open(OUT / "ref_tables.json")); B = json.load(open(OUT / "baselines.json"))
TICK = {"M60", "M66", "M68", "M71", "M73"}; PLAIN = {"M59", "M65", "M67", "M70", "M72", "M75"}
FISH = TICK | PLAIN | {"M61", "M62", "M63", "M64", "M69", "M74"}; PART = {"M53", "M387", "M343", "M171", "M389"}
rows = list(csv.DictReader(open(OUT / "new_texts.csv")))


def seq_of(r):
    return [s.rstrip("?") for s in r["seq_M"].split() if re.fullmatch(r"M\d+\??", s)]


def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def prop(k, n, minn):
    return dict(k=k, n=n, share=round(k / n, 3) if n else None, ci=wilson(k, n), evaluable=n >= minn)


def score(texts):
    R = {}; comp = [t for t in texts if len(t) >= 2]
    seals = [t for t, r in zip(texts, SETROWS) if len(t) >= 2 and r["object_type"].startswith("seal")]
    k = sum(t[-1] == "M342" or t[-2:] == ["M342", "M176"] for t in seals)
    R["P1"] = prop(k, len(seals), 8)
    if R["P1"]["evaluable"]:
        R["P1"]["pass"] = 0.2 <= R["P1"]["share"] <= 0.6 and R["P1"]["ci"][0] <= 0.38 <= R["P1"]["ci"][1]
    jt = [(i, t) for t in texts for i, s in enumerate(t) if s == "M342"]
    k = sum(i == len(t) - 1 or (i == len(t) - 2 and t[-1] == "M176") for i, t in jt)
    R["P1c"] = prop(k, len(jt), 5); R["P1c"]["pass"] = R["P1c"]["evaluable"] and R["P1c"]["share"] >= 0.65
    agree = n = 0
    for t in texts:
        for a, b in zip(t, t[1:]):
            if f"{a} {b}" in REF["ref_pairs"]: agree += 1; n += 1
            elif f"{b} {a}" in REF["ref_pairs"]: n += 1
    R["P2"] = prop(agree, n, 8)
    if n:
        R["P2"]["p_vs_0.5"] = binomtest(agree, n, 0.5, alternative="greater").pvalue
        R["P2"]["pass"] = R["P2"]["evaluable"] and R["P2"]["share"] >= 0.75 and R["P2"]["p_vs_0.5"] < 0.05
    tk = [(i, t) for t in texts for i, s in enumerate(t) if s in TICK]
    R["P3"] = prop(sum(i == len(t) - 1 for i, t in tk), len(tk), 3)
    m109 = [(i, t) for t in texts for i, s in enumerate(t) if s == "M109" and i < len(t) - 1]
    R["P4"] = prop(sum(t[i + 1] == "M59" for i, t in m109), len(m109), 2)
    # P5 parse with the frozen grammar (only if >= 10 texts, to avoid loading the model needlessly)
    R["P5"] = dict(n=len(comp), evaluable=len(comp) >= 10)
    if comp:
        import fr
        _, _, _, lex, comps, G = fr.load_model()
        acc = [G.accepts({"seq": t}) for t in comp]
        R["P5"].update(k=sum(acc), share=round(sum(acc) / len(acc), 3), ci=wilson(sum(acc), len(acc)))
    first = [t[0] for t in comp]; last = [t[-1] for t in comp]
    R["P6"] = prop(sum(s in REF["first"] for s in first), len(first), 8)
    R["P7"] = prop(sum(s in REF["last"] for s in last), len(last), 8)
    toks = [s for t in texts for s in t]
    R["P8"] = prop(sum(s in REF["inventory"] for s in toks), len(toks), 30)
    op = [(i, t) for t in comp for i, s in enumerate(t) if s in ("M267", "M391")]
    R["P9"] = prop(sum(i == 0 for i, t in op), len(op), 4)
    c176 = [(i, t) for t in texts for i, s in enumerate(t) if s == "M176"]
    R["P10"] = prop(sum(i == len(t) - 1 for i, t in c176), len(c176), 3)
    R["P11"] = dict(n=len(texts), mean_len=round(sum(map(len, texts)) / len(texts), 2) if texts else None,
                    evaluable=len(texts) >= 8)
    fp = [(a, b) for t in texts for a, b in zip(t, t[1:]) if (a in FISH) != (b in FISH)]
    R["P13"] = prop(sum((b if a in FISH else a) in PART for a, b in fp), len(fp), 8)
    R["P14_fish_first"] = prop(sum(a in FISH for a, b in fp), len(fp), 1)
    return R


prim = [r for r in rows if r["scored"] == "yes"]
sens = [r for r in rows if r["status"] in ("new", "possible_known") and seq_of(r)]
dirs = [r for r in rows if r["status"] == "new" and r["direction"].startswith("R-L")]
out = {"n_rows": len(rows), "n_candidate_objects_checked": 190,
       "status_counts": {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})},
       "P12_direction": dict(n_determinable=len(dirs), rl=len(dirs), evaluable=len(dirs) >= 8)}
for name, S in (("primary", prim), ("sensitivity_all_readable", sens)):
    SETROWS = S
    texts = [seq_of(r) for r in S]
    out[name] = dict(n_texts=len(texts), texts={r["obj_id"]: seq_of(r) for r in S}, scores=score(texts))
ev = [k for k, v in out["primary"]["scores"].items() if isinstance(v, dict) and v.get("evaluable") and k.startswith("P") and k[1:].isdigit()]
out["primary"]["n_evaluable_predictions"] = len(ev)
out["verdict"] = "untestable: no frozen prediction reached its minimum n" if not ev else "see scores"
json.dump(out, open(OUT / "results.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float)[:4000])
