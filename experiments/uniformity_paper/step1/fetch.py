"""Re-fetch the third-party inputs of step 1 (not needed if the copies under sources/ and experiments/*/raw exist).

Linear B: DAMOS (Database of Mycenaean at Oslo, https://damos.hf.uio.no, CC BY-NC-SA 4.0), public JSON endpoint
/ajaxitem/{id}/, heading + transliteration only. Raw text is NOT committed (licence is non-commercial share-alike);
it goes to sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl, which is gitignored.
Committed instead: sizes.json (derived counts) and the step-1 results.

Polite: 2 parallel requests, resumable, User-Agent "open-research-site/1.0".
Run: .venv/bin/python -I experiments/uniformity_paper/step1/fetch.py [max_id]
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
UA = {"User-Agent": "open-research-site/1.0"}


def get(i):
    url = f"https://damos.hf.uio.no/ajaxitem/{i}/"
    err = None
    for _ in range(3):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
            if raw.lstrip().startswith(b"<"):
                return i, None
            it = json.loads(raw).get("item") or {}
            if not it:
                return i, None
            return i, {"id": i, "heading": it.get("heading"), "content": it.get("content"),
                       "collectionid": it.get("collectionid")}
        except Exception as e:  # network errors: retry, then record
            err = e; time.sleep(2)
    return i, {"id": i, "error": str(err)}


def main():
    hi = int(sys.argv[1]) if len(sys.argv) > 1 else 7000
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if OUT.exists():
        for l in open(OUT):
            r = json.loads(l)
            if "error" not in r:
                done.add(r["id"])
    todo = [i for i in range(1, hi + 1) if i not in done]
    with open(OUT, "a") as f, ThreadPoolExecutor(2) as ex:
        for i, r in ex.map(get, todo):
            if r:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
