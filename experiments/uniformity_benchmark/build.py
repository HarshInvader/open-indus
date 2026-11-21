"""Uniformity benchmark: build reference pools (prereg docs/prereg/uniformity_benchmark.md).

Run: board/run.sh .venv/bin/python -I experiments/uniformity_benchmark/build.py
Writes data/<pool>.jsonl with {"id", "site", "lines": [[tok..]..], "group"} and prints SIZES ONLY
(texts per site, length mix). No classifier is run here. Inputs are parsed as data, never executed.

Pools
  ur3      ORACC epsd2/admin/ur3 (experiments/meaning_classes_seal/raw/ur3.zip): seal legends ("seal N"
           lines) on tablets; site = ORACC catalogue provenience of the tablet; unit = word form.
  pc       experiments/protocuneiform/pc_lines.json: one line (case) = one text; period from the file;
           provenience from cdli_cat.csv; unit = sign; numeral "k(Nxx)" -> "Nxx".
  lat      EDH (experiments/short_labels/raw/edh): label genre as in short_labels (owner/artist,
           label, identification inscription, or instrumentum monuments); site = modern country
           mapped to a Roman province; unit = word of the diplomatic text; lines split on "/".
"""
import csv
import glob
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)


def save(name, rows):
    with open(OUT / f"{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def bad_word(w):
    parts = re.split(r"[-.]", re.sub(r"\{[^}]*\}", "", w))
    return "..." in w or any(p == "x" or re.fullmatch(r"x+", p) for p in parts if p)


# ------------------------------------------------------------------ Ur III (ORACC)
def ur3():
    z = zipfile.ZipFile(ROOT / "experiments/meaning_classes_seal/raw/ur3.zip")
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
        seals = defaultdict(lambda: defaultdict(list))   # seal no -> line label -> forms
        broken = set()
        cur = [None]

        def walk(x):
            if isinstance(x, dict):
                if x.get("node") == "d" and x.get("type") == "line-start":
                    cur[0] = x.get("label", "")
                elif x.get("node") == "l" and cur[0]:
                    m = re.match(r"seal (\d+)\s*(.*)$", cur[0])
                    if m:
                        form = (x.get("f", {}) or {}).get("form", "") or x.get("frag", "")
                        form = form.strip().lower()
                        if not form or bad_word(form):
                            broken.add(m.group(1))
                        else:
                            seals[m.group(1)][m.group(2)].append(form)
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
    save("ur3", rows)
    return rows


# ------------------------------------------------------------------ proto-cuneiform
def pc():
    prov = {}
    with open(ROOT / "experiments/protocuneiform/raw/cdli_atf/cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            i = (r.get("id_text") or "").strip()
            if i.isdigit():
                prov[int(i)] = (r.get("provenience") or "").split("(")[0].strip()
    rows = []
    for l in json.load(open(ROOT / "experiments/protocuneiform/pc_lines.json")):
        per = l["period"]
        ph = "Uruk IV" if per.startswith("Uruk IV") else ("Uruk III" if per.startswith("Uruk III") else None)
        if ph is None:
            continue
        toks = []
        bad = False
        for t in l["tokens"]:
            if t in (",", ""):
                continue
            if re.search(r"(^|[^A-Za-z])X([^A-Za-z]|$)|\.\.\.|\[|\]", t) or t.lower() == "x":
                bad = True; break
            m = re.fullmatch(r"\d+\((N\d+[^)]*)\)", t)
            toks.append(m.group(1) if m else t)
        if bad or not toks:
            continue
        rows.append(dict(id=f"{l['pid']}.{l['surface']}.{l['line']}.{l['k']}", site=ph,
                         prov=prov.get(int(l["pid"]), ""), lines=[toks], group=str(l["pid"])))
    save("pc", rows)
    return rows


# ------------------------------------------------------------------ Latin (EDH)
LABEL_TYPES = ("owner/artist inscription", "label", "identification inscription")
LABEL_MON = ("instrumentum domesticum", "tile", "tessera", "signaculum", "lamp", "amphora", "vessel")


def lat():
    rows = []
    for fn in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        try:
            d = json.load(open(fn, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            if it.get("language") != "L":
                continue
            txt = it.get("diplomatic_text") or ""
            if not txt or re.search(r"[\[\]]|\+|---|\?", txt):
                continue
            ti = (it.get("type_of_inscription") or "").rstrip("?")
            tm = (it.get("type_of_monument") or "").rstrip("?")
            genre = "label" if (ti in LABEL_TYPES or tm in LABEL_MON) else "other"
            L = []
            for ln in txt.split("/"):
                ws = [re.sub(r"[^A-Z]", "", w.upper()) for w in re.split(r"[\s·•]+", ln)]
                ws = [w for w in ws if w]
                if ws:
                    L.append(ws)
            if L:
                rows.append(dict(id=it["id"], site=it.get("country", ""), region=it.get("modern_region") or "", genre=genre, ti=ti, lines=L, group=it["id"]))
    save("lat", rows)
    return rows


def describe(name, rows, key="site", top=10):
    c = Counter(r[key] for r in rows)
    print(name, "texts", len(rows), "by", key, c.most_common(top))
    for s, _ in c.most_common(4):
        ds = set(" ".join(w for l in r["lines"] for w in l) for r in rows if r[key] == s)
        lm = Counter(min(sum(len(l) for l in r["lines"]), 9) for r in rows if r[key] == s)
        print("   ", s, "distinct", len(ds), "len mix", sorted(lm.items()))


if __name__ == "__main__":
    which = sys.argv[1:] or ["ur3", "pc", "lat"]
    if "pc" in which:
        R = pc(); describe("pc", R)
        describe("pc Uruk-provenience", [r for r in R if r["prov"].startswith("Uruk")])
        print("   pc provenience", Counter(r["prov"] for r in R).most_common(5))
    if "lat" in which:
        R = lat(); describe("lat label", [r for r in R if r["genre"] == "label"], top=15)
        describe("lat other", [r for r in R if r["genre"] == "other"], top=15)
    if "ur3" in which:
        R = ur3(); describe("ur3", R)
