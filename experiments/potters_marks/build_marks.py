"""Build marks.csv: Early Harappan / pre-Mature potter's marks and graffiti with vessel type and M77 match.

Run: .venv/bin/python experiments/potters_marks/build_marks.py

Every M77 match is a shape judgement from the published drawing against Mahadevan's sign drawings
(data/sign_images), made by this study unless match_basis says otherwise:
  author  = the excavator/author names the Mahadevan sign himself (Kenoyer 2020)
  icit    = Wells/ICIT transcription mapped through the Wells-Mahadevan bridge
  study   = this study (single pass, drawings only)
Confidence: A = same shape, no plausible alternative; B = same shape, one alternative or orientation
unknown; C = loose resemblance. '-' = no M77 sign of that shape.
Vessel class is coded only from what the publication says for that mark (jar / bowl / lid /
unknown). Nothing is inferred from ware alone.
"""
import csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

COLS = ["mark_id", "source", "site", "phase", "approx_bce", "shape", "firing", "vessel_type_published",
        "vessel_class", "vessel_part", "n_marks", "m77_match", "match_conf", "match_basis", "wells",
        "early", "notes", "citation"]

CIT = {
    "K06": "Kenoyer, J.M. (n.d., c. 2006/2019) The origin, context and function of the Indus script: recent insights from Harappa. Mohen Jo Daro journal 1: 136-158, Figs 3-4 (same drawings as Kenoyer 2020 Fig. 5). https://mohenjodarorj.sindhila.org/index.php/journal/article/download/105/81",
    "K20": "Kenoyer, J.M. 2020. Origin and development of the Indus script: insights from Harappa and other sites. In Proc. Int. Conf. Mohenjo-daro, pp. 217-234 (Tables 3-4, Figs 3-6). harappa.com PDF (Wayback copy 2026-01-05)",
    "H72": "Halim, M.A. 1972. The pottery of Periods IA and II with incised potter's or graffiti marks. In Excavations at Sarai Khola Part II, Pakistan Archaeology 8: 95-99, Table 11 and catalogue. archive.org in.gov.ignca.69948",
    "K65": "Khan, F.A. 1965. Excavations at Kot Diji. Pakistan Archaeology 2: 11-85, pl. XXIV (via paragorth loop57 transcription)",
    "Q80": "Quivron, G. 1980. Les marques incisees sur les poteries de Mehrgarh au Baluchistan. Paleorient 6: 269-280, Tableau 4 (category counts as transcribed by paragorth loop57; text read from Persee page images)",
    "D74": "Dales, G.F. 1974. Excavations at Balakot, Pakistan, 1973. J. Field Archaeology 1: 3-22, Fig. 11 (as reproduced in Kenoyer 2020 Fig. 4)",
    "ICIT": "Wells/Fuls ICIT (data/icit_texts.jsonl), pottery and tag rows dated pre-Mature",
}

rows = []


def add(**kw):
    r = {c: "" for c in COLS}
    r.update(kw)
    r.setdefault("n_marks", 1)
    rows.append(r)


# ---------------------------------------------------------------- Harappa, Kenoyer figures (selection, not census)
K = dict(source="K06", site="Harappa", vessel_type_published="not recorded per mark", vessel_class="unknown",
         citation=CIT["K06"], early="yes")
rav = dict(phase="Period 1 Ravi", approx_bce="3700-2800")
kd = dict(phase="Period 2 Kot Diji", approx_bce="2800-2600")
# Ravi post-firing (6 of 13 inscribed sherds are rims, text p.144)
add(mark_id="hR-g1", **K, **rav, firing="post", shape="three branching tree/forked signs in a row (Fig3:1)", m77_match="M162|M161", match_conf="C", match_basis="study", wells="411-411-411 (ICIT H-1522)", notes="Kenoyer: anthropomorphic image or complex plant; ICIT transcribes as W411 x3 (no M77 equivalent in bridge)")
add(mark_id="hR-g2", **K, **rav, firing="post", shape="partial curved strokes with hatches (Fig3:2)", m77_match="M342", match_conf="C", match_basis="author", notes="Kenoyer 2006: 'partially preserved sign that looks like it might be ancestral to the most common symbol in the later Indus script'; Kenoyer 2020 Fig 6a calls the Ravi sherd M342")
add(mark_id="hR-g3", **K, **rav, firing="post", shape="circle quartered by a cross (wheel)", m77_match="-", match_conf="", match_basis="study", notes="intersecting-circle motif also painted")
add(mark_id="hR-g4", **K, **rav, firing="post", shape="V with central stroke (psi without stem)", m77_match="M162|M336", match_conf="C", match_basis="study")
add(mark_id="hR-g5", **K, **rav, firing="post", shape="fan of five strokes from one point", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hR-g6", **K, **rav, firing="post", shape="X with extra stroke", m77_match="M137", match_conf="C", match_basis="study")
add(mark_id="hR-g7", **K, **rav, firing="post", shape="asterisk (X with vertical)", m77_match="M141", match_conf="B", match_basis="study")
add(mark_id="hR-g8", **K, **rav, firing="post", shape="one oblique stroke", m77_match="M86|M97", match_conf="C", match_basis="study")
add(mark_id="hR-g9", **K, **rav, firing="post", shape="one vertical stroke", m77_match="M86|M97", match_conf="B", match_basis="study", notes="height class unknown")
add(mark_id="hR-g10", **K, **rav, firing="post", shape="two vertical strokes", m77_match="M87|M99", match_conf="B", match_basis="study", notes="tall 2 vs short 2 (connective) not separable")
add(mark_id="hR-p1", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="horizontal stroke ending in an arc", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hR-p2", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="V", m77_match="M365|M328", match_conf="C", match_basis="study", notes="ICIT/Wells would code W700=M328")
add(mark_id="hR-p3", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="V with central stroke", m77_match="M162|M336", match_conf="C", match_basis="study")
add(mark_id="hR-p4", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="X", m77_match="M137", match_conf="A", match_basis="study")
add(mark_id="hR-p5", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="plus (+)", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hR-p6", **K, **rav, firing="pre", vessel_part="base or lower body (general statement)", shape="two vertical strokes", m77_match="M87|M99", match_conf="B", match_basis="study")
# Kot Diji post-firing
add(mark_id="hK-g1", **K, **kd, firing="post", shape="U with forked (Y) tips on both arms (Fig4:1)", m77_match="M347", match_conf="B", match_basis="study", notes="Kenoyer 2020 names M347 (and M342) among Period 2 graffiti; paragorth coded W706")
add(mark_id="hK-g2", **K, **kd, firing="post", shape="V with forked tips (Fig4:2)", m77_match="M347", match_conf="B", match_basis="study")
add(mark_id="hK-g3", **K, **kd, firing="post", shape="forked V between two arcs (Fig4:3)", m77_match="M347", match_conf="C", match_basis="study", notes="brackets resemble M287/M303 enclosures")
add(mark_id="hK-g4", **K, **kd, firing="post", shape="jar-like U with hooked arms + U with forked tips (Fig4:4)", m77_match="M342-M347", match_conf="B", match_basis="author", notes="Kenoyer 2020: M342 'combined with another sign (M347) in a sequence that also appears in later Indus seals'")
add(mark_id="hK-g5", **K, **kd, firing="post", shape="stroke + dotted arch (Fig4:5)", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g6", **K, **kd, firing="post", shape="stroke + two cups with a crossbar (Fig4:6)", m77_match="M97-M328-M328", match_conf="C", match_basis="study", notes="paragorth: bowtie W540")
add(mark_id="hK-g7", **K, **kd, firing="post", shape="short stroke + V + V (Fig4:7)", m77_match="M97-M365-M365", match_conf="C", match_basis="study")
add(mark_id="hK-g8", **K, **kd, firing="post", shape="arrow-like caret + tick (Fig4:8)", m77_match="M153", match_conf="C", match_basis="study")
add(mark_id="hK-g9", **K, **kd, firing="post", shape="three strokes + zigzag M (Fig4:9)", m77_match="M89-M132", match_conf="C", match_basis="study")
add(mark_id="hK-g10", **K, **kd, firing="post", shape="stroke + three inverted V (Fig4:10)", m77_match="M86-M134-M134-M134", match_conf="C", match_basis="study")
add(mark_id="hK-g11", **K, **kd, firing="post", shape="V with central stroke (x3 drawings)", n_marks=3, m77_match="M162|M336", match_conf="C", match_basis="study")
add(mark_id="hK-g12", **K, **kd, firing="post", shape="fan of strokes", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g13", **K, **kd, firing="post", shape="stroke with two crossbars", m77_match="M177", match_conf="C", match_basis="study")
add(mark_id="hK-g14", **K, **kd, firing="post", shape="asterisk", m77_match="M141", match_conf="B", match_basis="study")
add(mark_id="hK-g15", **K, **kd, firing="post", shape="one oblique stroke", m77_match="M86|M97", match_conf="C", match_basis="study")
add(mark_id="hK-g16", **K, **kd, firing="post", shape="one vertical stroke", m77_match="M86|M97", match_conf="B", match_basis="study")
add(mark_id="hK-g17", **K, **kd, firing="post", shape="two vertical strokes", m77_match="M87|M99", match_conf="B", match_basis="study")
add(mark_id="hK-g18", **K, **kd, firing="post", shape="inverted V (chevron)", m77_match="M134", match_conf="B", match_basis="study")
add(mark_id="hK-g19", **K, **kd, firing="post", shape="hash # (x2)", n_marks=2, m77_match="-", match_conf="", match_basis="study", notes="closest boxed grid M245 (C)")
add(mark_id="hK-g20", **K, **kd, firing="post", shape="vertical with four teeth on one side (comb, E)", m77_match="M176|M177", match_conf="B", match_basis="study", notes="ICIT Harappa P2 has W413=M177 (440.1)")
add(mark_id="hK-g21", **K, **kd, firing="post", shape="angular hook", m77_match="M127", match_conf="C", match_basis="study")
add(mark_id="hK-g22", **K, **kd, firing="post", shape="N", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g23", **K, **kd, firing="post", shape="hooked square / bracket + crossed oval + stroke", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g24", **K, **kd, firing="post", shape="stroke + X", m77_match="M86-M137", match_conf="B", match_basis="study")
add(mark_id="hK-g25", **K, **kd, firing="post", shape="bowtie (hourglass on side)", m77_match="M214", match_conf="B", match_basis="study")
add(mark_id="hK-g26", **K, **kd, firing="post", shape="square with diagonal cross", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g27", **K, **kd, firing="post", shape="feather / curved fan", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g28", **K, **kd, firing="post", shape="ladder (two verticals, two rungs)", m77_match="M186|M245", match_conf="C", match_basis="study")
add(mark_id="hK-g29", **K, **kd, firing="post", shape="rayed dotted circle (sun)", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-g30", **K, **kd, firing="post", shape="crossed triangle on stem", m77_match="-", match_conf="", match_basis="study")
# Kot Diji pre-firing (some inscribed in moulds for large bowls or jars: Fig4:11-12)
pre = dict(firing="pre", vessel_part="base or lower body (general statement)")
add(mark_id="hK-p1", **K, **kd, **pre, shape="three oblique strokes + comb/fan (Fig4:11; mould mark for large bowl/jar)", m77_match="M102", match_conf="C", match_basis="study", notes="text: multi-sign pre-firing marks inscribed into moulds used to make large bowls or jars")
add(mark_id="hK-p2", **K, **kd, **pre, shape="stroke + figure-8 + branched mark (Fig4:12; mould mark)", m77_match="M97-M410", match_conf="C", match_basis="study")
add(mark_id="hK-p3", **K, **kd, **pre, shape="arc with inner cross (Fig4:13)", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-p4", **K, **kd, **pre, shape="I-beam", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-p5", **K, **kd, **pre, shape=")( two arcs back to back", m77_match="M303", match_conf="B", match_basis="study")
add(mark_id="hK-p6", **K, **kd, **pre, shape="multi-crossed X", m77_match="M140", match_conf="C", match_basis="study")
add(mark_id="hK-p7", **K, **kd, **pre, shape="asterisk", m77_match="M141", match_conf="B", match_basis="study")
add(mark_id="hK-p8", **K, **kd, **pre, shape="X", m77_match="M137", match_conf="A", match_basis="study")
add(mark_id="hK-p9", **K, **kd, **pre, shape="three vertical strokes", m77_match="M89|M102", match_conf="B", match_basis="study")
add(mark_id="hK-p10", **K, **kd, **pre, shape="two vertical strokes", m77_match="M87|M99", match_conf="B", match_basis="study")
add(mark_id="hK-p11", **K, **kd, **pre, shape="one vertical stroke", m77_match="M86|M97", match_conf="B", match_basis="study")
add(mark_id="hK-p12", **K, **kd, **pre, shape="two arcs crossing (bird/curved X)", m77_match="-", match_conf="", match_basis="study")
add(mark_id="hK-p13", **K, **kd, **pre, shape="shallow curved V; V + small v", n_marks=2, m77_match="M365", match_conf="C", match_basis="study")
add(mark_id="hK-p14", **K, **kd, **pre, shape="double arc ))", m77_match="M294", match_conf="B", match_basis="study")
add(mark_id="hK-p15", **K, **kd, **pre, shape="three oblique strokes", m77_match="M89|M102", match_conf="C", match_basis="study")

# ---------------------------------------------------------------- Kenoyer 2020: author-named M342 attestations
add(mark_id="k20-6a", source="K20", site="Harappa", phase="Period 1 Ravi", approx_bce="3700-2800", firing="post", shape="sherd H98/8440-202 with graffiti", vessel_type_published="not stated", vessel_class="unknown", m77_match="M342", match_conf="B", match_basis="author", early="yes", notes="Kenoyer 2020 Fig 6a: the sign that later becomes M342; photo is ambiguous at web resolution", citation=CIT["K20"])
add(mark_id="k20-6b", source="K20", site="Harappa", phase="Period 2 Kot Diji", approx_bce="2800-2600", firing="post", shape="sherd H99-4367/8946-37 with graffiti", vessel_type_published="not stated", vessel_class="unknown", m77_match="M342", match_conf="B", match_basis="author", early="yes", notes="Kenoyer 2020 Fig 6b", citation=CIT["K20"])
add(mark_id="k20-kal", source="K20", site="Kalibangan", phase="lower levels (Early Harappan?)", approx_bce="2900-2600?", firing="unknown", shape="single jar sign on 3 sherds", n_marks=3, vessel_type_published="not stated", vessel_class="unknown", m77_match="M342", match_conf="B", match_basis="author", early="doubtful", notes="Lal 1979: 33; not in Lal et al. 2003 Early Harappan report, so Kenoyer says they may be Mature", citation=CIT["K20"] + "; Lal, B.B. 1979 (cited p. 33)")
add(mark_id="k20-bal", source="K20", site="Balakot", phase="Period I", approx_bce="3500-2800", firing="unknown", shape="jar sign among Period I graffiti", n_marks="unknown", vessel_type_published="not stated", vessel_class="unknown", m77_match="M342", match_conf="B", match_basis="author", early="yes", notes="Franke-Vogt 2001 dissertation (not seen): 'the most important sign is M342'", citation=CIT["K20"] + "; Franke-Vogt, U. 2001 (dissertation, cited)")

# ---------------------------------------------------------------- Sarai Khola (Halim 1972): vessel type per mark
S = dict(source="H72", site="Sarai Khola", citation=CIT["H72"], early="yes")
# cat no: (shape, period, firing, published vessel, class, part, n, m77, conf, extra occurrences [(class, n, note)])
SK = [
    (1, "one short stroke", "II", "pre", "Type IX (Kot Dijian short-necked globular jar)", "jar", "shoulder", 1, "M86|M97", "B", [("unknown", 2, "+2 sherds, type not given")]),
    (2, "two strokes", "II", "pre", "Type IXA (Kot Dijian jar)", "jar", "shoulder", 1, "M87|M99", "B", [("jar", 1, "+1 sherd Type IXC"), ("unknown", 2, "+2 sherds")]),
    (3, "three strokes", "II", "pre", "Type X (bowl, convex sides)", "bowl", "near base", 1, "M89|M102", "B", [("jar", 1, "+1 sherd Type IX"), ("unknown", 1, "+1 sherd")]),
    (4, "two strokes offset", "surface", "pre", "red ware, disc base", "unknown", "near base", 1, "M87|M99", "C", []),
    (5, "three strokes scattered", "surface", "pre", "fragment, base", "unknown", "base", 1, "M89|M102", "C", [("unknown", 1, "+1 sherd")]),
    (6, "four strokes scattered", "II", "pre", "Type VII (grooved globular jar)", "jar", "near base", 1, "M95|M104", "C", []),
    (7, "cross (+)", "III", "pre", "Type X bowl", "bowl", "near base", 1, "-", "", [("bowl", 1, "+1 sherd Type X"), ("unknown", 2, "+2 sherds")]),
    (8, "inverted T", "II", "pre", "Type XIA (carinated bowl)", "bowl", "near base", 1, "-", "", [("unknown", 1, "+1 sherd")]),
    (9, "T", "?", "unknown", "red ware fragment", "unknown", "base", 1, "-", "", []),
    (10, "flat-based U (cup with two verticals)", "?", "pre", "red ware, buff and red slip, painted", "unknown", "", 1, "M328", "B", []),
    (11, "two tall verticals joined by a long bar (H)", "?", "pre", "Type IXB (Kot Dijian jar)", "jar", "", 1, "-", "", []),
    (12, "one oblique stroke", "?", "pre", "Type IX (Kot Dijian jar)", "jar", "", 1, "M86|M97", "C", []),
    (13, "inverted V (chevron)", "?", "pre", "Type X bowl; similar marks on Fig 18 No 101 (IXA), Fig 19 (IXB), Fig 22 No 140 (IXE)", "bowl", "near base", 1, "M134", "B", [("jar", 3, "Halim: similar marks on Types IXA, IXB, IXE (jars)")]),
    (14, "chevron with hatched arm", "IA", "pre", "red ware, wash", "unknown", "near base", 1, "M134", "C", []),
    (15, "cluster of short strokes under dotted arc", "II", "pre", "red ware, flat base", "unknown", "near base", 1, "-", "", []),
    (16, "three-armed star (inverted Y)", "II", "unknown", "Type X bowl", "bowl", "near base", 1, "M126|M161", "C", []),
    (17, "arrow (stem with barbed head)", "II", "post", "Type VII (grooved globular jar)", "jar", "shoulder", 1, "M153", "C", [("unknown", 1, "+1 surface sherd, pre-firing")]),
    (18, "W (two V)", "II", "unknown", "Type IXB (Kot Dijian jar)", "jar", "shoulder", 1, "M132", "C", []),
    (19, "W, asymmetric", "II", "unknown", "Type VII (grooved globular jar)", "jar", "near base", 1, "M132", "C", [("unknown", 1, "+1 surface sherd")]),
    (20, "V", "?", "unknown", "red ware, wash", "unknown", "near base", 1, "M365|M328", "C", [("lid", 1, "one of 4 further sherds is Fig 26 No 175 = Type XIIIA painted knobbed lid (read from OCR 'Fig. 16, No. 175')"), ("unknown", 3, "+3 sherds")]),
    (21, "Y", "?", "unknown", "Type IXA (Kot Dijian jar)", "jar", "shoulder", 1, "M161", "B", []),
    (22, "V with inner stroke", "II", "unknown", "Type XIA (carinated bowl)", "bowl", "near base", 1, "M162|M336", "C", [("unknown", 1, "+1 sherd")]),
    (23, "N (zigzag of three strokes)", "II", "unknown", "red ware", "unknown", "", 1, "-", "", [("unknown", 1, "+1 sherd")]),
    (24, "V with dotted arm (W?)", "II", "unknown", "Type X bowl", "bowl", "external surface", 1, "M365|M132", "C", []),
    (25, "V, open", "II", "unknown", "Type X bowl", "bowl", "near base", 1, "M365|M328", "C", []),
    (26, "V with two inner strokes (fan)", "II", "unknown", "Type IXE (painted Kot Dijian jar)", "jar", "shoulder", 1, "-", "", []),
    (27, "W (zigzag)", "IA", "unknown", "Type IXA (Kot Dijian jar)", "jar", "shoulder", 1, "M132", "C", []),
    (28, "N", "II", "unknown", "Type IXA (Kot Dijian jar)", "jar", "shoulder", 1, "-", "", []),
    (29, "two oblique strokes", "II", "unknown", "Type X bowl", "bowl", "near base", 1, "M87|M99", "C", [("unknown", 1, "+1 sherd")]),
    (30, "W with long arms", "II", "pre", "red ware, flat base", "unknown", "near base", 1, "M132", "C", []),
    (31, "W with short arms", "II", "unknown", "bowl, red ware", "bowl", "external surface", 1, "M132", "C", []),
    (32, "two strokes, one tall one short", "II", "unknown", "bowl", "bowl", "near base", 1, "M87|M99", "C", []),
    (33, "short oblique + tall stroke", "II", "pre", "bowl, red ware, flat base", "bowl", "near base", 1, "M87|M99", "C", []),
    (34, "stroke with branches on one side (half tree)", "II", "unknown", "red ware", "unknown", "external surface", 1, "M169", "C", []),
    (35, "two strokes crossing", "II", "unknown", "red ware, flat base", "unknown", "near base", 1, "-", "", []),
    (36, "E-shaped wiggle", "II", "unknown", "red ware, flat base", "unknown", "near base", 1, "-", "", []),
    (37, "single wave", "?", "unknown", "Type IXA (Kot Dijian jar)", "jar", "", 1, "-", "", []),
    (38, "double wave", "II", "unknown", "red ware, flat disc base", "unknown", "near base", 1, "-", "", []),
    (39, "double spiral with central strokes", "II", "unknown", "red ware, flat base", "unknown", "near base", 1, "-", "", []),
    (40, "one stroke; two strokes (two marks)", "?", "post", "Type VII (grooved globular jar), Fig 12 No 49", "jar", "shoulder and rim", 1, "M86|M97", "C", []),
]
for (no, shape, per, fir, vt, vc, part, n, m, conf, extra) in SK:
    add(mark_id=f"sk{no:02d}", **S, phase=f"Sarai Khola {per}", approx_bce="2900-2500", shape=shape, firing=fir,
        vessel_type_published=vt, vessel_class=vc, vessel_part=part, n_marks=n, m77_match=m, match_conf=conf,
        match_basis="study", notes=f"Halim cat. {no}; shapes checked against Table 11 page image")
    for j, (c2, n2, note) in enumerate(extra):
        add(mark_id=f"sk{no:02d}x{j+1}", **S, phase=f"Sarai Khola {per}", approx_bce="2900-2500", shape=shape, firing=fir,
            vessel_type_published=note, vessel_class=c2, vessel_part="", n_marks=n2, m77_match=m, match_conf=conf,
            match_basis="study", notes=f"Halim cat. {no}, additional sherds with the same mark")

# ---------------------------------------------------------------- Kot Diji (Khan 1965)
add(mark_id="kd-2", source="K65", site="Kot Diji", phase="Kot Diji levels", approx_bce="2800-2600", firing="unknown", shape="inverted V (chevron)", vessel_type_published="rimless jar", vessel_class="jar", m77_match="M134", match_conf="B", match_basis="study", early="yes", notes="Halim's parallel for Sarai Khola 13", citation=CIT["K65"])
add(mark_id="kd-3", source="K65", site="Kot Diji", phase="Kot Diji levels", approx_bce="2800-2600", firing="unknown", shape="X beside a vertical", vessel_type_published="not stated", vessel_class="unknown", m77_match="M86-M137", match_conf="C", match_basis="study", early="yes", citation=CIT["K65"])

# ---------------------------------------------------------------- Mehrgarh (Quivron 1980): category totals, periods IV-VII
Q = [  # (cat, shape, n, m77, conf)
    ("q01", "one vertical stroke", 25, "M86|M97", "B"), ("q02", "one horizontal stroke", 22, "-", ""),
    ("q03", "two vertical strokes", 68, "M87|M99", "B"), ("q04", "two horizontal strokes", 6, "-", ""),
    ("q05", "stroke with short tick at top", 1, "-", ""), ("q06", "stroke with two bars at top", 1, "-", ""),
    ("q07", "three vertical strokes", 119, "M89|M102", "B"), ("q08", "three strokes converging at base", 27, "-", ""),
    ("q09", "four vertical strokes", 16, "M95|M104", "B"), ("q10", "six vertical strokes", 1, "M110|M109", "C"),
    ("q11", "stroke with top bar and side bars", 1, "-", ""), ("q12", "stroke with many short hatches", 1, "M177", "C"),
    ("q13", "one arc", 49, "M287", "B"), ("q14", "two nested arcs", 61, "M294", "B"),
    ("q15", "three nested arcs", 23, "M298", "C"), ("q16", "four nested arcs", 12, "M298", "C"),
    ("q17", "single wavy line", 21, "-", ""), ("q18", "three stacked wavy lines", 4, "-", ""),
    ("q19", "X with curved arms", 16, "M137", "C"), ("q20", "curved X with central bar", 2, "-", ""),
    ("q21", "lens / eye (bow over bow)", 3, "M373", "C"), ("q22", "curve with upward tail", 41, "-", ""),
    ("q23", "double flourish curve", 1, "-", ""), ("q24", "wave with arc", 1, "-", ""), ("q25", "wave with two arcs", 1, "-", ""),
    ("q26", "stem with three branches each side (tree)", 1, "M168|M167", "C"), ("q27", "T", 22, "-", ""),
    ("q28", "arch with one inner stroke", 64, "-", ""), ("q29", "arch with three inner strokes", 17, "-", ""),
    ("q30", "V", 37, "M365|M328", "C"), ("q31", "V with tail", 68, "-", ""),
    ("q32", "V with inner stroke", 5, "M162|M336", "C"), ("q33", "y (V on a stem)", 3, "M161", "B"),
    ("q34", "stroke + V", 22, "M86-M365", "C"), ("q35", "stroke + N", 1, "-", ""),
    ("q36", "W (double V)", 7, "M132", "C"), ("q37", "VIV", 1, "-", ""), ("q38", "zigzag line", 1, "M132", "C"),
    ("q39", "X", 61, "M137", "A"), ("q40", "X with vertical through it", 1, "M141", "B"),
    ("q41", "double X side by side", 7, "M137-M137", "C"), ("q42", "X with central vertical (star)", 1, "M141", "B"),
    ("q43", "X with horizontal bar", 4, "-", ""), ("q44", "lens crossed by diagonal", 3, "-", ""),
    ("q45", "bowtie", 2, "M214", "B"), ("q46", "double bowtie", 1, "M215|M217", "C"),
    ("q47", "grid (hash in a box)", 1, "M245", "B"), ("q48", "rectangle with diagonals", 1, "-", ""),
    ("q49", "circle", 1, "-", ""), ("q50", "dotted circle", 1, "-", ""), ("q51", "hook / spiral", 1, "-", ""),
]
for cat, shape, n, m, conf in Q:
    add(mark_id=f"mr-{cat}", source="Q80", site="Mehrgarh", phase="MR IV-VII", approx_bce="3500-2500", firing="pre",
        shape=shape, vessel_type_published="not recorded per mark; Quivron: same marks indifferently on goblets, small cups and jars",
        vessel_class="unknown", vessel_part="80% outer base, 18% body", n_marks=n, m77_match=m, match_conf=conf,
        match_basis="study", early="yes", notes="category total over periods IV-VII from paragorth transcription of Tableau 4", citation=CIT["Q80"])

# ---------------------------------------------------------------- Balakot Period I (Dales 1974 Fig 11, via Kenoyer 2020 Fig 4)
B = dict(source="D74", site="Balakot", phase="Period I", approx_bce="3500-2800", firing="unknown (marks, graffiti and painted motifs not separated in the figure)",
         vessel_type_published="not stated in the reproduced figure", vessel_class="unknown", early="yes", citation=CIT["D74"], match_basis="study")
for mid, shape, m, conf in [
    ("b01", "X (painted?)", "M137", "A"), ("b02", "triangle over T", "-", ""), ("b05", "flag (vertical with top bar and short bar)", "M170|M127", "C"),
    ("b06", "vertical with top and bottom bars", "-", ""), ("b07", "X with side stroke", "-", ""),
    ("b09", "comb: vertical with four teeth on a base", "M176", "C"), ("b10", "Y with hooked arm", "M161", "C"),
    ("b11", "crossed strokes (X with bar)", "M137", "C"), ("b12", "crossed strokes", "M137", "C"), ("b13", "X in corner", "M137", "C"),
    ("b14", "two crossed jar-like forks with comb tips", "M347", "C"), ("b15", "X with top bar", "M139", "B"),
    ("b16", "vertical with two crossbars", "M177", "C"), ("b19", "fan of strokes (painted)", "-", ""),
    ("b20", "triangle with inner stroke", "-", ""), ("b21", "arrow in triangle over crossed stem", "M211", "C"),
    ("b24", "Y on stem with bar", "M161", "C"), ("b28", "branch with many arms (painted tree)", "M168", "C"),
]:
    add(mark_id=f"bk-{mid}", **B, shape=shape, m77_match=m, match_conf=conf)

# ---------------------------------------------------------------- ICIT pre-Mature pottery (external transcription)
bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))


def early_icit(r):
    s, p = r["site"], r["period"]
    if s == "Harappa" and p in ("1", "2"): return "yes"
    if s == "Harappa" and p == "2/3": return "transitional"
    if s == "Kalibangan" and p == "1": return "yes"
    if s == "Kot-Diji" and p == "1": return "yes"
    if s == "Nausharo" and p == "2": return "transitional"
    return None


for l in open(ROOT / "data/icit_texts.jsonl"):
    r = json.loads(l)
    e = early_icit(r)
    if not e or not (r["type"].startswith("PO") or r["type"].startswith("TAG")):
        continue
    ms = []
    for w in r["seq"]:
        if not w.startswith("W"):
            continue  # '#' break and '|' line break are not signs
        k = w[1:].lstrip("0")
        ms.append("|".join(f"M{m}" for m in bridge[k]["M"]) if k in bridge else "?")
    fir = {"POT:T:g": "post", "POT:T:p": "pre"}.get(r["type"], "unknown")
    add(mark_id=f"icit-{r['id']}", source="ICIT", site=r["site"], phase=f"{r['period']} {r['phase']}".strip(" -"), approx_bce="",
        firing=fir, shape="ICIT " + " ".join(r["seq"]), vessel_type_published="not recorded in ICIT",
        vessel_class="unknown", m77_match="-".join(ms),
        match_conf="B", match_basis="icit", wells=" ".join(r["seq"]), early=e,
        notes=f"ICIT type {r['type']}, CISI {r['cisi']}; may duplicate a Kenoyer figure mark", citation=CIT["ICIT"])

with open(HERE / "marks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows;", sum(int(r["n_marks"]) for r in rows if str(r["n_marks"]).isdigit()), "marks")
