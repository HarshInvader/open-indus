"""C1: locate every photographed seal side in CISI vol. 1-2 and link unicorn seals to ICIT.

Inputs: native page images (pdfimages -j of experiments/iconography/raw/cisi/CorpusVol{1,2}.pdf,
in work/pages/) and tesseract TSV of each page upscaled 3x (work/ocr/, made by work/ocr_one.sh).
Method: photo boxes = connected non-white blobs (as iconography/i3_detect_boxes.py); each box gets
the OCR label ("M-207" + side letter) found just below it and horizontally inside it.
Output: work/boxes.csv (one row per labelled box) and work/unicorn_boxes.csv (ICIT Bull1 square seals).
Run: .venv/bin/python -I experiments/carver_hands/c1_locate.py
"""
import os, re, json, csv, glob, collections as C
import numpy as np
from PIL import Image
from scipy import ndimage

D = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(D))
PG, OCR = os.path.join(D, 'work', 'pages'), os.path.join(D, 'work', 'ocr')
ID_RE = re.compile(r'^([A-Z][a-z]{0,2})-(\d{1,4})([A-Za-z]?)$')


def boxes(a):
    mask = a < 215
    mask = ndimage.binary_opening(mask, iterations=1)
    mask = ndimage.binary_closing(mask, iterations=4)
    mask = ndimage.binary_fill_holes(mask)
    lab, n = ndimage.label(mask)
    out = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if 50 < h < a.shape[0] * 0.8 and 50 < w < a.shape[1] * 0.9:
            out.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    return out


def ocr_tokens(tsv):
    toks = []
    for row in csv.reader(open(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
        if len(row) < 12 or row[0] == 'level' or not row[11].strip():
            continue
        x, y, w, h = (int(v) / 3 for v in row[6:10])
        toks.append((x, y, w, h, row[11].strip()))
    return toks


def labels(toks):
    """pair an ID token (M-207) with a side token (A/a/B/b...) just to its right."""
    out = []
    for x, y, w, h, t in toks:
        t2 = t.replace('—', '-').replace('–', '-').strip('.,;:')
        m = ID_RE.match(t2)
        if not m:
            continue
        side = m.group(3)
        if not side:
            cands = [(x2 - (x + w), t3) for x2, y2, w2, h2, t3 in toks
                     if 0 <= x2 - (x + w) < 25 and abs((y2 + h2 / 2) - (y + h / 2)) < 8 and len(t3) <= 4]
            if cands:
                side = min(cands)[1].strip('.,')
        out.append(dict(prefix=m.group(1), num=int(m.group(2)), side=side, x=x, y=y, w=w, h=h))
    return out


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(PG, '*.jpg'))):
        b = os.path.basename(f)[:-4]
        vol, page = b.split('-')[0], int(b.split('-')[1])
        tsv = os.path.join(OCR, b + '.tsv')
        if not os.path.exists(tsv):
            continue
        labs = labels(ocr_tokens(tsv))
        if not labs:
            continue
        a = np.asarray(Image.open(f).convert('L'))
        for (x0, y0, x1, y1) in boxes(a):
            best = None
            for L in labs:
                cx = L['x'] + L['w'] / 2
                dy = L['y'] - y1
                if -6 <= dy <= 45 and x0 - 15 <= cx <= x1 + 15:
                    score = dy + abs(cx - (x0 + x1) / 2) * 0.2
                    if best is None or score < best[0]:
                        best = (score, L)
            if best:
                L = best[1]
                side = {'а': 'a', 'А': 'A', 'a.': 'a', 'A.': 'A', 'à': 'a', 'á': 'a'}.get(L['side'], L['side'])
                rows.append(dict(file=os.path.basename(f), vol=vol, page=page, x0=x0, y0=y0, x1=x1, y1=y1,
                                 cisi=f"{L['prefix']}-{L['num']}", side=side))
    # missing side letter: on seal pages the seal (A) is photographed beside its impression (a).
    # If a box has no side letter and its id has exactly one other box on the page, the left one is A, the right a.
    byk = C.defaultdict(list)
    for r in rows:
        byk[(r['file'], r['cisi'])].append(r)
    for k, rs in byk.items():
        if len(rs) == 2 and any(r['side'] == '' for r in rs):
            l, rr = sorted(rs, key=lambda r: r['x0'])
            if l['side'] in ('', 'A') and rr['side'] in ('', 'a'):
                l['side'], rr['side'] = 'A', 'a'
    with open(os.path.join(D, 'work', 'boxes.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print('labelled boxes', len(rows), C.Counter(r['side'] for r in rows).most_common(8))

    icit = [json.loads(l) for l in open(os.path.join(REPO, 'data', 'icit_texts.jsonl'))]
    uni = {}
    for r in icit:
        if r['type'] == 'SEAL:S' and r['symbol'].startswith('Bull1') and r['cisi'] not in ('-', ''):
            uni.setdefault(r['cisi'], r)
    out = []
    seen = set()
    for r in rows:
        if r['cisi'] in uni and r['side'] in ('a', 'A'):
            k = (r['cisi'], r['side'])
            if k in seen:
                continue
            seen.add(k)
            i = uni[r['cisi']]
            out.append(dict(r, site=i['site'], symbol=i['symbol'], width_mm=i['width_mm'], height_mm=i['height_mm'],
                            seq=' '.join(i['seq']), icit_id=i['id']))
    with open(os.path.join(D, 'work', 'unicorn_boxes.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    imp = {r['cisi'] for r in out if r['side'] == 'a'}
    orig = {r['cisi'] for r in out if r['side'] == 'A'}
    print('ICIT unicorn square seals with CISI id:', len(uni), '| impression found', len(imp), '| seal found', len(orig),
          '| both', len(imp & orig))
    print('by site (impression):', C.Counter(uni[c]['site'] for c in imp).most_common())
    ww = np.array([r['x1'] - r['x0'] for r in out if r['side'] == 'a'])
    print('impression box width px: median', np.median(ww), 'IQR', np.percentile(ww, [25, 75]))


if __name__ == '__main__':
    main()
