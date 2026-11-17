# Open Indus Display and Open Indus Text (v0.7, direction study)

Two cuts for the Open Indus site, built by one script (`build_font.py`). The
family names live in `FAMILY` and `FAMILY_TEXT` (the display one may become
"Read Indus").

| Cut | Files | Use it for |
| --- | --- | --- |
| Open Indus Display | `OpenIndus-Regular/Bold.ttf/.woff2` | titles, the wordmark, all-caps lines |
| Open Indus Text | `OpenIndusText-Regular/Bold.ttf/.woff2` | sentences, paragraphs, interface labels (nav, buttons, captions) |

Display has our drawn capitals and figures (the almond O and 0). Next to
lowercase at small sizes the almond O reads like a zero ("Overview", "Our"), so
mixed-case text uses Text instead.

    @font-face { font-family: "Open Indus Display"; src: url("OpenIndus-Regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
    @font-face { font-family: "Open Indus Display"; src: url("OpenIndus-Bold.woff2") format("woff2"); font-weight: 700; font-display: swap; }
    @font-face { font-family: "Open Indus Text"; src: url("OpenIndusText-Regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
    @font-face { font-family: "Open Indus Text"; src: url("OpenIndusText-Bold.woff2") format("woff2"); font-weight: 700; font-display: swap; }

## Open Indus Text

Everything in it is Instrument Sans (wght 400 / wdth 100 Regular, wght 650 /
wdth 100 Bold): capitals, figures, & / ( ), lowercase, accents, punctuation,
symbols and kerning, outlines unchanged. What it adds: the same +12 unit body
spacing and word space as Display, and the dot letters Instrument Sans lacks
(ṣ ṭ ḍ ṇ ṛ ḷ ṃ ḥ ṅ and capitals, built from its own parts). A very slightly
pointed O / Q / 0 was tried (`TEXT_POINT` in `build_font.py`, now 0) and left
out: it cannot be seen at 14-28px and only adds overshoot.

## Open Indus Display

### What came from where

- **Capitals A-Z, figures 0-9, & / ( )**: drawn for this project as stroke
  skeletons in `glyphs.py` and expanded to outlines by `build_font.py`.
- **From Instrument Sans** (Copyright 2022 The Instrument Sans Project Authors,
  https://github.com/Instrument/instrument-sans; SIL Open Font License 1.1),
  downloaded from the google/fonts repository (`ofl/instrumentsans`) into
  `raw/instrumentsans/`. Instanced at wght 400 / wdth 100 (Regular) and
  wght 650 / wdth 100 (Bold); outlines used unchanged:
  - lowercase a-z and accented lowercase (Latin-1 plus ā ē ī ō ū ś);
  - text punctuation . , : ; ! ? ' " - – and curly quotes;
  - symbols % + _ · × → ← ↑ ↓ @ # $ * < = > [ ] \ ^ ` { | } ~ — … • € £ © ® °;
  - its kerning for every pair that involves one of these glyphs.
- **Built here from Instrument Sans parts**: accented capitals (our capital plus
  its accent), ≈ (two of its tildes), and the dot letters ṣ ṭ ḍ ṇ ṛ ḷ ṃ ḥ ṅ and
  their capitals (base letter plus its dot accent), which Instrument Sans lacks.

Dosis, used for the lowercase in v0.3-v0.4 (including the l with a foot), has
been removed completely; nothing from it is left in the font.

## Spacing (both cuts)

- Every glyph taken from Instrument Sans (in Text, every glyph) gets 12 extra units of advance
  (6 left, 6 right; `BODY_TRACK` in `build_font.py`), so text sizes are looser
  than plain Instrument Sans. Kerning is unchanged.
- The word space is Instrument Sans's space plus the same 12 units
  (212 Regular, 204 Bold).
- Size-based tracking for the site's CSS (the specimen uses the same rules):

      /* mixed case and running text */
      letter-spacing: clamp(-0.012em, calc(0.94px - 0.0214em), 0.05em);
      /* all-caps lines */
      letter-spacing: clamp(0.02em, 1.4px, 0.04em);

  This gives about +0.046em at 14px, +0.037em at 16px, +0.031em at 18px,
  +0.012em at 28px and -0.012em at 64px and above.

## Licence

Because both cuts include Instrument Sans outlines, they are distributed under the
SIL Open Font License 1.1; see `OFL.txt` (copyright notices at the top). The
font names do not use any Reserved Font Name ("Instrument Sans" is not
reserved, and the name is not used anyway).

## Build

From the project root:

    .venv/bin/python -I site/font/build_font.py   # writes both cuts, .ttf and .woff2
    sh site/font/shoot.sh                         # rebuilds both cuts and screenshots specimen.html
