#!/usr/bin/env python3
"""Draws the OPEN INDUS wordmark studies as single-colour stroked SVG.

Every letter is a centre-line path on a 100-unit cap height (y=0 top, y=100
baseline). Strokes are drawn in currentColor with one even weight per variant,
the way signs are cut into a seal. Run: python3 build_wordmarks.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Fish mark from site/assets/logo-mark.svg (32-unit box, stroke 2.4).
FISH = [
    "M16 3.56C9.18 9.28 8.74 16.32 16 23.14L21.05 27.88",
    "M16 3.56C22.82 9.28 23.26 16.32 16 23.14L10.95 27.88",
    "M11.71 17.44L8.67 19.82M20.29 17.44L23.33 19.82",
]
FISH_X0, FISH_X1, FISH_Y0, FISH_Y1 = 8.67, 23.33, 3.56, 27.88

# ---------------------------------------------------------------- glyph sets
# Each glyph: (advance width of the drawing, [paths]). Paths in local x from 0.

SUBTLE = {  # geometric sans; only O, D (almond bowl) and U (jar rim) carry the script
    "w": 10.5, "gap": 21, "space": 50,
    "O": (62, ["M31 0C7 14 2 40 2 50C2 60 7 86 31 100C55 86 60 60 60 50C60 40 55 14 31 0Z"]),
    "P": (46, ["M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0"]),
    "E": (42, ["M42 0H0V100H42", "M0 50H34"]),
    "N": (50, ["M0 100V0L50 100V0"]),
    "I": (0, ["M0 0V100"]),
    "D": (52, ["M0 0V100H8C38 92 52 70 52 50C52 30 38 8 8 0H0"]),
    "U": (50, ["M0 0V58C0 84 12 100 25 100C38 100 50 84 50 58V0", "M0 0H-7", "M50 0H57"]),
    "S": (46, ["M45 14C40 5 32 0 23 0C10 0 2 8 2 23C2 52 46 44 46 74C46 91 36 100 22 100C12 100 4 95 0 86"]),
    "R": (46, ["M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0", "M22 52L46 100"]),
    "A": (54, ["M0 100L27 0L54 100", "M10 64H44"]),
}

MEDIUM = {  # each stroke a separate cut, as on the sign drawings; almond O, jar U
    "w": 11, "gap": 20, "space": 48,
    "O": (50, ["M25 0C4 22 0 40 0 50C0 60 4 78 25 100C46 78 50 60 50 50C50 40 46 22 25 0Z"]),
    "P": (42, ["M0 0V100", "M17 0C36 2 42 14 42 27C42 40 36 52 17 54"]),
    "E": (40, ["M0 0V100", "M17 0H40", "M17 50H34", "M17 100H40"]),
    "N": (46, ["M0 19V100", "M0 0L46 100", "M46 0V81"]),
    "I": (0, ["M0 0V100"]),
    "D": (48, ["M0 0V100", "M17 0C38 12 48 32 48 50C48 68 38 88 17 100"]),
    "U": (46, ["M0 0V56C0 80 14 94 23 100C32 94 46 80 46 56V0", "M0 0H-11", "M46 0H57"]),
    "S": (42, ["M41 12C37 4 30 0 21 0C8 0 1 8 1 21C1 30 6 36 21 50C36 64 42 70 42 79C42 92 34 100 21 100C11 100 4 96 0 88"]),
    "R": (42, ["M0 0V100", "M17 0C36 2 42 14 42 27C42 40 36 52 17 54", "M27 66L42 100"]),
    "A": (48, ["M0 100L24 0L48 100", "M17 64H31"]),
}

BOLD = {  # strongly sign-like: fish-body O, jar U, numeral strokes, crossed apex
    "w": 13, "gap": 22, "space": 50,
    # O: the fish body; two arcs meet in a point at the top and cross near the foot
    "O": (50, ["M25 0C3 24 0 44 0 56C0 70 8 82 36 108", "M25 0C47 24 50 44 50 56C50 70 42 82 14 108"]),
    "P": (44, ["M0 0V100", "M18 0C40 4 44 20 44 27C44 36 40 50 18 54"]),
    # E: stem plus three short strokes set apart from it, as in the numeral signs
    "E": (40, ["M0 0V100", "M18 0H40", "M18 50H35", "M18 100H40"]),
    "N": (46, ["M0 20V100", "M0 0L46 100", "M46 0V80"]),
    # I: one stroke with short bars at top and foot
    "I": (22, ["M11 0V100", "M0 0H22", "M0 100H22"]),
    # D: stem plus the half almond of the fish body, cut apart
    "D": (46, ["M0 0V100", "M18 0C40 14 46 36 46 50C46 64 40 86 18 100"]),
    # U: the jar sign M342, pointed base and two rim ticks a side
    "U": (46, ["M0 0V52C0 74 12 90 23 100C34 90 46 74 46 52V0", "M0 0H-11", "M0 18H-11", "M46 0H57", "M46 18H57"]),
    # S: angular S with two pointed turns
    "S": (42, ["M41 8C33 -2 12 -3 3 14L39 86C30 103 9 102 1 92"]),
    "R": (44, ["M0 0V100", "M18 0C40 4 44 20 44 27C44 36 40 50 18 54", "M28 66L44 100"]),
    # A: the legs cross at the top and run on, the fish tail turned over
    "A": (50, ["M0 100L31 -12", "M50 100L19 -12", "M16 62H34"]),
}

VARIANTS = {"subtle": SUBTLE, "medium": MEDIUM, "bold": BOLD}


def layout(glyphs, text):
    """Return (paths with transforms, total width) for a line of text."""
    out, x = [], 0.0
    for ch in text:
        if ch == " ":
            x += glyphs["space"] - glyphs["gap"]
            continue
        adv, paths = glyphs[ch]
        out.append(f'<g transform="translate({x:.1f} 0)"><path d="{" ".join(paths)}"/></g>')
        x += adv + glyphs["gap"]
    return out, x - glyphs["gap"]


def svg(variant, text="OPEN INDUS", with_fish=True, label=None):
    g = VARIANTS[variant]
    sw = g["w"]
    parts, width = layout(g, text)
    pad = sw / 2 + 12  # room for overshoots and round caps
    fish = ""
    x0 = 0.0
    if with_fish:
        h = 128.0
        s = h / (FISH_Y1 - FISH_Y0)
        fw = (FISH_X1 - FISH_X0) * s
        tx, ty = -FISH_X0 * s, -14 - FISH_Y0 * s
        fish = (f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})" '
                f'stroke-width="{sw / s:.3f}"><path d="{" ".join(FISH)}"/></g>')
        x0 = fw + 40
    vb_x, vb_y = -pad, -14 - pad
    vb_w = x0 + width + 2 * pad
    vb_h = 128 + 2 * pad
    word = f'<g transform="translate({x0:.1f} 0)">{"".join(parts)}</g>'
    title = label or f"{text.title()} wordmark, {variant} study"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}" '
            f'fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" role="img" aria-label="{title}"><title>{title}</title>'
            f'{fish}{word}</svg>\n')


def main():
    for v in VARIANTS:
        open(os.path.join(HERE, f"open-indus-{v}.svg"), "w").write(svg(v))
        open(os.path.join(HERE, f"open-indus-{v}-wordonly.svg"), "w").write(svg(v, with_fish=False))
    for v in VARIANTS:
        open(os.path.join(HERE, f"read-indus-{v}.svg"), "w").write(svg(v, "READ INDUS"))
    open(os.path.join(HERE, "alphabet.svg"), "w").write(alphabet())


def alphabet():
    rows, y = [], 0
    for v in VARIANTS:
        parts, w = layout(VARIANTS[v], "O P E N I D U S R A")
        rows.append(f'<g transform="translate(0 {y})" stroke-width="{VARIANTS[v]["w"]}">{"".join(parts)}</g>')
        y += 170
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-30 -30 1000 {y}" fill="none" '
            f'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" role="img" '
            f'aria-label="Letter studies, subtle, medium and bold"><title>Letter studies</title>{"".join(rows)}</svg>\n')


def sized(svg_text, cap_px):
    """Inline an SVG at a given cap height in px; width scales down to fit its container."""
    vb = svg_text.split('viewBox="')[1].split('"')[0].split()
    w = float(vb[2]) * cap_px / 100
    return svg_text.replace("<svg ", f'<svg style="width:{w:.0f}px" ', 1)


def glyph(variant, ch):
    g = VARIANTS[variant]
    adv, paths = g[ch]
    pad = g["w"] / 2 + 14
    return (f'<svg viewBox="{-pad - 12:.1f} {-pad:.1f} {adv + 2 * pad + 24:.1f} {100 + 2 * pad:.1f}" fill="none" '
            f'stroke="currentColor" stroke-width="{g["w"]}" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true"><path d="{" ".join(paths)}"/></svg>')


SOURCES = [  # letter, sign drawing it borrows from, what it borrows
    ("O", "M373", "the pointed almond, as in the fish body"),
    ("P", "M59", "half of the fish head, cut apart from the stem"),
    ("E", "M176", "a stem with short strokes beside it"),
    ("N", "M124", "a diagonal meeting a stroke at a point"),
    ("I", "M86", "one even stroke"),
    ("D", "M304", "a stem and an almond-half bowl"),
    ("U", "M342", "the jar: pointed base and rim ticks"),
    ("S", "M119", "a stroke with two turns, end to end"),
    ("R", "M125", "P with a forked leg"),
    ("A", "M134", "the chevron"),
]

NOTES = {
    "medium": ("Medium · separate cuts", "Each stroke is its own cut and stops short of the next, the way strokes sit in the sign drawings. Almond O, almond-half bowls, the jar U with one rim tick a side. Recommended."),
    "subtle": ("Subtle · a clean sans", "A narrow geometric sans with continuous strokes. Only the almond O and D and the jar's rim ticks on U come from the script."),
    "bold": ("Bold · strongly sign-like", "The fish body for O (two arcs that cross at the foot), the jar U with two ticks a side, an angular S and an A whose legs cross and run on. Most character, least calm at small sizes."),
}


def page():
    files = {v: open(os.path.join(HERE, f"open-indus-{v}.svg")).read() for v in VARIANTS}
    reads = {v: open(os.path.join(HERE, f"read-indus-{v}.svg")).read() for v in VARIANTS}
    order = ["medium", "subtle", "bold"]
    rows = []
    for rank, v in enumerate(order, 1):
        title, note = NOTES[v]
        panels = ""
        for theme in ("light", "dark"):
            panels += (f'<div class="panel {theme}"><p class="sz">Header · 20 px cap height</p>{sized(files[v], 20)}'
                       f'<p class="sz">64 px</p>{sized(files[v], 64)}'
                       f'<p class="sz">200 px (shrinks to fit narrow screens)</p>{sized(files[v], 200)}</div>')
        letters = "".join(f'<span class="gl">{glyph(v, c)}</span>' for c in "OPENIDUSRA")
        rows.append(f'<section class="variant" aria-labelledby="v-{v}"><div class="vh"><span class="rank">{rank}</span>'
                    f'<div><h2 id="v-{v}">{title}</h2><p>{note}</p></div></div>'
                    f'<div class="letters" aria-label="Letters O P E N I D U S R A, {v} study">{letters}</div>'
                    f'{panels}<p class="files">Files: <a href="wordmarks/open-indus-{v}.svg">lockup</a> · '
                    f'<a href="wordmarks/open-indus-{v}-wordonly.svg">word only</a> · '
                    f'<a href="wordmarks/read-indus-{v}.svg">Read Indus</a></p></section>')
    src = "".join(f'<li><span class="gl">{glyph("medium", c)}</span><img src="signs/{m}.png" alt="sign {m}" width="56" height="56">'
                  f'<span class="why"><b>{c} ← {m}</b>{why}</span></li>' for c, m, why in SOURCES)
    read = "".join(f'<div class="panel {t}"><p class="sz">If the name becomes Read Indus · medium study, 64 px</p>{sized(reads["medium"], 64)}'
                   f'<p class="sz">200 px</p>{sized(reads["medium"], 200)}</div>' for t in ("light", "dark"))
    html = PAGE.replace("{{SOURCES}}", src).replace("{{ROWS}}", "".join(rows)).replace("{{READ}}", read)
    open(os.path.join(HERE, "..", "wordmark.html"), "w").write(html)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wordmark studies · Open Indus</title>
<!-- Generated by wordmarks/build_wordmarks.py; edit the script, not this file. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root { --bg: #f1efea; --ink: #1c1d1f; --ink-2: #4b4d52; --rule: rgba(28,29,31,.12); --light: #f7f5f0; --dark: #15171b; --light-ink: #1c1d1f; --dark-ink: #ece9e2; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #101215; --ink: #ece9e2; --ink-2: #b8b5ae; --rule: rgba(236,233,226,.12); color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #101215; --ink: #ece9e2; --ink-2: #b8b5ae; --rule: rgba(236,233,226,.12); color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 17px/1.6 "Hanken Grotesk", "Helvetica Neue", Arial, sans-serif; overflow-x: hidden; }
.wrap { width: min(1240px, 100% - 32px); margin: 0 auto; padding: 56px 0 96px; }
a { color: inherit; }
.back { font-weight: 600; font-size: 15px; }
h1 { font-size: clamp(36px, 5vw, 60px); line-height: 1.02; letter-spacing: -.02em; margin: 20px 0 14px; max-width: 18ch; }
.lead { max-width: 62ch; color: var(--ink-2); margin: 0; }
h2 { font-size: 24px; line-height: 1.2; margin: 0 0 4px; }
.sources { list-style: none; margin: 32px 0 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.sources li { display: grid; grid-template-columns: 44px 56px minmax(0, 1fr); gap: 12px; align-items: center; padding: 12px; border: 1px solid var(--rule); border-radius: 12px; }
.sources .gl svg { height: 48px; width: auto; display: block; }
.sources img { border-radius: 8px; background: #fff; }
.why { font-size: 14px; color: var(--ink-2); line-height: 1.35; }
.why b { display: block; color: var(--ink); font-size: 15px; }
.variant { margin-top: 72px; padding-top: 32px; border-top: 1px solid var(--rule); }
.vh { display: flex; gap: 16px; align-items: flex-start; }
.vh p { margin: 0; color: var(--ink-2); max-width: 68ch; }
.rank { flex: none; width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; font-weight: 700; border: 1.5px solid currentColor; }
.letters { display: flex; flex-wrap: wrap; gap: 6px 2px; margin: 24px 0; }
.letters .gl svg { height: 64px; width: auto; display: block; }
.panel { border-radius: 16px; padding: 28px; margin-top: 12px; overflow: hidden; }
.panel.light { background: var(--light); color: var(--light-ink); box-shadow: inset 0 0 0 1px rgba(0,0,0,.06); }
.panel.dark { background: var(--dark); color: var(--dark-ink); }
.panel svg { display: block; max-width: 100%; height: auto; }
.sz { font-size: 13px; font-weight: 600; opacity: .7; margin: 22px 0 10px; }
.sz:first-child { margin-top: 0; }
.files { font-size: 14px; color: var(--ink-2); }
.read { margin-top: 72px; padding-top: 32px; border-top: 1px solid var(--rule); }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="index.html">All directions</a>
  <h1>Open Indus, lettered with the script's strokes</h1>
  <p class="lead">Latin capitals drawn by hand as single even-weight strokes, the way signs are cut into a seal. Each letter borrows one construction from a real sign drawing. They are Latin letters wearing the script's stroke logic, not Indus signs standing in for sounds. Three strengths, ranked; the fish mark is the one from the live site, drawn at the same stroke weight.</p>
  <h2 style="margin-top:40px">Where each letter comes from</h2>
  <ul class="sources">{{SOURCES}}</ul>
  {{ROWS}}
  <section class="read" aria-labelledby="h-read"><h2 id="h-read">Read Indus</h2><p class="lead">The two extra letters are R (the P bowl with a cut leg) and A (the chevron with a cut bar). Drawn in all three studies; shown here in the recommended one.</p>{{READ}}</section>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
    page()
