"""Export every contest run in raj_check to one JSON for the article's interactive chart.
python3 -I stage4/export_runs.py <out.json>. Reads out/; runs whose files are missing are skipped."""
import json, os, sys, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(H, '..', 'out')
def seeds(d, L):
    try: return [json.load(open(f'{O}/{d}/{L}_real_{s}.json'))['heldout'] - json.load(open(f'{O}/{d}/{L}_null_{s}.json'))['heldout'] for s in range(10)]
    except FileNotFoundError: return None
def meta(d, L, k): return st.mean(json.load(open(f'{O}/{d}/{L}_real_{s}.json'))[k] for s in range(10))
RUNS = [  # (id, label, note, group, dir, lang file prefix, names description)
 ('tamil', 'Old Tamil', "the paper's headline list", 'paper', 'T0', 'tamil', 'Sangam names of every kind'),
 ('sanskrit', 'Vedic Sanskrit', "the paper's rival", 'paper', 'T0', 'sanskrit', 'Vedic names of every kind'),
 ('japanese', 'Japanese', 'no link to the Indus', 'other', 'T4_japanese', 'japanese', 'surnames'),
 ('sumerian', 'Sumerian', 'Mesopotamia', 'other', 'T5_sumerian', 'sumerian', 'Ur III personal names'),
 ('egyptian', 'Egyptian', 'Middle Kingdom and later', 'other', 'T5_egyptian', 'egyptian', 'personal names'),
 ('finnish', 'Finnish', 'no link to the Indus', 'other', 'T5_finnish', 'finnish', 'surnames'),
 ('tamil_ascii', 'Tamil, plain spelling', 'diacritics removed', 'tamilctl', 'T6_6a', 'tamil6a', 'Sangam names of every kind'),
 ('tamil_people', 'Tamil, people only', "the paper's list, persons only", 'tamilctl', 'T6_6b', 'tamil6b', 'Sangam personal names (532)'),
 ('tamil_fresh', 'Old Tamil, fresh list', 'same sources, new agent', 'dravidian', 'T7_tamil4b', 'tamil4b', 'Sangam and Tamil-Brahmi names, 68% people'),
 ('tamil_x2', "Paper's names, fresh pictures", 'exploratory', 'tamilctl', 'T7x_tamil4b_x2', 'tamil4b_x2', "the paper's 1,125 names with the fresh list's picture words"),
 ('tamil_x1', "Fresh names, paper's pictures", 'exploratory', 'tamilctl', 'T7x_tamil4b_x1', 'tamil4b_x1', "the fresh names with the paper's picture words"),
 ('kannada', 'Old Kannada', 'Dravidian', 'dravidian', 'T7_kannada4b', 'kannada4b', 'inscription and early literary names of every kind'),
 ('telugu', 'Old Telugu', 'reads only ~2 signs', 'dravidian', 'T7_telugu4b', 'telugu4b', 'inscription and early literary names of every kind'),
 ('malayalam', 'Old Malayalam', 'short list (510 names)', 'dravidian', 'T7_malayalam4b', 'malayalam4b', 'inscription and early literary names of every kind'),
]
T = seeds('T0', 'tamil'); out = []
for rid, label, note, group, d, L, desc in RUNS:
    x = seeds(d, L)
    if x is None: continue
    out.append({'id': rid, 'label': label, 'note': note, 'group': group, 'names_desc': desc,
                'names': json.load(open(f'{O}/{d}/{L}_real_0.json'))['names'],
                'D': round(st.mean(x), 1), 'sd': round(st.stdev(x), 1), 'above': sum(v > 0 for v in x),
                'ahead': None if rid == 'tamil' else sum(a > t for a, t in zip(x, T)),
                'opts': round(meta(d, L, 'pic_mean_opts'), 2), 'read': round(meta(d, L, 'read'), 1), 'seeds': [round(v, 1) for v in x]})
# permutation and fake-seal controls (summaries)
perm = []
for p in range(1, 51):
    x = seeds(f'T1/perm{p}', 'tamil')
    if x: perm.append(st.mean(x))
for kind, lab in (('order', 'Tamil on shuffled seals'), ('iid', 'Tamil on meaningless seals')):
    v = [st.mean(seeds(f'T2_{kind}/fake{f}', 'tamil')) for f in range(1, 21)]
    out.append({'id': f'fake_{kind}', 'label': lab, 'note': '20 fake corpora', 'group': 'control', 'names_desc': 'Sangam names of every kind', 'names': 1125,
                'D': round(st.mean(v), 1), 'sd': round(st.stdev(v), 1), 'above': None, 'ahead': None, 'opts': None, 'read': None, 'seeds': [round(a, 1) for a in v], 'seed_unit': 'corpus'})
out.insert(1, {'id': 'tamil_perm', 'label': 'Tamil, pictures on wrong signs', 'note': '50 random shuffles (median)', 'group': 'control', 'names_desc': 'Sangam names of every kind', 'names': 1125,
               'D': round(st.median(perm), 1), 'sd': round(st.stdev(perm), 1), 'above': None, 'ahead': None, 'opts': None, 'read': None, 'seeds': [round(a, 1) for a in perm], 'seed_unit': 'shuffle'})
json.dump({'tamil_D': 223.0, 'half_line': 111.5, 'runs': out}, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'rows:', ', '.join(f"{r['label']} {r['D']:+}" for r in out))
