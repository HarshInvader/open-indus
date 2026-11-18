"""Build datasets/: catalog.csv (every Indus data source the project uses) and open/ (the project's own tables).

    .venv/bin/python -I datasets/build.py

Rules:
- open/ holds only tables this project made. Tables over MAX_TEXT_ROWS rows lose any column that holds whole
  Indus sign texts (M### / W### sequences): the two corpora they come from have no terms that allow
  republishing (LICENSING.md). Catalogue numbers (CISI, ICIT id, M77 text_no) are kept so the texts can be
  re-joined after `datasets/fetch.py corpus`.
- catalog.csv lists every source: what it is, where it comes from, its terms, and whether it is
  included here, fetchable by datasets/fetch.py, or reference only.
"""
import csv, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets"
OPEN = OUT / "open"
MAX_TEXT_ROWS = 60
# columns that list sign numbers (not inscriptions) and must be kept; columns of whole texts the pattern misses
KEEP_COLS = {"m77_match", "variant_family", "lookalike_but_distinct"}
FORCE_DROP = {"assemblage_linked_objects.csv": {"seq_wells"}}
SIGNSEQ = re.compile(r"^\s*([MW]\d{1,3}[a-z]?[\s,;|#-]*){2,}$")

# (source file, published name, description)
OPEN_TABLES = [
    ("experiments/old_registers/registers.csv", "registers_1931_1940.csv", "Object registers of the 1931-1943 excavation reports (Marshall, Mackay, Vats), OCR transcribed and repaired: object no., findspot, depth, size, material, M77 link."),
    ("experiments/old_registers/fem_seals.csv", "register_mackay1938_seals.csv", "Mackay 1938 (Further Excavations at Mohenjo-daro) seal register: size, material, block/house/room, level."),
    ("experiments/old_registers/eh_seals.csv", "register_vats1940_seals.csv", "Vats 1940 (Excavations at Harappa) seal register: size, mound, depth, find no."),
    ("experiments/old_registers/mic_seals.csv", "register_marshall1931_seals.csv", "Marshall 1931 (Mohenjo-daro and the Indus Civilization) seal register."),
    ("experiments/old_registers/ce_seals.csv", "register_mackay1943_chanhudaro_seals.csv", "Mackay 1943 (Chanhu-daro Excavations) seal list."),
    ("experiments/reg_findspot/findspots.csv", "findspots_mohenjodaro.csv", "Mohenjo-daro seals: parsed block/house/room and depth, linked to M77 text numbers."),
    ("experiments/reg_harappa/findspots.csv", "findspots_harappa.csv", "Harappa seals (Vats 1940): mound, square, depth, linked to M77/ICIT/CISI."),
    ("experiments/fish_marshall/prose_findspots.csv", "findspots_marshall_prose.csv", "Findspots stated in the prose of Marshall 1931."),
    ("experiments/assemblage/craft_units.csv", "craft_units.csv", "Craft-activity evidence per excavation unit (Harappa, Mohenjo-daro, Lothal, Dholavira) with sources."),
    ("experiments/assemblage/assemblages.csv", "assemblages.csv", "Per excavation unit: crafts present and counts of inscribed objects."),
    ("experiments/assemblage/linked_objects.csv", "assemblage_linked_objects.csv", "Inscribed objects linked to excavation units."),
    ("experiments/carver_hands/clusters.csv", "seal_sizes_carver_clusters.csv", "Seal widths (mm) and photo-based carver clusters, by CISI/ICIT id."),
    ("experiments/tablet_archives/tablets.csv", "harappa_tablets.csv", "Harappa miniature tablets: type, material, mound, trench, HARP period, mould copy groups."),
    ("experiments/copper_series/types.csv", "copper_tablet_types.csv", "Mohenjo-daro copper tablet types (text + picture), counts in M77 and ICIT."),
    ("experiments/copper_series/tablets_typed.csv", "copper_tablets.csv", "Each copper tablet with its type, picture and sign face."),
    ("experiments/firing_stage/vessel_marks.csv", "vessel_marks.csv", "Inscribed and marked vessels: pre- or post-firing, vessel form and size, sources incl. Kenoyer 2021."),
    ("experiments/potters_marks/marks.csv", "potters_marks.csv", "Potter's marks from early and Mature Harappan sites (Rehman Dheri, Balakot, Kalibangan, Nausharo, Farmana, Gumla, Harappa) with firing stage and vessel type."),
    ("experiments/sealing_function/sealings.csv", "sealings.csv", "Clay sealings (Lothal and others): number of impressions, back type (door, jar, bundle), context."),
    ("experiments/magnitude/magnitude.csv", "inscribed_object_measurements.csv", "Masses and lengths of inscribed tools and objects from excavation reports."),
    ("experiments/elamite_bridge/objects.csv", "indus_objects_abroad.csv", "Indus-related inscribed objects found outside South Asia (Gulf, Mesopotamia, Iran), with context and publication."),
    ("experiments/foreign_corpus/foreign_corpus.csv", "foreign_seal_texts.csv", "Texts of Indus-sign seals found abroad, with findspot, shape, animal and date."),
    ("experiments/meluhha/catalogue.csv", "meluhha_cuneiform_mentions.csv", "Meluhha (the Indus region) in cuneiform texts: persons, goods, places, with text ids."),
    ("experiments/meluhha/foreign_objects.csv", "meluhha_foreign_objects.csv", "Indus objects abroad matched to cuneiform evidence from the same site and period."),
    ("experiments/sealing_hunt/candidates.csv", "meluhha_tablet_seal_candidates.csv", "Sealed cuneiform tablets naming Meluhha that need re-imaging (CDLI P-numbers)."),
    ("experiments/new_finds/new_texts.csv", "new_finds_post2010.csv", "Inscribed objects published after 2010 that are not in the corpora, with our readings."),
    ("experiments/open_journals/new_texts_extra.csv", "new_finds_open_journals.csv", "More new inscribed objects from open-access journals."),
    ("experiments/open_journals/context.csv", "open_journals_context.csv", "Excavation context for inscribed objects in open-access reports."),
    ("experiments/open_journals/pottery_marks.csv", "open_journals_pottery_marks.csv", "Pottery marks from open-access reports."),
    ("experiments/tn_brahmi_graffiti/both_sherds.csv", "tamil_nadu_sherds_graffiti_and_brahmi.csv", "Tamil Nadu sherds carrying both a graffiti mark and a Tamil-Brahmi text (Rajan & Sivanantham 2026)."),
    ("experiments/structure/sign_table.csv", "sign_statistics_m77.csv", "Per sign (Mahadevan numbers): frequency and share of initial, medial, final and standalone positions."),
    ("experiments/grammar/sign_classes.csv", "sign_positional_classes.csv", "Per sign: positional class (opener, connective, medial, closer...) with confidence."),
    ("experiments/modifiers/decomp.csv", "sign_decompositions.csv", "Compound signs split into base sign + modifier."),
    ("experiments/numeral_grammar/inventory.csv", "numeral_signs.csv", "Numeral signs in M77 and ICIT: value and layout."),
    ("experiments/harappa_com/sherd_phase_counts.csv", "harappa_marked_sherds_by_phase.csv", "Harappa marked sherds studied 1986-2003 by period (1,218 total), from Kenoyer 2020 Tables 3-4."),
    ("experiments/harappa_com/sherd_firing_counts.csv", "harappa_marked_sherds_firing.csv", "Pre- vs post-firing marks for 247 Ravi and Kot Diji phase sherds (Kenoyer 2020)."),
    ("experiments/harappa_com/marked_sherds.csv", "harappa_marked_vessels_2021.csv", "Eight Harappa marked vessels with object id, form and firing stage (Kenoyer 2021 Fig. 3)."),
    ("experiments/harappa_com/bangles.csv", "inscribed_bangles.csv", "Inscribed stoneware bangles: the 7 Harappa ICIT records plus 5 published illustrations (identities and diameters unknown)."),
    ("experiments/harappa_com/recent_objects.csv", "harappa_com_recent_objects.csv", "Inscribed objects shown on harappa.com, with source-year evidence and page links."),
    ("experiments/harappa_com/SOURCES.csv", "harappa_com_sources.csv", "Every harappa.com / HARP file located, with working URL, pixel size and terms note."),
    ("experiments/source_sweep/bangles_found.csv", "inscribed_bangles_franke1984.csv", "Inscribed stoneware bangles with outer/inner diameters read from Franke 1984 scans, matched to ICIT."),
    ("experiments/source_sweep/objects_found.csv", "objects_checked_2015_2026.csv", "Inscribed or seal-bearing objects from 2015-2026 publications (Gulf, Oman, Iran, South Asia) checked against our corpora."),
]

# Curated sources. tier: included | fetch | reference
SOURCES = [
    dict(id="corpus_m77", title="Mahadevan 1977, The Indus Script: Texts, Concordance and Tables (sign-by-sign texts)", kind="corpus", tier="fetch",
         origin="https://github.com/paragorth/Indus- (export of indusscript.in)", terms="Corpus is Mahadevan's work; no republishing terms stated", local="sources/paragorth_Indus-", fetch="corpus"),
    dict(id="corpus_icit", title="ICIT, Interactive Corpus of Indus Texts (Wells & Fuls), 5,679 inscriptions incl. post-1977 sites", kind="corpus", tier="fetch",
         origin="https://github.com/field-cady/indus_valley_script_corpus", terms="No data terms stated", local="sources/field-cady_indus_valley_script_corpus", fetch="corpus"),
    dict(id="bridge_wm", title="Mahadevan-Wells sign concordance and numeral/size notes (shaunmortal)", kind="corpus", tier="fetch",
         origin="https://github.com/shaunmortal/indus", terms="See repository", local="sources/shaunmortal_indus", fetch="corpus"),
    dict(id="joybose", title="joyboseroy/indus_decipher (data used for comparison)", kind="corpus", tier="fetch",
         origin="https://github.com/joyboseroy/indus_decipher", terms="See repository", local="sources/joyboseroy_indus_decipher", fetch="corpus"),
    dict(id="built_corpus", title="Cleaned M77 + ICIT texts with metadata and the dev/held-out split (data/)", kind="corpus", tier="fetch",
         origin="corpus/build.py from the two corpora above", terms="Derived from the corpora; not republished", local="data/", fetch="corpus"),
    dict(id="sign_images", title="Mahadevan's drawing of every sign (M1-M417)", kind="images", tier="reference",
         origin="indusscript.in (Roja Muthiah Research Library)", terms="Not stated", local="data/sign_images/", fetch=""),
    dict(id="cisi", title="Corpus of Indus Seals and Inscriptions (CISI), Joshi & Parpola 1987, Shah & Parpola 1991, vols 1-2 (photographs)", kind="photographs", tier="reference",
         origin="archive.org (scans); printed volumes, Suomalainen Tiedeakatemia", terms="In copyright; never republished here", local="experiments/iconography/raw/cisi", fetch=""),
    dict(id="cisi3", title="CISI vol. 3.1-3.3 (Harappa ICIT-era finds, HARP lot list)", kind="photographs", tier="reference",
         origin="Printed only", terms="In copyright", local="", fetch=""),
    dict(id="harappa_com", title="harappa.com / HARP: Kenoyer and Meadow papers, stoneware bangles, Harappa 1986-90 reports, slide images", kind="papers+images", tier="reference",
         origin="https://www.harappa.com (files under /sites/default/files/)", terms="Image-rights page: permission needed for reuse", local="experiments/harappa_com/raw", fetch=""),
    dict(id="kenoyer2021", title="Kenoyer 2021, Painted Indus script on ceramics and steatite, Ancient Pakistan 32", kind="paper", tier="fetch",
         origin="http://ojs.uop.edu.pk/ancientpakistan (open access)", terms="Open access", local="experiments/firing_stage/raw/kenoyer_painted", fetch=""),
    dict(id="ancient_pakistan", title="Ancient Pakistan journal, 35 issues indexed, 12 PDFs (Rehman Dheri marks, Gandi Umar...)", kind="papers", tier="fetch",
         origin="http://ojs.uop.edu.pk/ancientpakistan", terms="Open access", local="experiments/open_journals/raw/ancientpakistan", fetch=""),
    dict(id="asi_epub", title="ASI e-publications: MASI 110 Excavations at Kalibangan pt II; Indian Archaeology - A Review 2009-14", kind="reports", tier="fetch",
         origin="https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/<id> (ids 1-61)", terms="Government publication, free download", local="experiments/open_journals/raw/asi; experiments/new_finds/raw", fetch=""),
    dict(id="gujarat_dholavira", title="Dholavira object photographs (Gujarat museum accession images)", kind="photographs", tier="reference",
         origin="see experiments/new_finds/RESULTS.md", terms="Not stated", local="experiments/new_finds/raw/gujarat", fetch=""),
    dict(id="tn_graffiti", title="Rajan & Sivanantham 2026, Inscribed Potsherds of Tamil Nadu: Graffiti and Tamili, vols I-II", kind="catalogue", tier="fetch",
         origin="https://www.tamildigitallibrary.in (items 062969, 062968)", terms="Free official PDFs", local="experiments/tn_brahmi_graffiti/raw", fetch=""),
    dict(id="tn_graffiti_api", title="Tamil Nadu graffiti site x sign counts (9,349 occurrences, 53 sites)", kind="data", tier="fetch",
         origin="api.tamilknowledgecampus.in/graffiti/sites", terms="Not stated", local="experiments/tn_brahmi_graffiti/raw", fetch=""),
    dict(id="jalalabad", title="Vidale & Frenez 2021, Jalalabad cylinder seal with Indus signs (Fars)", kind="paper", tier="reference",
         origin="JARCS 2021", terms="Check journal", local="experiments/foreign_corpus/raw", fetch=""),
    dict(id="gadd1932", title="Gadd 1932, Seals of ancient Indian style found at Ur", kind="paper", tier="fetch",
         origin="https://archive.org/details/in.gov.ignca.33779", terms="1932 publication", local="experiments/foreign_readings/raw", fetch="reports"),
    dict(id="pam33", title="Majchrzak & Degli Esposti 2024, Umm al-Quwain stamp seal, PAM 33", kind="paper", tier="fetch",
         origin="Polish Archaeology in the Mediterranean 33 (open access)", terms="Open access", local="experiments/uaq_seal/raw", fetch=""),
    dict(id="cdli", title="CDLI cuneiform bulk dump (ATF + catalogue, 135,198 texts) - used for Meluhha mentions and seal legends", kind="corpus (non-Indus, Meluhha context)", tier="fetch",
         origin="https://github.com/cdli-gh/data", terms="CDLI data terms", local="experiments/short_labels/raw/cdli", fetch=""),
    dict(id="bdtns", title="BDTNS Ur III texts mentioning Meluhha", kind="corpus (Meluhha context)", tier="reference",
         origin="http://bdtns.filol.csic.es", terms="See site", local="experiments/sealing_hunt/raw/bdtns", fetch=""),
    dict(id="laursen2010", title="Laursen 2010, The westward transmission of Indus Valley sealing technology (Gulf seals)", kind="paper", tier="reference",
         origin="Arabian Archaeology and Epigraphy 21; copy on harappa.com", terms="In copyright", local="experiments/sealing_hunt/raw/laursen2010", fetch=""),
    dict(id="iith_restoration", title="IIT Hyderabad Indus sign-restoration deposit (probabilities per M77 position)", kind="model output", tier="fetch",
         origin="Zenodo (see experiments/bench_restoration/RESULTS.md)", terms="Zenodo record licence", local="experiments/bench_restoration/raw", fetch=""),
]


def is_seq_col(rows, col):
    vals = [r[col] for r in rows if r.get(col)]
    return bool(vals) and sum(bool(SIGNSEQ.match(v)) for v in vals) / len(vals) > 0.3


def build_open():
    if OPEN.exists():
        shutil.rmtree(OPEN)
    OPEN.mkdir(parents=True)
    man = []
    for src, name, desc in OPEN_TABLES:
        p = ROOT / src
        if not p.exists():
            print("missing", src); continue
        rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
        cols = list(rows[0].keys()) if rows else []
        drop = [c for c in cols if c not in KEEP_COLS and (c in FORCE_DROP.get(name, set())
                or (len(rows) > MAX_TEXT_ROWS and is_seq_col(rows, c)))]
        keep = [c for c in cols if c not in drop]
        with open(OPEN / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keep, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        man.append(dict(file=name, rows=len(rows), columns=len(keep), description=desc, made_by=src,
                        sign_text_columns_removed=";".join(drop)))
    with open(OPEN / "MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys())); w.writeheader(); w.writerows(man)
    return man


def archive_items():
    """Every archive.org item the project downloaded from, found by folder name or SOURCE.json."""
    items = {}
    for d in sorted((ROOT / "experiments").glob("*/raw/**/")):
        sj = d / "SOURCE.json"
        ident = title = None
        if sj.exists():
            try:
                j = json.load(open(sj)); ident, title = j.get("identifier"), j.get("title")
            except Exception:
                pass
        elif re.match(r"^(in\.ernet\.dli\.|in\.gov\.ignca\.|dli\.|[a-z0-9]{20,}_\d+_[A-Za-z]$|mohenjodaro|BK00|xSFp_|OLMh)", d.name):
            ident = d.name
        if ident and not ident.startswith("v2"):
            e = items.setdefault(ident, dict(title=title or "", used_in=set()))
            e["title"] = e["title"] or title or ""
            e["used_in"].add(d.relative_to(ROOT).parts[1])
    return items


ALIASES = {"OLMh": "OLMh_mohenjo-daro-and-the-indus-civilization-edited-by-sir-john-marshall-vol.-2-1931-"}


def build_catalog(man):
    rows = []
    for s in SOURCES:
        rows.append(dict(s, included_here=""))
    meta = json.load(open(OUT / "archive_titles.json")) if (OUT / "archive_titles.json").exists() else {}
    for ident, e in sorted(archive_items().items()):
        if ident in ("cisi_vol1", "cisi_vol2"):
            continue
        local_name = ident
        ident = ALIASES.get(ident, ident)
        m = meta.get(local_name, {})
        if m and not m.get("exists", True) and local_name not in ALIASES:
            continue        # not an archive.org item (a folder name that only looks like one)
        title = m.get("title") or e["title"] or ident
        date = m.get("date", "")
        if m.get("creator") and m.get("creator") not in title:
            title += f" ({m['creator']}{', ' + date if date else ''})"
        reprint = date[:4].isdigit() and int(date[:4]) > 1945
        terms = ("Later reprint or edition scan: check its own terms" if reprint else
                 "1931-1943 reports: public domain in India; US status uncertain (LICENSING.md)")
        rows.append(dict(id="archive:" + ident, title=title, kind="excavation report / book scan", tier="fetch",
                         origin=f"https://archive.org/details/{ident}", terms=terms,
                         local="experiments/{" + ",".join(sorted(e["used_in"])) + "}/raw/" + local_name, fetch="reports", included_here=""))
    for m in man:
        rows.append(dict(id="open:" + m["file"][:-4], title=m["description"], kind="project table", tier="included",
                         origin="this project (" + m["made_by"] + ")", terms="CC BY 4.0", local="datasets/open/" + m["file"],
                         fetch="", included_here=f"{m['rows']} rows"))
    with open(OUT / "catalog.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "title", "kind", "tier", "origin", "terms", "local", "fetch", "included_here"])
        w.writeheader(); w.writerows(rows)
    return rows


if __name__ == "__main__":
    man = build_open()
    rows = build_catalog(man)
    from collections import Counter
    print(len(man), "open tables;", len(rows), "catalogue rows;", Counter(r["tier"] for r in rows))
    for m in man:
        if m["sign_text_columns_removed"]:
            print("  removed", m["file"], m["sign_text_columns_removed"])
