"""Competing numeral-grammar models (frozen in docs/prereg/numeral_grammar.md).
A group is a tuple of (class, value) tokens in reading order."""
import math
from collections import Counter
from common import M_NUM, W_NUM

EPS = 0.01
ALPHA = 0.5
SUPPORT = sorted({(c, v) for c, v, _ in list(M_NUM.values()) + list(W_NUM.values()) if c != "C"})


def dirichlet(counts, cells):
    tot = sum(counts.get(x, 0) for x in cells) + ALPHA * len(cells)
    return {x: (counts.get(x, 0) + ALPHA) / tot for x in cells}


class Fit:
    def __init__(self, dev_groups):
        singles = Counter(g[0] for g in dev_groups if len(g) == 1)
        inmulti = Counter(t for g in dev_groups if len(g) > 1 for t in g)
        alltok = Counter(t for g in dev_groups for t in g)
        first = Counter(g[0] for g in dev_groups if len(g) > 1)
        second = Counter(t for g in dev_groups if len(g) > 1 for t in g[1:])
        self.pairs = Counter(g for g in dev_groups if len(g) == 2)
        self.B = dirichlet(alltok, SUPPORT)            # baseline token dist
        self.f1 = singles; self.f2 = inmulti
        self.first = dirichlet(first, SUPPORT); self.second = dirichlet(second, SUPPORT)

    # -- helpers
    def base(self, g):
        p = 1.0
        for t in g:
            p *= self.B[t]
        return p

    def single_dist(self, allowed):
        cells = [x for x in SUPPORT if allowed(x)]
        return dirichlet(self.f1, cells)

    def prob(self, model, g):
        """Q_M(g | len(g)) with leak."""
        A = self.allowed_prob(model, g)
        return (1 - EPS) * A + EPS * self.base(g)

    def allowed_prob(self, model, g):
        k = len(g)
        le12 = lambda x: x[1] <= 12
        if k == 1:
            allow = {"M1": le12, "M2a": le12, "M2b": le12, "M5": le12,
                     "M3": lambda x: x[1] <= 8 or x[1] == 16,
                     "M4": lambda x: x[1] <= 10}[model]
            return self.single_dist(allow).get(g[0], 0.0)
        if model == "M1":
            if not all(le12(t) for t in g):
                return 0.0
            d = dirichlet(self.f2, [x for x in SUPPORT if le12(x)])
            p = 1.0
            for t in g:
                p *= d[t]
            return p
        if model == "M5":
            if not all(le12(t) for t in g):
                return 0.0
            cells = [x for x in SUPPORT if le12(x)]
            fz = sum(self.first[x] for x in cells); sz = sum(self.second[x] for x in cells)
            p = self.first[g[0]] / fz if le12(g[0]) else 0
            for t in g[1:]:
                p *= self.second[t] / sz
            return p
        cells = self.allowed_cells(model, k)
        if g not in cells:
            return 0.0
        return dirichlet(Counter({x: n for x, n in self.pairs.items()}), cells)[g] if k == 2 else 1.0 / len(cells)

    def allowed_cells(self, model, k):
        S12 = ("S", 12)
        if model in ("M2a", "M2b"):
            smalls = [("S", n) for n in range(1, 12) if ("S", n) in SUPPORT]
            out = []
            units_only = tuple([S12] * k)
            out.append(units_only)
            for s in smalls:
                if model == "M2a":
                    out.append(tuple([S12] * (k - 1) + [s]))
                else:
                    out.append(tuple([s] + [S12] * (k - 1)))
            return out
        if model == "M3":
            units = [x for x in SUPPORT if x[1] in (8, 16)]
            smalls = [x for x in SUPPORT if x[1] <= 7]
        elif model == "M4":
            units = [x for x in SUPPORT if x[1] == 10]
            smalls = [x for x in SUPPORT if x[1] <= 9]
        if k == 2:
            return [(u, s) for u in units for s in smalls] + [(u, w) for u in units for w in units]
        return [tuple([u] * (k - 1) + [s]) for u in units for s in smalls] + [tuple([u] * k) for u in units]


MODELS = ["M1", "M2a", "M2b", "M3", "M4", "M5"]


def loglik(fit, model, groups):
    return sum(math.log10(fit.prob(model, g)) for g in groups)


def scopeB_prob(fit, model, g):
    """Q(g | k>=2 and contains S12), two-sign groups only (longer: leak-only)."""
    S12 = ("S", 12)
    cells = [x for x in SUPPORT]
    pairs12 = sorted({(S12, x) for x in cells} | {(x, S12) for x in cells})
    if model == "M1":
        d = dirichlet(fit.f2, cells)
        w = {p: d[p[0]] * d[p[1]] for p in pairs12}
        Z = sum(w.values())
        return w.get(g, 0.0) / Z if len(g) == 2 else 1e-6
    al = fit.allowed_cells(model, 2)
    A = dirichlet(fit.pairs, al).get(g, 0.0) if len(g) == 2 else 0.0
    d = dirichlet(fit.f2, cells)
    w = {p: d[p[0]] * d[p[1]] for p in pairs12}
    Z = sum(w.values())
    Bp = w.get(g, 0.0) / Z if len(g) == 2 else 1e-6
    return (1 - EPS) * A + EPS * Bp
