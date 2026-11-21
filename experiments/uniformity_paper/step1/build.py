"""Uniformity paper, step 1: build the extra reference pools (prereg docs/prereg/uniformity_paper_step1.md).

Writes data/*.jsonl (gitignored: they hold third-party text) and sizes.json (derived counts, committed).
Prints SIZES ONLY. No classifier is run here. Inputs are parsed as data, never executed.

  lb        Linear B, DAMOS (Database of Mycenaean at Oslo, CC BY-NC-SA 4.0), already on disk at
            sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl (fetch.py re-fetches).
            Site = heading prefix KN (Knossos) / PY (Pylos). Unit = one tablet line; group = tablet.
            Tokens: syllabic words as written, ideograms / measure signs as written, every numeral -> "NUM".
            Each word token carries a class: w (syllabic word), i (ideogram or measure sign), n (numeral),
            and a name tag: name (in the Linear B proper-name lists), common (in the common-word list), or unk.
  ur3pos    Ur III seal legends exactly as uniformity_benchmark/build.py::ur3, but each word keeps its ORACC
            part of speech (pos). Checked word-for-word against uniformity_benchmark/data/ur3.jsonl.
  lattr     Latin labels (EDH) re-tokenised from the edited transcription, where editors capitalise proper
            nouns. Each token keeps its diplomatic-style form (abbreviation, upper case, expansion dropped)
            and a flag proper (capitalised and never written lower-case anywhere in EDH).
Run: board/run.sh .venv/bin/python -I experiments/uniformity_paper/step1/build.py
"""
import csv
import glob
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
DAMOS = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
WIKT = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/linearb_words.json"
COG = ROOT / "experiments/cognate_decipher/ext/neurodecipher"
EDH = ROOT / "experiments/short_labels/raw/edh"
UR3ZIP = ROOT / "experiments/meaning_classes_seal/raw/ur3.zip"
csv.field_size_limit(10**9)


def save(name, rows):
    with open(OUT / f"{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ Linear B name lists
def _lb_translit(word):
    out = []
    for ch in word:
        n = unicodedata.name(ch, "")
        if not n.startswith("LINEAR B SYLLABLE"):
            return None
        out.append(n.split()[-1].lower())
    return "-".join(out)


def lb_lists():
    """names: NeuroDecipher (Luo et al. 2019) linear_b-greek.names.cog rows with a Greek form (proper names)
    + Wiktionary 'Mycenaean Greek proper nouns'. common: linear_b-greek.cog rows with a Greek cognate that are
    NOT in the names file (common words). Spellings normalised to DAMOS style (a-b-c, lower case)."""
    A = [l.rstrip("\n").split("\t") for l in open(COG / "linear_b-greek.cog", encoding="utf-8")][1:]
    B = [l.rstrip("\n").split("\t") for l in open(COG / "linear_b-greek.names.cog", encoding="utf-8")][1:]
    names, common = set(), set()
    for a, b in zip(A, B):
        w = _lb_translit(a[0])
        if not w:
            continue
        if b[1] != "_":
            names.add(w)
        elif a[1] != "_":
            common.add(w)
    wk = json.load(open(WIKT))
    for w in wk.get("Category:Mycenaean_Greek_proper_nouns", []):
        names.add(w.lower())
    common -= names
    return names, common


LB_EDIT = re.compile(r"^(sup|inf|lat|mut|vac|vacat|vacant|vest|v|r|fr|frr|deest|supra|infra|sigillum|angustum|"
                     r"prior|pars|reliqua|erasa|in|rasura|qs|dex|sin|mutila|perierunt|vestigia|x|nihil)\.?$")
DOT = "̣"


def lb_token(tok):
    """-> (token, class) or None (editorial) or 'BAD' (damaged / uncertain)."""
    tok = tok.strip("'\"")
    if not tok or tok in ("/", "//", "↓", "→", "←", "↑", "α", "β", "γ", "δ", "ε"):
        return None
    if LB_EDIT.match(tok.lower()):
        return None
    tok = tok.replace(DOT, "")                      # under-dot = sign read with some doubt: keep the reading
    if any(c in tok for c in "[]⟦⟧?•") or tok.lower() in ("x", "*x"):
        return "BAD"
    if tok.isdigit():
        return ("NUM", "n")
    if "-" in tok or re.fullmatch(r"[a-z][a-z0-9]*", tok):
        part = r"(\*\d+|[a-z]{0,2}[aeiou][23]?)"          # one syllabic sign: *NN, V, CV, CCV, a2, ra3
        if re.fullmatch(part + "(-" + part + ")*", tok):
            return (tok, "w")
        return "BAD"
    if re.fullmatch(r"[A-Z*][A-Za-z0-9*+:;^±]*", tok):
        return (tok, "i")
    return "BAD"


def lb_name_tag(w, names, common):
    base = re.sub(r"-(qe|de|pi|ja-de)$", "", w)
    if w in names or base in names:
        return "name"
    if w in common or base in common:
        return "common"
    return "unk"


def lb():
    names, common = lb_lists()
    rows, drop = [], Counter()
    for l in open(DAMOS, encoding="utf-8"):
        d = json.loads(l)
        h, c = d.get("heading"), d.get("content")
        if not h or not c:
            continue
        site = h.split()[0]
        if site not in ("KN", "PY"):
            continue
        m = re.match(r"(KN|PY)\s+([A-Z][a-z]?)", h)
        series = m.group(2) if m else "?"
        for k, ln in enumerate(c.split("\n")):
            ln = re.sub(r"^\s*\.[0-9A-Za-z]+\s*", " ", ln)       # line label .1 .A .a
            raw = [t for t in re.split(r"[\s,]+", ln) if t]
            if not raw:
                continue
            toks, bad = [], False
            for t in raw:
                r = lb_token(t)
                if r == "BAD":
                    bad = True; break
                if r:
                    toks.append(r)
            if bad:
                drop["damaged"] += 1; continue
            if not toks:
                continue
            words = [[w, cl, lb_name_tag(w, names, common) if cl == "w" else cl] for w, cl in toks]
            rows.append(dict(id=f"{d['id']}.{k}", site={"KN": "Knossos", "PY": "Pylos"}[site], series=series,
                             heading=h, toks=words, group=str(d["id"])))
    save("lb", rows)
    return rows, dict(names=len(names), common=len(common), dropped_lines=dict(drop))


# ------------------------------------------------------------------ Ur III with POS (mirror of benchmark build.ur3)
def bad_word(w):
    parts = re.split(r"[-.]", re.sub(r"\{[^}]*\}", "", w))
    return "..." in w or any(p == "x" or re.fullmatch(r"x+", p) for p in parts if p)


def ur3pos():
    z = zipfile.ZipFile(UR3ZIP)
    cat = json.loads(z.read("epsd2/admin/ur3/catalogue.json"))["members"]
    rows = []
    for nm in z.namelist():
        if "/corpusjson/" not in nm or not nm.endswith(".json"):
            continue
        s = z.read(nm)
        if b"seal" not in s:
            continue
        d = json.loads(s)
        pid = d.get("textid", "")
        prov = (cat.get(pid, {}).get("provenience") or "").strip()
        seals = defaultdict(lambda: defaultdict(list))
        broken = set()
        cur = [None]

        def walk(x):
            if isinstance(x, dict):
                if x.get("node") == "d" and x.get("type") == "line-start":
                    cur[0] = x.get("label", "")
                elif x.get("node") == "l" and cur[0]:
                    m = re.match(r"seal (\d+)\s*(.*)$", cur[0])
                    if m:
                        f = x.get("f", {}) or {}
                        form = (f.get("form", "") or x.get("frag", "")).strip().lower()
                        if not form or bad_word(form):
                            broken.add(m.group(1))
                        else:
                            seals[m.group(1)][m.group(2)].append([form, f.get("pos") or "?"])
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d.get("cdl", []))
        for sn, lines in seals.items():
            if sn in broken:
                continue
            L = [ws for ws in lines.values() if ws]
            if L:
                rows.append(dict(id=f"{pid}.s{sn}", site=prov, lines=L, group=f"{pid}.s{sn}"))
    # check against the benchmark's pool, word for word
    ref = {}
    for l in open(ROOT / "experiments/uniformity_benchmark/data/ur3.jsonl"):
        r = json.loads(l); ref[r["id"]] = r["lines"]
    same = sum(1 for r in rows if ref.get(r["id"]) == [[w for w, _ in l] for l in r["lines"]])
    save("ur3pos", rows)
    return rows, dict(rows=len(rows), identical_to_benchmark=same, benchmark_rows=len(ref))


# ------------------------------------------------------------------ Latin from the transcription
def _tr_tokens(txt):
    """Edited transcription -> lines of (expanded, abbreviated) tokens; None if it cannot be read cleanly."""
    t = txt.replace("(!)", "").replace("(?)", "")
    t = re.sub(r"\{[^}]*\}", "", t)
    if re.search(r"[\[\]<>]|&lt;|&gt;|---|\+|\?", t):
        return None
    L = []
    for ln in re.split(r"/+", t):
        cur = []
        for w in re.split(r"[\s·•]+", ln):
            if not w:
                continue
            exp = re.sub(r"[^A-Za-z]", "", w.replace("(", "").replace(")", ""))
            ab = re.sub(r"[^A-Za-z]", "", re.sub(r"\([^)]*\)", "", w)).upper().replace("U", "V").replace("J", "I")
            if exp and ab:
                cur.append((exp, ab, "(" in w))
        if cur:
            L.append(cur)
    return L


def lattr():
    keep = {}
    for l in open(ROOT / "experiments/uniformity_benchmark/data/lat.jsonl"):
        r = json.loads(l)
        if r["genre"] == "label" and r["site"] in ("United Kingdom", "Germany"):
            keep[r["id"]] = r
    lower_seen = set()
    trans = {}
    for fn in sorted(glob.glob(str(EDH / "p*.json"))):
        try:
            d = json.load(open(fn, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            if it.get("language") != "L":
                continue
            L = _tr_tokens(it.get("transcription") or "")
            if L is None:
                continue
            for ln in L:
                for exp, _, _ in ln:
                    if exp[0].islower():
                        lower_seen.add(exp.lower())
            if it["id"] in keep:
                trans[it["id"]] = L
    rows, miss = [], 0
    for i, r in keep.items():
        L = trans.get(i)
        if not L:
            miss += 1; continue
        out = []
        for ln in L:
            cur = []
            for exp, ab, had_exp in ln:
                numeral = (not had_exp) and re.fullmatch(r"[IVXLCDM]+", exp) is not None
                proper = (exp[0].isupper() and exp.lower() not in lower_seen and not numeral)
                cur.append([ab, "proper" if proper else ("num" if numeral else "common")])
            out.append(cur)
        rows.append(dict(id=i, site={"United Kingdom": "Britannia", "Germany": "Germania"}[r["site"]],
                         region=r.get("region", ""), lines=out, group=i, diplomatic=r["lines"]))
    agree = sum(1 for r in rows if [[w for w, _ in l] for l in r["lines"]] == r["diplomatic"])
    save("lattr", rows)
    return rows, dict(rows=len(rows), no_clean_transcription=miss, tokens_equal_diplomatic=agree,
                      lower_case_words_seen=len(lower_seen))


if __name__ == "__main__":
    which = sys.argv[1:] or ["lb", "ur3pos", "lattr"]
    S = json.load(open(HERE / "sizes.json")) if (HERE / "sizes.json").exists() else {}
    if "lb" in which:
        R, info = lb()
        c = Counter(r["site"] for r in R)
        tags = Counter((r["site"], t[2]) for r in R for t in r["toks"])
        ser = {s: Counter(r["series"][0] for r in R if r["site"] == s).most_common() for s in c}
        S["lb"] = dict(info, lines=dict(c), tablets={s: len({r["group"] for r in R if r["site"] == s}) for s in c},
                       token_tags={f"{a}|{b}": n for (a, b), n in sorted(tags.items())}, series_letter=ser)
        print("lb", json.dumps(S["lb"], ensure_ascii=False))
    if "ur3pos" in which:
        R, info = ur3pos()
        pos = Counter(p for r in R for l in r["lines"] for _, p in l)
        S["ur3pos"] = dict(info, pos=dict(pos.most_common()))
        print("ur3pos", json.dumps(S["ur3pos"], ensure_ascii=False))
    if "lattr" in which:
        R, info = lattr()
        fl = Counter((r["site"], t[1]) for r in R for l in r["lines"] for t in l)
        S["lattr"] = dict(info, sites=dict(Counter(r["site"] for r in R)),
                          token_flags={f"{a}|{b}": n for (a, b), n in sorted(fl.items())})
        print("lattr", json.dumps(S["lattr"], ensure_ascii=False))
    json.dump(S, open(HERE / "sizes.json", "w"), indent=1, ensure_ascii=False)
