"""Stage 2: build Japanese contest inputs from the agent outputs (prereg PREREG_STAGE2.md steps 2-5).
  python3 -I stage2/build_inputs.py parts   -> agents/parts_japanese.jsonl (labeler input)
  python3 -I stage2/build_inputs.py final   -> inputs/{names,parts,words}_japanese*, cfg_japanese.json
"""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, 'agents'); I = os.path.join(H, 'inputs')
sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving')); import nphon
REP1 = os.path.join(H, '..', 'work', 'REP1', 'inputs')
rows = [json.loads(l) for l in open(os.path.join(A, 'names_japanese.jsonl'), encoding='utf-8') if l.strip()]
rows.sort(key=lambda r: r['rank'])
def native(r): return [nphon.norm(p['m']) for p in r['parts'] if p.get('origin') == 'native' and nphon.norm(p['m'])]
keep = []
for r in rows:
    if native(r): keep.append(r)
    if len(keep) == 1125: break
if sys.argv[1] == 'parts':
    cnt = collections.Counter(); gl = {}
    for r in keep:
        for p in r['parts']:
            if p.get('origin') == 'native' and nphon.norm(p['m']):
                m = nphon.norm(p['m']); cnt[m] += 1; gl.setdefault(m, collections.Counter())[p.get('gloss', 'name')] += 1
    with open(os.path.join(A, 'parts_japanese.jsonl'), 'w', encoding='utf-8') as f:
        for m in sorted(cnt): f.write(json.dumps({'part': m, 'gloss': gl[m].most_common(1)[0][0], 'in_names': cnt[m]}, ensure_ascii=False) + '\n')
    print('names kept', len(keep), 'last rank', keep[-1]['rank'], 'native parts', len(cnt),
          'sino parts dropped', sum(1 for r in keep for p in r['parts'] if p.get('origin') == 'sino'))
else:
    os.makedirs(I, exist_ok=True)
    stab = json.load(open(os.path.join(REP1, 'category_stability.json'))); stab['sino_loan'] = 1
    lab = {json.loads(l)['part']: json.loads(l)['category'] for l in open(os.path.join(A, 'labels_japanese.jsonl'), encoding='utf-8') if l.strip()}
    with open(os.path.join(I, 'names_japanese.jsonl'), 'w', encoding='utf-8') as f:
        for r in keep: f.write(json.dumps({'name': r['kanji'], 'morphemes': [p['m'] for p in r['parts']], 'weight': 1}, ensure_ascii=False) + '\n')
    sino = {nphon.norm(p['m']) for r in keep for p in r['parts'] if p.get('origin') == 'sino'} - set(lab)
    miss = []
    with open(os.path.join(I, 'parts_japanese.jsonl'), 'w', encoding='utf-8') as f:
        for m, c in sorted(lab.items()): f.write(json.dumps({'m': m, 'category': c, 'stability': stab.get(c, 2)}, ensure_ascii=False) + '\n')
        for m in sorted(sino): f.write(json.dumps({'m': m, 'category': 'sino_loan', 'stability': 1}, ensure_ascii=False) + '\n')
    tr = json.load(open(os.path.join(A, 'words_japanese.json'), encoding='utf-8'))
    se = json.load(open(os.path.join(REP1, 'sign_english_words.json'), encoding='utf-8'))
    words = {s: {e: tr[e] for e in es} for s, es in se.items()}
    json.dump(words, open(os.path.join(I, 'words_japanese.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    cfg = {'corpus': '../../work/REP1/inputs_surviving/inscriptions.csv', 'punmax': 0.5, 'lang': 'japanese',
           'names': 'names_japanese.jsonl', 'parts': 'parts_japanese.jsonl',
           'number_words': {'1': 'hito', '2': 'futa', '3': 'mi', '4': 'yo', '5': 'itsu', '6': 'mu', '7': 'nana', '12': 'to'},
           'drop_parts': [], 'keep_noninitial': [], 'loan_category': 'sino_loan', 'words': 'words_japanese.json', 'weights': 'once'}
    json.dump(cfg, open(os.path.join(I, 'cfg_japanese.json'), 'w'), indent=1)
    print('names', len(keep), 'labelled parts', len(lab), 'sino parts', len(sino), 'filled english', sum(1 for v in tr.values() if v))
