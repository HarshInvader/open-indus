"""Descriptive token/text counts used for the power column of CATALOGUE.csv.
No hypothesis test is run here. Run: .venv/bin/python -I experiments/meaning_claims/counts.py
(-I needs the repo on sys.path, added below.)"""
import json, sys, csv, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout

bridge = json.load(open(ROOT/'sources/shaunmortal_indus/data/bridge_WM.json'))
M2W = collections.defaultdict(set)
for w, v in bridge.items():
    for m in v['M']: M2W[f'M{m}'].add(f'W{int(w):03d}')
def W(ms): return set().union(*[M2W.get(m, set()) for m in ms])

GROUPS = {
 'fish_family': ['M59','M60','M65','M66','M67','M68','M69','M70','M71','M72','M73','M74','M75'],
 'crop_M161_162_169': ['M161','M162','M169'],
 'M403_circles': ['M403'], 'M87_two_tall': ['M87'], 'M59_plain_fish': ['M59'],
 'M342_jar': ['M342'], 'M211_arrow': ['M211'], 'M1_man': ['M1'], 'M328_cup': ['M328'],
 'M326_leaf': ['M326'], 'M93_chanhu_end': ['M93'],
}
out = {}
m77 = distinct(m77_texts()); dev, ho = dev_heldout()
icit = icit_texts(); icit_d = distinct(icit)
def has(seq, sset): return any(s in sset for s in seq)
for g, ms in GROUPS.items():
    ws = W(ms)
    r = {'M_signs': ms, 'W_signs': sorted(ws),
         'm77_distinct_texts_with': sum(has(t['seq'], set(ms)) for t in m77),
         'm77_tokens': sum(sum(s in ms for s in t['seq']) for t in m77),
         'dev_texts': sum(has(t['seq'], set(ms)) for t in dev),
         'heldout_texts': sum(has(t['seq'], set(ms)) for t in ho),
         'icit_distinct_texts_with': sum(has(t['seq'], ws) for t in icit_d)}
    bytype = collections.Counter(t['type'].split(':')[0] for t in icit_d if has(t['seq'], ws))
    r['icit_by_type'] = dict(bytype)
    bysite = collections.Counter(t['site'] for t in icit_d if has(t['seq'], ws))
    r['icit_by_site_top'] = dict(bysite.most_common(8))
    out[g] = r
# denominators
out['_denominators'] = {
  'm77_distinct': len(m77), 'dev': len(dev), 'heldout': len(ho), 'icit_distinct': len(icit_d),
  'icit_distinct_by_type': dict(collections.Counter(t['type'].split(':')[0] for t in icit_d)),
  'icit_distinct_by_site_top': dict(collections.Counter(t['site'] for t in icit_d).most_common(10))}
# assemblage craft units: objects and fish-bearing objects per craft (Wells codes)
fishW = {w.lstrip('W').lstrip('0') for w in W(GROUPS['fish_family'])}
cropW = {w.lstrip('W').lstrip('0') for w in W(GROUPS['crop_M161_162_169'])}
rows = list(csv.DictReader(open(ROOT/'experiments/assemblage/linked_objects.csv')))
cr = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    seq = set(r['seq_wells'].split())
    crafts = [c for c in r['crafts'].split(';') if c] or ['NONE']
    for c in crafts:
        k = (r['site'], c)
        cr[k]['objects'] += 1
        cr[k]['fish'] += bool(seq & fishW)
        cr[k]['crop'] += bool(seq & cropW)
        cr[k]['nonseal'] += not r['type'].startswith('SEAL')
out['_assemblage_by_site_craft'] = {f'{s}|{c}': dict(v) for (s, c), v in sorted(cr.items())}
# Gulf / foreign texts
fp = ROOT/'datasets/open/foreign_seal_texts.csv'
if fp.exists():
    fr = list(csv.DictReader(open(fp))); out['_foreign_rows'] = len(fr); out['_foreign_cols'] = list(fr[0].keys())
json.dump(out, open(Path(__file__).with_name('counts.json'), 'w'), indent=1)
for k, v in out.items(): print(k, json.dumps(v)[:600])
