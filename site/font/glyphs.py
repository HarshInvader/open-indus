"""Open Indus Display: every glyph's skeleton in one place.

Grid: cap height 0-100, y=0 is the cap line, y=100 the baseline (y grows down,
as in the wordmark SVGs). Each glyph is a single-weight stroke drawing:

    "X": (left, right, [svg path strings])

- paths use absolute M L H V C Z commands only; a lone "M x y" is a round dot.
- left / right are sidebearings in grid units, measured from the skeleton's
  centre-line extent (not the inked edge). Advance width =
  left + skeleton width + right. The builder prints every advance.
- O P E N I D U S R A are the wordmark letters from
  site/explore/wordmarks/build_wordmarks.py (SUBTLE set), kept as drawn.

Indus touches, kept few on purpose: the pointed almond bowl (O C G Q D 0 and
the parentheses), the rim ticks on U, the crossing tail on Q, the comma as a
short cut tick.

v0.5: there is no drawn lowercase. a-z, accented letters, curly quotes and extra
symbols come from Instrument Sans (OFL), taken by build_font.py from
raw/instrumentsans/; see README.md.
"""

STROKE = 11.9        # regular weight, grid units (v0.4: 10.5); = 76 font units
STROKE_BOLD = 20.0   # bold weight from the same skeletons (v0.4: 15); = 128 font units
DOT_SCALE = 1.4      # dots are a little larger than the stroke, so they hold up

# Sidebearing presets (grid units from the centre line).
ST = 16.5 # straight stem (v0.1: 12, v0.2: 18; matched to the borrowed lowercase)
RD = 15   # round / almond side (v0.1: 10)
OP = 11   # open side (v0.1: 7, v0.2: 12) (arm ends, diagonals meeting the cap or baseline at a point)
DG = 7    # diagonal side (v0.1: 4, v0.2: 8) that slopes away (A, V, W, X, Y)


def _f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _pt(p):
    return f"{_f(p[0])} {_f(p[1])}"


def _split(b, t0, t1):
    """Cubic segment b=(p0,p1,p2,p3) restricted to t in [t0, t1]."""
    def at(t):
        return tuple(sum(c * w for c, w in zip(cs, (
            (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3)))
            for cs in zip(*b))

    def d(t):
        return tuple(sum(c * w for c, w in zip(cs, (
            -3 * (1 - t) ** 2, 3 * (1 - t) ** 2 - 6 * (1 - t) * t,
            6 * (1 - t) * t - 3 * t * t, 3 * t * t))) for cs in zip(*b))
    p0, p3 = at(t0), at(t1)
    k = (t1 - t0) / 3
    d0, d1 = d(t0), d(t1)
    p1 = (p0[0] + d0[0] * k, p0[1] + d0[1] * k)
    p2 = (p3[0] - d1[0] * k, p3[1] - d1[1] * k)
    return p0, p1, p2, p3


def _c(b):
    return f"C{_pt(b[1])} {_pt(b[2])} {_pt(b[3])}"


def almond(cx, hw, top=0, bot=100):
    """The four quarter curves of the pointed almond (the wordmark O's logic).

    Returns dict of cubics: ul (top->left), ll (left->bottom),
    lr (bottom->right), ur (right->top). hw = half width.
    """
    k = hw * 24 / 29   # same control spread as the wordmark O
    h = bot - top
    m = top + h / 2
    a = h * 0.14
    b = h * 0.10
    T, B = (cx, top), (cx, bot)
    L, R = (cx - hw, m), (cx + hw, m)
    return {
        "ul": (T, (cx - k, top + a), (cx - hw, m - b), L),
        "ll": (L, (cx - hw, m + b), (cx - k, bot - a), B),
        "lr": (B, (cx + k, bot - a), (cx + hw, m + b), R),
        "ur": (R, (cx + hw, m - b), (cx + k, top + a), T),
    }


def almond_path(cx, hw, top=0, bot=100):
    q = almond(cx, hw, top, bot)
    return f"M{_pt(q['ul'][0])}" + "".join(_c(q[s]) for s in ("ul", "ll", "lr", "ur")) + "Z"


def _rev(b):
    return (b[3], b[2], b[1], b[0])


def open_almond(cx, hw, t_top, t_bot, top=0, bot=100):
    """C-shape: left half of the almond plus short runs into the right half."""
    q = almond(cx, hw, top, bot)
    top = _split(_rev(q["ur"]), 0, t_top)       # from top point, heading right/down
    bot = _split(q["lr"], 0, t_bot)             # from bottom point, heading right/up
    return (f"M{_pt(top[3])}" + _c(_rev(top)) + _c(q["ul"]) + _c(q["ll"]) + _c(bot)), q


def _c_shape():
    return open_almond(31, 29, 0.55, 0.5)[0]


def _g_shape():
    q = almond(31, 29)
    top = _split(_rev(q["ur"]), 0, 0.55)
    lr = _split(q["lr"], 0, 0.86)
    end = lr[3]
    return (f"M{_pt(top[3])}" + _c(_rev(top)) + _c(q["ul"]) + _c(q["ll"]) + _c(lr)
            + f"V{_f(end[1])}H{_f(end[0] - 21)}")


def _rot180(path, w):
    """Rotate a path of absolute M/L/H/V/C/Z commands by 180 deg in a w x 100 box."""
    import re
    out, toks = [], re.findall(r"[MLHVCZ]|-?\d*\.?\d+", path)
    i, cmd = 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        if cmd == "H":
            out.append(_f(w - float(t)))
            i += 1
        elif cmd == "V":
            out.append(_f(100 - float(t)))
            i += 1
        else:
            out.append(f"{_f(w - float(t))} {_f(100 - float(toks[i + 1]))}")
            i += 2
    return " ".join(out).replace(" ,", ",")


_SIX = "M37 3C17 16 1 40 1 68C1 89 10 100 22 100C35 100 43 89 43 72C43 55 34 45 22 45C13 45 6 50 2 57"

GLYPHS = {
    # ---------------------------------------------------------------- capitals
    "A": (DG, DG, ["M0 100L27 0L54 100", "M10 64H44"]),
    "B": (ST, RD, ["M0 48H20C35 48 41 37 41 24C41 11 35 0 20 0H0V100H23C40 100 47 88 47 74C47 60 40 48 23 48H0"]),
    "C": (RD, OP, [_c_shape()]),
    "D": (ST, RD, ["M0 0V100H8C38 92 52 70 52 50C52 30 38 8 8 0H0"]),
    "E": (ST, OP, ["M42 0H0V100H42", "M0 50H34"]),
    "F": (ST, OP, ["M42 0H0V100", "M0 50H34"]),
    "G": (RD, ST - 2, [_g_shape()]),
    "H": (ST, ST, ["M0 0V100", "M46 0V100", "M0 50H46"]),
    "I": (ST, ST, ["M0 0V100"]),
    "J": (OP, ST, ["M34 0V68C34 88 26 100 16 100C7 100 2 95 0 87"]),
    "K": (ST, DG + 2, ["M0 0V100", "M44 0L0 58", "M15 41L46 100"]),
    "L": (ST, OP - 2, ["M0 0V100H40"]),
    "M": (ST, ST, ["M0 100V0L29 70L58 0V100"]),
    "N": (ST, ST, ["M0 100V0L50 100V0"]),
    "O": (RD, RD, ["M31 0C7 14 2 40 2 50C2 60 7 86 31 100C55 86 60 60 60 50C60 40 55 14 31 0Z"]),
    "P": (ST, RD, ["M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0"]),
    "Q": (RD, RD, ["M31 0C7 14 2 40 2 50C2 60 7 86 31 100C55 86 60 60 60 50C60 40 55 14 31 0Z",
                   "M40 78L60 108"]),
    "R": (ST, DG + 2, ["M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0", "M22 52L46 100"]),
    "S": (RD, RD, ["M45 14C40 5 32 0 23 0C10 0 2 8 2 23C2 52 46 44 46 74C46 91 36 100 22 100C12 100 4 95 0 86"]),
    "T": (OP - 2, OP - 2, ["M0 0H48", "M24 0V100"]),
    "U": (OP - 2, OP - 2, ["M0 0V58C0 84 12 100 25 100C38 100 50 84 50 58V0", "M0 0H-7", "M50 0H57"]),
    "V": (DG, DG, ["M0 0L26 100L52 0"]),
    "W": (DG, DG, ["M0 0L17 100L34 30L51 100L68 0"]),
    "X": (DG + 1, DG + 1, ["M0 0L48 100", "M48 0L0 100"]),
    "Y": (DG, DG, ["M0 0L25 52L50 0", "M25 52V100"]),
    "Z": (OP, OP, ["M2 0H46L0 100H48"]),
    # ---------------------------------------------------------------- digits
    "zero": (RD, RD, [almond_path(23, 22)]),   # figure width, no inner mark (v0.4 tick read as an eye); O is wider (62)
    "one": (OP, OP, ["M3 24L23 0V100", "M5 100H41"]),   # flag + foot: never I or l
    "two": (OP, OP, ["M2 22C4 8 13 0 23 0C36 0 44 9 44 24C44 46 18 64 0 100H46"]),
    "three": (OP, RD, ["M3 0H42L19 42C35 42 44 54 44 70C44 89 34 100 21 100C12 100 4 95 0 88"]),
    "four": (OP, OP, ["M32 100V0L0 68H46"]),
    "five": (OP, RD, ["M41 0H6L3 44C9 40 15 38 22 38C36 38 44 50 44 68C44 88 34 100 21 100C12 100 4 95 0 88"]),
    "six": (RD, RD, [_SIX]),
    "seven": (OP, OP, ["M0 0H44L14 100"]),
    "eight": (RD, RD, ["M22 46C11 46 4 38 4 24C4 9 12 0 22 0C32 0 40 9 40 24C40 38 33 46 22 46Z",
                       "M22 46C8 46 0 58 0 73C0 90 9 100 22 100C35 100 44 90 44 73C44 58 36 46 22 46Z"]),
    "nine": (RD, RD, [_rot180(_SIX, 44)]),
    # ---------------------------------------------------------------- punctuation
    "period": (ST, ST, ["M0 98"]),
    "comma": (ST, ST, ["M4 98", "M4 98L0 114"]),
    "colon": (ST, ST, ["M0 40", "M0 98"]),
    "semicolon": (ST, ST, ["M4 40", "M4 98", "M4 98L0 114"]),
    "exclam": (ST, ST, ["M0 0V68", "M0 98"]),
    "question": (OP, OP, ["M0 18C2 7 10 0 21 0C33 0 41 8 41 22C41 35 33 41 26 47C22 51 20 55 20 68", "M20 98"]),
    "hyphen": (OP, OP, ["M0 58H26"]),
    "endash": (OP, OP, ["M0 58H50"]),
    "quotesingle": (ST, ST, ["M0 0V26"]),
    "quotedbl": (ST, ST, ["M0 0V26", "M14 0V26"]),
    "ampersand": (OP, DG, ["M50 100L13 42C7 33 5 27 5 20C5 8 12 0 21 0C30 0 36 7 36 16C36 28 27 34 16 44"
                           "C6 53 0 61 0 74C0 90 10 100 23 100C37 100 46 89 50 60"]),
    "slash": (DG, DG, ["M36 -4L0 104"]),
    "parenleft": (OP + 3, OP, ["M22 -6C8 14 2 36 2 50C2 64 8 86 22 106"]),
    "parenright": (OP, OP + 3, ["M0 -6C14 14 20 36 20 50C20 64 14 86 0 106"]),
}

# Text punctuation taken from Instrument Sans instead of our drawings (ours were
# heavy round dots and ticks beside its flat-cut lowercase). The drawings stay
# above, unused, in case display settings want them back.
FROM_SOURCE = ["period", "comma", "colon", "semicolon", "exclam", "question",
               "quotesingle", "quotedbl", "hyphen", "endash"]

# Space advance in grid units (wordmark word gap was 50 centre-to-centre).
SPACE = 30   # unused since v0.6: the word space follows Instrument Sans (see build_font.py)

CHARS = {
    **{c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
    "6": "six", "7": "seven", "8": "eight", "9": "nine",
    ".": "period", ",": "comma", ":": "colon", ";": "semicolon", "!": "exclam",
    "?": "question", "-": "hyphen", "–": "endash", "'": "quotesingle",
    '"': "quotedbl", "&": "ampersand", "/": "slash",
    "(": "parenleft", ")": "parenright", " ": "space", " ": "space",
}

# Kerning pairs in grid units (negative = tighter). Left glyph groups -> right glyph groups.
# Optical overshoot: which glyphs' round/pointed extremes pass the cap line (t)
# and/or the baseline (b), and by how much (grid units).
OVERSHOOT_AMT = 1.6
OVERSHOOT = {
    "O": "tb", "Q": "tb", "C": "tb", "G": "tb", "S": "tb", "zero": "tb", "six": "tb",
    "eight": "tb", "nine": "tb", "U": "b", "J": "b", "three": "b", "five": "b", "two": "t",
    "question": "t", "ampersand": "tb",
}
# Horizontal strokes are drawn with an elliptical pen: horizontals = stroke / NIB.
NIB = 1.10

# Optical weight: long pointed curves look lighter than stems at the same
# thickness, so the almond glyphs use a round pen (no thinning near the points)
# and a slightly heavier stroke.
ROUND_PEN = {"O", "Q", "C", "G", "D", "zero", "parenleft", "parenright"}
WEIGHT = {"O": 1.04, "Q": 1.04, "C": 1.04, "G": 1.04, "D": 1.02}

# A path starting with "~" is a fine mark, drawn at FINE x the stroke (zero's inner tick).
FINE = 0.55

# Figures are tabular: one advance (grid units, before bold extra), ink centred.
DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
DIGIT_ADV = 70

KERN = [  # re-tuned for the v0.2 spacing; v0.4 adds round capitals before lowercase
    (["O", "Q", "D"], ["a", "c", "d", "e", "g", "o", "q", "p", "n", "m", "r", "u", "s", "x", "v", "w", "y", "z", "i", "j", "b", "h", "k", "l", "f", "t"], -4),
    (["C", "G"], ["a", "c", "d", "e", "g", "o", "q", "u"], -2),
    (["A"], ["V", "Y", "T"], -9), (["A"], ["W"], -6),
    (["V", "Y", "T"], ["A"], -9), (["W"], ["A"], -6),
    (["L"], ["T", "V", "Y"], -11), (["L"], ["W"], -8), (["L"], ["quotesingle", "quotedbl"], -14),
    (["P", "F", "T"], ["period", "comma"], -11), (["V", "Y", "W"], ["period", "comma"], -8),
    (["T"], ["O", "C", "G", "Q"], -4), (["O", "Q", "D"], ["T", "V", "Y"], -4),
    (["P"], ["A"], -7), (["F"], ["A"], -6),
    (["T"], ["a", "c", "d", "e", "g", "o", "q", "s"] + ["u", "r", "y", "v", "w", "z", "x", "m", "n", "p"], -10),
    (["V", "W", "Y"], ["a", "c", "d", "e", "g", "o", "q", "s"], -7), (["F", "P"], ["a", "c", "d", "e", "g", "o", "q", "s"], -5),
    (["r"], ["period", "comma"], -9), (["v", "w", "y"], ["period", "comma"], -7),
    (["f"], ["period", "comma"], -6),
]
