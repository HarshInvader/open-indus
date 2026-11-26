"""Red team follow-up, EXPLORATORY: rare-sign statistic under the stricter nulls."""
import sys, json, collections, runpy
import numpy as np
sys.argv = ['x', '1']
src = open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'diag.py')).read().split("pool = load(); lab, names")[0]
exec(src)
NP = 20000
pool = load(); lab, names = labels(pool); K = len(names); st = strata(pool); gl = lab >= 0
S, M, df = mats(pool); W = S * M
def lenbin(p): n = len(set(p['seq'])); return 0 if n <= 3 else (1 if n <= 5 else (2 if n <= 7 else 3))
pre = np.array([p['pre'] for p in pool]); num = np.array([p['num'] for p in pool])
A = (pre[:, None] == pre[None, :]) & (np.abs(num[:, None] - num[None, :]) <= 10)
Sr, _, _ = mats(pool, maxdf=25); Wr = Sr * M
same = (lab[:, None] == lab[None, :]) & gl[:, None]; np.fill_diagonal(same, False)
iu = np.triu_indices(len(pool), 1); wp = np.nonzero(same[iu])[0]; pi, pj = iu[0][wp], iu[1][wp]
sc = Wr[pi, pj]
hands_with = len({lab[i] for i, s in zip(pi, sc) if s > 0})
rep('rare_desc', dict(pairs_sharing_a_rare_sign=int((sc > 0).sum()), of=len(sc), hands_with_such_pair=hands_with,
                      top5_pairs_share=round(float(np.sort(sc)[-5:].sum() / sc.sum()), 3)))
on, od, NUM, DEN = run(lab, Wr, M, K, st, NP, 201); rep('rare_df25_sealed_strata', summ(on, od, NUM, DEN))
lo = sorted(summ(on, od, NUM, DEN, np.arange(K) != h)['p'] for h in range(K))
rep('rare_df25_LOHO', dict(p_min=lo[0], p_max=lo[-1]))
size = np.array([np.sum(lab == h) for h in range(K)]); order = np.argsort(-size)
keep = np.ones(K, bool); keep[order[:3]] = False; rep('rare_df25_drop3largest', summ(on, od, NUM, DEN, keep))
r = run(lab, Wr, M, K, strata(pool, extra=lenbin), NP, 202); rep('rare_df25_plus_textlen', summ(*r))
r = run(lab, Wr, M, K, strata(pool, extra=lenbin), NP, 203, elig=gl); rep('rare_df25_textlen_among_hand_seals', summ(*r))
M2 = M * ~A
r = run(lab, Sr * M2, M2, K, strata(pool, extra=lenbin), NP, 204); rep('rare_df25_textlen_mask_adjacent', summ(*r))
r = run(lab, W, M, K, [(p['site'], lenbin(p)) for p in pool], NP, 205, elig=gl); rep('idf_site_x_textlen_among_hand_seals', summ(*r))
r = run(lab, S * M2, M2, K, strata(pool, extra=lenbin), NP, 206); rep('idf_textlen_mask_adjacent', summ(*r))
r = run(lab, W, M, K, strata(pool, extra=lambda p: len(set(p['seq']))), NP, 207); rep('idf_strata_plus_exact_textlen', summ(*r))
# length-normalised statistic: score / (|A|*|B|) proxy for chance overlap
n = np.array([len(set(p['seq'])) for p in pool], float); Wn = W / np.outer(n, n)
r = run(lab, Wn, M, K, st, NP, 208); x = summ(*r); x.pop('obs'); x.pop('null'); rep('idf_per_sign_pair_normalised', x)
json.dump(OUT, open(RT + 'experiments/carver_text/redteam/diag2.json', 'w'), indent=1)
