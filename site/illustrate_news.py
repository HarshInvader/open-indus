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
    elif key=='cuneiform-2026':
        a.tablet(70,118,190,165); a.tablet(340,118,190,165)
        for x0 in (100,370):
            for i in range(4):
                x=x0+i*36; a.poly([(x,180),(x+20,180),(x+10,204)],INK)
        a.line([(260,192),(340,192)],BLUE,3)
        for x in (285,315): a.ellipse(x,192,5,5,BLUE)
        a.rect(469,226,40,40,PAPER,5,CLAY); a.poly([(479,236),(499,236),(489,256)],CLAY)
    elif key=='zenil-2026':
        a.tablet(72,102,292,190)
        for i in range(5): a.token(110+i*46,152,i,13)
        for i in range(4): a.token(110+i*46,243,i+2,13)
        a.line([(92,198),(344,198)],BLUE,1.5)
        a.ellipse(462,214,70,70,WHITE,INK)
        a.line([(402,214),(522,214)],RULE,1)
        a.line([(462,214),(400,203)],CLAY,4); a.ellipse(462,214,7,7,INK)
    elif key=='rozanova-2026':
        a.sheet(76,170,140,122); a.sheet(384,170,140,122,PALE)
        for x0,c in ((98,BLUE),(406,RULE)):
            for r in range(2):
                for i in range(4): a.token(x0+14+i*30,205+r*40,i+r,8,c)
        a.line([(300,92),(300,310)],INK,6); a.poly([(262,322),(338,322),(300,296)],BLUE)
        a.line([(146,128),(454,128)],INK,4)
        for x in (146,454):
            a.line([(x,128),(x-48,170)],RULE); a.line([(x,128),(x+48,170)],RULE)
        a.ellipse(300,128,9,9,CLAY)
    elif key=='stoicheia-2026':
        a.poly([(96,88),(442,88),(442,206),(372,206),(372,300),(96,300)],SAND,INK)
        for y in (128,170,212,254):
            a.line([(122,y),(352 if y>200 else 418,y)],RULE,2)
        a.rect(372,206,98,94,PAPER,4,CLAY)
        for i,(x,y) in enumerate([(398,232),(442,232),(398,274),(442,274)]): a.token(x,y,i,11)
        a.arrow(520,160,480,214,CLAY)
    elif key=='kelley-2026':
        a.tablet(110,96,380,208)
        for r in range(3):
            y=136+r*52
            for i in range(4): a.ellipse(150+i*24,y,8,8,PAPER,INK,1.5)
            a.line([(262,y-20),(262,y+20)],RULE,1)
            for i in range(3): a.token(300+i*52,y,i+r,13)
    elif key=='korovina-2026':
        a.rect(66,104,236,176,'#b78a5a',10)
        for r in range(4):
            y=134+r*38
            for i in range(5): a.token(98+i*44,y,i+r,9,INK if (i+r)%2 else BLUE)
        for k in range(4): a.sheet(338,212-k*10,74,64)
        for k in range(4): a.sheet(470,232-k*10,62,52,PALE)
        a.arrow(318,230,334,230,CLAY); a.line([(318,268),(462,268)],RULE,1); a.arrow(440,268,462,268,RULE)
    elif key=='rakhigarhi-rgr3-2026':
        a.poly([(48,331),(140,180),(300,140),(460,180),(552,331)],SAND,INK)
        a.poly([(232,166),(368,166),(368,331),(232,331)],PAPER,INK)
        for y,c in ((206,RULE),(246,CLAY),(286,RULE)): a.line([(232,y),(368,y)],c,2)
        a.rect(286,226,28,20,BLUE,3,INK)
        a.line([(332,176),(332,226)],INK,2); a.ellipse(332,170,9,9,CLAY,INK)
    elif key=='hexagon-2026':
        for gx in range(5):
            for gy in range(3):
                x=74+gx*92; y=86+gy*78
                a.rect(x,y,82,68,SAND if (gx+gy)%2 else PALE,3,RULE)
        a.ellipse(300,198,58,40,CLAY,INK)
        a.poly([(400,120),(470,112),(486,176),(430,206),(392,170)],WHITE,INK)
        for x,y in ((420,140),(450,150),(425,175)): a.rect(x,y,14,12,INK,2,None)
    elif key=='cattle-2026':
        a.ellipse(96,272,52,22,SAND,INK); a.ellipse(504,152,52,22,SAND,INK)
        for i in range(16):
            t=i/15; a.ellipse(140+t*320,262-t*104,3,3,RULE)
        x,y=300,198
        a.ellipse(x,y,58,26,WHITE,INK)
        a.ellipse(x+30,y-26,18,14,WHITE,INK)
        a.ellipse(x+68,y-12,16,14,WHITE,INK)
        a.curve([(x+62,y-24),(x+58,y-46),(x+70,y-50),(x+78,y-44)],INK,3)
        for dx in (-40,-22,22,40): a.line([(x+dx,y+20),(x+dx,y+52)],INK,4)
        a.line([(x-58,y-4),(x-72,y+24)],INK,2)
    elif key=='jognakhera-2026':
        for y in (280,296): a.curve([(48,y),(200,y-20),(380,y+18),(552,y-6)],BLUE,3)
        for x in (150,214,278):
            a.line([(x,252),(x,140)],'#b78a5a',3)
            for k in range(5): a.ellipse(x+(-6 if k%2 else 6),150+k*14,6,10,SAND,INK,1)
        for x,y in ((330,232),(352,240),(344,222),(372,230)): a.ellipse(x,y,6,4,CLAY)
        a.arrow(410,200,524,200,CLAY)
    elif key=='gini-2026':
        a.rect(62,92,300,212,PAPER,4,INK)
        for gx in range(3):
            for gy in range(2):
                a.rect(78+gx*94,108+gy*96,78-(gx*4),80-(gy*6),SAND,3,INK)
        a.line([(62,198),(362,198)],RULE,1)
        a.line([(410,292),(540,292)],INK,2); a.line([(410,292),(410,120)],INK,2)
        for i,h in enumerate((150,122,96,70)): a.rect(426+i*28,292-h,18,h,BLUE if i<3 else CLAY,2,None)
    else: raise ValueError(key)
    return a


TOPIC_ALT = {
 'decipherment-methods': 'Illustration: two sheets of plain shapes joined by curved lines, matching shapes on one side to shapes on the other.',
 'language-question': 'Illustration: a balance beam weighing a sheet of shapes against a loose scatter of the same shapes.',
 'readings': 'Illustration: a square seal with an arrow leading to a sheet of written lines.',
 'neighbour-scripts': 'Illustration: three clay tablets of different shapes standing in a row.',
 'corpus-data': 'Illustration: a stack of index cards beside a grid of plain shapes.',
 'administration': 'Illustration: a square seal pressed into a lump of clay beside a row of graded cube weights.',
 'archaeology': 'Illustration: a trench cut through the layers of a mound, with a trowel resting on the edge.',
 'chronology-environment': 'Illustration: a river winding across layered bands of ground under a pale sun.',
 'trade-meluhha': 'Illustration: a small boat on waves with a dotted route between two shores.',
 'people-dna': 'Illustration: a double helix in blue and red rising beside a pot.',
}


def draw_topic(key):
    a=Art()
    if key=='decipherment-methods':
        for x in (96,384): a.sheet(x,92,120,220)
        for i in range(4):
            y=128+i*50; a.token(156,y,i,14); a.token(444,y,(i+2)%4,14,CLAY)
            a.curve([(180,y),(260,y-24),(340,y+24),(420,(128+((i+1)%4)*50))],BLUE,2)
    elif key=='language-question':
        a.line([(300,92),(300,308)],INK,6); a.poly([(260,320),(340,320),(300,294)],BLUE)
        a.line([(140,128),(460,128)],INK,4)
        a.sheet(84,172,112,110)
        for r in range(3):
            for i in range(3): a.token(106+i*34,198+r*30,i+r,8)
        for k,(x,y) in enumerate([(420,206),(470,190),(452,246),(500,232),(404,262)]): a.token(x,y,k,10,CLAY)
        for x in (140,460):
            a.line([(x,128),(x-50,172)],RULE); a.line([(x,128),(x+50,172)],RULE)
    elif key=='readings':
        a.rect(96,128,140,140,SAND,10); a.rect(116,148,100,100,PAPER,6,RULE)
        a.token(166,198,1,26,BLUE)
        a.arrow(256,198,352,198,CLAY)
        a.sheet(372,104,140,190)
        for y in range(134,280,26): a.line([(394,y),(490,y)],RULE,2)
    elif key=='neighbour-scripts':
        a.tablet(64,140,130,150)
        a.poly([(236,290),(236,150),(300,110),(364,150),(364,290)],SAND,INK)
        a.ellipse(474,214,66,78,SAND,INK)
        for i in range(3):
            a.token(104+i*26,210,i,7); a.token(270+i*30,210,i+1,8,CLAY); a.token(446+i*28,214,i+2,8)
    elif key=='corpus-data':
        for k in range(5): a.sheet(80+k*8,96+k*14,150,100)
        for gx in range(4):
            for gy in range(4): a.token(344+gx*48,110+gy*48,gx+gy,12,CLAY if (gx*gy)%3==1 else BLUE)
    elif key=='administration':
        a.ellipse(198,232,104,58,SAND,INK)
        a.rect(150,104,96,96,PAPER,8,INK); a.token(198,152,2,22,BLUE)
        a.arrow(198,208,198,226,CLAY)
        for i,sz in enumerate((14,20,26,34)):
            x=372+i*44+sum((14,20,26,34)[:i])*0.6
            a.rect(x,300-sz*2,sz*2*0.7,sz*2*0.7,CLAY if i%2 else '#c9b79e',3,INK)
    elif key=='archaeology':
        a.poly([(48,331),(150,170),(300,128),(450,170),(552,331)],SAND,INK)
        a.poly([(236,152),(364,152),(364,331),(236,331)],PAPER,INK)
        for y,c in ((196,RULE),(236,CLAY),(276,RULE),(306,BLUE)): a.line([(236,y),(364,y)],c,2)
        a.poly([(380,140),(430,104),(442,116),(392,152)],RULE,INK); a.line([(430,104),(462,80)],INK,4)
    elif key=='chronology-environment':
        for i,c in enumerate((SAND,'#c9b79e',SAND,'#c9b79e')): a.rect(48,200+i*32,504,32,c,0,None)
        a.curve([(70,200),(220,330),(360,180),(530,330)],BLUE,10)
        a.ellipse(452,110,34,34,'#e7d7b9',RULE)
    elif key=='trade-meluhha':
        for y in (268,288): a.curve([(48,y),(200,y-14),(400,y+14),(552,y)],BLUE,3)
        a.poly([(230,238),(370,238),(346,268),(254,268)],'#b78a5a',INK)
        a.line([(300,238),(300,130)],INK,3); a.poly([(304,136),(304,226),(364,226)],WHITE,INK)
        a.poly([(48,331),(48,250),(110,262),(130,331)],SAND,INK); a.poly([(552,331),(552,240),(482,256),(470,331)],SAND,INK)
        for i in range(12): a.ellipse(132+i*30,208-math.sin(i/11*math.pi)*60,3,3,CLAY)
    elif key=='people-dna':
        for side in (0,1):
            pts=[(260+(1 if side else -1)*55*math.cos(i/130*math.pi*3),85+i*1.65) for i in range(131)]
            a.line(pts,CLAY if side else BLUE,6)
        for i in range(14):
            y=85+i*16; dx=55*math.cos(i*16/1.65/130*math.pi*3)
            a.line([(260-dx,y),(260+dx,y)],RULE,3)
        a.pot(430,262)
    else: raise ValueError(key)
    return a


def main():
    news=json.loads((SITE/'news.json').read_text())
    out=SITE/'assets/news'; out.mkdir(exist_ok=True)
    for item in news['items']:
        path=out/(item['id']+'.webp'); draw(item['id']).save(path)
        print(path.name, path.stat().st_size)
    lib=SITE/'assets/library'; lib.mkdir(exist_ok=True)
    for key in news['topics']:
        path=lib/(key+'.webp'); draw_topic(key).save(path)
        print(path.name, path.stat().st_size)
    (lib/'alt.json').write_text(json.dumps(TOPIC_ALT, indent=1)+'\n')

if __name__=='__main__': main()
