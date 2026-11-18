"""Step 2: consensus corpus and either-edition corpora, all in Mahadevan (M77) sign space so the nine
headline tests run unchanged. Pre-registered in docs/prereg/consensus_corpus.md.

Links between an M77 object side and an ICIT record:
  reg  the 469 register-matched texts (audit_followups B; linked through excavation registers, not signs).
  seq  every other M77 side: the best ICIT record from the same site (M77 'Other sites'/'West Asian finds':
       any site outside the five big ones) by normalised alignment distance under the corrected concordance,
       accepted if <= 0.5. Linked by signs, so biased toward agreement (stated in RESULTS).
  ext  = reg + seq.

Alignment: corrected primary concordance + doubled-sign rule (disagree.align_text).

Corpora (each a list of records dict(seq, object_type, site, complete, key0), key0 = original M77 seq string,
which fixes split-v2 held-out membership; plus T5 direction lines):
  base            M77 as published.
  cons_sign_reg   reg texts: every sign the editions disagree on becomes '#'; other texts unchanged.
  cons_sign_ext   PRIMARY consensus. ext texts masked as above; texts with no link dropped.
  cons_text_ext   ext texts with no disagreement only (strict); unlinked dropped.
  icit_reg        reg texts take ICIT's reading (mapped to M space); others M77.
  icit_ext        ext texts take ICIT's reading; others M77.   (with base = the either-edition pair)
  match_m77       the reg texts only, M77 reading.
  match_icit      the reg texts only, ICIT reading.

    board/run.sh .venv/bin/python -I experiments/consensus_corpus/corpora.py      # writes out/corpora/*.json
"""
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "audit_followups"))
import b_editor_agreement as B  # noqa
from disagree import align_text, merge_doubles  # noqa
from cooc import matched_pairs  # noqa
from corpus.load import m77_texts, m77_lines, icit_texts  # noqa

SEQ_CUT = 0.5
SITE = {"Mohenjodaro": "Mohenjo-daro", "Chanhudaro": "Chanhu-daro"}
BIG = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}
IDIR = {"R/L": "rl", "L/R": "lr", "R/l": "rl"}
OUT = HERE / "out" / "corpora"


def conc():
    c = json.load(open(HERE / "out" / "concordance.json"))
    return c["primary"], c["doubles_primary"]


def inverse(mp, dbl, freq):
    inv = defaultdict(list)
    for m, ws in mp.items():
        for w in ws: inv[w].append([m])
    for m, ws in dbl.items():
        for w in ws: inv[w].append([m, m])
    return {w: max(c, key=lambda ms: freq[ms[0]]) for w, c in inv.items()}


def to_m(iseq, ops, inv):
    """ICIT seq -> M space. Aligned matches use M77's own sign; other W via the inverse concordance;
    a W with no M partner keeps its W label (an unknown sign in M space)."""
    own = defaultdict(list)
    for k, m, w, _ in ops:
        if k == "match": own[w].append(m)
    out = []
    for s in iseq:
        if s in ("|", "#"):
            out.append(s); continue
        if own.get(s):
            m = own[s].pop(0); out += m.split("+")
        elif s in inv:
            out += inv[s]
        else:
            out.append(s)
    return out


def mask(mseq, iseq, ops, dbl):
    """M77 seq with every disputed sign replaced by '#'; an ICIT-only sign adds a '#' at its position.
    Signs with no concordance entry (sub_unmapped) are unverifiable, not disputed: kept."""
    fl = B.flat(mseq)
    toks = merge_doubles(fl, B.flat(iseq), dbl)
    tokpos, j = [], 0
    for t in toks:
        n = 2 if "+" in t else 1
        tokpos.append(list(range(j, j + n))); j += n
    bad, bad_before = set(), set()
    for k, m, w, i in ops:
        if k in ("sub", "m77_extra"):
            bad.update(tokpos[i])
        elif k == "transpose":
            bad.update(tokpos[i]); bad.update(tokpos[i + 1])
        elif k == "icit_extra":
            bad_before.add(tokpos[i][0] if i < len(tokpos) else len(fl))
    res, f = [], 0
    for s in mseq:
        if s in ("|", "#"):
            res.append(s); continue
        if f in bad_before: res.append("#")
        res.append("#" if f in bad else s); f += 1
    if len(fl) in bad_before: res.append("#")
    out = []
    for s in res:
        if s == "#" and out and out[-1] == "#": continue
        out.append(s)
    return out, bool(bad or bad_before)


def disagrees(ops):
    return any(o[0] in ("sub", "m77_extra", "icit_extra", "transpose") for o in ops)


def seq_links(mp, dbl, skip):
    icit = icit_texts()
    by_site = defaultdict(list)
    for it in icit:
        if B.flat(it["seq"]): by_site[it["site"]].append(it)
    other = [it for s, v in by_site.items() if s not in BIG for it in v]
    mapped = lambda s: set(mp.get(s, []))
    links = {}
    for t in m77_texts():
        key = (t["text_no"], t["side"])
        a = B.flat(t["seq"])
        if key in skip or not a: continue
        site = SITE.get(t["site"], t["site"])
        cands = by_site[site] if site in BIG else other
        aw = set().union(*[mapped(s) for s in a]) | {w for s in a for w in dbl.get(s, [])}
        best = None
        for it in cands:
            b = B.flat(it["seq"])
            if abs(len(b) - len(a)) > max(2, len(a) // 2) or not (aw & set(b)): continue
            d, ops, drev, na, nb = align_text(t["seq"], it["seq"], mp, dbl)
            nd = d / max(na, nb)
            if best is None or nd < best[0]: best = (nd, it, ops, d, drev)
        if best and best[0] <= SEQ_CUT:
            links[key] = dict(icit=best[1]["id"], norm=best[0], ops=best[2], rev_better=best[4] < best[3])
    return links


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mp, dbl = conc()
    freq = Counter(s for t in m77_texts() for s in t["seq"] if s not in "|#")
    inv = inverse(mp, dbl, freq)
    icit = {t["id"]: t for t in icit_texts()}
    reg = {}
    for p, mt, it in matched_pairs():
        d, ops, drev, na, nb = align_text(mt["seq"], it["seq"], mp, dbl)
        reg[(mt["text_no"], mt["side"])] = dict(icit=it["id"], norm=p["norm"], ops=ops, rev_better=drev < d)
    cache = HERE / "out" / "seq_links.json"
    if cache.exists():
        seq = {tuple(json.loads(k)): v for k, v in json.load(open(cache)).items()}
    else:
        seq = seq_links(mp, dbl, set(reg))
        json.dump({json.dumps(list(k)): v for k, v in seq.items()}, open(cache, "w"))
    ext = {**seq, **reg}
    m77 = m77_texts()
    lines_by = defaultdict(list)
    for l in m77_lines():
        d = {"right-to-left": "rl", "left-to-right": "lr"}.get(l["direction"])
        if d:
            for sg in l["segments"]:
                if len(sg) >= 2: lines_by[(l["text_no"], l["side"])].append((d, tuple(sg)))

    def rec(t, seq, complete=None):
        return dict(seq=list(seq), object_type=t["object_type"], site=t["site"],
                    complete=t["complete"] if complete is None else complete, key0=" ".join(t["seq"]))

    def icit_lines(key, L):
        it = icit[L["icit"]]; d = IDIR.get(it["direction"])
        if not d: return []
        return [(d, tuple(to_m(sg, L["ops"], inv))) for sg in it["segments"] if len(sg) >= 2]

    def dir_agree(key, L):
        it = icit[L["icit"]]; dm = {d for d, _ in lines_by.get(key, [])}
        return IDIR.get(it["direction"]) is not None and dm == {IDIR.get(it["direction"])}

    C = {}
    def put(name, recs, lines, info):
        C[name] = dict(recs=recs, lines=[[d, list(s)] for d, s in lines], info=info)

    all_lines = lambda keys: [x for k in keys for x in lines_by.get(k, [])]
    keys_all = [(t["text_no"], t["side"]) for t in m77]
    put("base", [rec(t, t["seq"]) for t in m77], all_lines(keys_all), {})
    for nm, L in (("reg", reg), ("ext", ext)):
        recs, lines, nmask = [], [], 0
        for t in m77:
            k = (t["text_no"], t["side"])
            if k in L:
                s, bad = mask(t["seq"], icit[L[k]["icit"]]["seq"], L[k]["ops"], dbl); nmask += bad
                recs.append(rec(t, s, t["complete"] and not bad))
                if not disagrees(L[k]["ops"]) and dir_agree(k, L[k]): lines += lines_by.get(k, [])
            elif nm == "reg":
                recs.append(rec(t, t["seq"])); lines += lines_by.get(k, [])
        put(f"cons_sign_{nm}", recs, lines, dict(linked=len(L), masked_texts=nmask))
    recs, lines = [], []
    for t in m77:
        k = (t["text_no"], t["side"])
        if k in ext and not disagrees(ext[k]["ops"]):
            recs.append(rec(t, t["seq"]))
            if dir_agree(k, ext[k]): lines += lines_by.get(k, [])
    put("cons_text_ext", recs, lines, dict(kept=len(recs)))
    for nm, L in (("reg", reg), ("ext", ext)):
        recs, lines, nW = [], [], 0
        for t in m77:
            k = (t["text_no"], t["side"])
            if k in L:
                s = to_m(icit[L[k]["icit"]]["seq"], L[k]["ops"], inv)
                nW += sum(x.startswith("W") for x in s)
                recs.append(rec(t, s, icit[L[k]["icit"]]["complete"])); lines += icit_lines(k, L[k])
            else:
                recs.append(rec(t, t["seq"])); lines += lines_by.get(k, [])
        put(f"icit_{nm}", recs, lines, dict(replaced=len(L), unmapped_W_tokens=nW))
    put("match_m77", [rec(t, t["seq"]) for t in m77 if (t["text_no"], t["side"]) in reg],
        all_lines([k for k in keys_all if k in reg]), {})
    recs, lines = [], []
    for t in m77:
        k = (t["text_no"], t["side"])
        if k in reg:
            recs.append(rec(t, to_m(icit[reg[k]["icit"]]["seq"], reg[k]["ops"], inv), icit[reg[k]["icit"]]["complete"]))
            lines += icit_lines(k, reg[k])
    put("match_icit", recs, lines, {})
    summ = {}
    for nm, c in C.items():
        json.dump(c, open(OUT / f"{nm}.json", "w"))
        summ[nm] = dict(records=len(c["recs"]), distinct=len({" ".join(r["seq"]) for r in c["recs"]}),
                        tokens=sum(s not in "|#" for r in c["recs"] for s in r["seq"]), lines=len(c["lines"]), **c["info"])
    seq_d = [v for v in seq.values()]
    summ["_links"] = dict(reg=len(reg), seq=len(seq), ext=len(ext), m77_sides=len(m77),
                          seq_exact=sum(not disagrees(v["ops"]) for v in seq_d),
                          reg_exact=sum(not disagrees(v["ops"]) for v in reg.values()))
    json.dump(summ, open(HERE / "out" / "corpora_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
