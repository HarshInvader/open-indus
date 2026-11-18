"""Reproducible, serial public-source fetcher. Never follows redirects without pacing."""
import argparse, datetime, email.message, hashlib, json, pathlib, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
LOG = ROOT / 'evidence' / 'requests.jsonl'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def fetch(url, kind='raw', name=None):
    opener = urllib.request.build_opener(NoRedirect)
    original = url
    for attempt in range(8):
        prior = ROOT / 'evidence' / 'last_request.txt'
        last = float(prior.read_text()) if prior.exists() else 0
        time.sleep(max(0, 2.2 - (time.time() - last)))
        started = time.time()
        prior.write_text(str(started))
        record = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'url': url, 'original_url': original}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; academic source collection; one request per 2.2 seconds)'})
            response = opener.open(req, timeout=45)
            data = response.read()
            record.update(status=response.status, content_type=response.headers.get('Content-Type'), bytes=len(data), headers={k:v for k,v in response.headers.items() if k.lower() != 'set-cookie'})
            disposition = email.message.Message()
            disposition['content-disposition'] = response.headers.get('Content-Disposition', '')
            filename = name or disposition.get_filename() or urllib.parse.unquote(pathlib.PurePosixPath(urllib.parse.urlsplit(url).path).name) or 'index.html'
            filename = pathlib.Path(filename).name
            if kind == 'evidence' and not pathlib.Path(filename).suffix:
                filename += '.html'
            path = ROOT / kind / filename
            if path.exists() and path.read_bytes() != data:
                path = path.parent / hashlib.sha256(original.encode()).hexdigest()[:8] / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            record.update(file=str(path.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest())
        except urllib.error.HTTPError as e:
            data = e.read()
            record.update(status=e.code, bytes=len(data), content_type=e.headers.get('Content-Type'), location=e.headers.get('Location'))
            err = ROOT / 'evidence' / ('http_' + hashlib.sha256(url.encode()).hexdigest()[:12] + '.html')
            err.write_bytes(data)
            record['response_file'] = str(err.relative_to(ROOT))
        except Exception as e:
            record['error'] = str(e)
        with LOG.open('a') as f:
            f.write(json.dumps(record) + '\n')
        print(json.dumps({k:v for k,v in record.items() if k != 'headers'}), flush=True)
        if record.get('status') in [301,302,303,307,308] and record.get('location'):
            url = urllib.parse.urljoin(url, record['location'])
            continue
        return record
    return record

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('urls', nargs='+')
    p.add_argument('--kind', default='raw', choices=['raw','evidence'])
    a = p.parse_args()
    for u in a.urls:
        fetch(u, a.kind)
