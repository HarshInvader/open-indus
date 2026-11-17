"""C2: carving-style features from the ANIMAL motif only, validation, and the frozen 'hand' clustering.

Motif crop: lower part of each photographed box (y from 42% to 100%; the text band sits on top on
unicorn seals). Seals whose ICIT text has more than one line are excluded so that text rarely enters
the crop. Features (flip-symmetrised so facing direction does not matter):
  HOG (cv2, unsigned gradients) on a CLAHE-normalised 128x72 crop  -> shape/pose/hatching orientation
  Gabor energy (4 orientations x 2 scales) on a 4x3 grid         -> hatching texture by body zone
  high-frequency share of the head/neck third                      -> 'hatched neck/face' index
Validation (none of it uses the text):
  V1 identity: retrieve the seal photo (A, mirrored) from its own impression (a) among all A photos.
  V2 annotation: predict ICIT's unicorn style letter (Bull1:W/J/S/...; a human motif coding) by CV
     logistic regression; null = letters permuted within site x CISI size group.
  V3 CISI order: within (vol, site, size group) CISI arranges unicorns by Rissman's collar ->
     hatched neck -> hatched face scheme; Spearman of CV-predicted vs actual within-group rank.
  Proxy check: how much of the feature space is explained by site, size, photo brightness/contrast.
Clustering (frozen before any text is looked at): features residualised on site, log size and photo
brightness/contrast/box width; PCA 20; KMeans K in 3..10 by best silhouette; seeds fixed.
Outputs: work/features.npz, clusters.csv (frozen), validation.json
Run: .venv/bin/python -I experiments/carver_hands/c2_features.py
"""
import os, csv, json, math, collections as C
import numpy as np
import cv2
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold, cross_val_predict
from sklearn.metrics import balanced_accuracy_score, silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from sklearn.cluster import KMeans
from scipy.stats import spearmanr

D = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20261115)
W, H = 128, 72


def hog(im, cell=8, nb=9):
    """numpy HOG: unsigned gradients, 9 bins, 8x8 cells, 2x2-cell blocks, L2-Hys."""
    f = im.astype(np.float32)
    gx = cv2.Sobel(f, cv2.CV_32F, 1, 0, ksize=1); gy = cv2.Sobel(f, cv2.CV_32F, 0, 1, ksize=1)
    mag = np.hypot(gx, gy); ang = (np.degrees(np.arctan2(gy, gx)) % 180) / (180 / nb)
    b0 = np.floor(ang).astype(int) % nb; w1 = ang - np.floor(ang); b1 = (b0 + 1) % nb
    ch, cw = im.shape[0] // cell, im.shape[1] // cell
    hist = np.zeros((ch, cw, nb), np.float32)
    ci = (np.arange(im.shape[0]) // cell)[:, None].repeat(im.shape[1], 1)
    cj = (np.arange(im.shape[1]) // cell)[None, :].repeat(im.shape[0], 0)
    m = (ci < ch) & (cj < cw)
    np.add.at(hist, (ci[m], cj[m], b0[m]), (mag * (1 - w1))[m])
    np.add.at(hist, (ci[m], cj[m], b1[m]), (mag * w1)[m])
    out = []
    for i in range(ch - 1):
        for j in range(cw - 1):
            v = hist[i:i + 2, j:j + 2].ravel(); v = v / (np.linalg.norm(v) + 1e-6)
            v = np.minimum(v, 0.2); out.append(v / (np.linalg.norm(v) + 1e-6))
    return np.concatenate(out)

CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
GAB = [cv2.getGaborKernel((11, 11), s, th, lam, 0.5, 0) for (s, lam) in [(2.0, 4.0), (3.0, 7.0)]
       for th in np.arange(4) * np.pi / 4]


def size_group(w):
    w = float(w or 0)
    if w <= 0: return 'NA'
    for g, lo in [('I', 43.5), ('II', 35), ('III', 29), ('IV', 23), ('V', 17.5)]:
        if w >= lo: return g
    return 'VI'


def crop(r):
    im = Image.open(os.path.join(D, 'work', 'pages', r['file'])).convert('L')
    x0, y0, x1, y1 = (int(r[k]) for k in ('x0', 'y0', 'x1', 'y1'))
    y0 = int(y0 + 0.42 * (y1 - y0))
    a = np.asarray(im.crop((x0, y0, x1, y1)))
    return a


def feats_one(a):
    g = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    g = CLAHE.apply(g)
    out = []
    for im in (g, g[:, ::-1].copy()):
        hg = hog(im)
        f = im.astype(np.float32) / 255
        gab = []
        for k in GAB:
            e = np.abs(cv2.filter2D(f, -1, k))
            for i in range(3):
                for j in range(4):
                    gab.append(e[i * H // 3:(i + 1) * H // 3, j * W // 4:(j + 1) * W // 4].mean())
        out.append(np.concatenate([hg, np.array(gab)]))
    v = (out[0] + out[1]) / 2
    # hatching index: high-frequency share in the head/neck third (whichever end is more textured)
    f = g.astype(np.float32)
    hp = f - cv2.GaussianBlur(f, (0, 0), 2.0)
    hf = [np.abs(hp[:, :W // 3]).mean(), np.abs(hp[:, -W // 3:]).mean()]
    hatch = max(hf) / (np.abs(hp).mean() + 1e-6)
    photo = [a.mean(), a.std(), a.shape[1]]
    return v, hatch, photo


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(D, 'work', 'unicorn_boxes.csv')))]
    keep = [r for r in rows if '|' not in r['seq'] and float(r['width_mm'] or 0) > 0]
    print('boxes', len(rows), 'single-line with size', len(keep))
    X, HT, PH, meta = [], [], [], []
    for r in keep:
        a = crop(r)
        if min(a.shape) < 30:
            continue
        v, h, p = feats_one(a)
        X.append(v); HT.append(h); PH.append(p); meta.append(r)
    X = np.array(X); HT = np.array(HT); PH = np.array(PH)
    side = np.array([m['side'] for m in meta]); cisi = np.array([m['cisi'] for m in meta])
    Xs = StandardScaler().fit_transform(np.column_stack([X, HT]))
    val = {}

    # ---- V1 identity retrieval: impression a vs seal photo A of the same object ----
    ia = np.where(side == 'a')[0]; iA = np.where(side == 'A')[0]
    Apos = {cisi[i]: i for i in iA}
    pairs = [(i, Apos[cisi[i]]) for i in ia if cisi[i] in Apos]
    Z = PCA(40, random_state=0).fit_transform(Xs)
    Zn = Z / np.linalg.norm(Z, axis=1, keepdims=True)
    ranks = []
    for i, j in pairs:
        sims = Zn[iA] @ Zn[i]
        ranks.append(int((sims > Zn[j] @ Zn[i]).sum()) + 1)
    ranks = np.array(ranks); nA = len(iA)
    null_med = []
    for _ in range(2000):
        null_med.append(np.median(RNG.integers(1, nA + 1, len(ranks))))
    val['V1_identity'] = dict(pairs=len(pairs), candidates=int(nA), median_rank=float(np.median(ranks)),
                              chance_median=(nA + 1) / 2, top1=int((ranks == 1).sum()), top10=int((ranks <= 10).sum()),
                              top10_chance=len(pairs) * 10 / nA,
                              p_median=float((np.array(null_med) <= np.median(ranks)).mean()))
    print('V1', val['V1_identity'])

    # analysis set for everything else: impressions (a); add seal photos only when no impression
    have_a = set(cisi[ia])
    use = np.array([s == 'a' or (s == 'A' and c not in have_a) for s, c in zip(side, cisi)])
    M = [m for m, u in zip(meta, use) if u]
    Xu = Xs[use]; PHu = PH[use]; HTu = HT[use]
    site = np.array([m['site'] for m in M]); sg = np.array([size_group(m['width_mm']) for m in M])
    logw = np.log(np.array([float(m['width_mm']) for m in M]))
    letter = np.array([m['symbol'].split(':')[1] if ':' in m['symbol'] else '' for m in M])
    strata = np.array([f'{a}|{b}' for a, b in zip(site, sg)])
    print('analysis seals', len(M), C.Counter(site).most_common(4))

    # ---- proxy check: variance explained by site/size/photo ----
    Zu = PCA(20, random_state=0).fit_transform(Xu)
    Dm = np.column_stack([np.eye(len(set(site)))[np.unique(site, return_inverse=True)[1]], logw,
                          (PHu - PHu.mean(0)) / PHu.std(0), (side[use] == 'A').astype(float)])
    beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(M)), Dm]), Zu, rcond=None)
    fit = np.column_stack([np.ones(len(M)), Dm]) @ beta
    r2 = 1 - ((Zu - fit) ** 2).sum() / ((Zu - Zu.mean(0)) ** 2).sum()
    val['proxy_R2_site_size_photo'] = float(r2)
    print('R2 of PCA20 features on site+size+photo', round(r2, 3))

    # ---- V2 predict ICIT style letter ----
    ok = np.isin(letter, [l for l, n in C.Counter(letter).items() if n >= 15 and l])
    y = letter[ok]; Xv = Zu[ok]
    def cvba(yy, seed=0):
        skf = StratifiedKFold(5, shuffle=True, random_state=seed)
        pr = cross_val_predict(LogisticRegression(max_iter=2000, C=0.1, class_weight='balanced'), Xv, yy, cv=skf)
        return balanced_accuracy_score(yy, pr)
    ba = cvba(y)
    st = strata[ok]
    nulls = []
    for k in range(200):
        yp = y.copy()
        for s in set(st):
            ii = np.where(st == s)[0]; yp[ii] = yp[RNG.permutation(ii)]
        nulls.append(cvba(yp, k))
    nulls = np.array(nulls)
    # baseline using only site+size+photo (to show the letter signal is not a proxy)
    Xb = np.column_stack([Dm[ok]])
    pr = cross_val_predict(LogisticRegression(max_iter=2000, C=0.1, class_weight='balanced'), Xb, y,
                           cv=StratifiedKFold(5, shuffle=True, random_state=0))
    val['V2_style_letter'] = dict(n=int(ok.sum()), classes=dict(C.Counter(y)), balanced_acc=float(ba),
                                  null_mean=float(nulls.mean()), null_95=float(np.percentile(nulls, 95)),
                                  p=float((nulls >= ba).mean() + 1 / len(nulls)),
                                  proxy_only_balanced_acc=float(balanced_accuracy_score(y, pr)))
    print('V2', val['V2_style_letter'])

    # ---- V3 CISI within-size-group order (Rissman collar -> hatched neck -> hatched face) ----
    vol = np.array([m['vol'] for m in M]); pg = np.array([int(m['page']) for m in M])
    pos = np.array([int(m['page']) * 10000 + int(m['y0']) // 60 * 100 + int(m['x0']) // 60 for m in M])
    grp = np.array([f'{a}|{b}|{c}' for a, b, c in zip(vol, site, sg)])
    rk = np.full(len(M), np.nan)
    for g in set(grp):
        ii = np.where(grp == g)[0]
        if len(ii) >= 12:
            rk[ii] = (np.argsort(np.argsort(pos[ii])) + 0.5) / len(ii)
    okr = ~np.isnan(rk)
    pr = cross_val_predict(Ridge(alpha=10.0), np.column_stack([Zu[okr], HTu[okr]]), rk[okr],
                           cv=KFold(5, shuffle=True, random_state=0))
    rho = spearmanr(pr, rk[okr]).statistic
    hrho = spearmanr(HTu[okr], rk[okr]).statistic
    nr = []
    gg = grp[okr]
    for k in range(500):
        rp = rk[okr].copy()
        for g in set(gg):
            ii = np.where(gg == g)[0]; rp[ii] = rp[RNG.permutation(ii)]
        p2 = cross_val_predict(Ridge(alpha=10.0), np.column_stack([Zu[okr], HTu[okr]]), rp,
                               cv=KFold(5, shuffle=True, random_state=k))
        nr.append(spearmanr(p2, rp).statistic)
    nr = np.array(nr)
    val['V3_cisi_order'] = dict(n=int(okr.sum()), groups=int(len(set(gg))), rho=float(rho),
                                null_95=float(np.percentile(nr, 95)), p=float((nr >= rho).mean() + 1 / len(nr)),
                                hatch_index_rho=float(hrho))
    print('V3', val['V3_cisi_order'])

    # ---- frozen clustering on residualised features ----
    R = Zu - fit
    R = StandardScaler().fit_transform(R)
    best = None; sil = {}
    for K in range(3, 11):
        lab = KMeans(K, n_init=20, random_state=0).fit_predict(R)
        s = silhouette_score(R, lab); sil[K] = float(s)
        if best is None or s > best[0]:
            best = (s, K, lab)
    s, K, lab = best
    # stability: ARI across 10 bootstrap re-fits (on the common items)
    aris = []
    for b in range(10):
        ii = RNG.choice(len(R), len(R), replace=True)
        km = KMeans(K, n_init=10, random_state=b).fit(R[ii])
        aris.append(adjusted_rand_score(lab, km.predict(R)))
    val['clustering'] = dict(K=int(K), silhouette=sil, sizes=dict(C.Counter(lab.tolist())),
                             bootstrap_ARI_mean=float(np.mean(aris)),
                             NMI_site=float(normalized_mutual_info_score(site, lab)),
                             NMI_sizegroup=float(normalized_mutual_info_score(sg, lab)),
                             NMI_letter=float(normalized_mutual_info_score(letter, lab)))
    print('clustering', val['clustering'])
    with open(os.path.join(D, 'clusters.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['cisi', 'icit_id', 'site', 'size_group', 'width_mm', 'photo_side', 'cluster'])
        for m, g, l in zip(M, sg, lab):
            w.writerow([m['cisi'], m['icit_id'], m['site'], g, m['width_mm'], m['side'], int(l)])
    json.dump(val, open(os.path.join(D, 'validation.json'), 'w'), indent=1)
    np.savez_compressed(os.path.join(D, 'work', 'features.npz'), X=Xu, Z=Zu, R=R, hatch=HTu)


if __name__ == '__main__':
    main()
