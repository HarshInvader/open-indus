"""local_hands step 2: planted power on SYNTHETIC occurrences only. No real data is read.

Synthetic corpus (parameters fixed here, not taken from ICIT counts):
  sites: 6, weights 0.45 0.30 0.10 0.07 0.05 0.03; types: 3, weights 0.70 0.20 0.10.
  neighbours: 120 sign types, Zipf(1.1); prev is the text edge with prob 0.30, next with prob
    0.30. Each site boosts its own 10 random neighbour signs x3 (sites differ in context, so
    a test that ignores context can be fooled).
  families: F, 2 variants each, base share of variant 0 ~ U(0.55, 0.85) per family;
    tokens shared out over families by Zipf(1.0).
Plants:
  NBd(q), diffuse: every neighbour value gets a preferred form at random; with prob q a
    token's form is the preferred form of its PREV (one side only), else the base draw.
  NBb(b), bound forms: per family, b of the 15 most frequent PREV values are binding; a
    token after a binding value takes that value's form (the rarer variant for the first,
    then alternating) with prob 0.9, else the base draw. This is the shape paragorth
    S-DARK-46.5 reports (e.g. one form after one sign in 29 of 29 cases).
  PL(d): every site gets s = +1 or -1 at random (at least one of each); P(variant 0) =
    clip(base + s*d, 0.02, 0.98).
Tests (lh_lib): nb_test (strata family x site x type) and pl_test (strata family x type x
  prev x next). The NB-only plant is also the confound check for pl_test (sites differ in
  context, so a place test that failed to hold context fixed would fire), and the PL-only
  plant is the confound check for nb_test.
Detection: dev (80% of tokens) p <= 0.005 AND held-out (20%) p <= 0.05 (also reported:
  dev-only rate). Informative-token counts (lh_lib.informative_counts, no form labels) are
  recorded per cell so the count gate can check them on real data.
Run: .venv/bin/python -I experiments/local_hands/power.py 4   -> power_F4.json
     .venv/bin/python -I experiments/local_hands/power.py 8   -> power_F8.json
     (seed = 20261125 + F; 60 reps, 250 permutations per test)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lh_lib as L  # noqa: E402

SEED = 20261125
REPS = 60
NPERM = 250
SITE_W = np.array([0.45, 0.30, 0.10, 0.07, 0.05, 0.03])
TYPE_W = np.array([0.70, 0.20, 0.10])
NCTX = 120


def zipf(n, a):
    w = 1.0 / np.arange(1, n + 1) ** a
    return w / w.sum()


def synth(rng, n, F, q=0.0, d=0.0, b=0):
    site = rng.choice(6, n, p=SITE_W)
    typ = rng.choice(3, n, p=TYPE_W)
    fam = rng.choice(F, n, p=zipf(F, 1.0))
    base_ctx = zipf(NCTX, 1.1)
    ctx_by_site = []
    for s in range(6):
        w = base_ctx.copy()
        w[rng.choice(NCTX, 10, replace=False)] *= 3
        ctx_by_site.append(w / w.sum())

    def draw_ctx(edge_code):
        out = np.empty(n, dtype=np.int64)
        for s in range(6):
            m = site == s
            out[m] = rng.choice(NCTX, m.sum(), p=ctx_by_site[s])
        out[rng.random(n) < 0.30] = edge_code
        return out
    prev = draw_ctx(NCTX)
    nxt = draw_ctx(NCTX + 1)
    base = rng.uniform(0.55, 0.85, F)
    p0 = base[fam].copy()
    if d > 0:
        sg = rng.choice([-1, 1], 6)
        sg[0], sg[1] = 1, -1
        p0 = np.clip(p0 + sg[site] * d, 0.02, 0.98)
    form = (rng.random(n) >= p0).astype(np.int64)  # 0 = variant 0
    if q > 0:
        pref = rng.integers(0, 2, NCTX + 2)
        m = rng.random(n) < q
        form[m] = pref[prev[m]]
    if b > 0:
        top = np.argsort(-base_ctx)[:15]
        for f in range(F):
            bind = rng.choice(top, b, replace=False)
            for j, c in enumerate(bind):
                m = (fam == f) & (prev == c) & (rng.random(n) < 0.9)
                form[m] = 1 if j % 2 == 0 else 0
    form = fam * 2 + form
    ho = rng.random(n) < 0.20
    return dict(form=form, fam=fam, site=site, type=typ, prev=prev, next=nxt), ho


def sub(A, m):
    return {k: v[m] for k, v in A.items()}


TESTS = {"nb": L.nb_test, "pl": L.pl_test}


def run(rng, n, F, q, d, b):
    hits = {k: 0 for k in TESTS}
    hits["dev_only_nb"] = hits["dev_only_pl"] = 0
    info = []
    for _ in range(REPS):
        A, ho = synth(rng, n, F, q, d, b)
        D, H = sub(A, ~ho), sub(A, ho)
        info.append(L.informative_counts(D))
        for k, fn in TESTS.items():
            pd = fn(D, rng, NPERM)["p"]
            if pd <= 0.005:
                hits["dev_only_" + k] += 1
                if fn(H, rng, NPERM)["p"] <= 0.05:
                    hits[k] += 1
    out = {k: v / REPS for k, v in hits.items()}
    out["dev_n_mean"] = float(np.mean([n * 0.8]))
    out["nb_informative_mean"] = float(np.mean([i["nb_informative"] for i in info]))
    out["pl_informative_mean"] = float(np.mean([i["pl_informative"] for i in info]))
    return out


def main():
    grid_F = [int(sys.argv[1])] if len(sys.argv) > 1 else [4, 8]
    rng = np.random.default_rng(SEED + grid_F[0] if len(grid_F) == 1 else SEED)
    grid_n = [400, 800, 1200, 2000, 3000]
    plants = {"null": (0, 0, 0), "NBd_q0.3": (0.3, 0, 0), "NBb_b3": (0, 0, 3),
              "PL_d0.15": (0, 0.15, 0), "PL_d0.2": (0, 0.2, 0), "both_b3_d0.2": (0, 0.2, 3)}
    out = dict(seed=SEED, reps=REPS, nperm=NPERM, rule="dev p<=0.005 and held-out p<=0.05", cells=[])
    for F in grid_F:
        for n in grid_n:
            for name, (q, d, b) in plants.items():
                r = run(rng, n, F, q, d, b)
                out["cells"].append(dict(F=F, n=n, plant=name, **r))
                print(F, n, name, r, flush=True)
    tag = "" if len(grid_F) > 1 else f"_F{grid_F[0]}"
    json.dump(out, open(HERE / f"power{tag}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
