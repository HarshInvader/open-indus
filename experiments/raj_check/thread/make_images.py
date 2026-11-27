"""Thread images for the raj_check write-up (1200x675 PNG). Numbers from RESULTS.md / out/."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os
D = os.path.dirname(os.path.abspath(__file__))
SURF, INK, INK2, BLUE, GRAY, ORANGE = '#fcfcfb', '#0b0b0b', '#52514e', '#2a78d6', '#b9b8b2', '#eb6834'
plt.rcParams.update({'font.family': ['Helvetica Neue', 'Arial Unicode MS', 'DejaVu Sans'], 'font.size': 15, 'text.color': INK, 'axes.edgecolor': GRAY})
def fig():
    f = plt.figure(figsize=(12, 6.75), dpi=100, facecolor=SURF); return f
def foot(f, t='Open Indus · reran the preprint’s own code on its own data · github.com/HarshInvader/open-indus · experiments/raj_check'):
    f.text(0.04, 0.035, t, fontsize=11, color=INK2)

# 1. scores
f = fig(); ax = f.add_axes([0.33, 0.17, 0.6, 0.6], facecolor=SURF)
rows = [('Old Tamil (their headline)', 223.0, BLUE), ('Tamil, picture words put on\nrandom wrong signs (50 runs)', 223.7, BLUE),
        ('Japanese family names\n(no link to the Indus)', 134.5, ORANGE), ('Vedic Sanskrit', -13.3, GRAY), ('Tamil on fake, meaningless seals', -28.5, GRAY)]
y = list(range(len(rows)))[::-1]
for yi, (lab, v, c) in zip(y, rows):
    ax.barh(yi, v, color=c, height=0.62)
    ax.text(v + (6 if v >= 0 else -6), yi, f'{v:+.0f}'.replace('-', '−'), va='center', ha='left' if v >= 0 else 'right', fontsize=16, color=INK, fontweight='bold')
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=14, color=INK)
ax.axvline(0, color=INK2, lw=1); ax.set_xlim(-80, 270)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='y', length=0); ax.tick_params(axis='x', colors=INK2, labelsize=12)
ax.set_xlabel('How much better real names fit than scrambled names (their score; 0 = chance)', color=INK2, fontsize=12)
f.text(0.04, 0.9, 'Their test doesn’t care what the signs depict', fontsize=26, fontweight='bold')
f.text(0.04, 0.835, 'Same code, same seals. Shuffling the pictures changes nothing; a language with no Indus link scores 60% of Tamil.', fontsize=14, color=INK2)
foot(f); f.savefig(f'{D}/1_scores.png', facecolor=SURF); plt.close(f)

# 2. copies
f = fig()
f.text(0.04, 0.9, 'The “object marks” are mostly copies', fontsize=26, fontweight='bold')
f.text(0.04, 0.835, 'Copper tablets were made in sets with the same inscription. Count each text once and the signal fades.', fontsize=14, color=INK2)
cards = [('“copper” sign on copper tablets', '21', 'tablet faces', '3', 'distinct texts', 'p = 6×10⁻¹¹  →  p = 0.19'),
         ('“armlet” sign on bangles', '10', 'bangle faces', '4', 'distinct texts', 'p = 1.5×10⁻⁷  →  p = 0.017*')]
for i, (h, a, al, b, bl, p) in enumerate(cards):
    x0 = 0.04 + i * 0.47
    f.patches.append(FancyBboxPatch((x0, 0.2), 0.43, 0.55, boxstyle='round,pad=0,rounding_size=0.015', transform=f.transFigure, fc='white', ec=GRAY, lw=1))
    f.text(x0 + 0.025, 0.69, h, fontsize=17, fontweight='bold')
    f.text(x0 + 0.025, 0.45, a, fontsize=64, fontweight='bold', color=BLUE); f.text(x0 + 0.025, 0.4, al, fontsize=14, color=INK2)
    f.text(x0 + 0.17, 0.5, '→', fontsize=40, color=INK2)
    f.text(x0 + 0.25, 0.45, b, fontsize=64, fontweight='bold', color=ORANGE); f.text(x0 + 0.25, 0.4, bl, fontsize=14, color=INK2)
    f.text(x0 + 0.025, 0.26, p, fontsize=15, color=INK)
f.text(0.04, 0.12, '* short of the paper’s own multiple-test line (1×10⁻⁵). Giving their readings to signs at random names the right object as often (p = 0.10).', fontsize=12, color=INK2)
foot(f); f.savefig(f'{D}/2_copies.png', facecolor=SURF); plt.close(f)

# 3. how they did it
f = fig()
f.text(0.04, 0.9, 'How the paper “reads” a sign', fontsize=26, fontweight='bold')
f.text(0.04, 0.835, 'Every step is open, which is why we could check it.', fontsize=14, color=INK2)
steps = [('1', 'An AI describes\neach sign in\nEnglish', '“jar”, “fish”,\n“bow”'),
         ('2', 'An AI translator\ngives Old Tamil\nwords', 'kuṭam, mīṉ,\nvil'),
         ('3', 'Add every Tamil\nname part that\nsounds similar', '59% of final readings\nare sound-alikes'),
         ('4', 'Pick the words\nthat make seals\nlook like Tamil\nnames', 'on half the seals'),
         ('5', 'Score on the\nother half vs\nscrambled names', 'Tamil +223,\nSanskrit −13')]
w = 0.172
for i, (n, t, s) in enumerate(steps):
    x0 = 0.04 + i * (w + 0.016)
    hl = (i == 2)
    f.patches.append(FancyBboxPatch((x0, 0.3), w, 0.42, boxstyle='round,pad=0,rounding_size=0.015', transform=f.transFigure, fc='white', ec=ORANGE if hl else GRAY, lw=2.5 if hl else 1))
    f.text(x0 + 0.015, 0.65, n, fontsize=22, fontweight='bold', color=ORANGE if hl else BLUE)
    f.text(x0 + 0.015, 0.6, t, fontsize=13.5, va='top', fontweight='bold')
    f.text(x0 + 0.015, 0.4, s, fontsize=12.5, va='top', color=INK2)
f.text(0.04, 0.17, 'What we found: steps 3–4 give so much freedom that the pictures stop mattering. Tamil scores the same with its picture\nwords on the wrong signs, and Japanese surnames score 60% as high. Nothing was tested on newly found inscriptions.', fontsize=14, color=INK)
foot(f); f.savefig(f'{D}/3_method.png', facecolor=SURF); plt.close(f)
print('ok')
