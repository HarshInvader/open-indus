"""Stage 0 role induction: Baum-Welch HMM over the 9 SIGIL roles with transitions masked to the SIGIL template,
then one hard role per sign type (majority posterior). Used to initialise the strict-parse fit in run.py."""
import numpy as np


def hmm_roles(texts, roles, allowed, init_role, iters=40, seed=0):
    rng = np.random.default_rng(seed)
    S = ["<s>"] + roles; K = len(roles); ri = {r: i for i, r in enumerate(roles)}
    vocab = sorted({s for t in texts for s in t}); vi = {s: i for i, s in enumerate(vocab)}; V = len(vocab)
    mask = np.array([[b in allowed.get(a, ()) for b in roles] for a in roles], float)
    start_mask = np.array([b in allowed["<s>"] for b in roles], float)
    end_mask = np.array(["</s>" in allowed.get(a, ()) for a in roles], float)
    A = mask * (1 + 0.1 * rng.random(mask.shape)); A /= A.sum(1, keepdims=True) + 1e-12
    pi = start_mask / start_mask.sum(); end = end_mask * 0.5
    B = np.full((K, V), 0.1)
    for s, r in init_role.items(): B[ri[r], vi[s]] += 3.0
    B /= B.sum(1, keepdims=True)
    X = [np.array([vi[s] for s in t]) for t in texts]
    for _ in range(iters):
        An = np.zeros((K, K)); Bn = np.full((K, V), 1e-3); pin = np.zeros(K); endn = np.zeros(K); occ = np.zeros(K)
        for x in X:
            T = len(x); al = np.zeros((T, K)); be = np.zeros((T, K)); c = np.zeros(T)
            al[0] = pi * B[:, x[0]]; c[0] = al[0].sum() + 1e-300; al[0] /= c[0]
            for t in range(1, T):
                al[t] = (al[t - 1] @ A) * B[:, x[t]]; c[t] = al[t].sum() + 1e-300; al[t] /= c[t]
            be[-1] = end
            for t in range(T - 2, -1, -1):
                be[t] = (A @ (B[:, x[t + 1]] * be[t + 1])) / c[t + 1]
            g = al * be; z = g.sum(1, keepdims=True) + 1e-300; g /= z
            pin += g[0]; endn += g[-1]
            for t in range(T - 1):
                xi = al[t][:, None] * A * (B[:, x[t + 1]] * be[t + 1])[None, :]; An += xi / (xi.sum() + 1e-300)
            for t in range(T):
                Bn[:, x[t]] += g[t]
            occ += g.sum(0)
        A = An * mask + 1e-6 * mask; A /= A.sum(1, keepdims=True)
        pi = (pin + 1e-6) * start_mask; pi /= pi.sum()
        end = np.clip(endn / (occ + 1e-9), 0, 1) * end_mask
        B = Bn / Bn.sum(1, keepdims=True)
    # hard role: majority posterior over tokens of each sign type (from the last E-step)
    post = Bn - 1e-3
    return {s: roles[int(post[:, vi[s]].argmax())] for s in vocab}
