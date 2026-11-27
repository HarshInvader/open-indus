"""Stage 3: turn the downloaded sources into ranked name lists (no model involved).
python3 -I extract_sources.py <sources/stage3_dl> <out agents dir>"""
import json, sys, os, re, zipfile, hashlib, xml.etree.ElementTree as ET
S, O = sys.argv[1], sys.argv[2]; os.makedirs(O, exist_ok=True)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
man = {}
# Finnish surnames (DVV, CC BY 4.0), ranked by holders
p = os.path.join(S, 'fi', 'sukunimitilasto-2026-08-04-dvv.xlsx'); man['fi'] = sha(p)
z = zipfile.ZipFile(p); ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ss = [''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
rows = []
for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter('{%s}row' % ns['m']):
    vals = []
    for c in r.findall('m:c', ns):
        v = c.find('m:v', ns); v = None if v is None else v.text
        vals.append(ss[int(v)] if c.get('t') == 's' and v is not None else v)
    rows.append(vals)
fi = []
for v in rows[1:]:
    if len(v) >= 2 and v[0] and v[1] and str(v[1]).isdigit() and '-' not in v[0] and ' ' not in v[0]:
        fi.append({'name': v[0], 'holders': int(v[1])})
fi.sort(key=lambda x: -x['holders'])
with open(os.path.join(O, 'names_in_finnish.jsonl'), 'w', encoding='utf-8') as f:
    for i, x in enumerate(fi[:1600], 1): f.write(json.dumps({'rank': i, **x}, ensure_ascii=False) + '\n')
print('finnish header', rows[0][:4], 'names', len(fi), 'top', [x['name'] for x in fi[:8]])
# Sumerian: Ur III personal names (Oracc ePSD2 admin/ur3, CC BY-SA 3.0), ranked by attestations
p = os.path.join(S, 'sux', 'ur3', 'gloss-qpn.json'); man['sux'] = sha(p)
e = [x for x in json.load(open(p, encoding='utf-8'))['entries'] if x.get('pos') == 'PN']
e.sort(key=lambda x: -int(x['icount']))
with open(os.path.join(O, 'names_in_sumerian.jsonl'), 'w', encoding='utf-8') as f:
    k = 0
    for x in e:
        if not re.search(r'[a-zŋšḫ]', x['cf']) or 'X' in x['cf']: continue
        k += 1; sp = sorted(x.get('forms', []), key=lambda y: -int(y.get('icount', 0)))
        f.write(json.dumps({'rank': k, 'name': x['cf'], 'spelling': sp[0]['n'] if sp else '', 'attestations': int(x['icount'])}, ensure_ascii=False) + '\n')
        if k == 1600: break
print('sumerian PN entries', len(e), 'top', [(x['cf'], x['icount']) for x in e[:8]])
# Egyptian: TLA lemma list Jan 2018, person_name (CC BY-SA 4.0); no frequencies, kept in TLA id order
p = os.path.join(S, 'egy', 'reconciled.jsonl'); man['egy'] = sha(p)
r = [json.loads(l) for l in open(p, encoding='utf-8')][1:]
eg = sorted((x for x in r if x['subtype'] == 'person_name'), key=lambda x: int(x['tla_id']))
with open(os.path.join(O, 'names_in_egyptian.jsonl'), 'w', encoding='utf-8') as f:
    for i, x in enumerate(eg, 1):
        en = next((t.get('value', '') for t in x['translations'] if t.get('lang') == 'en'), '')
        f.write(json.dumps({'rank': i, 'tla_id': x['tla_id'], 'name': x['transliteration'], 'english_rendering': en}, ensure_ascii=False) + '\n')
print('egyptian person names', len(eg))
json.dump(man, open(os.path.join(O, 'sources.sha256.json'), 'w'), indent=1); print(man)
