"""Planted known answers on synthetic layouts (prereg §5.1-5.3) for layout_word_division.

Prereg: docs/prereg/layout_word_division.md (SEALED v2, tag `layout_word_division`); this file is hashed under tag
`layout_word_division_code`. Every subcommand checks the prereg, this file and score.py against HASHES.txt (exit 2).
Scoring functions come from score.py in this folder, imported after an explicit `sys.path.insert(0, <this folder>)`
(python -I drops the script folder). Nothing else is imported from here.

Subcommands (repo root; `nice -n 10 .venv/bin/python -I experiments/layout_word_division/synth.py ...`):
  render         §5.1: 400 synthetic lines, each rendered at every delta in {0, 0.03, 0.06, 0.10, 0.20}; truth boxes,
                 labels and PNG images to raw/synth/; the §5.3 measurer set (40 lines) to raw/synth/measurer_set.json.
  check [--f3]   §5.2 with truth boxes: delta = 0 AUC in [0.47, 0.53]; within-line shuffle null rejects at p < 0.01 in
                 no more than 5% of 200 fresh delta = 0 replicates; delta = 0.20 AUC >= 0.80. Spline model, or the F3
                 model with --f3. Writes out/synth_check.json (out/synth_check_f3.json with --f3), aggregates only.

Fixed generator (all seeds fixed):
  * A line has 2-5 words (uniform), each of 1-4 signs (uniform); lines with fewer than 3 signs are redrawn.
  * Sign sizes: each line takes one Dencker face (with >= 5 sign boxes) at random and draws every sign's (width,
    height) from that face's boxes, with replacement, rounded to whole pixels (min 4 px). H = median sign height.
  * Base gap ~ N(0.10, 0.08) x H truncated at -0.15 (rejection sampling). Line-end compression: for gap position
    q = i / (n - 2) among the n - 1 gaps, gaps with q > 0.7 are multiplied by 1 - 0.5 (q - 0.7) / 0.3 (down to 0.5
    at the last gap). A word-boundary gap then gets + delta x H. The same base layout, sizes and glyphs are used at
    every delta, so only the boundary gaps differ. Lines are horizontal (no tilt), signs centred on one baseline.
  * Glyph: 2-6 random wedges (filled triangle head plus a stroke tail; orientations 0, 45, 90, 135 deg, jittered)
    drawn at 4x, cropped to the ink, resized (nearest) to exactly the sign box, so each truth box is tight.
  * Clay: grey 165 plus a linear shading gradient (random direction, +-25 grey levels), ink grey 70 (sd 10),
    Gaussian pixel noise sd 8; margins of 0.6 H.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # explicit: import score.py from this folder (python -I removes it from sys.path)
import score as S  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ME = Path(__file__).resolve()
SCORE = HERE / "score.py"
SYN = S.RAW / "synth"
IMG = SYN / "img"
LINES = SYN / "lines.json"
MEAS = SYN / "measurer_set.json"
N_LINES = 400
DELTAS = (0.0, 0.03, 0.06, 0.10, 0.20)
N_REP = 200
SEED_LAYOUT = 20261125
SEED_RENDER = 20261128
SEED_NULL = 20261200        # replicate r uses layout seed SEED_NULL + r
SEED_NULL_SHUF = 20261500   # replicate r uses shuffle seed SEED_NULL_SHUF + r
N_MEAS = 20                 # per delta in the §5.3 measurer set


def dkey(d):
    return f"{d:.2f}"


def did(d, idx):
    return f"synth.d{int(round(d * 100)):03d}.{idx:03d}"


def size_pool():
    """Per Dencker face, the (w, h) of its sign boxes (sizes only; no spacing is read)."""
    den = S.load_dencker()
    pool = []
    for k in sorted(den["boxes"]):
        wh = [(b["bbox"][2] - b["bbox"][0], b["bbox"][3] - b["bbox"][1]) for b in den["boxes"][k]]
        wh = [(w, h) for w, h in wh if w > 0 and h > 0]
        if len(wh) >= 5:
            pool.append(np.asarray(wh, dtype=float))
    if not pool:
        raise SystemExit("no Dencker face with >= 5 sign boxes found under raw/ds/")
    return pool


def trunc_normal(rng, n, mu=0.10, sd=0.08, lo=-0.15):
    # PREREG-AMBIGUITY: "truncated at -0.15" is read as a truncated normal (rejection sampling), not clipping.
    out = np.empty(n)
    k = 0
    while k < n:
        v = rng.normal(mu, sd, size=2 * (n - k) + 4)
        v = v[v >= lo]
        m = min(len(v), n - k)
        out[k:k + m] = v[:m]
        k += m
    return out


def draw_layout(rng, pool):
    """One base line. PREREG-AMBIGUITY: §5.1 gives word lengths (1-4) but not words per line; 2-5 words, uniform.
    PREREG-AMBIGUITY: "size and aspect statistics of the Dencker boxes" is read as drawing each sign's (w, h) from the
    boxes of one Dencker face per line (keeps one photo scale per line, as in a real line)."""
    while True:
        nw = int(rng.integers(2, 6))
        wl = [int(x) for x in rng.integers(1, 5, size=nw)]
        n = sum(wl)
        if n >= 3:
            break
    face = pool[int(rng.integers(len(pool)))]
    wh = face[rng.integers(len(face), size=n)]
    w = np.maximum(4, np.rint(wh[:, 0])).astype(int)
    h = np.maximum(4, np.rint(wh[:, 1])).astype(int)
    labels = []
    for wi, m in enumerate(wl):
        labels += [False] * (m - 1) + ([True] if wi < nw - 1 else [])
    base = trunc_normal(rng, n - 1)
    q = np.arange(n - 1) / (n - 2)
    # PREREG-AMBIGUITY: "shrinks the last 30% of gaps by up to 50%" = gaps at relative gap position q > 0.7 are
    # scaled linearly from 1 (q = 0.7) to 0.5 (last gap); the compression acts on the base gap, before + delta H.
    comp = np.where(q > 0.7, 1.0 - 0.5 * (q - 0.7) / 0.3, 1.0)
    return {"wl": wl, "n": n, "w": w.tolist(), "h": h.tolist(), "H": float(np.median(h)),
            "base": (base * comp).tolist(), "labels": labels}


def place(lay, delta):
    """Integer truth boxes for one delta. Returns (boxes, W, Hc)."""
    H = lay["H"]
    w, h = lay["w"], lay["h"]
    m = int(math.ceil(0.6 * H))
    hmax = max(h)
    cy = m + hmax / 2.0
    x = float(m)
    boxes = []
    for i in range(lay["n"]):
        x0 = int(round(x))
        y0 = int(round(cy - h[i] / 2.0))
        boxes.append([x0, y0, x0 + w[i], y0 + h[i]])
        if i < lay["n"] - 1:
            x = x0 + w[i] + (lay["base"][i] + delta * (1.0 if lay["labels"][i] else 0.0)) * H
    xmin = min(b[0] for b in boxes)
    if xmin < m:  # never needed unless overlaps run left; keeps every box inside the canvas
        boxes = [[b[0] + (m - xmin), b[1], b[2] + (m - xmin), b[3]] for b in boxes]
    W = max(b[2] for b in boxes) + m
    Hc = int(math.ceil(hmax + 2 * m))
    return boxes, W, Hc


def glyph(rng, w, h):
    """Wedge-cluster mask, tight to its ink, exactly w x h."""
    for _ in range(20):
        Wb, Hb = 4 * w, 4 * h
        im = Image.new("L", (Wb, Hb), 0)
        d = ImageDraw.Draw(im)
        for _k in range(int(rng.integers(2, 7))):
            ang = math.radians(float(rng.choice([0, 45, 90, 135])) + float(rng.normal(0, 8)))
            s = float(rng.uniform(0.25, 0.5)) * min(Wb, Hb)
            L = float(rng.uniform(0.3, 0.9)) * max(Wb, Hb)
            hx, hy = float(rng.uniform(0, Wb)), float(rng.uniform(0, Hb))
            ca, sa = math.cos(ang), math.sin(ang)
            tip = (hx + ca * s, hy + sa * s)
            p1 = (hx - sa * s / 2, hy + ca * s / 2)
            p2 = (hx + sa * s / 2, hy - ca * s / 2)
            d.polygon([p1, p2, tip], fill=255)
            d.line([tip, (hx + ca * L, hy + sa * L)], fill=255, width=max(1, int(s / 5)))
        bb = im.getbbox()
        if bb is not None and bb[2] - bb[0] >= 2 and bb[3] - bb[1] >= 2:
            return np.asarray(im.crop(bb).resize((w, h), Image.NEAREST)) > 0
    return np.ones((h, w), dtype=bool)


def render_line(idx, lay, boxes, W, Hc):
    rg = np.random.default_rng([SEED_RENDER, idx])
    rn = np.random.default_rng([SEED_RENDER, idx, 1])
    a, b = rg.uniform(-1, 1, size=2)
    yy, xx = np.mgrid[0:Hc, 0:W]
    img = 165.0 + 25.0 * (a * (xx / max(1, W - 1) - 0.5) + b * (yy / max(1, Hc - 1) - 0.5))
    for (x0, y0, x1, y1) in boxes:
        mk = glyph(rg, x1 - x0, y1 - y0)
        ink = 70.0 + rg.normal(0, 10, size=mk.shape)
        reg = img[y0:y1, x0:x1]
        reg[mk] = ink[mk]
    img = img + rn.normal(0, 8, size=img.shape)
    return Image.fromarray(np.clip(np.rint(img), 0, 255).astype(np.uint8), mode="L")


def cmd_render(args):
    info = S.seal_check([ME, SCORE])
    IMG.mkdir(parents=True, exist_ok=True)
    pool = size_pool()
    rng = np.random.default_rng(SEED_LAYOUT)
    lays = [draw_layout(rng, pool) for _ in range(N_LINES)]
    out = []
    for idx, lay in enumerate(lays):
        if idx % 20 == 0:
            S.heartbeat("synth_render", idx, N_LINES)
        for d in DELTAS:
            boxes, W, Hc = place(lay, d)
            # the glyphs and noise depend on idx only, so the five deltas differ in the boundary gaps alone
            im = render_line(idx, lay, boxes, W, Hc)
            f = IMG / f"{did(d, idx)}.png"
            im.save(f, format="PNG")
            out.append({"id": did(d, idx), "idx": idx, "delta": d, "delta_key": dkey(d), "file": S.rel_to_root(f),
                        "W": W, "H": Hc, "boxes_T": boxes, "labels": lay["labels"], "wl": lay["wl"], "n": lay["n"]})
    S.heartbeat("synth_render", N_LINES, N_LINES)
    S.write_json(LINES, {"utc": S.utc(), "seal": info, "n_lines": N_LINES, "deltas": list(DELTAS),
                         "seed_layout": SEED_LAYOUT, "seed_render": SEED_RENDER, "lines": out})
    # §5.3 measurer set: base lines ordered by sha256; the first 20 at delta 0.10, the next 20 at delta 0
    # (distinct base lines, so no rater sees one layout twice). PREREG-AMBIGUITY: selection key
    # sha256("layout_word_division:synth:measurer:<idx>"), not stated in §5.3.
    order = sorted(range(N_LINES), key=lambda i: S.hkey(f"layout_word_division:synth:measurer:{i}"))
    pick = [(i, 0.10) for i in order[:N_MEAS]] + [(i, 0.0) for i in order[N_MEAS:2 * N_MEAS]]
    by = {e["id"]: e for e in out}
    ms = [{k: by[did(d, i)][k] for k in ("id", "idx", "delta_key", "file", "W", "H")} for i, d in pick]
    S.write_json(MEAS, {"utc": S.utc(), "seal": info, "lines": ms})
    print(f"rendered {len(out)} images ({N_LINES} lines x {len(DELTAS)} deltas); measurer set {len(ms)}")


def as_score_lines(entries):
    return [{"boxes": {"T": e["boxes_T"]}, "labels": e["labels"], "tablet": e["id"], "cluster": e["id"]}
            for e in entries]


def replicate_lines(r, pool):
    rng = np.random.default_rng(SEED_NULL + r)
    out = []
    for i in range(N_LINES):
        lay = draw_layout(rng, pool)
        boxes, _, _ = place(lay, 0.0)
        out.append({"boxes": {"T": boxes}, "labels": lay["labels"], "tablet": f"r{r}.{i}", "cluster": f"r{r}.{i}"})
    return out


def cmd_check(args):
    info = S.seal_check([ME, SCORE])
    model = "f3" if args.f3 else "spline"
    src = S.read_json(LINES)
    res = {"utc": S.utc(), "seal": info, "model": model, "by_delta": {}}
    for d in DELTAS:
        L = as_score_lines([e for e in src["lines"] if e["delta_key"] == dkey(d)])
        r = S.score_lines(L, "T", model, with_ci=False, with_null=(d == 0.0))
        res["by_delta"][dkey(d)] = {"auc": r.get("auc"), "n_lines": r.get("n_lines"), "n_pairs": r.get("n_pairs"),
                                    "p_null": r.get("p_null"), "fit_converged": (r.get("fit") or {}).get("converged")}
    a0 = res["by_delta"]["0.00"]["auc"]
    a20 = res["by_delta"]["0.20"]["auc"]
    pool = size_pool()
    rej, ps = 0, []
    for r in range(N_REP):
        S.heartbeat(f"synth_null_{model}", r, N_REP)
        sc = S.score_lines(replicate_lines(r, pool), "T", model, with_ci=False, with_null=True,
                           shuf_seed=SEED_NULL_SHUF + r)
        p = sc.get("p_null")
        ps.append(p)
        rej += int(p is not None and p < 0.01)
    S.heartbeat(f"synth_null_{model}", N_REP, N_REP)
    rate = rej / N_REP
    res["null_replicates"] = {"n": N_REP, "n_reject_p_lt_0.01": rej, "rate": rate,
                              "seed_layout": f"{SEED_NULL}+r", "seed_shuffle": f"{SEED_NULL_SHUF}+r",
                              "p_quantiles": [float(np.quantile(ps, q)) for q in (0.01, 0.05, 0.25, 0.5)]}
    res["criteria"] = {"delta0_auc_in_[0.47,0.53]": a0 is not None and 0.47 <= a0 <= 0.53,
                       "null_reject_rate_le_0.05": rate <= 0.05,
                       "delta0.20_auc_ge_0.80": a20 is not None and a20 >= 0.80}
    res["pass"] = all(res["criteria"].values())
    dest = S.OUT / ("synth_check_f3.json" if args.f3 else "synth_check.json")
    S.write_json(dest, res)
    print(json.dumps({"model": model, "by_delta": {k: v["auc"] for k, v in res["by_delta"].items()},
                      "null_rate": rate, "pass": res["pass"]}, indent=1))
    if not res["pass"] and not args.f3:
        print("§5.2 failed under the spline: F3 applies (run `synth.py check --f3`)")


def main():
    ap = argparse.ArgumentParser(description="layout_word_division: synthetic planted answers (§5.1-5.3)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render")
    s = sub.add_parser("check")
    s.add_argument("--f3", action="store_true", help="F3: position-decile fixed effects + last-3-gap indicators")
    args = ap.parse_args()
    {"render": cmd_render, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
