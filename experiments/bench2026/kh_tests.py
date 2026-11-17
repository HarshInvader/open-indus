"""Kriger & Hunt 2026 registration-code predictions (prereg docs/prereg/bench2026_kriger_hunt.md).
usage: .venv/bin/python -I experiments/bench2026/kh_tests.py [planted|real]
"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/numeral_grammar"))
from corpus.load import m77_lines, m77_texts  # noqa
from common import M_NUM  # noqa

HERE = Path(__file__).resolve().parent
B = 2000
rng = random.Random(20261117)


def load_m77():
    desc = {}
    for l in m77_lines():
        desc[(l["text_no"], l["side"])] = (l.get("fs_description") or "")
    U, S = [], []
    for t in m77_texts():
        if t["object_type"] != "seal" or not t.get("complete"):
            continue
        seq = [s for s in t["seq"] if s != "|"]
        if not seq or "#" in seq:
            continue
        uni = "unicorn" in desc.get((t["text_no"], t["side"]), "").lower()
        (U if (t["site"] == "Mohenjodaro" and uni) else S).append(tuple(seq))
    return U, S


def load_ur():
    seen = {}
    for line in open(ROOT / "experiments/identifiers/data/ur3_occ.jsonl"):
        r = json.loads(line)
        sid = r.get("seal_id") or r["pid"]
        if sid in seen:
            continue
        seen[sid] = tuple(w for ln in r["legend"] for w in ln)
    return [v for v in seen.values() if v]


def uniq_share(objs):
    c = Counter(objs)
    return sum(1 for o in objs if c[o] == 1) / len(objs)


def redeal_n1(objs, r):
    toks = [s for o in objs for s in o]; r.shuffle(toks)
    out, i = [], 0
    for o in objs:
        out.append(tuple(toks[i:i + len(o)])); i += len(o)
    return out


def redeal_n2(objs, r):
    bylen = defaultdict(list)
    for idx, o in enumerate(objs):
        bylen[len(o)].append(idx)
    out = list(objs)
    for L, idxs in bylen.items():
        cols = []
        for p in range(L):
            col = [objs[i][p] for i in idxs]; r.shuffle(col); cols.append(col)
        for j, i in enumerate(idxs):
            out[i] = tuple(cols[p][j] for p in range(L))
    return out


def ent(xs):
    c = Counter(xs); n = len(xs)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def k2_stat(texts, L=5):
    T = [t for t in texts if len(t) == L]
    if len(T) < 10:
        return None, len(T)
    H = [ent([t[p] for t in T]) for p in range(L)]
    return sum(H[1:-1]) / (L - 2) - (H[0] + H[-1]) / 2, len(T)


def k2_stat_ur(texts):
    T = [t for t in texts if len(t) >= 3]
    first = ent([t[0] for t in T]); last = ent([t[-1] for t in T])
    mid = ent([t[rng.randrange(1, len(t) - 1)] for t in T])
    return mid - (first + last) / 2, len(T)


def shuffle_within(texts, r):
    out = []
    for t in texts:
        l = list(t); r.shuffle(l); out.append(tuple(l))
    return out


def ham1_pairs(texts):
    bylen = defaultdict(list)
    for t in set(texts):
        if len(t) >= 3:
            bylen[len(t)].append(t)
    edge = tot = 0
    for L, T in bylen.items():
        # bucket by masked key for speed
        for p in range(L):
            keyd = defaultdict(set)
            for t in T:
                keyd[t[:p] + t[p + 1:]].add(t[p])
            for k, v in keyd.items():
                n = len(v)
                if n > 1:
                    np_ = n * (n - 1) // 2
                    tot += np_
                    if p == 0 or p == L - 1:
                        edge += np_
    return edge, tot


def k4(texts, nulls=B):
    e, n = ham1_pairs(texts)
    obs = e / n if n else float("nan")
    r = random.Random(7)
    D = list(set(texts))
    vals = []
    for _ in range(nulls):
        e2, n2 = ham1_pairs(redeal_n2(D, r))
        if n2:
            vals.append(e2 / n2)
    vals.sort()
    lo, hi = vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals)) - 1]
    p_low = sum(v <= obs for v in vals) / len(vals)
    return dict(edge=e, pairs=n, edge_share=obs, null_mean=sum(vals) / len(vals), null_5=lo, null_95=hi,
                p_low=p_low, nulls=len(vals))


def planted(U):
    D = list(set(U))
    r = random.Random(11)
    # reference N2 interval from the real U (null distribution only; observed U statistic is not computed here)
    ref = []
    for _ in range(500):
        e, n = ham1_pairs(redeal_n2(D, r))
        if n: ref.append(e / n)
    ref.sort(); lo = ref[int(0.05 * len(ref))]
    pos_by = defaultdict(list)
    for t in D:
        for p, s in enumerate(t): pos_by[(len(t), p)].append(s)
    res = {"null5_ref": lo}
    for k in (10, 25):
        hits = 0
        for _ in range(200):
            base = redeal_n2(D, r)
            cands = [t for t in base if len(t) >= 3]
            extra = []
            for _ in range(k):
                t = list(r.choice(cands)); p = r.randrange(1, len(t) - 1)
                pool = [s for s in pos_by[(len(t), p)] if s != t[p]] or ["X"]
                t[p] = r.choice(pool); extra.append(tuple(t))
            e, n = ham1_pairs(base + extra)
            if n and e / n < lo: hits += 1
        res[f"power_k{k}"] = hits / 200
    return res


def main(mode):
    U, S = load_m77(); UR = load_ur()
    R = {"n_U_objects": len(U), "n_U_distinct": len(set(U)), "n_S_objects": len(S), "n_UR_distinct": len(set(UR))}
    if mode == "planted":
        R["K4_planted"] = planted(U)
        json.dump(R, open(HERE / "kh_planted.json", "w"), indent=1); print(json.dumps(R, indent=1)); return
    out = {}
    for name, objs in (("U", U), ("S", S)):
        d = {}
        # K1
        obs = uniq_share(objs)
        r = random.Random(1)
        n1 = sorted(uniq_share(redeal_n1(objs, r)) for _ in range(B))
        n2 = sorted(uniq_share(redeal_n2(objs, r)) for _ in range(B))
        d["K1"] = dict(real=obs, N1_mean=sum(n1) / B, N1_5=n1[int(.05 * B)], N1_95=n1[int(.95 * B) - 1],
                       p_real_ge_N1=sum(v >= obs for v in n1) / B, N2_mean=sum(n2) / B,
                       N2_5=n2[int(.05 * B)], N2_95=n2[int(.95 * B) - 1], p_real_ge_N2=sum(v >= obs for v in n2) / B)
        # K2
        D = list(set(objs))
        st, nT = k2_stat(D)
        r = random.Random(2)
        nv = sorted(k2_stat(shuffle_within(D, r))[0] for _ in range(B))
        d["K2"] = dict(stat_mid_minus_edge_bits=st, n_len5=nT, null_mean=sum(nv) / B, null_95=nv[int(.95 * B) - 1],
                       p=sum(v >= st for v in nv) / B)
        # K3
        num = [(t, p) for t in D for p, s in enumerate(t) if s in M_NUM and len(t) >= 2]
        pen = sum(1 for t, p in num if p == len(t) - 2) / len(num)
        r = random.Random(3); nv = []
        for _ in range(B):
            sh = shuffle_within(D, r)
            nn = [(t, p) for t in sh for p, s in enumerate(t) if s in M_NUM and len(t) >= 2]
            nv.append(sum(1 for t, p in nn if p == len(t) - 2) / len(nn))
        nv.sort()
        toks = [t[p] for t, p in num]
        v2 = sum(1 for s in toks if M_NUM[s][1] == 2) / len(toks)
        nom99 = [s for s in toks if s != "M99"]
        v2x = sum(1 for s in nom99 if M_NUM[s][1] == 2) / len(nom99) if nom99 else float("nan")
        allt = [s for t in D for s in t]
        d["K3"] = dict(numeral_token_share=len(toks) / len(allt), penult_share=pen, null_mean=sum(nv) / B,
                       null_95=nv[int(.95 * B) - 1], p=sum(v >= pen for v in nv) / B,
                       value2_share_all=v2, value2_share_excl_M99=v2x, n_numeral_tokens=len(toks),
                       n_M99=len(toks) - len(nom99), top_numerals=Counter(toks).most_common(6))
        d["K4"] = k4(objs)
        out[name] = d
        print(name, json.dumps(d, indent=1), flush=True)
    st, nT = k2_stat_ur(list(set(UR)))
    r = random.Random(4); DU = list(set(UR))
    nv = sorted(k2_stat_ur(shuffle_within(DU, r))[0] for _ in range(500))
    out["UR"] = {"K2": dict(stat=st, n=nT, null_mean=sum(nv) / 500, null_95=nv[474], p=sum(v >= st for v in nv) / 500),
                 "K4": k4(UR, nulls=500)}
    print("UR", json.dumps(out["UR"], indent=1))
    R.update(out)
    json.dump(R, open(HERE / "kh_real.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "real")
