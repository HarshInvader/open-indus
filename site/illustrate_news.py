#!/usr/bin/env python3
"""Original editorial artwork; no ancient glyphs, reference photos or font rendering.
Reproduce with .venv/bin/python -I site/illustrate_news.py (Pillow only).
Every coordinate uses a 600×400 artboard, rendered at 3× before WebP export.
"""
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parent
PAPER, INK, CLAY, BLUE = '#f3efe7', '#29251f', '#a9482c', '#526481'
SAND, PALE, WHITE, RULE = '#d8c5ac', '#dce0e5', '#faf7f0', '#b6a58d'
S = 3

class Art:
    def __init__(self):
        self.im = Image.new('RGB', (600*S, 400*S), PAPER)
        self.d = ImageDraw.Draw(self.im)
        # A quiet horizon and a printed-paper halo anchor the entire series.
        self.ellipse(300, 192, 166, 144, '#e9e1d3')
        self.line([(48, 331), (552, 331)], RULE, 1)
        self.line([(48, 338), (113, 338)], CLAY, 3)
    def points(self, pts): return [(round(x*S), round(y*S)) for x,y in pts]
    def line(self, pts, color=INK, w=2):
        self.d.line(self.points(pts), fill=color, width=max(1, round(w*S)), joint='curve')
    def poly(self, pts, fill, outline=None):
        self.d.polygon(self.points(pts), fill=fill)
        if outline: self.line(pts+[pts[0]], outline, 2)
    def rect(self, x,y,w,h,fill=WHITE,r=8,outline=INK):
        self.d.rounded_rectangle((round(x*S),round(y*S),round((x+w)*S),round((y+h)*S)), radius=round(r*S),fill=fill,outline=outline,width=2*S)
    def ellipse(self,x,y,rx,ry,fill,outline=None,w=2):
        self.d.ellipse((round((x-rx)*S),round((y-ry)*S),round((x+rx)*S),round((y+ry)*S)),fill=fill,outline=outline,width=round(w*S))
    def curve(self,p,color=INK,w=2):
        pts=[]
        for i in range(65):
            t=i/64; u=1-t
            pts.append((u**3*p[0][0]+3*u*u*t*p[1][0]+3*u*t*t*p[2][0]+t**3*p[3][0], u**3*p[0][1]+3*u*u*t*p[1][1]+3*u*t*t*p[2][1]+t**3*p[3][1]))
        self.line(pts,color,w)
    def sheet(self,x,y,w,h,fill=WHITE):
        self.rect(x+7,y+8,w,h,SAND,6,None)
        self.rect(x,y,w,h,fill,6)
    def token(self,x,y,k=0,size=16,color=BLUE):
        # Plain geometry, deliberately not a transcription or claimed reading.
        if k%4==0: self.ellipse(x,y,size,size,color)
        elif k%4==1: self.poly([(x,y-size),(x+size,y),(x,y+size),(x-size,y)],color)
        elif k%4==2: self.rect(x-size,y-size,size*2,size*2,color,3,None)
        else:
            self.ellipse(x,y,size,size,None,color,4)
    def arrow(self,x1,y1,x2,y2,color=BLUE):
        self.line([(x1,y1),(x2,y2)],color,2)
        a=math.atan2(y2-y1,x2-x1)
        self.line([(x2-9*math.cos(a-.55),y2-9*math.sin(a-.55)),(x2,y2),(x2-9*math.cos(a+.55),y2-9*math.sin(a+.55))],color,2)
    def tablet(self,x,y,w=205,h=155):
        self.sheet(x,y,w,h,SAND)
        self.line([(x+18,y+h-18),(x+w-20,y+h-18)],RULE,1)
    def crown(self,x,y):
        self.poly([(x-34,y+18),(x-39,y-20),(x-15,y-4),(x,y-31),(x+15,y-4),(x+39,y-20),(x+34,y+18)],CLAY,INK)
        self.line([(x-30,y+27),(x+30,y+27)],INK,3)
    def fish(self,x,y,scale=1):
        self.ellipse(x,y,45*scale,23*scale,BLUE,INK)
        self.poly([(x+38*scale,y),(x+69*scale,y-27*scale),(x+69*scale,y+27*scale)],BLUE,INK)
        self.ellipse(x-24*scale,y-4*scale,3*scale,3*scale,PAPER)
    def star(self,x,y,r=15):
        pts=[(x+math.cos(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.42),y+math.sin(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.42)) for i in range(10)]
        self.poly(pts,CLAY)
    def pot(self,x,y):
        self.poly([(x-28,y-60),(x+28,y-60),(x+22,y-38),(x+50,y+3),(x+34,y+53),(x-34,y+53),(x-50,y+3),(x-22,y-38)],CLAY,INK)
        self.line([(x-23,y-48),(x+23,y-48)],PAPER,3)
    def save(self,path):
        # Subtle deterministic fibres; all artwork is original, abstract and flat.
        rng=random.Random(91)
        for _ in range(6500):
            x=rng.randrange(600*S); y=rng.randrange(400*S)
            old=self.im.getpixel((x,y)); delta=rng.choice([-12,-7,7])
            self.d.point((x,y),fill=tuple(max(0,min(255,c+delta)) for c in old))
        self.im.resize((600,400),Image.Resampling.LANCZOS).save(path,'WEBP',quality=83,method=6)


def draw(key):
    a=Art()
    if key=='restoration-2026':
        a.tablet(72,109,308,176)
        for x,k in [(115,0),(179,1),(311,3)]: a.token(x,164,k,17)
        a.rect(221,138,50,50,PAPER,5,CLAY)
        a.poly([(212,109),(235,109),(231,124),(218,133)],PAPER)
        for y,k in [(100,1),(196,2),(283,0)]:
            a.sheet(449,y-26,56,52); a.token(477,y,k,12,CLAY if k==2 else BLUE)
        a.arrow(444,196,278,164,CLAY)
        a.line([(101,234),(345,234)],RULE)
    elif key=='voynich-2026':
        a.sheet(78,171,130,118); a.sheet(392,171,130,118)
        for x in (106,420):
            for i in range(3): a.token(x+i*35,209,i,8)
            for y in (240,256): a.line([(x,y),(x+72,y)],RULE)
        a.line([(300,86),(300,308)],INK,6); a.poly([(260,321),(340,321),(300,293)],BLUE)
        a.line([(126,127),(474,127)],INK,4)
        for x in (143,457):
            a.line([(x,127),(x-46,171)],RULE); a.line([(x,127),(x+46,171)],RULE)
        a.ellipse(300,127,9,9,CLAY)
    elif key=='dominik-2026':
        for y in (145,260):
            a.sheet(70,y-42,100,84); a.token(120,y,0 if y==145 else 1,24)
            a.sheet(385,y-42,100,84); a.token(435,y,2,24)
            a.arrow(185,y,365,y)
        a.rect(270,99,16,91,CLAY,3,None)
        a.ellipse(278,260,27,27,PAPER,BLUE)
        a.curve([(256,258),(270,279),(287,279),(300,251)],BLUE,4)
    elif key=='sigil-2026':
        for x in (88,328):
            a.sheet(x,93,184,205)
            for i in range(6): a.token(x+48+(i%2)*87,136+(i//2)*59,i,15,CLAY if i==3 else BLUE)
        a.line([(295,109),(295,289)],RULE,1)
        a.ellipse(295,200,20,20,PAPER,INK)
        a.ellipse(295,200,6,6,CLAY)
    elif key in ('lehs-2026','desset-2022'):
        if key=='lehs-2026':
            a.sheet(92,111,182,194); a.sheet(106,101,182,194); a.sheet(120,91,182,194)
            a.line([(143,91),(143,285)],RULE); a.crown(211,158)
            for i in range(3): a.token(173+i*39,239,i,9)
            a.tablet(362,163,135,120); a.arrow(315,213,348,213)
            for i in range(3): a.token(390+i*36,206,i,9)
        else:
            a.poly([(89,129),(220,129),(205,294),(105,294)],SAND,INK)
            a.line([(89,129),(220,129)],INK,5); a.crown(155,94)
            for i in range(3): a.token(128+i*27,192,i,8)
            a.sheet(358,132,156,158)
            for i in range(3):
                a.token(387+i*44,179,i,10)
                a.curve([(147+i*17,223),(245,310),(312,89),(387+i*44,220)],BLUE,1.5)
    elif key=='nair-2026':
        a.poly([(84,113),(218,113),(218,210),(151,275),(84,210)],BLUE,INK)
        a.ellipse(151,169,24,24,PAPER)
        a.sheet(382,112,132,171)
        for y in range(142,260,27): a.ellipse(405,y,4,4,CLAY); a.line([(424,y),(492,y)],RULE)
        a.line([(231,204),(362,204)],INK,2); a.ellipse(297,204,21,21,CLAY,INK)
    elif key=='uae-seal-2026':
        # Unverified find: an empty specimen silhouette, no invented bull or inscription.
        a.ellipse(229,191,95,95,SAND,INK,3); a.ellipse(229,191,68,68,PAPER,RULE)
        a.line([(90,301),(466,301)],BLUE)
        for y in (271,283): a.curve([(326,y),(380,y-17),(437,y+17),(504,y)],BLUE)
        a.ellipse(408,122,44,44,None,BLUE,5); a.line([(441,153),(485,196)],INK,12)
        a.line([(387,122),(429,122)],RULE,2)
    elif key=='kriger-2026':
        for x,y in [(83,94),(123,147),(163,200)]:
            a.sheet(x,y,202,91)
            for i in range(4): a.token(x+35+i*43,y+43,i,12)
        a.ellipse(437,198,64,64,None,BLUE,8); a.line([(480,246),(513,282)],INK,12)
        a.token(437,198,2,23,CLAY)
    elif key=='asi-2025':
        a.sheet(138,74,324,232)
        a.rect(138,74,324,51,BLUE,6)
        for x in (200,400): a.rect(x-5,55,10,39,INK,5,None)
        for i in range(15):
            x=179+(i%5)*60; y=157+(i//5)*57
            a.rect(x,y,37,33,CLAY if i in (6,7,8) else PAPER,4,RULE)
    elif key=='protoelamite-2025':
        a.tablet(76,89,217,217)
        for y in (131,185,239):
            a.token(112,y,1,12)
            for i in range(3): a.ellipse(162+i*39,y,7,7,INK)
        for i in range(3):
            a.sheet(365,88+i*77,141,59)
            a.token(395,118+i*77,i,11,CLAY)
            a.line([(422,118+i*77),(483,118+i*77)],RULE)
            a.arrow(304,133+i*53,353,118+i*77)
    elif key=='dixit-2025':
        a.tablet(130,85,299,223)
        for i in range(3):
            a.token(188+i*90,138,i,16)
            a.rect(160+i*90,109,56,58,None,4,BLUE)
        # Abstract animal silhouette, explicitly illustration rather than an artefact reproduction.
        a.ellipse(274,234,60,27,CLAY); a.ellipse(340,210,20,19,CLAY)
        a.line([(323,213),(305,239)],CLAY,14)
        for x in (238,285,304): a.line([(x,251),(x-6,276)],CLAY,8)
        a.rect(200,183,167,104,None,5,BLUE)
        a.line([(430,197),(497,197),(497,260)],BLUE,2); a.ellipse(497,270,6,6,BLUE)
    elif key=='tyc-2025':
        a.poly([(58,275),(139,149),(189,209),(252,107),(326,230),(383,145),(531,275)],PALE)
        a.poly([(116,275),(252,107),(335,275)],SAND)
        for x in (177,379):
            a.sheet(x-49,164,98,104); a.token(x,216,3,25)
        a.curve([(232,219),(274,185),(308,185),(325,219)],BLUE)
        a.ellipse(291,204,10,10,CLAY)
    elif key=='tn-graffiti-2025':
        for i,(x,y) in enumerate([(147,192),(303,218),(455,178)]):
            a.pot(x,y); a.token(x,y,i,13,PAPER)
        a.line([(130,307),(473,307)],RULE)
        for x in (147,303,455): a.ellipse(x,307,5,5,BLUE)
    elif key=='proskouriakoff-1960':
        a.poly([(98,291),(98,117),(113,81),(177,81),(195,117),(195,291)],SAND,INK)
        for y in (128,183,238):
            a.rect(118,y-20,56,39,PAPER,5,RULE); a.token(146,y,3,11,CLAY)
            a.line([(195,y),(268+(y-128)*1.8,y)],RULE,1)
        a.line([(260,296),(510,296)],INK,3)
        for i in range(3):
            x=276+i*106; a.ellipse(x,296,7,7,CLAY)
            a.line([(x,280),(x,136+i*52)],BLUE,2)
            a.ellipse(x,131+i*52,15,15,BLUE)
    elif key=='mahadevan-1977':
        a.sheet(142,77,300,237); a.sheet(130,65,300,237)
        for i in range(20):
            x=160+(i%5)*54; y=96+(i//5)*53
            a.rect(x-15,y-15,39,39,PAPER,3,RULE); a.token(x+4,y+4,i,9,CLAY if i==12 else BLUE)
        a.rect(441,148,27,120,BLUE,3,None)
        for y in range(162,255,14): a.line([(442,y),(452,y)],PAPER,1)
    elif key=='parpola-1994':
        a.ellipse(175,201,90,90,PAPER,RULE); a.fish(161,201,.95)
        a.curve([(268,193),(299,161),(323,161),(351,193)],BLUE,2)
        a.ellipse(435,201,86,86,PALE)
        for x,y,r in [(410,173,18),(464,208,21),(406,239,12),(457,153,10),(435,204,10),(477,253,9)]: a.star(x,y,r)
    elif key=='fsw-2004':
        a.sheet(83,148,268,101)
        for i in range(5): a.token(117+i*49,197,i,12)
        a.line([(83,278),(351,278)],INK)
        for x in (83,351): a.line([(x,269),(x,287)],INK)
        a.poly([(409,129),(508,129),(508,210),(459,263),(409,210)],BLUE,INK)
        a.token(459,183,0,19,PAPER)
    elif key=='rao-sproat':
        for x,y in [(93,112),(142,184),(191,256)]: a.rect(x,y,289,35,PALE,17,None)
        a.rect(219,112,133,179,SAND,9,None)
        for i,y in enumerate((129,201,273)):
            a.ellipse(252+i*36,y,13,13,CLAY)
        a.line([(77,310),(520,310)],INK,2)
        for x in range(100,521,42): a.line([(x,307),(x,317)],RULE,1)
    elif key=='laursen-2010':
        a.tablet(72,103,146,155)
        for i in range(3): a.token(101+i*44,151,i,11)
        a.ellipse(448,196,81,81,SAND,INK)
        for i in range(3): a.token(404+i*44,180,2-i,11)
        a.curve([(230,174),(286,95),(334,95),(360,174)],BLUE,2)
        for y in (278,292): a.curve([(57,y),(190,y-22),(346,y+22),(540,y)],BLUE,2)
    elif key=='snyder-luo':
        for x in (91,385): a.sheet(x,79,122,231)
        for i in range(4):
            y=119+i*51; a.token(151,y,i,15); a.token(445,y,(i+1)%4,15,CLAY)
            a.curve([(177,y),(256,y-20),(332,y+20),(419,y)],BLUE,2)
        a.ellipse(300,199,26,26,PAPER,INK); a.token(300,199,3,12,CLAY)
    elif key=='rakhigarhi-2019':
        for side in (0,1):
            pts=[(300+(1 if side else -1)*65*math.cos(i/130*math.pi*3),85+i*1.65) for i in range(131)]
            a.line(pts,CLAY if side else BLUE,7)
        for i in range(14):
            y=85+i*16; dx=65*math.cos(i*16/1.65/130*math.pi*3)
            a.line([(300-dx,y),(300+dx,y)],RULE,3)
        a.poly([(92,281),(166,191),(212,265),(173,308)],SAND)
        a.ellipse(166,249,9,9,CLAY); a.line([(166,249),(227,227)],RULE)
    elif key=='mukhopadhyay-2019':
        a.rect(98,154,162,142,SAND,6); a.line([(179,154),(179,296)],INK)
        a.line([(98,200),(260,200)],RULE)
        a.poly([(226,132),(320,156),(306,213),(217,186)],WHITE,INK)
        for i in range(3): a.token(242+i*22,162+i*6,i,7,CLAY)
        a.pot(417,234)
        for i in range(6): a.ellipse(328+i*23,307,7,7,CLAY,INK,1)
    elif key=='sign2vec-2022':
        a.ellipse(183,202,92,92,PALE,RULE); a.ellipse(420,202,92,92,SAND,RULE)
        for x,y in [(145,179),(209,163),(186,238)]: a.token(x,y,3,15)
        for x,y in [(387,163),(450,190),(410,243)]: a.token(x,y,1,15,CLAY)
        for x,y in [(80,89),(294,91),(522,294)]:
            a.token(x,y,3 if x<300 else 1,9,BLUE if x<300 else CLAY)
        a.arrow(282,92,220,136); a.arrow(514,276,477,246)
    else: raise ValueError(key)
    return a


def main():
    items=json.loads((SITE/'news.json').read_text())['items']
    out=SITE/'assets/news'; out.mkdir(exist_ok=True)
    for item in items:
        path=out/(item['id']+'.webp'); draw(item['id']).save(path)
        print(path.name, path.stat().st_size)

if __name__=='__main__': main()
