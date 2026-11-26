"""Descriptive counts quoted in the open note to Yajnadevam (coordinator ruling 2026-11-26).
Replaces the one-off review-only script behind docs/outreach/yajnadevam_blog_review.md.
Not a test: no hypothesis, no p-values. Every number written to counts.json.

Run from repo root: python3 -I experiments/yj_note_counts/count.py > experiments/yj_note_counts/run.log

Definitions
- sign tokens: M77 tokens starting 'M', ICIT tokens starting 'W'; line marks '|' and breaks '#' dropped.
- extra repeated tokens in a text = n_tokens - n_distinct_signs.
- "has a repeat" = extra > 0. Shares use texts with >= 2 sign tokens.
- ICIT distinct = distinct sign sequences across the whole corpus (first occurrence kept).
- ICIT numerals: W signs whose Mahadevan equivalents (bridge_WM.json) carry a NUMERAL role
  in experiments/functional_reading/lexicon.csv; removed before counting.
- six/seven + fish: M77 distinct texts (corpus.load.dev_heldout, v2 splits), pairs inside break-free runs,
  sign sets from experiments/language/a2_predictions.json; independent recount of language A2 P1.
- site counts: ICIT rows (one row per inscribed side) and distinct objects (id before the '.').
"""
import os, json, csv, hashlib, collections as C

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(D))
P = lambda *a: os.path.join(R, *a)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

FILES = {k: P(*v) for k, v in {
    'm77': ('data', 'm77_texts.jsonl'), 'icit': ('data', 'icit_texts.jsonl'),
    'bridge': ('sources', 'shaunmortal_indus', 'data', 'bridge_WM.json'),
    'lexicon': ('experiments', 'functional_reading', 'lexicon.csv')}.items()}

m77 = [[t for t in json.loads(l)['seq'] if t.startswith('M')] for l in open(FILES['m77'])]
icit_rows = [json.loads(l) for l in open(FILES['icit'])]
icit = [[t for t in r['seq'] if t.startswith('W')] for r in icit_rows]
seen, icit_d = set(), []
for s in icit:
    if tuple(s) not in seen:
        seen.add(tuple(s)); icit_d.append(s)

num_m = {r['item'] for r in csv.DictReader(open(FILES['lexicon']))
         if r['kind'] == 'sign' and r['roles'].startswith('NUMERAL')}
bridge = json.load(open(FILES['bridge']))
num_w = {'W%03d' % int(w) for w, v in bridge.items() if any('M%d' % m in num_m for m in v['M'])}
icit_dn = [[t for t in s if t not in num_w] for s in icit_d]

extra = lambda s: len(s) - len(set(s))


def share(texts):
    T = [s for s in texts if len(s) >= 2]
    k = sum(extra(s) > 0 for s in T)
    return dict(with_repeat=k, texts=len(T), pct=round(100 * k / len(T), 1))


def len78(texts):
    T = [s for s in texts if len(s) in (7, 8)]
    return dict(texts=len(T), texts_with_repeat=sum(extra(s) > 0 for s in T),
                extra_repeated_tokens=sum(extra(s) for s in T))


sites = C.Counter(r['site'] for r in icit_rows)
objs = C.defaultdict(set)
for r in icit_rows:
    objs[r['site']].add(r['id'].split('.')[0])

out = dict(
    inputs={k: dict(path=os.path.relpath(v, R), sha256=sha(v)) for k, v in FILES.items()},
    n_numeral_W_signs=len(num_w), numeral_W_signs=sorted(num_w),
    share_texts_with_repeat={'M77': share(m77), 'ICIT raw rows': share(icit),
                             'ICIT distinct': share(icit_d),
                             'ICIT distinct, numerals removed': share(icit_dn)},
    len_7_8={'M77': len78(m77), 'ICIT raw rows': len78(icit), 'ICIT distinct': len78(icit_d)},
    sites={s: dict(rows=sites[s], objects=len(objs[s])) for s in ('Lothal', 'Dholavira', 'Bhirrana')},
)
# 6- and 7-stroke signs followed by fish (independent recount of experiments/language A2 P1,
# sign sets from a2_predictions.json; M77 distinct texts, dev + held-out, break-free runs).
import sys
sys.path.insert(0, R)
from corpus.load import dev_heldout, runs
SS = json.load(open(P('experiments', 'language', 'a2_predictions.json')))['sign_sets']
NUMS = {s: int(v) for v, ss in SS['short_numerals'].items() for s in ss}
FISH0, FISHM = set(SS['fish_plain']), set(SS['fish_family_marked'])
dev, ho = dev_heldout()
fish = {}
for split, texts in (('all', dev + ho), ('dev', dev), ('heldout', ho)):
    k, N = C.Counter(), C.Counter()
    for t in texts:
        for r in runs(t['seq']):
            for a, b in zip(r, r[1:]):
                if a in NUMS:
                    N[NUMS[a]] += 1; k[(NUMS[a], 'plain')] += b in FISH0; k[(NUMS[a], 'family')] += b in FISH0 | FISHM
    fish[split] = {f'{n}': dict(N=N[n], plain_fish=k[(n, 'plain')], fish_family=k[(n, 'family')]) for n in (6, 7)}
    fish[split]['pooled_rate_family'] = round(sum(k[(n, 'family')] for n in N) / sum(N.values()), 3)
    fish[split]['pooled_rate_plain'] = round(sum(k[(n, 'plain')] for n in N) / sum(N.values()), 3)
out['six_seven_fish'] = fish

json.dump(out, open(os.path.join(D, 'counts.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('numeral_W_signs',)}, indent=1))
