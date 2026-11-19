"""News thumbnails, drawn in the landing-page style: carved stone and clay objects lit from the top left,
with Mahadevan's sign drawings cut into them, on a dark field of pressed signs.

Every object is an illustration, not a real artefact. Each scene is an SVG height map (white = surface,
black = cut) that the `carve` filter lights, the same way as the hero seal in build.py.

Run:  .venv/bin/python -I site/thumbs/make_news_thumbs.py        (writes site/assets/news/<id>.webp)
      .venv/bin/python -I site/thumbs/make_news_thumbs.py --sheet (also writes /tmp/oi_thumbs_sheet.png)
"""
import json
import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
SIGNS = SITE / "assets" / "signs"
OUT = SITE / "assets" / "news"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 600, 400
ACC = "#93B2E2"          # the site's accent in dark mode
GROUND = "#1c1814"

TONES = {   # base rgb (0-1), patina, shadow colour inside cuts, side colour, relief
    "steatite": ((.93, .88, .80), "#b99a7c", "#8a6e55", "#a48d73", 8),
    "terracotta": ((.80, .53, .38), "#8f4f33", "#5c3121", "#8a4c33", 7),
    "clay": ((.86, .70, .55), "#a87a58", "#6e4a33", "#9c7457", 7),
    "paper": ((.95, .92, .86), "#d9cdb8", "#b8ab95", "#c9bda8", 2.5),
    "stone": ((.74, .72, .68), "#8e8a82", "#4c4843", "#77736c", 8),
    "silver": ((.82, .82, .84), "#9a9aa2", "#56575e", "#8a8a92", 6),
}


def carve_filter(name):
    (r, g, b), patina, dark, _, relief = TONES[name]
    return f'''<filter id="carve-{name}" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}" color-interpolation-filters="sRGB">
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="h0"/>
<feGaussianBlur in="h0" stdDeviation="1.6" result="hb"/>
<feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="4" result="grain"/>
<feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .06 0" result="ga"/>
<feComposite in="hb" in2="ga" operator="arithmetic" k2="1" k3="1" result="h"/>
<feDiffuseLighting in="h" surfaceScale="{relief}" diffuseConstant="1" lighting-color="#fff6ea" result="dif"><feDistantLight azimuth="225" elevation="40"/></feDiffuseLighting>
<feSpecularLighting in="h" surfaceScale="{relief}" specularConstant="{.9 if name == 'silver' else .55}" specularExponent="{18 if name == 'silver' else 26}" lighting-color="#fff4e6" result="spec"><feDistantLight azimuth="225" elevation="48"/></feSpecularLighting>
<feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="11" result="mot"/>
<feColorMatrix in="mot" type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  0 0 0 0 1" result="base0"/>
<feColorMatrix in="mot" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -.35 0 0 0 .22" result="motA"/>
<feFlood flood-color="{patina}" result="pat0"/><feComposite in="pat0" in2="motA" operator="in" result="pat"/>
<feMerge result="base"><feMergeNode in="base0"/><feMergeNode in="pat"/></feMerge>
<feComponentTransfer in="hb" result="floor"><feFuncA type="table" tableValues=".62 1"/></feComponentTransfer>
<feComposite in="base" in2="dif" operator="arithmetic" k1=".95" k2=".22" result="lit"/>
<feComposite in="lit" in2="floor" operator="in" result="lit2"/>
<feFlood flood-color="{dark}" result="dk"/>
<feMerge result="lit3"><feMergeNode in="dk"/><feMergeNode in="lit2"/></feMerge>
<feComposite in="spec" in2="lit3" operator="arithmetic" k2=".4" k3="1" result="out"/>
<feComposite in="out" in2="SourceAlpha" operator="in"/>
</filter>'''


DEFS = "".join(carve_filter(t) for t in TONES) + f'''
<filter id="emb" color-interpolation-filters="sRGB"><feOffset in="SourceAlpha" dx="1" dy="1" result="o"/><feComposite in="o" in2="SourceAlpha" operator="out" result="e"/><feFlood flood-color="#000" flood-opacity=".35"/><feComposite in2="e" operator="in" result="lo"/><feOffset in="SourceAlpha" dx="-1" dy="-1" result="o2"/><feComposite in="o2" in2="SourceAlpha" operator="out" result="e2"/><feFlood flood-color="#fff" flood-opacity=".14"/><feComposite in2="e2" operator="in" result="hi"/><feMerge><feMergeNode in="lo"/><feMergeNode in="hi"/></feMerge></filter>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="tint" color-interpolation-filters="sRGB"><feFlood flood-color="{ACC}"/><feComposite in2="SourceAlpha" operator="in"/></filter>
<filter id="ink" color-interpolation-filters="sRGB"><feFlood flood-color="#2b231c"/><feComposite in2="SourceAlpha" operator="in"/></filter>
<radialGradient id="vig" cx="50%" cy="46%" r="70%"><stop offset="0" stop-color="{GROUND}" stop-opacity="0"/><stop offset=".55" stop-color="{GROUND}" stop-opacity=".55"/><stop offset="1" stop-color="#0f0d0b" stop-opacity=".95"/></radialGradient>
<radialGradient id="glow" cx="38%" cy="30%" r="60%"><stop offset="0" stop-color="#3a3129"/><stop offset="1" stop-color="{GROUND}"/></radialGradient>'''


# ---------------------------------------------------------------- drawing helpers
def sign(m, x, y, s, extra=""):
    """A sign drawing in black (a cut, when inside a height map)."""
    return f'<image href="{(SIGNS / f"M{m}.png").as_uri()}" x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" style="filter:brightness(0)"{extra}/>'


def raised(m, x, y, s):
    """A sign standing up out of a recessed field (an impression of a carved seal)."""
    return f'<image href="{(SIGNS / f"M{m}.png").as_uri()}" x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" style="filter:brightness(0) invert(1)"/>'


def ghost(m, x, y, s, op=1):
    return f'<image href="{(SIGNS / f"M{m}.png").as_uri()}" x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" filter="url(#tint)" opacity="{op}"/>'


def inked(m, x, y, s):
    return f'<image href="{(SIGNS / f"M{m}.png").as_uri()}" x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" filter="url(#ink)"/>'


def row(ms, x, y, s, gap=None, fn=sign):
    gap = s * .18 if gap is None else gap
    return "".join(fn(m, x + k * (s + gap), y, s) for k, m in enumerate(ms))


def rrect(x, y, w, h, r):
    return f'M{x + r} {y} H{x + w - r} Q{x + w} {y} {x + w} {y + r} V{y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} H{x + r} Q{x} {y + h} {x} {y + h - r} V{y + r} Q{x} {y} {x + r} {y} Z'


def circle(cx, cy, r):
    return f'M{cx - r} {cy} A{r} {r} 0 1 0 {cx + r} {cy} A{r} {r} 0 1 0 {cx - r} {cy} Z'


def blob(cx, cy, rx, ry, seed, wob=.07, n=14):
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1 + rnd.uniform(-wob, wob)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    d = f"M{(pts[0][0] + pts[-1][0]) / 2:.1f} {(pts[0][1] + pts[-1][1]) / 2:.1f}"
    for k in range(n):
        p, q = pts[k], pts[(k + 1) % n]
        d += f" Q{p[0]:.1f} {p[1]:.1f} {(p[0] + q[0]) / 2:.1f} {(p[1] + q[1]) / 2:.1f}"
    return d + " Z"


_CLIP = 0


def obj(d, cuts="", tone="steatite", depth=14, over="", tilt=None):
    """A solid object: soft shadow, a stack of side slices, then the lit face with its cuts.
    `over` is drawn on the face after lighting (ink on paper)."""
    side = TONES[tone][3]
    shadow = f'<path d="{d}" fill="#000" opacity=".55" filter="url(#soft)" transform="translate(6 {depth + 10})"/>'
    slices = "".join(f'<path d="{d}" fill="{side}" transform="translate(0 {k})" opacity="1"/>' for k in range(depth, 0, -1))
    edge = f'<path d="{d}" fill="#000" opacity=".28" transform="translate(0 {depth})"/>'
    global _CLIP
    _CLIP += 1
    cid = f"c{_CLIP}"
    face = (f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g filter="url(#carve-{tone})"><path d="{d}" fill="#fff"/>'
            f'<g clip-path="url(#{cid})">{cuts}</g></g>')
    g = f'{shadow}{slices}{edge}{face}{over}'
    return f'<g transform="{tilt}">{g}</g>' if tilt else g


def bull(x, y, s=1.0, fill="#000", flip=False):
    """The short-horned bull from the landing data figure, as a solid cut."""
    t = f'translate({x} {y}) scale({-s if flip else s} {s})'
    return (f'<g transform="{t}" fill="{fill}" stroke="{fill}" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 14 C4 6 12 4 24 5 C32 5 38 6 40 10 C41 16 36 19 26 19 C16 19 6 19 4 14 Z" stroke-width="1"/>'
            '<path d="M38 8 L44 3 C47 2 49 4 48 6 L44 10 Z" stroke-width="1"/>'
            '<path d="M45 3 C46 0 48 -2 51 -3" fill="none" stroke-width="2.2"/>'
            '<path d="M10 17 L9.5 24 M16 18 L16 24 M30 18 L30.5 24 M36 16 L36.5 23 M4 13 C1 15 0 19 1 22" fill="none" stroke-width="3.4"/></g>')


def acc(d, w=3, dash=None, op=1):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{ACC}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da} opacity="{op}"/>'


def corners(x, y, w, h, L=10):
    return acc(f"M{x} {y + L} V{y} H{x + L} M{x + w - L} {y} H{x + w} V{y + L} M{x + w} {y + h - L} V{y + h} H{x + w - L} M{x + L} {y + h} H{x} V{y + h - L}", 2.6)


def strokes(d, w=4, c="#000"):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def fake_marks(x, y, n, s, seed, w=3):
    """Abstract marks standing for another script's signs (not real signs of any script)."""
    rnd = random.Random(seed)
    out = ""
    for k in range(n):
        cx = x + k * s * 1.35
        kind = rnd.randrange(6)
        h = s / 2
        if kind == 0:
            d = f"M{cx} {y} V{y + s} M{cx - h * .7} {y + h} H{cx + h * .7}"
        elif kind == 1:
            d = f"M{cx - h} {y + s} L{cx} {y} L{cx + h} {y + s}"
        elif kind == 2:
            d = circle(cx, y + h, h * .7)
        elif kind == 3:
            d = f"M{cx - h} {y} H{cx + h} M{cx} {y} V{y + s} M{cx - h * .6} {y + s} H{cx + h * .6}"
        elif kind == 4:
            d = f"M{cx - h} {y + h} L{cx} {y} L{cx + h} {y + h} L{cx} {y + s} Z"
        else:
            d = f"M{cx - h} {y} Q{cx + h} {y + h * .5} {cx - h * .4} {y + s} M{cx + h * .4} {y} V{y + s * .6}"
        out += strokes(d, w)
    return out


def field(seed):
    """Background: the hero's field of pressed signs, faded toward the edges."""
    ids = sorted(int(p.stem[1:]) for p in SIGNS.glob("M*.png"))
    rnd = random.Random(seed)
    out = ""
    for j in range(13):
        for i in range(19):
            out += sign(rnd.choice(ids), 4 + i * 32, 2 + j * 32, 26)
    return (f'<rect width="{W}" height="{H}" fill="url(#glow)"/>'
            f'<g filter="url(#emb)" opacity=".75">{out}</g><rect width="{W}" height="{H}" fill="url(#vig)"/>')


# ---------------------------------------------------------------- the scenes
def square_seal(x, y, s, signs, animal=True, tone="steatite", depth=16, sz=None, tilt=None, extra=""):
    sz = sz or s * .22
    n = len(signs)
    gx = (s - n * sz - (n - 1) * sz * .15) / 2
    cuts = row(signs, x + gx, y + s * .1, sz, sz * .15)
    if animal:
        bs = s / 70
        cuts += bull(x + s * .17, y + s * .45, bs)
    return obj(rrect(x, y, s, s, s * .07), cuts + extra, tone, depth, tilt=tilt)


def s_restoration():
    d = blob(300, 205, 205, 150, 7, .06)
    rec = rrect(170, 92, 260, 200, 14)
    cuts = f'<path d="{rec}" fill="#a9a9a9"/>'
    cuts += raised(267, 192, 108, 52) + raised(99, 252, 108, 52) + raised(342, 372, 108, 52)
    cuts += bull(208, 178, 2.9, fill="#fff")
    cuts += f'<path d="M306 98 L345 96 L352 120 L343 150 L330 168 L309 160 L300 130 Z" fill="#2a2a2a"/>'
    over = acc(rrect(301, 101, 54, 58, 8), 2.6, "6 6") + ghost(176, 306, 108, 44)
    return obj(d, cuts, "clay", 18, over)


def s_voynich():
    beam = obj(rrect(110, 290, 380, 22, 6), "", "stone", 10)
    pivot = obj("M300 312 L330 362 L270 362 Z", "", "stone", 6)
    left = square_seal(140, 160, 128, [342, 59, 99], animal=True, depth=12)
    lines = "".join(strokes(f"M{348} {y} " + " ".join(f"q6 -7 12 0 t12 0" for _ in range(9)), 2.6) for y in (186, 210, 234))
    lines += strokes("M360 258 q14 -26 26 0 q10 18 22 -4", 2.6)
    page = obj(rrect(334, 150, 132, 140, 5), lines, "paper", 4)
    return beam + pivot + left + page + f'<circle cx="300" cy="300" r="5" fill="{ACC}"/>'


def s_dominik():
    top = obj(rrect(120, 92, 360, 92, 12), row([342, 99, 267], 160, 105, 66, 40), "steatite", 14)
    bot = obj(rrect(120, 232, 360, 92, 12), row([342], 160, 245, 66) + row([176], 372, 245, 66), "steatite", 14)
    over = acc("M228 112 Q262 78 296 112", 3) + acc("M222 103 l6 9 l-9 3", 3)
    over += acc(rrect(262, 243, 74, 70, 10), 2.6, "6 6") + ghost(99, 266, 245, 66, .45)
    over += acc("M285 266 l28 28 M313 266 l-28 28", 3.4)
    return top + bot + over


def sigil_marks(x, y, s):
    c = s / 2
    return (strokes(f"M{x + c} {y} V{y + s} M{x} {y + c} H{x + s}", 4)
            + strokes(circle(x + s * 1.65 + c, y + c, c * .8), 4)
            + strokes(f"M{x + s * 3.3} {y + s} L{x + s * 3.3 + c} {y} L{x + s * 3.3 + s} {y + s} Z", 4))


def s_sigil():
    left = square_seal(82, 110, 196, [342, 99, 267], animal=False, depth=16, extra=sign(59, 82 + 58, 110 + 70, 92))
    spiral = "M" + " L".join(f"{422 + r * math.cos(a):.1f} {226 + r * math.sin(a):.1f}" for a, r in
                             ((t / 8, 3 + t * .85) for t in range(0, 200)))
    right = obj(rrect(322, 110, 196, 196, 14), sigil_marks(352, 130, 34) + strokes(spiral, 5), "steatite", 16)
    return left + right + acc("M288 196 H312 M288 214 H312", 3.4)


def crown(cx, cy, s, c="#000"):
    return (f'<path d="M{cx - s} {cy + s * .5} L{cx - s} {cy - s * .4} L{cx - s * .5} {cy} L{cx} {cy - s * .7} '
            f'L{cx + s * .5} {cy} L{cx + s} {cy - s * .4} L{cx + s} {cy + s * .5} Z" fill="{c}"/>')


def s_lehs():
    back = obj(rrect(150, 96, 300, 220, 6), "", "paper", 4, tilt="rotate(-5 300 206)")
    mid = obj(rrect(150, 96, 300, 220, 6), "", "paper", 4, tilt="rotate(3 300 206)")
    ink = "".join(f'<g opacity=".85" style="filter:none">{fake_marks(190, 140 + k * 34, 9, 16, 30 + k, 2.4)}</g>' for k in range(4))
    front = obj(rrect(150, 96, 300, 220, 6), "", "paper", 4,
                over=f'<g stroke="#2b231c">{ink.replace("#000", "#2b231c")}</g>')
    medal = obj(circle(455, 108, 44), crown(455, 112, 24), "silver", 8)
    return back + mid + front + medal + acc(circle(455, 108, 52), 2.4, "5 6")


def shield_d(x, y, w, h):
    return f'M{x} {y} H{x + w} V{y + h * .5} Q{x + w} {y + h * .85} {x + w / 2} {y + h} Q{x} {y + h * .85} {x} {y + h * .5} Z'


def s_nair():
    sh = obj(shield_d(62, 118, 118, 148), strokes("M84 214 L121 168 L158 214 M84 242 L121 196 L158 242", 7), "stone", 12)
    seal = square_seal(262, 128, 120, [342, 59, 99], depth=12)
    ledger = obj(rrect(432, 118, 112, 148, 8),
                 "".join(strokes(f"M{448} {y} H{528}", 2) + strokes(" ".join(f"M{452 + i * 9} {y - 16} V{y - 4}" for i in range(n)), 2.6)
                         for y, n in ((146, 5), (176, 8), (206, 3), (236, 6))), "terracotta", 12)
    line = acc("M90 330 H516", 2.4) + acc("M90 320 V340 M516 320 V340", 2.4)
    mark = f'<path d="M322 316 L334 330 L322 344 L310 330 Z" fill="{ACC}"/>'
    return sh + seal + ledger + line + mark


def s_uae():
    cuts = row([267, 59, 99], 236, 132, 40, 6) + bull(246, 200, 2.1)
    d = circle(300, 206, 112)
    return obj(d, cuts, "steatite", 16) + acc(circle(300, 206, 134), 2.6, "4 9")


def s_kriger():
    a = [342, 99, 267]
    b = [176, 59, 342]
    out = ""
    for k, signs in enumerate((a, b, a)):
        x = 66 + k * 170
        out += square_seal(x, 144, 128, signs, animal=True, depth=12)
    out += acc("M130 136 Q300 50 470 136", 3) + acc("M462 124 l8 12 l-14 3", 3)
    return out


def s_asi():
    out = ""
    for k, m in enumerate((342, 59, 99)):
        x = 96 + k * 146
        lift = -10 if k == 1 else 0
        out += obj(rrect(x, 118 + lift, 118, 134, 10), sign(m, x + 22, 140 + lift, 74), "terracotta", 14)
        out += obj(rrect(x + 14, 102 + lift, 90, 16, 4), "", "stone", 4)
    return out + acc("M96 302 V312 H502 V302", 3)


def s_protoelamite():
    cuts = ""
    for r_, (y, ks) in enumerate(((132, "ooO|"), (186, "oO||"), (240, "Ooo|"))):
        x = 150
        for ch in ks:
            if ch == "o":
                cuts += f'<circle cx="{x}" cy="{y}" r="11" fill="#333"/>'
                x += 30
            elif ch == "O":
                cuts += f'<ellipse cx="{x + 6}" cy="{y}" rx="18" ry="9" fill="#333"/>'
                x += 44
            else:
                cuts += strokes(f"M{x} {y - 14} V{y + 14}", 3)
                x += 22
        cuts += fake_marks(x + 28, y - 13, 4, 26, 50 + r_, 3.2)
        cuts += strokes(f"M136 {y + 25} H464", 1.8, "#555")
    d = blob(300, 200, 196, 140, 3, .03, 18)
    return obj(d, cuts, "clay", 16) + corners(132, 114, 116, 40)


def s_dixit():
    x, y, s = 160, 60, 280
    cuts = row([342, 99, 267, 176], x + 34, y + 26, 46, 14) + bull(x + 40, y + 120, 3.6)
    out = obj(rrect(x, y, s, s, 20), cuts, "steatite", 18)
    for k in range(4):
        out += corners(x + 30 + k * 60, y + 22, 54, 54, 9)
    out += corners(x + 30, y + 112, 214, 132, 14)
    return out


def s_tyc():
    seal = square_seal(80, 128, 150, [342, 99], animal=False, depth=14, extra=sign(59, 80 + 38, 128 + 52, 80))
    rock = blob(420, 210, 120, 110, 12, .12, 11)
    cuts = strokes("M318 196 L360 146 L388 176 L420 128 L458 180 L484 154 L522 196", 4) + sign(59, 382, 196, 76)
    return seal + obj(rock, cuts, "stone", 16) + acc("M258 196 q8 -8 16 0 t16 0 M258 214 q8 -8 16 0 t16 0", 3)


def pot_d(cx, top, w, h):
    n = w * .32
    return (f'M{cx - n} {top} H{cx + n} L{cx + n * .9} {top + h * .1} C{cx + w * .62} {top + h * .3} {cx + w * .58} {top + h * .85} {cx + w * .2} {top + h} '
            f'H{cx - w * .2} C{cx - w * .58} {top + h * .85} {cx - w * .62} {top + h * .3} {cx - n * .9} {top + h * .1} Z')


def s_pots():
    out = ""
    for k, (m, h) in enumerate(((342, 200), (99, 228), (267, 190))):
        cx = 140 + k * 160
        top = 304 - h
        cuts = sign(m, cx - 30, top + h * .42, 60) + strokes(f"M{cx - 60} {top + h * .3} Q{cx} {top + h * .36} {cx + 60} {top + h * .3}", 2, "#555")
        out += obj(pot_d(cx, top, 150, h), cuts, "terracotta", 10)
    return out + acc(rrect(268, 166, 64, 64, 10), 2.6, "5 6")


def glyph_block(x, y, s, seed):
    rnd = random.Random(seed)
    out = f'<path d="{rrect(x, y, s, s, s * .28)}" fill="none" stroke="#000" stroke-width="3.5"/>'
    out += strokes(f"M{x + s * .22} {y + s * .25} V{y + s * .75} M{x + s * .36} {y + s * .25} V{y + s * .75}", 3)
    out += strokes(f"M{x + s * .52} {y + s * .3} Q{x + s * .8} {y + s * (.25 + rnd.random() * .1)} {x + s * .78} {y + s * .5} Q{x + s * .76} {y + s * .74} {x + s * .54} {y + s * .7}", 3)
    return out


def s_maya():
    d = (f"M216 360 V112 Q216 52 300 52 Q384 52 384 112 V360 Z")
    cuts = "".join(glyph_block(236 + c * 76, 96 + r * 66, 58, r * 2 + c) for r in range(4) for c in range(2))
    out = obj(d, cuts, "stone", 16)
    out += acc("M452 120 V312", 2.4) + "".join(f'<circle cx="452" cy="{y}" r="7" fill="{ACC}"/>' + acc(f"M444 {y} H{396}", 2, "3 5")
                                                for y in (125, 191, 257))
    return out


def s_mahadevan():
    under = obj(rrect(130, 70, 340, 260, 6), "", "paper", 4, tilt="rotate(-4 300 200)")
    ids = [1, 59, 342, 99, 267, 176, 211, 65, 109, 233, 162, 3, 47, 287, 12, 405, 293, 51, 132, 249, 230, 391, 145, 326]
    ids = [m for m in ids if (SIGNS / f"M{m}.png").exists()]
    ink = ""
    for k, m in enumerate(ids[:24]):
        x, y = 160 + (k % 6) * 48, 96 + (k // 6) * 54
        ink += inked(m, x, y, 38)
    rules = "".join(f'<path d="M150 {148 + j * 54} H450" stroke="#2b231c" stroke-opacity=".25" stroke-width="1"/>' for j in range(3))
    top = obj(rrect(130, 70, 340, 260, 6), "", "paper", 4, over=rules + ink, tilt="rotate(2 300 200)")
    return under + top


def star(cx, cy, r, n=6):
    pts = []
    for k in range(n * 2):
        rr = r if k % 2 == 0 else r * .42
        a = -math.pi / 2 + k * math.pi / n
        pts.append(f"{cx + rr * math.cos(a):.1f} {cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def s_parpola():
    left = obj(rrect(84, 98, 200, 200, 14), sign(59, 104, 118, 160), "steatite", 16)
    right = obj(circle(430, 198, 86), f'<path d="{star(430, 198, 54)}" fill="#000"/>', "stone", 14)
    return left + right + acc("M290 170 Q318 130 344 170", 3) + acc("M336 160 l8 10 l-12 4", 3)


def s_fsw():
    seal = square_seal(90, 120, 170, [342, 99], animal=True, depth=14)
    tile = obj(shield_d(354, 112, 156, 186), f'<path d="{star(432, 190, 46, 8)}" fill="#000"/>' + strokes("M380 250 H484", 6), "stone", 14)
    return seal + tile + acc("M282 205 H332", 2.6, "4 7")


def s_entropy():
    d = rrect(86, 86, 428, 232, 16)
    cuts = row([342, 99, 267, 176], 112, 104, 34, 10)
    cuts += f'<path d="{rrect(150, 170, 290, 34, 17)}" fill="#3a3a3a"/>' + f'<path d="{rrect(110, 232, 260, 34, 17)}" fill="#3a3a3a"/>'
    out = obj(d, cuts, "steatite", 16)
    return out + acc("M330 156 V282", 3.4) + f'<circle cx="330" cy="156" r="7" fill="{ACC}"/>'


def s_laursen():
    rs = obj(circle(170, 200, 104), row([342, 267, 99], 112, 120, 38, 4) + bull(118, 200, 1.9), "steatite", 16)
    sq = obj(rrect(332, 100, 196, 196, 14), row([342, 99, 267], 362, 120, 40, 8) + bull(372, 200, 2.0), "steatite", 16)
    swap = acc("M150 92 Q290 30 392 90", 2.6) + acc("M190 92 Q330 50 470 90", 2.6, "4 6")
    return rs + sq + swap


def s_snyder():
    left = obj(rrect(110, 64, 150, 272, 12), "".join(sign(m, 146, 82 + k * 62, 56) for k, m in enumerate((342, 59, 99, 267))), "steatite", 14)
    right = acc(rrect(340, 64, 150, 272, 12), 2.6, "6 8")
    links = "".join(acc(f"M268 {110 + k * 62} C300 {110 + k * 62} 312 {110 + k * 62} 334 {110 + k * 62}", 2.6) for k in range(4))
    slots = "".join(acc(rrect(386, 86 + k * 62, 58, 50, 8), 1.6, "3 5", .7) for k in range(4))
    return left + links + right + slots


def s_dna():
    d = rrect(150, 64, 300, 272, 16)
    cuts = ""
    pts1, pts2 = [], []
    for t in range(0, 101):
        y = 84 + t * 2.32
        a = t / 100 * 3 * math.pi
        pts1.append(f"{300 + 70 * math.sin(a):.1f} {y:.1f}")
        pts2.append(f"{300 - 70 * math.sin(a):.1f} {y:.1f}")
        if t % 6 == 3:
            cuts += strokes(f"M{300 + 70 * math.sin(a):.1f} {y:.1f} H{300 - 70 * math.sin(a):.1f}", 3)
    cuts += strokes("M" + " L".join(pts1), 7) + strokes("M" + " L".join(pts2), 7)
    y = 84 + 51 * 2.32
    hi = acc(f"M{300 + 70 * math.sin(51 / 100 * 3 * math.pi):.1f} {y:.1f} H{300 - 70 * math.sin(51 / 100 * 3 * math.pi):.1f}", 4)
    return obj(d, cuts, "terracotta", 16) + hi


def s_goods():
    jar = obj(pot_d(250, 60, 230, 286), strokes("M170 106 Q250 118 330 106", 2.4, "#555"), "terracotta", 12)
    cord = strokes("M178 72 Q236 120 360 170", 3.4, "#d8c6a5")
    tag_d = blob(392, 210, 70, 58, 21, .08)
    tag = obj(tag_d, f'<path d="{rrect(352, 172, 80, 76, 8)}" fill="#a9a9a9"/>' + raised(342, 360, 180, 30) + raised(99, 394, 180, 30) + bull(362, 214, 1.3, "#fff"), "clay", 12)
    return jar + cord + tag + acc(circle(392, 210, 88), 2.4, "4 8")


def beaker_d(cx, top, w, h):
    return (f"M{cx - w / 2} {top} H{cx + w / 2} L{cx + w * .34} {top + h * .45} Q{cx + w * .3} {top + h * .9} {cx + w * .36} {top + h} "
            f"H{cx - w * .36} Q{cx - w * .3} {top + h * .9} {cx - w * .34} {top + h * .45} Z")


def s_desset():
    cuts = fake_marks(250, 150, 5, 18, 71, 3) + fake_marks(254, 190, 5, 16, 72, 3)
    cuts += strokes("M232 132 H372 M236 222 H364", 2, "#555")
    vessel = obj(beaker_d(300, 104, 176, 236), cuts, "silver", 12)
    medal = obj(circle(468, 112, 46), crown(468, 116, 25), "stone", 10)
    return vessel + medal + acc("M424 128 Q400 150 378 152", 2.6) + acc("M386 146 l-9 6 l10 4", 2.6)


def s_cluster():
    d = rrect(70, 74, 460, 252, 18)
    rnd = random.Random(9)
    cuts = ""
    left = [59, 60, 65, 66, 67, 69]
    right = [342, 343, 344, 347, 348, 352]
    for k, m in enumerate(left):
        a = k / len(left) * 2 * math.pi
        cuts += sign(m, 160 + 58 * math.cos(a) - 27, 200 + 50 * math.sin(a) - 27, 54)
    for k, m in enumerate(right):
        a = k / len(right) * 2 * math.pi + .4
        cuts += sign(m, 440 + 58 * math.cos(a) - 27, 200 + 50 * math.sin(a) - 27, 54)
    out = obj(d, cuts, "clay", 16)
    return out + acc("M160 200 m-100 0 a100 86 0 1 0 200 0 a100 86 0 1 0 -200 0", 2.6, "5 7") + acc("M440 200 m-100 0 a100 86 0 1 0 200 0 a100 86 0 1 0 -200 0", 2.6, "5 7")


# ---------------------------------------------------------------- library news, 2026-11-19
def wedge(x, y, s=1.0):
    """An abstract wedge impression (not a real cuneiform sign)."""
    return (f'<path d="M{x} {y} L{x + 14 * s} {y + 5 * s} L{x} {y + 10 * s} Z" fill="#000"/>'
            + strokes(f"M{x + 12 * s} {y + 5 * s} H{x + 30 * s}", 2.6 * s))


def wedge_row(x, y, n, seed, s=1.0):
    rnd = random.Random(seed)
    out = ""
    for k in range(n):
        if rnd.random() < .5:
            out += wedge(x + k * 36 * s, y, s)
        else:
            out += (f'<path d="M{x + k * 36 * s} {y} L{x + k * 36 * s + 10 * s} {y + 14 * s} L{x + k * 36 * s + 20 * s} {y} Z" fill="#000"/>'
                    + strokes(f"M{x + k * 36 * s + 10 * s} {y + 12 * s} V{y + 28 * s}", 2.6 * s))
    return out


def s_hexagon():
    d = rrect(96, 60, 408, 280, 10)
    cuts = ""
    for k in range(1, 7):
        cuts += strokes(f"M{96 + k * 58} 60 V340", 1.6, "#6a6a6a")
    for k in range(1, 5):
        cuts += strokes(f"M96 {60 + k * 56} H504", 1.6, "#6a6a6a")
    cuts += f'<path d="{blob(300, 200, 92, 66, 31, .1)}" fill="#cfcfcf"/>'
    cuts += f'<path d="{blob(300, 200, 60, 42, 32, .1)}" fill="#e6e6e6"/>'
    for (x, y) in ((356, 148), (378, 166), (366, 188), (392, 196), (384, 218), (404, 240)):
        cuts += f'<path d="{rrect(x, y, 16, 12, 2)}" fill="#111"/>'
    out = obj(d, cuts, "paper", 4)
    return out + corners(110, 74, 380, 252, 18) + acc(blob(300, 200, 104, 76, 31, .1), 2.4, "5 7")


def s_zenil():
    d = rrect(64, 96, 330, 206, 14)
    cuts = row([342, 99, 267, 176], 88, 116, 58, 14) + row([59, 342, 99], 88, 222, 58, 14)
    out = obj(d, cuts, "steatite", 16)
    out += acc("M64 199 H394", 2.6, "6 6")
    g = obj(circle(474, 200, 66), strokes("M432 214 A44 44 0 0 1 516 214", 3) +
            "".join(strokes(f"M{474 + 50 * math.cos(a):.1f} {200 + 50 * math.sin(a) + 14:.1f} L{474 + 40 * math.cos(a):.1f} {200 + 40 * math.sin(a) + 14:.1f}", 2.4)
                    for a in [math.pi + k * math.pi / 6 for k in range(7)]), "silver", 10)
    needle = f'<path d="M474 214 L{474 - 42 * math.cos(.18):.1f} {214 - 42 * math.sin(.18):.1f}" stroke="{ACC}" stroke-width="3.4" stroke-linecap="round"/><circle cx="474" cy="214" r="6" fill="{ACC}"/>'
    return out + g + needle


def s_cuneiform():
    a = obj(blob(176, 200, 122, 112, 41, .04, 16), wedge_row(84, 124, 5, 1) + wedge_row(84, 190, 5, 2) + wedge_row(84, 256, 4, 3), "clay", 16)
    b = obj(blob(426, 200, 122, 112, 42, .04, 16), wedge_row(334, 124, 5, 1) + wedge_row(334, 190, 5, 4) + wedge_row(334, 256, 4, 5), "clay", 16)
    link = acc("M232 116 Q300 78 368 116", 3) + acc("M360 105 l8 11 l-13 3", 3)
    odd = acc(rrect(400, 248, 46, 46, 8), 2.6, "5 6")
    return a + b + link + odd


def s_cattle():
    left = obj(blob(110, 268, 74, 34, 51, .08), "", "stone", 12)
    right = obj(blob(494, 268, 74, 34, 52, .08), "", "stone", 12)
    route = acc("M128 238 Q300 120 476 238", 3, "2 10")
    tok = obj(circle(300, 168, 66), bull(256, 152, 1.9), "steatite", 14)
    return left + right + route + tok + f'<circle cx="476" cy="238" r="7" fill="{ACC}"/>'


def s_rozanova():
    beam = obj(rrect(100, 292, 400, 22, 6), "", "stone", 10)
    pivot = obj("M300 314 L330 362 L270 362 Z", "", "stone", 6)
    ink = "".join(fake_marks(148, 166 + k * 36, 6, 16, 80 + k, 2.6) for k in range(3))
    real = obj(rrect(126, 146, 150, 140, 5), "", "paper", 4, over=f'<g>{ink.replace("#000", "#2b231c")}</g>')
    pale = "".join(fake_marks(348, 166 + k * 36, 6, 16, 80 + k, 2.6) for k in range(3))
    copy = obj(rrect(326, 146, 150, 140, 5), "", "paper", 4, over=f'<g>{pale.replace("#000", "#c4b59c")}</g>')
    return beam + pivot + real + copy + acc(rrect(318, 138, 166, 156, 8), 2.4, "5 7") + f'<circle cx="300" cy="303" r="5" fill="{ACC}"/>'


def s_stoicheia():
    d = "M110 70 H490 V230 L420 330 H110 Z"
    cuts = "".join(fake_marks(140, 96 + k * 46, 11, 20, 90 + k, 3.4) for k in range(4) if True)
    cuts += '<path d="M490 230 L420 330 H490 Z" fill="#000"/>'
    slab = obj("M110 70 H490 V330 H110 Z", cuts, "stone", 16)
    gap = acc("M490 230 L420 330 H490 Z", 2.6, "5 6")
    return slab + gap + acc("M446 300 h14 M468 290 v18 M476 276 h10", 3)


def sheaf(cx, base, h, lean):
    out = ""
    for k in range(-2, 3):
        tx = cx + k * 7 + lean
        out += strokes(f"M{cx + k * 2} {base} Q{cx + k * 4} {base - h * .5} {tx} {base - h}", 2.6)
        for j in range(4):
            yy = base - h + 6 + j * 9
            out += f'<ellipse cx="{tx - 4:.1f}" cy="{yy:.1f}" rx="3.4" ry="6" transform="rotate(-25 {tx - 4:.1f} {yy:.1f})" fill="#000"/>'
            out += f'<ellipse cx="{tx + 4:.1f}" cy="{yy:.1f}" rx="3.4" ry="6" transform="rotate(25 {tx + 4:.1f} {yy:.1f})" fill="#000"/>'
    return out + strokes(f"M{cx - 12} {base - h * .35} H{cx + 12}", 4)


def s_jognakhera():
    d = rrect(96, 74, 408, 252, 16)
    cuts = sheaf(190, 262, 150, -6) + sheaf(274, 262, 168, 0) + sheaf(358, 262, 150, 6)
    cuts += "".join(strokes(f"M118 {y} " + " ".join("q14 -8 28 0 t28 0" for _ in range(13)), 2.2, "#555") for y in (290, 306))
    out = obj(d, cuts, "terracotta", 16)
    return out + acc("M420 150 H486", 3.4) + acc("M474 140 l12 10 l-12 10", 3.4)


def s_kelley():
    cuts = ""
    for r_, y in enumerate((120, 172, 224, 276)):
        x = 112
        for k in range(3 + r_ % 2):
            cuts += f'<circle cx="{x + k * 26}" cy="{y}" r="9" fill="#333"/>'
        cuts += fake_marks(x + 120, y - 12, 4, 24, 110 + r_, 3)
    tab = obj(rrect(86, 92, 296, 214, 18), cuts, "clay", 16)
    book = obj(rrect(420, 120, 120, 164, 4), "", "paper", 10, over=strokes("M432 120 V284", 2, "#9b8f7a") + strokes("M448 160 H520 M448 176 H508", 2.4, "#2b231c"))
    return tab + book + acc("M394 200 H410", 2.6)


def s_rgr3():
    d = "M60 330 Q140 150 300 130 Q460 150 540 330 Z"
    cuts = ""
    for k, y in enumerate((180, 220, 260, 300)):
        cuts += f'<path d="M40 {y} Q300 {y - 26} 560 {y} V{y + 40} H40 Z" fill="{["#e0e0e0", "#c8c8c8", "#b0b0b0", "#989898"][k]}"/>'
    cuts += '<path d="M250 140 V300 H350 V140 Z" fill="#555"/>'
    mound = obj(d, cuts, "clay", 14)
    seal = square_seal(272, 226, 56, [342], animal=False, depth=6, sz=22)
    pin = f'<path d="M300 186 V214" stroke="{ACC}" stroke-width="3"/><circle cx="300" cy="182" r="8" fill="{ACC}"/>'
    return mound + seal + pin + acc("M366 214 H392 M366 288 H392 M380 214 V288", 2.6)


def s_gini():
    d = rrect(72, 76, 300, 248, 10)
    cuts = strokes("M72 196 H372 M222 76 V324", 10, "#777")
    for bx, by in ((86, 90), (150, 90), (86, 140), (150, 140), (236, 90), (300, 90), (236, 140), (300, 140),
                   (86, 210), (150, 210), (86, 260), (150, 260), (236, 210), (300, 210), (236, 260), (300, 260)):
        cuts += f'<path d="{rrect(bx, by, 56, 42, 3)}" fill="none" stroke="#000" stroke-width="3"/>'
    plan = obj(d, cuts, "steatite", 14)
    bars = "".join(f'<path d="{rrect(434 + k * 26, 140 + k * 26, 16, 160 - k * 26, 2)}" fill="#000"/>' for k in range(4))
    chart = obj(rrect(414, 116, 124, 200, 10), bars, "terracotta", 12)
    return plan + chart + acc("M440 132 L520 214", 3) + acc("M512 200 l8 14 l-15 1", 3)


def s_korovina():
    board = obj(rrect(56, 104, 250, 196, 16), "".join(fake_marks(84, 128 + k * 40, 8, 18, 120 + k, 3) for k in range(4)), "terracotta", 14)
    near = obj(rrect(340, 150, 92, 112, 4), "", "paper", 8)
    far = obj(rrect(476, 196, 70, 86, 4), "", "paper", 6, tilt="rotate(3 510 240)")
    return board + near + far + acc("M314 206 H332", 3) + acc("M314 230 Q400 330 486 290", 2.6, "4 8")


SCENES = {
    "restoration-2026": (s_restoration, "Illustration: a clay sealing with one sign broken away, the gap outlined and a candidate sign shown in it."),
    "voynich-2026": (s_voynich, "Illustration: an Indus seal and a manuscript page resting level on the same beam."),
    "dominik-2026": (s_dominik, "Illustration: two bar seals; one pair of signs joins, the other pairing never occurs and is crossed out."),
    "sigil-2026": (s_sigil, "Illustration: a seal with Indus signs beside a seal with invented symbols, marked as equal."),
    "lehs-2026": (s_lehs, "Illustration: stacked edition pages of an unread script with a crown medallion for kings’ names."),
    "nair-2026": (s_nair, "Illustration: a shield, an Indus seal and a tally tablet on one scale, with the seal marked between them."),
    "uae-seal-2026": (s_uae, "Illustration: a round Gulf-style seal with Indus signs, outlined as reported and not yet seen."),
    "kriger-2026": (s_kriger, "Illustration: three seals; the first and last carry the same text, linked by an arc."),
    "asi-2025": (s_asi, "Illustration: three clay tiles, one sign on each, bracketed as three days."),
    "protoelamite-2025": (s_protoelamite, "Illustration: a clay accounting tablet with number impressions and marks; one entry is outlined."),
    "dixit-2025": (s_dixit, "Illustration: a seal with signs and a bull, each found by a detection box."),
    "tyc-2025": (s_tyc, "Illustration: an Indus seal beside a mountain rock carved with a similar mark."),
    "tn-graffiti-2025": (s_pots, "Illustration: three clay pots, each scratched with a mark; one is outlined."),
    "proskouriakoff-1960": (s_maya, "Illustration: a carved stone stela with glyph blocks, three of them linked to points on a timeline."),
    "mahadevan-1977": (s_mahadevan, "Illustration: a catalogue page printed with a grid of Indus signs."),
    "parpola-1994": (s_parpola, "Illustration: a seal cut with the fish sign, linked to a carved star."),
    "fsw-2004": (s_fsw, "Illustration: a seal with a short text beside an emblem shield."),
    "rao-sproat": (s_entropy, "Illustration: a stone cut with two overlapping range bands and a marker where they overlap."),
    "laursen-2010": (s_laursen, "Illustration: a round Gulf seal and a square Indus seal with the same signs in a different order."),
    "snyder-luo": (s_snyder, "Illustration: a column of Indus signs linked to empty slots where a known related language would be."),
    "rakhigarhi-2019": (s_dna, "Illustration: a clay tile carved with a DNA double helix, one rung marked."),
    "mukhopadhyay-2019": (s_goods, "Illustration: a storage jar tied with a cord and sealed with a clay tag stamped with signs."),
    "desset-2022": (s_desset, "Illustration: a silver beaker with a band of marks, linked to a crown medallion."),
    "hexagon-2026": (s_hexagon, "Illustration: an aerial print of fields with a low mound at the centre, a village creeping over one edge, framed like a photo."),
    "zenil-2026": (s_zenil, "Illustration: a stone tablet with two rows of Indus signs and the line break marked, beside a gauge that has barely moved."),
    "cuneiform-2026": (s_cuneiform, "Illustration: two clay tablets with wedge marks linked by an arc; one mark on the right tablet is outlined."),
    "cattle-2026": (s_cattle, "Illustration: a round seal with a bull between two distant mounds, on a dotted route."),
    "rozanova-2026": (s_rozanova, "Illustration: a written page and a pale fitted copy resting level on one beam."),
    "stoicheia-2026": (s_stoicheia, "Illustration: an inscribed stone slab with a broken corner, the gap outlined and partly refilled."),
    "jognakhera-2026": (s_jognakhera, "Illustration: a clay tile carved with three sheaves of grain above a river, with an arrow pointing east."),
    "kelley-2026": (s_kelley, "Illustration: a clay accounting tablet with counting marks and signs beside a short book."),
    "rakhigarhi-rgr3-2026": (s_rgr3, "Illustration: a mound cut in section with a trench, a small square seal resting on a dated layer, marked with a pin."),
    "gini-2026": (s_gini, "Illustration: a city-block plan with houses of similar size beside a small chart of falling bars."),
    "korovina-2026": (s_korovina, "Illustration: a board with rows of marks; one stack of pages lies close to it and another further away."),
    "sign2vec-2022": (s_cluster, "Illustration: a clay slab with two groups of similar sign shapes, each circled."),
}


def scene_svg(key, seed):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{DEFS}</defs>'
            f'<rect width="{W}" height="{H}" fill="{GROUND}"/>{field(seed)}{SCENES[key][0]()}</svg>')


def main():
    items = json.loads((SITE / "news.json").read_text())["items"]
    keys = [i["id"] for i in items]
    missing = [k for k in keys if k not in SCENES]
    assert not missing, missing
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    keys = [k for k in keys if not only or k in only]
    shots = []
    with tempfile.TemporaryDirectory() as td:
        for k, key in enumerate(keys):
            page = Path(td) / f"{key}.html"
            page.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{GROUND}}}svg{{display:block}}</style></head>'
                            f'<body>{scene_svg(key, k + 1)}</body></html>')
            png = Path(td) / f"{key}.png"
            for attempt in range(3):
                try:
                    r = subprocess.run(["nice", "-n", "20", CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                                        f"--user-data-dir={td}/prof{k}", f"--window-size={W},{H}", "--virtual-time-budget=3000", "--allow-file-access-from-files",
                                        f"--screenshot={png}", page.as_uri()], capture_output=True, text=True, timeout=90)
                    break
                except subprocess.TimeoutExpired:
                    subprocess.run(["pkill", "-f", f"prof{k}"], capture_output=True)
                    print(key, "timed out, retrying", flush=True)
            if not png.exists():
                sys.exit(f"{key}: no screenshot\n{r.stderr[-800:]}")
            im = Image.open(png).convert("RGB")
            shots.append((key, im))
            print(key, im.size, flush=True)
        if "--sheet" in sys.argv:
            cols = 4
            sheet = Image.new("RGB", (cols * W, ((len(shots) + cols - 1) // cols) * H))
            for k, (key, im) in enumerate(shots):
                sheet.paste(im.resize((W, H)), ((k % cols) * W, (k // cols) * H))
            sheet.save("/tmp/oi_thumbs_sheet.png")
        if "--dry" in sys.argv:
            return
        OUT.mkdir(parents=True, exist_ok=True)
        for key, im in shots:
            im.save(OUT / f"{key}.webp", quality=84, method=6)
    data = json.loads((SITE / "news.json").read_text())
    for it in data["items"]:
        if it["id"] in keys:
            it["thumbnail_alt"] = SCENES[it["id"]][1]
    (SITE / "news.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
