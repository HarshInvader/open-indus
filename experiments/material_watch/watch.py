"""Watch open sources for the new primary material that would reopen a closed route (docs/EXPERT_GATES.md).

Not a test. Each run saves a snapshot and lists what is new since the previous snapshot.
  python3 -I experiments/material_watch/watch.py        -> snapshots/<date>.json, reports/<date>.md

Sources (one request per second, User-Agent "open-research-site/1.0", no personal details):
- CDLI: artifacts whose transliteration contains me-luh-ha (Meluhha). A new one, or one that newly has an
  image or a seal impression, can feed the anchor route (EXPERT_GATES, anchor pairs; Gulf names).
  Also tracks the photo/impression state of the two requested tablets, P453801 and P516366,
  with YBC 5447 (P306518) as a positive control for the photo check.
- Zenodo: newest records matching Indus-script terms (new corpora, sign lists, photo sets).
"""
import json, os, sys, time, datetime, urllib.request, urllib.error, urllib.parse, glob

D = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "open-research-site/1.0", "Accept": "application/json"}
WATCHED = [453801, 516366]
ZENODO_Q = ['"Indus script"', '"Harappan" AND (seal OR inscription OR sign)', '"Indus valley" AND (seal OR inscription)']


def get(url):
    time.sleep(1)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def summarise(a):
    ins = a.get("inscription") or {}
    return dict(
        designation=a.get("designation"), museum_no=a.get("museum_no"),
        period=(a.get("period") or {}).get("period") if isinstance(a.get("period"), dict) else a.get("period"),
        provenience=(a.get("provenience") or {}).get("provenience") if isinstance(a.get("provenience"), dict) else a.get("provenience"),
        n_seals=len(a.get("seals") or []), n_impressions=len(a.get("impressions") or []),
        has_atf=bool(ins.get("atf")) if isinstance(ins, dict) else bool(ins))


def cdli_meluhha(max_pages=20):
    out = {}
    for page in range(1, max_pages + 1):
        q = urllib.parse.urlencode({"simple-value[]": "me-luh-ha", "simple-field[]": "transliteration", "limit": 100, "page": page})
        rows = get("https://cdli.earth/search?" + q)
        if not rows:
            break
        for a in rows:
            if "me-luh" in json.dumps(a.get("inscription") or {}).lower():
                out[str(a["id"])] = summarise(a)
        if len(rows) < 100:
            break
    return out


def has_photo(i):
    """CDLI photo URL; validated 2026-11-26: P306518 (YBC 5447, known photo) -> 200, P453801 -> 404."""
    time.sleep(1)
    req = urllib.request.Request(f"https://cdli.earth/dl/photo/P{i:06d}.jpg", headers=UA, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status == 200 and r.headers.get("Content-Type", "").startswith("image/")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def cdli_watched():
    out = {}
    for i in WATCHED + [306518]:  # 306518 = YBC 5447, positive control for has_photo
        try:
            r = get(f"https://cdli.earth/artifacts/{i}")
            out[str(i)] = dict(summarise(r[0] if isinstance(r, list) else r), has_photo=has_photo(i))
        except Exception as e:  # record the failure, never guess
            out[str(i)] = {"error": str(e)[:200]}
    return out


def zenodo():
    out = {}
    for q in ZENODO_Q:
        d = get("https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": q, "sort": "newest", "size": 25}))
        for h in d["hits"]["hits"]:
            m = h["metadata"]
            out[str(h["id"])] = dict(created=h["created"][:10], type=m.get("resource_type", {}).get("type"),
                                     title=m.get("title", "")[:200], doi=h.get("doi"))
    return out


def main():
    today = datetime.date.today().isoformat()
    snap = dict(date=today, cdli_meluhha=cdli_meluhha(), cdli_watched=cdli_watched(), zenodo=zenodo())
    os.makedirs(os.path.join(D, "snapshots"), exist_ok=True)
    os.makedirs(os.path.join(D, "reports"), exist_ok=True)
    prev_files = sorted(f for f in glob.glob(os.path.join(D, "snapshots", "*.json")) if not f.endswith(today + ".json"))
    prev = json.load(open(prev_files[-1])) if prev_files else None
    json.dump(snap, open(os.path.join(D, "snapshots", today + ".json"), "w"), indent=1, sort_keys=True)

    L = [f"# Material watch, {today}", ""]
    L.append(f"- CDLI artifacts with me-luh-ha: {len(snap['cdli_meluhha'])}; Zenodo records tracked: {len(snap['zenodo'])}.")
    if prev is None:
        L.append(f"- First run: baseline only, nothing to compare.")
    else:
        L.append(f"- Compared with {prev['date']}.")
        for key, label in (("cdli_meluhha", "New CDLI Meluhha artifacts"), ("zenodo", "New Zenodo records")):
            new = sorted(set(snap[key]) - set(prev[key]))
            L.append(f"- {label}: {len(new)}")
            L += [f"  - {k}: {json.dumps(snap[key][k], ensure_ascii=False)}" for k in new]
        ch = [k for k in snap["cdli_meluhha"] if k in prev["cdli_meluhha"] and snap["cdli_meluhha"][k] != prev["cdli_meluhha"][k]]
        L.append(f"- CDLI Meluhha artifacts whose record changed (seals, impressions, images): {len(ch)}")
        L += [f"  - {k}: {json.dumps(prev['cdli_meluhha'][k])} -> {json.dumps(snap['cdli_meluhha'][k])}" for k in ch]
    L.append("- Requested tablets:")
    L += [f"  - P{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in snap["cdli_watched"].items()]
    L.append("")
    L.append("A hit here is a lead, not a result: open the record, then check it against the route's gate in docs/EXPERT_GATES.md.")
    open(os.path.join(D, "reports", today + ".md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
