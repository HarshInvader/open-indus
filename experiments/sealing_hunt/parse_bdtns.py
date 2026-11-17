"""Parse saved BDTNS line-search pages (substring 'me-luh') and keep only real Meluhha lines.
Run: .venv/bin/python -I experiments/sealing_hunt/parse_bdtns.py
Input (untrusted): experiments/sealing_hunt/raw/bdtns/L_*.html
Output: experiments/sealing_hunt/bdtns_meluhha.csv
"""
import csv, glob, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for fn in sorted(glob.glob(os.path.join(HERE, "raw/bdtns/L_*.html"))):
    t = open(fn, "rb").read().decode("utf-8", errors="replace")
    for chunk in t.split('<tr align="left" valign="middle"')[1:]:
        def clean(s):
            s = re.sub(r"<sup>(.*?)</sup>", r"{\1}", s)
            s = re.sub(r"<sub>(.*?)</sub>", r"\1", s)
            s = re.sub(r"<[^>]+>", " ", s)
            return re.sub(r"\s+", " ", html.unescape(s)).strip()
        def grab(tag, nxt):
            m = re.search(r"<!--\s*" + tag + r".*?-->(.*?)<!--\s*" + nxt, chunk, re.S)
            return m.group(1) if m else ""
        line = clean(grab("Linea", "Transliteration"))
        tr = clean(grab("Transliteration", "Publication"))
        pubraw = grab("Publication", "Procedencia")
        pub = clean(re.sub(r'<div id="abrev.*', "", pubraw, flags=re.S))
        alt = clean(re.search(r'class="miclase">(.*?)</div>', pubraw, re.S).group(1)) if 'miclase' in pubraw else ""
        prov = clean(grab("Procedencia", "Datacion"))
        date = clean(grab("Datacion", "Sello"))
        seal = clean(grab("Sello", " Num Museo"))
        mus = clean(grab(" Num Museo", "Bibliograf"))
        cdli = re.findall(r"CDLI (P\d{6})", alt)
        ref = re.search(r"miReferencia=(\d+)", chunk)
        rows.append(dict(page=os.path.basename(fn), ref=ref.group(1) if ref else "", line=line, translit=tr,
                         publication=pub, cdli=cdli[0] if cdli else "", provenience=prov, date=date,
                         seal=seal, museum_no=mus, also=alt[:300]))

mel = [r for r in rows if re.search(r"me-luh|me-lu-ha", r["translit"], re.I)]
print("rows", len(rows), "meluhha rows", len(mel))
with open(os.path.join(HERE, "bdtns_meluhha.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(mel)
from collections import Counter
print(Counter(r["seal"] for r in mel))
for r in mel:
    if r["seal"].startswith("S"):
        print(r["cdli"], r["publication"], r["provenience"], r["date"], r["seal"], r["museum_no"], "|", r["translit"])
