"""Zero-shot stamp kill test. Prereg docs/prereg/stamp_zeroshot.md. Run with the vision venv:
  .venv-vision/bin/python -I experiments/stamp_detector/zeroshot.py  -> out/zeroshot.json"""
import json
from pathlib import Path
import numpy as np
import torch, open_clip

HERE = Path(__file__).resolve().parent
EMB, OUT = HERE / "raw" / "emb", HERE / "out"
STAMP = ["a photo of a round stamp seal impression pressed into clay",
         "a circular seal impression with carved animal figures on a clay tablet",
         "an oval stamp impression on the edge of a clay tablet"]
OTHER = ["a photo of cuneiform writing on a clay tablet", "a blank smooth clay surface",
         "a rolled cylinder seal impression on a clay tablet", "a museum photo of a black background"]
CTRL = ["YBC5447_yale", "P257839", "P272900", "P257073", "P269244"]


def main():
    model, _, _ = open_clip.create_model_and_transforms("ViT-B-16", pretrained="laion2b_s34b_b88k")
    tok = open_clip.get_tokenizer("ViT-B-16")
    with torch.no_grad():
        T = model.encode_text(tok(STAMP + OTHER)).float()
    T = (T / T.norm(dim=-1, keepdim=True)).numpy()

    def score(stem):
        z = np.load(EMB / f"{stem}.npz"); F = z["feats"].astype(np.float32)
        if not len(F):
            return None, None
        L = 100 * F @ T.T; L -= L.max(1, keepdims=True); P = np.exp(L); P /= P.sum(1, keepdims=True)
        s = P[:, :len(STAMP)].sum(1); i = int(np.argmax(s))
        return float(s[i]), z["xy"][i].tolist()

    split = json.loads((OUT / "split.json").read_text())
    neg = {k: score(k) for k in split["N_early_train"] if (EMB / f"{k}.npz").exists()}
    negs = np.array([v[0] for v in neg.values() if v[0] is not None])
    thr = float(np.quantile(negs, 0.99))
    ctrl = {k: score(k) for k in CTRL}
    res = dict(n_neg=len(negs), thr99=thr,
               controls={k: dict(score=v[0], top_tile_xy_size=v[1], above=v[0] > thr,
                                 rank_frac=float((negs >= v[0]).mean())) for k, v in ctrl.items()},
               neg_top10=sorted(((v[0], k) for k, v in neg.items() if v[0] is not None), reverse=True)[:10])
    (OUT / "zeroshot.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("n_neg", "thr99", "controls")}, indent=1))


if __name__ == "__main__":
    main()
