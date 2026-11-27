"""Summarise stage 4b runs: python3 -I stage4/summ_4b.py tag [tag ...]"""
import json, sys, statistics as st
T = json.load(open('out/T6_summary.json'))['tamil']['seeds']
for tag in sys.argv[1:]:
    d, o, r = [], [], []
    for s in range(10):
        R = json.load(open(f'out/T7_{tag}/{tag}_real_{s}.json')); N = json.load(open(f'out/T7_{tag}/{tag}_null_{s}.json'))
        d.append(R['heldout'] - N['heldout']); o.append(R['pic_mean_opts']); r.append(R['read'] if isinstance(R['read'], (int, float)) else len(R['read']))
    print(tag, 'D=%.1f sd=%.1f above=%d ahead=%d opts=%.2f read=%.1f' % (st.mean(d), st.stdev(d), sum(x > 0 for x in d), sum(a > b for a, b in zip(d, T)), st.mean(o), st.mean(r)), [round(x) for x in d])
