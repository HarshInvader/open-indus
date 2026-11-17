"""Leg 1: is the vessel in tablet scenes the same shape as sign M328?

Run from repo root:
  .venv/bin/python -I experiments/m328_measure/l1_shape.py masks   # crops + masks + contact sheet (inspect first)
  .venv/bin/python -I experiments/m328_measure/l1_shape.py score   # blind scoring on random IDs, then join key
Page images: pdfimages extractions of CISI vol 1 (p*.png) and vol 2 (w*.png) in pages/.
Pre-registration: docs/prereg/m328_measure.md
"""
import json, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PG = os.path.join(HERE, 'pages')
OUT = os.path.join(HERE, 'crops')
os.makedirs(OUT, exist_ok=True)

# (label, role, source)  source = ('page', file, box) or ('draw', sign)
ITEMS = [
    ('S1 H-180 B scene vessel (kneeling scene)', 'target', ('page', 'p245-000.png', (139, 797, 158, 818))),
    ('S2 H-714 A U-object beside figure', 'target', ('page', 'w353-000.png', (132, 532, 159, 573))),
    ('M328 photo H-723 A', 'm328photo', ('page', 'w354-000.png', (494, 1002, 521, 1054))),
    ('M328 photo H-178 A', 'm328photo', ('page', 'p245-000.png', (413, 83, 438, 129))),
    # EXCLUDED before scoring, no usable mask: ('M328 photo M-456 A', 'm328photo', ('page', 'p147-000.png', (673, 786, 703, 866))),
    # EXCLUDED before scoring, no usable mask: ('M328 photo H-697 A', 'm328photo', ('page', 'w351-000.png', (306, 78, 333, 128))),
    # EXCLUDED before scoring, no usable mask: ('M328 photo M-1402 A', 'm328photo', ('page', 'w223-000.png', (239, 391, 262, 445))),
    ('pot H-167', 'pot', ('page', 'p242-000.png', (50, 68, 308, 420))),
    ('pot H-370', 'pot', ('page', 'p269-000.png', (38, 737, 355, 1092))),
    ('pot H-371', 'pot', ('page', 'p270-000.png', (50, 66, 384, 396))),
    ('pot H-372', 'pot', ('page', 'p270-000.png', (45, 628, 288, 858))),
] + [(f'drawing {s}', 'sign', ('draw', s)) for s in
     ['M328', 'M342', 'M340', 'M347', 'M316', 'M319', 'M323', 'M332']]

NPROF = 12
# mask method per relief crop, chosen from mask_diag.png BEFORE scoring (prereg amendment A1)
METHOD = {'S1 H-180 B scene vessel (kneeling scene)': 'blob'}


def load(src):
    if src[0] == 'draw':
        im = Image.open(os.path.join(REPO, 'data', 'sign_images', f'{src[1]}.png')).convert('L')
    else:
        im = Image.open(os.path.join(PG, src[1])).convert('L').crop(src[2])
    return im


def mask_of(im, kind):
    """Revised after inspecting the first contact sheet, BEFORE any scoring (see prereg amendment):
    draw  = black strokes of the drawing;
    pot   = whole vessel photographed on a white page: non-white pixels, largest component, holes filled;
    relief= embossed/incised stroke in a tablet photo: local contrast |smooth - background| (catches both the lit
            and the shadowed flank of a stroke), Otsu threshold, union of non-speck components that do not hug the
            crop border, then convex hull."""
    a = np.asarray(im, dtype=float)
    H, W = a.shape
    if kind == 'draw':
        comp = a < 128
    elif kind == 'pot':
        m = ndimage.gaussian_filter(a, 1.5) < 225
        m = ndimage.binary_opening(m, iterations=2)
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        comp = ndimage.binary_fill_holes(lab == (int(np.argmax(sizes)) + 1))
    elif kind == 'blob':
        # first-pass rule: Otsu on smoothed grey, both polarities, component with least border contact, then largest
        sm = ndimage.gaussian_filter(a, 1.0)
        thr = otsu(sm)
        best = None
        for m in (sm < thr, sm >= thr):
            lab, n = ndimage.label(m)
            for i in range(1, n + 1):
                cm = lab == i
                if cm.sum() < 0.05 * H * W: continue
                border = cm[0].sum() + cm[-1].sum() + cm[:, 0].sum() + cm[:, -1].sum()
                k = (border / (2 * (H + W)), -cm.sum())
                if best is None or k < best[0]: best = (k, cm)
        comp = best[1]
    else:
        g = ndimage.gaussian_filter(a, 0.8)
        bg = ndimage.gaussian_filter(a, max(3.0, min(H, W) / 4))
        e = np.abs(g - bg)
        thr = otsu(e)
        m = e >= thr
        lab, n = ndimage.label(m)
        keep = np.zeros_like(m)
        for i in range(1, n + 1):
            cm = lab == i
            if cm.sum() < 0.03 * H * W: continue
            ys, xs = np.nonzero(cm)
            cy, cx = ys.mean() / H, xs.mean() / W
            if abs(cx - 0.5) > 0.4 or abs(cy - 0.5) > 0.4: continue
            keep |= cm
        comp = keep if keep.any() else m
    ys, xs = np.nonzero(comp)
    pts = np.c_[xs, ys]
    hull = ConvexHull(pts)
    poly = [tuple(map(int, pts[v])) for v in hull.vertices]
    hm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(hm).polygon(poly, fill=255)
    return comp, np.asarray(hm) > 0


def otsu(x):
    hist, edges = np.histogram(x, 64)
    c = (edges[:-1] + edges[1:]) / 2
    best, thr = -1, c[0]
    for k in range(1, 64):
        w0, w1 = hist[:k].sum(), hist[k:].sum()
        if w0 == 0 or w1 == 0: continue
        m0 = (hist[:k] * c[:k]).sum() / w0; m1 = (hist[k:] * c[k:]).sum() / w1
        v = w0 * w1 * (m0 - m1) ** 2
        if v > best: best, thr = v, c[k]
    return thr


def descriptor(hm):
    ys, xs = np.nonzero(hm)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sub = hm[y0:y1 + 1, x0:x1 + 1]
    h, w = sub.shape
    widths = sub.sum(1).astype(float)
    rows = np.linspace(0, h - 1, NPROF).round().astype(int)
    prof = widths[rows] / widths.max()
    return prof, np.log(h / w)


def dist(a, b):
    return float(np.sqrt(np.mean((a[0] - b[0]) ** 2)) + abs(a[1] - b[1]))


def hu(hm):
    m = hm.astype(float); ys, xs = np.mgrid[:m.shape[0], :m.shape[1]]
    m00 = m.sum(); xb = (xs * m).sum() / m00; yb = (ys * m).sum() / m00
    def mu(p, q): return (((xs - xb) ** p) * ((ys - yb) ** q) * m).sum()
    def eta(p, q): return mu(p, q) / m00 ** (1 + (p + q) / 2)
    n20, n02, n11, n30, n03, n21, n12 = eta(2,0), eta(0,2), eta(1,1), eta(3,0), eta(0,3), eta(2,1), eta(1,2)
    h1 = n20 + n02; h2 = (n20 - n02) ** 2 + 4 * n11 ** 2
    h3 = (n30 - 3 * n12) ** 2 + (3 * n21 - n03) ** 2; h4 = (n30 + n12) ** 2 + (n21 + n03) ** 2
    h = np.array([h1, h2, h3, h4])
    return -np.sign(h) * np.log10(np.abs(h) + 1e-30)


def stage_diag():
    rows = []
    for label, role, src in ITEMS:
        if role not in ('target', 'm328photo'): continue
        im = load(src)
        row = [np.asarray(im)]
        for k in ('blob', 'relief'):
            c, h = mask_of(im, k); row += [c * 255, h * 255]
        rows.append((label, row))
    T = 90
    sheet = Image.new('L', (5 * (T + 4) + 260, len(rows) * (T + 4)), 255)
    d = ImageDraw.Draw(sheet)
    for r, (label, row) in enumerate(rows):
        for c, arr in enumerate(row):
            t = ImageOps.contain(Image.fromarray(np.asarray(arr, dtype=np.uint8)), (T, T))
            sheet.paste(t, (c * (T + 4), r * (T + 4)))
        d.text((5 * (T + 4) + 4, r * (T + 4) + 40), label, fill=0)
    sheet.save(os.path.join(HERE, 'mask_diag.png'))


def stage_masks():
    rng = random.Random(20261115)
    ids = [f'X{n:02d}' for n in rng.sample(range(100), len(ITEMS))]
    key = {}
    tiles = []
    for (label, role, src), xid in zip(ITEMS, ids):
        im = load(src)
        comp, hm = mask_of(im, 'draw' if src[0] == 'draw' else ('pot' if role == 'pot' else METHOD.get(label, 'relief')))
        key[xid] = {'label': label, 'role': role}
        Image.fromarray((hm * 255).astype(np.uint8)).save(os.path.join(OUT, f'{xid}_hull.png'))
        im.save(os.path.join(OUT, f'{xid}.png'))
        tiles.append((xid, label, im, comp, hm))
    json.dump(key, open(os.path.join(HERE, 'l1_key.json'), 'w'), indent=1)
    # contact sheet: original | component | hull, labelled
    T = 120
    sheet = Image.new('RGB', (3 * (T + 6) + 250, len(tiles) * (T + 6)), 'white')
    d = ImageDraw.Draw(sheet)
    for r, (xid, label, im, comp, hm) in enumerate(tiles):
        y = r * (T + 6)
        for c, arr in enumerate([np.asarray(im), comp * 255, hm * 255]):
            t = Image.fromarray(np.asarray(arr, dtype=np.uint8)).convert('L')
            t = ImageOps.contain(t, (T, T), Image.NEAREST if c else Image.LANCZOS)
            sheet.paste(t, (c * (T + 6), y))
        d.text((3 * (T + 6) + 4, y + T // 2), f'{xid}  {label}', fill='black')
    sheet.save(os.path.join(HERE, 'contact_sheet.png'))
    print('wrote contact_sheet.png;', len(tiles), 'items')


def stage_score():
    key = json.load(open(os.path.join(HERE, 'l1_key.json')))
    # blind phase: only IDs and roles needed for lineup membership are hidden behind IDs;
    # the lineup = the 8 drawing IDs, queries = all non-drawing IDs.
    D = {xid: descriptor(np.asarray(Image.open(os.path.join(OUT, f'{xid}_hull.png'))) > 0) for xid in key}
    HU = {xid: hu(np.asarray(Image.open(os.path.join(OUT, f'{xid}_hull.png'))) > 0) for xid in key}
    lineup = sorted(x for x in key if key[x]['role'] == 'sign')
    queries = sorted(x for x in key if key[x]['role'] != 'sign')
    ranks = {}
    for q in queries:
        order = sorted(lineup, key=lambda s: dist(D[q], D[s]))
        order_hu = sorted(lineup, key=lambda s: float(np.linalg.norm(HU[q] - HU[s])))
        ranks[q] = {'order': order, 'd': {s: dist(D[q], D[s]) for s in lineup}, 'order_hu': order_hu}
    # unblind
    m328 = [x for x in lineup if key[x]['label'] == 'drawing M328'][0]
    res = {'items': {}, 'tests': {}}
    for q in queries:
        lab = key[q]['label']
        r = ranks[q]['order'].index(m328) + 1
        rh = ranks[q]['order_hu'].index(m328) + 1
        res['items'][lab] = {'id': q, 'role': key[q]['role'], 'rank_M328': r, 'rank_M328_hu': rh,
                             'd_M328': round(ranks[q]['d'][m328], 4),
                             'nearest': key[ranks[q]['order'][0]]['label'].replace('drawing ', ''),
                             'order': [key[s]['label'].replace('drawing ', '') for s in ranks[q]['order']],
                             'profile': [round(v, 3) for v in D[q][0]], 'log_aspect': round(float(D[q][1]), 3)}
    photos = [l for l in res['items'] if res['items'][l]['role'] == 'm328photo']
    pc_hits = sum(res['items'][l]['rank_M328'] == 1 for l in photos)
    from scipy.stats import binom
    res['tests']['PC'] = {'hits': pc_hits, 'n': len(photos), 'p_chance': float(binom.sf(pc_hits - 1, len(photos), 1 / 8)),
                          'pass': pc_hits == len(photos)}  # amendment A1: all retained photos
    thr = max(res['items'][l]['d_M328'] for l in photos)
    s1 = [l for l in res['items'] if l.startswith('S1')][0]
    s2 = [l for l in res['items'] if l.startswith('S2')][0]
    res['tests']['L1a'] = {'S1_rank': res['items'][s1]['rank_M328'], 'S2_rank': res['items'][s2]['rank_M328'],
                           'pass': res['items'][s1]['rank_M328'] == 1}
    res['tests']['L1b'] = {'threshold_max_photo_d': thr, 'S1_d': res['items'][s1]['d_M328'],
                           'S2_d': res['items'][s2]['d_M328'], 'pass': res['items'][s1]['d_M328'] <= thr}
    # L1c: nearest among pots + drawings + photos for each target
    pool = [x for x in key if key[x]['role'] in ('pot', 'sign', 'm328photo')]
    for lab in (s1, s2):
        q = res['items'][lab]['id']
        nn = sorted(pool, key=lambda s: dist(D[q], D[s]))
        res['tests'].setdefault('L1c', {})[lab] = [(key[s]['label'], round(dist(D[q], D[s]), 3)) for s in nn]
    # pots vs M328 drawing (descriptive)
    res['tests']['pots_vs_M328'] = {l: (res['items'][l]['rank_M328'], res['items'][l]['d_M328'])
                                    for l in res['items'] if res['items'][l]['role'] == 'pot'}
    pc, a, b = res['tests']['PC']['pass'], res['tests']['L1a']['pass'], res['tests']['L1b']['pass']
    if not pc: verdict = 'inconclusive (positive control failed: method cannot recognise M328 in photos)'
    elif a and b: verdict = 'supported'
    elif res['tests']['L1a']['S1_rank'] >= 4 or not b: verdict = 'refuted'
    else: verdict = 'inconclusive'
    res['verdict'] = verdict
    json.dump(res, open(os.path.join(HERE, 'l1_results.json'), 'w'), indent=1)
    for l, v in res['items'].items():
        print(f"{l:45s} rank(M328)={v['rank_M328']} hu={v['rank_M328_hu']} d={v['d_M328']:.3f} nearest={v['nearest']}")
    print(json.dumps({k: v for k, v in res['tests'].items() if k != 'L1c'}, indent=1))
    for lab in (s1, s2): print(lab, res['tests']['L1c'][lab][:5])
    print('VERDICT Leg 1:', verdict)


if __name__ == '__main__':
    {'masks': stage_masks, 'score': stage_score, 'diag': stage_diag}[sys.argv[1]]()
