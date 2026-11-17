"""Planted corpora in a simulated logo-syllabic script."""
import numpy as np
from names import write_cv

N_FRAME, N_LOGO = 12, 40


def zipf_p(n, a=1.0):
    w = 1.0 / np.arange(1, n + 1) ** a
    return w / w.sum()


def make_corpus(n, name_units, name_w, values, script, rng, p_name=0.75, misread=0.2,
                kmax=5, sign_perm_seed=None):
    """Return dict(texts, true_key (sign->value id, -1 for logograms), nsigns, name_text flags).
    Sign ids: syllable values occupy a random permutation of ids [0, nv); frame signs and
    logograms follow.  name_units: list of unit tuples; name_w: sampling weights."""
    nv = len(values); vid = {v: i for i, v in enumerate(values)}
    perm = rng.permutation(nv)                        # value i -> sign perm[i]
    nsigns = nv + N_FRAME + N_LOGO
    true_key = -np.ones(nsigns, dtype=np.int32)
    true_key[perm] = np.arange(nv)
    frame = nv + np.arange(N_FRAME); logo = nv + N_FRAME + np.arange(N_LOGO)
    pf, pl = zipf_p(N_FRAME), zipf_p(N_LOGO)
    pw = np.asarray(name_w, float); pw /= pw.sum()
    texts, flags = [], []
    while len(texts) < n:
        if rng.random() < p_name:
            u = name_units[rng.choice(len(name_units), p=pw)]
            sp = write_cv(u, rng) if script == "A" else tuple(u)
            if sp is None or not (2 <= len(sp) <= kmax) or any(x not in vid for x in sp):
                continue
            body = [int(perm[vid[x]]) for x in sp]
            body = [int(rng.integers(nsigns)) if rng.random() < misread else s for s in body]
            nf = rng.choice(3, p=[0.3, 0.45, 0.25])
            while len(body) + nf < 3:
                nf += 1
            nf = min(nf, 6 - len(body))
            fr = [int(x) for x in rng.choice(frame, size=nf, p=pf)]
            nb = int(rng.integers(nf + 1))                # frames before / after
            t = fr[:nb] + body + fr[nb:]
            flags.append(True)
        else:
            L = int(rng.integers(3, 7))
            t = [int(x) for x in rng.choice(np.concatenate([frame, logo]), size=L,
                                            p=np.concatenate([pf, pl]) / 2)]
            flags.append(False)
        texts.append(t)
    return dict(texts=texts, true_key=true_key, nsigns=nsigns, name_text=flags)


def shuffle_texts(texts, rng):
    toks = np.concatenate([np.asarray(t) for t in texts]); rng.shuffle(toks)
    out, i = [], 0
    for t in texts:
        out.append(toks[i:i + len(t)].tolist()); i += len(t)
    return out
