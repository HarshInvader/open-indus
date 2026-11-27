"""Stage 5b diagnostic: share of names with a picture-candidate part, by contest.py's own rules.
  python3 -I stage5/diag_5b.py            -> prints table, writes out/T9b_diag.json
  python3 -I stage5/diag_5b.py pick       -> also writes inputs/names_jsym1.jsonl (J_sym1)"""
import json, os, sys, collections, re
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); W = os.path.join(R, 'work', 'REP1')
sys.path.insert(0, os.path.join(W, 'code_surviving')); import nphon
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
def analyse(cfgp):
    base = os.path.dirname(cfgp); C = json.load(open(cfgp, encoding='utf-8')); P = lambda k: os.path.join(base, C[k])
    LOANS = set(C.get('drop_parts', [])); KN = set(C.get('keep_noninitial', []))
    for x in jl(P('parts')):
        if x.get('category') == C.get('loan_category', 'sanskrit_loan'): LOANS.add(nphon.norm(x['m']))
    def clean(ms):
        ms = [nphon.norm(m) for m in ms if m]
        return [m for i, m in enumerate(ms) if m and not (m in LOANS and not (m in KN and i > 0))]
    raw = jl(P('names')); named = [(n, clean(n['morphemes'])) for n in raw]; named = [(n, ms) for n, ms in named if ms]
    fixedv = set(C['number_words'].values())
    voc = collections.Counter(m for _, ms in named for m in ms)
    celems = sorted(m for m, c in voc.items() if len(m) >= 2 and c >= 2 and m not in fixedv)
    pw = set()
    for s, d in json.load(open(P('words'), encoding='utf-8')).items():
        for ws in d.values(): pw |= {nphon.norm(w) for w in ws}
    pc = nphon.pun_cost; eset = set(celems); PM = float(C.get('punmax', 0.5)); cand = set()
    for w in pw:
        if w in eset: cand.add(w)
        for m in celems:
            if abs(len(m) - len(w)) <= 3 and m[:1] == w[:1] and pc(m, w) <= PM: cand.add(m)
    hit = [n for n, ms in named if any(m in cand for m in ms)]
    top = collections.Counter(m for _, ms in named for m in set(ms) if m in cand).most_common(8)
    return {'names': len(named), 'with_picture_part': len(hit), 'share': round(len(hit) / len(named), 3), 'candidate_parts': len(cand), 'top_parts': top}, hit
S4 = os.path.join(R, 'stage4', 'inputs')
LISTS = [('Tamil, paper', os.path.join(W, 'inputs', 'cfg_headline_tamil.json')),
         ('Tamil, 4b list', os.path.join(S4, 'cfg_tamil4b.json')),
         ('Tamil, faithful list (T8b)', os.path.join(S4, 'cfg_tamilf4b.json')),
         ('C6 paper-only names', os.path.join(S4, 'cfg_tamil4c_c6.json')),
         ('C7 4b-only names', os.path.join(S4, 'cfg_tamil4c_c7.json')),
         ('Japanese T4', os.path.join(R, 'stage2', 'inputs', 'cfg_japanese.json'))]
out = {}
for lab, p in LISTS:
    if not os.path.exists(p): print('missing', lab, p); continue
    out[lab], hit = analyse(p); print(f'{lab:30s}', out[lab])
    if lab == 'Japanese T4' and len(sys.argv) > 1 and sys.argv[1] == 'pick':
        with open(os.path.join(H, 'inputs', 'names_jsym1.jsonl'), 'w', encoding='utf-8') as f:
            for n in hit: f.write(json.dumps(n, ensure_ascii=False) + '\n')
        print('J_sym1 written', len(hit))
json.dump(out, open(os.path.join(R, 'out', 'T9b_diag.json'), 'w'), ensure_ascii=False, indent=1)
