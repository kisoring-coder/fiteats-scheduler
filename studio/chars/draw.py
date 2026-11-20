"""Three original flat-illustration characters for the FitEats strength series."""
from PIL import Image, ImageDraw, ImageFont
import math

S = 3                      # supersample factor
PW, PH = 600, 980          # panel size (final px)
BG = (11, 11, 12); CARD = (24, 24, 27); ACC = (184, 240, 64); TXT = (242, 242, 240); MUTED = (120, 120, 128)
CORAL = (240, 120, 90)
SKIN = (176, 112, 66); SKIN_SH = (150, 92, 52); HAIR = (28, 22, 20)
FD = "/usr/share/fonts/opentype/inter/"; GF = "/usr/share/fonts/truetype/google-fonts/ofl/"

def F(kind, size):
    p = {"bold": FD + "InterDisplay-Bold.otf", "sans": FD + "InterDisplay-Medium.otf",
         "mono": GF + "anonymouspro/AnonymousPro-Bold.ttf", "serif": GF + "crimsontext/CrimsonText-Italic.ttf"}[kind]
    return ImageFont.truetype(p, size * S)

def s(v): return [x * S for x in v] if isinstance(v, (list, tuple)) else v * S

def ell(d, cx, cy, rx, ry, fill): d.ellipse(s([cx - rx, cy - ry, cx + rx, cy + ry]), fill=fill)
def rr(d, x0, y0, x1, y1, r, fill): d.rounded_rectangle(s([x0, y0, x1, y1]), radius=r * S, fill=fill)
def poly(d, pts, fill): d.polygon([(x * S, y * S) for x, y in pts], fill=fill)
def line(d, pts, fill, w): d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint="curve")
def limb(d, a, b, w, fill):
    line(d, [a, b], fill, w); ell(d, a[0], a[1], w / 2, w / 2, fill); ell(d, b[0], b[1], w / 2, w / 2, fill)

def face(d, cx, cy, r, mood="neutral", glasses=False, mustache=False):
    ell(d, cx, cy, r, r * 1.08, SKIN)
    ell(d, cx - r * 0.98, cy + 4, r * 0.16, r * 0.24, SKIN)      # ears
    ell(d, cx + r * 0.98, cy + 4, r * 0.16, r * 0.24, SKIN)
    ey = cy + r * 0.05
    for sx in (-1, 1):
        ell(d, cx + sx * r * 0.36, ey, r * 0.09, r * 0.12 if mood != "tired" else r * 0.05, HAIR)
        if mood == "pain":
            line(d, [(cx + sx * r * 0.52, ey - r * 0.28), (cx + sx * r * 0.2, ey - r * 0.2)], HAIR, 4)
    if glasses:
        for sx in (-1, 1):
            d.ellipse(s([cx + sx * r * 0.36 - r * 0.26, ey - r * 0.22, cx + sx * r * 0.36 + r * 0.26, ey + r * 0.22]), outline=HAIR, width=4 * S)
        line(d, [(cx - r * 0.1, ey), (cx + r * 0.1, ey)], HAIR, 4)
    if mustache:
        poly(d, [(cx - r * 0.4, cy + r * 0.42), (cx, cy + r * 0.32), (cx + r * 0.4, cy + r * 0.42), (cx + r * 0.3, cy + r * 0.5), (cx, cy + r * 0.42), (cx - r * 0.3, cy + r * 0.5)], HAIR)
    my = cy + r * 0.58
    if mood == "happy":
        d.arc(s([cx - r * 0.3, my - r * 0.25, cx + r * 0.3, my + r * 0.18]), 15, 165, fill=HAIR, width=5 * S)
    elif mood == "pain":
        line(d, [(cx - r * 0.25, my + 4), (cx - r * 0.08, my - 4), (cx + r * 0.08, my + 4), (cx + r * 0.25, my - 4)], HAIR, 5)
    elif mood == "tired":
        ell(d, cx, my + 4, r * 0.14, r * 0.16, (90, 40, 40))
    else:
        line(d, [(cx - r * 0.2, my), (cx + r * 0.2, my)], HAIR, 5)

def panel(name, age, role, tagline, drawer):
    im = Image.new("RGB", (PW * S, PH * S), BG); d = ImageDraw.Draw(im)
    rr(d, 24, 24, PW - 24, PH - 24, 28, CARD)
    ell(d, PW / 2, 470, 210, 210, (34, 34, 38))                # spotlight disc
    drawer(d)
    rr(d, 24, 760, PW - 24, PH - 24, 28, (30, 30, 34))
    d.text(s((PW / 2, 812)), f"{name}, {age}", font=F("bold", 46), fill=TXT, anchor="mm")
    d.text(s((PW / 2, 862)), role, font=F("mono", 24), fill=ACC, anchor="mm")
    d.text(s((PW / 2, 912)), tagline, font=F("serif", 30), fill=MUTED, anchor="mm")
    return im.resize((PW, PH), Image.LANCZOS)

# ---------- 1. Karthik: IT desk worker, back pain ----------
def karthik(d):
    cx = 300
    # chair + desk hint
    rr(d, 120, 560, 250, 580, 8, (60, 60, 66)); line(d, [(185, 580), (185, 660)], (60, 60, 66), 10)
    rr(d, 360, 470, 520, 486, 6, (70, 70, 78)); rr(d, 395, 420, 495, 470, 6, (90, 110, 140))   # desk + laptop
    # legs (standing, slightly bent)
    limb(d, (275, 560), (265, 700), 30, (40, 48, 70)); limb(d, (325, 560), (335, 700), 30, (40, 48, 70))
    rr(d, 240, 694, 290, 716, 10, (20, 20, 22)); rr(d, 315, 694, 365, 716, 10, (20, 20, 22))
    # torso: blue office shirt, leaning
    poly(d, [(245, 400), (355, 400), (365, 575), (235, 575)], (70, 120, 190))
    poly(d, [(285, 400), (300, 430), (315, 400)], (230, 230, 235))     # collar
    line(d, [(300, 430), (300, 570)], (55, 100, 165), 3)
    # lanyard ID
    line(d, [(275, 405), (300, 470), (325, 405)], CORAL, 4); rr(d, 288, 466, 312, 496, 4, (240, 240, 240))
    # arms: one on lower back, one rubbing neck
    limb(d, (355, 420), (395, 500), 24, (70, 120, 190)); limb(d, (395, 500), (350, 545), 22, SKIN)
    limb(d, (245, 420), (215, 470), 24, (70, 120, 190)); limb(d, (215, 470), (255, 395), 20, SKIN)
    # head
    face(d, cx, 335, 62, mood="pain", glasses=True)
    poly(d, [(238, 320), (250, 272), (300, 255), (350, 270), (362, 318), (345, 292), (300, 286), (255, 296)], HAIR)
    # pain marks on lower back
    for i, (x, y) in enumerate([(392, 548), (405, 572), (388, 592)]):
        line(d, [(x, y), (x + 14, y - 8), (x + 22, y + 6), (x + 36, y - 4)], CORAL, 6)

# ---------- 2. Priya: working mom, kid running ahead ----------
def priya(d):
    # Priya
    limb(d, (230, 585), (210, 700), 26, (40, 44, 60)); limb(d, (262, 585), (285, 698), 26, (40, 44, 60))
    rr(d, 186, 694, 232, 714, 10, (150, 70, 60)); rr(d, 268, 692, 314, 712, 10, (150, 70, 60))
    poly(d, [(200, 410), (290, 410), (310, 600), (180, 600)], (30, 150, 140))           # teal kurti
    for y in (470, 520, 570): line(d, [(190, y), (300, y)], (25, 125, 118), 3)
    poly(d, [(228, 410), (245, 440), (262, 410)], (25, 125, 118))
    limb(d, (205, 430), (185, 520), 22, SKIN)                                              # free arm
    limb(d, (285, 430), (335, 495), 22, SKIN)                                              # arm to kid
    face(d, 245, 345, 58, mood="tired")
    poly(d, [(187, 345), (192, 292), (245, 270), (298, 292), (303, 345), (290, 310), (245, 300), (200, 310)], HAIR)
    line(d, [(196, 340), (180, 420), (186, 500)], HAIR, 18)                              # braid
    ell(d, 245, 302, 6, 6, CORAL)                                                         # bindi-ish clip accent
    # sweat drops
    for x, y in ((310, 320), (322, 350)):
        poly(d, [(x, y - 12), (x - 7, y + 2), (x + 7, y + 2)], (130, 190, 240)); ell(d, x, y + 3, 7, 7, (130, 190, 240))
    # kid running ahead
    kx = 420
    limb(d, (kx - 8, 615), (kx - 40, 690), 18, (60, 60, 140)); limb(d, (kx + 8, 615), (kx + 40, 675), 18, (60, 60, 140))
    poly(d, [(kx - 30, 520), (kx + 30, 520), (kx + 34, 620), (kx - 34, 620)], ACC)
    limb(d, (kx - 28, 535), (kx - 70, 520), 14, SKIN)                                      # holding mom's hand
    limb(d, (kx + 28, 535), (kx + 60, 500), 14, SKIN)
    face(d, kx, 470, 40, mood="happy")
    poly(d, [(kx - 40, 460), (kx - 30, 428), (kx, 418), (kx + 30, 428), (kx + 40, 460), (kx + 20, 440), (kx - 20, 440)], HAIR)
    for i in range(3):
        line(d, [(kx + 70 + i * 14, 560 + i * 26), (kx + 100 + i * 14, 560 + i * 26)], (90, 90, 96), 5)   # speed lines

# ---------- 3. Ravi: dad, breathless on stairs ----------
def ravi(d):
    # stairs
    for i in range(5):
        x0 = 90 + i * 80; y0 = 700 - i * 70
        rr(d, x0, y0, 520, y0 + 70, 4, (52, 52, 58) if i % 2 else (60, 60, 66))
    line(d, [(140, 560), (520, 340)], (110, 110, 118), 8)
    # legs climbing
    limb(d, (285, 545), (250, 630), 30, (60, 55, 50)); limb(d, (250, 630), (255, 700), 28, (60, 55, 50))
    limb(d, (320, 545), (345, 590), 30, (60, 55, 50)); limb(d, (345, 590), (335, 630), 28, (60, 55, 50))
    rr(d, 232, 694, 282, 714, 10, (20, 20, 22)); rr(d, 315, 624, 365, 644, 10, (20, 20, 22))
    # belly torso: polo shirt
    ell(d, 302, 480, 82, 92, (200, 90, 70))
    rr(d, 230, 395, 375, 470, 30, (200, 90, 70))
    poly(d, [(285, 395), (302, 425), (319, 395)], (170, 70, 55))
    # arms: hand on knee, hand on railing
    limb(d, (238, 420), (225, 520), 24, (200, 90, 70)); limb(d, (225, 520), (255, 585), 22, SKIN)
    limb(d, (368, 420), (420, 470), 24, (200, 90, 70)); limb(d, (420, 470), (455, 440), 22, SKIN)
    face(d, 300, 330, 64, mood="tired", mustache=True)
    poly(d, [(238, 315), (244, 282), (300, 266), (356, 282), (362, 315), (345, 296), (300, 292), (255, 296)], (60, 56, 54))
    ell(d, 300, 270, 30, 10, (60, 56, 54))
    # breath puffs
    for i, (x, y, r) in enumerate([(385, 360, 12), (410, 345, 16), (442, 330, 20)]):
        d.ellipse(s([x - r, y - r, x + r, y + r]), outline=(150, 150, 158), width=4 * S)
    # sweat
    for x, y in ((228, 300), (372, 300)):
        poly(d, [(x, y - 12), (x - 7, y + 2), (x + 7, y + 2)], (130, 190, 240)); ell(d, x, y + 3, 7, 7, (130, 190, 240))

panels = [
    panel("Karthik", 32, "IT · 9 HRS AT A DESK", "“My back hurts by Friday.”", karthik),
    panel("Priya", 36, "WORKING MOM", "“I can't keep up with him.”", priya),
    panel("Ravi", 45, "DAD · 2ND FLOOR FLAT", "“Out of breath. Every day.”", ravi),
]
gap = 30
out = Image.new("RGB", (PW * 3 + gap * 4, PH + gap * 2), BG)
for i, p in enumerate(panels):
    out.paste(p, (gap + i * (PW + gap), gap))
out.save("/home/claude/chars/FitEats_strength_characters.png")
for i, p in enumerate(panels):
    p.save(f"/home/claude/chars/char_{i+1}.png")
print("ok")
