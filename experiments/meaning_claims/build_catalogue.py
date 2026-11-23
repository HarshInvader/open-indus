"""Builds CATALOGUE.csv (meaning proposals from culture, archaeology and history).
Run: .venv/bin/python -I experiments/meaning_claims/build_catalogue.py
No data are tested here. Counts in the power column come from counts.py (descriptive)."""
import csv
from pathlib import Path

COLS = ["id", "author", "year", "signs_M", "signs_W", "claimed_meaning", "basis", "source",
        "in_old_catalogue", "status", "status_detail", "rule", "prediction", "data", "power",
        "kill_condition", "ladder_if_positive", "rank"]

H = "https://www.harappa.com"
R = []
def add(**k): R.append(k)

# ---------------- Mukhopadhyay ----------------
add(id="MUK25-fish-gem", author="Mukhopadhyay", year="2025 (SSRN 5079207; earlier 2023 SSRN 4412558)",
    signs_M="M59 M60 M65-M75 (fish family)", signs_W="W220 W226 W231 W232 W233 W235 W236 W240 W241 W243",
    claimed_meaning="fish signs denote gemstones, beads, jewellery and shiny metals (Dravidian min/mani; Mesopotamian 'fish-eye stones' NA4.IGI.KU6)",
    basis="context (seals with fish found in lapidary workshops and jewellers' shops) + culture (word chain)",
    source="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5079207 (abstract only; full text not opened)",
    in_old_catalogue="no", status="already tested / untestable",
    status_detail="Updated 2026-11-23: experiments/bead_workshops coded bead/jeweller units blind to signs: only 4 primary units with 32 inscribed objects at unseen sites; power about 21% at 1.5x under clustering (56% at 2x), so no test was run. The western-object side prediction fails at low power (experiments/meluhha goods.py).",
    rule="If fish signs mean 'gem/bead', inscribed objects from bead, lapidary or jeweller contexts carry fish signs more often than objects from other units of the same site, against a null that permutes unit labels within site and weights each unit by its total find count.",
    prediction="Fish share on bead/lapidary-unit objects at least 2x the find-density-matched expectation, at two sites.",
    data="experiments/assemblage/craft_units.csv + linked_objects.csv (BEAD coded at Chanhu-daro and Harappa only). Needs new coding of Mohenjo-daro jewellers' hoards and bead debris by house from Mackay 1938 / Marshall 1931 OCR already used by assemblage/build_coding.py.",
    power="Base rate: fish on 27% of distinct ICIT texts (945/3504), 34% of M77 (781/2270). BEAD units now: 31 objects (Chanhu-daro 28, Harappa 3), mostly seals, in about 5 squares. If objects were independent, OR 2 gives power about 0.6 and OR 3 about 0.9 (one-sided 0.05). Clustering in 5 squares cuts this a lot. About 80 independent objects are needed for 0.8 at OR 2. NOTE: Chanhu-daro BEAD fish counts were seen while building counts.py, so Chanhu-daro is discovery only.",
    kill_condition="Fish share in coded bead/jeweller units at or below the find-density-matched expectation (ratio <= 1.2) at the confirmation site(s) with power >= 0.8 for ratio 2; or ratio < 1 at both Mohenjo-daro and Harappa.",
    ladder_if_positive="L2 (semantic field: precious goods)", rank="1")

add(id="MUK25-beadstring", author="Mukhopadhyay", year="2025",
    signs_M="bead-string-like sign (M-number to fix from her figures)", signs_W="",
    claimed_meaning="string of beads; with fish on the Kalibangan drain pipe it labels a bead container",
    basis="picture + context (one Kalibangan drain pipe)",
    source="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5079207 (abstract)",
    in_old_catalogue="no", status="testable (companion to MUK25-fish-gem)",
    status_detail="Sign identity must be fixed from the paper's figures before any count.",
    rule="Same test as MUK25-fish-gem for the bead-string sign.",
    prediction="Enriched on bead/lapidary-unit objects.",
    data="as MUK25-fish-gem", power="Unknown until the sign is identified; likely a rare sign, so power is low.",
    kill_condition="No enrichment at power >= 0.8; or sign has < 20 distinct texts (declare untestable).",
    ladder_if_positive="L2", rank="9")

add(id="MUK22-gold-ratti", author="Mukhopadhyay", year="2022 (SSRN 4110151)",
    signs_M="signs on Mohenjo-daro gold-assaying needles (M-numbers not reached)", signs_W="",
    claimed_meaning="'gold' and 'ratti' (seed weight) signs; fish-like signs = gemstones and weight standards",
    basis="context (inscribed needles) + culture (ratti weight)",
    source="https://ouci.dntb.gov.ua/en/works/7qnLvVQ4/ (record); full text not opened",
    in_old_catalogue="no", status="untestable with our data",
    status_detail="The claim is built on the needles themselves. ICIT has 18 distinct implement texts and 5 gold/silver objects, so no independent sample exists.",
    rule="", prediction="", data="ICIT type IMPL, material Gold/Silver", power="n <= 5 independent objects",
    kill_condition="", ladder_if_positive="L2", rank="")

add(id="MUK23-cup-vessel-fee", author="Mukhopadhyay", year="2023",
    signs_M="M328 (with 2/3/4/6 tall strokes)", signs_W="W700",
    claimed_meaning="standardized-capacity vessel; on tablet reverses it gives one of four licence-fee slabs",
    basis="picture (offering vessel on a tablet) + context (tablet reverses) + culture (cuneiform GAR/ninda)",
    source="https://doi.org/10.1057/s41599-023-02320-7 pp. 25-26",
    in_old_catalogue="partly (M328 metrological)", status="already tested",
    status_detail="See experiments/m328_measure (count not a measure; fixed values), experiments/tablet_archives (26 obverse texts carry 2-3 different tiers; sign x tier p = 0.75), experiments/scene_text (vessel unreadable at 100 ppi).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L3", rank="")

add(id="MUK23-licence-pairing", author="Mukhopadhyay", year="2023",
    signs_M="obverse text + reverse M328 docket", signs_W="",
    claimed_meaning="obverse = licensed activity; reverse = fee slab for that activity",
    basis="context + modern licence analogy", source="https://doi.org/10.1057/s41599-023-02320-7 pp. 25-26",
    in_old_catalogue="no", status="already tested",
    status_detail="experiments/tablet_archives finding 3: obverse texts do not split by tier (S = 101, p = 0.75); incised W176 W740 W400 occurs with tiers 2, 3 and 4.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L1", rank="")

add(id="MUK23-triple-cup-goblet", author="Mukhopadhyay", year="2023",
    signs_M="M328 x3 (triplicated cup) on goblet stamps", signs_W="W700",
    claimed_meaning="a denomination of a volumetric unit stamped on pointed-base goblets",
    basis="context (stamped goblets)", source="https://doi.org/10.1057/s41599-023-02320-7 p. 25",
    in_old_catalogue="no", status="untestable with our data",
    status_detail="Every known example is the basis of the claim. A test needs goblet capacities per stamp type, which are not in open data.",
    rule="If it is a volume denomination, stamped goblets should be more uniform in capacity than unstamped goblets of the same phase.",
    prediction="", data="none in repo (goblet volumes)", power="", kill_condition="", ladder_if_positive="L3", rank="")

add(id="MUK23-no-names-no-toponyms", author="Mukhopadhyay", year="2023",
    signs_M="all", signs_W="", claimed_meaning="texts encode no personal names or place names; they encode commodities, fees and rules",
    basis="context + script-internal", source="https://doi.org/10.1057/s41599-023-02320-7 pp. 9-12, 22-23",
    in_old_catalogue="no", status="already tested",
    status_detail="experiments/toponyms (no travelling place names), experiments/identifiers (identifier vs label undecidable once length is matched), experiments/administration (not commodity labels on Lothal backs).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="MUK23-emblem-organisation", author="Mukhopadhyay", year="2023",
    signs_M="field animal (not a sign)", signs_W="",
    claimed_meaning="seal animals are emblems of guilds or tax authorities; same-emblem seals share licence content",
    basis="context + culture", source="https://doi.org/10.1057/s41599-023-02320-7 pp. 18-23",
    in_old_catalogue="no", status="already tested",
    status_detail="experiments/context Q1: unicorn vs other AUC 0.52; same-emblem Jaccard at null in 16/16 class tests.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="MUK23-kanmer-occupation", author="Mukhopadhyay; Kharakwal et al.", year="2023; 2012",
    signs_M="walking person with implement at waist (M-number not fixed)", signs_W="",
    claimed_meaning="an occupation (agate workers?) needing gate passes at fortified Kanmer",
    basis="context (Kanmer pendants near an agate quarry)", source="https://doi.org/10.1057/s41599-023-02320-7 p. 35; Kharakwal et al. 2012 p. 832",
    in_old_catalogue="no", status="untestable with our data", status_detail="Kanmer has 4 distinct ICIT texts.",
    rule="", prediction="", data="", power="n = 4", kill_condition="", ladder_if_positive="L2", rank="")

add(id="MUK23-wild-ass", author="Mukhopadhyay; Kharakwal et al.", year="2023; 2012",
    signs_M="'wild ass' sign (scribbled on a Kanmer pendant reverse)", signs_W="",
    claimed_meaning="emblem of a Kutch authority (wild ass is a Kutch animal)",
    basis="picture + regional fauna", source="https://doi.org/10.1057/s41599-023-02320-7 pp. 22-23",
    in_old_catalogue="no", status="untestable with our data",
    status_detail="Kutch sites outside Dholavira have 19 distinct ICIT texts in all; the sign is not a regular sign-list entry.",
    rule="If a regional emblem, the sign is confined to Kutch sites.", prediction="", data="ICIT site", power="< 20 texts", kill_condition="", ladder_if_positive="L2", rank="")

add(id="MUK21-pilu", author="Mukhopadhyay", year="2021",
    signs_M="none named", signs_W="", claimed_meaning="Indus word pilu 'elephant/ivory/toothbrush tree', borrowed as Akkadian piru",
    basis="culture (loanword chain)", source="https://doi.org/10.1057/s41599-021-00868-w",
    in_old_catalogue="no", status="untestable with our data",
    status_detail="A language claim with no sign attached. No script test follows without a sign.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L4", rank="")

add(id="MUK19-crop-on-jars", author="Mukhopadhyay; Kenoyer", year="2019; 2006",
    signs_M="M161 M162 M169 (+ preceding strokes)", signs_W="W064 W390 W405 W406 W407",
    claimed_meaning="crop/commodity; with numerals on jar bodies it gives a quantity of grain or oil",
    basis="picture (plant) + context (jar graffiti)", source="https://doi.org/10.1057/s41599-019-0274-1 (CROP section); Kenoyer 2006 cited there",
    in_old_catalogue="yes (CROP)", status="testable (currently underpowered)",
    status_detail="Lothal sealing backs (administration t4: W390 p = 0.65) and western objects (meluhha) were tested. Storage-jar vs other-vessel was not.",
    rule="If crop+numeral records a grain/oil quantity, it sits on storage jars more than on bowls, dishes or seals, within site.",
    prediction="Crop+numeral share on storage-jar graffiti >= 2x that on other vessel forms.",
    data="datasets/open/vessel_marks.csv (vessel_form), ICIT POT types",
    power="Crop signs on 23 of 347 distinct ICIT pottery texts. Vessel form is recorded for about 20 of 650 inscribed vessels, so power is near zero now. Needs the Harappa 1986-2003 sherd register with forms.",
    kill_condition="With >= 150 form-recorded vessels: crop+numeral share on storage jars <= share on other forms.",
    ladder_if_positive="L2", rank="5")

add(id="MUK19-class-exclusivity", author="Mukhopadhyay", year="2019",
    signs_M="the two CROP signs; the PPF signs; PF1 (M342)", signs_W="",
    claimed_meaning="members of a class are mutually exclusive logograms (a paradigm: one slot, one filler)",
    basis="script-internal (used to argue logograms)", source="https://doi.org/10.1057/s41599-019-0274-1 (logographic-nature section)",
    in_old_catalogue="no", status="testable",
    status_detail="Atlas 7.4 tested graphic modifiers, not these classes. Her counts (crop signs in 162 and 137 lines, never together; no line with two PPF signs in 309) were never put under a null.",
    rule="Under a length- and position-preserving shuffle, two signs with these frequencies share a line far more often than observed.",
    prediction="Observed co-occurrence of class members below the 5th percentile of the shuffle, on dev and on held-out families.",
    data="M77 dev/held-out; sign mapping from her figures to M-numbers (manual)",
    power="Crop group 301 distinct M77 texts (dev 236, held-out 65). Expected chance co-occurrence for two signs in about 150 lines each, mean length 4.6, is only a few lines, so the test separates 'never' from 'rare' only weakly. Compute power by planting exclusive pairs first.",
    kill_condition="Observed co-occurrence within the shuffle's central 90% on held-out.",
    ladder_if_positive="L1", rank="7")

add(id="MUK19-stroked-jar-MET", author="Mukhopadhyay", year="2019",
    signs_M="jar signs with infixed strokes (M-numbers to fix)", signs_W="",
    claimed_meaning="metrological units of volume",
    basis="picture + context (jar bodies)", source="https://doi.org/10.1057/s41599-019-0274-1 (MET section)",
    in_old_catalogue="no", status="testable",
    status_detail="experiments/self_label found vessel-looking signs depleted on pottery (M342, M336, M343). Stroked-jar variants were not tested on their own.",
    rule="If they are volume units, stroked-jar signs are enriched on pottery against the within-site object-type null.",
    prediction="Enrichment >= 2x on pottery.", data="ICIT POT vs other types",
    power="Rare signs; likely < 30 texts in total. Run only if >= 30.", kill_condition="Ratio <= 1 on pottery.",
    ladder_if_positive="L2", rank="10")

# ---------------- Mahadevan ----------------
add(id="MAH09-jar-bearer", author="Mahadevan", year="2009",
    signs_M="jar-bearer ligature (bearer M12 family + jar)", signs_W="",
    claimed_meaning="one who carries a sacrificial vessel (priestly officiant); jar = priestly elite (Agastya, 'jar-born')",
    basis="picture + culture (Agastya legend)", source=H + "/sites/default/files/pdf/meluhha_and_agastya_2009.pdf (403 to us; summarised from search result and Jyothibabu review)",
    in_old_catalogue="partly (M342 priest)", status="already tested",
    status_detail="Priest vs warrior predicts different precincts: experiments/administration P6-P7 (final M342 and M211 vs area: 0/12 held-out) and reg_findspot (jar null at 3x in two cities).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L2", rank="")

add(id="MAH09-arrow-bearer", author="Mahadevan", year="2009",
    signs_M="arrow-bearer ligature; M211", signs_W="W520",
    claimed_meaning="warrior ('one who carries the arrow')", basis="picture + culture",
    source=H + "/content/arrow-sign-indus-script-5 (403 to us)", in_old_catalogue="partly (M211 military)",
    status="already tested", status_detail="As MAH09-jar-bearer. 'Man never with arrow' was tested in experiments/dominik_w090 (mixed; not special).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L2", rank="")

add(id="MAH-bearer-kaviti", author="Mahadevan (via Jyothibabu review)", year="1980s-2009",
    signs_M="M12 (bearer)", signs_W="", claimed_meaning="officer title (Tamil kaviti 'yoke-bearer'); later Sanskrit bhartr 'lord'",
    basis="picture + culture", source="https://www.researchgate.net/publication/370480645",
    in_old_catalogue="partly (M12 poraiyan)", status="untestable with our data",
    status_detail="A title needs an external role record. Positional behaviour is L1 and is in experiments/functional_reading.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L2", rank="")

add(id="MAH-fish-bath", author="Mahadevan", year="c. 2011",
    signs_M="M59 family", signs_W="", claimed_meaning="UNVERIFIED: ties the fish sign to the Great Bath ritual",
    basis="culture", source=H + "/sites/default/files/pdf/The%20Indus%20Fish%20Swam%20in%20the%20Great%20Bath.pdf (403 to us; content not read)",
    in_old_catalogue="no", status="untestable with our data",
    status_detail="Full text not reached. If it predicts fish signs near the Great Bath (Mohenjo-daro SD), experiments/administration P7 found no area effect.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

# ---------------- Parpola ----------------
add(id="PAR-vel-substitution", author="Parpola", year="1994; 2010",
    signs_M="M87 (two tall strokes) vs M59", signs_W="W032 vs W220",
    claimed_meaning="M87 = vel (spear/god); fills the same slot as fish (M-172 vs H-6)",
    basis="culture (Murukan vel) + one substitution", source="Parpola 2010 Coimbatore lecture pp. 27-29 (experiments/news_read/raw/parpola-1994)",
    in_old_catalogue="partly (numerals)", status="already tested",
    status_detail="Updated 2026-11-23: experiments/parpola_rules34 (prereg parpola_rules34): known-answer gate 1/50 = 2% (bar 80%), so underpowered; real pair not passing (dev p 0.22, held-out 0.31, new sites 0.23). M87 sits next to fish, not in its slot.",
    rule="If M87 and M59 are interchangeable, their left and right contexts overlap more than for frequency-matched sign pairs.",
    prediction="Context-overlap of M87/M59 above the 95th percentile of 50 frequency-matched pairs, on dev, then held-out.",
    data="M77 dev/held-out; ICIT check", power="M87 in 232 distinct M77 texts, M59 in 289 (held-out 53 and 62). Ample for a strong substitution.",
    kill_condition="Overlap at or below the median of matched pairs on held-out.", ladder_if_positive="L1", rank="3")

add(id="PAR-murukan-partners", author="Parpola", year="1994; 2010",
    signs_M="M403 + M87 (Muruka-vel); M403 + squirrel sign (Muruka-ppillai)", signs_W="W840 + W032",
    claimed_meaning="fixed names of the god Murukan", basis="culture (Old Tamil names)",
    source="Parpola 2010 pp. 23-29", in_old_catalogue="partly (M403 muruku; squirrel without sign)",
    status="already tested", status_detail="Updated 2026-11-23: experiments/parpola_rules34 (prereg parpola_rules34; gate 96%): M403 -> M87 is a fixed pair on dev (23/48, p 0.0014), held-out (4/17, p 0.003) and new sites (4/9, p 0.0009), red team 'fragile' only under a degenerate near-copy collapse; the squirrel partner (M51/M52) never follows M403 (0/74). The fixed pair is Parpola's starting observation, not the reading (M87 is also tall-stroke 2).",
    rule="If M403+M87 and M403+squirrel are fixed names, M403's next sign is concentrated on these two far beyond a frequency-matched null, as six+fish is (README #5).",
    prediction="Share of M403 tokens followed by M87 or the squirrel sign >= 0.4 on held-out, above the null 99th percentile.",
    data="M77 dev/held-out, ICIT", power="M403 in 66 distinct M77 texts (dev 49, held-out 17); ICIT 94. A six+fish-strength pair (12/25) is easy to detect; a weak one is not. Squirrel sign M-number to fix from drawings first.",
    kill_condition="Held-out partner share inside the null central 90%.", ladder_if_positive="L1", rank="4")

add(id="PAR-vata-min", author="Parpola", year="1994; 2010",
    signs_M="fig/banyan sign + M59", signs_W="", claimed_meaning="vata-min 'north star'",
    basis="culture", source="Parpola 2010 pp. 19-21", in_old_catalogue="yes (no sign number)",
    status="testable", status_detail="Not tested. Fish partner set is known (M53, M387, M343, M171, M389; core_semantics).",
    rule="Fig+fish is a fixed pair beyond a frequency-matched null.", prediction="As six+fish.",
    data="M77, ICIT", power="Fig sign to identify; if it is one of the fish partners above, n is several dozen texts.",
    kill_condition="Pair rate inside null central 90% on held-out.", ladder_if_positive="L1", rank="8")

add(id="PAR75-chanhu-toponym", author="Parpola (cited by Mukhopadhyay 2023)", year="1975",
    signs_M="M93", signs_W="W031 W032 (Wells splits it)", claimed_meaning="the ancient name of Chanhu-daro",
    basis="context (found only at Chanhu-daro)", source="https://doi.org/10.1057/s41599-023-02320-7 p. 22",
    in_old_catalogue="no", status="already tested",
    status_detail="experiments/toponyms finding 4: local end mark at Chanhu-daro (10/10 texts), replicated; nothing local travels on sealings.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="PAR-sign193-weight", author="Parpola (sign list, as reproduced on Wikiversity)", year="1994",
    signs_M="Parpola sign 193 (Mahadevan number not verified)", signs_W="",
    claimed_meaning="weight / metrology", basis="picture", source="https://en.wikiversity.org/wiki/Indus_Script",
    in_old_catalogue="no", status="already tested",
    status_detail="Updated 2026-11-23: experiments/weight_sign (prereg weight_sign): Parpola 193 is M206/M208 (not M197), in 9 distinct texts, too rare to test; M197 on fresh data has 5 texts and planted power 7% (bar 80%). Verdict underpowered.",
    rule="If a sign means 'weight', it is enriched on objects from units with weights, against a null that weights units by total finds.",
    prediction="Ratio >= 2 at Harappa and Mohenjo-daro.", data="experiments/assemblage/assemblages.csv, linked_objects.csv",
    power="WEIGHT units: Harappa 610 objects (442 non-seal), Mohenjo-daro 38. M197 is in 55 distinct M77 texts, W575 in 67 ICIT. Mohenjo-daro side is too small for 0.8 power unless ratio >= 5.",
    kill_condition="Ratio <= 1.2 at Harappa under the find-density null, or the mapped sign is not M197 and has < 30 texts.",
    ladder_if_positive="L2 (metrology)", rank="2")

add(id="PAR-man-steelyard", author="Parpola (sign list)", year="1994",
    signs_M="M1", signs_W="W090", claimed_meaning="porter/carrier; Dravidian homophones include 'lever of a steelyard'",
    basis="picture + culture", source="https://en.wikiversity.org/wiki/Indus_Script", in_old_catalogue="partly (M1 al)",
    status="already tested", status_detail="experiments/assemblage x1: M1 storage signal was one seal (dead lead); WEIGHT units not enriched.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

# ---------------- Wells ----------------
add(id="WEL15-jar-40L", author="Wells (as reported by Rao 2018)", year="2015",
    signs_M="M342 or M328 (sign image lost in Rao's text)", signs_W="W740/W700",
    claimed_meaning="volumetric measure of about 40 L; a related sign about 160 L",
    basis="context (pot volume)", source="https://arxiv.org/abs/1812.00049 (citing Wells 2015)", in_old_catalogue="partly (M328 volumetric)",
    status="already tested", status_detail="experiments/m342_offsite (untestable, leans against), experiments/m328_measure (dead), self_label (jar rarer on jars).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L3", rank="")

add(id="WEL15-17-signs", author="Wells", year="2015",
    signs_M="17 signs (list not reached)", signs_W="", claimed_meaning="17 signs identified with Dravidian values; some sequences are verbs or nouns",
    basis="script-internal + language", source="https://www.archaeopress.com/Archaeopress/DMS/3608E8E0F92C4920AE82709E2A32643F/9781784910464-sample.pdf (blurb)",
    in_old_catalogue="no", status="untestable with our data", status_detail="Book not open; list not reached. If obtained, values can go on the phonetic bench (atlas 1.1).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L4", rank="")

add(id="WEL15-fish-number", author="Wells", year="2015",
    signs_M="M59 + numerals (W220 clusters)", signs_W="W220", claimed_meaning="fish + number clusters as fixed units",
    basis="script-internal", source="Wells 2015 figs 3.20-3.22 (TOC only)", in_old_catalogue="no",
    status="already tested", status_detail="atlas 6.9 and README #5 (six+fish fixed; M59 carries the number-name effect).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

# ---------------- Kenoyer / Meadow / Vidale / Frenez / Laursen ----------------
add(id="KEN06-jar-strokes", author="Kenoyer", year="2006 (cited in Mukhopadhyay 2019)",
    signs_M="stroke numerals on jar bodies and rims", signs_W="", claimed_meaning="measure of oil or grain in the jar before sealing",
    basis="context", source="https://doi.org/10.1057/s41599-019-0274-1 (quoting Kenoyer 2006)", in_old_catalogue="no",
    status="untestable with our data", status_detail="Needs capacity per inscribed vessel. experiments/magnitude found no usable size data for pots.",
    rule="Stroke count rises with vessel capacity within one vessel form.", prediction="", data="none (vessel capacities)", power="", kill_condition="", ladder_if_positive="L3", rank="")

add(id="KM-tablets-tokens", author="Kenoyer & Meadow; Rao", year="2010; 2018",
    signs_M="moulded/incised tablet texts", signs_W="", claimed_meaning="transaction tokens or ration records; deliberate disposal of tablet groups",
    basis="context", source=H + "/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf (403 to us); https://arxiv.org/abs/1812.00049",
    in_old_catalogue="no", status="already tested", status_detail="experiments/tablet_archives (0/5), experiments/slot_function B (counted people not supported).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="KEN20-premature-marks", author="Kenoyer", year="2020",
    signs_M="M342, M347", signs_W="", claimed_meaning="pre-Mature post-firing pot marks: owner or user marks that became script signs",
    basis="context (stratified sherds)", source=H + "/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script.pdf",
    in_old_catalogue="no", status="already tested", status_detail="experiments/potters_marks (descriptive; frame vs core OR 1.26, p = 0.39).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="HV-bangle-workshop", author="Halim & Vidale; Kenoyer", year="1984; 1990s",
    signs_M="M373/M374 oval; M403", signs_W="W790", claimed_meaning="stoneware-bangle inscriptions are workshop, batch or owner marks",
    basis="context (kiln production)", source="experiments/bangle_oval RESULTS (secondary)", in_old_catalogue="partly",
    status="already tested", status_detail="experiments/bangle_oval H1 untestable (n = 0 new bangles); H4b leans workshop (5/27 vs 0/13, p = 0.15).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="FT05-access-control", author="Frenez & Tosi; Frenez", year="2005; 2018",
    signs_M="seal texts on Lothal sealings", signs_W="", claimed_meaning="seals controlled access to stored goods; elephant-seal boxes tied to maritime trade",
    basis="context (sealing backs)", source="https://www.academia.edu/78555754 ; https://www.academia.edu/41634804",
    in_old_catalogue="no", status="already tested", status_detail="experiments/administration P13-P14, experiments/sealing_function (route closed by sample size).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="VID05-bison-abroad", author="Vidale", year="2004-2005",
    signs_M="field animal (bison/short-horned bull)", signs_W="", claimed_meaning="bison emblem marks clans in the western trade",
    basis="context (seals abroad)", source=H + "/sites/default/files/201402/Vidale-Indus-Mesopotamia.pdf (403 to us; cited in Mukhopadhyay 2023)",
    in_old_catalogue="no", status="already tested", status_detail="Not a sign claim. Emblem-text link: context Q1 (null). Foreign texts: meluhha goods, README #4.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="LAU10-twins-prefix", author="Laursen", year="2010",
    signs_M="'twins' sign (likely M87 = W032; check against his figures)", signs_W="W032?",
    claimed_meaning="a prefix common on Gulf-type seals; part of a non-Harappan (Dilmun) language or name formula",
    basis="context (Gulf seals) + Parpola's observation", source="https://doi.org/10.1111/j.1600-0471.2010.00329.x pp. 117-118 (abstract only read)",
    in_old_catalogue="no", status="testable (very low power)",
    status_detail="Round Gulf seals breaking order is README #4. The twins prefix itself is untested. Our foreign corpus has 46 legible texts; only 3 contain W032 in our transcription, so the sign mapping must be checked first.",
    rule="If 'twins' is a prefixed title, on Gulf-type seals it is text-initial more often than at home and is followed by many different sequences.",
    prediction="Initial rate on Gulf seals >= 3x the home initial rate of the same sign; follower diversity at the null for a title.",
    data="datasets/open/foreign_seal_texts.csv; M77/ICIT home texts",
    power="n of Gulf texts with the sign is 3 (W032) by our transcription. Power negligible unless the mapping adds more.",
    kill_condition="Fewer than 8 Gulf texts carry the sign after mapping (declare untestable), or initial rate not above home.",
    ladder_if_positive="L1", rank="6")

add(id="LAU10-other-language", author="Laursen; Parpola", year="2010; 1994",
    signs_M="Gulf round-seal texts", signs_W="", claimed_meaning="Gulf seals write another language with Indus signs",
    basis="context", source="https://doi.org/10.1111/j.1600-0471.2010.00329.x", in_old_catalogue="no",
    status="already tested", status_detail="README #4 and correction: off-order is a property of round Gulf-type seals wherever found; three readings cannot be separated.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

# ---------------- Farmer/Sproat/Witzel, Possehl, Koskenniemi, Fairservis, others ----------------
add(id="FSW04-emblems", author="Farmer, Sproat & Witzel", year="2004",
    signs_M="all", signs_W="", claimed_meaning="non-linguistic emblems of deities, clans and offices (cf. kudurru symbols); number signs symbolic",
    basis="culture (Near Eastern emblem systems) + statistics", source="https://safarmer.com/fsw2.pdf pp. 19-57",
    in_old_catalogue="no", status="already tested / untestable",
    status_detail="Emblem-text link null (context Q1); numerals do not match any quantity class (numeral_class); language vs code untestable (atlas 3.1-3.2).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="POS96-survey", author="Possehl", year="1996",
    signs_M="none", signs_W="", claimed_meaning="no new sign meaning; surveys earlier decipherments; seals as identity/office markers",
    basis="review", source="Possehl 1996, Indus Age: The Writing System (not open)", in_old_catalogue="no",
    status="untestable with our data", status_detail="No sign-level claim to test. Office/identity covered by administration and identifiers.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="KOS-segmentation", author="Koskenniemi (with Parpola)", year="1970s-1981",
    signs_M="none", signs_W="", claimed_meaning="no meaning claims found; segmentation and sign classes only",
    basis="script-internal", source="Parpola 1994 pp. 68-82 (as listed in contents)", in_old_catalogue="no",
    status="untestable with our data", status_detail="Structural work, covered by grammar and functional_reading.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="FAI92-honorifics", author="Fairservis", year="1992",
    signs_M="M59 and others", signs_W="", claimed_meaning="fish = loom-twist, used as an honorific; seal texts = names and titles of chiefs",
    basis="picture + rebus + archaeology", source="https://doi.org/10.1163/9789004676756 ; fish gloss via Sparavigna (cogprints 6179)",
    in_old_catalogue="no", status="already tested",
    status_detail="His key failed the shuffle bench (atlas 1.1; literature RESULTS). Book text not read: the only full copy online is an unlicensed upload.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="KAL-metalwork", author="Kalyanaraman", year="2010-2019",
    signs_M="most signs", signs_W="", claimed_meaning="rebus readings for metalwork and 'wealth-accounting ledgers' (e.g. drongo = steel)",
    basis="rebus (fringe)", source="https://academia.edu/38240522", in_old_catalogue="no",
    status="untestable with our data",
    status_detail="No fixed one-value-per-sign key, so any outcome fits. Copper context tested in assemblage (zero power).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="KNO-team", author="Knorozov, Volchok et al.", year="1965-1981",
    signs_M="various", signs_W="", claimed_meaning="Dravidian values for many signs (specific values not reached)",
    basis="language + picture", source="cited in experiments/literature RESULTS", in_old_catalogue="no",
    status="untestable with our data", status_detail="Values not in hand. If obtained, they go on the phonetic bench.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="L4", rank="")

add(id="KW74-indo-sumerian", author="Kinnier Wilson", year="1974",
    signs_M="various", signs_W="", claimed_meaning="Sumerian logogram values",
    basis="picture + language", source="Kinnier Wilson 1974, Indo-Sumerian (not open)", in_old_catalogue="no",
    status="already tested", status_detail="Sumerian as the language: atlas 1.8 (z 0.33-0.54) and 2.4 (Meluhha interpreter). Sign values not in hand.",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="MEL-goods", author="Laursen & Steinkeller; Parpola; others", year="1977-2017",
    signs_M="candidates: tree W390/W405, fish W220, cup W700", signs_W="",
    claimed_meaning="Meluhha goods in cuneiform (carnelian, ivory, ab-ba and mes wood, copper, gold dust, dar-bird, dogs) as possible sign referents",
    basis="culture (cuneiform trade texts)", source="experiments/meluhha/catalogue.csv",
    in_old_catalogue="no", status="already tested",
    status_detail="No published scholarly sign-to-good link was found outside fringe rebus work. Candidates tested on 30 western objects: none enriched; jar depleted (experiments/meluhha goods.py).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

add(id="GREEN-offices", author="Green; Mukhopadhyay", year="2018-2023",
    signs_M="none (object level)", signs_W="", claimed_meaning="seals and weights co-occur in public buildings (Mohenjo-daro DK-G 8A, 6A) used for administration",
    basis="context", source="https://doi.org/10.1057/s41599-023-02320-7 p. 35", in_old_catalogue="no",
    status="untestable with our data", status_detail="Not a sign claim. Household/office signature in seal texts refuted (reg_findspot, reg_harappa).",
    rule="", prediction="", data="", power="", kill_condition="", ladder_if_positive="", rank="")

out = Path(__file__).with_name("CATALOGUE.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
    for r in R: w.writerow({c: r.get(c, "") for c in COLS})
import collections
print(len(R), collections.Counter(r["status"].split(" (")[0] for r in R))
