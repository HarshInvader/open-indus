# Stamp-impression detector: prior art, licences, controls

Research note, 2026-11-19. No bulk download, no compute, nobody contacted. Fetches used the User-Agent `open-research-site/1.0`. Every URL below was opened unless marked "(unverified)".

## Verdict first

**Feasible as a pilot, blocked as a full CDLI/BDTNS sweep.**

- Nobody has done this search. The novelty holds.
- The block is licensing and rate, not method. CDLI photos are not openly licensed as a whole, and CDLI asks for one request per 60 seconds.
- Five visible stamp impressions exist online, but only one is a Gulf seal. The kill test can measure "stamp vs cylinder" recovery. It cannot measure Gulf-seal recovery (n = 1).

## 1. Prior art

- **Seal presence on 3D scans.** Hagelskjær classifies whole tablets as sealed or unsealed from point clouds: 136 sealed and 223 unsealed HeiCuBeDa tablets, labels taken from the `@seal` tag. Tablet-level only, no localisation, no stamp/cylinder split. https://arxiv.org/abs/2202.10851 ; follow-up https://arxiv.org/abs/2603.03892
  - The `@seal` label is the same field that hides YBC 5447, so this training signal is blind to our target.
- **Motifs inside cylinder-seal images.** Bampfield, Dahl, Dutta, Zisserman (CDLB 2026:2) fine-tune EfficientDet on 2,491 annotations to find "person" motifs in cylinder impressions and unwrappings. It does not locate impressions on tablets and has no stamp class. https://ora.ox.ac.uk/objects/uuid:4ea75656-62fc-49a4-8404-c27c83cc8f07/files/s2n49t415r
- **CuneiML.** 38,947 CDLI photos cut into faces, for period, genre and provenience tasks. No seal task. DOI 10.5334/johd.151, PDF https://openhumanitiesdata.metajnl.com/articles/151/files/65703d56cc273.pdf
- **Sign detection (no seal component).**
  - Dencker et al. 2020: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243039
  - DeepScribe: https://arxiv.org/abs/2306.01268
  - eBL, 87,668 fragments: https://arxiv.org/abs/2606.22608
  - Stötzner, Homburg, Mara: https://arxiv.org/abs/2308.11277
- **Tablet silhouettes for dating**, 94,000 CDLI images: https://arxiv.org/abs/2406.04039
- **HeiCuBeDa**, 1,977 3D scans, CC BY-SA 4.0: https://doi.org/10.11588/data/IE8CCN
- **Aegean stamp sealings in 3D** (Bogacz, Finlayson, Panagiotopoulos, Mara) compare known impressions; they do not search an archive. https://link.springer.com/chapter/10.1007/978-3-030-41590-7_25
- **Glyptic projects.** ACAWAI-CS lists machine learning only as a future aim. https://www.geschkult.fu-berlin.de/en/e/vaa/forschung/projekte_abgeschlossen/acawai-cs/index.html
- Not opened: ACM survey "Digital Assyriology" (403) (unverified); SIANE device poster, DOI 10.5281/zenodo.14313640 (unverified).

**Novelty.** No published work searches a cuneiform photo archive for seal impressions by location, and none separates stamp from cylinder impressions.

## 2. Licences and terms

### CDLI
- **Licence.** Images are "for the non-commercial use of students, scholars, and the public"; photos are "the property of the institutions that own the artifacts"; publication needs written permission. https://cdli.earth/terms-of-use
- **Per-photo licences exist.** The page for P306518 reads "Photo © Yale Babylonian Collection at the Yale Peabody Museum (CC0-1.0)". The `/artifact-assets` export should give the licence per image (endpoint listed, not tested). https://cdli.earth/docs/api
- **robots.txt.** `User-agent: *` has `Crawl-delay: 60` and no Disallow. https://cdli.earth/robots.txt
- **Rate limits.** None stated beyond the crawl delay. Photos resolve at `/dl/photo/P######.jpg`.
- **Bulk route.** None for images. The GitHub dump is text and catalogue only. https://github.com/cdli-gh/data
- **CuneiML bundle** is CC BY-NC 4.0, but its Zenodo record returned a login wall (403). Availability unverified.

### BDTNS
- 105,666 texts; 55,571 have a photograph, 52.2% of those via CDLI. That leaves about 26,600 photos BDTNS holds itself. https://bdtns.cesga.es/index.php?p=about
- No licence statement found. No robots.txt (404). Treat as all rights reserved.

### Yale Peabody (not in the brief, but the cleanest source)
- IIIF manifests state CC0. The YBC 5447 manifest: https://manifests.collections.yale.edu/ypm/nat/1836075
- robots.txt disallows only `/view/results/`. Terms say to check rights per record. https://peabody.yale.edu/about/terms-of-use

### What this allows
- **Download:** single images for private research at 1 request per 60 s (CDLI). For BDTNS, the same pace by courtesy.
- **Republish:** derived counts, P-numbers, scores and links. Image crops only where the record says CC0 or CC BY.
- **Ask first:** a full sweep. It is not a default right under these terms.

### Counts (local CDLI catalogue dump, 353,283 rows)
- ED I to Old Babylonian, Ebla and Old Assyrian included: 223,578 records, **56,598 with a photo**. The photo flags carry 2016 dates, so this is a lower bound.
  - Ur III 28,408; Old Babylonian 18,203; Old Akkadian 2,860; Early Old Babylonian 2,020; ED IIIb 1,823; Old Assyrian 1,514.
- 11,332 of those photos have a seal field filled.
- **Edges.** 13 of 17 photos I inspected show all four edges (76%). The sample is small and not random. CuneiML says "most" CDLI photos show six faces. Estimate: about 43,000 early photos with edges, range 35,000 to 50,000.
- **Time.** 56,598 photos at one per minute is about 39 days.

## 3. Positive controls

Twelve candidates inspected by eye. Five show a stamp impression.

| Object | Period | Visible? | Source |
|---|---|---|---|
| YBC 5447 (P306518), Gulf stamp | Gungunum 10 | **Yes**, on Yale's 2021 six-side photo, which adds an enlarged detail of the stamped edge. **No** on the CDLI file, which shows obverse, reverse and one edge. | https://collections.peabody.yale.edu/search/Record/YPM-BC-019511 |
| CBS 391 (P257839) | Old Babylonian | Yes, two ovals on the lower reverse | https://cdli.earth/dl/photo/P257839.jpg |
| Walters 48.1464 (P272900) | Old Assyrian | Yes, four round stamps plus cylinder rollings | https://cdli.earth/dl/photo/P272900.jpg |
| UM 29-16-639 (P257073) | uncertain | Yes, a row of ovals under the text | https://cdli.earth/dl/photo/P257073.jpg |
| CBS 14276 (P269244), bulla | undated | Yes, ovals with an animal | https://cdli.earth/dl/photo/P269244.jpg |

- **Not visible:** P280724, P280655, P269246, P263310 (catalogue says stamp; photo shows nothing legible). P357780, P359942, P359956 (Old Assyrian; the photo shows the inner tablet, the stamped envelope is absent).
- **Gulf and Dilmun impressions elsewhere:**
  - Susa tablet Louvre Sb 11221 (Lambert, RA 70, 1976): the Louvre site returned 429. Not on CDLI. (unverified)
  - Failaka, Qala'at al-Bahrain, Saar: CDLI has no sealed tablet or bulla from these sites, only vessels and two later Failaka seals without photos. Published impressions are in print (Kjærum; Crawford) (unverified). Tell Abraq: nothing found.
  - Laursen 2010 (harappa.com) and Encyclopaedia Iranica returned 403.
- **Later-period pool.** About 100 CDLI photo records carry a stamp-seal note (Neo-Assyrian, Achaemenid, Neo-Babylonian). Not inspected.

**Does n ≥ 5 exist?** Yes for stamp impressions in general: five, of which two are securely early 2nd millennium. No for Gulf or Indus impressions: one.

## 4. Verdict

- **Feasible:** a pilot on CC0 Yale photos plus the five controls, with the later-period pool to raise the count of true stamps.
- **Blocked:** the all-CDLI and all-BDTNS sweep, by image terms and by the 60-second crawl delay.
- **Weak point:** a detector that passes the kill test has shown it finds Old Assyrian and later stamps. Whether it finds a Gulf stamp rests on YBC 5447 alone.
