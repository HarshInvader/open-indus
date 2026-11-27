"""Stage 4a inputs: Raj's headline Tamil, mechanically converted to ASCII and/or restricted to people. python3 -I stage4/build_4a.py"""
import json, os, unicodedata
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); I = os.path.join(H, 'inputs'); os.makedirs(I, exist_ok=True)
def asc(s): return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))
def conv(x, f):
    if isinstance(x, str): return f(x)
    if isinstance(x, list): return [conv(v, f) for v in x]
    if isinstance(x, dict): return {k: conv(v, f) for k, v in x.items()}
    return x
cfg0 = json.load(open(os.path.join(W, 'inputs', 'cfg_headline_tamil.json'), encoding='utf-8'))
names = [json.loads(l) for l in open(os.path.join(W, 'inputs_surviving', 'names_model_clean.jsonl'), encoding='utf-8')]
parts = [json.loads(l) for l in open(os.path.join(W, 'inputs_surviving', 'morphemes.jsonl'), encoding='utf-8')]
words = json.load(open(os.path.join(W, 'inputs', 'words_tamil_new.json'), encoding='utf-8'))
for tag, ascii_, people in [('6a', True, False), ('6b', False, True), ('6c', True, True)]:
    f = asc if ascii_ else (lambda s: s)
    nm = [dict(n, name=f(n['name']), morphemes=[f(m) for m in n['morphemes']]) for n in names if (not people or n.get('type') == 'person')]
    seen, pt, merged = set(), [], 0
    for p in parts:
        m = f(p['m'])
        if m in seen: merged += 1; continue
        seen.add(m); pt.append(dict(p, m=m))
    w = {s: {e: [f(x) for x in v] for e, v in d.items()} for s, d in words.items()}
    cfg = dict(cfg0, lang=f'tamil{tag}', names=f'names_{tag}.jsonl', parts=f'parts_{tag}.jsonl', words=f'words_{tag}.json',
               corpus='../../work/REP1/inputs_surviving/inscriptions.csv',
               number_words={k: f(v) for k, v in cfg0['number_words'].items()},
               drop_parts=[f(x) for x in cfg0['drop_parts']], keep_noninitial=[f(x) for x in cfg0['keep_noninitial']])
    with open(os.path.join(I, f'names_{tag}.jsonl'), 'w', encoding='utf-8') as o:
        for n in nm: o.write(json.dumps(n, ensure_ascii=False) + '\n')
    with open(os.path.join(I, f'parts_{tag}.jsonl'), 'w', encoding='utf-8') as o:
        for p in pt: o.write(json.dumps(p, ensure_ascii=False) + '\n')
    json.dump(w, open(os.path.join(I, f'words_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(cfg, open(os.path.join(I, f'cfg_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(tag, 'names', len(nm), 'parts', len(pt), 'merged parts', merged, 'number words', cfg['number_words'])
