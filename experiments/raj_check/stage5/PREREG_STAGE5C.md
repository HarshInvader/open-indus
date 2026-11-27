# raj_check stage 5c: how high can a picture-word Japanese list go? (prereg T9c)

2026-11-27. Written and hashed before any 5c run or agent. Known: T0–T9b, in particular J_sym2 (Japanese names containing picture words, 59% family names) +185.6 full corpus, +105.1 on seal half B, against the paper's Tamil +223.0 / +103.8.

Deliberate list-building, openly labelled, as before. Several variants are tried; **all are reported**, and the best one is an upper bound on what list-building of this kind achieves, not a typical value.

## Type mix
The paper's Tamil list: person 47.3%, place 21.3%, deity 8.7%, group 7.7%, lineage 3.3%, hill 2.9%, celestial 2.6%, other 2.6%, title 1.8%, river 1.2%, festival 0.4%. Japanese equivalents: person → family; place → place, island, cape, lake; deity → deity, shrine; group and lineage → clan; hill → mountain; river → river; celestial, other, title, festival → other.
Target counts in 1,125: family 532, place 240, deity/shrine 98, clan 124, mountain 33, river 14, other 84. A shortfall in any class is filled from place.

## Variants (Raj's `contest.py` unchanged; T4 Japanese picture words; labels as T9b, new parts labelled with the T4 labeler prompt)
- **V1.** The J_sym pool (1,347 names), sampled to the target counts (seed 20261127).
- **V2.** A fresh agent adds real Japanese names containing picture words in the classes the pool lacks (clans and be groups, gods and shrines, celestial and mythological names, titles and festivals, mountains, rivers). The enlarged pool is sampled to the target counts (same seed).
- **V3.** From the V2 pool, a local search chooses 1,125 names to maximise mean D on seal half A (seeds 0–4), starting from V2, 1,500 single-swap proposals (seed 3). Tested on seal half B.

## Reported
For each variant: D on the full corpus (seeds 0–9; for V3 not held out) and on half B (seeds 0–9), with sd, median and seeds above control. Readings, on half B against the paper's Tamil list (+103.8): "above Tamil" if D ≥ 103.8 with at least 8 of 10 seeds above control; "level" if within 20; otherwise "below". On the full corpus, V1 and V2 against +223.0 the same way.
