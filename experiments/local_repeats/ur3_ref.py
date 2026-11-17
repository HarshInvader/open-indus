"""Ur III reference for local_repeats: repeated seal legends on distinct physical seals.
Standalone (no repo imports); run isolated: .venv/bin/python -I experiments/local_repeats/ur3_ref.py
Reads experiments/identifiers/data/ur3_occ.jsonl and experiments/short_labels/raw/cdli/cdli_cat.csv (read-only).
"""
import csv, json, os, re, itertools, random
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
HERE = os.path.join(ROOT, "experiments/local_repeats")
REIGN = {"šū-suen": "SS", "su-suen": "SS", "shu-suen": "SS", "amar-suen": "AS", "amar-sin": "AS", "šulgi": "SH",
         "shulgi": "SH", "ibbi-suen": "IS", "ibbi-sin": "IS", "ibb-suen": "IS", "ibbisuen": "IS"}
ORDER = {"SH": 0, "AS": 1, "SS": 2, "IS": 3}


def cun_signs(word):
    dets = re.findall(r"\{[^}]*\}", word)
    rest = re.sub(r"\{[^}]*\}", "-", word)
    return dets + [p for p in re.split(r"[-.+]", rest) if p]


csv.field_size_limit(10 ** 9)
date = {}
with open(os.path.join(ROOT, "experiments/short_labels/raw/cdli/cdli_cat.csv"), encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f):
        pid = (r.get("id_text") or "").strip()
        if pid.isdigit() and (r.get("period") or "").startswith("Ur III"):
            d = (r.get("date_of_origin") or "").strip().split(".")
            rg = REIGN.get(d[0].lower())
            if rg:
                yr = int(d[1]) if len(d) > 1 and d[1].isdigit() else 0
                date["P" + pid.zfill(6)] = (ORDER[rg], yr)

occ = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/identifiers/data/ur3_occ.jsonl"))]
seal = {}
for u in occ:
    if not u["seal_id"] or u["prov"] in ("uncertain", ""): continue
    sid = u["seal_id"].split()[0]
    words = tuple(w for l in u["legend"] for w in l)
    sg = tuple(s for w in words for s in cun_signs(w))
    s = seal.setdefault(sid, dict(sid=sid, prov=u["prov"], words=words, signs=sg, dates=[]))
    if u["pid"] in date: s["dates"].append(date[u["pid"]])
S = list(seal.values())
for s in S: s["first"] = min(s["dates"]) if s["dates"] else None


def analyse(S, label):
    by = defaultdict(list)
    for s in S: by[s["signs"]].append(s)
    rep = {k: v for k, v in by.items() if len(v) >= 2}
    pairs = [(a, b) for v in rep.values() for a, b in itertools.combinations(v, 2)]
    same_arch = [p for p in pairs if p[0]["prov"] == p[1]["prov"]]
    dated = [p for p in same_arch if p[0]["first"] and p[1]["first"]]
    diff_reign = sum(p[0]["first"][0] != p[1]["first"][0] for p in dated)
    # random same-archive pairs of seals (dated)
    rnd = random.Random(1); byp = defaultdict(list)
    for s in S:
        if s["first"]: byp[s["prov"]].append(s)
    byp = {k: v for k, v in byp.items() if len(v) >= 2}
    w = [len(v) for v in byp.values()]; provs = list(byp)
    rr = []
    for _ in range(20000):
        p = rnd.choices(provs, weights=w)[0]; a, b = rnd.sample(byp[p], 2); rr.append(a["first"][0] != b["first"][0])
    # random pair cross-archive base rate
    tot = sum(w); cross_base = 1 - sum((x / tot) ** 2 for x in w)
    # one-word-longer legend in same archive
    words_by_prov = defaultdict(set)
    for s in S: words_by_prov[s["prov"]].add(s["words"])
    def has_longer(s):
        for u in words_by_prov[s["prov"]]:
            if len(u) == len(s["words"]) + 1 and any(u[:i] + u[i + 1:] == s["words"] for i in range(len(u))): return True
        return False
    def has_shorter(s):
        ws = s["words"]; return any(ws[:i] + ws[i + 1:] in words_by_prov[s["prov"]] for i in range(len(ws)))
    rep_first = [v[0] for v in rep.values()]
    single = [v[0] for v in by.values() if len(v) == 1]
    rnd2 = random.Random(2); single_s = rnd2.sample(single, min(3000, len(single)))
    out = dict(label=label, n_seals=len(S), n_legends=len(by), n_rep_legends=len(rep),
               seals_on_rep=sum(len(v) for v in rep.values()), share_seals_on_rep=sum(len(v) for v in rep.values()) / len(S),
               n_pairs=len(pairs), share_pairs_same_archive=len(same_arch) / max(1, len(pairs)),
               random_pair_cross_archive=cross_base,
               dated_same_arch_pairs=len(dated), share_diff_reign=diff_reign / max(1, len(dated)),
               random_same_arch_diff_reign=sum(rr) / len(rr),
               rep_has_longer=sum(map(has_longer, rep_first)) / max(1, len(rep_first)),
               single_has_longer=sum(map(has_longer, single_s)) / len(single_s),
               rep_has_shorter=sum(map(has_shorter, rep_first)) / max(1, len(rep_first)),
               single_has_shorter=sum(map(has_shorter, single_s)) / len(single_s))
    print(json.dumps(out))
    return out


res = {"all": analyse(S, "all legends"), "le7": analyse([s for s in S if len(s["signs"]) <= 7], "legends <=7 written signs"),
       "4to7": analyse([s for s in S if 4 <= len(s["signs"]) <= 7], "legends 4-7 written signs")}
# examples
by = defaultdict(list)
for s in S: by[s["signs"]].append(s)
ex = sorted([v for v in by.values() if len(v) >= 2 and len(v[0]["signs"]) <= 7], key=len, reverse=True)[:8]
res["examples_le7"] = [dict(legend=" ".join(v[0]["words"]), n=len(v), provs=dict(Counter(s["prov"] for s in v))) for v in ex]
json.dump(res, open(os.path.join(HERE, "ur3_ref.json"), "w"), indent=1)
for e in res["examples_le7"]: print(e)
