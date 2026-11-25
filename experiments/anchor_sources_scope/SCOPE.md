# Anchor sources: desk scope (2026-11-25)

Research only. Nobody was contacted and nothing was committed. Downloads are in `sources/anchor_scope_dl/`, which git ignores through the `/sources/` rule (checked with `git check-ignore`). All requests used the User-Agent `open-research-site/1.0`. Sites that returned 403 or 429 were not retried by any other route.

## Verdict on the key question

**No.** No open source gives more than 15 anchor pairs, and no open source gets us there when added to what we have. The count of anchor-grade pairs in sources I actually opened is **0**. It is not 1.

- **YBC 5447 does not meet the definition as it stands.** Buchanan (AS 16, pp. 204–207, opened) assigns its impressions to his Type III, the "Tilmun group". He reconstructs the design as a bucranium, birds and two seated figures drinking through a tube. He says of Type III that "the signs of the Indus script, if present, seem no longer used as such" (p. 206 f.).
  - The sealer is not named either. Hallo (p. 202) only infers that the impressions "are likely to be those of the debtor", Hatin-Ibanum.
  - So YBC 5447 is a dated Gulf-seal impression with a probable owner. It is not an Indus-sign anchor unless new photos show signs.
- **The gap is structural, not a gap in our searching.**
  - Gulf seals that carry Indus script are Buchanan's Types I–II and Laursen's early "Gulf Type", c. 2100–2000 BC. They are known as loose seals, or as sealings with no text, such as the Umma jar sealing now in the Ashmolean.
  - The few Gulf stamps impressed on cuneiform tablets are the later Dilmun type (Type III). That type has largely dropped the script.
  - The secondary sources I opened name only two such tablets: YBC 5447 and Susa Louvre Sb 11221 (Lambert 1976, not opened).
- **The CDLI catalogue route is already exhausted.** The repo's `sealing_hunt` found no stamp notes on Gulf material in 135,198 texts. The stamp sweep (atlas 9.2) found 17 Old Assyrian stamps and one Gulf stamp, which is YBC 5447.
- **What this means for `anchor_crossread`.** Its threshold of more than 15 pairs cannot be reached from published material. The realistic ceiling is single digits even with every request granted, and it may be 0 pairs with Indus signs. The only way past it is an unpublished find: an archive of sealed tablets whose impressions have never been photographed.

## Sources

"Count" means Gulf- or Indus-style impressions on objects whose sealer is named in a legible text, and whose seal carries Indus signs. "(unverified)" marks anything I did not open.

| # | Source | What it holds | Count | Photos open? | Licence | Access | Citation / URL opened |
|---|---|---|---|---|---|---|---|
| 1 | Hallo & Buchanan 1965, AS 16: 199–209 | Edition of YBC 5447 (Gungunum 10, probably from Ur); drawings of the Gulf stamp; Buchanan's Type I–III list of Gulf seals with find-spots (Gadd 1–18, Bahrain I–VI, Failaka I–VI, Lothal) | **0** (1 Gulf impression, no Indus signs, sealer inferred) | Plate XVI is in the free PDF | ISAC free PDF; terms not checked | Open download | https://isac.uchicago.edu/publications/studies-honor-benno-landsberger-his-birthday ; PDF in `sources/anchor_scope_dl/as16/` |
| 2 | Yale YPM / YBC 5447 (P306518) | Six-side photos plus a detail of the stamped edge | 0 (same object) | Yes | CC0-1.0, stated on the CDLI page | Open | https://cdli.earth/artifacts/306518 ; https://collections.peabody.yale.edu/search/Record/YPM-BC-019511 |
| 3 | CDLI P516366, P453801 | Ur III tablets; seal recorded as "illegible"; no photo | unknown (0 to 1 each) | No | – | Request (sent to SBAH 2026-11-24; Messina pending) | https://cdli.earth/artifacts/516366 ; https://cdli.earth/artifacts/453801 |
| 4 | CDLI P415075 (UET 5 184) | Old Babylonian tablet from Ur; seal recorded as "no legend"; witnesses, no single sealer | 0 by definition | Line drawing only | – | Request | https://cdli.earth/artifacts/415075 |
| 5 | CDLI catalogue, seal entities | Seal and stamp notes across the whole dump | 1 Gulf stamp (YBC 5447), 0 anchors | Per object | Per photo | Open | repo: `sealing_hunt`, atlas 9.2 |
| 6 | Buchanan 1981, *Early Near Eastern Seals in the Yale Babylonian Collection* (CBCY 4) | Yale seals and impressions; cited on CDLI for the YBC 5447 seal | unknown (unverified) | No | © Yale | Purchase or library. An archive.org copy exists, but it is a private upload with no rights statement, so I did not use it. | CDLI citation on P306518 |
| 7 | Laursen 2010, AAE 21: 96–134 | Main corpus of Gulf Type seals with Indus inscriptions (about 121 seals per a secondary source; unverified) | unknown; seals, not impressions on texts (unverified) | No | © Wiley, closed per OpenAlex | Purchase. The harappa.com copy returned 403. | https://doi.org/10.1111/j.1600-0471.2010.00329.x (OpenAlex record opened) |
| 8 | Laursen 2018, CUP chapter, pp. 204–226 | Dilmun sealing technology; the abstract says it covers "impression on sealings and cuneiform tablets" | not stated in the abstract | No | © CUP | Purchase | https://doi.org/10.1017/9781108160186.015 (abstract opened) |
| 9 | Laursen 2023 (2022 online), AAE | Gulf and Dilmun seals from Ur, Girsu, Susa, Tepe Yahya and Makkan | unknown | – | CC BY-NC-ND, per OpenAlex | Open access, but the Wiley PDF returned 403 to scripts | https://doi.org/10.1111/aae.12221 |
| 10 | Laursen et al. 2026, JNES 85/1 | Stamped tokens from Bahrain: two Dilmun stamps with cuneiform legends naming Yagli-El | 0. The owner is named on the seal itself; whether it has Indus signs is unstated | No | © UChicago | Purchase | https://doi.org/10.1086/739820 (via https://en.wikipedia.org/wiki/Yagli-El) |
| 11 | Lambert 1976, RA 70: 71–72 (Louvre Sb 11221) | Old Elamite Susa contract (loan to Ekiba) sealed with a Gulf stamp | 0 to 1 (unverified); seal type and signs unknown | No; the Louvre returned 429 | © Louvre. Record it only; do not publish its images. | Request | Citation confirmed by search only (unverified) |
| 12 | Amiet 1972, MDAI 43; Amiet 1986 | Susa glyptic, including Gulf seals and the Sb 11221 impression | unknown (unverified) | No | © | Library | https://catalog.hathitrust.org/Record/001662353 (search-only rights) |
| 13 | Gadd 1932, "Seals of ancient Indian style found at Ur" | 18 seals; BM 120573 has a cuneiform legend | 0. These are seals with no text naming a sealer | A Digital Library of India scan exists | Unclear | archive.org `in.gov.ignca.33779` | Item metadata opened |
| 14 | Legrain 1951, UE X; Ur Online | Ur seals; the Gadd seals are UE X 624–632 | 0 anchors known; seals, not impressions on texts (unverified) | Ur Online did not resolve or timed out | © BM/Penn | Retry later | – |
| 15 | Kjærum 1983, Failaka/Dilmun seals; David-Cuny & Neyme 2016, Failaka vol. 2; Abu-Laban 2016 | Hundreds of Dilmun stamps; sealings from Tell F6 | 0. Sealings and bullae carry no named sealer (unverified) | No | © JASP/NCCAL | Purchase | Search results only |
| 16 | Kjærum 1994 (Qal'at al-Bahrain vol. 1); Crawford, Saar | Stamp seals, impressions and blanks; stamped tokens and discs | 0 (unverified) | No | © | Purchase | Search results only |
| 17 | Mitchell & Searight 2008, BM Stamp Seals III | Stamp impressions on tablets, 9th–2nd c. BC | 0. Out of the Bronze Age range | No | © BM/Brill | – | https://cdli.earth/publications/1787443 |
| 18 | Umma jar sealing (Ashmolean) | Indus bull-and-manger motif, 6 signs, cloth back | 0. Indus script, but no text | harappa.com | – | – | https://www.harappa.com/blog/indus-seal-impression-umma-mesopotamia (search result only) |
| 19 | British Museum, Penn Museum, Louvre online search | – | not checked | – | – | Each returned 403 or 429 to scripts | – |
| 20 | Iraq Museum | No online catalogue found | unknown | – | – | Request only | – |
| 21 | Tell Abraq | No texts known | 0 (unverified) | – | – | – | per `stamp_detector_priorart.md` |

## Owner ask list (ranked by expected new pairs per ask)

People already contacted are marked. No new outreach was made here.

1. **Steffen Terp Laursen (Moesgaard)**, already contacted 2026-11-18 via the Moesgaard info address. Ask: from his Gulf and Dilmun corpus, every impression of a Gulf or Dilmun stamp on a cuneiform tablet. For each, whether the seal carries Indus signs and whether the text names the sealer. He is the one person who could confirm "single digits, about 0 with signs" or overturn it.
2. **Yale Babylonian Collection**, associate curator already emailed. Ask:
   - raking-light images of the YBC 5447 stamped edge and end, to look for script;
   - whether CBCY 4 (Buchanan 1981) or Yale records list any other Gulf stamp impressions on Yale's Ur and Larsa tablets.
3. **Asko Parpola**, already contacted. Ask: the CISI 3.1 West Asia entries that are impressions on cuneiform objects.
4. **SBAH / Iraq Museum (P516366, already sent) and the Messina Nisaba editors (P453801)**. Ask: photos of all faces and edges, to settle the 0-to-2 pair ceiling.
5. **Louvre DAO**. Ask: the Sb 11221 record and photos for study only, not for publication. Also ask whether any other Susa tablets carry Gulf stamps (Amiet MDAI 43).
6. **Library or purchase, no contact needed**: Laursen 2010, Laursen 2018, Laursen et al. 2026 (JNES), Lambert 1976. These would confirm the count in rows 7–11.
7. **Low value**: NCCAL Kuwait (Failaka) and the Bahrain authorities. Their sealings have no texts, so they hold no anchors.
