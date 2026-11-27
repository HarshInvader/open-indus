"""Stage 6 (T10, PREREG_STAGE6.md): Brahui contest inputs, same steps as stage4/build_4b.py.
  python3 -I stage6/build_6.py parts          -> agents/parts_brahui.jsonl (labeler input)
  python3 -I stage6/build_6.py sample         -> agents/checker_sample_brahui.json (50 names + 50 words, seed '20261127-brahui')
  python3 -I stage6/build_6.py final [meaningfirst]  -> inputs/*_brahui6{,m}, cfg_brahui6{,m}.json
Main run: loans (category 'loan') dropped. 'meaningfirst': loans labelled by meaning and kept."""
import json, os, sys, random, collections
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, 'agents'); I = os.path.join(H, 'inputs')
sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving')); import nphon
REP1 = os.path.join(H, '..', 'work', 'REP1', 'inputs'); L = 'brahui'
NUM = {'1': 'asiṭ', '2': 'irāṭ', '3': 'musiṭ', '4': 'chār', '5': 'panch', '6': 'shash', '7': 'haft', '12': 'dwāzdah'}
def names():
    out, seen = [], set()
    for l in open(os.path.join(A, 'names_brahui.jsonl'), encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        if r['name'] in seen: continue
        seen.add(r['name']); out.append(r)
    return out
def glosses(r):
    g = [x.strip() for x in str(r.get('gloss', '')).split('+')]
    return [g[i] if i < len(g) and g[i] else 'name' for i in range(len(r['morphemes']))]
WF = os.path.join(A, 'words_brahui.json'); step = sys.argv[1]; ns = names()
if step == 'sample':
    rnd = random.Random('20261127-brahui'); w = json.load(open(WF, encoding='utf-8'))
    pairs = [(e, x) for e, v in w.items() for x in (v if isinstance(v, list) else [v]) if x]
    out = {'names': [{k: r[k] for k in ('name', 'type', 'morphemes', 'gloss', 'source') if k in r} for r in rnd.sample(ns, min(50, len(ns)))],
           'words': [{'english': e, 'word': x} for e, x in rnd.sample(pairs, min(50, len(pairs)))]}
    json.dump(out, open(os.path.join(A, 'checker_sample_brahui.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('sample', len(out['names']), len(out['words']))
elif step == 'parts':
    cnt = collections.Counter(); gl = {}
    for r in ns:
        for m, g in zip(r['morphemes'], glosses(r)):
            m = nphon.norm(m)
            if m: cnt[m] += 1; gl.setdefault(m, collections.Counter())[g] += 1
    with open(os.path.join(A, 'parts_brahui.jsonl'), 'w', encoding='utf-8') as f:
        for m in sorted(cnt): f.write(json.dumps({'part': m, 'gloss': gl[m].most_common(1)[0][0], 'in_names': cnt[m]}, ensure_ascii=False) + '\n')
    print('names', len(ns), 'parts', len(cnt), 'types', collections.Counter(r.get('type') for r in ns).most_common())
else:
    os.makedirs(I, exist_ok=True); stab = json.load(open(os.path.join(REP1, 'category_stability.json'))); stab.setdefault('loan', 1)
    var = sys.argv[2] if len(sys.argv) > 2 else ''
    lab = {json.loads(l)['part']: json.loads(l)['category'] for l in open(os.path.join(A, 'labels_brahui' + (f'_{var}' if var else '') + '.jsonl'), encoding='utf-8') if l.strip()}
    keep = [r for r in ns if any(lab.get(nphon.norm(m)) not in (None, 'loan') for m in r['morphemes'])][:1125]
    tag = 'brahui6' + ('m' if var else '')
    with open(os.path.join(I, f'names_{tag}.jsonl'), 'w', encoding='utf-8') as f:
        for r in keep: f.write(json.dumps({'name': r['name'], 'type': r.get('type'), 'morphemes': r['morphemes'], 'weight': 1}, ensure_ascii=False) + '\n')
    with open(os.path.join(I, f'parts_{tag}.jsonl'), 'w', encoding='utf-8') as f:
        for m, c in sorted(lab.items()): f.write(json.dumps({'m': m, 'category': c, 'stability': stab.get(c, 2)}, ensure_ascii=False) + '\n')
    tr = json.load(open(WF, encoding='utf-8')); se = json.load(open(os.path.join(REP1, 'sign_english_words.json'), encoding='utf-8'))
    json.dump({s: {e: tr.get(e, []) for e in es} for s, es in se.items()}, open(os.path.join(I, f'words_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    cfg = {'corpus': '../../work/REP1/inputs_surviving/inscriptions.csv', 'punmax': 0.5, 'lang': tag, 'names': f'names_{tag}.jsonl', 'parts': f'parts_{tag}.jsonl',
           'number_words': NUM, 'drop_parts': [], 'keep_noninitial': [], 'loan_category': 'loan', 'words': f'words_{tag}.json', 'weights': 'once'}
    json.dump(cfg, open(os.path.join(I, f'cfg_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(tag, 'names kept', len(keep), 'of', len(ns), 'parts', len(lab), 'loans', sum(c == 'loan' for c in lab.values()), 'filled english', sum(1 for v in tr.values() if v))
