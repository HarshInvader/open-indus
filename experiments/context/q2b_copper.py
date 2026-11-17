"""Q2b. Copper tablets (Mohenjo-daro): does the text predict the picture on the other face?

Image per tablet: IM77 line file (sources/paragorth_Indus-/data/im77/im77_corpus_lines.csv, read as DATA),
copper-tablet (object_code 5) rows whose fs80 != 0 give the picture; text = our M77 text sides.
Replicates paragorth S-DARK-67 (tablet-level binding strong; die-level null) and adds:
 (1) tablet level: identical-text tablet pairs sharing the image, vs image labels permuted among tablets;
 (2) die level (die = distinct text x image): do DIFFERENT texts that share signs share the image?
     - nearest-neighbour (max Jaccard, ties random) image prediction, leave-one-die-out, vs image labels
       permuted among dies (5000x);
     - pairwise: P(same image | share >= 1 bigram) vs P(same image | share none), same null;
 (3) 'image-as-sign' faces: two-sided copper tablets whose second face is one large sign: do those signs
     stand for a picture? (which image do their partner texts carry on one-faced tablets?)
"""
import csv
from common import *

rng = np.random.default_rng(22)


def img_class(fs):
    a = m77_animal(fs)
    if a: return a
    return {163: "hare", 290: "two_headed", 860: "endless_knot", 101: "horned_tiger", 102: "horned_tiger"}.get(fs, f"fs{fs}")


def main():
    R = {}
    rows = list(csv.DictReader(open(SRC / "paragorth_Indus-/data/im77/im77_corpus_lines.csv")))
    img = defaultdict(set)
    for r in rows:
        if r["object_code"] == "5" and r["fs80"] not in ("0", "", "999"):
            img[int(r["text_no"])].add(int(r["fs80"]))
    fsd = m77_fs_desc()
    T = [t for t in m77_texts() if t["object_type"] == "copper tablet"]
    by_no = defaultdict(list)
    for t in T: by_no[t["text_no"]].append(t)
    tabs = []
    single_sign_faces = []
    for no, sides in by_no.items():
        txt_sides = [s for s in sides if len(signs(s["seq"])) >= 2 and "#" not in s["seq"]]
        one = [s for s in sides if len(signs(s["seq"])) == 1]
        if len(img[no]) == 1 and len(txt_sides) == 1:
            fs = next(iter(img[no]))
            tabs.append(dict(no=no, text=" ".join(txt_sides[0]["seq"]), fs=fs, cls=img_class(fs)))
        if one and txt_sides and not img[no]:
            single_sign_faces.append(dict(no=no, sign=signs(one[0]["seq"])[0], text=" ".join(txt_sides[0]["seq"])))
    print(f"copper tablets with one complete text face + one picture: {len(tabs)}; distinct texts {len(set(t['text'] for t in tabs))}; "
          f"pictures (fs80) {len(set(t['fs'] for t in tabs))}; classes {Counter(t['cls'] for t in tabs)}")
    # (1) tablet level
    texts = np.array([t["text"] for t in tabs]); cls = np.array([t["cls"] for t in tabs]); fss = np.array([t["fs"] for t in tabs])
    same_txt = [(i, j) for i in range(len(tabs)) for j in range(i + 1, len(tabs)) if texts[i] == texts[j]]
    def share(lab): return np.mean([lab[i] == lab[j] for i, j in same_txt])
    obs = share(fss); null = np.array([share(rng.permutation(fss)) for _ in range(5000)])
    R["tablet_level"] = dict(n_tablets=len(tabs), n_pairs=len(same_txt), share_same_image=float(obs), null=float(null.mean()),
                             p=float((1 + (null >= obs).sum()) / 5001))
    print(f"(1) identical-text tablet pairs {len(same_txt)}: same picture {obs:.2f} vs permuted {null.mean():.2f} (p={R['tablet_level']['p']:.4f})")
    # (2) die level
    dies = sorted({(t["text"], t["cls"]) for t in tabs})
    D = [dict(text=a, cls=b, sset=set(signs(a.split())), big=ngrams(a.split(), 2)) for a, b in dies]
    print(f"(2) dies (distinct text x picture class): {len(D)}; texts with >1 class: "
          f"{sum(1 for k, v in Counter(d['text'] for d in D).items() if v > 1)}")
    labs = np.array([d["cls"] for d in D])
    n = len(D)
    # text FAMILIES: variant copies of one legend (edit distance <= 1, or one (>=3 signs) contained in the other)
    def lev(a, b):
        dp = list(range(len(b) + 1))
        for i, x in enumerate(a, 1):
            prev, dp[0] = dp[0], i
            for j, y in enumerate(b, 1):
                prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
        return dp[-1]
    def contained(a, b):
        sa, sb = " ".join(a), " ".join(b)
        return sa in sb or sb in sa
    par = list(range(n))
    def find(i):
        while par[i] != i: i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            a, b = signs(D[i]["text"].split()), signs(D[j]["text"].split())
            if lev(a, b) <= 1 or (min(len(a), len(b)) >= 3 and contained(a, b)): par[find(i)] = find(j)
    fam = np.array([find(i) for i in range(n)])
    print(f"   text families (variants merged): {len(set(fam))}")
    J = np.zeros((n, n)); B = np.zeros((n, n), bool); diff = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            u = D[i]["sset"] | D[j]["sset"]
            J[i, j] = len(D[i]["sset"] & D[j]["sset"]) / len(u)
            B[i, j] = bool(D[i]["big"] & D[j]["big"])
            diff[i, j] = fam[i] != fam[j]
    def nn_acc(lab):
        hits = []
        for i in range(n):
            cand = np.where(diff[i])[0]
            # exclude other dies with the identical picture? no: we ask whether similar texts have the same picture
            best = cand[J[i, cand] == J[i, cand].max()]
            if J[i, cand].max() == 0: continue
            hits.append(np.mean(lab[best] == lab[i]))
        return np.mean(hits), len(hits)
    obs, m = nn_acc(labs)
    null = np.array([nn_acc(rng.permutation(labs))[0] for _ in range(5000)])
    R["die_nn"] = dict(n_dies=n, n_scored=m, acc=float(obs), null=float(null.mean()), p=float((1 + (null >= obs).sum()) / 5001))
    print(f"   nearest-neighbour (Jaccard) picture prediction across different text FAMILIES: {obs:.3f} vs null {null.mean():.3f} (p={R['die_nn']['p']:.4f}, scored {m})")
    iu = np.triu_indices(n, 1)
    mask = diff[iu]
    def pair_stat(lab):
        same = (lab[:, None] == lab[None, :])[iu][mask]
        b = B[iu][mask]
        return same[b].mean() - same[~b].mean(), same[b].mean(), same[~b].mean(), int(b.sum())
    o, a1, a0, nb_ = pair_stat(labs)
    null = np.array([pair_stat(rng.permutation(labs))[0] for _ in range(5000)])
    R["die_pairs_bigram"] = dict(same_if_shared_bigram=float(a1), same_if_not=float(a0), n_pairs_shared=nb_, diff=float(o),
                                 null=float(null.mean()), p=float((1 + (null >= o).sum()) / 5001))
    print(f"   different-family die pairs sharing a bigram ({nb_}): same picture {a1:.3f} vs not sharing {a0:.3f}; diff {o:+.3f} null {null.mean():+.3f} p={R['die_pairs_bigram']['p']:.4f}")
    # per-shared bigram: which bigrams join same-picture dies?
    bg = defaultdict(list)
    for d in D:
        for b in d["big"]: bg[b].append(d["cls"])
    R["bigram_pictures"] = {b: v for b, v in bg.items() if len(v) >= 2}
    print("   bigrams on >=2 dies, with their pictures:")
    for b, v in sorted(R["bigram_pictures"].items(), key=lambda z: -len(z[1]))[:15]: print(f"     {b:12s} {v}")
    # (3) image-as-sign faces
    text2cls = defaultdict(Counter)
    for t in tabs: text2cls[t["text"]][t["cls"]] += 1
    print(f"(3) two-sided copper tablets with a one-sign face and no picture: {len(single_sign_faces)}")
    out = []
    for f in sorted(single_sign_faces, key=lambda z: z["sign"]):
        pic = dict(text2cls.get(f["text"], {}))
        out.append(dict(sign=f["sign"], text=f["text"], picture_of_same_text_elsewhere=pic))
        print(f"     {f['sign']:6s} + {f['text']:40s} same text on picture tablets: {pic}")
    R["image_sign_faces"] = out
    save_json("q2b_copper", R)


if __name__ == "__main__":
    main()
