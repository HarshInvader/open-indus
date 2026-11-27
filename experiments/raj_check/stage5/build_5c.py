"""Stage 5c inputs: python3 -I stage5/build_5c.py v1|v2  -> inputs/names_jsym_<v>.jsonl, parts_jsym_<v>.jsonl (PREREG_STAGE5C.md)."""
import json, os, sys, random, collections
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); A = os.path.join(H, 'agents'); I = os.path.join(H, 'inputs')
sys.path.insert(0, os.path.join(R, 'work', 'REP1', 'code_surviving')); import nphon
v = sys.argv[1]; tag = f'jsym_{v}'
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
pool = jl(os.path.join(A, 'names_jsym.jsonl')) + (jl(os.path.join(A, 'names_jsym3.jsonl')) if v == 'v2' else [])
seen = set(); pool = [r for r in pool if not (r['name'] in seen or seen.add(r['name']))]
native = lambda r: [nphon.norm(p['m']) for p in r['parts'] if p.get('origin') == 'native' and nphon.norm(p['m'])]
pool = [r for r in pool if native(r)]
CLS = {'family': 'family', 'place': 'place', 'island': 'place', 'cape': 'place', 'lake': 'place', 'deity': 'deity', 'shrine': 'deity', 'clan': 'clan', 'mountain': 'mountain', 'river': 'river', 'other': 'other'}
TARGET = {'family': 532, 'deity': 98, 'clan': 124, 'mountain': 33, 'river': 14, 'other': 84}
by = collections.defaultdict(list)
for r in pool: by[CLS.get(r.get('type'), 'other')].append(r)
rnd = random.Random(20261127); out = []
for c, n in TARGET.items():
    take = by[c] if len(by[c]) <= n else rnd.sample(by[c], n); out += take
out += rnd.sample(by['place'], min(len(by['place']), 1125 - len(out)))
lab = {}
for p in ('../stage2/agents/labels_japanese.jsonl', 'agents/labels_jsym2.jsonl') + (('agents/labels_jsym3.jsonl',) if v == 'v2' else ()):
    for x in jl(os.path.join(H, p)): lab[x['part']] = x['category']
stab = json.load(open(os.path.join(R, 'work', 'REP1', 'inputs', 'category_stability.json'))); stab['sino_loan'] = 1
miss = {m for r in out for m in native(r)} - set(lab)
sino = {nphon.norm(p['m']) for r in out for p in r['parts'] if p.get('origin') == 'sino'} - set(lab)
with open(os.path.join(I, f'names_{tag}.jsonl'), 'w', encoding='utf-8') as f:
    for r in out: f.write(json.dumps({'name': r['name'], 'type': r.get('type'), 'morphemes': [p['m'] for p in r['parts']], 'weight': 1}, ensure_ascii=False) + '\n')
with open(os.path.join(I, f'parts_{tag}.jsonl'), 'w', encoding='utf-8') as f:
    for m, c in sorted(lab.items()): f.write(json.dumps({'m': m, 'category': c, 'stability': stab.get(c, 2)}, ensure_ascii=False) + '\n')
    for m in sorted(sino): f.write(json.dumps({'m': m, 'category': 'sino_loan', 'stability': 1}, ensure_ascii=False) + '\n')
print(tag, 'names', len(out), collections.Counter(CLS.get(r.get('type'), 'other') for r in out), 'unlabelled native', len(miss))
