# REP-1 contest script (as step0/code/contest.py, plus the 'weights' setting: stored = counts in the names file, once = each name counts 1).
# One run = one seed, one mode (real | null). Language-general: all inputs are given as paths.
# usage: python3 contest.py CONFIG.json SEED MODE OUTDIR
import sys, os, json, random, collections, statistics, time, csv, re
HERE = os.path.dirname(os.path.abspath(__file__))
SURV = os.environ['RAJ_SURV']; sys.path.insert(0, SURV)
import decoder, nphon
from functools import lru_cache
CFG = json.load(open(sys.argv[1], encoding='utf-8')); SEED = int(sys.argv[2]); MODE = sys.argv[3]; OUT = sys.argv[4]
os.makedirs(OUT, exist_ok=True); t0 = time.time()
BASE = os.path.dirname(os.path.abspath(sys.argv[1]))
def P(k): return os.path.join(BASE, CFG[k])
# seal texts: as common.py
rows = list(csv.DictReader(open(P('corpus'), encoding='utf-8'))); seen = set(); S = []
for r in rows:
    t = r['text'].strip(); ss = [s for s in re.findall(r'\d{3}', t) if s != '999']
    if not ss or ('[' in t or ']' in t or '/' in t) or r['dir.'] not in ('R/L', 'L/R') or '000' in ss or len(ss) < 2 or not r['type'].startswith('SEAL') or tuple(ss) in seen: continue
    seen.add(tuple(ss)); S.append(ss[::-1])
# --- control hook (raj_check): fake seals. CTL_FAKE = 'order:<seed>' or 'iid:<seed>' ---
_F = os.environ.get('CTL_FAKE')
if _F:
    _kind, _fs = _F.split(':'); _r = random.Random(int(_fs) * 7919 + 13)
    if _kind == 'order':
        S = [_r.sample(t, len(t)) for t in S]
    elif _kind == 'iid':
        _cnt = collections.Counter(x for t in S for x in t); _pop = list(_cnt); _w = [_cnt[x] for x in _pop]
        S = [_r.choices(_pop, weights=_w, k=len(t)) for t in S]
    else: raise SystemExit('bad CTL_FAKE')
NUMSIGN = {'032': 2, '033': 3, '031': 1, '001': 1, '003': 3, '017': 7, '004': 4, '055': 12, '005': 5, '013': 3, '016': 6}
NUMW = {int(k): v for k, v in CFG['number_words'].items()}
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
info = {}; LOANS = set(CFG.get('drop_parts', []))
for x in jl(P('parts')):
    if x.get('category') == CFG.get('loan_category', 'sanskrit_loan'): LOANS.add(nphon.norm(x['m']))
    info[nphon.norm(x['m'])] = x
KEEP_NONINITIAL = set(CFG.get('keep_noninitial', []))
def clean(ms):
    ms = [nphon.norm(m) for m in ms if m]
    return [m for i, m in enumerate(ms) if m and not (m in LOANS and not (m in KEEP_NONINITIAL and i > 0))]
named = []
for n in jl(P('names')):
    ms = clean(n['morphemes'])
    if ms: named.append((ms, n.get('weight', 1) if CFG.get('weights', 'stored') == 'stored' else 1))
pw = collections.defaultdict(set)
for s, d in json.load(open(P('words'), encoding='utf-8')).items():
    for ws in d.values(): pw[s] |= {nphon.norm(w) for w in ws}
for s in NUMSIGN: pw.pop(s, None)
# --- control hook (raj_check): permute picture-word sets among signs. CTL_PERM = '<seed>' ---
if os.environ.get('CTL_PERM'):
    _ks = sorted(pw); _vs = [pw[k] for k in _ks]; random.Random(int(os.environ['CTL_PERM']) * 104729 + 7).shuffle(_vs)
    pw = collections.defaultdict(set, dict(zip(_ks, _vs)))
fixed = {s: NUMW[v] for s, v in NUMSIGN.items()}
top = set(pw) | set(NUMSIGN)
corpus = [[x if x in top else 'GAP' for x in t] for t in S]
seals = [t for t in corpus if t.count('GAP') <= 1 and len(t) - t.count('GAP') >= 2]
si = list(range(len(seals))); random.Random(800 + SEED).shuffle(si)
S1 = [seals[i] for i in si[:len(si) // 2]]; S2 = [seals[i] for i in si[len(si) // 2:]]
def scramble(names, seed):
    pool = [m for n, _ in names for m in n]; r = random.Random(seed); r.shuffle(pool); it = iter(pool)
    return [([next(it) for _ in n], w) for n, w in names]
def model(nms):
    nm = decoder.NameModel(nms, info); nm.breaks = True; nm.break_p = 0.3
    nm.lp = lru_cache(maxsize=None)(nm.logp); return nm
FULL = scramble(named, 7000 + SEED) if MODE == 'null' else named
idx = list(range(len(FULL))); random.Random(500 + SEED).shuffle(idx)
A = [FULL[i] for i in idx[:len(idx) // 2]]; B = [FULL[i] for i in idx[len(idx) // 2:]]
MA = [model(A)] + [model(scramble(A, 3000 + i)) for i in range(8)]
MB = [model(B)] + [model(scramble(B, 4000 + i)) for i in range(8)]
voc = collections.Counter(m for n, _ in FULL for m in n)
celems = sorted(m for m, c in voc.items() if len(m) >= 2 and c >= 2 and m not in fixed.values())
SIGNS = sorted(s for s in pw if any(s in t for t in seals))
pc = lru_cache(maxsize=None)(nphon.pun_cost); eset = set(celems); PUNMAX = float(CFG.get('punmax', 0.5))
PIC = {}
for s in SIGNS:
    c = set()
    for w in pw[s]:
        if w in eset: c.add(w)
        for m in celems:
            if abs(len(m) - len(w)) <= 3 and m[:1] == w[:1] and pc(m, w) <= PUNMAX: c.add(m)
    PIC[s] = sorted(c)
def slots_of(sl):
    sl_ = collections.defaultdict(collections.Counter)
    for t in sl:
        seq = ['<s>'] + t + ['</s>']
        for j in range(len(seq) - 1):
            a, b = seq[j], seq[j + 1]
            for s in {a, b} & set(SIGNS): sl_[s][(a, b)] += 1
    return sl_
SL1, SL2 = slots_of(S1), slots_of(S2)
nocc = collections.Counter(x for t in S1 for x in t)
def val(x, a): return a.get(x) or fixed.get(x) or ('GAP' if x not in ('<s>', '</s>') else x)
def gain(s, m, a, models, slots):
    pairs = []
    for (l, r), n in slots[s].items():
        l1 = m if l == s else val(l, a); r1 = m if r == s else val(r, a)
        l0 = 'GAP' if l == s else val(l, a); r0 = 'GAP' if r == s else val(r, a)
        pairs.append((n, l1, r1, l0, r0))
    out = [sum(n * (mm.lp(l1, r1) - mm.lp(l0, r0)) for n, l1, r1, l0, r0 in pairs) for mm in models]
    return out[0] - statistics.mean(out[1:])
def score(a, sl, models):
    tot = 0.0
    for t in sl:
        seq = ['<s>'] + [val(x, a) for x in t] + ['</s>']
        v = [sum(mm.lp(p, q) for p, q in zip(seq, seq[1:])) for mm in models]; tot += v[0] - statistics.mean(v[1:])
    return tot
def select(cands, sweeps=2):
    a = {s: 'GAP' for s in SIGNS}
    for sw in range(sweeps):
        for s in sorted(SIGNS, key=lambda s: -nocc[s]):
            used = {v for k, v in a.items() if k != s and v != 'GAP'}
            best, bm = 0.0, 'GAP'
            for m in cands.get(s, []):
                if m in used: continue
                g = gain(s, m, a, MA, SL1)
                if g > best: best, bm = g, m
            a[s] = bm
    return a
a = select(PIC); read = {s: v for s, v in a.items() if v != 'GAP'}
ho = score(a, S2, MB)
res = {'lang': CFG['lang'], 'seed': SEED, 'mode': MODE, 'names': len(named), 'name_parts': len(celems), 'seals': len(seals), 'signs': len(SIGNS),
       'pic_mean_opts': round(statistics.mean(len(v) for v in PIC.values()), 2), 'signs_with_options': sum(1 for v in PIC.values() if v),
       'read': len(read), 'heldout': round(ho, 2), 'readings': read, 'secs': round(time.time() - t0)}
res['ctl'] = {'perm': os.environ.get('CTL_PERM'), 'fake': os.environ.get('CTL_FAKE')}
json.dump(res, open(f'{OUT}/{CFG["lang"]}_{MODE}_{SEED}.json', 'w'), ensure_ascii=False, indent=1)
print({k: res[k] for k in ('lang', 'seed', 'mode', 'names', 'seals', 'signs', 'pic_mean_opts', 'read', 'heldout', 'secs')}, flush=True)
