"""Uniformity paper, step 2: pools for seal-type references with within-site floors.

All sources are already on disk (fetch2.py documents where they come from). Outputs go to data/ (gitignored,
third-party text); counts go to sizes2.json.

  ur3meta   ORACC epsd2/admin/ur3 seal impressions (ids as uniformity_paper/step1 data/ur3pos.jsonl): the
            carrying tablet's reign (from catalogue date_of_origin) and museum-number prefix (collection).
  cdliseal  CDLI seal entries (object_type "seal (not impression)": one entry per seal, mostly composites
            reconstructed from all its impressions), Ur III and Old Babylonian, with ATF; words converted to
            ORACC form spelling (sz -> š, index digits -> subscripts) so ORACC parts of speech can be looked
            up; reign = majority reign of the CDLI tablets that list the seal in seal_id.
  obpos     ORACC epsd2/admin/oldbab seal impressions, parsed exactly as step-1 ur3pos (form + POS).
  latmeta   EDH metadata of the step-1 Latin labels (lattr ids): type of monument, type of inscription,
            material, and a stamped flag from the editors' commentary.

  .venv/bin/python -I experiments/uniformity_paper/step2/build2.py
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
ROOT = HERE.parents[2]
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
csv.field_size_limit(10**9)

UR3ZIP = ROOT / "experiments/meaning_classes_seal/raw/ur3.zip"
OBZIP = ROOT / "experiments/onomasticon/raw/epsd2-admin-oldbab.zip"
CDLI_CAT = ROOT / "experiments/short_labels/raw/cdli/cdli_cat.csv"
CDLI_ATF = ROOT / "experiments/short_labels/raw/cdli/cdliatf_unblocked.atf"
EDH = ROOT / "experiments/short_labels/raw/edh"
S1DATA = ROOT / "experiments/uniformity_paper/step1/data"


def save(name, rows):
    with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def bad_word(w):  # step-1 / benchmark rule
    parts = re.split(r"[-.]", re.sub(r"\{[^}]*\}", "", w))
    return "..." in w or any(p == "x" or re.fullmatch(r"x+", p) for p in parts if p)


# ------------------------------------------------------------------ reigns
def reign_oracc(d):
    d = (d or "").strip()
    for k, pre in (("SH", ("SH", "Šulg", "Sulg")), ("AS", ("AS", "Amar")), ("SS", ("SS", "Šū-S", "Šu-S", "Su-S")),
                   ("IS", ("IS", "Ibbi"))):
        if d.startswith(pre):
            return k
    return None


def reign_cdli(d):
    d = (d or "").strip()
    for k, pre in (("SH", ("Šulgi", "Sulgi", "SH")), ("AS", ("Amar-Suen", "Amar-Sin", "AS")),
                   ("SS", ("Šū-Suen", "Šu-Suen", "Šu-Sin", "SS")), ("IS", ("Ibbi-Suen", "Ibbi-Sin", "IS"))):
        if d.startswith(pre):
            return k
    return None


def museum_prefix(m):
    m = (m or "").strip()
    x = re.match(r"([A-Za-z]+)", m)
    return x.group(1) if x else None


# ------------------------------------------------------------------ ORACC Ur III metadata
def ur3meta():
    z = zipfile.ZipFile(UR3ZIP)
    cat = json.loads(z.read("epsd2/admin/ur3/catalogue.json"))["members"]
    rows = []
    for l in open(S1DATA / "ur3pos.jsonl", encoding="utf-8"):
        r = json.loads(l)
        c = cat.get(r["id"].split(".")[0], {})
        rows.append(dict(id=r["id"], site=r["site"], reign=reign_oracc(c.get("date_of_origin")),
                         museum=museum_prefix(c.get("museum_no"))))
    save("ur3meta", rows)
    return rows


# ------------------------------------------------------------------ ORACC Old Babylonian with POS (mirror of step-1 ur3pos)
def obpos():
    z = zipfile.ZipFile(OBZIP)
    cat = json.loads(z.read("epsd2/admin/oldbab/catalogue.json"))["members"]
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
                rows.append(dict(id=f"{pid}.s{sn}", site=prov, lines=L, group=f"{pid}.s{sn}",
                                 period=cat.get(pid, {}).get("period")))
    save("obpos", rows)
    return rows


# ------------------------------------------------------------------ CDLI seals (one entry per seal)
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def cdli_form(w):
    """CDLI ATF word -> ORACC-style form; None if damaged (x, ...) or unreadable."""
    w = re.sub(r"[#?!*\[\]⸢⸣<>]", "", w)
    w = w.replace("sz", "š").replace("SZ", "Š").replace("s,", "ṣ").replace("t,", "ṭ").replace("S,", "Ṣ")
    w = re.sub(r"(?<=[^\d\s{}\-.])(\d+)", lambda m: m.group(1).translate(SUB), w)
    w = w.strip().lower()
    if not w or bad_word(w) or re.search(r"[^\w₀-₉{}\-.()|@~'+šṣṭŋĝḫ×:/]", w):
        return None
    return w


def cdliseal():
    meta, sealreigns = {}, defaultdict(Counter)
    for x in csv.DictReader(open(CDLI_CAT, encoding="utf-8", errors="ignore")):
        ot = (x.get("object_type") or "")
        if ot.startswith("seal (not impression)"):
            per = (x.get("period") or "").split("(")[0].strip()
            if per in ("Ur III", "Old Babylonian", "Early Old Babylonian"):
                meta[int(x["id_text"])] = dict(period=per, site=(x.get("provenience") or "").split("(")[0].strip(),
                                               seal_id=(x.get("seal_id") or "").strip(),
                                               subgenre=x.get("subgenre") or "")
        elif x.get("seal_id"):
            r = reign_cdli(x.get("date_of_origin"))
            if r:
                for s in re.findall(r"S\d{6}", x["seal_id"]):
                    sealreigns[s][r] += 1
    rows, cur, lines, bad = [], None, None, False

    def flush():
        if cur in meta and lines and not bad:
            m = meta[cur]
            sid = m["seal_id"] or f"P{cur}"
            rc = sealreigns.get(m["seal_id"], Counter())
            early = rc["SH"] + rc["AS"]; late = rc["SS"] + rc["IS"]
            rg = "early" if early > late else ("late" if late > early else None)
            rows.append(dict(id=f"P{cur}", site=m["site"], period=m["period"], lines=lines, group=sid,
                             reign=rg, n_linked=sum(rc.values()), subgenre=m["subgenre"]))
    for l in open(CDLI_ATF, encoding="utf-8", errors="ignore"):
        if l.startswith("&P"):
            flush()
            mm = re.match(r"&P(\d+)", l)
            cur = int(mm.group(1)) if mm else None
            lines, bad = [], False
            continue
        if cur not in meta:
            continue
        mm = re.match(r"\s*\d+'?\.\s+(.*)$", l)
        if not mm:
            continue
        ws = []
        for w in mm.group(1).split():
            if w.startswith(("($", "$")):
                bad = True; break
            f = cdli_form(w)
            if f is None:
                bad = True; break
            ws.append(f)
        if ws:
            lines.append(ws)
    flush()
    # parts of speech from the ORACC lemmatised corpora (form -> most common POS); unknown -> "?" (counted as
    # a name by the step-1 rule, so name-free removes it)
    pos = defaultdict(Counter)
    for fn in (S1DATA / "ur3pos.jsonl", OUT / "obpos.jsonl"):
        for l in open(fn, encoding="utf-8"):
            for ln in json.loads(l)["lines"]:
                for w, p in ln:
                    pos[w][p] += 1
    known = tot = 0
    for r in rows:
        L = []
        for ln in r["lines"]:
            cur_l = []
            for w in ln:
                p = pos[w].most_common(1)[0][0] if w in pos else "?"
                known += w in pos; tot += 1
                cur_l.append([w, p])
            L.append(cur_l)
        r["lines"] = L
    save("cdliseal", rows)
    return rows, dict(pos_coverage=known / max(tot, 1))


# ------------------------------------------------------------------ Latin metadata
STAMP = re.compile(r"gestempelt|stempel|stamp|signacul", re.I)


def latmeta():
    ids = {json.loads(l)["id"] for l in open(S1DATA / "lattr.jsonl", encoding="utf-8")}
    rows = []
    for fn in sorted(glob.glob(str(EDH / "p*.json"))):
        try:
            d = json.load(open(fn, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            if it["id"] in ids:
                rows.append(dict(id=it["id"], tm=(it.get("type_of_monument") or "").rstrip("?"),
                                 ti=(it.get("type_of_inscription") or "").rstrip("?"),
                                 material=it.get("material"),
                                 stamped=bool(STAMP.search((it.get("commentary") or "")))))
    save("latmeta", rows)
    return rows


if __name__ == "__main__":
    S = {}
    R = ur3meta()
    S["ur3meta"] = {s: dict(reign=dict(Counter(r["reign"] for r in R if r["site"] == s)),
                            museum=dict(Counter(r["museum"] for r in R if r["site"] == s).most_common(8)))
                    for s in ("Umma", "Girsu")}
    R = obpos()
    S["obpos"] = dict(rows=len(R), sites=dict(Counter(r["site"] for r in R).most_common(12)))
    R, info = cdliseal()
    S["cdliseal"] = dict(info, rows=len(R), sites=dict(Counter((r["period"], r["site"]) for r in R).most_common(14)),
                         reign_ur3=dict(Counter((r["site"], r["reign"]) for r in R if r["period"] == "Ur III" and r["site"] in ("Umma", "Girsu"))))
    S["cdliseal"]["sites"] = {f"{k[0]}|{k[1]}": v for k, v in S["cdliseal"]["sites"].items()}
    S["cdliseal"]["reign_ur3"] = {f"{k[0]}|{k[1]}": v for k, v in S["cdliseal"]["reign_ur3"].items()}
    R = latmeta()
    S["latmeta"] = dict(rows=len(R), stamped=sum(r["stamped"] for r in R))
    json.dump(S, open(HERE / "sizes2.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(S, ensure_ascii=False, indent=1))
