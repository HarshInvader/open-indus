"""Thread images in Open Indus branding (site fonts and colour tokens), rendered by headless Chromium at 2x.
Run: ../../../.venv/bin/python -I make_branded.py   (needs playwright's chromium-headless-shell)"""
import os, subprocess, re, glob
D = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.join(D, '..', '..', '..', 'site')
FONT = os.path.join(SITE, 'font')
CHROME = sorted(glob.glob(os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell')))[-1]
def svg(p):
    s = open(p).read(); s = re.sub(r'<\?xml.*?\?>|<!DOCTYPE.*?>|<metadata>.*?</metadata>', '', s, flags=re.S); return s
MARK = svg(os.path.join(SITE, 'assets', 'logo-mark.svg'))
def glyph(m): return svg(os.path.join(D, 'glyphs', f'M{m}.svg')).replace('<svg ', '<svg class="g" ', 1)
CSS = f"""
@font-face{{font-family:"OID";src:url("file://{FONT}/OpenIndus-Bold.ttf");font-weight:700}}
@font-face{{font-family:"OID";src:url("file://{FONT}/OpenIndus-Regular.ttf");font-weight:400}}
@font-face{{font-family:"OIT";src:url("file://{FONT}/OpenIndusText-Regular.ttf");font-weight:400}}
@font-face{{font-family:"OIT";src:url("file://{FONT}/OpenIndusText-Bold.ttf");font-weight:700}}
:root{{--paper:#F4F0E7;--surface:#FAF7F0;--plate:#E7E1D4;--ink:#1E1A16;--muted:#594F45;--line:#DED6C7;--line-strong:#C3B9A7;
--accent:#2A4D84;--accent-soft:#DCE3EE;--clay:#A9482C;--clay-soft:#F1DED5;--chance:#857A6D}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1200px;height:675px;background:var(--paper);color:var(--ink);font-family:OIT,sans-serif;-webkit-font-smoothing:antialiased}}
.f{{position:relative;width:1200px;height:675px;padding:52px 64px 0;overflow:hidden}}
.kick{{font-family:OID;font-weight:700;font-size:15px;letter-spacing:.14em;color:var(--clay);text-transform:uppercase}}
h1{{font-weight:700;font-size:46px;line-height:1.08;letter-spacing:-.018em;margin-top:12px;max-width:1060px}}
.sub{{font-size:21px;line-height:1.4;color:var(--muted);margin-top:12px;max-width:1040px}}
.foot{{position:absolute;left:64px;right:64px;bottom:0;height:58px;border-top:1px solid var(--line-strong);display:flex;align-items:center;justify-content:space-between;font-size:15px;color:var(--muted)}}
.brand{{display:flex;align-items:center;gap:10px;font-family:OID;font-weight:700;letter-spacing:.1em;font-size:15px;color:var(--ink)}}
.brand svg{{width:24px;height:24px;color:var(--accent)}}
.ta{{color:var(--accent)}} .jp{{color:var(--clay)}}
"""
def page(body, kick, title, sub, foot_l):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{body[0]}</style></head><body><div class="f">
<div class="kick">{kick}</div><h1>{title}</h1><p class="sub">{sub}</p>{body[1]}
<div class="foot"><span>{foot_l}</span><span class="brand">{MARK}OPEN INDUS</span></div></div></body></html>"""

imgs = {}
# --- A: one seal, two readings
cols = [(59, ('fish', 'mīṉ', None, 'star'), ('fishing', 'tsuri', 'tsuru', 'crane')),
        (342, ('pot', 'kuṭam', 'kuṭi', 'clan village'), ('handle', 'tsuka', 'tsuki', 'moon')),
        (176, ('teeth', 'pal', 'pālai', 'desert'), ('comb', 'kushi', 'koshi', 'crossing'))]
def cell(e, cls):
    pic, w, alike, mean = e
    chain = f'picture “{pic}” → <i>{w}</i>' + (f'<br>sounds like → <i>{alike}</i>' if alike else '<br>&nbsp;')
    return f'<div class="cell {cls}"><div class="ch">{chain}</div><div class="mean">“{mean}”</div></div>'
grid = ''.join(f'<div class="sg">{glyph(m)}</div>' for m, _, _ in cols)
rowT = ''.join(cell(t, 'ta') for _, t, _ in cols); rowJ = ''.join(cell(j, 'jp') for _, _, j in cols)
cssA = """.wrap{display:grid;grid-template-columns:200px repeat(3,1fr);gap:14px 18px;margin-top:22px;align-items:stretch}
.seal{grid-column:2/5;display:grid;grid-template-columns:repeat(3,1fr);gap:18px;background:var(--plate);border-radius:14px;padding:10px 0}
.sg{display:flex;justify-content:center}.g{height:74px;width:auto}.g path,.g g{fill:var(--ink)}
.lab{display:flex;flex-direction:column;justify-content:center}.lab b{font-size:26px}.lab span{font-size:16px;color:var(--muted);margin-top:4px}
.cell{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 18px 12px;border-left:5px solid}
.cell.ta{border-left-color:var(--accent)}.cell.jp{border-left-color:var(--clay)}
.ch{font-size:15.5px;line-height:1.45;color:var(--muted)}.ch i{font-style:normal;color:var(--ink);font-weight:700}
.mean{font-size:30px;font-weight:700;margin-top:4px;letter-spacing:-.01em}.cell.ta .mean{color:var(--accent)}.cell.jp .mean{color:var(--clay)}"""
bodyA = (cssA, f"""<div class="wrap"><div></div><div class="seal">{grid}</div>
<div class="lab"><b class="ta">Old Tamil</b><span>the paper’s language</span></div>{rowT}
<div class="lab"><b class="jp">Japanese</b><span>no link to the Indus</span></div>{rowJ}</div>""")
imgs['A_one_seal'] = page(bodyA, 'Checking “AI cracked the Indus script”', 'Same seal, same code: it “reads” in Japanese too',
    'Seal M-1312 through the paper’s method twice. Both read fluently, so fluency proves nothing.',
    'Readings from seed 0 of each run · sign drawings after Mahadevan 1977')
# --- B: scores
rows = [('Old Tamil', 'the paper’s headline', 223.0, 'var(--accent)'),
        ('Tamil, pictures on wrong signs', 'picture words moved at random, 50 runs', 223.7, 'var(--accent)'),
        ('Japanese family names', 'no link to the Indus', 134.5, 'var(--clay)'),
        ('Vedic Sanskrit', 'which the paper rules out', -13.3, 'var(--chance)'),
        ('Tamil on fake seals', 'meaningless sign strings', -28.5, 'var(--chance)')]
Z, SC = 140, 2.2  # zero position px, px per point
bars = ''
for name, note, v, c in rows:
    w = abs(v) * SC; left = Z if v >= 0 else Z - w
    val = f'{v:+.0f}'.replace('-', '−')
    bars += f'''<div class="r"><div class="nm"><b>{name}</b><span>{note}</span></div><div class="tr">
<div class="bar" style="left:{left}px;width:{w}px;background:{c}"></div>
<div class="v" style="left:{(Z + w + 12) if v >= 0 else (Z - w - 70)}px;{'text-align:right;width:58px' if v < 0 else ''}">{val}</div></div></div>'''
cssB = f""".rows{{margin-top:26px}}.r{{display:grid;grid-template-columns:330px 1fr;align-items:center;height:62px}}
.nm b{{display:block;font-size:20px}}.nm span{{font-size:15px;color:var(--muted)}}
.tr{{position:relative;height:62px}}.tr::before{{content:"";position:absolute;left:{Z}px;top:-6px;bottom:-6px;border-left:1.5px solid var(--muted)}}
.bar{{position:absolute;top:14px;height:34px;border-radius:5px}}
.v{{position:absolute;top:13px;font-size:26px;font-weight:700}}
.ax{{margin-left:{330 + Z - 40}px;font-size:14px;color:var(--muted);margin-top:4px}}"""
bodyB = (cssB, f'<div class="rows">{bars}</div><div class="ax">0 = no better than chance</div>')
imgs['B_scores'] = page(bodyB, 'Checking “AI cracked the Indus script”', 'Japanese scores 60% as well as Tamil',
    'Japanese has no link to the Indus. Score = how much better real names fit than scrambled ones.',
    'Mean of 10 held-out splits each · github.com/HarshInvader/open-indus')
# --- C: copies
cssC = """.cards{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:28px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:24px 30px}
.card h3{font-size:22px}.nums{display:flex;align-items:center;gap:26px;margin:14px 0 6px}
.n{font-family:OID;font-weight:700;font-size:92px;line-height:1}.n small{display:block;font-family:OIT;font-weight:400;font-size:16px;color:var(--muted);margin-top:6px;letter-spacing:0}
.arrow{font-size:40px;color:var(--muted)}.p{font-size:18px;color:var(--ink);margin-top:10px}.p b{color:var(--clay)}
.note{font-size:15px;color:var(--muted);margin-top:18px;max-width:1060px}"""
def card(h, a, al, b, bl, p0, p1):
    return f'''<div class="card"><h3>{h}</h3><div class="nums"><div class="n ta">{a}<small>{al}</small></div><div class="arrow">→</div>
<div class="n jp">{b}<small>{bl}</small></div></div><div class="p">p = {p0} &nbsp;→&nbsp; <b>p = {p1}</b></div></div>'''
bodyC = (cssC, '<div class="cards">' + card('“Copper” sign on copper tablets', '21', 'tablet faces', '3', 'distinct inscriptions', '6×10⁻¹¹', '0.19')
         + card('“Armlet” sign on bangles', '10', 'bangle faces', '4', 'distinct inscriptions', '1.5×10⁻⁷', '0.017*') + '</div>'
         + '<p class="note">* Short of the paper’s own bar for many tests (1×10⁻⁵). Giving their readings to signs at random names the right object about as often (p = 0.10).</p>')
imgs['C_copies'] = page(bodyC, 'Checking “AI cracked the Indus script”', 'Count each text once and the “proof” fades',
    'Copper tablets came in sets with the same inscription. The paper counted every copy as new evidence.',
    'Fisher tests on the paper’s corpus · github.com/HarshInvader/open-indus')
# --- D: sound-alikes, one example + the split
cssD = """.ex{display:flex;align-items:center;gap:14px;margin-top:30px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:20px 28px}
.ex .g{height:78px;width:auto}.ex .g path,.ex .g g{fill:var(--ink)}
.stp{display:flex;flex-direction:column;align-items:flex-start}.stp small{font-size:14px;color:var(--muted)}.stp b{font-size:28px;letter-spacing:-.01em}
.ar{font-size:28px;color:var(--line-strong)}.fin b{color:var(--clay)}
.split{margin-top:34px}.split .lbl{font-size:17px;color:var(--muted);margin-bottom:10px}
.barr{display:flex;height:64px;gap:3px}.seg{border-radius:6px;display:flex;align-items:center;padding:0 20px;color:#fff;font-weight:700;font-size:21px}
.seg.lit{background:var(--accent);width:41%}.seg.snd{background:var(--clay);width:59%}
.keys{display:flex;margin-top:10px;font-size:16px;color:var(--muted)}.keys div:first-child{width:41%}"""
def stp(top, word): return f'<div class="stp"><small>{top}</small><b>{word}</b></div>'
bodyD = (cssD, f'''<div class="ex">{glyph(342)}<span class="ar">→</span>{stp('the sign shows', '“pot”')}<span class="ar">→</span>
{stp('in Tamil', 'kuṭam')}<span class="ar">→</span>{stp('swapped for a sound-alike', 'kuṭi')}<span class="ar">→</span>
<div class="stp fin"><small>their reading</small><b>“clan village”</b></div></div>
<div class="split"><div class="lbl">All 274 Tamil readings in the paper’s headline runs</div>
<div class="barr"><div class="seg lit">41%</div><div class="seg snd">59%</div></div>
<div class="keys"><div>the picture’s own word</div><div>a word that only sounds like it</div></div></div>''')
imgs['D_method'] = page(bodyD, 'Checking “AI cracked the Indus script”', 'Most readings only sound like the picture',
    'Any name part that sounds similar can stand in for the picture’s word. That freedom lets Japanese fit too.',
    'From the paper’s archived runs (113 picture words, 161 sound-alikes) · github.com/HarshInvader/open-indus')

os.makedirs(os.path.join(D, 'html'), exist_ok=True)
for k, h in imgs.items():
    hp = os.path.join(D, 'html', k + '.html'); open(hp, 'w').write(h)
    out = os.path.join(D, k + '.png')
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2', '--window-size=1200,675',
                    '--allow-file-access-from-files', f'--screenshot={out}', 'file://' + hp], check=True, capture_output=True)
    print(k, os.path.getsize(out))
