#!/usr/bin/env python3
"""Build the sign catalogue: site/signs/index.html (grid) and site/signs/M{n}.html (one page per sign).

Called by site/build.py (which also checks every link). Run alone to rebuild only the sign data snapshot:
    .venv/bin/python -I site/build_signs.py

Every fact on these pages is computed from repo files at build time. Nothing is typed by hand except
the short labels of KEY_RESULTS and CLAIM_UPDATES, and each of those carries a quote that must appear
verbatim in its source file or the build stops.

What it reads
  data/m77_texts.jsonl, data/icit_texts.jsonl     the two corpora (not in the public repo; see LICENSING.md)
  data/sign_images/M*.png                         Mahadevan's drawings (provenance flagged in LICENSING.md)
  sources/shaunmortal_indus/data/bridge_WM.json   Mahadevan <-> Wells concordance (176 Wells signs)
  sources/shaunmortal_indus/data/model3b_allographs_min8.json   allograph / look-alike pairs (shaunmortal M3)
  experiments/signlist_robustness/variants.json   alternative sign lists (merges)
  experiments/grammar/sign_classes.csv            validated positional classes (docs/GRAMMAR.md)
  experiments/functional_reading/lexicon.csv      functional roles and fixed sequences
  experiments/literature/proposals.json           published sign-value proposals
  experiments/meaning_claims/CATALOGUE.csv        published meaning claims with test status
  experiments/*/RESULTS.md, docs/NEGATIVE_ATLAS.md, docs/GRAMMAR.md, README.md   mentions of each sign

When data/ or sources/ is absent (a public clone), the last snapshot in site/data/signs.json is used.
"""
import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
SNAP = SITE / "data" / "signs.json"
N_SIGNS = 417
EXAMPLES = 3          # example texts per sign page. Whole texts: whether these may be published is open (LICENSING.md).
NO_SIGN = {148}       # same rule as build.py: M148's drawing is never shown

SITE_NAMES = {"Mohenjodaro": "Mohenjo-daro", "Chanhudaro": "Chanhu-daro", "Other sites": "other sites",
              "West Asian finds": "West Asian finds"}
TYPE_GROUP = {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet", "copper tablet": "copper tablet",
              "pottery graffito": "pottery", "ivory/bone rod": "other", "bronze implement": "other", "miscellaneous": "other"}
TYPE_ORDER = ["seal", "sealing", "tablet", "copper tablet", "pottery", "other"]
TYPE_PLURAL = {"seal": "seals", "sealing": "sealings", "tablet": "tablets", "copper tablet": "copper tablets",
               "pottery": "pottery", "other": "other objects"}
TYPE_LABEL = {"seal": "Seal", "sealing": "Sealing", "tablet": "Tablet", "copper tablet": "Copper tablet",
              "pottery": "Pottery", "other": "Other"}


def icit_group(t):
    if t.startswith("SEAL"):
        return "seal"
    if t.startswith("TAG"):
        return "sealing"
    if t == "TAB:C":
        return "copper tablet"
    if t.startswith("TAB"):
        return "tablet"
    if t.startswith("PO"):
        return "pottery"
    return "other"


def mnum(s):
    return int(s[1:])


def wid(k):
    return f"W{int(k):03d}"


def jl(p):
    return [json.loads(l) for l in open(p)]


def runs(seq):
    out, cur = [], []
    for s in seq:
        if s in ("|", "#"):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur:
        out.append(cur)
    return out


def distinct(rows):
    seen, out = set(), []
    for r in rows:
        k = " ".join(r["seq"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


# ---------------------------------------------------------------- sourced labels
# Each label is a plain summary of a result in the repo; `quote` must appear verbatim in `path`.
KEY_RESULTS = [
    dict(signs=["M403", "M87"], path="experiments/parpola_rules34/RESULTS.md",
         quote="M403 is followed by M87 in 23 of 48 dev tokens",
         title="M403 is followed by M87 about half the time: a fixed pair",
         line="Holds on held-out texts and at post-1977 sites. It is a fixed pair, not a reading; the red team labels it fragile."),
    dict(signs=["M103", "M403"], path="experiments/functional_reading/RESULTS.md",
         quote="the bound numeral compound M103→M403",
         title="M103 (three strokes as two over one) is bound to M403",
         line="A grade-A fixed sequence in the functional reading, from the prior project's F7."),
    dict(signs=["M87", "M59"], path="experiments/parpola_rules34/RESULTS.md",
         quote="Rule 3 (M87 substitutes for fish M59): underpowered",
         title="Whether M87 stands in for the fish M59 cannot be tested at this corpus size",
         line="The method found 2% of planted stand-ins; M87 sits next to the fish rather than in its slot.", level="untestable"),
]
FISH_FAMILY_RE = (ROOT / "experiments/core_semantics/RESULTS.md", r"One core class is solid: the fish family\*\* \(([M0-9, ]+)\)")
# Updates to a published claim's status from a later test in the repo (catalogue id or proposal key -> outcome).
CLAIM_UPDATES = {
    "PAR-murukan-partners": dict(status="partly holds", path="experiments/parpola_rules34/RESULTS.md",
                                 quote="the M87 half passes, the squirrel half gets nothing",
                                 detail="Tested later (Parpola rules 3 and 4): M403 is followed by M87 far more than chance; the squirrel never follows M403. A fixed pair, not a reading."),
    "PAR-vel-substitution": dict(status="underpowered", path="experiments/parpola_rules34/RESULTS.md",
                                 quote="Rule 3 (M87 substitutes for fish M59): underpowered",
                                 detail="Tested later (Parpola rules 3 and 4): the method found too few planted stand-ins to decide either way."),
    ("parpola", "aṟu-mīn"): dict(status="partly holds", path="site/build.py", quote="The pair is confirmed as a unit",
                                 detail="Six followed by fish is a fixed expression (finding 5); the star reading itself is not tested."),
    ("parpola", "eḻu-mīn"): dict(status="did not hold", path="site/build.py", quote="the “seven stars” reading is not supported",
                                 detail="Seven plus fish is not a fixed pair the way six plus fish is (finding 5)."),
    ("parpola", "rebus 'star'"): dict(status="did not hold", path="experiments/core_semantics/RESULTS.md",
                                      quote="\"Fish = deity class\" (Parpola) is not supported",
                                      detail="The fish signs form one substituting class, but the deity-name test failed on held-out texts."),
    ("parpola", "muruku"): dict(status="partly holds", path="experiments/parpola_rules34/RESULTS.md",
                                quote="Rule 4 is a fixed pair, not a reading",
                                detail="M403 is followed by M87 as Parpola observed; the Murukan reading is not tested by this."),
    ("yajnadevam", ""): dict(status="did not hold", path="docs/NEGATIVE_ATLAS.md", quote="Refuted at stated power, for these keys",
                             detail="Part of a 714-value sound key that scores no better than keys fitted to noise (atlas 1.1)."),
}


def check_quote(path, quote):
    text = (ROOT / path).read_text()
    if quote not in text:
        raise SystemExit(f"build_signs: quote not found in {path}: {quote!r}")


# ---------------------------------------------------------------- data
def mentions():
    """Lines in RESULTS files and core docs that mention each sign id."""
    files = sorted(ROOT.glob("experiments/*/RESULTS.md")) + [ROOT / "docs/NEGATIVE_ATLAS.md", ROOT / "docs/GRAMMAR.md", ROOT / "README.md"]
    files = [f for f in files if "ensemble_rehearsal" not in f.parts]
    out = defaultdict(list)
    for f in files:
        rel = str(f.relative_to(ROOT))
        lines = f.read_text().splitlines()
        title = next((l[2:].strip() for l in lines if l.startswith("# ")), rel)
        hits = defaultdict(list)
        for line in lines:
            for m in set(re.findall(r"(?<![\w/.-])M(\d{1,3})(?![\w])", line)):
                n = int(m)
                if not 1 <= n <= N_SIGNS:
                    continue
                if n == 77 and not re.search(r"\bsign M77\b", line):
                    continue      # M77 is also the name of the corpus
                if n <= 6 and (not re.search(r"\bsigns?\b", line, re.I) or re.search(r"milestone|\bM[1-6]\b\s*(\(|:|names|bench|south|sign meaning|latest|red team)", line, re.I)):
                    continue      # M1-M6 are also milestone and model names
                hits[n].append(line)
        for n, ls in hits.items():
            out[f"M{n}"].append(dict(path=rel, title=clean(title), n=len(ls), snippet=snippet(ls[0], f"M{n}")))
    return out


def clean(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("**", "").replace("`", "").replace("|", " ").strip()
    s = re.sub(r"^[-*#>\d.\s]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def snippet(line, sid, width=200):
    s = clean(line)
    i = s.find(sid)
    if len(s) <= width:
        return s
    a = max(0, i - width // 2)
    b = min(len(s), a + width)
    return ("…" if a else "") + s[a:b].strip() + ("…" if b < len(s) else "")


def parse_signs_field(s):
    out = []
    for a, b in re.findall(r"\bM(\d{1,3})(?:\s*-\s*M?(\d{1,3}))?", s):
        a = int(a)
        b = int(b) if b else a
        if b < a or b - a > 40:
            b = a
        out += [f"M{n}" for n in range(a, b + 1) if 1 <= n <= N_SIGNS]
    return out


def compute():
    m77 = jl(ROOT / "data/m77_texts.jsonl")
    icit = jl(ROOT / "data/icit_texts.jsonl")
    bridge = json.loads((ROOT / "sources/shaunmortal_indus/data/bridge_WM.json").read_text())
    m2w = defaultdict(list)
    w2m = {}
    for k, v in bridge.items():
        w2m[wid(k)] = [f"M{x}" for x in v["M"]]
        for x in v["M"]:
            m2w[f"M{x}"].append(wid(k))

    S = {f"M{n}": dict(id=f"M{n}", n=n, objects=0, tokens=0, texts=0, by_type=Counter(), by_site=Counter(),
                       pos=Counter(), before=Counter(), after=Counter(), examples=[]) for n in range(1, N_SIGNS + 1)}
    for r in m77:
        for s in r["seq"]:
            if s in S:
                S[s]["tokens"] += 1
        for s in {x for x in r["seq"] if x in S}:
            S[s]["objects"] += 1
    dm = distinct(m77)
    seen_cat = defaultdict(set)
    bigram = Counter()
    first = Counter()
    for r in dm:
        seq = r["seq"]
        signs = [x for x in seq if x in S]
        g = TYPE_GROUP.get(r["object_type"], "other")
        site = SITE_NAMES.get(r["site"], r["site"])
        for s in set(signs):
            S[s]["texts"] += 1
            S[s]["by_type"][g] += 1
            S[s]["by_site"][site] += 1
        if "#" not in seq:           # position only where the whole text is legible
            flat = [x for x in seq if x != "|"]
            for i, s in enumerate(flat):
                if s not in S:
                    continue
                k = "alone" if len(flat) == 1 else "initial" if i == 0 else "final" if i == len(flat) - 1 else "medial"
                S[s]["pos"][k] += 1
        for run in runs(seq):
            for a, b in zip(run, run[1:]):
                bigram[(a, b)] += 1
                S[b]["before"][a] += 1
                S[a]["after"][b] += 1
            for a in run:
                first[a] += 1
    # fixed pairs: at least 5 texts, and one sign takes the other at least half the time
    pairs = defaultdict(list)
    for (a, b), c in bigram.items():
        if c < 5 or a not in S or b not in S:
            continue
        pa, pb = c / max(1, sum(S[a]["after"].values())), c / max(1, sum(S[b]["before"].values()))
        if max(pa, pb) >= 0.5:
            d = dict(a=a, b=b, n=c, after_a=round(pa, 2), before_b=round(pb, 2))
            pairs[a].append(d)
            if b != a:
                pairs[b].append(d)

    # examples: complete texts, varied object types and sites, 2-8 signs, in corpus order
    for s in S.values():
        pool = [r for r in dm if s["id"] in r["seq"]]
        pool.sort(key=lambda r: (not r.get("complete"), "#" in r["seq"], not 2 <= len([x for x in r["seq"] if x != "|"]) <= 8))
        picked, used = [], set()
        for r in pool:
            key = (TYPE_GROUP.get(r["object_type"], "other"), r["site"])
            if key in used and len(pool) > EXAMPLES:
                continue
            used.add(key)
            picked.append(r)
            if len(picked) == EXAMPLES:
                break
        for r in pool:          # fill up if the varied pick ran short
            if len(picked) >= EXAMPLES:
                break
            if r not in picked:
                picked.append(r)
        s["examples"] = [dict(no=r["text_no"], site=SITE_NAMES.get(r["site"], r["site"]), type=r["object_type"],
                              seq=r["seq"], complete=bool(r.get("complete"))) for r in picked]

    # ICIT, per Wells sign
    di = distinct(icit)
    W = defaultdict(lambda: dict(texts=0, tokens=0, by_site=Counter(), by_type=Counter()))
    for r in icit:
        for x in r["seq"]:
            if x.startswith("W"):
                W[x]["tokens"] += 1
    for r in di:
        for x in {y for y in r["seq"] if y.startswith("W")}:
            W[x]["texts"] += 1
            W[x]["by_site"][r["site"]] += 1
            W[x]["by_type"][icit_group(r["type"])] += 1

    classes = {r["sign"]: r for r in csv.DictReader(open(ROOT / "experiments/grammar/sign_classes.csv"))}
    lex = list(csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")))
    lex_sign = {r["item"]: r for r in lex if r["kind"] == "sign"}
    lex_seq = defaultdict(list)
    for r in lex:
        if r["kind"].startswith("sequence"):
            for x in set(re.findall(r"M\d+", r["item"])):
                lex_seq[x].append(dict(item=r["item"].replace("-", " "), kind=r["kind"].split(":")[1].lower().replace("-", " "),
                                       dev_texts=r["dev_texts"], meaning=r["meaning_category"], grade=r["role_grade"]))

    # variants
    var = json.loads((ROOT / "experiments/signlist_robustness/variants.json").read_text())["partitions"]
    groups = {}
    for lst, part in var.items():
        if lst == "M77":
            continue
        g = defaultdict(list)
        for s, k in part.items():
            g[k].append(s)
        groups[lst] = {s: sorted(g[k], key=mnum) for s, k in part.items() if len(g[k]) > 1}
    allo = json.loads((ROOT / "sources/shaunmortal_indus/data/model3b_allographs_min8.json").read_text())
    allo_pairs = defaultdict(list)
    for kind in ("allograph_candidates", "lookalikes_distinct"):
        for a, b, img, dist in allo.get(kind, []):
            for x, y in ((a, b), (b, a)):
                allo_pairs[f"M{x}"].append(dict(other=f"M{y}", kind=kind, image=img, context=dist))

    # published readings
    props = json.loads((ROOT / "experiments/literature/proposals.json").read_text())["proposals"]
    readings = defaultdict(list)
    for author, rows in props.items():
        for p in rows:
            for s in p.get("sign_M") or []:
                if s not in S:
                    continue
                upd = None
                for key, u in CLAIM_UPDATES.items():
                    if isinstance(key, tuple) and key[0] == author and key[1] in p["proposed_value"]:
                        upd = u
                        break
                readings[s].append(dict(kind="proposal", author=author, year=year_of(p["source"]), sign=p["sign"],
                                        value=p["proposed_value"], source=p["source"], confidence=p.get("mapping_confidence", ""),
                                        status=upd["status"] if upd else "not tested on its own",
                                        detail=upd.get("detail", "") if upd else "", status_path=upd["path"] if upd else "",
                                        collapsed=author == "yajnadevam"))
    for c in csv.DictReader(open(ROOT / "experiments/meaning_claims/CATALOGUE.csv")):
        ms = parse_signs_field(c["signs_M"])
        if not ms:
            for w in re.findall(r"W\d{3}", c["signs_W"] + " " + c["signs_M"]):
                ms += w2m.get(w, [])
        upd = CLAIM_UPDATES.get(c["id"])
        st = c["status"].lower()
        status = (upd["status"] if upd else "untestable" if st.startswith("untestable") else
                  "testable, not yet run" if st.startswith("testable") else "tested" if st.startswith("already") else st)
        for s in dict.fromkeys(ms):
            if s in S:
                readings[s].append(dict(kind="claim", id=c["id"], author=c["author"], year=c["year"], value=c["claimed_meaning"],
                                        source=c["source"], basis=c["basis"], status=status,
                                        detail=upd["detail"] if upd and upd.get("detail") else c["status_detail"],
                                        status_path=upd["path"] if upd else "experiments/meaning_claims/CATALOGUE.csv",
                                        collapsed=False))

    for k in KEY_RESULTS:
        check_quote(k["path"], k["quote"])
    for u in CLAIM_UPDATES.values():
        check_quote(u["path"], u["quote"])
    fam_path, fam_re = FISH_FAMILY_RE
    fish = re.search(fam_re, fam_path.read_text())
    fish_family = re.findall(r"M\d+", fish.group(1)) if fish else []

    ment = mentions()
    out = []
    for n in range(1, N_SIGNS + 1):
        s = S[f"M{n}"]
        sid = s["id"]
        ws = sorted(set(m2w.get(sid, [])))
        icit_rows = []
        for w in ws:
            d = W.get(w)
            icit_rows.append(dict(w=w, shared=[x for x in w2m.get(w, []) if x != sid], texts=d["texts"] if d else 0,
                                  tokens=d["tokens"] if d else 0, by_site=(d["by_site"].most_common(6) if d else []),
                                  by_type=dict(d["by_type"]) if d else {}))
        cl = classes.get(sid)
        lx = lex_sign.get(sid)
        out.append(dict(
            id=sid, n=n, texts=s["texts"], objects=s["objects"], tokens=s["tokens"],
            by_type={k: s["by_type"][k] for k in TYPE_ORDER if s["by_type"][k]},
            by_site=s["by_site"].most_common(), pos=dict(s["pos"]),
            before=s["before"].most_common(6), after=s["after"].most_common(6),
            pairs=sorted(pairs.get(sid, []), key=lambda d: -d["n"])[:8], sequences=lex_seq.get(sid, []),
            examples=s["examples"], wells=ws, icit=icit_rows,
            grammar=dict(cls=cl["final_class"], conf=cl["confidence"], raw=cl["label_raw"], dev_tokens=cl["dev_tokens"],
                         wells_check=cl["wells_check"]) if cl else None,
            lexicon=dict(roles=lx["roles"], meaning=lx["meaning_category"], evidence=lx["evidence"], grade=lx["role_grade"],
                         source=lx["source"]) if lx else None,
            variants={lst: g[sid] for lst, g in groups.items() if sid in g},
            allographs=allo_pairs.get(sid, []),
            readings=readings.get(sid, []),
            key_results=[dict(k, signs=k["signs"]) for k in KEY_RESULTS if sid in k["signs"]],
            fish_family=sid in fish_family, fish_family_list=fish_family,
            mentions=sorted(ment.get(sid, []), key=lambda m: -m["n"]),
        ))
    return out


def year_of(src):
    m = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", src)
    return m.group(1) if m else ""


def load():
    have = (ROOT / "data/m77_texts.jsonl").is_file() and (ROOT / "sources/shaunmortal_indus/data/bridge_WM.json").is_file()
    if not have:
        print("signs: corpus not found, using the snapshot in site/data/signs.json")
        return json.loads(SNAP.read_text())["signs"]
    signs = compute()
    SNAP.parent.mkdir(exist_ok=True)
    SNAP.write_text(json.dumps({"_readme": "Written by site/build_signs.py from data/ and the repo's results. Do not edit.",
                                "signs": signs}, ensure_ascii=False, separators=(",", ":")))
    return signs


def copy_drawings():
    out = SITE / "assets" / "signs"
    out.mkdir(parents=True, exist_ok=True)
    src = ROOT / "data" / "sign_images"
    for n in range(1, N_SIGNS + 1):
        if n in NO_SIGN:
            continue
        dst = out / f"M{n}.png"
        if not dst.exists() and (src / f"M{n}.png").exists():
            shutil.copy2(src / f"M{n}.png", dst)


# ---------------------------------------------------------------- HTML
def html_pages(b):
    """b is the build module (render, E, repo_link, FINDINGS...). Returns the written page paths."""
    E = b.E
    signs = load()
    copy_drawings()
    by_id = {s["id"]: s for s in signs}
    findings = {f["n"]: f for f in b.FINDINGS}
    fish_family = next((s["fish_family_list"] for s in signs if s["fish_family_list"]), [])
    FINDING_SIGNS = {3: [f"M{g}" for g in findings[3].get("glyphs", ())], 5: [f"M{g}" for g in findings[5].get("glyphs", ())],
                     11: fish_family}

    def img(sid, cls="sg", size=None, alt=None, lazy=True):
        n = mnum(sid)
        if n in NO_SIGN:
            return f'<span class="{cls} sg-none" role="img" aria-label="sign {sid}, drawing not shown">{sid}</span>'
        wh = f' width="{size}" height="{size}"' if size else ""
        return (f'<img class="{cls}" src="assets/signs/{sid}.png"{wh} alt="{E(alt if alt is not None else "sign " + sid)}"'
                f'{" loading=\"lazy\"" if lazy else ""} decoding="async">')

    def slink(sid):
        return f'<a class="sref" href="signs/{sid}.html">{img(sid, "sg sg-xs", 20, "")}<span>{sid}</span></a>'

    def pct(a, t):
        return f"{round(100 * a / t)}%" if t else "–"

    def role_of(s):
        g = s["grammar"]
        return g["cls"] if g else "not classified"

    def summary(s):
        if not s["texts"]:
            return "Not found in the 1977 concordance texts."
        t = s["texts"]
        parts = [f'Appears in {t:,} {"text" if t == 1 else "texts"} ({s["tokens"]:,} {"use" if s["tokens"] == 1 else "uses"})']
        bt = sorted(s["by_type"].items(), key=lambda kv: -kv[1])
        if bt:
            top, c = bt[0]
            on = (f"mostly on {TYPE_PLURAL[top]}" if c / t >= 0.5 else
                  f"on {TYPE_PLURAL[top]} and {TYPE_PLURAL[bt[1][0]]}" if len(bt) > 1 else f"on {TYPE_PLURAL[top]}")
            if t <= 2:
                on = f"on {' and '.join(TYPE_PLURAL[k] for k, _ in bt)}"
            bs = s["by_site"]
            at = ""
            if bs:
                if bs[0][1] / t >= 0.5 or len(bs) == 1:
                    at = f" at {bs[0][0]}"
                elif len(bs) > 1:
                    at = f" at {bs[0][0]} and {bs[1][0]}"
            parts[0] += f", {on}{at}"
        p = s["pos"]
        tot = sum(p.values())
        if tot < 5:
            pos = "too rare to say where it sits in a text"
        else:
            share = {k: p.get(k, 0) / tot for k in ("initial", "medial", "final", "alone")}
            pos = ("usually stands alone" if share["alone"] >= 0.5 else "usually ends a text" if share["final"] >= 0.5 else
                   "usually starts a text" if share["initial"] >= 0.5 else "usually sits inside a text" if share["medial"] >= 0.6 else
                   "found at the start, middle and end of texts")
        out = "; ".join([parts[0], pos]) + "."
        if s["icit"]:
            w = s["icit"][0]
            new = [site for site, _ in w["by_site"] if site in ("Dholavira", "Banawali", "Rakhigarhi", "Nausharo", "Kanmer", "Farmana")]
            out += (f' In the larger ICIT corpus its Wells equivalent {w["w"]} is in {w["texts"]:,} {"text" if w["texts"] == 1 else "texts"}'
                    + (f", including at {new[0]}" if new else "") + ".")
        return out

    def established(s):
        out = []
        g = s["grammar"]
        if g and g["cls"] in ("opener", "closer", "connective"):
            out.append(dict(title=f'Validated {g["cls"]}: {dict(opener="starts texts", closer="ends texts", connective="follows an opener")[g["cls"]]}',
                            line=f'Kept its class in {round(100 * float(g["conf"]))}% of bootstrap resamples'
                                 + ("; the Wells-list grammar agrees." if g["wells_check"] == "agree" else "."),
                            path="docs/GRAMMAR.md", tag="Held up", cls="ok"))
        for n, ids in FINDING_SIGNS.items():
            if s["id"] in ids:
                f = findings[n]
                lvl = b.STRENGTH and next(w for k, w, _ in b.STRENGTH if k == f["level"])
                out.append(dict(title=f["head"], line=f["gist"], path=f["folders"][0] + "/", tag=lvl,
                                cls="ok" if f["level"] == "strong" else "", href=f"findings.html#f{n}"))
        for k in s["key_results"]:
            unt = k.get("level") == "untestable"
            out.append(dict(title=k["title"], line=k["line"], path=k["path"], tag="Can’t test yet" if unt else "Held up",
                            cls="wait" if unt else "ok"))
        return out

    # ---------- sign pages
    pages = []
    status_cls = {"holds": "ok", "partly holds": "run", "did not hold": "out", "underpowered": "wait", "untestable": "wait",
                  "testable, not yet run": "", "tested": "", "not tested on its own": "wait"}
    status_lab = {"holds": "Holds", "partly holds": "Partly holds", "did not hold": "Did not hold", "underpowered": "Underpowered",
                  "untestable": "Untestable with our data", "testable, not yet run": "Testable, not yet run",
                  "tested": "Tested, see detail", "not tested on its own": "Not tested on its own"}
    n_read = n_tests = 0
    for i, s in enumerate(signs):
        sid = s["id"]
        prev_s, next_s = signs[i - 1]["id"] if i else None, signs[i + 1]["id"] if i + 1 < len(signs) else None
        est = sorted(established(s), key=lambda e: {"ok": 0, "": 1, "run": 1, "wait": 2}.get(e["cls"], 1))

        # where it appears
        t = s["texts"]
        rows_t = "".join(f'<tr><th scope="row">{TYPE_LABEL[k]}</th><td>{v:,}</td><td>{pct(v, t)}</td></tr>' for k, v in s["by_type"].items())
        rows_s = "".join(f'<tr><th scope="row">{E(k[:1].upper() + k[1:])}</th><td>{v:,}</td><td>{pct(v, t)}</td></tr>' for k, v in s["by_site"])
        p = s["pos"]
        ptot = sum(p.values())
        pos_rows = "".join(f'<tr><th scope="row">{lab}</th><td>{p.get(k, 0):,}</td><td>{pct(p.get(k, 0), ptot)}</td></tr>'
                           for k, lab in (("initial", "First sign"), ("medial", "Inside"), ("final", "Last sign"), ("alone", "Whole text")))
        icit = ""
        for w in s["icit"]:
            shared = f' Wells lumps it with {", ".join(w["shared"])}, so these counts cover both.' if w["shared"] else ""
            bt = ", ".join(f"{TYPE_PLURAL[k]} {v:,}" for k, v in sorted(w["by_type"].items(), key=lambda kv: -kv[1]))
            bs = ", ".join(f"{E(k)} {v:,}" for k, v in w["by_site"])
            icit += (f'<p><b>{w["w"]}</b>: {w["texts"]:,} distinct texts, {w["tokens"]:,} uses.{shared}</p>'
                     + (f'<p class="small">By object: {bt}. Top sites: {bs}.</p>' if w["texts"] else ""))
        where = (f'<p class="small">Counts are distinct texts in the Mahadevan 1977 concordance (a text repeated on many moulded tablets counts once). '
                 f'{s["objects"]:,} objects in all carry it.</p>'
                 f'<div class="sg-tables"><table><caption>By object</caption><thead><tr><th scope="col">Object</th><th scope="col">Texts</th><th scope="col">Share</th></tr></thead><tbody>{rows_t or "<tr><td colspan=3>None</td></tr>"}</tbody></table>'
                 f'<table><caption>By site</caption><thead><tr><th scope="col">Site</th><th scope="col">Texts</th><th scope="col">Share</th></tr></thead><tbody>{rows_s or "<tr><td colspan=3>None</td></tr>"}</tbody></table>'
                 f'<table><caption>Position in the text</caption><thead><tr><th scope="col">Where</th><th scope="col">Uses</th><th scope="col">Share</th></tr></thead><tbody>{pos_rows}</tbody></table></div>'
                 f'<p class="small">Position counts use only texts with no damaged passage ({ptot:,} uses).</p>'
                 + (f'<h3 class="sg-h3">In the ICIT corpus (Wells numbering)</h3>{icit}' if icit else
                    '<p class="small">No Wells equivalent in the concordance this project uses, so there are no ICIT counts.</p>'))

        # variants
        var = []
        if s["wells"]:
            var.append(f'<p><b>Wells (ICIT) equivalent:</b> {", ".join(s["wells"])}.</p>')
        al = [a for a in s["allographs"] if a["kind"] == "allograph_candidates"]
        lk = [a for a in s["allographs"] if a["kind"] == "lookalikes_distinct"]
        if al:
            var.append('<p><b>Probably the same sign</b> (looks alike and is used alike):</p><ul class="sg-refs">'
                       + "".join(f'<li>{slink(a["other"])}<span class="small">drawing similarity {a["image"]:.2f}, context similarity {a["context"]:.2f}</span></li>' for a in al) + "</ul>")
        if lk:
            var.append('<p><b>Looks alike but used differently</b> (probably a separate sign):</p><ul class="sg-refs">'
                       + "".join(f'<li>{slink(a["other"])}<span class="small">drawing similarity {a["image"]:.2f}, context similarity {a["context"]:.2f}</span></li>' for a in lk) + "</ul>")
        if al or lk:
            var.append(f'<p class="small">Pairs from the prior project’s allograph model (image × distribution, signs with at least 8 uses).</p>')
        if s["variants"]:
            names = {"parpola": "Parpola’s list", "lump_fish": "Fish forms merged", "lump_numerals": "Numerals merged by value",
                     "lump_jar_man": "Jar and man forms merged", "lump_all": "All proposed merges", "img_hi": "Merged by drawing (fine)",
                     "img_mid": "Merged by drawing (medium)", "img_lo": "Merged by drawing (coarse)"}
            var.append('<p><b>Merged with other signs in alternative sign lists</b> (used to test whether findings survive):</p><ul class="sg-merge">'
                       + "".join(f'<li><span>{E(names.get(k, k))}</span> {" ".join(slink(x) for x in v if x != sid)}</li>' for k, v in s["variants"].items())
                       + f'</ul><p class="small">{b.repo_link("experiments/signlist_robustness/RESULTS.md", "How the alternative lists were built and what survived")}</p>')
        if not var:
            var.append("<p>No Wells equivalent, allograph pair or merge is recorded for this sign.</p>")

        # neighbours and fixed pairs
        def nb(rows):
            return "".join(f'<li>{slink(x)}<span class="small">{c:,}</span></li>' for x, c in rows) or "<li>None recorded</li>"
        fp = "".join(f'<li>{slink(d["a"])}{slink(d["b"])}<span class="small">{d["n"]:,} texts. {d["a"]} is followed by {d["b"]} {round(100 * d["after_a"])}% of the time; '
                     f'{d["b"]} follows {d["a"]} {round(100 * d["before_b"])}% of the time.</span></li>' for d in s["pairs"])
        sq = "".join(f'<li><span>{" ".join(slink(x) for x in d["item"].split())}</span><span class="small">{E(d["kind"].capitalize())}, {E(d["dev_texts"])} development texts, grade {E(d["grade"])}. {E(d["meaning"][:1].upper() + d["meaning"][1:])}.</span></li>'
                     for d in s["sequences"])
        neigh = (f'<div class="sg-cols"><div><h3 class="sg-h3">Comes after</h3><ul class="sg-refs">{nb(s["before"])}</ul></div>'
                 f'<div><h3 class="sg-h3">Comes before</h3><ul class="sg-refs">{nb(s["after"])}</ul></div></div>'
                 f'<p class="small">Signs read directly before or after it, counted in distinct texts, never across a line break or damage.</p>'
                 + (f'<h3 class="sg-h3">Fixed pairs</h3><ul class="sg-pairs">{fp}</ul><p class="small">At least 5 texts, and one sign takes the other at least half the time.</p>' if fp else "")
                 + (f'<h3 class="sg-h3">Fixed sequences in the functional reading</h3><ul class="sg-pairs">{sq}</ul>'
                    f'<p class="small">{b.repo_link("experiments/functional_reading/lexicon.csv", "lexicon.csv")}</p>' if sq else ""))

        # readings
        main = [r for r in s["readings"] if not r["collapsed"]]
        yaj = [r for r in s["readings"] if r["collapsed"]]
        def reading(r):
            who = E(r["author"].replace("fuls2024_linear_elamite_lookalikes", "Fuls").capitalize() if r["kind"] == "proposal" else r["author"])
            yr = E(", ".join(dict.fromkeys(re.findall(r"\b1[89]\d\d\b|\b20\d\d\b", str(r["year"]))))) if r["year"] else ""
            src = r["source"]
            url = re.search(r"https?://\S+", src)
            src_txt = re.sub(r"\s*https?://\S+\s*", " ", src)
            src_txt = re.sub(r"([,;])(\s*[,;])+", r"\1", re.sub(r"\s+([,;])", r"\1", src_txt)).strip(" ;,")
            src_txt = E(src_txt or "Source")
            if url:
                href = url.group(0).rstrip(".,;)")
                lead = re.match(r"[^(]*[A-Za-z]", src_txt or "")   # link text needs words of its own, else use the site name
                src_html = (f'<a href="{E(href)}">{src_txt}</a>' if lead else
                            f'<a href="{E(href)}">{E(re.sub(r"^www\.", "", href.split("/")[2]))}</a> {src_txt if src_txt != "Source" else ""}'.strip())
            else:
                src_html = src_txt
            det = f'<p class="small">{E(r["detail"])}</p>' if r.get("detail") else ""
            if r["kind"] == "proposal" and r["author"] == "fuls2024_linear_elamite_lookalikes":
                det += '<p class="small">A Linear Elamite sign that looks like this one, with its Linear Elamite sound value. Fuls lists look-alikes; he does not claim the Indus sign has this value.</p>'
            link = b.repo_link(r["status_path"], "test record") if r.get("status_path") else ""
            return (f'<li class="sg-read"><div class="sg-read-h"><b>{who}</b>{" · " + yr if yr else ""}'
                    f'<span class="tag {status_cls.get(r["status"], "")}">{E(status_lab.get(r["status"], r["status"]))}</span></div>'
                    f'<p>{E(r["value"])}</p><p class="small">{src_html}{" · " + link if link else ""}</p>{det}</li>')
        rd = ""
        if main:
            rd += '<ul class="sg-reads">' + "".join(reading(r) for r in main) + "</ul>"
        if yaj:
            y = yaj[0]
            rd += (f'<details class="sg-sub"><summary>Yajnadevam’s sound value</summary><ul class="sg-reads">{"".join(reading(r) for r in yaj)}</ul></details>')
        if not rd:
            rd = "<p>No published reading of this sign is in the project’s lists.</p>"
        rd += (f'<p class="small">From {b.repo_link("experiments/literature/proposals.json", "proposals.json")} and '
               f'{b.repo_link("experiments/meaning_claims/CATALOGUE.csv", "CATALOGUE.csv")}. A claim is listed under every sign it names.</p>')

        # project tests
        tests = ""
        if est:
            tests += '<h3 class="sg-h3">Established results</h3><ul class="sg-tests">' + "".join(
                f'<li><div class="sg-read-h"><b>{E(e["title"])}</b><span class="tag {e["cls"]}">{E(e["tag"])}</span></div><p>{E(e["line"])}</p>'
                f'<p class="small">{("<a href=\"" + e["href"] + "\">On the findings page</a> · ") if e.get("href") else ""}{b.repo_link(e["path"])}</p></li>' for e in est) + "</ul>"
        if s["grammar"] or s["lexicon"]:
            g, lx = s["grammar"], s["lexicon"]
            tests += '<h3 class="sg-h3">Role in the text</h3><dl class="sg-dl">'
            if g:
                tests += (f'<dt>Positional class</dt><dd>{E(g["cls"].capitalize())}'
                          + (f' (bootstrap stability {float(g["conf"]):.2f})' if g["cls"] != "unclassified" else
                             f'. Its raw label was {E(g["raw"])}, but it did not keep that label reliably.')
                          + f' {b.repo_link("docs/GRAMMAR.md", "Grammar")}</dd>')
            if lx and lx["source"] != "default":
                tests += (f'<dt>Functional reading</dt><dd>{E(lx["roles"])}. {E(lx["meaning"][:1].upper() + lx["meaning"][1:])}. '
                          f'<span class="small">{E(lx["evidence"])}</span> {b.repo_link("experiments/functional_reading/RESULTS.md", "Functional reading")}</dd>')
            tests += "</dl><p class=\"small\">Role names such as opener or noun are labels for positions, not tested meanings.</p>"
        ment = s["mentions"]
        if ment:
            tests += (f'<h3 class="sg-h3">Mentioned in {len(ment)} result {"file" if len(ment) == 1 else "files"}</h3><ul class="sg-ment">'
                      + "".join(f'<li>{b.repo_link(m["path"], m["title"])}<span class="small">{m["n"]} {"line" if m["n"] == 1 else "lines"}. “{E(m["snippet"])}”</span></li>' for m in ment)
                      + "</ul>")
        if not tests:
            tests = "<p>No project result mentions this sign yet.</p>"
        if s["readings"]:
            n_read += 1
        if est or ment:
            n_tests += 1

        # examples
        def seq_html(seq):
            out = []
            for x in seq:
                if x == "|":
                    out.append('<span class="sg-brk" title="line break">/</span>')
                elif x == "#":
                    out.append('<span class="sg-brk" title="damaged">…</span>')
                else:
                    cur = " sg-cur" if x == sid else ""
                    out.append(f'<a class="sg-tok{cur}" href="signs/{x}.html" title="{x}">{img(x, "sg sg-sm", 28, x)}</a>')
            return "".join(out)
        ex = "".join(f'<li><div class="sg-seq">{seq_html(e["seq"])}</div><p class="small">Text {e["no"]} · {E(e["site"])} · {E(e["type"])}'
                     f'{"" if e["complete"] else " · incomplete"} · {E(" ".join(x for x in e["seq"]))}</p></li>' for e in s["examples"])
        ex = (f'<ul class="sg-ex">{ex}</ul><p class="small">Signs in reading order, first sign on the left. Text numbers are Mahadevan’s (1977). / marks a line break, … a damaged passage.</p>'
              if ex else "<p>No example text.</p>")

        def sect(key, title, count, body):
            c = f' <span class="sg-count">{count}</span>' if count != "" else ""
            return f'<details class="sg-sec" id="{key}"><summary>{title}{c}</summary><div class="sg-body">{body}</div></details>'

        role = role_of(s)
        n_est = len(est)
        body = (
            f'<nav class="sg-crumb wrap" aria-label="Breadcrumb"><a href="signs/index.html">Sign catalogue</a></nav>'
            f'<section class="sg-head wrap"><div class="sg-big">{img(sid, "sg sg-lg", 154, "Drawing of sign " + sid, lazy=False)}</div>'
            f'<div class="sg-intro"><p class="kicker">Sign</p><h1>{sid}</h1>'
            f'<p class="sg-meta">{"Wells " + ", ".join(s["wells"]) + " · " if s["wells"] else ""}{E(role.capitalize())}</p>'
            f'<p class="lede">{E(summary(s))}</p>'
            + (f'<p class="sg-est"><b>Project finding:</b> {E(est[0]["title"])} <span class="tag {est[0]["cls"]}">{E(est[0]["tag"])}</span></p>' if est else "")
            + (f'<p class="small">Drawing not shown: out of context this sign is easily mistaken for a modern symbol.</p>' if mnum(sid) in NO_SIGN else "")
            + '</div></section>'
            f'<section class="wrap sg-secs">'
            + sect("where", "Where it appears", f'{t:,}', where)
            + sect("variants", "Variants", "", "".join(var))
            + sect("neighbours", "Neighbours and fixed pairs", len(s["pairs"]) + len(s["sequences"]) or "", neigh)
            + sect("readings", "Published readings", len(main) + len(yaj) or "", rd)
            + sect("tests", "Project tests", (n_est + len(ment)) or "", tests)
            + sect("examples", "Example texts", len(s["examples"]) or "", ex)
            + '</section>'
            f'<nav class="sg-pn wrap" aria-label="Previous and next sign">'
            + (f'<a href="signs/{prev_s}.html" rel="prev">{img(prev_s, "sg sg-sm", 28, "")}<span>Previous<b>{prev_s}</b></span></a>' if prev_s else "<span></span>")
            + f'<a class="sg-all" href="signs/index.html">All signs</a>'
            + (f'<a href="signs/{next_s}.html" rel="next"><span>Next<b>{next_s}</b></span>{img(next_s, "sg sg-sm", 28, "")}</a>' if next_s else "<span></span>")
            + '</nav>')
        pages.append(b.render("sign", f"Sign {sid} · {b.NAME} sign catalogue",
                              f"Indus sign {sid}: {summary(s)}", "signs/index.html", dict(SIGN_BODY=body), output=f"signs/{sid}.html"))

    # ---------- catalogue
    sites = [k for k, _ in Counter(site for s in signs for site, _ in s["by_site"]).most_common()]
    cards = []
    for s in signs:
        types = " ".join(k.replace(" ", "-") for k in s["by_type"])
        st = "|".join(k for k, _ in s["by_site"])
        search = " ".join([s["id"].lower()] + [w.lower() for w in s["wells"]])
        cards.append(f'<li data-n="{s["n"]}" data-f="{s["texts"]}" data-role="{E(role_of(s))}" data-types="{types}" data-sites="{E(st)}" '
                     f'data-read="{1 if any(not r["collapsed"] for r in s["readings"]) else 0}" data-q="{E(search)}">'
                     f'<a href="signs/{s["id"]}.html">{img(s["id"], "sg sg-md", 64, "")}<b>{s["id"]}</b>'
                     f'<small>{s["texts"]:,} {"text" if s["texts"] == 1 else "texts"}</small></a></li>')
    roles = Counter(role_of(s) for s in signs)
    role_btn = '<option value="">Any role</option>' + "".join(
        f'<option value="{k}">{k.capitalize()} ({roles[k]})</option>' for k in ("opener", "connective", "medial", "closer", "unclassified", "not classified") if roles[k])
    type_opt = '<option value="">Any object</option>' + "".join(
        f'<option value="{k.replace(" ", "-")}">{TYPE_LABEL[k]}</option>' for k in TYPE_ORDER)
    site_opt = '<option value="">Any site</option>' + "".join(f'<option value="{E(k)}">{E(k[:1].upper() + k[1:])}</option>' for k in sites)
    n_any_read = sum(1 for s in signs if any(not r["collapsed"] for r in s["readings"]))
    total_tok = sum(s["tokens"] for s in signs)
    pages.insert(0, b.render("signs", f"Sign catalogue · {b.NAME} · Every Indus sign",
                             "Every Indus sign in Mahadevan's 1977 list: where it appears, what comes before and after it, published readings and what the project's tests found.",
                             "signs/index.html", dict(SIGN_N=len(signs), SIGN_TOK=f"{total_tok:,}", SIGN_READ=n_any_read,
                                                      SIGN_TESTS=n_tests, SIGN_CARDS="".join(cards), SIGN_ROLES=role_btn,
                                                      SIGN_TYPES=type_opt, SIGN_SITES=site_opt),
                             output="signs/index.html"))
    print(f"signs: {len(signs)} sign pages; {n_read} with a published reading or claim ({n_any_read} outside Yajnadevam's key), "
          f"{n_tests} with project results linked")
    return pages


if __name__ == "__main__":
    s = load()
    print(f"signs: wrote {SNAP.relative_to(ROOT)} for {len(s)} signs")
