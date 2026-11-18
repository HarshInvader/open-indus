"""Build collection-only tables/crops from saved evidence. Makes no network requests."""
import csv, hashlib, json, pathlib, sys
from collections import Counter
import pymupdf as fitz
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / 'evidence' / 'crops'
OUT.mkdir(exist_ok=True)
records = [json.loads(x) for x in (ROOT/'evidence/requests.jsonl').read_text().splitlines()]
urls = {r['file']:r['url'] for r in records if r.get('file')}
RIGHTS = ('Harappa.com represents commercial image rights; non-commercial scholarly works usually free, '
          'not an automatic open licence. Contact site for use. See evidence/indus-image-rights.html; '
          'PDF author/publisher and object-owner rights may also apply.')
CISI_RIGHTS = ('CISI 1 PDF page 6: Copyright 1987 Academia Scientiarum Fennica (volume), '
               'owners of original objects (photographs). Public mirror is not an open licence.')
rows=[]
def add(need,oid,desc,file,url=None,pixels='',notes='',rights=RIGHTS,**extra):
    r=dict(item_need=need,object_id=oid,description=desc,local_file=file,
           url=url or urls.get(file,''),pixel_size=pixels,licence_or_terms_note=rights,notes=notes,
           object_px_across='',object_bbox_xyxy='',image_kind='',source_page_figure='',site='',year='',year_basis='')
    r.update(extra); rows.append(r); return r

def native(pdf,page,name):
    d=fitz.open(ROOT/'raw'/pdf); xref=d[page-1].get_images()[0][0]; data=d.extract_image(xref)
    f=OUT/name; f.write_bytes(data['image']); return str(f.relative_to(ROOT))

# Every need-1 photo uses original embedded pixels, never an enlarged PDF render.
# Bounding boxes are manual approximate face extents; x1/y1 are exclusive.
measures=[]
def face(oid,source,bbox,desc,url,page='',rights=RIGHTS,kind='photograph',notes=''):
    im=Image.open(ROOT/source); box=tuple(bbox)
    fn=oid.replace(' ','_').replace('/','_').replace('?','')+'.png'
    dest=OUT/fn; im.crop(box).save(dest)
    r=add(1,oid,desc,str(dest.relative_to(ROOT)),url,f'{im.width} x {im.height} native source; {box[2]-box[0]} x {box[3]-box[1]} crop',
          notes=f'Native source: {source}. Approximate manual face extent +/-5 px (irregular edges +/-10); no resampling. {notes}',rights=rights,
          object_px_across=box[2]-box[0],object_bbox_xyxy=json.dumps(box),image_kind=kind,source_page_figure=page)
    measures.append(dict(object_id=oid,source_file=source,crop_file=r['local_file'],native_image_size=list(im.size),
                         bbox_xyxy=list(box),px_across_object=box[2]-box[0],tolerance_px=10 if 'H95' in oid else 5,kind=kind))
    return r

c151=native('CorpusVol1.pdf',151,'cisi_native_p151.jpg')
c245=native('CorpusVol1.pdf',245,'cisi_native_p245.jpg')
cisi_url=urls['raw/CorpusVol1.pdf']
for oid,src,box,page in [
 ('M-478 B',c151,(432,65,743,166),'CISI 1 printed p.115; PDF p.151'),
 ('M-479 B',c151,(441,271,745,362),'CISI 1 printed p.115; PDF p.151'),
 ('M-480 B',c151,(429,404,747,500),'CISI 1 printed p.115; PDF p.151'),
 ('H-177 B',c245,(68,222,269,318),'CISI 1 printed p.209; PDF p.245'),
 ('H-180 B',c245,(62,743,433,860),'CISI 1 printed p.209; PDF p.245')]:
    face(oid,src,box,'Requested tablet face; low-resolution CISI scan',cisi_url,page,CISI_RIGHTS)

master='Kenoyer 2010 Master of Animals.pdf'; d=fitz.open(ROOT/'raw'/master)
im=d.extract_image(107);photo=OUT/'H95-2487_fig11_native.jpg';photo.write_bytes(im['image'])
face('H95-2487',str(photo.relative_to(ROOT)),(30,30,905,383),'Fig.11 horned deity and temple: caption-identified Harappa tablet',urls['raw/'+master],
     'Printed p.50; PDF p.16, Fig.11',notes='935 x 410 native photograph. H-1975 cross-reference supplied as a prior local lead; not independently established by this caption. Do not count as a confirmed offering-vessel image.')
face('Harappa_Trench11_seated_scene','raw/harappa-molded-tablets.jpg',(78,399,357,519),'Seated-scene face in a group of Trench 11 tablets',urls['raw/harappa-molded-tablets.jpg'],
     'Slide molded-tablets, third horizontal face',notes='Museum/CISI id not given on slide. Other group faces are also measured in image_measurements.json.')
# Other broad scene leads retained explicitly as related, not confirmed offering scenes.
face('H95-2486_scene','raw/indus-story.jpg',(30,90,790,463),'Buffalo scene; related narrative tablet',urls['raw/indus-story.jpg'],
     'Slide molded-tablet-0 (89/90)',notes='Caption H95-2486, lot 4651-01. Related scene only; not a confirmed kneeling-vessel target.')
face('H95-2486_reverse','raw/tablet-harappa-inscribed.jpg',(143,60,434,776),'Reverse scene of H95-2486',urls['raw/tablet-harappa-inscribed.jpg'],
     'Slide molded-tablet (90/90)',notes='Face is vertically displayed; horizontal pixel extent reported as stored (291 px); long axis 716 px. Related scene only.')
face('H2001-5075_scene','raw/tiger-tree-man.jpg',(14,69,522,355),'Captioned man-in-tree tablet, H2001-5075/2922-01',urls['raw/tiger-tree-man.jpg'],
     'Slide tablet-man-tree-and-tiger',notes='Related scene; do not relabel M-478. Right-hand reverse also measured separately.')
for oid,src,box,desc in [
 ('Harappa_narrative_left','raw/80_3.jpg',(9,44,241,169),'Left narrative tablet, slide 80'),
 ('Harappa_narrative_right','raw/80_3.jpg',(242,38,543,170),'Right narrative tablet, slide 80'),
 ('Mohenjo_daro_MD602_boat','raw/tablet-indus.jpg',(59,151,756,333),'Three-sided boat tablet MD602; related lead')]:
    face(oid,src,box,desc,urls[src],notes='Caption does not identify a requested kneeling-vessel face; retain only as a related lead.')
# More than one object in group images: record every pictured face, including excluded leads.
for oid,src,box in [
 ('Trench11_script','raw/harappa-molded-tablets.jpg',(78,60,351,177)),
 ('Trench11_bull','raw/harappa-molded-tablets.jpg',(82,237,357,348)),
 ('Trench11_standing','raw/harappa-molded-tablets.jpg',(464,151,592,426)),
 ('H2001-5075_reverse','raw/tiger-tree-man.jpg',(566,5,781,381)),
 ('MD602_gharial_and_script','raw/25_1.jpg',(382,19,733,356)),
 ('MD602_boat_and_script','raw/25_1.jpg',(15,18,378,338)),
 ('faience_tablet_67_obverse','raw/67_1_0.jpg',(35,12,467,245)),
 ('faience_tablet_67_reverse','raw/67_1_0.jpg',(31,273,446,508))]:
    face(oid,src,box,'Additional measured face in retained related slide image',urls[src],notes='Related lead only; no identification as a requested offering tablet.')

# Preserve the corrected identity of the 2184x662 lead without misclassifying it as target photography.
data=d.extract_image(114); (OUT/'master_fig12_drawings_native.png').write_bytes(data['image'])
add(1,'CORRECTION-Fig12','2184 x 662 native image is Fig.12 drawings, not H95-2487',
    'evidence/crops/master_fig12_drawings_native.png',urls['raw/'+master],pixels='2184 x 662',
    notes='Excluded from tablet-face measurement: circular seal Mehrgarh MR-17, Mohenjo-daro M-312 seal, Banawali scene. Caption on PDF p.16.',image_kind='excluded drawings',source_page_figure='Fig.12, printed p.50 / PDF p.16',object_px_across='not applicable - excluded non-tablet lead')
( ROOT/'evidence/image_measurements.json').write_text(json.dumps(measures,indent=2)+'\n')

# Exact local baseline. BNGL is the corpus code, not the literal word bangle.
icit=[json.loads(s) for s in (REPO/'data/icit_texts.jsonl').read_text().splitlines()]
baseline=[r for r in icit if r['site']=='Harappa' and ('bangle' in r['type'].lower() or r['type']=='BNGL')]
(ROOT/'evidence/icit_harappa_bangles.json').write_text(json.dumps(baseline,indent=2)+'\n')
bangles=[]
for r in baseline:
    bangles.append(dict(id=r['cisi'] if r['cisi']!='-' else 'ICIT-'+r['id'],site=r['site'],inner_diameter_mm='',
        inscription_as_given=' '.join(r['seq']),source_page_figure='corpus/load.py icit_texts(); ICIT '+r['id'],in_ICIT='yes',
        local_crop='',url='',notes='Existing baseline, not an added text. Type '+r['type']+'; material '+r['material']+'. No inner diameter recorded; width_mm/height_mm zero are not diameters.'))

bangle_specs=[
 ('Vidale-fig3-14756_27','Mohenjo-daro','evidence/crops/stoneware_p6_native.png',(0,1200,850,2338),90,'Vidale, Stoneware Industry; PDF p.6, Fig.3','Source caption: micro-inscription of 5 signs; Dep.CS.Neg.14756/27. No sign-number transcription supplied.'),
 ('Vidale-fig4-14575_12','Mohenjo-daro','evidence/crops/stoneware_p7_native.png',(900,0,1653,1180),90,'Vidale, Stoneware Industry; PDF p.7, Fig.4','Source caption: micro-inscription of 2 signs; Dep.CS.Neg.14575/12. No sign-number transcription supplied.'),
 ('Kenoyer2021-fig4.1','Mohenjo-daro','raw/painted-script.jpg',(7,12,460,223),0,'Kenoyer 2021, printed/PDF p.7, Fig.4.1','Not transcribed; photograph and source line drawing retained. Caption says not to scale.'),
 ('Kenoyer2021-fig4.2','Mohenjo-daro','raw/painted-script.jpg',(7,223,460,362),0,'Kenoyer 2021, printed/PDF p.7, Fig.4.2','Not transcribed; photograph and source line drawing retained. Caption says not to scale.'),
 ('Kenoyer2021-fig4.3','Harappa','raw/painted-script.jpg',(7,362,460,560),0,'Kenoyer 2021, printed/PDF p.7, Fig.4.3','Not transcribed; source drawing and scale retained. Source is a drawing, not a photograph.')]
for oid,site,src,box,rotate,page,inscr in bangle_specs:
    im=Image.open(ROOT/src).crop(box)
    if rotate:im=im.rotate(rotate,expand=True)
    dest=OUT/(oid+'.png'); im.save(dest)
    url=urls['raw/stoneware_bangles.pdf'] if oid.startswith('Vidale') else urls['raw/580-Article Text-993-1-10-20220407.pdf']
    bangles.append(dict(id=oid,site=site,inner_diameter_mm='',inscription_as_given=inscr,source_page_figure=page,in_ICIT='unsure',
        local_crop=str(dest.relative_to(ROOT)),url=url,notes='Illustration identifier only, not a museum id. No individual inner diameter. Unknown overlap with ICIT and with other illustrated instances; do not count as a confirmed new object/text.'))
    add(2,oid,'Illustrated stoneware-bangle inscription; '+site,str(dest.relative_to(ROOT)),url,f'{im.width} x {im.height} crop',
        notes=inscr+' Inner diameter not supplied. ICIT overlap unsure; no sign interpretation.',source_page_figure=page,site=site)

def writecsv(path,data,fields=None):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fields or list(data[0]));w.writeheader();w.writerows(data)
writecsv(ROOT/'bangles.csv',bangles)
add(2,'ICIT-Harappa-BNGL','Seven existing Harappa bangle records; deduplication baseline','evidence/icit_harappa_bangles.json',
    notes='Literal type contains bangle yields zero. BNGL yields seven. Includes Clay/Stoneware/unspecified materials; do not treat all seven as stoneware.')
add(2,'stoneware-size-range','Kenoyer Ancient Cities pp.145-146 quoted on slide: 5.5-6 cm interior diameter',
    'evidence/stoneware-bangle.html',notes='Class-level range 55-60 mm only, never assigned to individual bangles.',source_page_figure='Ancient Cities pp.145-146, fig.7.47')
add(2,'Vidale-paper','stoneware_bangles.pdf is Massimo Vidale\'s technology paper, not a Kenoyer 19-bangle catalogue',
    'raw/stoneware_bangles.pdf',notes='Only Figs.3-4 illustrate inscriptions; PDF p.6 and p.7. Figures 1-2 and later production figures do not supply a per-bangle text/diameter table.')
add(2,'Dales-stoneware','Dales ceramics chapter: stoneware bangles and chemical characterization, not inscription catalogue',
    'raw/Harappa1986-90_05_Dales-Ceramics.pdf',notes='Printed pp.67-68 / PDF pp.9-10; no 19 individual inscriptions or paired inner diameters.')

# Need 3: transcribe only supplied counts and explicitly captioned vessel forms/stages.
phases=[('1 Ravi',23,'1.89%'),('1/2',7,'0.57%'),('2 Kot Diji',224,'18.39%'),('2/3',19,'1.56%'),('3 Harappa',941,'77.26%'),('4/5 Late Harappa',4,'0.33%')]
writecsv(ROOT/'sherd_phase_counts.csv',[dict(period=a,sherds=b,percentage_as_printed=c,source='Kenoyer 2020, printed p.230 / PDF p.14, Table 3') for a,b,c in phases])
writecsv(ROOT/'sherd_firing_counts.csv',[dict(period=p,firing_stage=s,sherds=n,percentage_as_printed=q,source='Kenoyer 2020, printed p.230 / PDF p.14, Table 4') for p,s,n,q in [('1 Ravi','pre',7,'30.43%'),('1 Ravi','post',16,'69.57%'),('2 Kot Diji','pre',49,'21.88%'),('2 Kot Diji','post',175,'78.13%')]])
d=fitz.open(ROOT/'raw/Kenoyer2020 Origin of Indus Script.pdf');d[13].get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/'sherd_tables3_4_p230.png')
add(3,'Harappa-1218','All-phase marked/graffiti sherd counts and early phase firing split','evidence/crops/sherd_tables3_4_p230.png',
    urls['raw/Kenoyer2020 Origin of Indus Script.pdf'],notes='Table 3 total 1218; Table 4 covers only Periods 1 and 2, 247 sherds (56 pre, 191 post). No vessel-form cross-tab for all 1218.',source_page_figure='Printed p.230 / PDF p.14, Tables 3-4',image_kind='page render; not native photo')
add(3,'Kenoyer-Meadow-2010','Chronology and definitions; PBGs with pre-firing impressed script',
    'raw/Kenoyer-Meadow-2010-HARP.pdf',notes='PDF pp.6-10, printed xlvii-li. Graffiti defined post-manufacture in footnote 7; pre-firing marks distinguished. H-1081/H-1082 pointed-base goblets; no table of 1218 sherds.')
add(3,'Dales-ceramics','Harappa ceramic forms and production review','raw/Harappa1986-90_05_Dales-Ceramics.pdf',
    notes='No per-sherd 1218-row register or complete pre/post x vessel-form table found in this 1991 chapter.')
sherds=[]
forms=[('H95 / 5684-02','Black Slipped Jar','post-firing graffiti on rim and body'),('H95-2662 / 6640-501','Black Slipped Jar','post-firing graffiti on rim and body; pre-firing potter\'s marks on base and body'),('H94 / 4290-14','Large Red Slipped Black Band Jar','post-firing graffiti on body'),('H95 / 5630-15','Plain globular jar','post-firing graffiti on body'),('H93 / 4305-500','Black Slipped Jar','post-firing graffiti on body'),('H93 / 4159-500','Black Slipped Jar','post-firing graffiti on body'),('H93 / 4043-503','Black Slipped Jar','post-firing graffiti on body'),('H93 / 4304-500','Black Slipped Jar','post-firing graffiti on body')]
d=fitz.open(ROOT/'raw/580-Article Text-993-1-10-20220407.pdf');d[5].get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/'painted2021_fig3_sherds.png')
for n,(oid,form,stage) in enumerate(forms,1):
    sherds.append(dict(object_id=oid,site='Harappa',vessel_form_as_given=form,firing_and_location_as_given=stage,source_page_figure=f'Kenoyer 2021 p.6, Fig.3.{n}',local_file='evidence/crops/painted2021_fig3_sherds.png',url=urls['raw/580-Article Text-993-1-10-20220407.pdf'],notes='Illustrative object; membership in the 1986-2003 tabulation not individually established.'))
writecsv(ROOT/'marked_sherds.csv',sherds)
add(3,'Harappa-Fig3-eight','Eight captioned vessel-form/stage examples from Kenoyer 2021','evidence/crops/painted2021_fig3_sherds.png',
    urls['raw/580-Article Text-993-1-10-20220407.pdf'],notes='See marked_sherds.csv; seven post-only, one explicitly both pre and post. Cannot join these eight to the 1218-row dataset.',source_page_figure='Kenoyer 2021 p.6, Fig.3.1-8',image_kind='page render')

# Need 4: year means source/publication evidence; no fabricated Drupal creation date.
recent=[]
def recentrow(oid,site,desc,file,page,year,basis,status):
    im=Image.open(ROOT/file)
    recent.append(dict(object_id=oid,site=site,object=desc,year=year,year_basis=basis,date_status=status,url=page,local_file=file,pixel_size=f'{im.width} x {im.height}',notes='Visible inscription checked on saved image; no sign reading attempted.'))
    add(4,oid,desc,file,urls.get(file,urls['raw/painted-script.jpg']),f'{im.width} x {im.height}',notes=f'Page: {page}. {status}. {basis}',site=site,year=year,year_basis=basis,image_kind='photograph')
recentrow('Ganweriwala-tablet','Ganweriwala','Clay tablet with seated figure and inscription; photo plus drawing','raw/ganweriwala-3.jpg','https://www.harappa.com/blog/glimpses-ganweriwala','2018-2026','Page discusses Walking with the Unicorn (2018); exact website post year not exposed.','post-2018 source-supported interval; exact post year unknown')
recentrow('Umma-Indus-sealing','Umma, Mesopotamia (reported provenance)','Inscribed Indus seal impression; now Ashmolean, formerly Louvre','raw/umma-seal-impression.jpg','https://www.harappa.com/blog/indus-seal-impression-umma-mesopotamia','2022-2026','Page quotes Save Mohenjo Daro! (2022); exact website post year not exposed.','post-2018 source-supported interval; exact post year unknown')
for k,site in [(1,'Mohenjo-daro'),(2,'Mohenjo-daro'),(3,'Harappa')]:
    # Fig4.3 is drawing-only and not a qualifying legible photo.
    if k==3:continue
    file=f'evidence/crops/Kenoyer2021-fig4.{k}.png';im=Image.open(ROOT/file)
    recent.append(dict(object_id=f'Kenoyer2021-fig4.{k}',site=site,object='Inscribed stoneware bangle photograph plus source drawing',year='2021-2026',year_basis='Harappa page identifies original publication Ancient Pakistan XXXII (2021); site post date absent.',date_status='post-2018 source-supported interval; exact post year unknown',url='https://www.harappa.com/content/painted-indus-script-ceramics-and-steatite-new-insights-indus-script-calligraphy-and',local_file=file,pixel_size=f'{im.width} x {im.height}',notes='Anonymous object: ICIT overlap and duplication across publications unsure.'))
    add(4,f'Kenoyer2021-fig4.{k}','Inscribed stoneware bangle photograph',file,urls['raw/painted-script.jpg'],f'{im.width} x {im.height}',notes=recent[-1]['year_basis'],site=site,year='2021-2026',year_basis=recent[-1]['year_basis'],image_kind='photograph plus source drawing')
im=Image.open(ROOT/'raw/painted-script.jpg').crop((493,204,978,422));im.save(OUT/'Kenoyer2021-fig5-gold.png')
recentrow('Kenoyer2021-fig5','Mohenjo-daro','Inscribed gold pendant photograph plus drawing','evidence/crops/Kenoyer2021-fig5-gold.png','https://www.harappa.com/content/painted-indus-script-ceramics-and-steatite-new-insights-indus-script-calligraphy-and','2021-2026','Kenoyer 2021 p.7 Fig.5; Harappa page identifies original 2021 publication.','post-2018 source-supported interval; exact post year unknown')
rows[-1]['url']=urls['raw/painted-script.jpg']
for file,oid in [('unicorn-seal-IMG_9616.jpg','Four-seals-unicorn-1'),('unicorn-seal-2-IMG_9269.jpg','Four-seals-unicorn-2'),('elephant-seal-IMG_9278.jpg','Four-seals-elephant'),('tiger-seal-IMG_9284.jpg','Four-seals-tiger')]:
    recentrow(oid,'Mohenjo-daro','Inscribed seal photographed at National Museum of Pakistan, Karachi','raw/'+file,'https://www.harappa.com/blog/four-seals-close','unknown','Individual page has no post date; do not infer a year from copyright or listing order.','candidate only; since-2018 date unverified')
recentrow('Chanhu-daro-M77-5033','Chanhu-daro','Unicorn seal photograph at MFA Boston; source identifies inscription 5033','raw/chanhu-daro-seal_0_0.jpg','https://www.harappa.com/blog/toponym-chanhu-daro','unknown','Individual page has no post date; do not infer date from copyright or listing order.','candidate only; since-2018 date unverified')
recentrow('Mohenjo-daro-featured-seal','Mohenjo-daro','Inscribed unicorn seal, featured photo in interregional study article','raw/seal-2-mohen.jpg','https://www.harappa.com/content/mohenjo-daro-and-interregional-connections-indus-civilization-evidence-inscribed-seals','unknown','No website creation date in captured HTML.','candidate only; since-2018 date unverified')
for oid,file in [('BSR-7368','bagasra-2.jpg'),('BSR-8288','bagasra-2.jpg'),('BSR-7197','bagasra-4.jpg'),('BSR-6719','bagasra-3.jpg'),('BSR-6952','bagasra-3.jpg')]:
    recentrow(oid,'Bagasra (Gola Dhoro), Gujarat','Inscribed unicorn seal; source-labelled photo figure','raw/'+file,'https://www.harappa.com/content/inscribed-unicorn-seals-bagasra-gujarat-comparative-analysis-morphology-carving-styles-and','unknown','Source-labelled object; website post year absent. Same object may occur in multiple saved composites.','candidate only; since-2018 date unverified')
writecsv(ROOT/'recent_objects.csv',recent)
# Exclude the dated new-year graphic from the photographic count.
add(4,'EXCLUDED-new-year-2022','Dated image is a modern graphic, not an object photograph','raw/unicorn-seal-2021-2022-b.jpg',
    pixels='582 x 706',notes='Happy New Year 2022 page. Excluded despite an explicit year; site provenance not supplied.',year='2022',image_kind='excluded modern graphic')

# Supplementary paper and page inventory, with exact successful URLs.
for need,file,desc in [
 (1,'raw/CorpusVol1.pdf','CISI 1 complete public mirror; native targets on PDF pp.151 and 245'),
 (1,'raw/76884.pdf','Government mirror checked for improved resolution: same target image pixels, repeated twice in 862 pages; no improvement'),
 (1,'raw/Kenoyer 2010 Master of Animals.pdf','Source of caption-corrected Figure 11 and excluded Figure 12'),
 (1,'raw/Kenoyer1997_Excavations at Harappa 1994-1995 New Perspective.pdf','Figure 9.10 H95-2487/4466-01 line drawing; PDF p.18'),
 (1,'raw/Parpola_Asko_2011._Crocodile_in_the_Indu.pdf','Figure 49 M-478 drawing; PDF p.41; not a higher-resolution target photograph'),
 (2,'raw/580-Article Text-993-1-10-20220407.pdf','Kenoyer 2021, Figures 3-5; working HTTP link, HTTPS previously timed out')]:
    add(need,pathlib.Path(file).stem,desc,file,rights=CISI_RIGHTS if ('CorpusVol1' in file or '76884' in file) else RIGHTS)
for need,fn in [(1,'indus-narrative-tablets'),(1,'molded-tablets'),(1,'molded-tablet-0'),(1,'molded-tablet'),(1,'tablet-man-tree-and-tiger'),(1,'moulded-tablet-mohenjo-daro'),(4,'glimpses-ganweriwala'),(4,'indus-seal-impression-umma-mesopotamia'),(4,'four-seals-close'),(4,'toponym-chanhu-daro'),(4,'painted-indus-script-ceramics-and-steatite-new-insights-indus-script-calligraphy-and')]:
    add(need,'page-'+fn,'Caption/context page','evidence/'+fn+'.html')
# Provenance for a crop is its parent URL.
for r in recent:
    if not r['url']:raise ValueError(r)
writecsv(ROOT/'SOURCES.csv',rows)
# Hash inventory validates transport integrity and derived-file readability.
manifest=[]
for f in sorted(ROOT.rglob('*')):
    if f.is_file() and f.name not in ['asset_manifest.csv','last_request.txt'] and '__pycache__' not in f.parts:
        b=f.read_bytes();manifest.append(dict(local_file=str(f.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
writecsv(ROOT/'asset_manifest.csv',manifest)
print(json.dumps(dict(source_rows=len(rows),need1_measured_faces=len(measures),bangle_rows=len(bangles),baseline_bangles=len(baseline),illustrated_bangle_instances=5,recent_rows=len(recent),phase_sherds=sum(x[1] for x in phases),request_status_counts=Counter(str(r.get('status','error')) for r in records)),indent=2))
