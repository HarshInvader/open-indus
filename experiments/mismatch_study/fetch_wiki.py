"""Fetch Wikipedia article intros for the mismatch study's training and confirmation languages.
Same method as experiments/decipherability/fetch_wiki.py; generic User-Agent.
Never fetches the sealed held-out families (tr, az, cs, sk, nl, de).
Run: .venv/bin/python -I experiments/mismatch_study/fetch_wiki.py es pt ro hu te id ms
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "decipherability" / "raw"
HELD_OUT = {"tr", "az", "cs", "sk", "nl", "de"}


def fetch(lang, rounds=60):
    assert lang not in HELD_OUT, f"{lang} is a sealed held-out language"
    out = RAW / f"wiki_{lang}.txt"
    if out.exists():
        print(lang, "exists"); return
    seen, texts = set(), []
    for r in range(rounds):
        q = dict(action="query", generator="random", grnnamespace=0, grnlimit=20, prop="extracts",
                 exintro=1, explaintext=1, exlimit=20, format="json")
        url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": "open-research-site/1.0"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print(lang, r, e); time.sleep(3); continue
        for p in d.get("query", {}).get("pages", {}).values():
            if p["pageid"] in seen:
                continue
            seen.add(p["pageid"]); t = p.get("extract", "").strip()
            if len(t) > 80:
                texts.append(t)
        time.sleep(0.5)
    out.write_text("\n".join(texts))
    print(lang, len(texts), sum(map(len, texts)), flush=True)


if __name__ == "__main__":
    for l in sys.argv[1:]:
        fetch(l)
