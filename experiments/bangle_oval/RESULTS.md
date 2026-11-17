# Bangle oval: a clean confirmatory test is not possible yet

Pre-registration: `docs/prereg/bangle_oval.md`, hashed (tag `bangle_oval`) with `b0_baselines.py`, `baselines.json`, `b1_power.py` and `power.json` before any candidate bangle's signs were seen. Code: `b0_baselines.py` (discovery-data baselines), `b1_power.py` (power), `b2_workshop.py` (workshop descriptives, discovery data only). Numbers: `results.json`, `power.json`, `workshop.json`, `baselines.json`. Ledger: `bo_h1`, `bo_pow`, `bo_h4a`, `bo_h4b`.

## Findings first

1. **No independent sample exists in what we can reach.**
   - Every published inscribed bangle we could trace is already one of the 50 ICIT `BNGL` rows (41 distinct texts) the lead was found on. That covers the Mohenjo-daro 1983-85 surface finds (Halim & Vidale; CISI M-1628 to M-1647), the Marshall/Mackay DK, HR and SD bangles, and the HARP Harappa finds. Secondary counts give about 22-23 inscribed stoneware bangles in all (Mohenjo-daro 18, Harappa 4, Balakot 1), and ICIT holds more than that.
   - No ICIT row of another type is a bangle. We checked the type, material, shape, cross-section, excavation-number and notes fields for bangle, bracelet, ring, stoneware, shell and annular. The only stoneware or shell row outside `BNGL` is L-111, a shell seal.
   - CISI vol. 1 has no bangle section.
   - CISI vol. 2 objects missing from ICIT:
     - H-1008 is captioned "t.c. BANGLE(?)". It is a pierced terracotta arc with crosshatching and a few short strokes. That may be decoration rather than text, and it has no oval.
     - M-1648 is a small shell ring or bead.
     - M-1655 to M-1657 are ornaments, not bangles.
   - Eligible new bangle texts: **n = 0** confirmed, at most 1 doubtful. The minimum for the frozen test is 10, so H1 is **UNTESTABLE**. The test stays frozen for the next sample. Likely sources are the Fuls 2023 catalogue, CISI 3.x, the HARP bangle records, and the harappa.com papers, which return 403 to our fetcher.
2. **Power statement.** The null rate is p0 = 0.0106, the share of distinct non-bangle ICIT texts at the same sites that carry W790.
   - If the true rate on bangles is 15%, about the discovery rate of 6/41, then **19 new bangle texts** give 80% power under the pre-registered rule (binomial p < 0.05 and share ≥ 0.08). If the true rate is 8%, it takes 53.
   - The literal rule "observed share ≥ 15%" passes only about 50% of the time at any n when the truth is 15%. That is why the prereg makes 15% the point prediction ("strong pass") and keeps the frozen L2 bar of 0.08 for the pass itself.
   - With 10 new texts, a real 15% effect still shows zero ovals 20% of the time.
3. **The workshop-mark reading is not excluded, and is if anything favoured. This is descriptive only, on the discovery data.**
   - At Mohenjo-daro, all **5 oval objects come from one collection**, the 1983-85 surface finds: 5 of 27 objects, against 0 of 13 Marshall/Mackay excavated bangles (Fisher p = 0.15; distinct texts 4/24 vs 0/9, p = 0.55).
   - Against that, the oval is also at Harappa (2 of 7 objects, vs Mohenjo-daro 5/40, p = 0.28). One of the Harappa ovals, H-2578 (Period 3B/C), is on a **clay** bangle rather than stoneware. So it is not only a mark of the stoneware kilns.
   - The site test has 4-14% power at realistic sizes, so a null there says nothing about workshops.
4. **Slot (H2), descriptive only.** The oval stands alone on 4 of 7 oval objects (2 of 5 distinct texts). In longer texts it is first, middle and last once each, so it has no fixed slot. A sign that usually stands alone fits a maker's or owner's mark as well as a word.

**Plain reading:** the bangle-oval lead cannot be confirmed or refuted with data in hand, because every known inscribed bangle was used to find it. Mohenjo-daro's ovals all come from one surface collection, which keeps "workshop or batch mark" fully alive. The Harappa clay-bangle oval is the only hint against a single stoneware workshop.

## Hypotheses

| id | hypothesis | result | verdict |
|---|---|---|---|
| H1 | oval M373/M374 on ≥15% of new bangle texts vs <1% elsewhere | n = 0 eligible | untestable (frozen; 80% power needs n ≈ 19) |
| H2 | oval stands alone or in a fixed slot | discovery: alone 4/7 objects; no fixed slot | descriptive only |
| H3 | M403 on new bangles (exploratory) | n = 0 | untestable |
| H4a | oval concentrated at one site (MD vs Harappa) | 5/40 vs 2/7 objects, p = 0.28 | inconclusive (power ≤14%) |
| H4b | oval confined to one MD collection | surface 1983-85 5/27 vs old excavations 0/13, p = 0.15 | leans workshop/batch, n.s. |

## Caveats
- The distinct-text dedup here, by W-signs and site, merges H-2578 and H-1010, which both read W790. So Harappa is 1/5 texts here against self_label's 2/6, which kept the break mark. Object counts are given alongside.
- The H-1010 photograph (CISI vol. 2 p. 349) shows the oval beside a branched sign. ICIT records only W790 plus a break.
- The literature search was web-only. Halim & Vidale 1984, Blackman & Vidale 1992 and Kenoyer's stoneware-bangle papers were not read in full, so an unpublished or untranscribed batch, such as HARP bangle fragments, may exist.

## Next
1. Human access: the HARP inscribed-bangle list (Kenoyer/Meadow) and the Fuls 2023 catalogue. Either one could supply ≥ 19 new texts.
2. When a sample arrives, transcribe it blind to these predictions where possible, then run the prereg rules H1-H4. Test H4 against Harappa versus Mohenjo-daro stoneware chemistry groups (Blackman & Vidale 1992) if the provenance of individual bangles is published.
