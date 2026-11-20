"""Tile embeddings for the stamp detector. Run with the vision venv:
  .venv-vision/bin/python -I experiments/stamp_detector/embed.py LIST.txt OUTDIR
LIST.txt holds one image path per line. Writes OUTDIR/<stem>.npz with feats (float16, n_tiles x 512, L2-normalised
CLIP ViT-B-16 laion2b image features) and xy (tile top-left x, y and tile size, in 1600-px-wide space).

Tiling: the image is resized to 1600 px wide. Two scales: 192-px tiles at stride 96 and 320-px tiles at stride 160,
each resized to 224 (done on the GPU by resizing the whole image and unfolding). A tile is kept if >= 50% of its
pixels are foreground (grey > 40 on the black background). The left 8% strip and the bottom 10% band are skipped
(catalogue number, logo, scale bar)."""
import sys
from pathlib import Path
import numpy as np
import torch, open_clip
import torch.nn.functional as Fn
from PIL import Image

W, SCALES = 1600, (192, 320)
MEAN = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1)
STD = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1)


def tiles(path, dev):
    im = Image.open(path).convert("RGB")
    H = round(im.height * W / im.width)
    x = torch.from_numpy(np.array(im)).to(dev).permute(2, 0, 1)[None].float() / 255.0
    x = Fn.interpolate(x, size=(H, W), mode="bilinear", antialias=True, align_corners=False)
    fg = (x.mean(1, keepdim=True) > 40 / 255).float()
    out, xy = [], []
    for t in SCALES:
        f = 224 / t
        h2, w2 = round(H * f), round(W * f)
        xs = Fn.interpolate(x, size=(h2, w2), mode="bilinear", antialias=True, align_corners=False)
        fs = Fn.interpolate(fg, size=(h2, w2), mode="bilinear", antialias=True, align_corners=False)
        p = xs.unfold(2, 224, 112).unfold(3, 224, 112)            # 1,3,ny,nx,224,224
        q = fs.unfold(2, 224, 112).unfold(3, 224, 112).mean((-1, -2))[0, 0]  # ny,nx
        ny, nx = q.shape
        ys = torch.arange(ny, device=dev)[:, None] * 112 / f
        xs_ = torch.arange(nx, device=dev)[None, :] * 112 / f
        keep = (q >= 0.5) & (ys + t <= 0.90 * H) & (xs_ >= 0.08 * W)
        idx = keep.nonzero()
        if len(idx):
            out.append(p[0].permute(1, 2, 0, 3, 4)[idx[:, 0], idx[:, 1]])
            xy += [(int(xs_[0, j]), int(ys[i, 0]), t) for i, j in idx.tolist()]
    T = torch.cat(out) if out else torch.zeros((0, 3, 224, 224), device=dev)
    return (T - MEAN.to(dev)) / STD.to(dev), np.array(xy, dtype=np.int16).reshape(-1, 3)


def main(lst, outdir):
    torch.set_num_threads(2)
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model, _, _ = open_clip.create_model_and_transforms("ViT-B-16", pretrained="laion2b_s34b_b88k")
    model = model.eval().to(dev)
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    paths = [Path(l.strip()) for l in Path(lst).read_text().splitlines() if l.strip()]
    for i, p in enumerate(paths):
        dst = out / f"{p.stem}.npz"
        if dst.exists():
            continue
        try:
            with torch.no_grad():
                ts, xy = tiles(p, dev)
                feats = [Fn.normalize(model.encode_image(ts[k:k + 128]), dim=-1).cpu().numpy().astype(np.float16)
                         for k in range(0, len(ts), 128)]
        except Exception as e:  # noqa: BLE001
            print("bad image", p, e, flush=True); continue
        F = np.concatenate(feats) if feats else np.zeros((0, 512), np.float16)
        np.savez(dst, feats=F, xy=xy)
        if i % 50 == 0:
            print(i, len(paths), p.stem, len(xy), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
