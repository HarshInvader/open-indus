# Material watch

Watches open sources for the new primary material that would reopen a route closed in `docs/EXPERT_GATES.md`. Not a test; a hit is a lead to open and check against the route's gate.

- Run: `python3 -I experiments/material_watch/watch.py` (network only, about 5 minutes at one request per second). Intended cadence: weekly.
- Checks: CDLI artifacts whose transliteration contains me-luh-ha (record fields, seals, impressions); the two requested tablets P453801 and P516366, including whether CDLI now serves a photo; Zenodo records for Indus-script terms.
- Photo check validated against a known case: YBC 5447 (P306518) returns a photo, P453801 does not. It runs as a positive control on every pass.
- Baseline 2026-11-26: 184 Meluhha artifacts, 59 Zenodo records; neither requested tablet has a photo or a transliterated impression on CDLI.
- Outputs: `snapshots/<date>.json`, `reports/<date>.md`.
