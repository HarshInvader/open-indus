"""Build the copper-tablet TYPE table for the series test.

Input: experiments/logograms/copper_tablets.csv (one row per tablet per source; built by logograms/l1 from
the IM77 line file and ICIT TAB:C). Re-verified here against data/m77_texts.jsonl (object_type 'copper
tablet') and data/icit_texts.jsonl (type TAB:C).

Type rule (stricter than the logograms 'family', which merged 2-sign legends at edit distance 1):
  * complete legend = no '#' and >= 2 signs.
  * two complete legends are one type if (both >= 4 signs and edit distance <= 1) or (the shorter has >= 4 signs
    and is contained in the longer), AND their specific pictures are compatible (shared picture class, or one
    side has no specific picture). This keeps 204-245-342 (rhino) apart from 204-245-358-342 (ox-antelope).
  * fragments ('#') and 1-sign legends join a type only if every break-free run occurs in one of its complete
    legends, the runs total >= 2 signs, the picture is compatible, and exactly one type qualifies.
  * 'lumped' variant (sensitivity): also merge types that share a contiguous bigram (excluding the formula
    signs M342, M169, M407) and share a specific picture class.
Counts: objects per type in M77, in ICIT, and n_est = max(M77, ICIT) (the two corpora overlap in objects and
share no ids; max is the conservative union estimate, sum is an upper bound).
Writes types.csv, tablets_typed.csv.
"""
import csv, json, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts  # noqa

OUT = ROOT / "experiments" / "copper_series"
SRC = ROOT / "experiments" / "logograms" / "copper_tablets.csv"
FORMULA = {"M342", "M169", "M407"}

COARSE = {
    "ox-antelope (long curly horns)": "ox-antelope", "ox-antelope (short horns)": "ox-antelope",
    "ox-antelope/gaur (ICIT Gaur)": "ox-antelope", "composite/two-headed (ICIT Comp)": "two-headed/composite",
    "two-headed animal": "two-headed/composite", "composite animal": "two-headed/composite",
    "bull (ICIT)": "bull", "short-horned bull": "bull", "uncertain bovine": "bull",
    "goat-antelope (horns arching back)": "goat-antelope arching", "goat-antelope (twirled horns)": "goat-antelope twirled",
}
NONSPEC = {"", "other picture (ICIT Othr)", "unknown"}


def coarse(p):
    return None if p in NONSPEC else COARSE.get(p, p)


def toks(s):
    return s.split() if s else []


def signs(seq):
    return [x for x in seq if x not in ("|", "#")]


def runs(seq):
    out, cur = [], []
    for s in seq:
        if s in ("|", "#"):
            if cur: out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur: out.append(cur)
    return out


def lev(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]


def contains(big, small):
    n = len(small)
    return any(big[i:i + n] == small for i in range(len(big) - n + 1))


def verify(rows):
    """Re-verify copper_tablets.csv legends against the corpus files."""
    m77 = defaultdict(list)
    for r in m77_texts():
        if r["object_type"] == "copper tablet":
            m77[str(r["text_no"])].append(signs(r["seq"]))
    icit = defaultdict(list)
    for r in icit_texts():
        if r["type"] == "TAB:C":
            icit[r["id"].split(".")[0]].append(r)
    ok_m = sum(1 for r in rows if r["source"] == "M77" and (not signs(toks(r["legend"])) or
               any(signs(toks(r["legend"])) == s for s in m77[r["id"]])))
    n_m = sum(1 for r in rows if r["source"] == "M77")
    ok_i = sum(1 for r in rows if r["source"] == "ICIT" and r["id"] in icit)
    n_i = sum(1 for r in rows if r["source"] == "ICIT")
    return dict(m77_objects_in_corpus=len(m77), m77_rows=n_m, m77_legend_matches_corpus=ok_m,
                icit_objects_in_corpus=len(icit), icit_rows=n_i, icit_ids_found=ok_i,
                icit_sites=dict(Counter(v[0]["site"] for v in icit.values())))


def main():
    rows = list(csv.DictReader(open(SRC)))
    ver = verify(rows)
    print("verification:", ver)
    for r in rows:
        r["seq"] = toks(r["legend"])
        r["pic"] = coarse(r["picture"])
    comp = defaultdict(lambda: dict(pics=Counter(), m77pics=Counter(), n=0))
    for r in rows:
        s = r["seq"]
        if s and "#" not in s and len(signs(s)) >= 2:
            k = " ".join(s); comp[k]["n"] += 1
            if r["pic"]: comp[k]["pics"][r["pic"]] += 1
            if r["pic"] and r["source"] == "M77": comp[k]["m77pics"][r["pic"]] += 1
    keys = sorted(comp)
    par = {k: k for k in keys}

    def find(x):
        while par[x] != x: x = par[x]
        return x

    def pic_ok(a, b):
        # block only on M77 fs80 pictures: ICIT 'symbol' is unreliable on copper (paragorth, logograms)
        A, B = set(comp[a]["m77pics"]), set(comp[b]["m77pics"])
        return not A or not B or bool(A & B)

    for i, a in enumerate(keys):
        A = signs(a.split())
        for b in keys[i + 1:]:
            B = signs(b.split())
            short, long_ = (A, B) if len(A) <= len(B) else (B, A)
            same = (min(len(A), len(B)) >= 4 and lev(A, B) <= 1) or (len(short) >= 4 and contains(long_, short))
            if same and pic_ok(a, b):
                par[find(a)] = find(b)
    # Known cross-transcription duplicate: M77 reads 336-89-87 // 72-194-169 (MD 3302, 3335, 3364), ICIT reads
    # 72-194-169 // 106-336 (M-513..515): same faces, tall 3+2 strokes vs 5 strokes, opposite order; no other
    # copper tablet carries 72-194-169 as a whole face. Merged (stated in RESULTS).
    if "M336 M89 M87" in par and "M72 M194 M169" in par:
        par[find("M72 M194 M169")] = find("M336 M89 M87")
    groups = defaultdict(list)
    for k in keys:
        groups[find(k)].append(k)

    def assign(seq, pic):
        rr = runs(seq)
        if sum(len(x) for x in rr) < 2:
            return None
        hits = set()
        for root, mem in groups.items():
            if any(all(contains(m.split(), x) for x in rr) for m in mem):
                gp = set().union(*[set(comp[m]["pics"]) for m in mem])
                if not pic or not gp or pic in gp:
                    hits.add(root)
        return hits.pop() if len(hits) == 1 else None

    for r in rows:
        s = r["seq"]
        k = " ".join(s)
        if k in par:
            r["root"] = find(k); r["how"] = "complete"
        else:
            r["root"] = assign(s, r["pic"]); r["how"] = "fragment-assigned" if r["root"] else "unassigned"

    # type ids by n_est
    def n_est(root):
        c = Counter(r["source"] for r in rows if r["root"] == root)
        return max(c["M77"], c["ICIT"]), c["M77"], c["ICIT"]

    roots = sorted(groups, key=lambda g: (-n_est(g)[0], g))
    tid = {g: f"T{i+1:02d}" for i, g in enumerate(roots)}

    # lumped variant
    lpar = {g: g for g in roots}

    def lfind(x):
        while lpar[x] != x: x = lpar[x]
        return x

    def bigrams(g):
        out = set()
        for m in groups[g]:
            for run in runs(m.split()):
                for a, b in zip(run, run[1:]):
                    if a not in FORMULA and b not in FORMULA:
                        out.add((a, b))
        return out

    def gpics(g):  # modal picture of the type
        c = Counter()
        for m in groups[g]:
            c.update(comp[m]["pics"])
        return {c.most_common(1)[0][0]} if c else set()

    for i, a in enumerate(roots):
        for b in roots[i + 1:]:
            if bigrams(a) & bigrams(b) and gpics(a) & gpics(b):
                lpar[lfind(a)] = lfind(b)

    out = []
    for g in roots:
        mem = [r for r in rows if r["root"] == g]
        nmax, nm, ni = n_est(g)
        pics = Counter(r["pic"] for r in mem if r["pic"])
        sf = Counter(r["sign_face"] for r in mem if r["sign_face"])
        st = Counter(r["second_text"] for r in mem if r["second_text"])
        label = max(groups[g], key=lambda k: (comp[k]["n"], k))
        out.append(dict(type=tid[g], lumped=tid[lfind(g)], legend=label,
                        variants=" / ".join(sorted(groups[g])), n_M77=nm, n_ICIT=ni, n_est=nmax, n_sum=nm + ni,
                        n_fragments_assigned=sum(1 for r in mem if r["how"] == "fragment-assigned"),
                        picture=pics.most_common(1)[0][0] if pics else "",
                        pictures=json.dumps(dict(pics)), sign_faces=json.dumps(dict(sf)),
                        second_texts=json.dumps(dict(st)), kinds=json.dumps(dict(Counter(r["kind"] for r in mem)))))
    with open(OUT / "types.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    with open(OUT / "tablets_typed.csv", "w", newline="") as fh:
        f = ["source", "id", "cisi", "legend", "kind", "picture", "pic", "sign_face", "second_text", "how", "type"]
        w = csv.DictWriter(fh, fieldnames=f, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r["type"] = tid.get(r["root"], "")
            w.writerow(r)
    summ = dict(verification=ver, n_types_strict=len(roots), n_types_lumped=len(set(lpar[lfind(g)] for g in roots)),
                tablets_by_how=dict(Counter(r["source"] + ":" + r["how"] for r in rows)))
    print(json.dumps(summ, indent=1))
    for o in out:
        print(o["type"], o["lumped"], o["n_M77"], o["n_ICIT"], o["n_est"], o["picture"][:22].ljust(22), o["legend"],
              o["sign_faces"] if o["sign_faces"] != "{}" else "", o["second_texts"] if o["second_texts"] != "{}" else "")
    json.dump(summ, open(OUT / "types_summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
