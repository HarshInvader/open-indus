"""Verbatim copy of the stroked-jar statistic (prereg r_symmetry "Code plan": signmap/strokedjar_test.py runs its test
at import). Source: experiments/signmap/strokedjar_test.py at commit 592193f, lines 13-28. The statements are
unchanged except that they sit inside a function: `T` (the s2_test module), the text set and the sign mapping are
arguments, so the same lines run on a variant cell or the other edition. Lines 13-14 originally read
`texts = T.icit_set()` and tested membership in SJ; here `texts` and `SJ` are passed in already mapped.
"""
from scipy.stats import poisson


def strokedjar(T, texts, SJ):
    # ---- strokedjar_test.py lines 15-28 (line 13 SJ and line 14 texts are the arguments)
    for t in texts:
        if t["signs"] & SJ: t["signs"] = t["signs"] | {"SJ"}
    signs = ["SJ"]                     # line 17 lists SJ, M343, M344, M345; only the pooled SJ is the sealed statistic
    r = T.perm_test(texts, signs, ["pottery graffito"])["pottery graffito"]
    out = {}
    for j, s in enumerate(signs):
        mu = float(r["mu"][j]); obs = int(r["obs"][j])
        out[s] = dict(obs=obs, exp=round(mu, 2), ratio=round(obs / mu, 3) if mu else None, p_enrich=float(r["p"][j]), present=int(r["present"][j]))
    mu = out["SJ"]["exp"]; q99 = poisson.ppf(0.99, mu)
    power_2x = float(1 - poisson.cdf(q99 - 1, 2 * mu))
    sj = out["SJ"]
    verdict = ("survives: enriched >= 2x on pottery" if sj["ratio"] >= 2 and sj["p_enrich"] <= 0.01 else
               "refuted: ratio <= 1 on pottery (kill condition), test powered for 2x" if sj["ratio"] <= 1 and power_2x >= 0.8 else
               "inconclusive")
    return dict(n_pottery_texts=r["n_cls"], signs=out, power_2x=round(power_2x, 3), verdict=verdict)


def power_2x_from_mu(mu):
    """strokedjar_test.py lines 23-24 (Poisson 2x power at the 0.99 quantile), as a function of the null mean."""
    q99 = poisson.ppf(0.99, mu)
    return float(1 - poisson.cdf(q99 - 1, 2 * mu))
