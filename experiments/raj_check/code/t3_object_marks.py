"""T3: chance base rate for 'object marks' (prereg T3). Uses Raj's REP-7 scan definition on the lipi corpus."""
import csv, re, json, os, random, collections
from math import comb
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(H, '..', '..', '..')
SRC = os.path.join(ROOT, 'sources', 'raj_zenodo_24383779_v0.7')
R = [(r['type'].strip(), set(re.findall(r'\d{3}', r['text'])), r['text']) for r in csv.DictReader(open(os.path.join(ROOT, 'sources', 'lipi_inscriptions_fc8813a', 'inscriptions.csv'), encoding='utf-8'))]
N = len(R)
def fisher(a, b, c, d):
    n1 = a + b; K = a + c; T = a + b + c + d
    return sum(comb(K, x) * comb(T - K, n1 - x) for x in range(a, min(n1, K) + 1)) / comb(T, n1)
def case(sig, typ, rows):
    a = sum(1 for t, s, _ in rows if t == typ and sig in s); n1 = sum(1 for t, _, _ in rows if t == typ)
    c = sum(1 for t, s, _ in rows if t != typ and sig in s); n2 = len(rows) - n1
    return a, n1, c, n2, fisher(a, n1 - a, c, n2 - c)
sc = collections.Counter(s for _, ss, _ in R for s in ss); tc = collections.Counter(t for t, _, _ in R)
signs = [s for s, v in sc.items() if v >= 5 and s != '000']; types = [t for t, v in tc.items() if v >= 20]
bonf = 0.05 / (len(signs) * len(types))
passed = [(s, t) for s in signs for t in types if case(s, t, R)[4] < bonf]
# readings
G = {}
for r in csv.DictReader(open(os.path.join(SRC, 'Indus_Sign_Readings_v0.7.csv'), encoding='utf-8-sig')):
    G[r['sign'].strip()] = r['gloss'].lower()
RULE = {'BNGL': ['armlet', 'bangle', 'bracelet', 'ring'], 'TAB:C': ['copper', 'metal', 'metal-work', 'smith', 'bronze'],
        'POT:T:g': ['pot', 'jar', 'vessel', 'pitcher', 'potter'], 'POT:T:s': ['pot', 'jar', 'vessel', 'pitcher', 'potter'],
        'TAG': ['tag', 'label', 'token'], 'TAG:L': ['tag', 'label', 'token'], 'ROD': ['rod', 'stick', 'staff'],
        'IMPL': ['tool', 'axe', 'knife', 'chisel', 'implement'], 'TAB:B': ['tablet', 'token'], 'TAB:I': ['tablet', 'token']}
for t in ('SEAL', 'SEAL:S', 'SEAL:R', 'SEAL:C'): RULE[t] = ['seal', 'stamp']
def names(gloss, typ):
    return any(re.search(r'(?<![a-z-])' + re.escape(w) + r'(?![a-z-])', gloss) for w in RULE.get(typ, []))
read = sorted(s for s in signs if s in G)
def count(assign):
    return [(s, t) for s, t in passed if s in assign and names(assign[s], t)]
obs = count({s: G[s] for s in read})
rng = random.Random(20261127); null = []
gl = [G[s] for s in read]
for _ in range(100000):
    rng.shuffle(gl); a = dict(zip(read, gl)); null.append(len(count(a)))
nc = collections.Counter(null)
p = (1 + sum(1 for x in null if x >= len(obs))) / (len(null) + 1)
# duplication on copper tablets
def distinct_case(sig, typ):
    seen = set(); rows = []
    for t, s, txt in R:
        key = (t, re.sub(r'\s', '', txt))
        if key in seen: continue
        seen.add(key); rows.append((t, s, txt))
    a, n1, c, n2, pv = case(sig, typ, rows); return dict(on_type=a, type_rows=n1, on_others=c, other_rows=n2, p=pv)
dup = {}
for sig, typ in (('840', 'BNGL'), ('061', 'TAB:C'), ('705', 'TAB:C'), ('706', 'TAB:C')):
    a, n1, c, n2, pv = case(sig, typ, R)
    txts = [txt for t, s, txt in R if t == typ and sig in s]
    dup[f'{sig}/{typ}'] = dict(rows=dict(on_type=a, type_rows=n1, on_others=c, other_rows=n2, p=pv), distinct_texts_on_type=len(set(txts)),
                               distinct_rows_test=distinct_case(sig, typ), bonferroni=bonf)
out = dict(rows=N, signs=len(signs), types=types, bonferroni=bonf, passed=len(passed), read_signs_in_scan=len(read),
           read_signs_among_passed=len({s for s, _ in passed if s in G}),
           observed=len(obs), observed_pairs=obs, null_mean=sum(null) / len(null), null_dist=dict(sorted(nc.items())),
           null_p99=sorted(null)[int(0.99 * len(null))], p=p, copper_and_bangle=dup)
json.dump(out, open(os.path.join(H, '..', 'out', 'T3_object_marks.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != 'types'}, indent=1, ensure_ascii=False))
