"""Image 4: one seal, two 'decipherments' from the same code (seed 0 of each contest run)."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.image as mpimg, os
from matplotlib.patches import FancyBboxPatch
D = os.path.dirname(os.path.abspath(__file__)); SIGNS = os.path.join(D, '..', '..', '..', 'site', 'assets', 'signs')
SURF, INK, INK2, BLUE, GRAY, ORANGE = '#fcfcfb', '#0b0b0b', '#52514e', '#2a78d6', '#b9b8b2', '#eb6834'
plt.rcParams.update({'font.family': ['Helvetica Neue', 'Arial Unicode MS', 'DejaVu Sans'], 'text.color': INK})
f = plt.figure(figsize=(12, 6.75), dpi=100, facecolor=SURF)
f.text(0.04, 0.9, 'One seal, two “decipherments”, same code', fontsize=26, fontweight='bold')
f.text(0.04, 0.845, 'Seal M-1312, Mohenjo-daro, in reading order. Both readings were picked by the paper’s own method.', fontsize=14, color=INK2)
cols = [(59, ('fish', 'mīṉ', 'star'), ('fishing', 'tsuri', 'tsuru', 'crane')),
        (342, ('pot', 'kuṭam', 'kuṭi', 'clan village'), ('handle', 'tsuka', 'tsuki', 'moon')),
        (176, ('teeth', 'pal', 'pālai', 'desert'), ('comb', 'kushi', 'koshi', 'crossing'))]
X0, W = 0.25, 0.235
f.text(0.04, 0.565, 'Old Tamil', fontsize=18, fontweight='bold', color=BLUE)
f.text(0.04, 0.33, 'Japanese', fontsize=18, fontweight='bold', color=ORANGE)
f.text(0.04, 0.53, '(their method’s pick)', fontsize=12, color=INK2); f.text(0.04, 0.295, '(no link to the Indus)', fontsize=12, color=INK2)
for i, (m, t, j) in enumerate(cols):
    x = X0 + i * W
    ax = f.add_axes([x + 0.06, 0.65, 0.1, 0.16]); ax.imshow(mpimg.imread(os.path.join(SIGNS, f'M{m}.png'))); ax.axis('off')
    for row, (y, c) in enumerate(((0.47, BLUE), (0.235, ORANGE))):
        e = t if row == 0 else j
        f.patches.append(FancyBboxPatch((x, y), W - 0.02, 0.17, boxstyle='round,pad=0,rounding_size=0.012', transform=f.transFigure, fc='white', ec=GRAY, lw=1))
        if len(e) == 3:
            chain = f'picture “{e[0]}” = {e[1]}'
        else:
            chain = f'picture “{e[0]}” = {e[1]}\n≈ sounds like {e[2]}'
        f.text(x + 0.012, y + 0.15, chain, fontsize=11.5, color=INK2, va='top')
        f.text(x + 0.012, y + 0.025, f'“{e[-1]}”', fontsize=19, fontweight='bold', color=c)
f.text(0.04, 0.13, 'Japanese family names fit the seals 60% as well as Tamil and beat it in 4 of 10 test splits. A method that can do this\ncannot tell us which language the seals record.', fontsize=14, color=INK)
f.text(0.04, 0.035, 'Open Indus · readings from seed 0 of each contest run · sign drawings: Mahadevan 1977 · github.com/HarshInvader/open-indus', fontsize=11, color=INK2)
f.savefig(f'{D}/4_one_seal.png', facecolor=SURF); print('ok')
