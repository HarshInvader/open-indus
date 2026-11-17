"""Task #20 red team of ivc2tyc. Prereg docs/prereg/redteam_ivc2tyc.md. Data only from raw/ivc2tyc/datasets.
Run: .venv/bin/python -I experiments/redteam_ivc2tyc/run.py"""
import json, os, random
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA

HERE = Path(__file__).resolve().parent
BASE = HERE / "raw" / "ivc2tyc" / "datasets"
TYC = ["ba-shu", "naxi_dongba", "old_naxi", "standard_yi", "yi"]
OTH = ["proto_cuneiform", "proto_elamite"]
ALL = ["indus"] + TYC + OTH
N, R, S = 280, 20, 64
K3 = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

def load(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); im = Image.alpha_composite(bg, im)
    g = np.array(im.convert("L"))
    _, b = cv2.threshold(g, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if b.mean() > 0.5: b = 1 - b  # ink should be the minority
    ys, xs = np.nonzero(b)
    if len(ys) < 5: return None
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = b.shape; m = max(h, w)
    sq = np.zeros((m, m), np.uint8); sq[(m - h) // 2:(m - h) // 2 + h, (m - w) // 2:(m - w) // 2 + w] = b
    return (cv2.resize(sq * 255, (S, S), interpolation=cv2.INTER_AREA) > 127).astype(np.uint8)

def skeleton(b):
    img = b.copy(); sk = np.zeros_like(img)
    while img.any():
        er = cv2.erode(img, K3); op = cv2.dilate(er, K3)
        sk |= (img - op).clip(0, 1).astype(np.uint8); img = er
    return sk

def redraw(b, width):
    sk = skeleton(b); k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (width, width))
    return cv2.dilate(sk, k)

def feats(b):
    sk = skeleton(b); n, _ = cv2.connectedComponents(b)
    return {"ink": float(b.mean()), "stroke_w": float(b.sum() / max(sk.sum(), 1)), "components": n - 1}

def vec(b):
    return cv2.resize(b.astype(np.float32), (32, 32), interpolation=cv2.INTER_AREA).ravel()

def nnsim(E, a, b):
    A = E[a]; B = E[b]
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-9); B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    M = A @ B.T
    return float(M.max(1).mean()), float(A.mean(0) @ B.mean(0) / (np.linalg.norm(A.mean(0)) * np.linalg.norm(B.mean(0)) + 1e-9))

if __name__ == "__main__":
    rng = random.Random(20)
    glyphs = {}
    for s in ALL:
        fs = sorted(f for f in os.listdir(BASE / s) if f.lower().endswith((".png", ".jpg", ".jpeg")))
        out = [load(BASE / s / f) for f in fs]
        glyphs[s] = [g for g in out if g is not None]
        print(s, len(fs), len(glyphs[s]), flush=True)
    # style features on a fixed sample
    style = {}
    for s in ALL:
        smp = rng.sample(glyphs[s], min(N, len(glyphs[s])))
        F = [feats(g) for g in smp]
        style[s] = {k: float(np.median([f[k] for f in F])) for k in F[0]}
    wI = max(3, int(round(style["indus"]["stroke_w"]))) | 1
    print("style", style, "indus width", wI, flush=True)
    res = {"n_loaded": {s: len(glyphs[s]) for s in ALL}, "style_median": style, "indus_width_px": wI}
    conds = {"RAW": {}, "NORM": {}, "THICK": {}}
    for rep in range(R):
        smp = {s: rng.sample(glyphs[s], min(N, len(glyphs[s]))) for s in ALL}
        for cond in conds:
            imgs, lab = [], []
            for s in ALL:
                for g in smp[s]:
                    if cond == "NORM": g = redraw(g, 3)
                    elif cond == "THICK" and s in OTH: g = redraw(g, wI)
                    imgs.append(vec(g)); lab.append(s)
            X = np.array(imgs); lab = np.array(lab)
            E = PCA(50, random_state=rep).fit_transform(X)
            idx = {s: np.where(lab == s)[0] for s in ALL}
            sims = {s: nnsim(E, idx["indus"], idx[s]) for s in ALL if s != "indus"}
            alltyc = np.concatenate([idx[s] for s in TYC]); tyc_sub = np.array(rng.sample(list(alltyc), N))
            sims["TYC_pooled"] = nnsim(E, idx["indus"], tyc_sub)
            conds[cond].setdefault("reps", []).append(sims)
        print("rep", rep, flush=True)
    for cond, d in conds.items():
        reps = d["reps"]
        keys = reps[0].keys()
        nn = {k: [r[k][0] for r in reps] for k in keys}; cen = {k: [r[k][1] for r in reps] for k in keys}
        D = [r["TYC_pooled"][0] - max(r["proto_cuneiform"][0], r["proto_elamite"][0]) for r in reps]
        single = [s for s in keys if s != "TYC_pooled"]
        closest = [max(single, key=lambda s: r[s][0]) for r in reps]
        res[cond] = {"nn_mean": {k: float(np.mean(v)) for k, v in nn.items()},
                     "centroid_mean": {k: float(np.mean(v)) for k, v in cen.items()},
                     "D_tyc_minus_best_bronze": {"mean": float(np.mean(D)), "lo": float(np.percentile(D, 2.5)), "hi": float(np.percentile(D, 97.5))},
                     "closest_single_script_counts": {s: closest.count(s) for s in set(closest)},
                     "rank_nn": sorted(single, key=lambda s: -np.mean(nn[s]))}
    json.dump(res, open(HERE / "results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items()}, indent=1))
