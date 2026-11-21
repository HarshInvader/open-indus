# Stamp-impression detector (Yale CC0 photos)

Result 2026-11-21: **gate failed, no sweep.** Recall 0.44 on 73 held-out stamped tablets and controls (bar 0.80); 0/5 controls, YBC 5447 missed; false flags 1/300. Recall came only from Achaemenid and Hellenistic objects, so the detector learned late sealing types. Details: `out/gate.json`, `out/gate_review.json`, `docs/prereg/stamp_detector.md`, atlas 9.2.

Images and catalogue records stay in `raw/` (gitignored). Files: `harvest.py` (Peabody API, 1 req/s), `sheets.py`, `embed.py`, `gate.py`, `labels_pos.csv`.
