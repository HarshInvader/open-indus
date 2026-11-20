"""Harvest Yale Peabody (Yale Babylonian Collection) records with images, via the open Peabody API.

Rate: one request per second, single connection, UA "open-research-site/1.0". Peabody robots.txt disallows only
/view/results/; the LUX host (lux.collections.yale.edu) is behind a bot challenge and is NOT used.
Images are CC0 (IIIF manifests state CC0). Records and images stay in raw/ (gitignored).

Usage (repo root):
  .venv/bin/python -I experiments/stamp_detector/harvest.py records NAME "TEXT" [MAX]   -> raw/records_NAME.jsonl
  .venv/bin/python -I experiments/stamp_detector/harvest.py images NAME [WIDTH]         -> raw/img/<nat>.jpg
Resumable: already fetched ids/images are skipped.
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"; RAW.mkdir(exist_ok=True)
UA = {"User-Agent": "open-research-site/1.0"}
API = "https://peabody.collections.yale.edu"
SET = API + "/data/set/a996e468-616e-47b3-966a-ced654bc53a6"  # Babylonian Collection, Yale Peabody Museum
_last = [0.0]


def get(url, binary=False, tries=3):
    for k in range(tries):
        wait = 1.0 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except Exception as e:  # noqa: BLE001
            print("retry", k, url[:120], e, flush=True)
            time.sleep(10 * (k + 1))
    return None


def search_ids(text, maxn):
    q = {"AND": [{"memberOf": {"id": SET}}, {"hasDigitalImage": 1}] + ([{"text": text}] if text else [])}
    base = f"{API}/api/search/item?q={urllib.parse.quote(json.dumps(q))}&pageLength=50&page="
    ids, page = [], 1
    while len(ids) < maxn:
        d = get(base + str(page), tries=6)
        if d is None:  # transient 504s: log and move to the next page
            print("page failed, skipped", page, flush=True); page += 1
            if page > 1000:
                break
            continue
        items = [x["id"] for x in d.get("orderedItems", [])]
        ids += items
        if not items or not d.get("next"):
            break
        page += 1
    return ids[:maxn]


def slim(rec):
    out = dict(id=rec["id"], label=rec.get("_label", ""))
    for x in rec.get("identified_by", []):
        labs = [c.get("_label") for c in x.get("classified_as", [])]
        if "YPM External Catalog Number" in labs:
            out["ypm"] = x.get("content")
        elif "Primary Name" in labs:
            out["name"] = x.get("content")
        elif x.get("type") == "Identifier":
            out.setdefault("other_ids", []).append(x.get("content"))
    nat = []
    for rep in rec.get("representation", []):
        for d in rep.get("digitally_shown_by", []):
            for a in d.get("access_point", []):
                if "/thumbnail/ypm/nat/" in a["id"]:
                    nat.append(a["id"].rsplit("/", 1)[1])
    out["nat"] = nat
    out["texts"] = [x.get("content", "")[:600] for x in rec.get("referred_to_by", []) if x.get("content")]
    return out


def records(name, text, maxn=100000):
    path = RAW / f"records_{name}.jsonl"
    done = {json.loads(l)["id"] for l in path.read_text().splitlines()} if path.exists() else set()
    ids = search_ids(text, maxn)
    print(name, "ids", len(ids), "already", len(done), flush=True)
    with path.open("a") as f:
        for i, oid in enumerate(ids):
            if oid in done:
                continue
            rec = get(oid)
            if rec:
                f.write(json.dumps(slim(rec)) + "\n"); f.flush()
            if i % 200 == 0:
                print(name, i, flush=True)


def images(name, width=1600):
    img = RAW / "img"; img.mkdir(exist_ok=True)
    recs = [json.loads(l) for l in (RAW / f"records_{name}.jsonl").read_text().splitlines()]
    for i, r in enumerate(recs):
        for nat in r["nat"]:
            dst = img / f"{nat}.jpg"
            if dst.exists():
                continue
            man = get(f"https://manifests.collections.yale.edu/ypm/nat/{nat}")
            if not man or not man.get("items"):
                continue
            if "publicdomain/zero" not in man.get("rights", ""):
                print("not CC0, skipped", nat, man.get("rights")); continue
            svc = man["items"][0]["items"][0]["items"][0]["body"]["service"][0]["@id"]
            data = get(f"{svc}/full/{width},/0/default.jpg", binary=True)
            if data:
                dst.write_bytes(data)
        if i % 100 == 0:
            print(name, "img", i, len(recs), flush=True)


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "records":
        records(name, sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 100000)
    else:
        images(name, int(sys.argv[3]) if len(sys.argv) > 3 else 1600)
