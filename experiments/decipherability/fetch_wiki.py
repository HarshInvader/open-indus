"""Fetch plain-text intros of random Wikipedia articles for prose / lexicon material.
Run once: .venv/bin/python experiments/decipherability/fetch_wiki.py
Writes experiments/decipherability/raw/wiki_<lang>.txt
"""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
RAW.mkdir(exist_ok=True)


def fetch(lang, rounds):
    out = RAW / f"wiki_{lang}.txt"
    seen, texts = set(), []
    for r in range(rounds):
        q = dict(action="query", generator="random", grnnamespace=0, grnlimit=20, prop="extracts",
                 exintro=1, explaintext=1, exlimit=20, format="json")
        url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": "indus-decipher-research/0.1 (offline study)"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print(lang, r, e); time.sleep(2); continue
        for p in d.get("query", {}).get("pages", {}).values():
            if p["pageid"] in seen: continue
            seen.add(p["pageid"]); t = p.get("extract", "").strip()
            if len(t) > 80: texts.append(t)
        time.sleep(0.3)
    out.write_text("\n".join(texts))
    print(lang, len(texts), sum(map(len, texts)))


if __name__ == "__main__":
    langs = sys.argv[1:] or ["ta", "sa", "fi", "et", "it", "ml"]
    for l in langs:
        fetch(l, 60)
