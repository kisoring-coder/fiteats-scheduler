import json, math, sys, os, subprocess, random
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
DUR = 24.3
BG = (21, 23, 26); LIME = (198, 242, 78); CORAL = (255, 107, 91); WHITE = (245, 245, 240)
GREY = (140, 146, 152); CARD = (36, 39, 44); GOLD = (255, 196, 60); WA = (37, 211, 102)
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
INTERB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
TAG = "DESK JOB DIET"
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

words = [w for w in json.load(open(f'{ROOT}/words.json'))['words'] if w.get('type', 'word') == 'word']
WS = [w['start'] for w in words]

AV1_END = 7.15   # hook avatar clip covers 0 .. 6.70
AV2_T0 = 11.85
AV2_END = 17.25   # shared mid avatar clip starts here (audio cut point)

# (caption text, prop). 98 = hook avatar, 97 = mid avatar
SC = [
 ("You're sitting at a laptop nine hours a day.", 98),
 ("The gym isn't your problem, your lunch is.", 98),
 ("Hours of sitting means your body burns less.", 98),
 ("Then comes the heavy lunch", 40),
 ("and chai", 41), ("and samosa", 42), ("at 4PM", 43),
 ("It adds up without you noticing.", 44),
 ("That's why every FitEats meal", 97), ("is low calorie, high protein,", 97), ("and cooked fresh every day.", 97),
 ("Delivered to your desk", 45), ("in Chennai.", 46),
 ("No cooking,", 47), ("no counting.", 48),
 ("Message us on WhatsApp for this week's menu.", 49),
]
scenes = []; wi = 0
for txt, prop in SC:
    n = len(txt.split()); scenes.append(dict(txt=txt, prop=prop, i0=wi, i1=wi + n)); wi += n
assert wi == len(words), (wi, len(words))
for k, s in enumerate(scenes):
    s['t0'] = 0.0 if k == 0 else WS[s['i0']]
    s['t1'] = DUR if k == len(scenes) - 1 else WS[scenes[k + 1]['i0']]
# snap avatar boundaries to the clip cut points
for k, s in enumerate(scenes):
    if s['prop'] == 40 and scenes[k - 1]['prop'] == 98: s['t0'] = AV1_END; scenes[k - 1]['t1'] = AV1_END
    if s['prop'] == 97 and scenes[k - 1]['prop'] == 44: s['t0'] = AV2_T0; scenes[k - 1]['t1'] = AV2_T0
    if s['prop'] == 45 and scenes[k - 1]['prop'] == 97: s['t0'] = AV2_END; scenes[k - 1]['t1'] = AV2_END
for k, s in enumerate(scenes):
    s['punch'] = not (k > 0 and scenes[k - 1]['prop'] == s['prop'])

CORALW = {"heavy", "lunch", "chai", "samosa", "4pm", "adds", "up", "noticing.", "less.", "problem,", "is.", "sitting", "burns"}
LIMEW = {"fiteats", "low", "calorie,", "high", "protein,", "fresh", "desk", "chennai.", "whatsapp", "menu.", "cooked"}

def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eb(x):
    x = cl(x); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

S2 = 2; PW, PH = 1080, 640; PY = 880
class L:
    def __init__(self):
        self.im = Image.new("RGBA", (PW * S2, PH * S2), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def rr(self, b, r, fill=None, outline=None, w=0):
        self.d.rounded_rectangle([v * S2 for v in b], r * S2, fill=fill, outline=outline, width=w * S2)
    def el(self, b, fill=None, outline=None, w=0):
        self.d.ellipse([v * S2 for v in b], fill=fill, outline=outline, width=w * S2)
    def ln(self, pts, fill, w):
        self.d.line([(x * S2, y * S2) for x, y in pts], fill=fill, width=int(w * S2), joint="curve")
    def pg(self, pts, fill=None, outline=None):
        self.d.polygon([(x * S2, y * S2) for x, y in pts], fill=fill, outline=outline)
    def tx(self, xy, s, font, size, fill, anchor="mm"):
        if size < 6: return
        self.d.text((xy[0] * S2, xy[1] * S2), s, font=F(font, size * S2), fill=fill, anchor=anchor)
    def circ(self, c, r, **k): self.el((c[0] - r, c[1] - r, c[0] + r, c[1] + r), **k)

def xmark(P, cx, cy, sz, col, w=18):
    P.ln([(cx - sz, cy - sz), (cx + sz, cy + sz)], col, w); P.ln([(cx + sz, cy - sz), (cx - sz, cy + sz)], col, w)

def check(P, cx, cy, sz, col, w=14):
    P.ln([(cx - sz, cy), (cx - sz * 0.3, cy + sz * 0.7), (cx + sz, cy - sz * 0.7)], col, w)

def steam(P, cx, top, lt, n=3, h=90, col=(220, 220, 215, 160)):
    for i in range(n):
        x0 = cx + (i - (n - 1) / 2) * 46; ph = lt * 5 + i
        pts = [(x0 + 12 * math.sin(ph + k * 0.9), top - k * (h / 6)) for k in range(7)]
        P.ln(pts, col, 8)

def thali(P, cx, cy, r, lt):
    P.circ((cx, cy), r, fill=(200, 202, 205)); P.circ((cx, cy), r * 0.9, fill=(226, 228, 230))
    P.el((cx - r * 0.55, cy - r * 0.2, cx + r * 0.25, cy + r * 0.55), fill=(236, 190, 90))   # biryani
    for k in range(14):
        a = k * 2.4; rr = r * (0.12 + 0.2 * ((k * 37) % 10) / 10)
        P.circ((cx - r * 0.15 + math.cos(a) * rr, cy + r * 0.17 + math.sin(a) * rr), r * 0.05, fill=(250, 245, 230))
    for i, (dx, dy, col) in enumerate([(0.42, -0.35, (190, 80, 40)), (0.5, 0.15, (230, 160, 40)), (-0.1, -0.55, (150, 60, 30))]):
        P.circ((cx + r * dx, cy + r * dy), r * 0.2, fill=(180, 182, 186)); P.circ((cx + r * dx, cy + r * dy), r * 0.16, fill=col)
    P.el((cx + r * 0.05, cy + r * 0.45, cx + r * 0.5, cy + r * 0.72), fill=(245, 225, 170))  # papad-ish

def chai(P, cx, by, sc, lt):
    w0, w1, h = 70 * sc, 54 * sc, 170 * sc
    P.pg([(cx - w0, by - h), (cx + w0, by - h), (cx + w1, by), (cx - w1, by)], fill=(235, 240, 245, 230))
    P.pg([(cx - w0 * 0.93, by - h * 0.82), (cx + w0 * 0.93, by - h * 0.82), (cx + w1 * 0.95, by - 6), (cx - w1 * 0.95, by - 6)], fill=(196, 140, 84))
    for k in range(4): P.ln([(cx - w0 * 0.9 + k * 0, by - h + 20 * sc + k * 34 * sc), (cx + w0 * 0.9, by - h + 20 * sc + k * 34 * sc)], (255, 255, 255, 70), 3)
    steam(P, cx, by - h - 20, lt)

def samosa(P, cx, cy, s, rot=0):
    pts = [(0, -1.0), (0.95, 0.65), (-0.95, 0.65)]
    c, sn = math.cos(rot), math.sin(rot)
    P.pg([(cx + s * (x * c - y * sn), cy + s * (x * sn + y * c)) for x, y in pts], fill=(222, 160, 70))
    pts2 = [(0, -0.75), (0.68, 0.45), (-0.68, 0.45)]
    P.pg([(cx + s * (x * c - y * sn), cy + s * (x * sn + y * c)) for x, y in pts2], fill=(236, 182, 92))
    for k in range(6):
        a = k * 1.1; P.circ((cx + s * 0.25 * math.cos(a), cy + s * 0.1 + s * 0.2 * math.sin(a)), s * 0.04, fill=(190, 120, 50))

def laptop(P, cx, cy, sc):
    P.rr((cx - 210 * sc, cy - 260 * sc, cx + 210 * sc, cy), 18, fill=(60, 64, 70))
    P.rr((cx - 190 * sc, cy - 242 * sc, cx + 190 * sc, cy - 18 * sc), 10, fill=(32, 90, 140))
    for k in range(5): P.rr((cx - 160 * sc, cy - 215 * sc + k * 40 * sc, cx + (40 + 30 * (k % 3)) * sc, cy - 200 * sc + k * 40 * sc), 6, fill=(110, 170, 220))
    P.pg([(cx - 260 * sc, cy), (cx + 260 * sc, cy), (cx + 230 * sc, cy + 30 * sc), (cx - 230 * sc, cy + 30 * sc)], fill=(90, 94, 100))

def mealbox(P, cx, cy, sc):
    P.rr((cx - 150 * sc, cy - 95 * sc, cx + 150 * sc, cy + 95 * sc), 26, fill=(250, 250, 246))
    P.rr((cx - 150 * sc, cy - 95 * sc, cx + 150 * sc, cy - 45 * sc), 26, fill=LIME)
    P.tx((cx, cy - 70 * sc), "FITEATS", ANTON, int(36 * sc), BG)
    P.el((cx - 120 * sc, cy - 30 * sc, cx - 10 * sc, cy + 70 * sc), fill=(250, 245, 230))
    P.rr((cx + 0 * sc, cy - 30 * sc, cx + 120 * sc, cy + 20 * sc), 20, fill=(214, 150, 90))
    for k in range(4): P.circ((cx + (20 + k * 28) * sc, cy + 50 * sc), 16 * sc, fill=(80, 170, 80))

CAL = [(40, 0.42), (41, 0.62), (42, 0.86), (43, 0.92), (44, 1.18)]
def calbar(P, t):
    # persistent calorie meter across the problem section
    lvl = 0.0
    for pid, v in CAL:
        s = next(x for x in scenes if x['prop'] == pid)
        if t >= s['t0']: lvl = max(lvl, v * eo((t - s['t0']) / 0.35) + (lvl if False else 0))
    prev = 0.0
    for pid, v in CAL:
        s = next(x for x in scenes if x['prop'] == pid)
        if t >= s['t0']:
            prev2 = v; a = eo((t - s['t0']) / 0.35); lvl = prev + (prev2 - prev) * a; prev = prev2
    x0, x1, y = 120, 840, 40
    P.rr((x0, y, x1, y + 44), 22, fill=(48, 52, 58))
    fillw = (x1 - x0) * min(lvl, 1.0)
    col = LIME if lvl < 0.6 else GOLD if lvl < 0.9 else CORAL
    if fillw > 30: P.rr((x0, y, x0 + fillw, y + 44), 22, fill=col)
    P.tx((x0 + 18, y + 22), "CALORIES", INTER, 24, BG if fillw > 200 else WHITE, anchor="lm")
    if lvl > 1.0:
        sh = 6 * math.sin(t * 60)
        P.rr((x1 + 16 + sh, y - 6, x1 + 150 + sh, y + 50), 22, fill=CORAL); P.tx((x1 + 83 + sh, y + 22), "OVER!", ANTON, 34, WHITE)

def prop(pid, t, s):
    lt = t - s['t0']; P = L(); cx = 540
    if pid in (40, 41, 42, 43, 44): calbar(P, t)
    if pid == 40:
        a = eb(lt / 0.28); y = 330 - 260 * (1 - eo(lt / 0.2))
        thali(P, cx, y, 210 * a, lt); steam(P, cx, y - 230, lt, n=4, h=110)
        if lt > 0.2: P.rr((cx - 190, 570, cx + 190, 630), 30, fill=CORAL); P.tx((cx, 600), "HEAVY LUNCH", ANTON, 44, WHITE)
    elif pid == 41:
        thali(P, 200, 380, 120, lt)
        a = eb(lt / 0.25); chai(P, 640, 560, 1.4 * a, lt)
        P.tx((640, 590 if False else 120), "+ CHAI", ANTON, int(70 * max(a, 0.01)), GOLD)
    elif pid == 42:
        thali(P, 170, 400, 100, lt); chai(P, 420, 560, 1.0, lt)
        a = eb(lt / 0.25)
        samosa(P, 760, 400, 130 * a, 0.15 * math.sin(lt * 6)); samosa(P, 900, 470, 90 * eb((lt - 0.12) / 0.25), -0.4)
        P.tx((800, 140), "+ SAMOSA", ANTON, int(70 * max(a, 0.01)), GOLD)
    elif pid == 43:
        a = eb(lt / 0.25); R = 210 * a; cy0 = 340
        P.circ((cx, cy0), R + 14, fill=CORAL); P.circ((cx, cy0), R, fill=(245, 245, 240))
        for k in range(12):
            ang = k * math.pi / 6; P.ln([(cx + math.cos(ang) * R * 0.82, cy0 + math.sin(ang) * R * 0.82), (cx + math.cos(ang) * R * 0.92, cy0 + math.sin(ang) * R * 0.92)], BG, 8)
        spin = (1 - eo(lt / 0.45))
        hang = math.radians(-90 + 120 + spin * 360); mang = math.radians(-90 + spin * 1440)
        P.ln([(cx, cy0), (cx + math.cos(hang) * R * 0.5, cy0 + math.sin(hang) * R * 0.5)], BG, 16)
        P.ln([(cx, cy0), (cx + math.cos(mang) * R * 0.75, cy0 + math.sin(mang) * R * 0.75)], BG, 10)
        P.circ((cx, cy0), 16, fill=BG)
        P.rr((cx - 120, 585, cx + 120, 640), 28, fill=GOLD); P.tx((cx, 612), "4 PM", ANTON, 42, BG)
    elif pid == 44:
        items = 7; base = 610
        for k in range(items):
            a = eb((lt - k * 0.08) / 0.22)
            if a <= 0: continue
            wob = math.sin(lt * 8 + k) * (k * 1.6) * cl((lt - 0.6) / 0.3)
            y = base - k * 58 - 260 * (1 - eo((lt - k * 0.08) / 0.2))
            c = [(236, 190, 90), (196, 140, 84), (222, 160, 70)][k % 3]
            P.rr((cx - 150 + wob, y - 52, cx + 150 + wob, y), 18, fill=c)
            P.tx((cx + wob, y - 26), ["LUNCH", "CHAI", "SAMOSA"][k % 3], INTER, 24, BG)
    elif pid == 45:
        laptop(P, 420, 520, 1.05)
        a = eo(lt / 0.35); bx = 1200 - 420 * a
        mealbox(P, bx, 420, 1.0)
        if lt > 0.4:
            b = eb((lt - 0.4) / 0.2); P.circ((bx + 130, 300), 44 * b, fill=LIME); check(P, bx + 130, 300, 22 * b, BG, 10)
    elif pid == 46:
        a = eb(lt / 0.3); bob = 14 * math.sin(lt * 7)
        for k in range(6):
            P.ln([(80 + k * 190, 520), (180 + k * 170, 620)], (60, 66, 72), 6)
        P.el((cx - 160, 540, cx + 160, 600), fill=(10, 12, 14, 120))
        r = 120 * a; py = 300 + bob
        P.pg([(cx - r * 0.8, py + r * 0.5), (cx + r * 0.8, py + r * 0.5), (cx, py + r * 2.0)], fill=CORAL)
        P.circ((cx, py), r, fill=CORAL); P.circ((cx, py), r * 0.42, fill=WHITE)
        P.tx((cx, 90), "CHENNAI", ANTON, int(80 * max(a, 0.01)), LIME)
    elif pid == 47:
        a = eb(lt / 0.22)
        P.circ((cx - 40, 340), 170 * a, fill=(70, 74, 80)); P.circ((cx - 40, 340), 140 * a, fill=(40, 43, 48))
        P.rr((cx + 110 * a, 320, cx + 380 * a, 360), 20, fill=(70, 74, 80))
        b = eb((lt - 0.22) / 0.2)
        if b > 0: P.circ((cx - 40, 340), 210 * b, outline=CORAL, w=16); xmark(P, cx - 40, 340, 120 * b, CORAL, 22)
        P.tx((cx, 600), "NO COOKING", ANTON, 52, WHITE)
    elif pid == 48:
        a = eb(lt / 0.22)
        P.rr((cx - 140 * a, 160, cx + 140 * a, 540), 28, fill=(70, 74, 80))
        P.rr((cx - 110 * a, 190, cx + 110 * a, 270), 12, fill=(160, 200, 150))
        P.tx((cx, 232), "2,340" if a > 0.6 else "", INTER, 40, BG)
        for r_ in range(3):
            for c_ in range(3):
                P.rr((cx - 100 * a + c_ * 72 * a, 300 + r_ * 75, cx - 50 * a + c_ * 72 * a, 355 + r_ * 75), 10, fill=(110, 116, 122))
        b = eb((lt - 0.22) / 0.2)
        if b > 0: P.circ((cx, 350), 230 * b, outline=CORAL, w=16); xmark(P, cx, 350, 130 * b, CORAL, 22)
        P.tx((cx, 600), "NO COUNTING", ANTON, 52, WHITE)
    elif pid == 49:
        a = eb(lt / 0.3); pulse = 1 + 0.04 * math.sin(lt * 7)
        bw, bh = 440 * a * pulse, 74 * a * pulse
        P.rr((cx - bw, 150 - bh, cx + bw, 150 + bh), int(bh), fill=WA)
        if a > 0.7:
            P.circ((cx - bw + 75, 150), 42, fill=WHITE); P.circ((cx - bw + 75, 150), 32, fill=WA)
            P.pg([(cx - bw + 48, 182), (cx - bw + 44, 200), (cx - bw + 66, 188)], fill=WHITE)
            P.tx((cx + 40, 150), "MESSAGE US ON WHATSAPP", ANTON, 52, WHITE)
        b = eo((lt - 0.45) / 0.3)
        if b > 0: P.tx((cx, 300 + 30 * (1 - b)), "+91 73391 63082", ANTON, int(86), (245, 245, 240, int(255 * b)))
        c = eo((lt - 0.85) / 0.3)
        if c > 0:
            P.rr((cx - 290, 390, cx + 290, 470), 40, fill=(LIME[0], LIME[1], LIME[2], int(255 * c))); P.tx((cx, 430), "GET THIS WEEK'S MENU", ANTON, 46, BG)
        d = eo((lt - 1.2) / 0.3)
        if d > 0:
            ay = 560 + 14 * math.sin(lt * 8)
            P.tx((cx, ay), "LOW CALORIE · HIGH PROTEIN · CHENNAI", INTERB, 30, (200, 205, 210, int(255 * d)))
    return P.im.resize((PW, PH), Image.LANCZOS)

def caption(img, s, t, cy=650, cap=999):
    d = ImageDraw.Draw(img)
    toks = s['txt'].split(); idxs = list(range(s['i0'], s['i1']))
    n = len(toks); size = min(cap, 150 if n <= 2 else 126 if n <= 5 else 112)
    while True:
        f = F(ANTON, size); lines = [[]]; wid = 0
        for k, tk in enumerate(toks):
            w = d.textlength(tk.upper(), font=f) + 24
            if wid + w > 960 and lines[-1]: lines.append([]); wid = 0
            lines[-1].append(k); wid += w
        if len(lines) <= 3 or size < 80: break
        size -= 8
    lh = int(size * 1.12); y = cy - lh * len(lines) / 2 + lh / 2
    for ln_ in lines:
        ws = [d.textlength(toks[k].upper(), font=f) for k in ln_]; tot = sum(ws) + 24 * (len(ln_) - 1); x = 540 - tot / 2
        for k, w in zip(ln_, ws):
            st = WS[idxs[k]] if s['i0'] + k else 0.0
            if t >= st - 0.02:
                a = cl((t - st) / 0.14); sc = 1.0 + 0.22 * (1 - eo(a))
                word = toks[k].upper(); raw = toks[k].lower()
                col = CORAL if raw in CORALW else LIME if raw in LIMEW else WHITE
                tmp = Image.new("RGBA", (int(w + 80), int(size * 1.6)), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
                td.text((tmp.width / 2 + 5, tmp.height / 2 + 6), word, font=f, fill=(0, 0, 0, 150), anchor="mm")
                td.text((tmp.width / 2, tmp.height / 2), word, font=f, fill=col, anchor="mm")
                if sc != 1: tmp = tmp.resize((int(tmp.width * sc), int(tmp.height * sc)), Image.LANCZOS)
                img.paste(tmp, (int(x + w / 2 - tmp.width / 2), int(y - tmp.height / 2)), tmp)
            x += w + 24
        y += lh

def background(t, s):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    hot = s['prop'] in (40, 41, 42, 43, 44)
    col = (40, 26, 26) if hot else (28, 36, 24)
    off = (t * 60) % 90
    for i in range(-2, 24):
        y = int(i * 90 + off); d.line([(0, y), (W, y + 120)], fill=col, width=2)
    g = Image.new("RGB", (W, H), BG); gd = ImageDraw.Draw(g)
    gc = (80, 30, 28) if hot else (40, 80, 50) if s['prop'] == 49 else (46, 66, 28)
    gd.ellipse([140, 1000, 940, 1500], fill=gc); g = g.filter(ImageFilter.GaussianBlur(160))
    return Image.blend(im, g, 0.7)

PHOTO = None
def avframe(dirname, idx):
    global PHOTO
    p = f'{ROOT}/{dirname}'
    if os.path.isdir(p):
        n = len([f for f in os.listdir(p) if f.endswith('.png')])
        if n: return Image.open(f'{p}/{min(idx, n - 1):04d}.png').convert("RGBA").resize((W, H))
    if PHOTO is None: PHOTO = Image.open('/home/claude/v2/photo_hq.png').convert("RGBA").resize((W, H))
    return PHOTO.copy()

HOOK_CHIPS = [(WS[5], WS[9], "9 HRS", CORAL, "laptop"), (WS[10], WS[14], "GYM", CORAL, "x"), (WS[15], WS[17], "LUNCH", CORAL, "!"), (WS[23], AV1_END, "BURNS LESS", CORAL, "down")]
MID_CHIPS = [(WS[48], "LOW CALORIE"), (WS[50], "HIGH PROTEIN"), (WS[53], "COOKED FRESH")]

def chip(d, t, c0, lab, col, y, kind):
    a = eb((t - c0) / 0.18); f = F(ANTON, 76)
    tw = d.textlength(lab, font=f); w2 = (tw + 160) * a
    if w2 <= 10: return
    d.rounded_rectangle([540 - w2 / 2, y, 540 + w2 / 2, y + 92], 46, fill=col)
    if a > 0.8:
        tx = 540 - 30; d.text((tx, y + 46), lab, font=f, fill=WHITE if col == CORAL else BG, anchor="mm")
        xr = tx + tw / 2 + 44; ic = WHITE if col == CORAL else BG
        if kind == "x": d.line([(xr - 16, y + 30), (xr + 16, y + 62)], fill=ic, width=9); d.line([(xr + 16, y + 30), (xr - 16, y + 62)], fill=ic, width=9)
        elif kind == "check": d.line([(xr - 18, y + 46), (xr - 5, y + 60), (xr + 18, y + 30)], fill=ic, width=9)
        elif kind == "!": d.text((xr, y + 46), "!", font=f, fill=ic, anchor="mm")
        elif kind == "down": d.line([(xr, y + 26), (xr, y + 64)], fill=ic, width=9); d.polygon([(xr - 16, y + 52), (xr + 16, y + 52), (xr, y + 70)], fill=ic)
        elif kind == "laptop": d.rounded_rectangle([xr - 20, y + 30, xr + 20, y + 56], 4, outline=ic, width=6); d.line([(xr - 26, y + 62), (xr + 26, y + 62)], fill=ic, width=6)

def frame(fi):
    t = fi / FPS
    s = next((x for x in scenes if x['t0'] <= t < x['t1']), scenes[-1])
    lt = t - s['t0']
    av = s['prop'] in (98, 97)
    if av:
        img = avframe('avA', fi) if s['prop'] == 98 else avframe('avM', int((t - AV2_T0) * FPS))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for y in range(1050, 1700, 6): gd.rectangle([0, y, W, y + 6], fill=(10, 11, 13, int(200 * cl((y - 1050) / 450))))
        img.alpha_composite(g)
    else:
        img = background(t, s).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 215, 1020, 223], 4, fill=(50, 54, 60)); d.rounded_rectangle([60, 215, 60 + 960 * cl(t / DUR), 223], 4, fill=LIME)
    tw = d.textlength(TAG, font=F(INTER, 28)) + 56
    d.rounded_rectangle([60, 255, 60 + tw, 311], 28, fill=LIME); d.text((60 + tw / 2, 284), TAG, font=F(INTER, 28), fill=BG, anchor="mm")
    if s['prop'] == 98:
        for c0, c1, lab, col, kind in HOOK_CHIPS:
            if c0 <= t < c1 + 0.15: chip(d, t, c0, lab, col, 345, kind)
        caption(img, s, t, cy=1390, cap=96)
    elif s['prop'] == 97:
        for k, (c0, lab) in enumerate(MID_CHIPS):
            if t >= c0: chip(d, t, c0, lab, LIME, 345 + k * 108, "check")
        caption(img, s, t, cy=1390, cap=96)
    else:
        pl = prop(s['prop'], t, s)
        sc = 1.0 + (0.12 * (1 - eo(lt / 0.16)) if s['punch'] else 0.0) + 0.03 * eo(lt / 1.5)
        rnd = random.Random(int(t * 30))
        shake = (rnd.uniform(-7, 7), rnd.uniform(-7, 7)) if (s['prop'] in (40, 44, 47, 48) and lt < 0.28) else (0, 0)
        if sc != 1.0: pl = pl.resize((int(PW * sc), int(PH * sc)), Image.LANCZOS)
        img.alpha_composite(pl, (int(540 - pl.width / 2 + shake[0]), int(PY + PH / 2 - pl.height / 2 + shake[1])))
        caption(img, s, t)
    if lt < 0.07 and s['punch'] and fi > 0:
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(80 * (1 - lt / 0.07)))); img.alpha_composite(fl)
    return img.convert("RGB")

def render(fi): return frame(fi).tobytes()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        for tt in map(float, sys.argv[2:]):
            frame(int(tt * FPS)).save(f"{ROOT}/still_{tt:05.2f}.png")
    elif mode == "cuts":
        print(json.dumps([[round(s['t0'], 3), s['prop'], s['punch']] for s in scenes]))
    else:
        n = int(DUR * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"{ROOT}/silent.mp4"], stdin=subprocess.PIPE)
        with Pool(2) as pool:
            for b in pool.imap(render, range(n), chunksize=6): p.stdin.write(b)
        p.stdin.close(); p.wait()
