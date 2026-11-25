"""FitEats - Idli protein fix, in the "Reality Check" style of the Nobody Budgets reel.
Phrase headlines (Anton, drop shadow, coral/lime keywords), top progress bar, lime tag pill,
flat outlined illustrations over a soft radial glow. Sprites are drawn 3x and downsampled.
python3 build2.py stills t...  |  python3 build2.py render
"""
import math, os, random, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BG = (21, 22, 27); TXT = (244, 241, 234); GREY = (150, 150, 158); DARK = (43, 46, 54)
LIME = (201, 236, 74); CORAL = (255, 107, 91); OUT = (244, 242, 236); INK = (18, 18, 22)
GF = "/usr/share/fonts/truetype/google-fonts/ofl/"; FD = "/usr/share/fonts/opentype/inter/"
TOTAL = 36.3
SS = 3  # supersampling for sprites

@lru_cache(None)
def F(k, s):
    return ImageFont.truetype({"anton": GF + "anton/Anton-Regular.ttf", "bold": FD + "InterDisplay-Bold.otf",
                               "black": FD + "InterDisplay-Black.otf", "med": FD + "InterDisplay-Medium.otf"}[k], s)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.6
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def prog(t, t0, d=0.3): return ease((t - t0) / d)

# ---------------------------------------------------------------- sprites
def sprite(w, h, fn):
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), SS, im)
    return im.resize((w, h), Image.LANCZOS)

def vgrad(im, box, top, bot, mask=None):
    x0, y0, x1, y1 = [int(v) for v in box]
    g = Image.new("RGBA", (x1 - x0, y1 - y0))
    gd = ImageDraw.Draw(g)
    for y in range(y1 - y0):
        k = y / max(1, y1 - y0 - 1)
        gd.line([(0, y), (x1 - x0, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
    if mask is not None:
        im.paste(g, (x0, y0), mask.crop((x0, y0, x1, y1)))
    else:
        im.alpha_composite(g, (x0, y0))

def shape_mask(size, draw_fn):
    m = Image.new("L", size, 0); draw_fn(ImageDraw.Draw(m)); return m

def leaf(w=820, h=380):
    def fn(d, k, im):
        cx, cy = w * k / 2, h * k / 2
        box = (20 * k, 30 * k, (w - 20) * k, (h - 30) * k)
        d.ellipse((box[0] + 10 * k, box[1] + 24 * k, box[2] + 10 * k, box[3] + 24 * k), fill=(0, 0, 0, 110))
        m = shape_mask(im.size, lambda md: md.ellipse(box, fill=255))
        vgrad(im, box, (92, 168, 74), (46, 112, 50), m)
        d.line([(box[0] + 40 * k, cy), (box[2] - 40 * k, cy)], fill=(150, 206, 110, 255), width=int(6 * k))
        for i in range(1, 9):
            x = box[0] + (box[2] - box[0]) * i / 9
            for sgn in (-1, 1):
                d.line([(x, cy), (x + 70 * k, cy + sgn * 110 * k)], fill=(104, 176, 84, 255), width=int(3 * k))
        d.ellipse(box, outline=(30, 86, 38, 255), width=int(5 * k))
    return sprite(w, h, fn)

def idli(w=210, h=140):
    def fn(d, k, im):
        d.ellipse((14 * k, 70 * k, (w - 6) * k, (h - 4) * k), fill=(0, 0, 0, 90))
        body = (8 * k, 18 * k, (w - 14) * k, (h - 16) * k)
        m = shape_mask(im.size, lambda md: md.ellipse(body, fill=255))
        vgrad(im, body, (255, 253, 246), (222, 214, 196), m)
        d.ellipse((40 * k, 30 * k, (w - 70) * k, 70 * k), fill=(252, 250, 244, 255))
        rnd = random.Random(3)
        for _ in range(14):
            x = rnd.uniform(40, w - 50) * k; y = rnd.uniform(56, h - 40) * k; r = rnd.uniform(2, 4) * k
            d.ellipse((x - r, y - r, x + r, y + r), fill=(205, 196, 176, 255))
        d.ellipse(body, outline=OUT + (255,), width=int(5 * k))
    return sprite(w, h, fn)

def dosa(w=640, h=260):
    def fn(d, k, im):
        pts = [(30 * k, 150 * k), ((w - 80) * k, 40 * k), ((w - 60) * k, 220 * k)]
        d.polygon([(x + 10 * k, y + 18 * k) for x, y in pts], fill=(0, 0, 0, 100))
        m = shape_mask(im.size, lambda md: md.polygon(pts, fill=255))
        vgrad(im, (0, 40 * k, w * k, 220 * k), (250, 196, 96), (200, 120, 40), m)
        rnd = random.Random(5)
        for _ in range(60):
            x = rnd.uniform(80, w - 110); f = (x - 30) / (w - 110)
            ytop = 150 - 110 * f; ybot = 150 + 70 * f
            y = rnd.uniform(ytop + 6, ybot - 6)
            d.line([(x * k, y * k), ((x + rnd.uniform(10, 26)) * k, (y + rnd.uniform(-3, 3)) * k)], fill=(190, 114, 40, 255), width=int(3 * k))
        d.line(pts + [pts[0]], fill=OUT + (255,), width=int(5 * k), joint="curve")
        end = ((w - 120) * k, 40 * k, (w - 10) * k, 220 * k)
        me = shape_mask(im.size, lambda md: md.ellipse(end, fill=255))
        vgrad(im, end, (236, 170, 70), (186, 108, 36), me)
        d.ellipse(((w - 96) * k, 70 * k, (w - 34) * k, 190 * k), fill=(150, 84, 26, 255))
        d.ellipse(end, outline=OUT + (255,), width=int(5 * k))
    return sprite(w, h, fn)

def bowl(fill_top, fill_bot, specks=None, w=300, h=220, temper=False):
    def fn(d, k, im):
        d.ellipse((30 * k, 150 * k, (w - 10) * k, (h - 4) * k), fill=(0, 0, 0, 100))
        body = (14 * k, 40 * k, (w - 14) * k, (h - 20) * k)
        m = shape_mask(im.size, lambda md: md.pieslice((body[0], body[1] - 60 * k, body[2], body[3]), 0, 180, fill=255))
        vgrad(im, (body[0], body[1], body[2], body[3]), (206, 210, 218), (120, 124, 134), m)
        rim = (14 * k, 26 * k, (w - 14) * k, 86 * k)
        d.ellipse(rim, fill=(226, 230, 236, 255))
        inner = (30 * k, 34 * k, (w - 30) * k, 80 * k)
        mi = shape_mask(im.size, lambda md: md.ellipse(inner, fill=255))
        vgrad(im, inner, fill_top, fill_bot, mi)
        if specks:
            rnd = random.Random(len(specks))
            for col, n, r in specks:
                for _ in range(n):
                    a = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0, 0.82)
                    x = w * k / 2 + math.cos(a) * rr * (w - 70) * k / 2; y = 57 * k + math.sin(a) * rr * 18 * k
                    d.ellipse((x - r * k, y - r * k * 0.8, x + r * k, y + r * k * 0.8), fill=col + (255,))
        if temper:
            for x, y in ((0.36, 0.0), (0.62, 0.02)):
                cx = w * k * x; cy = 52 * k + y
                d.ellipse((cx - 16 * k, cy - 6 * k, cx + 16 * k, cy + 6 * k), fill=(52, 120, 46, 255))
        d.ellipse(rim, outline=OUT + (255,), width=int(5 * k))
        d.arc((body[0], body[1] - 60 * k, body[2], body[3]), 0, 180, fill=OUT + (255,), width=int(5 * k))
    return sprite(w, h, fn)

def mixer(w=330, h=560):
    def fn(d, k, im):
        d.ellipse((40 * k, (h - 40) * k, (w - 30) * k, (h - 4) * k), fill=(0, 0, 0, 110))
        jar = [(40 * k, 70 * k), ((w - 70) * k, 70 * k), ((w - 90) * k, 360 * k), (60 * k, 360 * k)]
        mj = shape_mask(im.size, lambda md: md.polygon(jar, fill=255))
        vgrad(im, (40 * k, 70 * k, (w - 70) * k, 360 * k), (88, 96, 110), (60, 66, 78), mj)
        batter = [(52 * k, 220 * k), ((w - 82) * k, 220 * k), ((w - 92) * k, 356 * k), (62 * k, 356 * k)]
        mb = shape_mask(im.size, lambda md: md.polygon(batter, fill=255))
        vgrad(im, (52 * k, 220 * k, (w - 82) * k, 356 * k), (250, 236, 196), (226, 200, 140), mb)
        rnd = random.Random(9)
        for _ in range(26):
            x = rnd.uniform(70, w - 110) * k; y = rnd.uniform(236, 340) * k; r = rnd.uniform(3, 6) * k
            col = (232, 190, 70) if rnd.random() < 0.5 else (120, 168, 70)
            d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))
        d.polygon([(60 * k, 90 * k), (84 * k, 90 * k), (96 * k, 340 * k), (78 * k, 340 * k)], fill=(110, 118, 132, 255))
        d.line(jar + [jar[0]], fill=OUT + (255,), width=int(6 * k), joint="curve")
        d.rounded_rectangle((26 * k, 40 * k, (w - 56) * k, 78 * k), int(12 * k), fill=(36, 38, 44, 255), outline=OUT + (255,), width=int(5 * k))
        d.arc(((w - 110) * k, 110 * k, (w - 10) * k, 300 * k), 270, 90, fill=OUT + (255,), width=int(16 * k))
        base = (30 * k, 360 * k, (w - 50) * k, (h - 30) * k)
        mbase = shape_mask(im.size, lambda md: md.rounded_rectangle(base, int(26 * k), fill=255))
        vgrad(im, base, (236, 238, 242), (196, 198, 206), mbase)
        d.rounded_rectangle(base, int(26 * k), outline=OUT + (255,), width=int(5 * k))
        cx = (w - 20) * k / 2; cy = (360 + h - 30) * k / 2
        d.ellipse((cx - 38 * k, cy - 38 * k, cx + 38 * k, cy + 38 * k), fill=(50, 54, 62, 255), outline=(30, 30, 36, 255), width=int(4 * k))
        d.line([(cx, cy), (cx + 20 * k, cy - 26 * k)], fill=LIME + (255,), width=int(7 * k))
    return sprite(w, h, fn)

def peanuts(w=520, h=300):
    def fn(d, k, im):
        rnd = random.Random(21)
        d.ellipse((40 * k, (h - 70) * k, (w - 40) * k, (h - 10) * k), fill=(0, 0, 0, 90))
        for i in range(46):
            x = rnd.uniform(70, w - 70); y = rnd.uniform(70, h - 50) + abs(x - w / 2) * 0.25
            a = rnd.uniform(0, math.pi)
            rx, ry = 26, 17
            pts = [(x + math.cos(a) * rx * math.cos(u) - math.sin(a) * ry * math.sin(u),
                    y + math.sin(a) * rx * math.cos(u) + math.cos(a) * ry * math.sin(u)) for u in [j * math.pi / 18 for j in range(36)]]
            d.polygon([(px * k, py * k) for px, py in pts], fill=(214, 160, 100, 255), outline=(150, 96, 52, 255))
            d.ellipse(((x - 8) * k, (y - 8) * k, (x - 1) * k, (y - 2) * k), fill=(240, 200, 150, 255))
    return sprite(w, h, fn)

def meter(level, col, w=760, h=150):
    def fn(d, k, im):
        d.rounded_rectangle((10 * k, 60 * k, (w - 10) * k, 120 * k), int(30 * k), fill=DARK + (255,), outline=OUT + (255,), width=int(5 * k))
        if level > 0.02:
            d.rounded_rectangle((22 * k, 72 * k, (22 + (w - 44) * level) * k, 108 * k), int(18 * k), fill=col + (255,))
        for i in range(1, 5):
            x = (22 + (w - 44) * i / 5) * k
            d.line([(x, 76 * k), (x, 104 * k)], fill=(30, 32, 38, 255), width=int(3 * k))
    return sprite(w, h, fn)

def badge(text, col, fg=INK, size=240):
    def fn(d, k, im):
        d.ellipse((14 * k, 22 * k, (size - 6) * k, (size + 2) * k), fill=(0, 0, 0, 110))
        d.ellipse((8 * k, 8 * k, (size - 12) * k, (size - 12) * k), fill=col + (255,), outline=OUT + (255,), width=int(6 * k))
        f = F("anton", int(size * 0.3 * k))
        d.text(((size - 4) * k / 2, (size - 6) * k / 2), text, font=f, fill=fg + (255,), anchor="mm")
    return sprite(size, size, fn)

def pill(text, col, fg=INK, size=56, pad=44, icon=None):
    f0 = F("anton", size); tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f0))
    iw = int(size * 1.3) if icon else 0
    w, h = tw + pad * 2 + iw, int(size * 2.0)
    def fn(d, k, im):
        d.rounded_rectangle((6 * k, 14 * k, (w - 2) * k, (h + 2) * k), int(h * k / 2), fill=(0, 0, 0, 110))
        d.rounded_rectangle((2 * k, 2 * k, (w - 8) * k, (h - 8) * k), int(h * k / 2), fill=col + (255,), outline=OUT + (255,), width=int(5 * k))
        x = (pad + iw) * k
        if icon == "wa":
            cx, cy, r = (pad + size * 0.45) * k, (h - 8) * k / 2, size * 0.5 * k
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fg + (255,), width=int(6 * k))
            d.polygon([(cx - r * 0.85, cy + r * 0.55), (cx - r * 1.1, cy + r * 1.15), (cx - r * 0.35, cy + r * 0.9)], fill=fg + (255,))
            d.arc((cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5), 100, 250, fill=fg + (255,), width=int(7 * k))
        if icon == "plus":
            cx, cy = (pad + size * 0.45) * k, (h - 8) * k / 2
            d.line([(cx - 18 * k, cy), (cx + 18 * k, cy)], fill=fg + (255,), width=int(8 * k))
            d.line([(cx, cy - 18 * k), (cx, cy + 18 * k)], fill=fg + (255,), width=int(8 * k))
        d.text((x, (h - 8) * k / 2), text, font=F("anton", size * k), fill=fg + (255,), anchor="lm")
    return sprite(w, h, fn)

def bookmark(w=240, h=320):
    def fn(d, k, im):
        pts = [(30, 20), (w - 30, 20), (w - 30, h - 20), (w / 2, h - 90), (30, h - 20)]
        d.polygon([((x + 10) * k, (y + 16) * k) for x, y in pts], fill=(0, 0, 0, 100))
        d.polygon([(x * k, y * k) for x, y in pts], fill=LIME + (255,))
        d.line([(x * k, y * k) for x, y in pts + [pts[0]]], fill=OUT + (255,), width=int(6 * k), joint="curve")
    return sprite(w, h, fn)

def clock(size=360):
    def fn(d, k, im):
        c = size * k / 2; r = (size / 2 - 20) * k
        d.ellipse((c - r + 10 * k, c - r + 16 * k, c + r + 10 * k, c + r + 16 * k), fill=(0, 0, 0, 100))
        d.ellipse((c - r, c - r, c + r, c + r), fill=DARK + (255,), outline=OUT + (255,), width=int(8 * k))
        for i in range(12):
            a = i * math.pi / 6
            d.line([(c + math.cos(a) * r * 0.78, c + math.sin(a) * r * 0.78), (c + math.cos(a) * r * 0.9, c + math.sin(a) * r * 0.9)], fill=GREY + (255,), width=int(6 * k))
        d.line([(c, c), (c, c - r * 0.6)], fill=OUT + (255,), width=int(12 * k))
        d.line([(c, c), (c + r * 0.45, c + r * 0.2)], fill=CORAL + (255,), width=int(12 * k))
        d.ellipse((c - 14 * k, c - 14 * k, c + 14 * k, c + 14 * k), fill=OUT + (255,))
    return sprite(size, size, fn)

def cross(size=300):
    def fn(d, k, im):
        for a, b in (((40, 40), (size - 40, size - 40)), ((size - 40, 40), (40, size - 40))):
            d.line([(a[0] * k, a[1] * k), (b[0] * k, b[1] * k)], fill=CORAL + (255,), width=int(26 * k))
    return sprite(size, size, fn)

def sparkle(size=120, col=LIME):
    def fn(d, k, im):
        c = size * k / 2
        pts = []
        for i in range(8):
            r = (size / 2 - 6) * k if i % 2 == 0 else size * 0.12 * k
            a = i * math.pi / 4 - math.pi / 2
            pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
        d.polygon(pts, fill=col + (255,))
    return sprite(size, size, fn)

def check(size=200):
    def fn(d, k, im):
        c = size * k / 2; r = (size / 2 - 10) * k
        d.ellipse((c - r, c - r, c + r, c + r), fill=LIME + (255,), outline=OUT + (255,), width=int(6 * k))
        d.line([(c - r * 0.45, c), (c - r * 0.1, c + r * 0.35), (c + r * 0.5, c - r * 0.35)], fill=INK + (255,), width=int(16 * k), joint="curve")
    return sprite(size, size, fn)

def follow_card(w=720, h=300):
    def fn(d, k, im):
        d.rounded_rectangle((12 * k, 20 * k, (w - 2) * k, (h + 6) * k), int(40 * k), fill=(0, 0, 0, 110))
        d.rounded_rectangle((4 * k, 4 * k, (w - 10) * k, (h - 10) * k), int(40 * k), fill=DARK + (255,), outline=OUT + (255,), width=int(5 * k))
        cx, cy, r = 120 * k, (h - 10) * k / 2, 72 * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LIME + (255,))
        d.text((cx, cy), "FE", font=F("anton", int(60 * k)), fill=INK + (255,), anchor="mm")
        d.text((230 * k, cy - 34 * k), "@fit_eats_25", font=F("bold", int(46 * k)), fill=TXT + (255,), anchor="lm")
        d.text((230 * k, cy + 30 * k), "High-protein meals · Chennai", font=F("med", int(30 * k)), fill=GREY + (255,), anchor="lm")
    return sprite(w, h, fn)

def tomato_bowl(): return bowl((236, 86, 58), (196, 52, 36), [((255, 150, 120), 10, 4)])
def gnut_bowl(): return bowl((214, 170, 110), (176, 128, 74), [((140, 96, 54), 22, 3), ((40, 40, 40), 10, 3)], temper=True)
def dal_bowl(col, dark, oval):
    return bowl(col, dark, [((255, 235, 160) if not oval else (170, 210, 110), 26, 6 if not oval else 5)])

SP = {}
def build_sprites():
    SP.update(leaf=leaf(), idli=idli(), dosa=dosa(), tomato=tomato_bowl(), gnut=gnut_bowl(),
              chana=dal_bowl((236, 196, 80), (206, 160, 48), False), moong=dal_bowl((132, 178, 78), (96, 140, 52), True),
              mixer=mixer(), peanuts=peanuts(), meter_low=meter(0.12, CORAL), meter_mid=meter(0.5, LIME),
              meter_hi=meter(0.92, LIME), b10=badge("~10g", CORAL), b5=badge("+5g", LIME), bfix=badge("FIX", LIME),
              bookmark=bookmark(), clock=clock(), cross=cross(), spark=sparkle(), check=check(),
              follow=follow_card(), wa=pill("ORDER ON WHATSAPP", LIME, icon="wa"), bio=pill("LINK IN BIO", OUT, size=44),
              follow_btn=pill("FOLLOW", LIME, size=50, icon="plus"))

@lru_cache(4096)
def scaled(name, s):
    im = SP[name]
    if abs(s - 1) < 0.01: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)

def put(canvas, name, cx, cy, s=1.0, a=1.0):
    if a <= 0.01 or s <= 0.02: return
    im = scaled(name, round(s, 2))
    if a < 0.99:
        im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------------------------------------------------------------- background glow
@lru_cache(8)
def bg(glow):
    im = Image.new("RGBA", (W, H), BG + (255,))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse((90, 700, W - 90, 1660), fill=glow + (70,))
    g = g.filter(ImageFilter.GaussianBlur(160))
    im.alpha_composite(g)
    return im

GLOW = {"warm": (120, 60, 30), "red": (130, 36, 30), "lime": (70, 100, 24), "neutral": (60, 60, 70)}

# ---------------------------------------------------------------- headline
def parse(markup):
    out = []; col = TXT
    for tok in markup.replace("{", " { ").replace("}", " } ").replace("[", " [ ").replace("]", " ] ").split():
        if tok == "{": col = LIME
        elif tok == "[": col = CORAL
        elif tok in ("}", "]"): col = TXT
        else: out.append((tok, col))
    return out

@lru_cache(64)
def headline_img(markup, size=150):
    words = parse(markup)
    f = F("anton", size); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines, cur = [], []
    for w, c in words:
        test = " ".join(x for x, _ in cur + [(w, c)])
        if d0.textlength(test, font=f) > 940 and cur: lines.append(cur); cur = []
        cur.append((w, c))
    if cur: lines.append(cur)
    lh = int(size * 1.08)
    im = Image.new("RGBA", (W, lh * len(lines) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sp = d0.textlength(" ", font=f)
    for li, ln in enumerate(lines):
        tw = sum(d0.textlength(w, font=f) for w, _ in ln) + sp * (len(ln) - 1)
        x = (W - tw) / 2; y = li * lh
        for w, c in ln:
            d.text((x + 6, y + 8), w, font=f, fill=(0, 0, 0, 255))
            d.text((x, y), w, font=f, fill=c + (255,))
            x += d0.textlength(w, font=f) + sp
    if size > 110 and len(lines) > 2: return headline_img(markup, size - 18)
    return im

@lru_cache(512)
def headline_scaled(markup, s):
    im = headline_img(markup)
    if abs(s - 1) < 0.01: return im
    return im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)

# ---------------------------------------------------------------- scenes
# (start, headline markup, glow, scene-key)
SC = [
 (0.00, "IDLI AND DOSA", "warm", "hero"),
 (0.95, "IDLI AND DOSA {AREN'T THE ENEMY}", "warm", "hero"),
 (2.05, "THE PROBLEM IS", "red", "low"),
 (3.45, "HOW LITTLE [PROTEIN] THEY HAVE", "red", "low"),
 (5.55, "4 IDLIS", "warm", "four"),
 (6.85, "ONLY [~10 g PROTEIN]", "red", "four10"),
 (8.90, "HERE'S A {SIMPLE FIX}", "lime", "fix"),
 (10.40, "GRIND SOAKED {CHANA} OR {MOONG DAL}", "warm", "dal"),
 (12.95, "ADD IT TO YOUR {IDLI BATTER}", "lime", "mixer"),
 (14.60, "{MORE PROTEIN} IN EVERY IDLI", "lime", "mid"),
 (16.90, "SWAP [TOMATO CHUTNEY]", "red", "tomato"),
 (18.65, "FOR {GROUNDNUT CHUTNEY}", "lime", "gnut"),
 (20.20, "A HANDFUL OF PEANUTS", "warm", "peanuts"),
 (21.65, "{+5 g} PROTEIN", "lime", "peanuts5"),
 (23.35, "SAME BREAKFAST YOU LOVE", "warm", "final"),
 (24.85, "NOW {HIGH-PROTEIN}", "lime", "finalhi"),
 (27.45, "{SAVE} THIS VIDEO", "lime", "save"),
 (28.60, "FOLLOW {FITEATS}", "lime", "follow"),
 (30.80, "NO TIME TO COOK HEALTHY?", "neutral", "clock"),
 (32.25, "ORDER ON {WHATSAPP}", "lime", "cta"),
]

def scene_at(t):
    i = max(j for j, s in enumerate(SC) if s[0] <= t)
    return i, SC[i]

def scene_start(key_idx):
    """start of the run of consecutive scenes sharing a visual group"""
    groups = {"hero": "hero", "low": "low", "four": "four", "four10": "four", "fix": "fix", "dal": "dal", "mixer": "mixer",
              "mid": "mid", "tomato": "tomato", "gnut": "gnut", "peanuts": "pea", "peanuts5": "pea", "final": "final",
              "finalhi": "final", "save": "save", "follow": "follow", "clock": "clock", "cta": "cta"}
    g = groups[SC[key_idx][3]]; i = key_idx
    while i > 0 and groups[SC[i - 1][3]] == g: i -= 1
    return SC[i][0], g

CY = 1180

def draw_graphic(cv, d, key, t, t0, tl):
    """t0 = start of visual group, tl = start of this headline"""
    p = back((t - t0) / 0.45) if t0 > 0 else 1.0
    bob = math.sin(t * 2.2) * 6
    zoom = 1 + 0.03 * clamp((t - t0) / 3)
    if key in ("hero",):
        put(cv, "leaf", W / 2, CY + 60, 1.05 * zoom * p)
        for i, dx in enumerate((-210, 0, 210)):
            put(cv, "idli", W / 2 + dx, CY + 90 + bob * (i % 2), 0.95 * zoom * p)
        put(cv, "dosa", W / 2 + 10, CY - 140 + bob, 1.1 * zoom * p)
    elif key == "low":
        put(cv, "idli", W / 2, CY - 120 + bob, 1.4 * p)
        put(cv, "meter_low", W / 2, CY + 140, 1.0 * p)
        d.text((W / 2 - 370, CY + 40), "PROTEIN", font=F("anton", 52), fill=GREY, anchor="lm")
        if t > 3.45:
            pulse = 0.5 + 0.5 * math.sin(t * 8)
            d.text((W / 2 + 370, CY + 40), "LOW", font=F("anton", 52), fill=tuple(int(CORAL[i] * (0.6 + 0.4 * pulse)) for i in range(3)), anchor="rm")
    elif key == "four":
        put(cv, "leaf", W / 2, CY + 40, 1.05 * p)
        for i, (dx, dy) in enumerate(((-260, 30), (-88, -10), (88, 30), (260, -10))):
            pi = back((t - t0 - i * 0.12) / 0.4) if t0 > 0 else 1
            put(cv, "idli", W / 2 + dx, CY + 40 + dy + bob * (i % 2), 0.85 * pi)
        if t >= 6.85:
            put(cv, "b10", W / 2 + 300, CY - 190, back((t - tl) / 0.4))
    elif key == "fix":
        put(cv, "bfix", W / 2, CY, 1.35 * p)
        for i, (dx, dy, s) in enumerate(((-230, -160, 0.9), (240, -120, 0.6), (200, 190, 0.75), (-210, 170, 0.5))):
            put(cv, "spark", W / 2 + dx, CY + dy, s * back((t - t0 - 0.2 - i * 0.1) / 0.4) * (0.85 + 0.15 * math.sin(t * 6 + i)))
    elif key == "dal":
        put(cv, "chana", W / 2 - 190, CY + bob, 1.15 * p)
        put(cv, "moong", W / 2 + 190, CY - bob, 1.15 * back((t - t0 - 0.15) / 0.45))
        d.text((W / 2 - 190, CY + 190), "CHANA DAL", font=F("anton", 52), fill=GREY, anchor="mm")
        d.text((W / 2 + 190, CY + 190), "MOONG DAL", font=F("anton", 52), fill=GREY, anchor="mm")
    elif key == "mixer":
        shake = math.sin(t * 40) * 3 if t - t0 > 0.5 else 0
        put(cv, "mixer", W / 2 + shake, CY - 20, 1.0 * p)
        d.text((W / 2 - 330, CY + 40), "GRIND", font=F("anton", 56), fill=GREY, anchor="mm")
        d.text((W / 2 + 330, CY + 40), "+ BATTER", font=F("anton", 56), fill=GREY, anchor="mm")
    elif key == "mid":
        put(cv, "idli", W / 2, CY - 130 + bob, 1.4 * p)
        lv = 0.12 + 0.4 * ease((t - t0) / 1.2)
        put(cv, "meter_mid" if lv > 0.3 else "meter_low", W / 2, CY + 140, 1.0)
        d.text((W / 2 - 370, CY + 40), "PROTEIN", font=F("anton", 52), fill=GREY, anchor="lm")
        d.text((W / 2 + 370, CY + 40), "+ DAL", font=F("anton", 52), fill=LIME, anchor="rm")
    elif key == "tomato":
        put(cv, "tomato", W / 2, CY, 1.6 * p)
        if t > 18.0:
            put(cv, "cross", W / 2, CY, 1.1 * back((t - 18.0) / 0.3))
        d.text((W / 2, CY + 250), "TOMATO", font=F("anton", 56), fill=GREY, anchor="mm")
    elif key == "gnut":
        put(cv, "gnut", W / 2, CY, 1.6 * p)
        d.text((W / 2, CY + 250), "GROUNDNUT", font=F("anton", 56), fill=LIME, anchor="mm")
        put(cv, "check", W / 2 + 250, CY - 160, 0.8 * back((t - t0 - 0.4) / 0.4))
    elif key in ("pea",):
        put(cv, "peanuts", W / 2, CY + 20 + bob, 1.3 * p)
        if t >= 21.65:
            put(cv, "b5", W / 2 + 290, CY - 180, back((t - 21.65) / 0.4))
    elif key == "final":
        put(cv, "leaf", W / 2, CY + 60, 1.05 * p)
        for i, dx in enumerate((-230, -40, 150)):
            put(cv, "idli", W / 2 + dx, CY + 100 + bob * (i % 2), 0.9 * p)
        put(cv, "gnut", W / 2 + 10, CY - 120, 0.75 * p)
        if t >= 24.85:
            put(cv, "meter_hi", W / 2, CY + 330, 1.0 * back((t - 24.85) / 0.4))
            put(cv, "check", W / 2 + 330, CY - 170, 0.9 * back((t - 25.3) / 0.4))
    elif key == "save":
        put(cv, "bookmark", W / 2, CY, 1.2 * p * (1 + 0.04 * math.sin(t * 7)))
    elif key == "follow":
        put(cv, "follow", W / 2, CY - 40, 1.0 * p)
        put(cv, "follow_btn", W / 2, CY + 200, back((t - t0 - 0.3) / 0.4) * (1 + 0.03 * math.sin(t * 7)))
    elif key == "clock":
        put(cv, "clock", W / 2, CY, 1.1 * p)
    elif key == "cta":
        fb = F("black", 150)
        a = clamp((t - t0) / 0.3)
        tw = d.textlength("FitEats", font=fb)
        d.text((W / 2 + 6, CY - 210 + 8), "FitEats", font=fb, fill=(0, 0, 0), anchor="mm")
        d.text((W / 2, CY - 210), "FitEats", font=fb, fill=tuple(int(BG[i] + (TXT[i] - BG[i]) * a) for i in range(3)), anchor="mm")
        d.ellipse((W / 2 + tw / 2 + 6, CY - 190, W / 2 + tw / 2 + 40, CY - 156), fill=LIME)
        d.text((W / 2, CY - 100), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 30), fill=GREY, anchor="mm")
        put(cv, "wa", W / 2, CY + 50, back((t - t0 - 0.3) / 0.4) * (1 + 0.035 * math.sin(t * 6)))
        put(cv, "bio", W / 2, CY + 210, back((t - t0 - 0.8) / 0.4))

def frame(t):
    i, (s0, markup, glow, key) = scene_at(t)
    gstart, grp = scene_start(i)
    cv = bg(GLOW[glow]).copy(); d = ImageDraw.Draw(cv)
    # progress bar + tag pill
    d.rounded_rectangle((60, 214, W - 60, 224), 5, fill=(49, 53, 57))
    d.rounded_rectangle((60, 214, 60 + (W - 120) * clamp(t / TOTAL), 224), 5, fill=LIME)
    d.rounded_rectangle((60, 254, 360, 312), 29, fill=LIME)
    d.text((210, 284), "PROTEIN FIX", font=F("bold", 30), fill=INK, anchor="mm")
    # headline: pops on each new phrase (frame 0 is already fully visible)
    s = 0.9 + 0.1 * back((t - s0) / 0.22) if s0 > 0 else 1.0
    him = headline_scaled(markup, round(s, 2))
    hy = 640 - him.height / 2 + 40
    cv.alpha_composite(him, (int((W - him.width) / 2), int(hy)))
    draw_graphic(cv, d, grp, t, gstart, s0)
    if 5.5 < t < 24.8:
        d.text((W / 2, 1545), "Estimate: idli ~2.5 g protein each, 20 g peanuts ~5 g. Varies by recipe.", font=F("bold", 28), fill=GREY, anchor="mm")
    return cv.convert("RGB")

def main():
    build_sprites()
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(float(s)).save(f"s2_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "video_tmp.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); os.rename("video_tmp.mp4", "video_only2.mp4")

if __name__ == "__main__":
    main()
