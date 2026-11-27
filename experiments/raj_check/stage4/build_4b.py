"""Stage 4b: build contest inputs from the agent outputs (PREREG_STAGE4B.md).
  python3 -I stage4/build_4b.py parts <lang>   -> agents/parts_<lang>.jsonl (labeler input)
  python3 -I stage4/build_4b.py sample         -> agents/checker_samples.json (50 names + 50 words per language, seed 20261127)
  python3 -I stage4/build_4b.py final <lang>   -> inputs/{names,parts,words}_<lang>4b*, cfg_<lang>4b.json
"""
import json, os, sys, random, collections
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, 'agents'); I = os.path.join(H, 'inputs')
sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving')); import nphon
REP1 = os.path.join(H, '..', 'work', 'REP1', 'inputs')
LANGS = ('tamil', 'kannada', 'telugu', 'malayalam')
NUM = {'tamil': {'1': 'oru', '2': 'iru', '3': 'mū', '4': 'nāl', '5': 'ai', '6': 'aṟu', '7': 'ēḻu', '12': 'pattu'},
       'kannada': {'1': 'ondu', '2': 'eraḍu', '3': 'mūru', '4': 'nālku', '5': 'aydu', '6': 'āru', '7': 'ēḷu', '12': 'panneraḍu'},
       'telugu': {'1': 'okaṭi', '2': 'reṇḍu', '3': 'mūḍu', '4': 'nālugu', '5': 'aidu', '6': 'āru', '7': 'ēḍu', '12': 'panneṇḍu'},
       'malayalam': {'1': 'oṉṉu', '2': 'raṇṭu', '3': 'mūṉṉu', '4': 'nālu', '5': 'añcu', '6': 'āṟu', '7': 'ēḻu', '12': 'pantraṇṭu'}}
def names(L):
    out, seen = [], set()
    for l in open(os.path.join(A, f'names_{L}.jsonl'), encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        if r['name'] in seen: continue
        seen.add(r['name']); out.append(r)
    return out
def glosses(r):
    g = [x.strip() for x in str(r.get('gloss', '')).split('+')]
    return [g[i] if i < len(g) and g[i] else 'name' for i in range(len(r['morphemes']))]
step = sys.argv[1]
if step == 'sample':
    rnd = random.Random(20261127); out = {}
    for L in LANGS:
        ns = names(L); w = json.load(open(os.path.join(A, f'words_{L}.json'), encoding='utf-8'))
        pairs = [(e, x) for e, v in w.items() for x in v]
        out[L] = {'names': rnd.sample(ns, min(50, len(ns))), 'words': [{'english': e, 'word': x} for e, x in rnd.sample(pairs, min(50, len(pairs)))]}
    json.dump(out, open(os.path.join(A, 'checker_samples.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('samples written')
    sys.exit()
L = sys.argv[2]; ns = names(L)
if step == 'parts':
    cnt = collections.Counter(); gl = {}
    for r in ns:
        for m, g in zip(r['morphemes'], glosses(r)):
            m = nphon.norm(m)
            if m: cnt[m] += 1; gl.setdefault(m, collections.Counter())[g] += 1
    with open(os.path.join(A, f'parts_{L}.jsonl'), 'w', encoding='utf-8') as f:
        for m in sorted(cnt): f.write(json.dumps({'part': m, 'gloss': gl[m].most_common(1)[0][0], 'in_names': cnt[m]}, ensure_ascii=False) + '\n')
    print(L, 'names', len(ns), 'parts', len(cnt), 'types', collections.Counter(r.get('type') for r in ns).most_common())
else:
    os.makedirs(I, exist_ok=True)
    stab = json.load(open(os.path.join(REP1, 'category_stability.json')))
    lab = {json.loads(l)['part']: json.loads(l)['category'] for l in open(os.path.join(A, f'labels_{L}.jsonl'), encoding='utf-8') if l.strip()}
    keep = [r for r in ns if any(lab.get(nphon.norm(m)) not in (None, 'sanskrit_loan') for m in r['morphemes'])][:1125]
    tag = f'{L}4b'
    with open(os.path.join(I, f'names_{tag}.jsonl'), 'w', encoding='utf-8') as f:
        for r in keep: f.write(json.dumps({'name': r['name'], 'type': r.get('type'), 'morphemes': r['morphemes'], 'weight': 1}, ensure_ascii=False) + '\n')
    with open(os.path.join(I, f'parts_{tag}.jsonl'), 'w', encoding='utf-8') as f:
        for m, c in sorted(lab.items()): f.write(json.dumps({'m': m, 'category': c, 'stability': stab.get(c, 2)}, ensure_ascii=False) + '\n')
    tr = json.load(open(os.path.join(A, f'words_{L}.json'), encoding='utf-8'))
    se = json.load(open(os.path.join(REP1, 'sign_english_words.json'), encoding='utf-8'))
    json.dump({s: {e: tr[e] for e in es} for s, es in se.items()}, open(os.path.join(I, f'words_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    cfg = {'corpus': '../../work/REP1/inputs_surviving/inscriptions.csv', 'punmax': 0.5, 'lang': tag, 'names': f'names_{tag}.jsonl', 'parts': f'parts_{tag}.jsonl',
           'number_words': NUM[L], 'drop_parts': ['tiru', 'aiyaṉ'] if L == 'tamil' else [], 'keep_noninitial': ['aiyaṉ'] if L == 'tamil' else [],
           'loan_category': 'sanskrit_loan', 'words': f'words_{tag}.json', 'weights': 'once'}
    json.dump(cfg, open(os.path.join(I, f'cfg_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    draw = {'animal', 'plant', 'body_part', 'artefact', 'landscape', 'celestial'}
    print(L, 'names kept', len(keep), 'of', len(ns), 'parts labelled', len(lab), 'loans', sum(c == 'sanskrit_loan' for c in lab.values()),
          'filled english', sum(1 for v in tr.values() if v), 'drawable share', round(sum(c in draw for c in lab.values()) / len(lab), 3),
          'types kept', collections.Counter(r.get('type') for r in keep).most_common(6))
