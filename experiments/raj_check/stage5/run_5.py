"""Stage 5 (T9): picking power with a held-out seal half (PREREG_STAGE5.md).
  python3 -I stage5/run_5.py split    -> inputs/corpus_A.csv, corpus_B.csv
  python3 -I stage5/run_5.py search   -> inputs/names_jpick.jsonl, search_log.json
  python3 -I stage5/run_5.py test     -> out/T9/..., out/T9_summary.json
Raj's contest.py unchanged; nice 20, 4 processes."""
import csv, json, os, re, random, subprocess, sys, statistics as st, tempfile, itertools
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); W = os.path.join(R, 'work', 'REP1'); I = os.path.join(H, 'inputs'); O = os.path.join(R, 'out')
SURV = os.path.join(W, 'code_surviving'); SRC = os.path.join(W, 'inputs_surviving', 'inscriptions.csv')
J2 = os.path.join(R, 'stage2', 'inputs'); os.makedirs(I, exist_ok=True)
def seal_key(r):  # contest.py's own row filter; returns the text tuple or None
    t = r['text'].strip(); ss = [s for s in re.findall(r'\d{3}', t) if s != '999']
    if not ss or ('[' in t or ']' in t or '/' in t) or r['dir.'] not in ('R/L', 'L/R') or '000' in ss or len(ss) < 2 or not r['type'].startswith('SEAL'): return None
    return tuple(ss)
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
def wjl(p, rows):
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
JCFG = json.load(open(os.path.join(J2, 'cfg_japanese.json')))
TCFG = json.load(open(os.path.join(W, 'inputs', 'cfg_headline_tamil.json')))
def cfg(base, basedir, names_path, corpus, lang, d):
    c = dict(base, lang=lang, corpus=os.path.abspath(corpus), names=os.path.abspath(names_path))
    for k in ('parts', 'words'): c[k] = os.path.abspath(os.path.join(basedir, base[k]))
    for k in ('corpus', 'names', 'parts', 'words'): c[k] = os.path.relpath(c[k], os.path.abspath(d))  # relative paths: no local path in committed configs
    p = os.path.join(d, f'cfg_{lang}.json'); json.dump(c, open(p, 'w', encoding='utf-8'), ensure_ascii=False); return p
def job(a):
    cfgp, seed, mode, out = a
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', cfgp, str(seed), mode, out], cwd=W, env=dict(os.environ, RAJ_SURV=SURV), capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-800:])
EX = ThreadPoolExecutor(4)
def D(cfgp, lang, seeds, out):
    list(EX.map(job, [(cfgp, s, m, out) for s in seeds for m in ('real', 'null')]))
    return [json.load(open(f'{out}/{lang}_real_{s}.json'))['heldout'] - json.load(open(f'{out}/{lang}_null_{s}.json'))['heldout'] for s in seeds]
step = sys.argv[1]
if step == 'split':
    rows = list(csv.DictReader(open(SRC, encoding='utf-8'))); keys = sorted({k for k in map(seal_key, rows) if k})
    rnd = random.Random(20261127); rnd.shuffle(keys); A = set(keys[:len(keys) // 2])
    for half, test in (('A', lambda k: k in A), ('B', lambda k: k is not None and k not in A)):
        with open(os.path.join(I, f'corpus_{half}.csv'), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader()
            for r in rows:
                if test(seal_key(r)): w.writerow(r)
    print('unique seal texts', len(keys), 'A', len(A), 'B', len(keys) - len(A))
elif step == 'search':
    names = jl(os.path.join(J2, 'names_japanese.jsonl')); N = len(names); K = N // 2
    cur = set(random.Random(1).sample(range(N), K)); rnd = random.Random(2); tmp = tempfile.mkdtemp(prefix='t9s_')
    def obj(sel, tag):
        npth = os.path.join(tmp, 'names.jsonl'); wjl(npth, [names[i] for i in sorted(sel)])
        return st.mean(D(cfg(JCFG, J2, npth, os.path.join(I, 'corpus_A.csv'), 'jsearch', tmp), 'jsearch', range(5), tmp))
    best = obj(cur, 0); log = [(0, best)]; print('start', round(best, 1), flush=True)
    for it in range(1, 1501):
        a = rnd.choice(sorted(cur)); b = rnd.choice(sorted(set(range(N)) - cur))
        cand = (cur - {a}) | {b}; v = obj(cand, it)
        if v > best: cur, best = cand, v; log.append((it, best))
        if it % 50 == 0: print(it, round(best, 1), flush=True)
    wjl(os.path.join(I, 'names_jpick.jsonl'), [names[i] for i in sorted(cur)])
    json.dump({'start': log[0][1], 'final': best, 'accepted': log}, open(os.path.join(H, 'search_log.json'), 'w'), indent=0)
    print('final', round(best, 1), 'accepted', len(log) - 1)
elif step == 'test':
    jn = jl(os.path.join(J2, 'names_japanese.jsonl')); tpath = os.path.join(W, 'inputs', TCFG['names']); tn = jl(tpath); res = {}
    B = os.path.join(I, 'corpus_B.csv'); TW = os.path.join(W, 'inputs')
    def run(tag, base, bdir, rows, corpus):
        d = os.path.join(O, 'T9', tag); os.makedirs(d, exist_ok=True); p = os.path.join(I, f'names_{tag}.jsonl')
        if rows is not None: wjl(p, rows)
        x = D(cfg(base, bdir, p if rows is not None else tpath, corpus, tag, I), tag, range(10), d)
        res[tag] = {'D': round(st.mean(x), 1), 'sd': round(st.stdev(x), 1), 'above': sum(v > 0 for v in x), 'seeds': [round(v, 1) for v in x]}; print(tag, res[tag], flush=True)
    run('jpick_B', JCFG, J2, jl(os.path.join(I, 'names_jpick.jsonl')), B)
    run('tpaper_B', TCFG, TW, None, B)
    for s in range(11, 16):
        run(f'jrand{s}_B', JCFG, J2, random.Random(s).sample(jn, len(jn) // 2), B)
        run(f'trand{s}_B', TCFG, TW, random.Random(s).sample(tn, 562), B)
    run('jpick_full', JCFG, J2, jl(os.path.join(I, 'names_jpick.jsonl')), SRC)
    res['J_rand_median'] = st.median(res[f'jrand{s}_B']['D'] for s in range(11, 16)); res['T_rand_median'] = st.median(res[f'trand{s}_B']['D'] for s in range(11, 16))
    jp, tp, jr = res['jpick_B']['D'], res['tpaper_B']['D'], res['J_rand_median']
    res['reading'] = ('Picking alone lifts a wrong language to the paper\'s Tamil level' if jp >= tp else
                      'Picking lifts it part of the way' if jr < jp < tp and jp - jr >= 0.5 * (tp - jr) else 'Picking does not generalise')
    json.dump(res, open(os.path.join(O, 'T9_summary.json'), 'w'), indent=1); print(res['reading'], 'J_pick', jp, 'T_paper', tp, 'J_rand', jr, 'T_rand', res['T_rand_median'])
