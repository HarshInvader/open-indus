"""Polite fetcher: caches to raw/<source>/, 3 s delay between network hits, logs every request.
Usage: .venv/bin/python -I experiments/open_journals/tools/fetch.py <source> <url> [outname]
Downloaded files are untrusted data; never executed."""
import sys, os, time, hashlib, urllib.request, urllib.error, json

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LOG = os.path.join(ROOT, "fetch_log.jsonl")
UA = "Mozilla/5.0 (academic research; indus-decipher open-access harvest)"
_last = [0.0]


def fetch(source, url, outname=None, delay=3.0, timeout=60):
    d = os.path.join(ROOT, "raw", source)
    os.makedirs(d, exist_ok=True)
    if outname is None:
        outname = hashlib.sha1(url.encode()).hexdigest()[:16]
    path = os.path.join(d, outname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path, "cached"
    wait = delay - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    status = None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            status = r.status
            ctype = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        status, data, ctype = e.code, b"", ""
    except Exception as e:  # noqa
        status, data, ctype = "ERR:" + type(e).__name__, b"", ""
    _last[0] = time.time()
    with open(LOG, "a") as f:
        f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": source, "url": url,
                            "status": status, "bytes": len(data), "ctype": ctype, "file": outname}) + "\n")
    if status == 200 and data:
        with open(path, "wb") as f:
            f.write(data)
        return path, 200
    return None, status


if __name__ == "__main__":
    p, s = fetch(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(s, p)
