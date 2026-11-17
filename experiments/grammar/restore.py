"""Propose top-5 fillers for missing signs in a broken Indus text, using the positional class grammar.

Usage (reading order, signs separated by spaces):
    .venv/bin/python experiments/grammar/restore.py "M267 M99 ? M342"
    .venv/bin/python experiments/grammar/restore.py "# M59 ? M342"            # '#' at an edge = broken edge
    .venv/bin/python experiments/grammar/restore.py "W817 W002 ? W740" --list wells
    .venv/bin/python experiments/grammar/restore.py "M267 ? ? M342" --top 8 --register sealing

'?' is exactly one missing sign. A leading/trailing '#' means the text is broken there (no start/end
of text is assumed on that side). Several '?' are handled jointly (forward-backward over classes);
the output gives each gap's own top fillers (marginals). Signs unknown to the grammar count as <UNK>.
Fillers are ranked by P(sign | rest of text); class = fine class and its functional label.
This proposes structurally likely signs. It says nothing about sound or meaning.
"""
import argparse, json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def load(sign_list, register=None):
    if sign_list == "m77":
        g = json.load(open(HERE / "grammar.json"))
        words = []; cls = []; emit = []
        for c in g["classes"]:
            for w, p in c["emissions"].items():
                words.append(w); cls.append(c["id"]); emit.append(p)
        T = np.array(g["transitions"]["P"])
        if register and register in g["registers"]["T"]:
            T = np.array(g["registers"]["T"][register])
        labels = [c["label"] for c in g["classes"]]
        final = {k: v["final_class"] for k, v in g["sign_classes"].items()}
        return words, np.array(cls), np.array(emit), T, labels, final, g["K"]
    g = json.load(open(HERE / "classes_wells.json"))
    K = g["K"]
    words = g["words"]; cls = np.array(g["cls"]); emit = np.array(g["emit"])
    final = {k: v["label"] for k, v in g["signs"].items()}
    return words, cls, emit, np.array(g["T"]), g["class_labels"], final, K


def restore(text, sign_list="m77", top=5, register=None):
    words, cls, emit, T, labels, final, K = load(sign_list, register)
    widx = {w: i for i, w in enumerate(words)}
    toks = text.split()
    bos = not (toks and toks[0] == "#")
    eos = not (toks and toks[-1] == "#")
    toks = [t for t in toks if t != "#"]
    if "#" in toks:
        raise SystemExit("'#' is only allowed at the edges; use '?' for each missing sign inside")
    n = len(toks)
    # per-position class likelihood vectors
    L = np.zeros((n, K))
    for j, t in enumerate(toks):
        if t == "?":
            L[j] = 1.0                     # sum over all signs of a class = 1
        else:
            i = widx.get(t, widx.get("<UNK>"))
            L[j, cls[i]] = emit[i]
    start = T[K, :K] if bos else np.full(K, 1.0 / K)     # broken start: no start-of-text constraint
    end = T[:K, K] if eos else np.ones(K)
    A = T[:K, :K]
    alpha = np.zeros((n, K)); beta = np.zeros((n, K))
    alpha[0] = start * L[0]; alpha[0] /= alpha[0].sum()
    for j in range(1, n):
        alpha[j] = (alpha[j - 1] @ A) * L[j]; alpha[j] /= alpha[j].sum()
    beta[-1] = end
    for j in range(n - 2, -1, -1):
        beta[j] = A @ (L[j + 1] * beta[j + 1]); beta[j] /= beta[j].sum()
    out = []
    for j, t in enumerate(toks):
        if t != "?":
            continue
        pc = alpha[j] * beta[j]; pc /= pc.sum()
        pw = pc[cls] * emit
        pw[[i for i, w in enumerate(words) if w == "<UNK>"]] = 0     # a rare/unseen sign is not a proposal
        pw /= pw.sum()
        order = np.argsort(-pw)[:top]
        cands = [dict(sign=words[i], p=float(pw[i]), fine_class=int(cls[i]), class_label=labels[cls[i]],
                      validated_class=final.get(words[i], "")) for i in order]
        lab = {}
        for c in range(K):
            lab[labels[c]] = lab.get(labels[c], 0) + float(pc[c])
        out.append(dict(position=j + 1, candidates=cands, label_posterior=dict(sorted(lab.items(), key=lambda kv: -kv[1]))))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text")
    ap.add_argument("--list", default="m77", choices=["m77", "wells"])
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--register", default=None, help="seal | sealing | tablet | copper | pottery | other (M77 only)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = restore(a.text, a.list, a.top, a.register)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        if not res:
            print("no '?' in the text: nothing to restore")
        for g in res:
            lp = ", ".join(f"{k} {v:.2f}" for k, v in list(g["label_posterior"].items())[:3])
            print(f"gap at position {g['position']}  (slot: {lp})")
            for k, c in enumerate(g["candidates"], 1):
                print(f"  {k}. {c['sign']:6s} p={c['p']:.3f}  class c{c['fine_class']} ({c['class_label']}; validated: {c['validated_class'] or '-'})")
