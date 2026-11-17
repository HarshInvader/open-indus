"""Build tablets.csv: one row per Harappa miniature tablet object (ICIT TAB:B moulded / TAB:I incised)
with provenance, docket tier, obverse text and copy group.

Run from repo root: .venv/bin/python -I experiments/tablet_archives/build_tablets.py

Provenance comes from the merged ICIT export (sources/paragorth_Indus-/.../merged-corpus-reading-order.json),
whose rows align 1:1 (in order) with data/icit_texts.jsonl rows that are not all-break. Fields used:
  area-section  (e.g. 'ETrench 11', 'FTrench I', 'FGranery', 'AB-')       -> mound, trench
  room-grid     (HARP grid square e.g. '-M11/11' or Vats grid)            -> grid
  time          (HARP sub-period, e.g. 'Period 3C-1')                      -> harp_time
  period/phase  (ICIT; Vats 'Stratum I..VII' for old excavations)
HARP lot (excavation unit) numbers are NOT in any available source: they are printed only in the CISI 3.1 data list
(pp. 423-441), which we could not obtain (Kenoyer & Meadow 2010 intro chapter, raw/harp_km2010, has no lot list).
'deposit' = mound|trench|grid|time|stratum is therefore the finest provenience proxy.

Docket: a side whose signs are exactly {tall-stroke numeral W032/W033/W034, W700 (=M328)} in either order.
Tier = 2/3/4. Objects with two different tiers are dropped. Obverse = all other sides (joined ' / ', sides in id order).
Copy group = (object type, obverse text, tier); only objects whose obverse has no break '#' get an exact group;
damaged obverses get their own singleton group (flag obv_complete=0).
"""
import csv, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TALL = {'W032': 2, 'W033': 3, 'W034': 4}


def load():
    R = [json.loads(l) for l in open(os.path.join(REPO, 'data', 'icit_texts.jsonl'))]
    M = json.load(open(os.path.join(REPO, 'sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json')))
    ih = [r for r in R if r['site'] == 'Harappa']
    mh = [r for r in M if r['site'] == 'Harappa']
    # align in order
    j = 0
    for r in ih:
        s = [int(x[1:]) for x in r['seq'] if x.startswith('W')]
        k = j
        while k < len(mh) and k - j < 20 and not (mh[k]['cisi'] == r['cisi'] and [x for x in mh[k]['seq'] if isinstance(x, int)] == s):
            k += 1
        if k < len(mh) and k - j < 20:
            r['_m'] = mh[k]; j = k + 1
        else:
            r['_m'] = None
    return ih


def clean(v):
    v = (v or '').strip()
    return '' if v in ('-', '--', '') else v


def mound_of(area):
    a = area.replace(' ', '')
    if a.startswith('AB'): return 'AB'
    if a.startswith('ET'): return 'ET'
    if a[:1] in ('E', 'F', 'D', 'G', 'J', 'I'): return a[:1]
    return ''


def main():
    ih = load()
    objs = collections.defaultdict(list)
    for r in ih:
        if r['type'] in ('TAB:B', 'TAB:I'):
            objs[r['id'].split('.')[0]].append(r)
    rows = []
    for oid, recs in objs.items():
        recs.sort(key=lambda r: int(r['id'].split('.')[1]) if r['id'].split('.')[1].isdigit() else 0)
        ms = [r['_m'] for r in recs if r['_m']]
        m = ms[0] if ms else {}
        area = clean(m.get('area-section', '').replace('-', ' ')) if m else ''
        area = ' '.join(area.split())
        grid = clean(m.get('room-grid', '')).strip('-') if m else ''
        htime = clean(m.get('time', '')) if m else ''
        tiers, dock_ids, obv = set(), [], []
        for r in recs:
            s = r['seq']
            if len(s) == 2 and 'W700' in s and any(x in TALL for x in s):
                tiers.add(TALL[[x for x in s if x in TALL][0]]); dock_ids.append(r['id'])
            else:
                obv.append(' '.join(s))
        tier = tiers.pop() if len(tiers) == 1 else (None if not tiers else -1)
        obv_text = ' / '.join(obv)
        obv_complete = int(bool(obv) and '#' not in obv_text)
        rows.append(dict(
            oid=oid, cisi=recs[0]['cisi'], type=recs[0]['type'], material=recs[0]['material'],
            mound=mound_of(area), trench=area, grid=grid, harp_time=htime,
            icit_period=recs[0]['period'], icit_phase=recs[0]['phase'].strip(),
            excavation='HARP' if htime.startswith('Period') or mound_of(area) in ('E', 'ET') else ('Vats/old' if 'Stratum' in recs[0]['phase'] or mound_of(area) in ('F', 'AB', 'D', 'G') else ''),
            tier='' if tier is None else tier, docket_side=';'.join(dock_ids),
            obverse=obv_text, obv_complete=obv_complete, n_sides=len(recs)))
    # copy groups
    for r in rows:
        if r['tier'] in ('', -1):
            r['copy_group'] = ''
            continue
        if r['obv_complete']:
            r['copy_group'] = f"{r['type']}|{r['obverse']}|{r['tier']}"
        else:
            r['copy_group'] = f"single|{r['oid']}"
    size = collections.Counter(r['copy_group'] for r in rows if r['copy_group'])
    for r in rows:
        r['group_size'] = size[r['copy_group']] if r['copy_group'] else ''
        tp = r['harp_time'] or (r['icit_phase'] if 'Stratum' in r['icit_phase'] else '')
        r['period_key'] = tp
        r['deposit'] = '|'.join([r['mound'], r['trench'], r['grid'], tp]) if (r['trench'] or r['grid']) else ''
    out = os.path.join(HERE, 'tablets.csv')
    keys = list(rows[0].keys())
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    # audit
    D = [r for r in rows if r['tier'] in (2, 3, 4)]
    print(f"Harappa tablet objects: {len(rows)}; with docket tier 2/3/4: {len(D)}; conflicting tiers: {sum(r['tier']==-1 for r in rows)}")
    print('tier x type', collections.Counter((r['type'], r['tier']) for r in D))
    print('mound', collections.Counter(r['mound'] for r in D))
    print('excavation', collections.Counter(r['excavation'] for r in D))
    print('trench', collections.Counter(r['trench'] for r in D).most_common(25))
    print('grid known', sum(bool(r['grid']) for r in D), 'harp_time', collections.Counter(r['harp_time'] for r in D))
    print('stratum', collections.Counter(r['icit_phase'] for r in D))
    print('obv complete', sum(r['obv_complete'] for r in D))
    print('deposits (>=1)', len(set(r['deposit'] for r in D if r['deposit'])), 'tablets w/ deposit', sum(bool(r['deposit']) for r in D))
    dep = collections.Counter(r['deposit'] for r in D if r['deposit'])
    print('deposits with >=3 tablets', sum(v >= 3 for v in dep.values()), 'covering', sum(v for v in dep.values() if v >= 3))
    print(dep.most_common(15))
    cg = collections.Counter(r['copy_group'] for r in D)
    print('copy groups', len(cg), 'size dist', collections.Counter(cg.values()))


if __name__ == '__main__':
    main()
