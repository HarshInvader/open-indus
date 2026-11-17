# Amendment 1 to crib_attack_v2_planted (task #26, H10), 2026-11-17

Reason: compute budget only. Under background priority the first 72 searches (elamite30, n = 9, a = 0; only `secs` was inspected, no E values) ran at 1.37 s each, so the registered grid would take about 5.5 CPU-hours, over the laptop limit of a few CPU-hours.

Cuts (no outcome seen):
- list `sumerian` dropped (same size class, ~200 spellings, as `akkadian`);
- n = 11 dropped (differs from n = 9 by 2 texts; n = 9 stays as the small-n point);
- a = 6 run only at n = 49 (the most favourable n); a = 0 and a = 3 run at every n.

Everything else (method, reps 20/10/40, gate, go rule, adequacy check) unchanged. The go rule now reads: at least one passing cell with n in {20, 41, 49} and a <= 3. Estimated cost about 3.2 CPU-hours.
