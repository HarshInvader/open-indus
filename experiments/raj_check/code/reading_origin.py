"""Descriptive: in Raj's own headline runs (T0), how many chosen readings are the sign's literal picture word vs a sound-alike name part."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving'))
import nphon
W = os.path.join(H, '..', 'work', 'REP1', 'inputs')
for lang in ('tamil', 'sanskrit'):
    words = json.load(open(f'{W}/words_{lang}_new.json', encoding='utf-8'))
    pw = {s: {nphon.norm(w) for ws in d.values() for w in ws} for s, d in words.items()}
    lit = alike = 0
    for s in range(10):
        r = json.load(open(os.path.join(H, '..', 'out', 'T0', f'{lang}_real_{s}.json')))['readings']
        for sg, v in r.items():
            if nphon.norm(v) in pw.get(sg, set()): lit += 1
            else: alike += 1
    print(lang, 'literal picture word', lit, 'sound-alike', alike, 'share literal %.2f' % (lit / (lit + alike)))
