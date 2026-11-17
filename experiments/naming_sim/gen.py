"""Parametric name generator, fitted to each real onomasticon, then sampled at Indus size / frequency profile.

Generator G(theta), theta =
  p1, p2            length distribution (rest = 3; 4 for mixtec-like via p4 share of the rest, fixed 0.3 of 3+)
  zipf, V           element inventory: V elements, frequency ~ rank^-zipf
  conc              slot polarisation: each element has first-slot propensity pi_e ~ Beta(conc*m, conc*(1-m)),
                    with m = 0.5 + rho*(standardised log-frequency rank)/2 clipped to [.05,.95]
                    (small conc -> pi near 0/1 = two stocks; large conc -> pi ~ m = one stock)
  rho               head rule: frequent elements lean to position 2 (rho>0, head-final) or 1 (rho<0)
  q                 one-element names drawn from the compounding stock with prob q, else from a separate
                    stock (hypocoristics / monothematic names) never used in compounds
  lam               lexicalisation: each unordered pair has one canonical order (drawn once by pi odds) used
                    with prob lam; otherwise the order is drawn afresh by pi odds for each name
  csh, kappa        lexical class: elements of total token share csh form a class; after a class element,
                    class partners are up-weighted by kappa (self-compounding)
Slot-aware drawing: position 1 ~ freq * pi, last position ~ freq * (1 - pi), middle ~ freq * 2 sqrt(pi(1-pi));
a class element up-weights class partners (kappa) for the next position. Lexicalisation: with prob lam a
name keeps every adjacent pair in the order first generated (canonical order; L>=3 resampled up to 6 times).
vm: size of the separate monothematic stock relative to V.
Sampling produces exactly n distinct types.
"""
import numpy as np

PARAMS = ["p1", "p2", "zipf", "V", "conc", "rho", "q", "vm", "lam", "csh", "kappa"]
STRUCT = ["p1", "p2", "conc", "rho", "q", "vm", "lam", "csh", "kappa"]     # structural (system) parameters
BOUNDS = dict(V=(40.0, 4000.0), p1=(0.0, 0.7), p2=(0.0, 1.0), zipf=(0.5, 1.4), conc=(0.2, 60.0), rho=(-1.0, 1.0), q=(0.0, 1.0),
              lam=(0.0, 1.0), csh=(0.0, 0.25), kappa=(1.0, 12.0), vm=(0.1, 20.0))
LOG = {"conc", "kappa", "V", "vm"}


def sample(theta, n, rng, V=None):
    t = dict(theta)
    V = int(V or t.get("V", 300))
    r = np.arange(1, V + 1)
    f = r ** -t["zipf"]; f /= f.sum()
    z = (np.log(r) - np.log(r).mean()) / np.log(r).std()
    # head-final (rho>0): frequent elements (z small) go second -> low first-slot propensity
    m = np.clip(0.5 + t["rho"] * z / 2, 0.05, 0.95)
    c = t["conc"]
    pi = rng.beta(c * m, c * (1 - m))
    pi = np.clip(pi, 1e-3, 1 - 1e-3)
    # class: random elements until token share csh
    cls = np.zeros(V, bool)
    if t["csh"] > 0:
        order = rng.permutation(V)
        acc = 0
        for e in order[V // 20:]:          # skip nothing systematic; random members
            if acc >= t["csh"]:
                break
            cls[e] = True; acc += f[e]
    wpos = {"F": f * pi, "L": f * (1 - pi), "M": f * 2 * np.sqrt(pi * (1 - pi))}
    canon = {}
    Vm = max(5, int(round(V * t.get("vm", 1.0))))      # monothematic stock size (relative to V)
    fm = np.arange(1, Vm + 1) ** -t["zipf"]; fm /= fm.sum()
    p1, p2 = t["p1"], min(t["p2"], 1 - t["p1"])
    out = set()
    tries = 0
    while len(out) < n and tries < n * 50:
        tries += 1
        u = rng.random()
        L = 1 if u < p1 else (2 if u < p1 + p2 else (3 if rng.random() < 0.7 else 4))
        if L == 1:
            if rng.random() < t["q"]:
                out.add((f"e{rng.choice(V, p=f)}",))
            else:
                out.add((f"m{rng.choice(Vm, p=fm)}",))   # m = separate monothematic stock

            continue
        slots = ["F"] + ["M"] * (L - 2) + ["L"]
        lex = rng.random() < t["lam"]
        for attempt in range(6):
            els = []
            for sl in slots:
                w = wpos[sl].copy()
                if els and t["kappa"] > 1 and cls[els[-1]]:
                    w = np.where(cls, w * t["kappa"], w)
                w[els] = 0
                w /= w.sum()
                els.append(int(rng.choice(V, p=w)))
            if L == 2 and lex and (els[1], els[0]) in canon:
                els = [els[1], els[0]]
            # lexicalised: no adjacent pair may contradict an earlier canonical order (resample)
            if not lex or all((b, a) not in canon for a, b in zip(els, els[1:])):
                break
        for a, b in zip(els, els[1:]):
            if (b, a) not in canon:
                canon[(a, b)] = 1
        out.add(tuple(f"e{e}" for e in els))
    cset = {f"e{e}" for e in np.where(cls)[0]}
    return sorted(out), (cset if cset else None)


def clip(theta):
    t = dict(theta)
    for k, (lo, hi) in BOUNDS.items():
        t[k] = float(np.clip(t[k], lo, hi))
    if t["p1"] + t["p2"] > 1:
        t["p2"] = 1 - t["p1"]
    return t


def random_theta(rng):
    t = {}
    for k, (lo, hi) in BOUNDS.items():
        t[k] = float(np.exp(rng.uniform(np.log(lo), np.log(hi)))) if k in LOG else float(rng.uniform(lo, hi))
    return clip(t)
