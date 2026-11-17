"""Q2a. Sign inventory size: observed, Good-Turing coverage, Chao1 (tokens), Chao2 (incidence over distinct texts),
rarefaction by site, and comparison with other writing systems at matched sample size.

Comparison corpora are DATA files from sources/paragorth_Indus- (read only, no code executed):
  Latin (EDH, letters), Linear B (DAMOS, syllabograms + logograms), Linear A (SigLA-style JS, Unicode signs),
  Linear Elamite (HLED translit), Proto-Elamite (CDLI ATF signs, variants collapsed), Sumerian Ur III seal legends
  (CDLI, sign READINGS - an upper bound on sign identities because one sign can have several readings).
"""
import json
import math
import random
import re
from collections import Counter, defaultdict

import numpy as np

from common import ROOT, distinct, icit_texts, m77_texts, save_json, signs, site_norm

random.seed(20261114)
np.random.seed(20261114)
PG = ROOT / "sources/paragorth_Indus-"


def stats(texts):
    """texts: list of sign lists. Returns inventory estimators."""
    tok = Counter(); inc = Counter()
    for t in texts:
        tok.update(t); inc.update(set(t))
    N = sum(tok.values()); S = len(tok); T = len(texts)
    f1 = sum(1 for c in tok.values() if c == 1); f2 = sum(1 for c in tok.values() if c == 2)
    q1 = sum(1 for c in inc.values() if c == 1); q2 = sum(1 for c in inc.values() if c == 2)
    chao1 = S + f1 * (f1 - 1) / (2 * (f2 + 1))
    chao2 = S + (T - 1) / T * q1 * (q1 - 1) / (2 * (q2 + 1))
    # Chao1 variance (Chao 1987, bias-corrected form, approx) and log-normal CI
    def ci(est, a1, a2):
        if a2 == 0:
            a2 = 1
        r = a1 / a2
        var = a2 * (r ** 2 / 2 + r ** 3 + r ** 4 / 4)
        f0 = est - S
        if f0 <= 0:
            return (S, S)
        C = math.exp(1.96 * math.sqrt(math.log(1 + var / f0 ** 2)))
        return (S + f0 / C, S + f0 * C)
    # ACE (abundance coverage estimator, rare threshold 10)
    rare = {k: c for k, c in tok.items() if c <= 10}
    Nr = sum(rare.values()); Sr = len(rare); Sab = S - Sr
    C_ace = 1 - f1 / Nr if Nr else 1
    if C_ace > 0 and Nr > 1:
        g2 = max(Sr / C_ace * sum(i * (i - 1) * sum(1 for c in rare.values() if c == i) for i in range(1, 11)) / (Nr * (Nr - 1)) - 1, 0)
        ace = Sab + Sr / C_ace + f1 / C_ace * g2
    else:
        ace = float("nan")
    srt = sorted(tok.values(), reverse=True)
    cum = np.cumsum(srt) / N
    return {
        "texts": T, "tokens": N, "types": S, "hapax_f1": f1, "f2": f2, "hapax_share_types": f1 / S,
        "GT_coverage": 1 - f1 / N, "GT_unseen_mass": f1 / N,
        "chao1": chao1, "chao1_ci95": ci(chao1, f1, f2), "q1_one_text": q1, "q2_two_texts": q2,
        "chao2": chao2, "chao2_ci95": ci(chao2, q1, q2), "ACE": ace,
        "signs_for_50pct": int(np.searchsorted(cum, 0.5) + 1), "signs_for_80pct": int(np.searchsorted(cum, 0.8) + 1),
        "signs_for_90pct": int(np.searchsorted(cum, 0.9) + 1), "signs_for_95pct": int(np.searchsorted(cum, 0.95) + 1),
        "top10_share": sum(srt[:10]) / N,
    }


def rarefy(texts, checkpoints, reps=30):
    """Mean types seen after the first n tokens of a random text order."""
    out = defaultdict(list)
    for _ in range(reps):
        order = texts[:]
        random.shuffle(order)
        seen = set(); n = 0; ci = 0
        for t in order:
            for s in t:
                n += 1; seen.add(s)
                while ci < len(checkpoints) and n >= checkpoints[ci]:
                    out[checkpoints[ci]].append(len(seen)); ci += 1
        while ci < len(checkpoints):
            ci += 1
    return {c: (float(np.mean(v)), float(np.std(v))) for c, v in out.items() if len(v) == reps}


def subsample(texts, N):
    order = texts[:]
    random.shuffle(order)
    out, n = [], 0
    for t in order:
        if n >= N:
            break
        out.append(t); n += len(t)
    return out


# ---------------- comparison corpora ----------------
def jl(p):
    return [json.loads(l)["seq"] for l in open(p)]


def comp_corpora():
    C = {}
    lat = jl(PG / "data/codelib/latin_edh.jsonl")
    C["Latin letters (alphabet)"] = [[ch for ch in "".join(t) if ch.isalpha()] for t in lat]
    lb = []
    syl = re.compile(r"^(?:[a-z]{1,3}[23]?|\*\d+)$")
    logo = re.compile(r"^[A-Z][A-Z]*(?:\+[A-Z]+)?(?::[mfx])?$|^\*\d+VAS$")
    for t in jl(PG / "data/codelib/linear_b.jsonl"):
        s = []
        for w in t:
            w = re.sub(r"[\u0323\u2e22\u2e23\u231c\u231d\u231e\u231f\[\]?<>]", "", w)
            parts = w.split("-") if "-" in w or re.fullmatch(r"[a-z0-9*]+", w) else [w]
            for x in parts:
                if syl.match(x) or (logo.match(x) and x not in ("NUM", "X")):
                    s.append(x)
        if s:
            lb.append(s)
    C["Linear B (syllabary+logograms)"] = lb
    pe = []
    for t in jl(PG / "data/codelib/proto_elamite.jsonl"):
        s = [re.sub(r"~[a-z0-9]+", "", x) for x in t]
        s = [x for x in s if x and "X" not in x]
        if s:
            pe.append(s)
    C["Proto-Elamite (signs+numeral types)"] = pe
    ur = []
    for t in jl(PG / "data/codelib/ur3_legends.jsonl"):
        s = []
        for w in t:
            w = w.replace("_", "").lower()
            w = re.sub(r"\{([^}]*)\}", r"-\1-", w)
            s += [x for x in re.split(r"[-.\s]+", w) if x and x not in ("x", "...", "[", "]")]
        if s:
            ur.append(s)
    C["Sumerian Ur III seal legends (sign readings)"] = ur
    # Linear A
    js = open(PG / "other-scripts/linear-a/data/LinearAInscriptions.js", encoding="utf-8").read()
    LA = []
    for m in re.finditer(r'"parsedInscription":\s*"((?:[^"\\]|\\.)*)"', js):
        s = [ch for ch in m.group(1) if 0x10600 <= ord(ch) <= 0x1077F]
        if s:
            LA.append(s)
    C["Linear A (Unicode signs)"] = LA
    return C


res = {}
T_all = [t for t in m77_texts()]
T_d = distinct(T_all)
res["M77_all_objects"] = stats([signs(t["seq"]) for t in T_all])
res["M77_distinct"] = stats([signs(t["seq"]) for t in T_d])
for site in ["Mohenjodaro", "Harappa", "Lothal", "Kalibangan", "Chanhudaro"]:
    res[f"M77_distinct_{site}"] = stats([signs(t["seq"]) for t in T_d if t["site"] == site])
for ot in ["seal", "sealing", "miniature tablet", "copper tablet", "pottery graffito"]:
    res[f"M77_distinct_{ot}"] = stats([signs(t["seq"]) for t in T_d if t["object_type"] == ot])

I = distinct(icit_texts())
res["ICIT_distinct"] = stats([signs(t["seq"]) for t in I])
for site in ["Mohenjo-daro", "Harappa", "Dholavira", "Lothal", "Kalibangan"]:
    res[f"ICIT_distinct_{site}"] = stats([signs(t["seq"]) for t in I if t["site"] == site])

# merged list (shaunmortal v3 allograph merges, 16 merges) for sensitivity
mer = {"M%s" % k: "M%s" % v for k, v in json.load(open(ROOT / "sources/shaunmortal_indus/data/model4_merges_v3.json")).items()}
res["M77_distinct_v3merged"] = stats([[mer.get(s, s) for s in signs(t["seq"])] for t in T_d])

# site rarefaction at common token counts
cps = [250, 500, 1000, 2000, 3000, 4000, 6000, 8000, 9000]
rf = {}
for site in ["Mohenjodaro", "Harappa", "Lothal", "Kalibangan"]:
    rf["M77_" + site] = rarefy([signs(t["seq"]) for t in T_d if t["site"] == site], cps)
rf["M77_all_distinct"] = rarefy([signs(t["seq"]) for t in T_d], cps)
for site in ["Mohenjo-daro", "Harappa", "Dholavira"]:
    rf["ICIT_" + site] = rarefy([signs(t["seq"]) for t in I if t["site"] == site], cps)
res["rarefaction_types_at_tokens"] = rf

# ---------------- comparison with other scripts at matched sample size ----------------
C = comp_corpora()
Nm = res["M77_distinct"]["tokens"]
comp = {}
indus = [signs(t["seq"]) for t in T_d]
for name, texts in list(C.items()) + [("Indus M77 distinct", indus), ("Indus ICIT distinct", [signs(t["seq"]) for t in I])]:
    ntok = sum(map(len, texts))
    row = {"corpus_texts": len(texts), "corpus_tokens": ntok, "corpus_types": len({s for t in texts for s in t}),
           "mean_len": ntok / max(len(texts), 1)}
    for N in (2000, 5000, Nm):
        if ntok >= N:
            subs = [stats(subsample(texts, N)) for _ in range(10)]
            row[f"at_{N}"] = {k: float(np.mean([s[k] for s in subs])) for k in
                              ("types", "hapax_share_types", "GT_coverage", "chao2", "signs_for_90pct", "top10_share")}
    comp[name] = row
res["comparison_scripts"] = comp

save_json("q2_inventory", res)
for k, v in res.items():
    if k.startswith(("M77", "ICIT")):
        print(k, {x: (round(v[x], 3) if isinstance(v[x], float) else v[x]) for x in
                  ("texts", "tokens", "types", "hapax_f1", "GT_coverage", "chao1", "chao2", "chao2_ci95", "ACE", "signs_for_90pct")})
print(json.dumps(rf, indent=0)[:3000])
print(json.dumps(comp, indent=1))
