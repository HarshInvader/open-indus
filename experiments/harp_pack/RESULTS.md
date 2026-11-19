# HARP prediction pack (sealed 2026-11-19, before the HARP spreadsheet)

## Verdict
- **Five tests are sealed and kept**, all with planted power of at least 0.92 at the likely size (alpha 0.05/13):
  - C1: jar sign M342 rarer on pre-firing marks (power 1.00).
  - C2: opener-type signs M391/M343/M267 commoner on pre-firing marks (0.92).
  - C6: M342 on new Harappa pottery vs Harappa seals (1.00).
  - C7: docket tier x HARP lot (0.95).
  - C9: numeral value vs rim diameter (1.00).
- **Nine candidates are dropped now** and will not be run as confirmatory tests on this sheet:
  - C3 lot-split pre-firing vocabulary (0.34) and C4 sign x vessel form (0.28).
  - C5 storage jars (F3b): power 0.39. It is scored only under forward_predictions.md.
  - Bangle, implement and rod magnitude tests C10a/C10b/C11/C12, ticked-fish findspots C13 and new-bangle oval C14: all 0.00. Each class has 3 to 10 objects.
- **Fragility.** Under the pessimistic scenario (600 readable sherds, 10% pre-firing, half the tablets with a lot), only C6 (0.99) and C9 (0.82) stay powered. C1, C2 and C7 fall to 0.28-0.49. The frozen minimum n values (power.json) then make them UNTESTABLE instead of weakly tested.

## Files
- `docs/prereg/harp_pack.md`: hypotheses, column mapping, units, statistics, kill rules, Holm, power table, January procedure.
- `loader.py`: frozen tolerant loader. `test_loader.py` runs a synthetic fixture (`fixture/harp_fixture.csv`): 23 checks, all pass.
- `score.py`: frozen statistics and verdict rules. It reads `power.json` for the kept list and the minimum n.
- `power.py`, `power.log`, `power.json`: planted-power simulation (run through board/run.sh, about 23 min).

## Caveats
- Every scenario number is an assumption: share readable, pre-firing share, lot structure, rim coverage. The sheet's real shape decides eligibility; it never decides which tests are kept.
- The texts of most HARP inscribed objects are already in ICIT. Only the new links (firing stage, form, lot, rim) and sherds not in ICIT are blind; see the disclosure in the prereg.
- C9 had 1 false pass in 60 unplanted sheets at alpha 0.0038. This is within Monte Carlo error.
