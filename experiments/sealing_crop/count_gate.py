"""sealing_crop count gate. Label-free: metadata and file listings only.

Run from the repo root:  python3 -I experiments/sealing_crop/count_gate.py
Rules: experiments/sealing_crop/MINIMUM.txt (hashed before this script was written).
Inputs : data/icit_texts.jsonl (ICIT metadata: type, site, symbol, complete, seq)
         experiments/scene_text/work/faces.json (listing of located CISI vol 1-2 photo boxes; local only)
Output : experiments/sealing_crop/count_gate.json (counts only)
Opens no image. Codes no share. Crosses no outcome with anything.
"""
import collections
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ICIT = os.path.join(ROOT, 'data', 'icit_texts.jsonl')
FACES = os.path.join(ROOT, 'experiments', 'scene_text', 'work', 'faces.json')

# MINIMUM.txt b: "named animal or icon code", not None / - / ? / blank / geometric-only.
# "Unknown" is read as not a named code (implementer reading, disclosed in count_gate.md).
NOT_DETERMINABLE = {'None', '-', '?', '', 'Unknown'}
# K1: a named ANIMAL code (stricter than b: no Scene, Mult, Othr, T-A-T, T-M-T, Phyt, Htgr).
ANIMAL = re.compile(r'^(Bull|Bult|CompBull|Elep|Zebu|Gaur|Rhin|Tigr|Buff|Goat|Gavi)')

MAX_SKIP = 0.25
M1, M2, M3_SITE = 80, 25, 5
C1, C2, C3_SITE = (math.ceil(m / (1 - MAX_SKIP)) for m in (M1, M2, M3_SITE))
K1 = 30


def norm_cisi(c):
    c = (c or '').strip()
    m = re.match(r'^([A-Z][a-z]*)-(\d+)', c)
    return f'{m.group(1)}-{int(m.group(2))}' if m else None


def has_sign(r):
    return any(isinstance(s, str) and re.match(r'^W\d+', s) for s in r.get('seq') or [])


def main():
    rows = [json.loads(l) for l in open(ICIT, encoding='utf8')]
    faces = json.load(open(FACES, encoding='utf8'))
    photo = collections.Counter(f['cisi'] for f in faces if f.get('box') is not None)

    def obj(r):
        return r['id'].split('.')[0]

    tag = [r for r in rows if r['type'].startswith('TAG')]
    out = {'n_tag_rows': len(tag), 'n_tag_objects': len({obj(r) for r in tag})}

    with_cisi = [r for r in tag if norm_cisi(r['cisi'])]
    with_photo = [r for r in with_cisi if photo.get(norm_cisi(r['cisi']), 0) > 0]
    out['tag_rows_with_cisi_by_site'] = dict(collections.Counter(r['site'] for r in with_cisi).most_common())
    out['tag_rows_with_photo_by_site'] = dict(collections.Counter(r['site'] for r in with_photo).most_common())
    out['tag_objects_with_photo'] = len({obj(r) for r in with_photo})

    def summarise(sel):
        by_site = collections.Counter(r['site'] for r in sel)
        non_lothal = sum(v for k, v in by_site.items() if k != 'Lothal')
        sites_ok = sorted(k for k, v in by_site.items() if v >= C3_SITE)
        return {
            'rows': len(sel),
            'objects': len({obj(r) for r in sel}),
            'by_site': dict(by_site.most_common()),
            'objects_by_site': dict(collections.Counter(s for s, _ in {(r['site'], obj(r)) for r in sel}).most_common()),
            'non_lothal_rows': non_lothal,
            f'sites_with_ge_{C3_SITE}': sites_ok,
        }

    # Primary eligible set (a, b, c, d).
    elig = [r for r in with_photo
            if r['symbol'] not in NOT_DETERMINABLE and has_sign(r) and r.get('site')]
    # Record-only inclusive set (a, c-text, d; any symbol value).
    incl = [r for r in with_photo if has_sign(r) and r.get('site')]
    out['eligible_primary'] = summarise(elig)
    out['eligible_primary_symbol_values'] = dict(collections.Counter(r['symbol'] for r in elig).most_common())
    out['inclusive_record_only'] = summarise(incl)

    # Calibration: intact seals with a local photo.
    def calib(sel):
        objs = {}
        for r in sel:
            objs.setdefault(obj(r), r)
        return {'objects': len(objs),
                'by_site': dict(collections.Counter(r['site'] for r in objs.values()).most_common())}

    seal_ok = [r for r in rows if r['type'].startswith('SEAL') and r.get('complete') is True
               and ANIMAL.match(r['symbol'] or '') and has_sign(r) and norm_cisi(r['cisi'])
               and photo.get(norm_cisi(r['cisi']), 0) > 0]
    # K2: drop any calibration seal whose CISI number is also an eligible sealing's (no die pairs known in ICIT).
    elig_cisi = {norm_cisi(r['cisi']) for r in elig}
    seal_ok = [r for r in seal_ok if norm_cisi(r['cisi']) not in elig_cisi]
    out['calibration_all_seal_types'] = calib(seal_ok)
    out['calibration_square_only'] = calib([r for r in seal_ok if r['type'] == 'SEAL:S'])

    p = out['eligible_primary']
    k = out['calibration_square_only']
    checks = {
        f'C1 eligible >= {C1}': p['rows'] >= C1,
        f'C2 non-Lothal >= {C2}': p['non_lothal_rows'] >= C2,
        f'C3 >= 3 sites with >= {C3_SITE}': len(p[f'sites_with_ge_{C3_SITE}']) >= 3,
        f'K1 calibration seals >= {K1} from >= 2 sites': k['objects'] >= K1 and len(k['by_site']) >= 2,
    }
    out['checks'] = checks
    out['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    json.dump(out, open(os.path.join(HERE, 'count_gate.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
