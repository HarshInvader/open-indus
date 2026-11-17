"""Fetch lemma lists from Wiktionary categories (titles only) into experiments/language/ext/wikt/.
Run: .venv/bin/python experiments/language/fetch_vocab.py
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "ext" / "wikt"
OUT.mkdir(parents=True, exist_ok=True)
CATS = ["Burushaski_lemmas", "Proto-Dravidian_lemmas", "Old_Tamil_lemmas", "Santali_lemmas",
        "Proto-Austroasiatic_lemmas", "Sumerian_lemmas", "Elamite_lemmas", "Tamil_lemmas",
        "Proto-Munda_lemmas", "Burushaski_nouns", "Proto-Dravidian_nouns"]


def members(cat):
    out, cont = [], None
    while True:
        q = {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat,
             "cmlimit": "500", "format": "json"}
        if cont:
            q["cmcontinue"] = cont
        req = urllib.request.Request("https://en.wiktionary.org/w/api.php?" + urllib.parse.urlencode(q),
                                     headers={"User-Agent": "indus-research/0.1 (academic)"})
        for attempt in range(8):
            try:
                d = json.load(urllib.request.urlopen(req, timeout=60)); break
            except Exception as e:  # noqa
                time.sleep(30 * (attempt + 1))
        else:
            raise RuntimeError("rate limited")
        out += [m["title"] for m in d["query"]["categorymembers"]]
        cont = d.get("continue", {}).get("cmcontinue")
        if not cont:
            return out
        time.sleep(3)


for c in CATS:
    try:
        m = members(c)
    except Exception as e:  # noqa
        print(c, "ERR", e); continue
    time.sleep(5)
    (OUT / f"{c}.txt").write_text("\n".join(m))
    print(c, len(m), m[:5])
