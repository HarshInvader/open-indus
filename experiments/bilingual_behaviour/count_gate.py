"""bilingual_behaviour count gate. Label-free: per-pair counts only.

Run from anywhere:  python3 -I experiments/bilingual_behaviour/count_gate.py
Rules: experiments/bilingual_behaviour/MINIMUM.txt
       (sha256 cd108774c180a643389b53fbe18cdf1cd52374ffd7068a8202d3da92107de7ed, hashed before this script).
Input : data/icit_texts.jsonl
Output: experiments/bilingual_behaviour/count_gate.json
Counts n(s) (eligible seals containing each pair sign) and N(a) (eligible seals with each pair icon)
separately. It never crosses a sign with an icon: no share, similarity, rank or p is computed.
"""
import collections
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ICIT = os.path.join(ROOT, 'data', 'icit_texts.jsonl')
MINIMUM = os.path.join(HERE, 'MINIMUM.txt')
OUT = os.path.join(HERE, 'count_gate.json')
MIN_SHA = 'cd108774c180a643389b53fbe18cdf1cd52374ffd7068a8202d3da92107de7ed'

NOT_NAMED = {'None', '-', '?', '', 'Unknown'}
MIN_N_SIGN, MIN_N_ICON = 5, 5
MIN_PAIRS, MIN_SIGN_UNITS = 3, 3
POOL = 40

ICON = {  # MINIMUM.txt: picture -> ICIT symbol code (prefix before ":")
    'unicorn': {'Bull1', 'Bult'}, 'rhino': {'Rhin'}, 'hare': {'Hare'},
    'goat': {'Goat'}, 'anthropomorph': {'Anth'},
}
PAIRS = [  # id, picture type, sign type, primary sign, icon key
    ('P1', 'A2', 'C4', 'W749', None),
    ('P2', 'B1', 'C1', None, 'unicorn'),
    ('P3', 'B5', 'A11', 'W341', 'rhino'),
    ('P4', 'B7', 'C2', 'W753', 'hare'),
    ('P5', 'B9', 'C5', 'W777', 'goat'),
    ('P6', 'B10', 'A7', None, None),
    ('P7', 'B19', 'C6', 'W777', 'anthropomorph'),
]
FAMILY = ['W777', 'W780', 'W781', 'W782']  # sensitivity only


def main():
    sha = hashlib.sha256(open(MINIMUM, 'rb').read()).hexdigest()
    assert sha == MIN_SHA, 'MINIMUM.txt changed since it was hashed'

    rows = [json.loads(l) for l in open(ICIT, encoding='utf8')]
    objs = collections.defaultdict(list)
    for r in rows:
        if r['type'].startswith('SEAL'):
            objs[r['id'].split('.')[0]].append(r)

    seals, n_conflict = [], 0
    for oid, faces in objs.items():
        codes = {f['symbol'].strip() for f in faces} - NOT_NAMED
        if len(codes) != 1:
            n_conflict += len(codes) > 1
            continue
        toks = {t for f in faces for t in (f.get('seq') or []) if isinstance(t, str) and t.startswith('W')}
        seals.append((codes.pop().split(':')[0], toks))

    n_sign = collections.Counter(t for _, toks in seals for t in toks)
    n_icon = collections.Counter(c for c, _ in seals)

    def icon_n(key):
        return sum(n_icon[c] for c in ICON[key]) if key else None

    out = {'minimum_sha256': sha, 'n_seal_objects': len(objs), 'n_eligible_seals': len(seals),
           'n_dropped_conflicting_codes': n_conflict,
           'n_signs_with_n_ge_5': sum(v >= MIN_N_SIGN for v in n_sign.values()), 'pairs': []}
    usable = []
    for pid, pic, sgn, s, key in PAIRS:
        ns = n_sign.get(s, 0) if s else None
        na = icon_n(key)
        reasons = []
        if s is None:
            reasons.append('no single W sign')
        elif ns < MIN_N_SIGN:
            reasons.append(f'n(sign)={ns} < {MIN_N_SIGN}')
        if key is None:
            reasons.append('picture is not a seal-field icon code')
        elif na < MIN_N_ICON:
            reasons.append(f'N(icon)={na} < {MIN_N_ICON}')
        ok = not reasons
        if ok:
            usable.append((pid, s))
        out['pairs'].append({'pair': pid, 'picture_type': pic, 'sign_type': sgn, 'sign': s,
                             'icon': key, 'icon_codes': sorted(ICON[key]) if key else None,
                             'n_sign_eligible_seals': ns, 'N_icon_eligible_seals': na,
                             'usable': ok, 'why_not': reasons})
    out['family_sensitivity_n'] = {w: n_sign.get(w, 0) for w in FAMILY}
    out['family_union_n'] = sum(1 for _, toks in seals if toks & set(FAMILY))
    # Descriptive, icon-free: in how many ICIT objects of each type class does each pair sign occur?
    by_class = collections.defaultdict(collections.Counter)
    seen = collections.defaultdict(set)
    for r in rows:
        oid = r['id'].split('.')[0]
        for t in r.get('seq') or []:
            if t in {'W749', 'W341', 'W753'} | set(FAMILY) and oid not in seen[t]:
                seen[t].add(oid)
                by_class[t][r['type'].split(':')[0]] += 1
    out['pair_sign_objects_by_type_class'] = {t: dict(c) for t, c in sorted(by_class.items())}
    units = sorted({s for _, s in usable})
    out['usable_pairs'] = [p for p, _ in usable]
    out['usable_sign_units'] = units
    out['pool_feasible'] = out['n_signs_with_n_ge_5'] - 1 >= POOL
    out['p_min_pool_null'] = (1 / (POOL + 1)) ** len(units) if units else None
    out['verdict'] = ('PASS' if len(usable) >= MIN_PAIRS and len(units) >= MIN_SIGN_UNITS
                      and out['pool_feasible'] else 'FAIL')
    json.dump(out, open(OUT, 'w', encoding='utf8'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
