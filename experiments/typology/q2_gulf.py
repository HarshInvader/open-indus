"""Q2. Gulf round/cylinder seals: after removing person and number signs, do they use a small, repetitive
sign subset (as foreign names spelled phonetically would)?  Pre-registered in docs/prereg/2026-11-14_typology.md.

Run: .venv/bin/python experiments/typology/q2_gulf.py
"""
import sys, json, csv, re
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from corpus.load import icit_texts, m77_texts, distinct  # noqa
from corpora import ur3_names, linear_b_names  # noqa

rng = np.random.default_rng(2026)
NDRAW = 10000
FOREIGN_WEST = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar",
                "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Dilmun", "Kalba"}
FOREIGN_ALL = FOREIGN_WEST | {"Gonur", "Gonur Depe", "Altyn Depe", "Shortughai"}
ROUND = ("SEAL:R", "SEAL:C", "SEAL:CY")


def wnum(s):
    return int(s[1:]) if re.fullmatch(r"W\d+", s) else None


def is_person(s):
    n = wnum(s); return n is not None and 90 <= n <= 175


def is_num(s):
    n = wnum(s); return n is not None and 1 <= n <= 59


def clean(seq):
    return [s for s in seq if s not in ("|", "#")]


def residue(seq, strip=True):
    return [s for s in clean(seq) if not (strip and (is_person(s) or is_num(s)))]


# ---------------------------------------------------------------- Gulf set
def gulf_set(conf_only=False):
    out = {}
    if not conf_only:
        for t in icit_texts():
            if t["site"] in FOREIGN_WEST and t["type"] in ROUND:
                sq = tuple(clean(t["seq"]))
                if sq:
                    out[sq] = dict(src="ICIT", site=t["site"], type=t["type"], conf="icit")
    for r in csv.DictReader(open(ROOT / "sources/paragorth_Indus-/data/gulf_seals.csv")):
        if r["found_abroad"] != "True" or not r["sequence_glyph_coding"]:
            continue
        if conf_only and r["confidence"] not in ("confirmed", "probable"):
            continue
        sq = tuple(f"W{int(x):03d}" for x in r["sequence_glyph_coding"].split("-"))
        if sq not in out:
            out[sq] = dict(src=f"gulf_seals#{r['seal_no']}", site=r["site"], type="round", conf=r["confidence"])
        else:
            out[sq]["conf"] = r["confidence"]
    return out


def home_texts(kind="seal"):
    H = []
    for t in distinct(icit_texts()):
        if t["site"] in FOREIGN_ALL or t["site"] == "Unknown":
            continue
        if kind == "seal" and not t["type"].startswith("SEAL"):
            continue
        if kind == "round" and t["type"] not in ROUND:
            continue
        H.append(t["seq"])
    return H


# ---------------------------------------------------------------- statistics
def stats(res):
    toks = [s for r in res for s in r]
    pairs = [(a, b) for r in res for a, b in zip(r, r[1:])]
    sets = [set(r) for r in res]
    jac = [len(a & b) / len(a | b) for a, b in combinations(sets, 2)]
    return dict(G1_types_per_token=len(set(toks)) / len(toks),
                G2_any_repeat=float(np.mean([len(set(r)) < len(r) for r in res])),
                G3_adjacent_redup=sum(a == b for a, b in pairs) / max(1, len(pairs)),
                G4_jaccard=float(np.mean(jac)))


DIRECTION = dict(G1_types_per_token=-1, G2_any_repeat=+1, G3_adjacent_redup=+1, G4_jaccard=+1)


def matched_test(gres, home_res, label, ndraw=NDRAW):
    bylen = defaultdict(list)
    for r in home_res:
        if r:
            bylen[min(len(r), 5)].append(r)
    keys = [min(len(r), 5) for r in gres]
    obs = stats(gres)
    draws = defaultdict(list)
    for _ in range(ndraw):
        smp = [bylen[k][rng.integers(len(bylen[k]))] for k in keys]
        for k, v in stats(smp).items():
            draws[k].append(v)
    out = {}
    print(f"\n{label}: n Gulf residues = {len(gres)}, tokens {sum(map(len, gres))}; home pool {sum(map(len, bylen.values()))}")
    for k, v in obs.items():
        d = np.array(draws[k])
        p = (1 + ((d <= v) if DIRECTION[k] < 0 else (d >= v)).sum()) / (ndraw + 1)
        out[k] = dict(gulf=v, home_mean=float(d.mean()), home_95=[float(np.quantile(d, .025)), float(np.quantile(d, .975))], p=float(p))
        print(f"  {k:20s} Gulf {v:.3f}  home {d.mean():.3f} [{np.quantile(d,.025):.3f}, {np.quantile(d,.975):.3f}]  p = {p:.4f}")
    return out


def pattern(seq):
    m = {}; return "".join(m.setdefault(s, "ABCDEFGHIJ"[len(m)]) for s in seq)


def main():
    R = {}
    G = gulf_set()
    print(f"Gulf set: {len(G)} distinct sequences")
    for sq, meta in G.items():
        print(f"  {meta['src']:16s} {meta['site'][:28]:28s} {meta['conf']:10s} {' '.join(sq):45s} -> residue {' '.join(residue(sq))}")
    gres_all = [residue(sq) for sq in G]
    gres = [r for r in gres_all if r]
    print(f"empty residues dropped: {len(gres_all) - len(gres)}")
    home = [residue(s) for s in home_texts("seal")]
    R["primary"] = matched_test(gres, home, "PRIMARY: Gulf residues vs length-matched home seal residues")

    # robustness
    Gc = gulf_set(conf_only=True)
    R["conf_only"] = matched_test([r for r in (residue(s) for s in Gc) if r], home, "ROBUST: gulf_seals confirmed/probable only")
    R["home_round"] = matched_test(gres, [residue(s) for s in home_texts("round")], "ROBUST: baseline = home round/cylinder seals")
    R["no_strip"] = matched_test([residue(s, False) for s in G], [residue(s, False) for s in home_texts("seal")],
                                 "ROBUST: no person/number removal")
    # sign-share of person+number signs
    tok = [s for sq in G for s in sq]; htok = [s for s in home_texts("seal") for s in clean(s)]
    R["person_number_share"] = dict(gulf=float(np.mean([is_person(s) or is_num(s) for s in tok])),
                                    home=float(np.mean([is_person(s) or is_num(s) for s in htok])),
                                    gulf_person=float(np.mean([is_person(s) for s in tok])),
                                    home_person=float(np.mean([is_person(s) for s in htok])))
    print("\nperson+number token share: Gulf {gulf:.3f} vs home seals {home:.3f}; person signs alone {gulf_person:.3f} vs {home_person:.3f}".format(**R["person_number_share"]))

    # M77 replication: West Asian finds vs M77 home seals; person = M1-M47 anthropomorph range is not
    # defined in M77 numbering, so strip only stroke numerals (M86-M121) and M1 (man).
    STROKE = {f"M{i}" for i in range(86, 123)}
    def m77res(seq):
        return [s for s in clean(seq) if s not in STROKE and s != "M1"]
    m77 = distinct(m77_texts())
    wa = [m77res(t["seq"]) for t in m77 if t["site"] == "West Asian finds"]
    mh = [m77res(t["seq"]) for t in m77 if t["site"] != "West Asian finds" and t["object_type"] == "seal"]
    R["m77_west_asian"] = matched_test([r for r in wa if r], mh, "ROBUST: M77 West Asian finds (all shapes) vs M77 home seals")

    # candidate syllabogram set
    gc = Counter(s for r in gres for s in set(r))
    hc = Counter(s for r in home if r for s in set(r)); nh = sum(1 for r in home if r)
    cand = []
    for s, n in gc.most_common():
        if n >= 2:
            rate_g = n / len(gres); rate_h = (hc[s] + 0.5) / (nh + 1)
            cand.append(dict(sign=s, gulf_texts=n, gulf_rate=rate_g, home_rate=rate_h, ratio=rate_g / rate_h))
    cand.sort(key=lambda d: -d["ratio"])
    R["candidates"] = cand
    print("\ncandidate set (residue signs in >= 2 distinct Gulf texts):")
    for c in cand:
        print(f"  {c['sign']}  Gulf texts {c['gulf_texts']:2d} ({c['gulf_rate']:.2f})  home rate {c['home_rate']:.3f}  ratio {c['ratio']:.1f}")
    single = sum(1 for s, n in gc.items() if n == 1)
    print(f"  residue sign types used once only: {single} of {len(gc)}")

    # name shapes
    def syllabic_ur(n):
        logos = {"ur", "lu2", "lugal", "nin", "e2", "dingir", "szesz", "ab", "ad", "sa6", "kal", "mes", "nig2", "inim", "gu", "za"}
        return "{" not in "".join(n) and all(re.fullmatch(r"[^aeiu\d]{0,2}[aeiu][^aeiu\d]?\d?", s) for s in n) and n[0] not in logos
    ur = [n for n in ur3_names() if 2 <= len(n) <= 5 and syllabic_ur(n)]
    lb = [n for n in linear_b_names() if 2 <= len(n) <= 5]
    homeL = [r for r in home if 2 <= len(r) <= 5]
    def shape(cores, label):
        P = Counter(pattern(c) for c in cores); n = len(cores)
        rep = np.mean([len(set(c)) < len(c) for c in cores]); adj = np.mean([any(a == b for a, b in zip(c, c[1:])) for c in cores])
        Ld = Counter(len(c) for c in cores)
        print(f"  {label:42s} n={n:5d} any-repeat {rep:.3f} adjacent {adj:.3f} len {dict(sorted(Ld.items()))} top patterns {P.most_common(5)}")
        return dict(n=n, any_repeat=float(rep), adjacent=float(adj), patterns=dict(P.most_common(10)))
    print("\nname shapes (length 2-5):")
    gL = [r for r in gres if 2 <= len(r) <= 5]
    R["shapes"] = dict(gulf=shape(gL, "Gulf residues"), home=shape(homeL, "home seal residues"),
                       ur3_syllabic=shape(ur, "Ur III syllabically spelled names"), linb=shape(lb, "Linear B person names"))
    print("  Gulf residue patterns:", [(" ".join(r), pattern(r)) for r in gres])
    # Meluhha attestations: personal names in the same line as me-luh-ha
    att = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/cdli-meluhha-attestations.json"))
    names = Counter()
    for a in att:
        for ctx in a.get("ctx", []):
            for line in ctx.split(" / "):
                if "me-luh-ha" in line:
                    for m in re.finditer(r"(\S+) dumu me-luh-ha", line):
                        names[m.group(1)] += 1
                    for m in re.finditer(r"me-luh-ha(?:-ta|-sze3|-ke4)?\s+(\S+-\S+)", line):
                        if not m.group(1).startswith(("dumu", "ta", "sze3")):
                            names["after:" + m.group(1)] += 1
    R["meluhha_names"] = dict(names.most_common(30))
    print("\nnames in Meluhha lines ('X dumu me-luh-ha' and words after me-luh-ha):", names.most_common(20))
    json.dump(R, open(HERE / "q2_gulf.json", "w"), indent=1)
    print("wrote", HERE / "q2_gulf.json")


if __name__ == "__main__":
    main()
