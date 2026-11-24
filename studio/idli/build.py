"""FitEats - Idli and dosa aren't the enemy: the protein fix. Same engine as eggs/coffee.
python3 build.py stills t...   |   python3 build.py render
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (16, 16, 18); CARD = (30, 30, 34); TXT = (244, 241, 234); MUTE = (150, 146, 138)
ACC = (120, 214, 120); IDLI = (238, 234, 222); DOSA = (214, 150, 64); RED = (226, 82, 60)
CHANA = (232, 190, 70); MOONG = (120, 168, 70); PEANUT = (196, 140, 86); GNUT = (176, 128, 80)
GF = "/usr/share/fonts/truetype/google-fonts/ofl/"; FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def F(k, s):
    if (k, s) not in _fc:
        _fc[(k, s)] = ImageFont.truetype({"anton": GF + "anton/Anton-Regular.ttf", "bold": FD + "InterDisplay-Bold.otf",
                                          "med": FD + "InterDisplay-Medium.otf"}[k], s)
    return _fc[(k, s)]
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, t0, d=0.3): return ease((t - t0) / d)
def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

CHUNKS = [
 (0.00, 1.72, "Idli and dosa aren't the enemy."),
 (2.18, 5.20, "The problem is how little protein idly and dosa has."),
 (5.71, 8.51, "Four idlis give you only about ten grams of protein."),
 (9.10, 10.09, "Here's a simple fix."),
 (10.55, 12.91, "Grind soaked chana or moong dal in Mixer"),
 (13.16, 14.44, "and add to your idli batter,"),
 (14.76, 16.61, "for more protein in every idli."),
 (17.08, 17.45, "Next,"),
 (17.72, 19.80, "swap tomato chutney for groundnut chutney."),
 (20.35, 23.09, "A handful of peanuts adds about five grams of protein."),
 (23.53, 24.65, "Same breakfast you love,"),
 (24.99, 27.21, "now a healthy, high-protein breakfast."),
 (27.63, 28.39, "Save this video."),
 (28.73, 30.59, "Follow FitEats for more tips like this."),
 (30.97, 31.98, "No time to cook healthy?"),
 (32.44, 33.55, "Order from us on WhatsApp."),
 (33.95, 34.80, "Link in bio."),
]
TM = [(0.00, 5.20), (5.71, 8.51), (9.10, 16.61), (17.08, 23.09), (23.53, 27.21), (27.63, 30.59), (30.97, 34.80)]
TOTAL = 36.3
HL = ("enemy", "protein", "ten", "chana", "moong", "groundnut", "five", "high-protein", "save", "fiteats", "whatsapp")

WORDS = []
for a, b, txt in CHUNKS:
    si = next(i for i, (s0, e0) in enumerate(TM) if s0 - 0.01 <= a <= e0)
    ws = txt.split(); L = [len(w) + 2 for w in ws]; tot = sum(L); t = a
    for w, l in zip(ws, L):
        WORDS.append((si, w, t)); t += (b - a) * l / tot

def caption(d, t):
    si = next((i for i, (a, b) in enumerate(TM) if a - 0.15 <= t < (TM[i + 1][0] - 0.15 if i + 1 < len(TM) else 99)), None)
    if si is None: return
    ws = [(w, t0) for s, w, t0 in WORDS if s == si]
    f = F("bold", 54); lines, cur = [], []
    for w, t0 in ws:
        test = " ".join(x for x, _ in cur + [(w, t0)])
        if d.textlength(test, font=f) > 860 and cur: lines.append(cur); cur = []
        cur.append((w, t0))
    if cur: lines.append(cur)
    groups = [lines[i:i + 2] for i in range(0, len(lines), 2)]
    gi = 0
    for i, g in enumerate(groups):
        if t >= g[0][0][1] - 0.05: gi = i
    y = 1500
    for ln in groups[gi]:
        x = (W - d.textlength(" ".join(w for w, _ in ln), font=f)) / 2
        for w, t0 in ln:
            p = prog(t, t0 - 0.05, 0.18)
            hl = any(w.lower().strip(",.?") == k or w.lower().startswith(k) for k in HL)
            col = ACC if hl else TXT
            d.text((x, y), w, font=f, fill=mix(BG, col, 0.25 + 0.75 * p) if p > 0 else mix(BG, TXT, 0.18), anchor="ls")
            x += d.textlength(w + " ", font=f)
        y += 74

def tag(d, cx, cy, txt, a, col=ACC, size=34, fg=None):
    if a <= 0: return
    f = F("bold", size); w = d.textlength(txt, font=f)
    d.rounded_rectangle((cx - w / 2 - 26, cy - size * 0.95, cx + w / 2 + 26, cy + size * 0.95), int(size * 0.95), fill=mix(BG, col, a))
    d.text((cx, cy + 2), txt, font=f, fill=mix(col, fg or BG, a), anchor="mm")

def head(d, y, txt, a, col=TXT, size=120):
    if a <= 0: return
    d.text((W / 2, y + (1 - a) * 30), txt, font=F("anton", size), fill=mix(BG, col, a), anchor="ms")

def sa(t, i):
    s = TM[i][0] - 0.2; e = TM[i + 1][0] - 0.2 if i + 1 < len(TM) else 999
    if t < s or t >= e: return 0, s
    return min(prog(t, s, 0.3), clamp((e - t) / 0.2)), s

# ---------- props ----------
def idli(d, cx, cy, s, a):
    if a <= 0: return
    d.ellipse((cx - 70 * s, cy - 34 * s, cx + 70 * s, cy + 34 * s), fill=mix(BG, (200, 196, 184), a))
    d.ellipse((cx - 70 * s, cy - 44 * s, cx + 70 * s, cy + 22 * s), fill=mix(BG, IDLI, a))
    for dx, dy in ((-30, -14), (10, -22), (34, -6), (-6, 0)):
        d.ellipse((cx + (dx - 3) * s, cy + (dy - 3) * s, cx + (dx + 3) * s, cy + (dy + 3) * s), fill=mix(BG, (214, 208, 194), a))

def dosa(d, cx, cy, s, a):
    if a <= 0: return
    d.polygon([(cx - 150 * s, cy + 40 * s), (cx + 150 * s, cy + 40 * s), (cx, cy - 90 * s)], fill=mix(BG, DOSA, a))
    d.polygon([(cx - 150 * s, cy + 40 * s), (cx, cy - 90 * s), (cx - 40 * s, cy + 40 * s)], fill=mix(BG, (186, 120, 44), a))

def plate(d, cx, cy, r, a):
    d.ellipse((cx - r, cy - r * 0.42, cx + r, cy + r * 0.42), fill=mix(BG, (58, 58, 64), a))
    d.ellipse((cx - r * 0.82, cy - r * 0.32, cx + r * 0.82, cy + r * 0.32), fill=mix(BG, (72, 72, 80), a))

def bowl(d, cx, cy, s, col, a, label=None):
    if a <= 0: return
    d.pieslice((cx - 110 * s, cy - 90 * s, cx + 110 * s, cy + 90 * s), 0, 180, fill=mix(BG, (180, 180, 188), a))
    d.ellipse((cx - 110 * s, cy - 22 * s, cx + 110 * s, cy + 22 * s), fill=mix(BG, col, a))
    if label: d.text((cx, cy + 130 * s), label, font=F("bold", int(34 * s)), fill=mix(BG, TXT, a), anchor="mm")

def meter(d, y, level, a, label):
    if a <= 0: return
    x0, x1 = 160, W - 160
    d.text((x0, y - 46), "PROTEIN", font=F("bold", 30), fill=mix(BG, MUTE, a), anchor="lm")
    d.text((x1, y - 46), label, font=F("anton", 44), fill=mix(BG, ACC, a), anchor="rm")
    d.rounded_rectangle((x0, y, x1, y + 44), 22, fill=mix(BG, CARD, a))
    if level > 0.02:
        d.rounded_rectangle((x0, y, x0 + (x1 - x0) * level, y + 44), 22, fill=mix(BG, ACC, a))

def grains(d, cx, cy, n, col, a, t0, t, spread=150, oval=False):
    import random
    rnd = random.Random(int(cx * 7 + cy))
    for i in range(n):
        p = prog(t, t0 + i * 0.03, 0.35) * a
        if p <= 0: continue
        x = cx + rnd.uniform(-spread, spread); y = cy - 220 * (1 - p) + rnd.uniform(-40, 40)
        r = 14 if not oval else 11
        d.ellipse((x - r * (1.4 if oval else 1), y - r, x + r * (1.4 if oval else 1), y + r), fill=mix(BG, col, p))

def mixer(d, cx, cy, a):
    if a <= 0: return
    d.polygon([(cx - 90, cy - 170), (cx + 90, cy - 170), (cx + 70, cy + 60), (cx - 70, cy + 60)], fill=mix(BG, (90, 96, 106), a))
    d.rectangle((cx - 100, cy - 190, cx + 100, cy - 165), fill=mix(BG, (60, 64, 72), a))
    d.rounded_rectangle((cx - 110, cy + 60, cx + 110, cy + 150), 18, fill=mix(BG, (200, 200, 208), a))
    d.ellipse((cx - 22, cy + 85, cx + 22, cy + 129), fill=mix(BG, (60, 64, 72), a))

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((W / 2, 250), "F I T E A T S  ·  P R O T E I N   F I X", font=F("bold", 28), fill=MUTE, anchor="mm")
    d.line([(W / 2 - 40, 285), (W / 2 + 40, 285)], fill=ACC, width=4)

    a, s = sa(t, 0)  # hook
    if a:
        plate(d, W / 2, 660, 330, a)
        for k, dx in enumerate((-170, 0, 170)):
            idli(d, W / 2 + dx, 640, 0.95, prog(t, s + 0.1 + k * 0.15, 0.3) * a)
        dosa(d, W / 2, 470, 1.3, prog(t, s + 0.4, 0.3) * a)
        head(d, 930, "NOT THE ENEMY", a * prog(t, s + 0.6), ACC, 120)
        p = prog(t, s + 2.4, 0.3) * a
        meter(d, 1110, 0.12 * prog(t, s + 2.6, 0.8), p, "LOW")
        tag(d, W / 2, 1290, "THE PROBLEM: TOO LITTLE PROTEIN", prog(t, s + 3.2, 0.3) * a, RED, 32)

    a, s = sa(t, 1)  # 4 idlis = 10 g
    if a:
        plate(d, W / 2, 640, 360, a)
        for k, (dx, dy) in enumerate(((-190, 10), (-63, -20), (63, 10), (190, -20))):
            idli(d, W / 2 + dx, 630 + dy, 0.85, prog(t, s + 0.1 + k * 0.15, 0.3) * a)
        head(d, 380, "4 IDLIS", a, TXT, 110)
        n = 10 * prog(t, s + 1.4, 1.0)
        head(d, 960, f"≈ {n:.0f} g PROTEIN", a * prog(t, s + 1.2), ACC, 120)
        meter(d, 1110, 0.2 * prog(t, s + 1.4, 1.0), a, "≈ 10 g")

    a, s = sa(t, 2)  # fix 1: dal in batter
    if a:
        head(d, 400, "FIX 1", a, ACC, 90)
        d.text((W / 2, 470), "Grind soaked dal, add to batter", font=F("bold", 40), fill=mix(BG, TXT, a), anchor="mm")
        mixer(d, W / 2, 760, a * prog(t, s + 0.2, 0.3))
        grains(d, W / 2 - 40, 640, 16, CHANA, a, s + 1.5, t, 70)
        grains(d, W / 2 + 40, 640, 16, MOONG, a, s + 2.0, t, 70, oval=True)
        tag(d, W / 2 - 170, 1000, "CHANA DAL", prog(t, s + 1.6, 0.3) * a, CHANA, 30)
        tag(d, W / 2 + 170, 1000, "MOONG DAL", prog(t, s + 2.1, 0.3) * a, MOONG, 30)
        meter(d, 1160, 0.2 + 0.25 * prog(t, s + 5.8, 0.8), prog(t, s + 5.4, 0.3) * a, "+ DAL")

    a, s = sa(t, 3)  # fix 2: groundnut chutney
    if a:
        head(d, 400, "FIX 2", a, ACC, 90)
        sw = prog(t, s + 1.0, 0.5)
        bowl(d, W / 2 - 220, 700, 1.0, RED, a * (1 - 0.6 * sw), "TOMATO")
        if sw > 0.3:
            d.line([(W / 2 - 330, 590), (W / 2 - 110, 830)], fill=mix(BG, RED, a * sw), width=10)
            d.line([(W / 2 - 110, 590), (W / 2 - 330, 830)], fill=mix(BG, RED, a * sw), width=10)
        d.text((W / 2, 700), "→", font=F("anton", 110), fill=mix(BG, MUTE, a * sw), anchor="mm")
        bowl(d, W / 2 + 220, 700, 1.0, GNUT, a * sw, "GROUNDNUT")
        grains(d, W / 2 + 220, 620, 10, PEANUT, a, s + 3.3, t, 60, oval=True)
        head(d, 1020, "+ ≈ 5 g PROTEIN", prog(t, s + 3.6, 0.3) * a, ACC, 100)
        meter(d, 1160, 0.45 + 0.2 * prog(t, s + 4.0, 0.8), prog(t, s + 3.6, 0.3) * a, "+ PEANUTS")

    a, s = sa(t, 4)  # same breakfast, now high protein
    if a:
        plate(d, W / 2, 640, 360, a)
        for k, dx in enumerate((-170, 0, 170)):
            idli(d, W / 2 + dx, 640, 0.95, a)
        bowl(d, W / 2, 470, 0.6, GNUT, a)
        head(d, 920, "SAME BREAKFAST.", a, TXT, 104)
        head(d, 1040, "HIGH PROTEIN.", a * prog(t, s + 1.4), ACC, 104)
        meter(d, 1160, 0.65 + 0.25 * prog(t, s + 1.6, 0.8), a, "HIGH")

    a, s = sa(t, 5)  # save + follow
    if a:
        x0, y0 = W / 2 - 70, 470
        bp = prog(t, s + 0.1, 0.4) * a
        d.polygon([(x0, y0), (x0 + 140, y0), (x0 + 140, y0 + 180), (x0 + 70, y0 + 130), (x0, y0 + 180)], fill=mix(BG, ACC, bp))
        head(d, 820, "SAVE THIS", a, TXT, 120)
        head(d, 960, "FOLLOW @FIT_EATS_25", a * prog(t, s + 1.1), ACC, 84)
        d.text((W / 2, 1040), "More tips like this, every day", font=F("bold", 36), fill=mix(BG, MUTE, a * prog(t, s + 1.3)), anchor="mm")

    a, s = sa(t, 6)  # CTA
    if a:
        head(d, 560, "NO TIME TO COOK?", a, TXT, 104)
        p = prog(t, s + 1.2, 0.4) * a
        if p:
            fb = F("bold", 150); d.text((W / 2, 780), "FitEats", font=fb, fill=mix(BG, TXT, p), anchor="mm")
            tw = d.textlength("FitEats", font=fb); d.ellipse((W / 2 + tw / 2 + 4, 808, W / 2 + tw / 2 + 36, 840), fill=mix(BG, ACC, p))
            d.text((W / 2, 900), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 28), fill=mix(BG, MUTE, p), anchor="mm")
        tag(d, W / 2, 1060, "ORDER ON WHATSAPP · LINK IN BIO", prog(t, s + 1.6, 0.3) * a, ACC, 42)

    if 5.5 < t < 23.3:
        d.text((W / 2, 1830), "Estimate: idli about 2.5 g protein (39 g piece); 20 g peanuts about 5 g. Varies by recipe.",
               font=F("med", 22), fill=(96, 94, 90), anchor="mm")
    caption(d, t)
    return img

def main():
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(float(s)).save(f"still_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "video_tmp.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); os.rename("video_tmp.mp4", "video_only.mp4")

if __name__ == "__main__":
    main()
