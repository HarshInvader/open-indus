"""Red team of the uniformity benchmark (prereg docs/prereg/redteam_uniformity.md).

Every condition goes through the benchmark's own code: uniformity_benchmark/run.py clean() (drop strings
found at both sites, then non-chaining greedy de-dup from fish_tick_closer_v2/dedup.py), draw_n() (Indus
length mix, bin filling), score() (frozen site_signal NB pipeline + one permuted-label AUC per draw).
Indus texts are put into the same {id, site, lines, group} format as the references.

  board/run.sh .venv/bin/python -I experiments/redteam_uniformity/rt.py sizes
  board/run.sh .venv/bin/python -I experiments/redteam_uniformity/rt.py run      # resumable -> draws.jsonl
  .venv/bin/python -I experiments/redteam_uniformity/rt.py report                 # -> results.json, table.md
"""
import json
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/uniformity_benchmark"))
import run as ub  # noqa: E402  benchmark code, used unchanged
import lib  # noqa: E402  frozen site_signal pipeline (imported by ub)
from corpus.load import icit_texts, m77_texts  # noqa: E402

N_DRAWS = 30
SEED = 20261122
MD, HA = "Mohenjo-daro", "Harappa"
MIX, _ = ub.indus_mix()
K_VOCAB = 400


# --------------------------------------------------------------------------- Indus pools
def icit_seal_pool(amap=None):
    out = []
    for t in icit_texts():
        if not t["type"].startswith("SEAL") or "#" in t["seq"] or not t["complete"]:
            continue
        L = [[(amap or {}).get(s, s) for s in seg] for seg in t["segments"] if seg]
        if L:
            out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["id"]))
    return out


def icit_band_pool():
    """Mohenjo-daro seals labelled by period band (time pair, like Uruk IV/III)."""
    out = []
    for t in icit_texts():
        if t["site"] != MD or not t["type"].startswith("SEAL") or "#" in t["seq"] or not t["complete"]:
            continue
        b = lib.band(t)
        L = [list(seg) for seg in t["segments"] if seg]
        if b and L:
            out.append(dict(id=t["id"], site=b, lines=L, group=t["id"]))
    return out


def strict_pool():
    """The exact site_signal P1 pool (strict exclusion), in benchmark format."""
    out = []
    for t in lib.eligible_icit("strict"):
        if t["site"] in (MD, HA):
            out.append(dict(id=t["id"], site=t["site"], lines=[list(r) for r in t["runs"] if r], group=t["id"]))
    return out


def m77_pool(objs, sitemap=None, partition=None):
    """M77 (Mahadevan) texts of the given object types; site label may be remapped (e.g. to object type)."""
    out = []
    for i, t in enumerate(m77_texts()):
        if t["object_type"] not in objs or "#" in t["seq"] or not t.get("complete"):
            continue
        site = {"Mohenjodaro": MD}.get(t["site"], t["site"])
        if sitemap:
            site = sitemap(site, t["object_type"])
            if site is None:
                continue
        L, cur = [], []
        for s in t["seq"]:
            if s == "|":
                if cur:
                    L.append(cur)
                cur = []
            else:
                cur.append((partition or {}).get(s, s))
        if cur:
            L.append(cur)
        if L:
            out.append(dict(id=f"m{i:05d}", site=site, lines=L, group=f"m{i:05d}"))
    return out


def lump_all_partition():
    v = json.load(open(ROOT / "experiments/signlist_robustness/variants.json"))["partitions"]
    p = v.get("lump_all") or {}
    return p if isinstance(p, dict) else {}


# --------------------------------------------------------------------------- reference transforms
def map_tokens(texts, f):
    out = []
    for t in texts:
        L = [[x for w in l for x in f(w)] for l in t["lines"]]
        L = [l for l in L if l]
        if L:
            out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["group"]))
    return out


def topk(texts, k=K_VOCAB):
    """Keep the k most frequent types; every other token becomes one class UNK."""
    wc = Counter(w for t in texts for l in t["lines"] for w in l)
    keep = {w for w, _ in wc.most_common(k - 1)}
    return map_tokens(texts, lambda w: [w if w in keep else "UNK"])


def topk_drop(texts, k=K_VOCAB):
    """Keep the k most frequent types; drop every other token."""
    wc = Counter(w for t in texts for l in t["lines"] for w in l)
    keep = {w for w, _ in wc.most_common(k)}
    return map_tokens(texts, lambda w: [w] if w in keep else [])


def hashk(texts, k=K_VOCAB):
    """Top k/2 types keep their identity; every other type is hashed into one of k/2 shared classes
    (a 400-class vocabulary in which rare words collide, like homophonous signs)."""
    wc = Counter(w for t in texts for l in t["lines"] for w in l)
    keep = {w for w, _ in wc.most_common(k // 2)}
    return map_tokens(texts, lambda w: [w if w in keep else "H%d" % (zlib.crc32(w.encode()) % (k // 2))])


def ur3_signs(texts):
    """Ur III word forms split into sign readings (ur-{d}ašnan -> ur, {d}ašnan)."""
    return map_tokens(texts, lambda w: [p for p in re.split(r"[-.]", w) if p])


def ur3_no_names(texts):
    """Drop every token with a god or place determinative ({d}, {ki}): gods, cities, theophoric names."""
    return map_tokens(texts, lambda w: [] if ("{d}" in w or "{ki}" in w) else [w])


def ur3_owner_dedup(texts):
    """One legend per seal owner: key = first line. Owners seen at both sites are dropped."""
    sites = {}
    for t in texts:
        sites.setdefault(" ".join(t["lines"][0]), set()).add(t["site"])
    seen, out = set(), []
    for t in sorted(texts, key=lambda t: t["id"]):
        k = " ".join(t["lines"][0])
        if len(sites[k]) > 1 or k in seen:
            continue
        seen.add(k); out.append(t)
    return out


MIL = re.compile(r"^(LEG|COH|ALA|VEX|VEXIL|CL|CLBR|CLASSIS|MIL|NUMERUS|N|PR|PF|AVG|AUG|VV|VALVIC|BR|BRIT|GER|GERM|EX|EXGER|EXGERINF|DUP|DUPL)$")
ROMAN = re.compile(r"^[IVXLC]{2,}$")


def lat_civil(texts):
    """Drop every label with a military or unit word or a Roman numeral of 2+ letters."""
    return [t for t in texts if not any(MIL.match(w) or ROMAN.match(w) for l in t["lines"] for w in l)]


def pc_base(texts):
    """Proto-cuneiform signs without variant marks (~a, @g, #, numbers kept): palaeographic leak check."""
    return map_tokens(texts, lambda w: [re.split(r"[~@]", w)[0] or w])


# --------------------------------------------------------------------------- conditions
REF = {  # pair -> (a, b, one_per_group)
    "ur3_umma_girsu": ("Umma", "Girsu", False),
    "ur3_pd_nippur": ("Puzriš-Dagan", "Nippur", False),
    "lat_britannia_germania": ("Britannia", "Germania", False),
    "pc_uruk4_uruk3": ("Uruk IV", "Uruk III", True),
}
_POOLS = {}


def ref_pool(pair, variant):
    if pair not in _POOLS:
        _POOLS[pair] = ub.pools(pair)[0]
    return _POOLS[pair][variant]


def ref_transformed(pair, steps, frame=False):
    """Apply transforms to the cleaned whole pool, re-clean; optionally strip the frame (benchmark rule)."""
    T = ref_pool(pair, "whole")
    for s in steps:
        T = s(T)
    T = ub.clean(T)
    if frame:
        T, _ = ub.strip_frame(T)
        T = ub.clean(T)
    return T


def conditions():
    """name -> (attack, builder, a, b, n_side, one_per_group, plant)"""
    C = {}
    lump = lump_all_partition()
    A1, A2 = lib.allograph_map("A1"), lib.allograph_map("A2")
    # ---- 1 like-for-like
    C["I_icit_MD_H_227"] = ("1", lambda: ub.clean([t for t in icit_seal_pool() if t["site"] in (MD, HA)]), MD, HA, 227, False, None)
    for n in (100, 50, 35):
        C[f"I_icit_MD_H_{n}"] = ("1", lambda: ub.clean([t for t in icit_seal_pool() if t["site"] in (MD, HA)]), MD, HA, n, False, None)
    C["I_strict_MD_H_130"] = ("1", lambda: ub.clean(strict_pool()), MD, HA, 130, False, None)
    for pair, (a, b, opg) in REF.items():
        for n in (227, 130):
            C[f"R_{pair}_whole_{n}"] = ("1", lambda pair=pair: ref_pool(pair, "whole"), a, b, n, opg, None)
        C[f"R_{pair}_frame_227"] = ("1", lambda pair=pair: ref_pool(pair, "frame_removed"), a, b, 227, opg, None)
    # ---- 2 vocabulary and tokenisation (n = 227, the Indus like-for-like size)
    for pair, (a, b, opg) in REF.items():
        C[f"V_{pair}_top400"] = ("2", lambda pair=pair: ref_transformed(pair, [topk]), a, b, None, opg, None)
        C[f"V_{pair}_top400drop"] = ("2", lambda pair=pair: ref_transformed(pair, [topk_drop]), a, b, None, opg, None)
        C[f"V_{pair}_hash400"] = ("2", lambda pair=pair: ref_transformed(pair, [hashk]), a, b, None, opg, None)
        C[f"V_{pair}_top400_frame"] = ("2", lambda pair=pair: ref_transformed(pair, [topk], frame=True), a, b, None, opg, None)
    for pair in ("ur3_umma_girsu", "ur3_pd_nippur"):
        a, b, opg = REF[pair]
        C[f"V_{pair}_signs"] = ("2", lambda pair=pair: ref_transformed(pair, [ur3_signs]), a, b, None, opg, None)
        C[f"V_{pair}_signs_top400_frame"] = ("2", lambda pair=pair: ref_transformed(pair, [ur3_signs, topk], frame=True), a, b, None, opg, None)
    # ---- 3 label leaks
    for pair in ("ur3_umma_girsu", "ur3_pd_nippur"):
        a, b, opg = REF[pair]
        C[f"L_{pair}_ownerdedup"] = ("3", lambda pair=pair: ref_transformed(pair, [ur3_owner_dedup]), a, b, None, opg, None)
        C[f"L_{pair}_nonames"] = ("3", lambda pair=pair: ref_transformed(pair, [ur3_no_names]), a, b, None, opg, None)
        C[f"L_{pair}_all"] = ("3", lambda pair=pair: ref_transformed(pair, [ur3_owner_dedup, ur3_no_names, ur3_signs, topk], frame=True), a, b, None, opg, None)
    a, b, opg = REF["lat_britannia_germania"]
    C["L_lat_civil"] = ("3", lambda: ref_transformed("lat_britannia_germania", [lat_civil]), a, b, None, opg, None)
    C["L_lat_civil_top400_frame"] = ("3", lambda: ref_transformed("lat_britannia_germania", [lat_civil, topk], frame=True), a, b, None, opg, None)
    a, b, opg = REF["pc_uruk4_uruk3"]
    C["L_pc_base"] = ("3", lambda: ref_transformed("pc_uruk4_uruk3", [pc_base]), a, b, None, opg, None)
    C["L_pc_base_frame"] = ("3", lambda: ref_transformed("pc_uruk4_uruk3", [pc_base], frame=True), a, b, None, opg, None)
    # ---- 4 Indus transcription
    C["T_icit_A1"] = ("4", lambda: ub.clean([t for t in icit_seal_pool(A1) if t["site"] in (MD, HA)]), MD, HA, 227, False, None)
    C["T_icit_A2"] = ("4", lambda: ub.clean([t for t in icit_seal_pool(A2) if t["site"] in (MD, HA)]), MD, HA, 227, False, None)
    C["T_m77_seal"] = ("4", lambda: ub.clean([t for t in m77_pool({"seal"}) if t["site"] in (MD, HA)]), MD, HA, 227, False, None)
    C["T_m77_seal_lumpall"] = ("4", lambda: ub.clean([t for t in m77_pool({"seal"}, partition=lump) if t["site"] in (MD, HA)]), MD, HA, 227, False, None)
    # ---- 5 other Indus pairs (n set at run time to the smaller side, capped)
    for s in ("Dholavira", "Lothal", "Kalibangan", "Chanhu-daro"):
        C[f"P_icit_H_{s}"] = ("5", lambda s=s: ub.clean([t for t in icit_seal_pool() if t["site"] in (HA, s)]), HA, s, None, False, None)
        C[f"P_icit_MD_{s}"] = ("5", lambda s=s: ub.clean([t for t in icit_seal_pool() if t["site"] in (MD, s)]), MD, s, None, False, None)
    C["P_m77_sealing_MD_H"] = ("5", lambda: ub.clean([t for t in m77_pool({"sealing"}) if t["site"] in (MD, HA)]), MD, HA, None, False, None)
    C["P_m77_sealseal_Lothal_H"] = ("5", lambda: ub.clean([t for t in m77_pool({"seal", "sealing"}) if t["site"] in ("Lothal", HA)]), "Lothal", HA, None, False, None)
    C["P_m77_H_seal_vs_sealing"] = ("5", lambda: ub.clean(m77_pool({"seal", "sealing"}, sitemap=lambda s, o: o if s == HA else None)), "seal", "sealing", None, False, None)
    C["P_icit_MD_band"] = ("5", lambda: ub.clean(icit_band_pool()), "earlier", "late", None, False, None)
    C["P_m77_H_tablet_vs_seal"] = ("5", lambda: ub.clean(m77_pool({"seal", "miniature tablet"}, sitemap=lambda s, o: o if s == HA else None)), "seal", "miniature tablet", None, False, None)
    # small-n reference baselines for attack 5
    for n in (35, 50):
        for pair, (a, b, opg) in REF.items():
            C[f"R_{pair}_whole_{n}"] = ("5", lambda pair=pair: ref_pool(pair, "whole"), a, b, n, opg, None)
            C[f"V_{pair}_top400_frame_{n}"] = ("5", lambda pair=pair: ref_transformed(pair, [topk], frame=True), a, b, n, opg, None)
    # ---- 6 power: plant local stocks into Indus (labels permuted within each draw)
    for kind in ("new100", "old40"):
        for q in (0.05, 0.1, 0.15, 0.2, 0.3):
            C[f"W_{kind}_q{q}"] = ("6", lambda: ub.clean([t for t in icit_seal_pool() if t["site"] in (MD, HA)]), MD, HA, 227, False, (kind, q))
    return C


# --------------------------------------------------------------------------- plant + descriptive stats
def plant(sample, kind, q, rng, common):
    """Permute site labels (kill real signal), then give EACH site its own local stock, Zipf-weighted,
    replacing each token with prob q. new100: 100 brand-new symbols per site (reference-like: local names
    are types not used elsewhere). old40: 40 existing common Indus signs per site, disjoint."""
    sites = [t["site"] for t in sample]
    sites = [sites[i] for i in rng.permutation(len(sites))]
    if kind == "new100":
        stocks = {s: [f"{s[:2]}_{i}" for i in range(100)] for s in set(sites)}
    else:
        pick = list(rng.choice(common, 80, replace=False))
        stocks = dict(zip(sorted(set(sites)), (pick[:40], pick[40:])))
    w = {s: (lambda n: (1 / np.arange(1, n + 1)) / (1 / np.arange(1, n + 1)).sum())(len(v)) for s, v in stocks.items()}
    out = []
    for t, s in zip(sample, sites):
        L = [[stocks[s][rng.choice(len(stocks[s]), p=w[s])] if rng.random() < q else x for x in l] for l in t["lines"]]
        out.append(dict(t, site=s, lines=L))
    return out


def describe(sample, a):
    """Types, tokens, and the share of tokens whose type is local: seen >= 2 times in the sample and
    >= 90% of its uses at one site (a classifier-free measure of a local stock)."""
    toks = [(w, t["site"]) for t in sample for l in t["lines"] for w in l]
    by = {}
    for w, s in toks:
        by.setdefault(w, Counter())[s] += 1
    loc = {w for w, c in by.items() if sum(c.values()) >= 2 and max(c.values()) / sum(c.values()) >= 0.9}
    n = len(toks)
    return dict(types=len(by), tokens=n, ttr=len(by) / n, local_share=sum(1 for w, _ in toks if w in loc) / n,
                mean_len=n / len(sample))


# --------------------------------------------------------------------------- modes
def sizes():
    for name, (att, build, a, b, n, opg, pl) in conditions().items():
        T = build()
        c = Counter(t["site"] for t in T)
        print(f"{att} {name:40s} {a}={c[a]} {b}={c[b]} n_side={n}", flush=True)


def run(only=None):
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    common = None
    with open(path, "a") as f:
        for name, (att, build, a, b, n, opg, pl) in conditions().items():
            if only and not any(name.startswith(o) for o in only):
                continue
            if done[name] >= N_DRAWS:
                continue
            T = build()
            c = Counter(t["site"] for t in T)
            n_side = n if n is not None else min(c[a], c[b], 227)
            if pl and common is None:
                freq = Counter(w for t in T for l in t["lines"] for w in l)
                common = sorted(s for s, k in freq.items() if k >= 5)
            for k in range(done[name], N_DRAWS):
                rng = np.random.default_rng([SEED, k, zlib.crc32(name.encode())])
                smp, short = ub.draw_n(T, a, b, rng, MIX, opg, n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, attack=att, draw=k, auc=None, n_side=n_side, avail=[c[a], c[b]])
                else:
                    if pl:
                        smp = plant(smp, pl[0], pl[1], rng, common)
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, attack=att, draw=k, auc=obs, null_auc=nul, n_feat=nf, n=nn, n_side=n_side,
                               short=short, avail=[c[a], c[b]], **describe(smp, a))
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(name, "done", rec.get("auc"), flush=True)


def report():
    R = [json.loads(l) for l in open(HERE / "draws.jsonl")]
    by = {}
    for r in R:
        by.setdefault(r["cond"], []).append(r)
    order = list(conditions())
    out, lines = {}, ["| attack | condition | n per side | median AUC | 2.5-97.5% | null q95 | share >= 0.65 | types | TTR | local share | mean len |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in order:
        rs = by.get(name, [])
        ok = [r for r in rs if r["auc"] is not None]
        if not rs:
            continue
        if not ok:
            out[name] = dict(failed=len(rs), avail=rs[0].get("avail"))
            lines.append(f"| {rs[0]['attack']} | {name} | {rs[0]['n_side']} | failed (avail {rs[0].get('avail')}) | | | | | | | |")
            continue
        a = np.array([r["auc"] for r in ok]); nu = np.array([r["null_auc"] for r in ok])
        d = dict(attack=ok[0]["attack"], n_side=ok[0]["n_side"], n_draws=len(ok), failed=len(rs) - len(ok),
                 median_auc=float(np.median(a)), lo=float(np.quantile(a, 0.025)), hi=float(np.quantile(a, 0.975)),
                 null_mean=float(nu.mean()), null_q95=float(np.quantile(nu, 0.95)), share_ge_065=float(np.mean(a >= 0.65)),
                 p_vs_pooled_null=None, avail=ok[0]["avail"])
        for k in ("types", "ttr", "local_share", "mean_len", "n_feat"):
            d[k] = float(np.mean([r[k] for r in ok]))
        out[name] = d
        lines.append(f"| {d['attack']} | {name} | {d['n_side']} | {d['median_auc']:.3f} | {d['lo']:.3f}-{d['hi']:.3f} | {d['null_q95']:.3f} | {d['share_ge_065']:.0%} | {d['types']:.0f} | {d['ttr']:.2f} | {d['local_share']:.3f} | {d['mean_len']:.1f} |")
    lib.jdump(out, HERE / "results.json")
    (HERE / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2:] or None)
    else:
        {"sizes": sizes, "report": report}[mode]()
