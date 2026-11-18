"""Offline validation of the source collection; no sign or vessel interpretation."""
import csv,datetime,hashlib,json,pathlib,re
from collections import Counter
import pymupdf as fitz
from PIL import Image
R=pathlib.Path(__file__).resolve().parent

def read(name):return list(csv.DictReader((R/name).open()))
req=[json.loads(s) for s in (R/'evidence/requests.jsonl').read_text().splitlines()]
success={r['url'] for r in req if r.get('status')==200}
src=read('SOURCES.csv');bang=read('bangles.csv');recent=read('recent_objects.csv')
assert len(src)==69
assert Counter(r['item_need'] for r in src).keys()=={'1','2','3','4'}
for r in src:
    assert (R/r['local_file']).is_file(),r
    if r['url']:assert r['url'] in success,r
for r in recent:
    assert (R/r['local_file']).is_file(),r
    assert r['url'] in success,r
assert len(bang)==12 and Counter(r['in_ICIT'] for r in bang)=={'yes':7,'unsure':5}
assert all(not r['inner_diameter_mm'] for r in bang)
for r in bang:
    if r['local_crop']:Image.open(R/r['local_crop']).verify()
assert sum(int(r['sherds']) for r in read('sherd_phase_counts.csv'))==1218
stages=read('sherd_firing_counts.csv');assert sum(int(r['sherds']) for r in stages)==247
assert sum(int(r['sherds']) for r in stages if r['firing_stage']=='pre')==56
assert sum(int(r['sherds']) for r in stages if r['firing_stage']=='post')==191
assert len(read('marked_sherds.csv'))==8
assert len(recent)==16
assert sum(r['date_status'].startswith('post-2018') for r in recent)==5
m=json.loads((R/'evidence/image_measurements.json').read_text());assert len(m)==21
for r in m:
    im=Image.open(R/r['source_file']);box=r['bbox_xyxy'];x0,y0,x1,y1=box
    assert 0<=x0<x1<=im.width and 0<=y0<y1<=im.height,r
    crop=Image.open(R/r['crop_file'])
    assert crop.size==(x1-x0,y1-y0),r
    assert crop.tobytes()==im.crop(tuple(box)).tobytes(),r
# Independent mirrors have identical native target-image bytes, no improvement.
d1=fitz.open(R/'raw/CorpusVol1.pdf');d2=fitz.open(R/'raw/76884.pdf')
assert len(d1)==431 and len(d2)==862
for page in [151,245]:
    def raster(d,n):return d.extract_image(d[n-1].get_images()[0][0])['image']
    assert raster(d1,page)==raster(d2,page)==raster(d2,page+431)
# Verify all transport hashes still match the saved bytes.
for r in req:
    if r.get('file') and r.get('sha256'):
        assert hashlib.sha256((R/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
# Captured requests have no duplicate successful original URLs.
c=Counter(r['url'] for r in req if r.get('status')==200)
assert all(v==1 for v in c.values()),c
# Validate local Markdown links in the delivered report.
for target in re.findall(r'\]\(([^)]+)\)',(R/'RESULTS.md').read_text()):
    if not target.startswith(('http:','https:')):assert (R/target.split('#')[0]).exists(),target
for f in (R/'raw').glob('*.jpg'):Image.open(f).verify()
for r in read('asset_manifest.csv'):
    f=R/r['local_file'];assert f.stat().st_size==int(r['bytes']),f
    assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],f
out=dict(result='PASS',source_rows=len(src),bangle_rows=len(bang),baseline_bangles=7,illustration_instances=5,
         confirmed_new_bangle_texts=0,individual_inner_diameters=0,need1_measured_faces=len(m),requested_faces=5,
         recent_photo_rows=len(recent),recent_source_year_intervals=5,exact_website_post_years=0,
         sherd_phase_total=1218,sherds_with_firing_split=247,vessel_examples=8,
         request_status_counts=Counter(str(r.get('status','error')) for r in req),
         source_hashes_verified=sum(bool(r.get('sha256')) for r in req),
         mirror_target_native_bytes_equal=True,no_duplicate_successful_urls=True)
(R/'evidence/validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
