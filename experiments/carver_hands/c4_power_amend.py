"""C4 (amendment A1, logged AFTER c3 ran; exploratory, does not change the pre-registered verdict).
The frozen planted control replaced closers by each group's MODAL closer; every group's mode is the jar
W740, so the plant added no group-specific signal (power 0 everywhere). Here each group gets its OWN
closer (a distinct value drawn from the observed closer vocabulary, excluding the jar) with probability
q; detection = one-sided E_F permutation p < 0.0125 (200 perms, 50 plants). Also: upper 95% bound on the
frame within/between rate ratio from the frozen c3 null spread.
Run: .venv/bin/python -I experiments/carver_hands/c4_power_amend.py -> c4.json
"""
import os, sys, csv, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c3_test as T

D = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(7)


def ef_p(V, strata, within, I, J, nperm=200):
    obs = T.summarize(T.stat(V, np.arange(len(strata)), I, J, within))['E_F']
    nf = np.array([T.summarize(T.stat(V, T.strat_perm(strata), I, J, within))['E_F'] for _ in range(nperm)])
    return (nf >= obs).mean() + 1 / nperm, nf


def plant_power(name, texts, strata, within_fn, groups, qs=(0.05, 0.1, 0.2), reps=50):
    V0, _ = T.codes(texts)
    n = len(texts); I, J = np.triu_indices(n, 1); within = within_fn(I, J)
    vocab = [v for v in np.unique(V0['closer']) if v >= 0]
    jar = np.bincount(V0['closer'][V0['closer'] >= 0]).argmax()
    vocab = [v for v in vocab if v != jar]
    out = {}
    for q in qs:
        hits = 0
        for r in range(reps):
            V = {k: v.copy() for k, v in V0.items()}
            gs = sorted(set(groups.tolist()))
            pick_vals = RNG.choice(vocab, len(gs), replace=len(vocab) < len(gs))
            for g, val in zip(gs, pick_vals):
                ii = np.where(groups == g)[0]
                V['closer'][ii[RNG.random(len(ii)) < q]] = val
            p, _ = ef_p(V, strata, within, I, J)
            hits += p < 0.0125
        out[str(q)] = hits / reps
    print(name, 'power (group-specific closer planted):', out, flush=True)
    return out


def main():
    c3 = json.load(open(os.path.join(D, 'c3.json')))
    icit = {r['id']: r for r in (json.loads(l) for l in open(os.path.join(T.REPO, 'data/icit_texts.jsonl')))}
    CL = list(csv.DictReader(open(os.path.join(D, 'clusters.csv'))))
    texts = [[s for s in icit[c['icit_id']]['seq'] if s not in ('|', '#')] for c in CL]
    strata = np.array([f"{c['site']}|{c['size_group']}" for c in CL])
    lab = np.array([int(c['cluster']) for c in CL])
    U = [r for r in icit.values() if r['type'] == 'SEAL:S' and r['symbol'].startswith('Bull1:') and r['complete']
         and '|' not in r['seq'] and '#' not in r['seq'] and float(r['width_mm'] or 0) > 0]
    t3 = [r['seq'] for r in U]
    s3 = np.array([f"{r['site']}|{T.size_group(r['width_mm'])}" for r in U])
    l3 = np.array([r['symbol'].split(':')[1] for r in U])
    OUT = {'power_P2': plant_power('P2', texts, strata, lambda I, J: lab[I] == lab[J], lab),
           'power_P3': plant_power('P3', t3, s3, lambda I, J: l3[I] == l3[J], l3)}
    # upper bounds on frame ratio: obs E_F + 1.96 * null sd of E_F (null sd from a fresh 500-perm run)
    for name, tx, st, wf in [('P1', texts, strata, None), ('P2', texts, strata, lambda I, J: lab[I] == lab[J]),
                             ('P3', t3, s3, lambda I, J: l3[I] == l3[J])]:
        V, _ = T.codes(tx); n = len(tx); I, J = np.triu_indices(n, 1)
        if name == 'P1':
            F = np.load(os.path.join(D, 'work', 'features.npz'))['R']
            Rn = F / np.linalg.norm(F, axis=1, keepdims=True); S = Rn @ Rn.T; np.fill_diagonal(S, -9)
            nn = np.argsort(-S, axis=1)[:, :5]; near = np.zeros((n, n), bool)
            for i in range(n): near[i, nn[i]] = True
            near |= near.T; within = near[I, J]
        else:
            within = wf(I, J)
        _, nf = ef_p(V, st, within, I, J, nperm=500)
        key = {'P1': 'P1_knn', 'P2': 'P2_clusters', 'P3': 'P3_letter'}[name]
        ef = c3[key]['obs']['E_F']
        ub = float(np.exp(ef - nf.mean() + 1.96 * nf.std()))
        OUT[f'frame_ratio_upper95_{name}'] = ub
        print(name, f'E_F {ef:+.3f}, null {nf.mean():+.3f}+-{nf.std():.3f}, frame within/between ratio upper 95% ~{ub:.2f}', flush=True)
    json.dump(OUT, open(os.path.join(D, 'c4.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
