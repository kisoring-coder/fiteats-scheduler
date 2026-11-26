"""More realistic, shaded sprites for the back-pain reel (drawn in code, no image credits)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from b2 import sprite, vgrad, shape_mask, OUT, LIME, CORAL, F

def hgrad(im, box, left, right, mask=None):
    x0, y0, x1, y1 = [int(v) for v in box]
    g = Image.new("RGBA", (max(1, x1 - x0), max(1, y1 - y0)))
    gd = ImageDraw.Draw(g)
    for x in range(x1 - x0):
        t = x / max(1, x1 - x0 - 1)
        gd.line([(x, 0), (x, y1 - y0)], fill=tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3)) + (255,))
    if mask is not None: im.paste(g, (x0, y0), mask.crop((x0, y0, x1, y1)))
    else: im.alpha_composite(g, (x0, y0))

def cyl(im, box, base, mask=None, hi=1.35, lo=0.55):
    """Cylinder shading: dark edges, bright band at 30%."""
    x0, y0, x1, y1 = [int(v) for v in box]
    g = Image.new("RGBA", (max(1, x1 - x0), max(1, y1 - y0)))
    gd = ImageDraw.Draw(g)
    for y in range(y1 - y0):
        t = y / max(1, y1 - y0 - 1)
        f = lo + (hi - lo) * math.exp(-((t - 0.3) / 0.28) ** 2)
        gd.line([(0, y), (x1 - x0, y)], fill=tuple(min(255, int(c * f)) for c in base) + (255,))
    if mask is not None: im.paste(g, (x0, y0), mask.crop((x0, y0, x1, y1)))
    else: im.alpha_composite(g, (x0, y0))

def glow(im, cx, cy, rx, ry, col, a=160, blur=None):
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(L).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col + (a,))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur or rx * 0.45)))

def soft_shadow(im, box, a=120):
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(L).ellipse(box, fill=(0, 0, 0, a))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur((box[2] - box[0]) * 0.05)))

def fill(im, draw_fn, box, top, bot):
    vgrad(im, box, top, bot, shape_mask(im.size, draw_fn))

def lighten(c, f): return tuple(min(255, int(v * f)) for v in c)

# ------------------------------------------------------------------ spine
def spine_real(state="pain", w=340, h=720):
    def fn(d, k, im):
        n = 13
        top, bot = 30, h - 150
        def cx(y):  # gentle S-curve: neck/thoracic/lumbar
            t = (y - top) / (bot - top)
            return w / 2 + 26 * math.sin(t * 2 * math.pi - 0.4)
        # discs + vertebrae
        for i in range(n):
            y0 = top + i * (bot - top) / n; hh = (bot - top) / n - 12
            vw = 82 + i * 7; x = cx(y0 + hh / 2)
            lumbar = i >= n - 5
            # spinous process (back side, to the right)
            pr = [((x + vw / 2 - 6) * k, (y0 + 6) * k), ((x + vw / 2 + 34 + i) * k, (y0 + hh * 0.75) * k), ((x + vw / 2 - 6) * k, (y0 + hh) * k)]
            fill(im, lambda md, p=pr: md.polygon(p, fill=255), (x * k, y0 * k, (x + vw / 2 + 40 + i) * k, (y0 + hh + 2) * k), (226, 212, 186), (176, 158, 128))
            d.line(pr, fill=(92, 72, 52, 255), width=int(3 * k))
            # body
            box = ((x - vw / 2) * k, y0 * k, (x + vw / 2) * k, (y0 + hh) * k)
            m = shape_mask(im.size, lambda md, b=box: md.rounded_rectangle(b, int(14 * k), fill=255))
            hgrad(im, box, (252, 246, 232), (196, 180, 150), m)
            d.rounded_rectangle(((x - vw / 2 + 8) * k, (y0 + 5) * k, (x - vw / 2 + 22) * k, (y0 + hh - 5) * k), int(6 * k), fill=(255, 255, 248, 150))
            d.rounded_rectangle(box, int(14 * k), outline=(92, 72, 52, 255), width=int(3 * k))
            # disc below
            if i < n - 1:
                dy = y0 + hh + 1; dc = (150, 190, 220)
                if state == "pain" and lumbar: dc = (232, 84, 64)
                if state == "ok": dc = (170, 214, 90)
                db = ((x - vw / 2 + 10) * k, dy * k, (x + vw / 2 - 6) * k, (dy + 10) * k)
                dm = shape_mask(im.size, lambda md, b=db: md.rounded_rectangle(b, int(5 * k), fill=255))
                vgrad(im, db, lighten(dc, 1.2), lighten(dc, 0.75), dm)
        # sacrum / pelvis wedge
        x = cx(bot)
        sac = [((x - 70) * k, (bot + 4) * k), ((x + 74) * k, (bot + 4) * k), ((x + 16) * k, (bot + 120) * k), ((x - 6) * k, (bot + 122) * k)]
        fill(im, lambda md: md.polygon(sac, fill=255), ((x - 72) * k, bot * k, (x + 76) * k, (bot + 124) * k), (240, 228, 204), (180, 162, 132))
        for j in range(4):
            yy = bot + 24 + j * 22
            d.line([((x - 44 + j * 12) * k, yy * k), ((x + 46 - j * 12) * k, yy * k)], fill=(150, 128, 98, 255), width=int(3 * k))
        d.polygon(sac, outline=(92, 72, 52, 255), width=int(3 * k))
        if state == "pain":
            ly = top + (n - 3) * (bot - top) / n
            glow(im, cx(ly) * k, ly * k, 120 * k, 110 * k, (240, 60, 40), 150)
    return sprite(w, h, fn)

# ------------------------------------------------------------------ person at desk
def desk_real(w=760, h=620):
    def fn(d, k, im):
        K = lambda *p: tuple(v * k for v in p)
        soft_shadow(im, K(40, h - 70, w - 30, h - 10), 140)
        # desk
        fill(im, lambda md: md.rectangle(K(640, 330, 660, h - 40), fill=255), K(640, 330, 660, h - 40), (120, 84, 54), (80, 54, 34))
        fill(im, lambda md: md.rounded_rectangle(K(380, 300, 740, 334), int(6 * k), fill=255), K(380, 300, 740, 334), (196, 146, 98), (140, 98, 62))
        d.rounded_rectangle(K(380, 300, 740, 334), int(6 * k), outline=OUT + (255,), width=int(3 * k))
        d.line([K(384, 304), K(736, 304)], fill=(226, 184, 140, 255), width=int(3 * k))
        # laptop: base + tilted screen with glow
        fill(im, lambda md: md.polygon([K(470, 292), K(640, 292), K(650, 302), K(462, 302)], fill=255), K(460, 290, 652, 304), (210, 214, 222), (150, 154, 164))
        scr = [K(600, 296), K(640, 150), K(656, 152), K(618, 298)]
        fill(im, lambda md: md.polygon(scr, fill=255), K(598, 148, 658, 300), (190, 194, 204), (120, 124, 134))
        glow(im, *K(560, 220), 70 * k, 60 * k, (120, 180, 255), 90)
        # chair: base, caster wheels, gas lift, seat, backrest
        for xx in (150, 250, 330):
            d.ellipse(K(xx - 14, h - 62, xx + 14, h - 36), fill=(30, 32, 38, 255))
        d.line([K(150, h - 66), K(330, h - 66)], fill=(54, 58, 66, 255), width=int(14 * k))
        fill(im, lambda md: md.rectangle(K(232, 420, 250, h - 66), fill=255), K(232, 420, 250, h - 66), (190, 196, 206), (110, 116, 126))
        seat = K(120, 392, 370, 430)
        fill(im, lambda md: md.rounded_rectangle(seat, int(18 * k), fill=255), seat, (78, 84, 96), (40, 44, 52))
        d.rounded_rectangle(seat, int(18 * k), outline=OUT + (255,), width=int(3 * k))
        backr = [K(96, 170), K(140, 160), K(150, 400), K(106, 404)]
        fill(im, lambda md: md.polygon(backr, fill=255), K(94, 158, 152, 406), (84, 90, 104), (42, 46, 54))
        d.line(backr + [backr[0]], fill=OUT + (255,), width=int(3 * k), joint="curve")
        # legs (trousers + shoes)
        pants = (52, 58, 82)
        d.line([K(190, 382), K(410, 382)], fill=pants + (255,), width=int(62 * k))
        d.line([K(406, 384), K(420, 540)], fill=lighten(pants, 0.85) + (255,), width=int(50 * k), joint="curve")
        d.ellipse(K(170, 352, 230, 412), fill=pants + (255,))
        d.rounded_rectangle(K(396, 532, 484, 566), int(14 * k), fill=(34, 30, 28, 255))
        d.line([K(214, 360), K(400, 360)], fill=lighten(pants, 1.3) + (255,), width=int(6 * k))
        # hunched torso (shirt)
        torso = [K(150, 400), K(156, 300), K(186, 220), K(250, 160), K(320, 138), K(352, 176), K(300, 230), K(262, 300), K(258, 400)]
        fill(im, lambda md: md.polygon(torso, fill=255), K(146, 130, 360, 404), (98, 138, 206), (52, 82, 140))
        d.line([K(196, 240), K(232, 300)], fill=(60, 90, 150, 255), width=int(4 * k))
        d.line(torso + [torso[0]], fill=OUT + (255,), width=int(3 * k), joint="curve")
        # neck + head pushed forward
        d.line([K(318, 150), K(352, 124)], fill=(196, 140, 104, 255), width=int(34 * k))
        head = K(330, 52, 418, 146)
        fill(im, lambda md: md.ellipse(head, fill=255), head, (232, 180, 140), (186, 128, 92))
        hair = [K(330, 98), K(336, 62), K(370, 48), K(410, 60), K(418, 84), K(392, 74), K(356, 82), K(344, 104)]
        fill(im, lambda md: md.polygon(hair, fill=255), K(328, 46, 420, 106), (54, 40, 32), (24, 18, 14))
        d.ellipse(K(352, 94, 368, 116), fill=(200, 140, 104, 255))
        d.ellipse(head, outline=OUT + (255,), width=int(3 * k))
        d.ellipse(K(410, 100, 426, 118), fill=(222, 162, 122, 255))  # nose
        d.ellipse(K(395, 95, 405, 103), fill=(40, 28, 22, 255))  # eye
        d.line([K(391, 93), K(408, 96)], fill=(120, 76, 56, 255), width=int(4 * k))  # heavy lid
        d.arc(K(392, 102, 408, 112), 20, 160, fill=(150, 96, 84, 220), width=int(2 * k))  # eye bag
        d.arc(K(390, 128, 410, 142), 200, 340, fill=(140, 80, 62, 255), width=int(3 * k))  # frown
        # arms to keyboard
        d.line([K(300, 180), K(350, 270), K(470, 286)], fill=(80, 116, 182, 255), width=int(30 * k), joint="curve")
        d.ellipse(K(458, 274, 490, 298), fill=(222, 166, 126, 255))
        # pain glow on lower back
        glow(im, *K(168, 318), 70 * k, 70 * k, (245, 60, 40), 190)
        glow(im, *K(168, 318), 30 * k, 30 * k, (255, 200, 80), 160)
    return sprite(w, h, fn)

# ------------------------------------------------------------------ alarm clock
def alarm_real(w=380, h=430, hour=6, minute=0):
    def fn(d, k, im):
        K = lambda *p: tuple(v * k for v in p)
        soft_shadow(im, K(60, h - 50, w - 60, h - 14), 130)
        for x0, sgn in ((70, -1), (w - 70, 1)):
            d.line([K(x0, h - 120), K(x0 + sgn * 30, h - 34)], fill=(60, 60, 66, 255), width=int(14 * k))
        for bx in (96, w - 96):
            bb = K(bx - 62, 30, bx + 62, 130)
            fill(im, lambda md, b=bb: md.pieslice((b[0], b[1], b[2], b[3] + 100 * k), 180, 360, fill=255), (bb[0], bb[1], bb[2], bb[3]), (250, 120, 100), (170, 40, 30))
            d.arc((bb[0], bb[1], bb[2], bb[3] + 100 * k), 180, 360, fill=OUT + (255,), width=int(4 * k))
        d.line([K(w / 2, 20), K(w / 2, 70)], fill=(80, 80, 86, 255), width=int(10 * k))
        body = K(34, 70, w - 34, h - 50)
        fill(im, lambda md: md.ellipse(body, fill=255), body, (236, 84, 66), (150, 30, 24))
        d.ellipse(body, outline=OUT + (255,), width=int(5 * k))
        face = K(64, 100, w - 64, h - 80)
        fill(im, lambda md: md.ellipse(face, fill=255), face, (255, 254, 248), (222, 220, 212))
        cx, cy = w / 2, (100 + h - 80) / 2; r = (w - 128) / 2
        for i in range(12):
            a = math.radians(i * 30 - 90); r1 = r - (22 if i % 3 == 0 else 14)
            d.line([K(cx + r1 * math.cos(a), cy + r1 * math.sin(a)), K(cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a))], fill=(50, 50, 56, 255), width=int((6 if i % 3 == 0 else 3) * k))
        ah = math.radians((hour % 12 + minute / 60) * 30 - 90); am = math.radians(minute * 6 - 90)
        d.line([K(cx, cy), K(cx + r * 0.5 * math.cos(ah), cy + r * 0.5 * math.sin(ah))], fill=(30, 30, 34, 255), width=int(10 * k))
        d.line([K(cx, cy), K(cx + r * 0.78 * math.cos(am), cy + r * 0.78 * math.sin(am))], fill=(30, 30, 34, 255), width=int(7 * k))
        d.ellipse(K(cx - 10, cy - 10, cx + 10, cy + 10), fill=CORAL + (255,))
        d.arc(K(80, 116, w - 80, h - 96), 200, 250, fill=(255, 255, 255, 200), width=int(8 * k))
    return sprite(w, h, fn)

# ------------------------------------------------------------------ briefcase
def briefcase_real(w=380, h=300):
    def fn(d, k, im):
        K = lambda *p: tuple(v * k for v in p)
        soft_shadow(im, K(30, h - 50, w - 30, h - 10), 140)
        d.rounded_rectangle(K(130, 22, w - 130, 82), int(18 * k), outline=(60, 40, 24, 255), width=int(14 * k))
        body = K(20, 66, w - 20, h - 30)
        fill(im, lambda md: md.rounded_rectangle(body, int(26 * k), fill=255), body, (166, 110, 64), (96, 58, 30))
        flap = K(20, 66, w - 20, 150)
        fill(im, lambda md: md.rounded_rectangle(flap, int(26 * k), fill=255), flap, (186, 128, 78), (138, 88, 48))
        for y in (78, 138):
            for x in range(40, w - 40, 18): d.line([K(x, y), K(x + 9, y)], fill=(230, 190, 140, 200), width=int(2 * k))
        for x in (110, w - 110):
            cb = K(x - 22, 128, x + 22, 168)
            fill(im, lambda md, b=cb: md.rounded_rectangle(b, int(6 * k), fill=255), cb, (255, 226, 140), (190, 140, 40))
            d.rounded_rectangle(cb, int(6 * k), outline=OUT + (255,), width=int(3 * k))
        d.rounded_rectangle(K(40, 80, 70, h - 46), int(12 * k), fill=(255, 255, 255, 40))
        d.rounded_rectangle(body, int(26 * k), outline=OUT + (255,), width=int(5 * k))
    return sprite(w, h, fn)

# ------------------------------------------------------------------ dumbbell
def dumbbell_real(w=460, h=230):
    def fn(d, k, im):
        K = lambda *p: tuple(v * k for v in p)
        soft_shadow(im, K(40, h - 44, w - 40, h - 8), 140)
        hb = K(110, 96, w - 110, 134)
        cyl(im, hb, (200, 206, 216))
        for x in range(140, w - 140, 8): d.line([K(x, 98), K(x + 4, 132)], fill=(120, 126, 136, 160), width=int(2 * k))
        d.rounded_rectangle(hb, int(8 * k), outline=OUT + (255,), width=int(3 * k))
        for x0 in (30, w - 120):
            hx = [K(x0, 60), K(x0 + 20, 26), K(x0 + 70, 26), K(x0 + 90, 60), K(x0 + 90, 170), K(x0 + 70, 204), K(x0 + 20, 204), K(x0, 170)]
            m = shape_mask(im.size, lambda md, p=hx: md.polygon(p, fill=255))
            cyl(im, K(x0, 26, x0 + 90, 204), (70, 74, 84), m, hi=1.6, lo=0.5)
            d.line(hx + [hx[0]], fill=OUT + (255,), width=int(4 * k), joint="curve")
            cap = K(x0 + 30, 96, x0 + 60, 134) if x0 < w / 2 else K(x0 + 30, 96, x0 + 60, 134)
            cyl(im, cap, (220, 224, 232))
        for x0 in (20, w - 34):
            cyl(im, K(x0, 92, x0 + 14, 138), (190, 196, 206))
    return sprite(w, h, fn)

# ------------------------------------------------------------------ protein bowl
def protein_bowl_real(w=500, h=360):
    def fn(d, k, im):
        K = lambda *p: tuple(v * k for v in p)
        soft_shadow(im, K(50, h - 60, w - 50, h - 12), 150)
        bowl = [K(24, 140), K(w - 24, 140), K(w - 70, h - 50), K(70, h - 50)]
        bm = shape_mask(im.size, lambda md: (md.pieslice(K(24, 40, w - 24, h - 40), 0, 180, fill=255)))
        vgrad(im, K(24, 140, w - 24, h - 40), (246, 246, 250), (170, 176, 190), bm)
        d.arc(K(24, 40, w - 24, h - 40), 0, 180, fill=OUT + (255,), width=int(4 * k))
        rim = K(24, 92, w - 24, 188)
        fill(im, lambda md: md.ellipse(rim, fill=255), rim, (226, 228, 234), (250, 250, 252))
        d.ellipse(rim, outline=OUT + (255,), width=int(4 * k))
        food = K(44, 100, w - 44, 180)
        fill(im, lambda md: md.ellipse(food, fill=255), food, (250, 246, 236), (226, 218, 198))  # rice bed
        dome = K(70, 60, w - 70, 170)
        fill(im, lambda md: md.pieslice(dome, 180, 360, fill=255), (dome[0], dome[1], dome[2], (dome[1]+dome[3])/2), (255, 252, 244), (232, 224, 204))
        import random; rr = random.Random(3)
        for _ in range(90):
            x = rr.uniform(70, w - 70); y = rr.uniform(80, 170)
            if ((x - w/2)/(w/2-60))**2 + ((y-125)/55)**2 < 1:
                d.ellipse(K(x - 5, y - 2.5, x + 5, y + 2.5), fill=(255, 255, 250, 255), outline=(226, 218, 200, 255))
        # grilled chicken slices fanned on top
        for i in range(3):
            x = 196 + i * 50; y = 78 + abs(i - 1) * 10
            sl = [K(x, y + 8), K(x + 46, y), K(x + 54, y + 40), K(x + 8, y + 48)]
            fill(im, lambda md, p=sl: md.polygon(p, fill=255), K(x, y - 2, x + 56, y + 50), (238, 184, 116), (192, 120, 58))
            for g in range(2): d.line([K(x + 12 + g * 18, y + 6), K(x + 20 + g * 18, y + 42)], fill=(120, 66, 26, 200), width=int(3 * k))
            d.polygon(sl, outline=(130, 74, 32, 255))
        # egg halves
        for x, y in ((116, 112), (156, 98)):
            eb = K(x - 30, y - 22, x + 30, y + 22)
            fill(im, lambda md, b=eb: md.ellipse(b, fill=255), eb, (255, 255, 252), (230, 226, 216))
            d.ellipse(eb, outline=(196, 190, 176, 255), width=int(2 * k))
            yb = K(x - 13, y - 11, x + 13, y + 11)
            fill(im, lambda md, b=yb: md.ellipse(b, fill=255), yb, (255, 214, 70), (236, 150, 20))
        # broccoli
        for bx, by in ((370, 96), (404, 118), (352, 128)):
            d.line([K(bx, by + 8), K(bx, by + 26)], fill=(130, 180, 90, 255), width=int(9 * k))
            for dx, dy, r in ((-11, 0, 13), (9, -4, 14), (0, -13, 13), (13, 8, 11), (-13, 10, 11)):
                cb = K(bx + dx - r, by + dy - r, bx + dx + r, by + dy + r)
                fill(im, lambda md, b=cb: md.ellipse(b, fill=255), cb, (104, 178, 76), (40, 110, 40))
        # cherry tomatoes
        for tx, ty in ((430, 120), (300, 146), (86, 146)):
            tb = K(tx - 16, ty - 16, tx + 16, ty + 16)
            fill(im, lambda md, b=tb: md.ellipse(b, fill=255), tb, (255, 104, 84), (190, 30, 20))
            d.ellipse(K(tx - 9, ty - 11, tx - 2, ty - 4), fill=(255, 225, 215, 230))
        # bowl highlight
        d.arc(K(60, 150, w - 60, h - 60), 120, 150, fill=(255, 255, 255, 180), width=int(10 * k))
    return sprite(w, h, fn)
