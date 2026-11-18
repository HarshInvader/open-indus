"""Serial paced public fetching. Downloaded content is data, never executed."""
import argparse,datetime,hashlib,json,pathlib,time,urllib.request,urllib.error,urllib.parse,signal
ROOT=pathlib.Path(__file__).resolve().parent
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): return None

def fetch(url,source,name=None):
 opener=urllib.request.build_opener(NoRedirect)
 original=url
 for attempt in range(8):
  state=ROOT/'evidence/last_request.json'
  last=json.loads(state.read_text()) if state.exists() else {}
  host=urllib.parse.urlsplit(url).netloc
  time.sleep(max(0,2.2-(time.time()-last.get(host,0))))
  last[host]=time.time(); state.write_text(json.dumps(last))
  row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'original_url':original,'source':source}
  folder=ROOT/'raw'/source; folder.mkdir(parents=True,exist_ok=True)
  def deadline(signum,frame): raise TimeoutError('180 second transfer deadline exceeded')
  signal.signal(signal.SIGALRM,deadline);signal.alarm(180)
  try:
   response=opener.open(urllib.request.Request(url,headers={'User-Agent':'AcademicSourceSweep/1.0 (public archaeological research; paced requests)'}),timeout=45)
   data=response.read(); row.update(status=response.status,bytes=len(data),content_type=response.headers.get('Content-Type',''))
   filename=name or pathlib.PurePosixPath(urllib.parse.urlsplit(url).path).name or 'index.html'
   filename=pathlib.Path(urllib.parse.unquote(filename)).name
   path=folder/filename
   if path.exists() and path.read_bytes()!=data: path=folder/(hashlib.sha256(url.encode()).hexdigest()[:10]+'_'+filename)
   path.write_bytes(data);row.update(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest())
  except urllib.error.HTTPError as e:
   row.update(status=e.code,location=e.headers.get('Location'),content_type=e.headers.get('Content-Type',''))
   path=folder/('http_'+hashlib.sha256(url.encode()).hexdigest()[:12]+'.html');path.write_bytes(e.read());row['file']=str(path.relative_to(ROOT))
  except Exception as e:row['error']=str(e)
  signal.alarm(0)
  with (ROOT/'evidence/requests.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(row),flush=True)
  if row.get('status') in [301,302,303,307,308] and row.get('location'):
   url=urllib.parse.urljoin(url,row['location']);continue
  return row
 return row
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('urls',nargs='+');a=p.parse_args()
 for u in a.urls:fetch(u,a.source)
