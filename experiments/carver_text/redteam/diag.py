"""Red team diagnostics for carver_text. ALL EXPLORATORY. Base config = sealed replica
(first ICIT row, ICIT site, tercile ties upward, >=3 known sizes) unless stated."""
import sys, json, math, re, collections
import numpy as np
import os; RT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')) + '/'
sys.path.insert(0, RT + 'experiments/carver_text/redteam')
import rt
NP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
OUT = {}
icit = {}
for l in open(RT + 'data/icit_texts.jsonl'):
    x = json.loads(l); icit[x['id']] = x

def load(fix_m734=False, klb=False):
    d = json.load(open(RT + 'experiments/carver_text/out/seals.json'))
    if klb:
        K = {}
        for x in icit.values():
            m = re.fullmatch(r'K-(\d+)\s*([A-Za-z]?)', x['cisi'])
            if m: K.setdefault(m.group(1) + m.group(2).lower(), []).append(x)
        have = {r['id'] for r in d if r['icit']}
        for r in d:
            if r['id'].startswith('KLB') and not r['icit'] and r['id'][3:].lower() in K and 'K' + r['id'][3:] not in have:
                r['icit'] = K[r['id'][3:].lower()]
    pool = []
    for r in d:
        if not r['icit'] or not r['icit'][0]['seq']: continue
        t = r['icit'][0]
        try: a = float(t['width_mm']) * float(t['height_mm'])
        except ValueError: a = 0.0
        g = r['group']
        if fix_m734 and g == 'M-KLB-ND1': g = 'MD-KLB-ND1'
        full = icit[t['id']]
        m = re.fullmatch(r'([A-Za-z]+)(\d+)[A-Za-z]?', r['id'])
        pool.append(dict(id=r['id'], site=t['site'], group=g, seq=list(t['seq']), area=a, complete=t['complete'],
                         period=full['period'], phase=full['phase'], pre=m.group(1), num=int(m.group(2))))
    return pool

def strata(pool, nbins=3, extra=None):
    by = collections.defaultdict(list)
    for i, p in enumerate(pool): by[p['site']].append(i)
    st = [None] * len(pool)
    for s, idx in by.items():
        known = [i for i in idx if pool[i]['area'] > 0]
        cuts = np.quantile([pool[i]['area'] for i in known], [k / nbins for k in range(1, nbins)]) if len(known) >= 3 else None
        for i in idx:
            a = pool[i]['area']
            b = 'u' if a <= 0 else (0 if cuts is None else int(np.searchsorted(cuts, a, side='right')))
            st[i] = (s, b) + ((extra(pool[i]),) if extra else ())
    return st

def mats(pool, drop=(), weight='idf', maxdf=None):
    N = len(pool); sets = [set(p['seq']) - set(drop) for p in pool]
    dfull = collections.Counter(s for p in pool for s in set(p['seq']))
    S = np.zeros((N, N)); M = np.ones((N, N)); np.fill_diagonal(M, 0)
    for i in range(N):
        for j in range(i + 1, N):
            sh = sets[i] & sets[j]
            if maxdf: sh = {s for s in sh if dfull[s] <= maxdf}
            S[i, j] = S[j, i] = sum(math.log(N / dfull[s]) for s in sh) if weight == 'idf' else len(sh)
            a, b = pool[i]['seq'], pool[j]['seq']
            if rt.lev(a, b) <= 1 or rt.contained(a, b): M[i, j] = M[j, i] = 0
    return S, M, dfull

def labels(pool):
    lab, names = rt.hands(pool); return lab, names

def parts(L, W, M, K):
    gi = np.nonzero(L >= 0)[0]; l = L[gi]; eq = (l[:, None] == l[None, :])
    num = np.bincount(l, weights=(W[np.ix_(gi, gi)] * eq).sum(1), minlength=K) / 2
    den = np.bincount(l, weights=(M[np.ix_(gi, gi)] * eq).sum(1), minlength=K) / 2
    return num, den

def run(lab, W, M, K, st, nperm, seed, elig=None):
    rng = np.random.default_rng(seed)
    g = collections.defaultdict(list)
    for i, s in enumerate(st):
        if elig is None or elig[i]: g[s].append(i)
    g = [np.array(v) for v in g.values() if len(v) > 1]
    on, od = parts(lab, W, M, K)
    NUM = np.empty((nperm, K)); DEN = np.empty((nperm, K))
    for b in range(nperm):
        L = lab.copy()
        for idx in g: L[idx] = lab[rng.permutation(idx)]
        NUM[b], DEN[b] = parts(L, W, M, K)
    return on, od, NUM, DEN

def summ(on, od, NUM, DEN, keep=None):
    if keep is None: keep = np.ones(len(on), bool)
    obs = on[keep].sum() / od[keep].sum()
    null = NUM[:, keep].sum(1) / np.maximum(DEN[:, keep].sum(1), 1e-9)
    ge = int((null >= obs - 1e-12).sum())
    return dict(obs=round(float(obs), 4), null=round(float(null.mean()), 4), ratio=round(float(obs / null.mean()), 3),
                p=round((ge + 1) / (len(null) + 1), 5), pairs=int(od[keep].sum()), hands=int(keep.sum()))

def rep(name, r):
    OUT[name] = r; print(name, json.dumps(r), flush=True)

pool = load(); lab, names = labels(pool); K = len(names); st = strata(pool)
S, M, df = mats(pool); W = S * M
# 1 sealed replica, 100k (robustness)
on, od, NUM, DEN = run(lab, W, M, K, st, 100000, 101)
rep('replica_sealed_config_100k', summ(on, od, NUM, DEN))
for k in range(5):
    sl = slice(k * 10000, (k + 1) * 10000)
    rep(f'replica_10k_block{k}', summ(on, od, NUM[sl], DEN[sl]))
# 2 leave-one-hand-out, same permutations
lo = []
for h in range(K):
    keep = np.ones(K, bool); keep[h] = False
    r = summ(on, od, NUM, DEN, keep); lo.append((r['p'], names[h], int(od[h]), r['ratio']))
lo.sort()
rep('LOHO', dict(p_min=lo[0][0], p_max=lo[-1][0], p_median=float(np.median([x[0] for x in lo])),
                 n_p_le_01=sum(1 for x in lo if x[0] <= 0.01), n_p_gt_05=sum(1 for x in lo if x[0] > 0.05),
                 worst3=[dict(p=x[0], hand_pairs=x[2], ratio=x[3]) for x in lo[-3:]],
                 best3=[dict(p=x[0], hand_pairs=x[2], ratio=x[3]) for x in lo[:3]]))
size = np.array([np.sum(lab == h) for h in range(K)])
order = np.argsort(-size)
for kdrop in (1, 2, 3):
    keep = np.ones(K, bool); keep[order[:kdrop]] = False
    rep(f'drop_{kdrop}_largest_hands', summ(on, od, NUM, DEN, keep))
keep = np.zeros(K, bool); keep[order[:3]] = True
rep('only_3_largest_hands', summ(on, od, NUM, DEN, keep))
# hand-equal weighting (mean of per-hand means)
ok = od > 0
obs_eq = np.mean(on[ok] / od[ok])
with np.errstate(invalid='ignore', divide='ignore'):
    null_eq = np.nanmean(np.where(DEN > 0, NUM / DEN, np.nan), 1)
rep('hand_equal_weight', dict(obs=round(float(obs_eq), 4), null=round(float(null_eq.mean()), 4),
                              p=round(float((1 + (null_eq >= obs_eq).sum()) / (1 + len(null_eq))), 5)))
# per-hand excess share
exp_h = NUM.mean(0); exc = on - exp_h * (od / np.maximum(DEN.mean(0), 1e-9))
tot = exc.sum(); top = np.sort(exc)[::-1]
rep('excess_concentration', dict(total_excess=round(float(tot), 2), top1_share=round(float(top[0] / tot), 3),
                                 top3_share=round(float(top[:3].sum() / tot), 3), hands_positive=int((exc > 0).sum()), hands=K))
# single- vs multi-site hands
ms = np.array([len({pool[i]['site'] for i in np.nonzero(lab == h)[0]}) > 1 for h in range(K)])
rep('single_site_hands_only', summ(on, od, NUM, DEN, ~ms)); rep('multi_site_hands_only', summ(on, od, NUM, DEN, ms))
# 3 selection confound: grouped vs ungrouped texts
gl = lab >= 0
rep('desc_text_len', dict(grouped=round(float(np.mean([len(pool[i]['seq']) for i in np.nonzero(gl)[0]])), 2),
                          ungrouped=round(float(np.mean([len(pool[i]['seq']) for i in np.nonzero(~gl)[0]])), 2),
                          complete_grouped=round(float(np.mean([pool[i]['complete'] for i in np.nonzero(gl)[0]])), 3),
                          complete_ungrouped=round(float(np.mean([pool[i]['complete'] for i in np.nonzero(~gl)[0]])), 3),
                          ntypes_grouped=round(float(np.mean([len(set(pool[i]['seq'])) for i in np.nonzero(gl)[0]])), 2),
                          ntypes_ungrouped=round(float(np.mean([len(set(pool[i]['seq'])) for i in np.nonzero(~gl)[0]])), 2)))
r = run(lab, W, M, K, st, NP, 102, elig=gl); rep('perm_among_hand_seals_only', summ(*r))
anyg = np.array([p['group'] is not None for p in pool])
r = run(lab, W, M, K, st, NP, 103, elig=anyg); rep('perm_among_any_grouped_seals', summ(*r))
r = run(lab, W, M, K, [(p['site'],) for p in pool], NP, 104, elig=gl); rep('perm_among_hand_seals_site_only_strata', summ(*r))
def lenbin(p): n = len(set(p['seq'])); return 0 if n <= 3 else (1 if n <= 5 else (2 if n <= 7 else 3))
r = run(lab, W, M, K, strata(pool, extra=lenbin), NP, 105); rep('strata_plus_textlen_bin', summ(*r))
r = run(lab, W, M, K, [(p['site'], lenbin(p)) for p in pool], NP, 106); rep('strata_site_x_textlen_only', summ(*r))
r = run(lab, W, M, K, strata(pool, extra=lambda p: p['complete']), NP, 107); rep('strata_plus_complete', summ(*r))
# 4 period / phase
r = run(lab, W, M, K, strata(pool, extra=lambda p: p['period']), NP, 108); rep('strata_plus_period', summ(*r))
r = run(lab, W, M, K, strata(pool, extra=lambda p: p['phase']), NP, 109); rep('strata_plus_phase', summ(*r))
kn = np.array([p['period'] != '-' or p['phase'] != '-' for p in pool])
same = (lab[:, None] == lab[None, :]) & (lab[:, None] >= 0); np.fill_diagonal(same, False)
iu = np.triu_indices(len(pool), 1); wp = np.nonzero(same[iu])[0]
pi, pj = iu[0][wp], iu[1][wp]
rep('desc_period', dict(pool_with_period=int(sum(p['period'] != '-' for p in pool)), pool_with_phase=int(sum(p['phase'] != '-' for p in pool)),
    within_pairs_both_phase_known=int(sum(pool[i]['phase'] != '-' and pool[j]['phase'] != '-' for i, j in zip(pi, pj))),
    of_those_same_phase=int(sum(pool[i]['phase'] != '-' and pool[i]['phase'] == pool[j]['phase'] and pool[i]['site'] == pool[j]['site'] for i, j in zip(pi, pj)))))
# 5 size finer
for nb in (5, 8):
    r = run(lab, W, M, K, strata(pool, nbins=nb), NP, 110 + nb); rep(f'strata_site_x_size_{nb}bins', summ(*r))
r = run(lab, W, M, K, [(p['site'],) for p in pool], NP, 120); rep('strata_site_only', summ(*r))
r = run(lab, W, M, K, [(0,) for p in pool], NP, 121); rep('no_strata', summ(*r))
# 6 CISI-number adjacency (proxy for catalogue order / lot)
adj = np.array([pool[i]['pre'] == pool[j]['pre'] and abs(pool[i]['num'] - pool[j]['num']) <= 10 for i, j in zip(pi, pj)])
sc = W[pi, pj]
rep('desc_cisi_adjacent', dict(within_pairs=int(len(pi)), adjacent_le10=int(adj.sum()), mean_score_adjacent=round(float(sc[adj].mean()), 3),
                               mean_score_nonadjacent=round(float(sc[~adj].mean()), 3)))
N = len(pool); pre = np.array([p['pre'] for p in pool]); num = np.array([p['num'] for p in pool])
for k in (10, 50):
    A = (pre[:, None] == pre[None, :]) & (np.abs(num[:, None] - num[None, :]) <= k)
    M2 = M * ~A
    r = run(lab, S * M2, M2, K, st, NP, 130 + k); rep(f'mask_cisi_adjacent_le{k}', summ(*r))
r = run(lab, W, M, K, [(p['site'], p['pre'], p['num'] // 100) for p in pool], NP, 140); rep('strata_site_x_cisi_hundred', summ(*r))
# pool-wide: do CISI-adjacent pairs share more regardless of hand?
allA = (pre[:, None] == pre[None, :]) & (np.abs(num[:, None] - num[None, :]) <= 10) & ~same
samesite = np.array([[a['site'] == b['site'] for b in pool] for a in pool]) & ~same; np.fill_diagonal(samesite, False); np.fill_diagonal(allA, False)
rep('desc_pool_adjacency', dict(mean_score_adjacent_nonhand=round(float(S[allA].mean()), 3), mean_score_same_site_nonhand=round(float(S[samesite & ~allA].mean()), 3)))
# 7 common signs
topdf = [s for s, _ in df.most_common(20)]
rep('desc_df', dict(n_types=len(df), top5_df=[c for _, c in df.most_common(5)], N=N))
for k in (3, 5, 10, 20):
    S2, M2, _ = mats(pool, drop=topdf[:k]); r = run(lab, S2 * M, M, K, st, NP, 150 + k); rep(f'drop_top{k}_signs', summ(*r))
S2, _, _ = mats(pool, weight='count'); r = run(lab, S2 * M, M, K, st, NP, 171); rep('unweighted_shared_count', summ(*r))
for mx in (10, 25):
    S2, _, _ = mats(pool, maxdf=mx); r = run(lab, S2 * M, M, K, st, NP, 172 + mx); rep(f'only_signs_df_le{mx}', summ(*r))
S2, _, _ = mats(pool); 
# share of observed score from top-k signs
def contrib(k):
    Sk, _, _ = mats(pool, drop=topdf[:k]); return float(1 - (Sk * M)[pi, pj].sum() / W[pi, pj].sum())
rep('obs_score_share_from_top_signs', {f'top{k}': round(contrib(k), 3) for k in (3, 5, 10)})
# 8 join fixes
p2 = load(fix_m734=True); l2, n2 = labels(p2); S2, M2, _ = mats(p2)
r = run(l2, S2 * M2, M2, len(n2), strata(p2), NP, 180); rep('fix_M734_label', summ(*r))
p3 = load(fix_m734=True, klb=True); l3, n3 = labels(p3); S3, M3, _ = mats(p3)
r = run(l3, S3 * M3, M3, len(n3), strata(p3), NP, 181); x = summ(*r); x['pool'] = len(p3); x['grouped'] = int((l3 >= 0).sum()); rep('fix_M734_plus_KLB_join', x)
json.dump(OUT, open(RT + 'experiments/carver_text/redteam/diag.json', 'w'), indent=1)
