#!/usr/bin/env python3
"""Builds Open Indus Display.

Capitals, digits and our punctuation: stroke skeletons in glyphs.py, expanded
to outlines (shapely buffer with round caps and joins, slightly elliptical pen
so horizontals are a touch thinner than verticals), unioned per glyph.

Lowercase a-z, accented lowercase, curly quotes and the symbols we never drew:
taken unchanged from Instrument Sans (SIL OFL 1.1), instanced from
raw/instrumentsans/InstrumentSans-VF.ttf, with its kerning for every pair that
involves a borrowed glyph. Accented capitals = our capital + an Instrument Sans
accent. Instrument Sans keeps its 1000-unit em and 720 cap height; our capitals'
ink is sized to that cap height.

Writes OpenIndus-Regular/Bold .ttf + .woff2 next to this file.

Also builds the second cut, Open Indus Text (OpenIndusText-Regular/Bold): the
same font with Instrument Sans's own capitals, figures and & / ( ) in place of
our drawn ones, for sentences and interface labels. See TEXT_* below.
Run from the project root:  .venv/bin/python -I site/font/build_font.py
"""
import importlib.util
import os
import re

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampNow
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("glyphs", os.path.join(HERE, "glyphs.py"))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

FAMILY = "Open Indus Display"     # the one place the family name lives (no reserved font names)
PS_FAMILY = FAMILY.replace(" ", "")
FILE_STEM = "OpenIndus"
FAMILY_TEXT = "Open Indus Text"   # mixed-case cut: Instrument Sans capitals and figures, our spacing
FILE_STEM_TEXT = "OpenIndusText"
VERSION = "0.7"
COPYRIGHT_TEXT = ("Spacing and build: Copyright 2026 The Open Indus project. Outlines: "
                  "Copyright 2022 The Instrument Sans Project Authors (https://github.com/Instrument/instrument-sans).")
COPYRIGHT = ("Capitals, figures, & / ( ): Copyright 2026 The Open Indus project. Lowercase, punctuation and symbols: "
             "Copyright 2022 The Instrument Sans Project Authors (https://github.com/Instrument/instrument-sans).")
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
LICENSE_URL = "https://openfontlicense.org"

SOURCE = os.path.join(HERE, "raw", "instrumentsans", "InstrumentSans-VF.ttf")
# Instance per style. wdth 90 pulls it a little toward our narrow capitals while
# keeping the ordinary text look; stems are about 75 (Regular) and 133 (Bold) units.
SOURCE_AXES = {"Regular": {"wght": 400, "wdth": 100}, "Bold": {"wght": 650, "wdth": 100}}
# Body-size spacing: every borrowed glyph (lowercase, punctuation, symbols) gets
# this many extra units of advance, split evenly left and right, and the word
# space grows by the same amount. Large mixed-case settings tighten it in CSS.
BODY_TRACK = 12
HALF = BODY_TRACK // 2
LOWER = list("abcdefghijklmnopqrstuvwxyz")
# Everything else borrowed as is (characters our skeletons do not cover).
BORROW = ("ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿıœāēīōūś"
          ".,:;!?'\"-–"
          "%+_·×→←↑↓@#$*<=>[]\\^`{|}~—…‘’“”•€£©®°")
ACCENTED_CAPS = "ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝĀĒĪŌŪŚ"
# Text cut: these come from Instrument Sans too (in Display they are ours).
TEXT_EXTRA = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&/()") + list(ACCENTED_CAPS)
# Optional trace of the display O in the Text cut: lift the top and drop the
# bottom of O / Q / 0 by this many units at the centre, fading to nothing at the
# sides, so the round letter gets a very slight point. 0 = Instrument's shape.
TEXT_POINT = 0
TEXT_POINT_GLYPHS = ("O", "Q", "zero")

UPM = 1000
CAP_INK = 720                       # Instrument Sans cap height; our capitals' ink fills exactly this
S = CAP_INK / (100 + G.STROKE)      # font units per grid unit (horizontal and pen width)


def parse(d):
    """Absolute M L H V C Z -> list of (points, closed) polylines; lone M = dot."""
    toks = re.findall(r"[MLHVCZ]|-?\d*\.?\d+", d)
    subs, cur, pos, start, cmd, i = [], None, (0.0, 0.0), (0.0, 0.0), None, 0

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                if cur is not None:
                    cur[1] = True
                    pos = start
                continue
        if cmd == "M":
            cur = [[], False]
            subs.append(cur)
            pos = start = (num(), num())
            cur[0].append(pos)
            cmd = "L"
        elif cmd == "L":
            pos = (num(), num())
            cur[0].append(pos)
        elif cmd == "H":
            pos = (num(), pos[1])
            cur[0].append(pos)
        elif cmd == "V":
            pos = (pos[0], num())
            cur[0].append(pos)
        elif cmd == "C":
            p1, p2, p3 = (num(), num()), (num(), num()), (num(), num())
            p0 = pos
            n = 28
            for k in range(1, n + 1):
                t = k / n
                a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                cur[0].append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0],
                               a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
            pos = p3
        else:
            raise ValueError(f"bad command {cmd} in {d}")
    return [(pts, closed) for pts, closed in subs]


def skeleton(name):
    left, right, paths = G.GLYPHS[name]
    subs = [(s, p.startswith("~")) for p in paths for s in parse(p.lstrip("~"))]
    fine = [f for _, f in subs]
    subs = [s for s, _ in subs]
    os_mode = G.OVERSHOOT.get(name, "")
    k = 1 + G.OVERSHOOT_AMT / 50

    def ov(y):
        if ("b" in os_mode and y > 50) or ("t" in os_mode and y < 50):
            return 50 + (y - 50) * k
        return y
    subs = [([(x, ov(y)) for x, y in pts], c, fn) for (pts, c), fn in zip(subs, fine)]
    xs = [x for pts, _, _ in subs for x, _ in pts]
    return left, right, subs, min(xs), max(xs)


def outline(subs, w, dx, name=""):
    """Union of stroked skeleton in font units (y up), baseline-aligned ink."""
    f = 1.0 if name in G.ROUND_PEN else G.NIB
    w = w * G.WEIGHT.get(name, 1.0)
    r = w * S / 2                         # pen half-width (verticals)
    sy = (CAP_INK - 2 * r / f) / 100      # vertical scale so ink spans 0..CAP_INK
    shapes = []
    r_main = r
    for pts, closed, fine in subs:
        r = r_main * (G.FINE if fine else 1)
        # work in a space stretched by f vertically; buffering there and squashing
        # back gives an elliptical pen: horizontals come out w / f thick.
        fp = [((x + dx) * S, ((100 - y) * sy + r_main / f) * f) for x, y in pts]
        if len(fp) == 1:
            dr = r * G.DOT_SCALE
            cx, cy = fp[0]
            if pts[0][1] > 90:   # low dots (period, colon, !, ?) sit exactly on the baseline
                cy = dr / f ** 0.5 * f
            shapes.append(Point(cx, cy).buffer(dr * f ** 0.5, quad_segs=16))
            continue
        if closed and fp[0] != fp[-1]:
            fp.append(fp[0])
        shapes.append(LineString(fp).buffer(r, quad_segs=16, cap_style="round", join_style="round"))
    geom = affinity.scale(unary_union(shapes), 1, 1 / f, origin=(0, 0))
    geom = geom.simplify(0.6, preserve_topology=True)
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    return [orient(p, sign=-1.0) for p in polys if isinstance(p, Polygon)]


def draw(polys):
    pen = TTGlyphPen(None)
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = []
            for x, y in list(ring.coords)[:-1]:
                p = (round(x), round(y))
                if not pts or pts[-1] != p:
                    pts.append(p)
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts.pop()
            if len(pts) < 3:
                continue
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
    return pen.glyph()


def notdef():
    pen = TTGlyphPen(None)
    for ring in [[(50, 0), (50, 700), (450, 700), (450, 0)], [(110, 60), (390, 60), (390, 640), (110, 640)]]:
        pen.moveTo(ring[0])
        for p in ring[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


# ------------------------------------------------------------------ borrowed part
def source_instance(style):
    return instantiateVariableFont(TTFont(SOURCE), SOURCE_AXES[style])


class _Flat(BasePen):
    """Flattens a glyph to polygon rings."""
    def __init__(self, gs):
        super().__init__(gs)
        self.rings, self.cur = [], []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16
            self.cur.append(tuple((1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * a[k]
                                  + 3 * (1 - t) * t * t * b[k] + t ** 3 * c[k] for k in (0, 1)))

    def _closePath(self):
        if len(self.cur) > 2:
            self.rings.append(self.cur)
        self.cur = []


def flat_polys(gs, name, dx=0, dy=0):
    fp = _Flat(gs)
    gs[name].draw(fp)
    geom = None
    for r in fp.rings:      # nonzero-ish: union outer rings, subtract holes (orientation)
        poly = Polygon([(x + dx, y + dy) for x, y in r]).buffer(0)
        if geom is None:
            geom = poly
        elif Polygon(r).exterior.is_ccw == Polygon(fp.rings[0]).exterior.is_ccw:
            geom = geom.union(poly)
        else:
            geom = geom.difference(poly)
    if geom is None:
        return []
    return [orient(p, -1.0) for p in (geom.geoms if isinstance(geom, MultiPolygon) else [geom])]


def copy_glyph(gs, src, dx=0):
    rec = DecomposingRecordingPen(gs)
    gs[src].draw(rec)
    pen = TTGlyphPen(None)
    rec.replay(TransformPen(pen, (1, 0, 0, 1, dx, 0)))
    bp = BoundsPen(gs)
    gs[src].draw(bp)
    return pen.glyph(), (round(bp.bounds[0] + dx) if bp.bounds else 0)


def pointed(gs, src, dx, amt):
    """Copy a round glyph, warping its bowl so the top and bottom come to a soft point."""
    rec = DecomposingRecordingPen(gs)
    gs[src].draw(rec)
    contours, cur = [], []
    for op, pts in rec.value:
        cur.append((op, pts))
        if op in ("closePath", "endPath"):
            contours.append(cur)
            cur = []
    bp = BoundsPen(gs)
    gs[src].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    def height(c):
        ys = [p[1] for _, pts in c for p in pts]
        return max(ys) - min(ys) if ys else 0
    tall = max(height(c) for c in contours)
    cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
    cy = (min(p[1] for c in contours if height(c) == tall for _, pts in c for p in pts)
          + max(p[1] for c in contours if height(c) == tall for _, pts in c for p in pts)) / 2
    def warp(p):
        x, y = p
        t = max(0.0, 1 - abs(x - cx) / hw)
        return (x + dx, y + (amt * t * t if y > cy else -amt * t * t))
    pen = TTGlyphPen(None)
    for c in contours:
        bowl = height(c) > 0.6 * tall      # the bowl rings, not Q's tail
        for op, pts in c:
            getattr(pen, op)(*[(warp(p) if bowl else (p[0] + dx, p[1])) for p in pts])
    g = pen.glyph()
    g.recalcBounds(None)
    return g, round(x0 + dx)


def borrowed(sf, own_names, extra=()):
    """{our glyph name: (glyph, adv, lsb)} and {char: name} for everything taken as is."""
    gs, cm, hm = sf.getGlyphSet(), sf.getBestCmap(), sf["hmtx"].metrics
    out, cmap = {}, {}
    for ch in LOWER + list(BORROW) + list(extra):
        src = cm.get(ord(ch))
        if src is None or src in own_names:
            print("  not borrowed:", repr(ch))
            continue
        if extra and TEXT_POINT and src in TEXT_POINT_GLYPHS:
            g, lsb = pointed(gs, src, HALF, TEXT_POINT)
        else:
            g, lsb = copy_glyph(gs, src, HALF)
        out[src] = (g, hm[src][0] + BODY_TRACK, lsb)
        cmap[ch] = src
    # ≈ is not in Instrument Sans: two of its tildes, stacked
    t = cm[ord("~")]
    bp = BoundsPen(gs)
    gs[t].draw(bp)
    mid = (bp.bounds[1] + bp.bounds[3]) / 2
    gap = (bp.bounds[3] - bp.bounds[1]) * 0.62
    polys = flat_polys(gs, t, HALF, gap) + flat_polys(gs, t, HALF, -gap)
    out["approxequal"] = (draw(polys), hm[t][0] + BODY_TRACK, round(bp.bounds[0] + HALF))
    cmap["≈"] = "approxequal"
    return out, cmap


def accented_caps(sf, our_polys, our_adv):
    """Our capital + the source's accent, centred on our letter's ink."""
    gs, cm = sf.getGlyphSet(), sf.getBestCmap()
    glyf = sf["glyf"]
    out, cmap = {}, {}
    for ch in ACCENTED_CAPS:
        src = cm.get(ord(ch))
        g = glyf[src] if src else None
        if g is None or not g.isComposite():
            print("  no composite for", ch)
            continue
        base, *marks = g.components
        base_char = next((c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if cm.get(ord(c)) == base.glyphName), None)
        if base_char is None:
            print("  base not ours for", ch)
            continue
        bp = BoundsPen(gs)
        gs[base.glyphName].draw(bp)
        src_mid = (bp.bounds[0] + bp.bounds[2]) / 2
        ours = our_polys[base_char]
        xs = [x for p in ours for x, _ in p.exterior.coords]
        shift = (min(xs) + max(xs)) / 2 - src_mid
        polys = list(ours)
        for m in marks:
            polys += flat_polys(gs, m.glyphName, m.x + shift, m.y)
        geom = unary_union(polys)
        polys = [orient(p, -1.0) for p in (geom.geoms if isinstance(geom, MultiPolygon) else [geom])]
        out[src] = (draw(polys), our_adv[base_char], min(round(x) for p in polys for x, _ in p.exterior.coords))
        cmap[ch] = src
    return out, cmap


# Letters Instrument Sans lacks (Indological transliteration): base + its dot accent.
DOT_BELOW = {"ṣ": "s", "ṭ": "t", "ḍ": "d", "ṇ": "n", "ṛ": "r", "ḷ": "l", "ṃ": "m", "ḥ": "h",
             "Ṣ": "S", "Ṭ": "T", "Ḍ": "D", "Ṇ": "N", "Ṛ": "R", "Ḷ": "L", "Ṃ": "M", "Ḥ": "H"}
DOT_ABOVE = {"ṅ": "n", "Ṅ": "N"}


def dotted(sf, our_polys, our_adv):
    gs, cm, hm = sf.getGlyphSet(), sf.getBestCmap(), sf["hmtx"].metrics
    bp = BoundsPen(gs)
    gs["dotaccent"].draw(bp)
    dx0, dy0, dx1, dy1 = bp.bounds
    dot_h = dy1 - dy0
    out, cmap = {}, {}
    for table, below in ((DOT_BELOW, True), (DOT_ABOVE, False)):
        for ch, base in table.items():
            if base in our_polys:
                polys, adv = list(our_polys[base]), our_adv[base]
                top = CAP_INK
            else:
                src = cm[ord(base)]
                polys, adv = flat_polys(gs, src, HALF), hm[src][0] + BODY_TRACK
                top = CAP_INK if base.isupper() else sf["OS/2"].sxHeight
            xs = [x for p in polys for x, _ in p.exterior.coords]
            cx = (min(xs) + max(xs)) / 2
            shift_x = cx - (dx0 + dx1) / 2
            if below:
                shift_y = -0.55 * dot_h - dot_h - dy0 - 40
            else:
                shift_y = top + 0.45 * dot_h + 60 - dy0
            geom = unary_union(polys + flat_polys(gs, "dotaccent", shift_x, shift_y))
            polys = [orient(p, -1.0) for p in (geom.geoms if isinstance(geom, MultiPolygon) else [geom])]
            name = f"uni{ord(ch):04X}"
            out[name] = (draw(polys), adv, min(round(x) for p in polys for x, _ in p.exterior.coords))
            cmap[ch] = name
    return out, cmap


def kern_pairs(sf, names):
    """Flatten the source's kern feature into {(left, right): value} for the given glyphs."""
    gp = sf["GPOS"].table
    idx = sorted({i for fr in gp.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
                  for i in fr.Feature.LookupListIndex})
    total = {}
    for li in idx:
        lk = gp.LookupList.Lookup[li]
        subs = lk.SubTable
        if lk.LookupType == 9:
            if subs[0].ExtensionLookupType != 2:
                continue
            subs = [s.ExtSubTable for s in subs]
        elif lk.LookupType != 2:
            continue
        prepared = []
        for st in subs:
            cov = {g: i for i, g in enumerate(st.Coverage.glyphs)}
            if st.Format == 1:
                sets = {g: {r.SecondGlyph: getattr(r.Value1, "XAdvance", 0) or 0
                            for r in st.PairSet[i].PairValueRecord} for g, i in cov.items()}
                prepared.append((cov, 1, sets))
            else:
                prepared.append((cov, 2, st))
        for L in names:
            for R in names:
                for cov, fmt, data in prepared:
                    if L not in cov:
                        continue
                    if fmt == 1:
                        if R not in data[L]:
                            continue
                        v = data[L][R]
                    else:
                        c1 = data.ClassDef1.classDefs.get(L, 0)
                        c2 = data.ClassDef2.classDefs.get(R, 0)
                        v = getattr(data.Class1Record[c1].Class2Record[c2].Value1, "XAdvance", 0) or 0
                    if v:
                        total[(L, R)] = total.get((L, R), 0) + v
                    break
    return total


def build(style, w, verbose=False, text=False):
    extra = 0.5 * (w - G.STROKE) / 2      # bold: keep most of the inked gap
    sf = source_instance(style)
    cms = sf.getBestCmap()

    glyphs = {".notdef": notdef(), "space": TTGlyphPen(None).glyph()}
    metrics = {".notdef": (500, 50), "space": (sf["hmtx"][cms[32]][0] + BODY_TRACK, 0)}   # Instrument Sans word space + body tracking
    our_polys, our_adv, table = {}, {}, []
    built = [] if text else [n for n in G.GLYPHS if n not in G.FROM_SOURCE]
    for name in built:
        left, right, subs, x0, x1 = skeleton(name)
        left, right = left + extra, right + extra
        if name in G.DIGITS:           # tabular figures: centre the skeleton
            side = (G.DIGIT_ADV - (x1 - x0)) / 2
            left = right = side + extra
        polys = outline(subs, w, left - x0, name)
        glyphs[name] = draw(polys)
        adv = round((left + (x1 - x0) + right) * S)
        metrics[name] = (adv, min(round(x) for p in polys for x, _ in p.exterior.coords))
        our_polys[name], our_adv[name] = polys, adv
        table.append(f"{name}:{adv}")
    cmap = {ord(ch): g for ch, g in G.CHARS.items() if g in glyphs}
    parts = ([borrowed(sf, set(), TEXT_EXTRA)] if text
             else [borrowed(sf, set(built)), accented_caps(sf, our_polys, our_adv)])
    for part in parts + [dotted(sf, our_polys, our_adv)]:
        for name, (g, adv, lsb) in part[0].items():
            glyphs[name] = g
            metrics[name] = (adv, lsb)
        cmap.update({ord(ch): n for ch, n in part[1].items()})
    order = [".notdef", "space"] + [n for n in glyphs if n not in (".notdef", "space")]
    if verbose:
        print("advances:", " ".join(table))
        print("source n/o/H adv:", metrics[cms[ord("n")]][0], metrics[cms[ord("o")]][0], sf["hmtx"][cms[ord("H")]][0])

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    asc, desc = sf["hhea"].ascent, sf["hhea"].descent     # same line height as Instrument Sans
    fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0)
    family, stem_base = (FAMILY_TEXT, FILE_STEM_TEXT) if text else (FAMILY, FILE_STEM)
    ps_family = family.replace(" ", "")
    fb.setupNameTable({
        "copyright": COPYRIGHT_TEXT if text else COPYRIGHT,
        "familyName": family,
        "styleName": style,
        "uniqueFontIdentifier": f"{ps_family}-{style};{VERSION}",
        "fullName": f"{family} {style}",
        "psName": f"{ps_family}-{style}",
        "version": f"Version {VERSION}",
        "licenseDescription": LICENSE,
        "licenseInfoURL": LICENSE_URL,
    })
    bold = style == "Bold"
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                usWinAscent=asc, usWinDescent=-desc, sCapHeight=CAP_INK,
                sxHeight=sf["OS/2"].sxHeight, usWeightClass=700 if bold else 400,
                fsSelection=(0x20 if bold else 0x40) | 0x80, achVendID="NONE", version=4)
    fb.setupPost()
    now = timestampNow()
    fb.setupHead(unitsPerEm=UPM, macStyle=1 if bold else 0, created=now, modified=now)
    font = fb.font

    # Kerning: source values for every pair touching a borrowed glyph (source names
    # mapped to ours via the cmap), our own list for pairs between our glyphs.
    rename = {}
    for cp, ours in cmap.items():
        if cp in cms:
            rename[cms[cp]] = ours
    ours_set = set(built)
    raw = kern_pairs(sf, list(rename))
    pairs = {}
    for (L, R), v in raw.items():
        l2, r2 = rename[L], rename[R]
        if l2 not in ours_set or r2 not in ours_set:
            pairs[(l2, r2)] = v
    from_source = len(pairs)
    for lefts, rights, v in ([] if text else G.KERN):
        for L in lefts:
            for R in rights:
                if L in ours_set and R in ours_set:     # pairs with borrowed marks keep the source value
                    pairs[(L, R)] = round(v * S)
                elif (L, R) not in pairs and L in glyphs and R in glyphs:
                    pairs[(L, R)] = round(v * S)
    lines = [f"  pos {L} {R} {v};" for (L, R), v in sorted(pairs.items()) if v]
    addOpenTypeFeaturesFromString(font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n"
                                  "feature kern {\n" + "\n".join(lines) + "\n} kern;\n")
    if verbose:
        print(f"kern pairs: {len(lines)} ({from_source} from Instrument Sans)")

    stem = f"{stem_base}-{style}"
    ttf = os.path.join(HERE, stem + ".ttf")
    font.save(ttf)
    f2 = TTFont(ttf)
    f2.flavor = "woff2"
    f2.save(os.path.join(HERE, stem + ".woff2"))
    print(f"wrote {stem}.ttf / .woff2  ({len(order)} glyphs)")


if __name__ == "__main__":
    build("Regular", G.STROKE, verbose=True)
    build("Bold", G.STROKE_BOLD)
    build("Regular", G.STROKE, verbose=True, text=True)
    build("Bold", G.STROKE_BOLD, text=True)
