"""Stage 3: build contest inputs from the agent outputs (PREREG_STAGE3.md steps 2-6).
  python3 -I stage3/build_inputs.py parts <lang>  -> agents/parts_<lang>.jsonl (labeler input)
  python3 -I stage3/build_inputs.py final <lang>  -> inputs/{names,parts,words}_<lang>*, cfg_<lang>.json
"""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, 'agents'); I = os.path.join(H, 'inputs')
sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving')); import nphon
REP1 = os.path.join(H, '..', 'work', 'REP1', 'inputs')
NUM = {'sumerian': {'1': 'dish', '2': 'min', '3': 'esh', '4': 'limmu', '5': 'ia', '6': 'ash', '7': 'imin', '12': 'umin'},
       'egyptian': {'1': 'wa', '2': 'senwy', '3': 'khemet', '4': 'fedu', '5': 'diu', '6': 'sisu', '7': 'sefekh', '12': 'medjsenwy'},
       'finnish': {'1': 'yksi', '2': 'kaksi', '3': 'kolme', '4': 'nelja', '5': 'viisi', '6': 'kuusi', '7': 'seitseman', '12': 'kaksitoista'}}
step, L = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(os.path.join(A, f'names_{L}.jsonl'), encoding='utf-8') if l.strip()]
rows.sort(key=lambda r: r['rank'])
def parts(r, kinds): return [nphon.norm(p['m']) for p in r['parts'] if p.get('origin') in kinds and nphon.norm(p['m'])]
keep = []
for r in rows:
    if parts(r, ('native',)): keep.append(r)
    if len(keep) == 1125: break
if step == 'parts':
    cnt = collections.Counter(); gl = {}
    for r in keep:
        for p in r['parts']:
            m = nphon.norm(p['m'])
            if p.get('origin') in ('native', 'suffix') and m:
                cnt[m] += 1; gl.setdefault(m, collections.Counter())[p.get('gloss', 'name')] += 1
    with open(os.path.join(A, f'parts_{L}.jsonl'), 'w', encoding='utf-8') as f:
        for m in sorted(cnt): f.write(json.dumps({'part': m, 'gloss': gl[m].most_common(1)[0][0], 'in_names': cnt[m]}, ensure_ascii=False) + '\n')
    print(L, 'names kept', len(keep), 'last rank', keep[-1]['rank'], 'native+suffix parts', len(cnt),
          'loan parts', sum(1 for r in keep for p in r['parts'] if p.get('origin') == 'loan'))
else:
    os.makedirs(I, exist_ok=True)
    stab = json.load(open(os.path.join(REP1, 'category_stability.json'))); stab['loan'] = 1
    lab = {json.loads(l)['part']: json.loads(l)['category'] for l in open(os.path.join(A, f'labels_{L}.jsonl'), encoding='utf-8') if l.strip()}
    with open(os.path.join(I, f'names_{L}.jsonl'), 'w', encoding='utf-8') as f:
        for r in keep: f.write(json.dumps({'name': r['name'], 'morphemes': [p['m'] for p in r['parts'] if nphon.norm(p['m'])], 'weight': 1}, ensure_ascii=False) + '\n')
    loans = set(m for r in keep for m in parts(r, ('loan',))) - set(lab)
    with open(os.path.join(I, f'parts_{L}.jsonl'), 'w', encoding='utf-8') as f:
        for m, c in sorted(lab.items()): f.write(json.dumps({'m': m, 'category': c, 'stability': stab.get(c, 2)}, ensure_ascii=False) + '\n')
        for m in sorted(loans): f.write(json.dumps({'m': m, 'category': 'loan', 'stability': 1}, ensure_ascii=False) + '\n')
    tr = json.load(open(os.path.join(A, f'words_{L}.json'), encoding='utf-8'))
    se = json.load(open(os.path.join(REP1, 'sign_english_words.json'), encoding='utf-8'))
    words = {s: {e: tr[e] for e in es} for s, es in se.items()}
    json.dump(words, open(os.path.join(I, f'words_{L}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    cfg = {'corpus': '../../work/REP1/inputs_surviving/inscriptions.csv', 'punmax': 0.5, 'lang': L,
           'names': f'names_{L}.jsonl', 'parts': f'parts_{L}.jsonl', 'number_words': NUM[L],
           'drop_parts': [], 'keep_noninitial': [], 'loan_category': 'loan', 'words': f'words_{L}.json', 'weights': 'once'}
    json.dump(cfg, open(os.path.join(I, f'cfg_{L}.json'), 'w'), indent=1)
    draw = {'animal', 'plant', 'body_part', 'artefact', 'landscape', 'celestial'}
    print(L, 'names', len(keep), 'labelled parts', len(lab), 'loan parts', len(loans), 'filled english', sum(1 for v in tr.values() if v),
          'drawable share of labelled parts', round(sum(c in draw for c in lab.values()) / len(lab), 3))
