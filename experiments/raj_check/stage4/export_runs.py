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
 ('tamil_fresh', 'Old Tamil, second list', 'same sources, new agent', 'dravidian', 'T7_tamil4b', 'tamil4b', 'Sangam and Tamil-Brahmi names, 68% people'),
 ('tamil_faithful', 'Old Tamil, third list', "the paper's prompt, nothing added", 'dravidian', 'T7_tamilf4b', 'tamilf4b', 'Sangam and Tamil-Brahmi names, 70% people'),
 ('tamil_faithful_p', "Third list, paper's pictures", 'preregistered check', 'tamilctl', 'T7_tamilf4bp', 'tamilf4bp', "the third list's names with the paper's picture words"),
 ('tamil_x2', "Paper's names, second list's pictures", 'exploratory', 'tamilctl', 'T7x_tamil4b_x2', 'tamil4b_x2', "the paper's 1,125 names with the second list's picture words"),
 ('tamil_x1', "Second list's names, paper's pictures", 'exploratory', 'tamilctl', 'T7x_tamil4b_x1', 'tamil4b_x1', "the second list's names with the paper's picture words"),
 ('tamil_c6', "Paper's names not in the second list", 'preregistered check', 'tamilctl', 'T8_c6', 'tamil4c_c6', "the paper's names that the second list lacks"),
 ('tamil_c7', "Second list's names not in the paper's", 'preregistered check', 'tamilctl', 'T8_c7', 'tamil4c_c7', "the second list's names that the paper's lacks"),
 ('tamil_c4', 'Second list, endings removed', 'preregistered check', 'tamilctl', 'T8_c4', 'tamil4c_c4', 'honorific and gender endings dropped'),
 ('japanese_sym', 'Japanese, built from the sign pictures', 'deliberately built (stage 5b)', 'other', 'T9b/jsym2_full', 'jsym2_full', 'family, place, mountain and shrine names containing picture words'),
 ('japanese_v2', 'Japanese, sign-picture names in the paper\'s mix', 'deliberately built (stage 5c V2)', 'other', 'T9b/jsym_v2_full', 'jsym_v2_full', 'picture-word names matched to the paper\'s mix of name kinds'),
 ('japanese_v1', 'Japanese, paper\'s mix, first try', 'deliberately built (stage 5c V1)', 'other', 'T9b/jsym_v1_full', 'jsym_v1_full', 'picture-word names matched to the paper\'s mix, without the extra names'),
 ('japanese_sym1', 'Japanese surnames with picture words', 'deliberately picked (stage 5b)', 'other', 'T9b/jsym1_full', 'jsym1_full', 'the T4 surnames that contain a picture word'),
 ('kannada', 'Old Kannada', 'void: reads under 3 signs', 'dravidian', 'T7_kannada4b', 'kannada4b', 'inscription and early literary names of every kind'),
 ('telugu', 'Old Telugu', 'void: reads under 2 signs', 'dravidian', 'T7_telugu4b', 'telugu4b', 'inscription and early literary names of every kind'),
 ('brahui', 'Brahui', 'void: reads no signs', 'dravidian', 'T10_brahui6', 'brahui6', 'colonial-era Brahui names of every kind, loans dropped'),
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
