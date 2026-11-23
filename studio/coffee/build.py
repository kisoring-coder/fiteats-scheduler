"""FitEats - 3 filter coffees a day for 30 days. Charcoal + coffee theme, voice + music.
Same engine and style as studio/eggs. Sentence timings from the voice's pauses.
python3 build.py stills t...   |   python3 build.py render
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (16, 16, 18); CARD = (30, 30, 34); TXT = (244, 241, 234); MUTE = (150, 146, 138)
COF = (222, 158, 78); CREAM = (240, 226, 200); BROWN = (122, 78, 44); RED = (232, 84, 62); GREEN = (88, 196, 120)
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

# speech segments from silencedetect on dl/voice.mp3
CHUNKS = [
 (0.00, 3.68, "What happens if you drink three filter coffees a day, for thirty days?"),
 (4.19, 4.61, "First,"), (4.91, 5.32, "one cup."),
 (5.86, 9.00, "A hundred millilitres of toned milk, about sixty calories."),
 (9.36, 10.25, "Two spoons of sugar,"), (10.57, 11.40, "another thirty-two."),
 (11.81, 13.35, "That's about ninety calories a cup."),
 (13.93, 14.58, "Three cups,"), (14.83, 16.99, "around two hundred and seventy calories a day,"),
 (17.30, 18.44, "before a single meal."),
 (18.89, 19.97, "Now the thirty days."), (20.30, 22.31, "Over eight thousand calories."),
 (22.62, 23.46, "And the sugar alone?"), (23.78, 25.75, "About seven hundred and twenty grams."),
 (26.05, 27.87, "Almost a full one-kilo packet."),
 (28.31, 29.54, "You don't have to quit coffee."), (29.91, 30.77, "Make it one spoon,"),
 (31.03, 31.43, "or none,"), (31.75, 33.36, "and that number drops fast."),
 (33.79, 36.43, "Want every meal high in protein, with calories counted?"),
 (36.79, 37.57, "Order on WhatsApp."), (37.97, 38.60, "Link in bio."),
]
TM = [(0.00, 3.68), (4.19, 11.40), (11.81, 18.44), (18.89, 22.31), (22.62, 27.87), (28.31, 33.36), (33.79, 38.60)]
TOTAL = 39.9
HL = ("three", "thirty", "sixty", "thirty-two", "ninety", "seventy", "single", "eight", "thousand", "seven", "twenty",
      "one-kilo", "spoon", "none", "fast", "protein", "whatsapp")

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
            col = COF if hl else TXT
            d.text((x, y), w, font=f, fill=mix(BG, col, 0.25 + 0.75 * p) if p > 0 else mix(BG, TXT, 0.18), anchor="ls")
            x += d.textlength(w + " ", font=f)
        y += 74

def tumbler(d, cx, cy, s, a, steam_t=None):
    """South Indian davara-tumbler: tumbler sitting in a wide bowl, with steam."""
    if a <= 0: return
    col = mix(BG, (196, 196, 204), a); dark = mix(BG, (150, 150, 160), a)
    # davara (bowl)
    d.polygon([(cx - 130 * s, cy + 40 * s), (cx + 130 * s, cy + 40 * s), (cx + 100 * s, cy + 110 * s), (cx - 100 * s, cy + 110 * s)], fill=dark)
    d.rectangle((cx - 135 * s, cy + 30 * s, cx + 135 * s, cy + 46 * s), fill=col)
    # tumbler
    d.polygon([(cx - 70 * s, cy - 150 * s), (cx + 70 * s, cy - 150 * s), (cx + 55 * s, cy + 40 * s), (cx - 55 * s, cy + 40 * s)], fill=col)
    d.rectangle((cx - 76 * s, cy - 160 * s, cx + 76 * s, cy - 146 * s), fill=mix(BG, (225, 225, 232), a))
    d.ellipse((cx - 66 * s, cy - 158 * s, cx + 66 * s, cy - 140 * s), fill=mix(BG, BROWN, a))
    d.ellipse((cx - 48 * s, cy - 156 * s, cx + 48 * s, cy - 144 * s), fill=mix(BG, CREAM, a * 0.85))
    if steam_t is not None:
        for k in (-1, 0, 1):
            ph = (steam_t * 0.8 + k * 0.33) % 1.0
            x = cx + k * 34 * s; y0 = cy - 175 * s - ph * 110 * s
            al = a * (1 - ph) * 0.8
            d.arc((x - 18 * s, y0 - 40 * s, x + 18 * s, y0), 200, 340, fill=mix(BG, MUTE, al), width=max(3, int(6 * s)))

def tag(d, cx, cy, txt, a, col=COF, size=34, fg=None):
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

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((W / 2, 250), "F I T E A T S  ·  C O F F E E   M A T H", font=F("bold", 28), fill=MUTE, anchor="mm")
    d.line([(W / 2 - 40, 285), (W / 2 + 40, 285)], fill=COF, width=4)

    a, s = sa(t, 0)  # hook
    if a:
        for k, dx in enumerate((-260, 0, 260)):
            tumbler(d, W / 2 + dx, 640, 0.78, prog(t, s + 0.1 + k * 0.25, 0.3) * a, t)
        head(d, 910, "3 FILTER COFFEES", a * prog(t, s + 0.8), COF, 104)
        head(d, 1030, "A DAY", a * prog(t, s + 1.0), TXT, 96)
        head(d, 1200, "× 30 DAYS = ?", a * prog(t, s + 2.2), TXT, 110)

    a, s = sa(t, 1)  # one cup breakdown
    if a:
        tumbler(d, W / 2, 560, 0.95, a, t)
        rows = [("TONED MILK", "100 ml", "59 kcal", 1.6), ("SUGAR", "2 tsp · 8 g", "32 kcal", 5.2)]
        for i, (k, q, v, dt) in enumerate(rows):
            p = prog(t, s + dt, 0.3) * a; y = 760 + i * 170
            if p <= 0: continue
            d.rounded_rectangle((110, y, W - 110, y + 140), 22, fill=mix(BG, CARD, p))
            d.text((150, y + 52), k, font=F("anton", 60), fill=mix(BG, TXT, p), anchor="lm")
            d.text((150, y + 108), q, font=F("bold", 30), fill=mix(BG, MUTE, p), anchor="lm")
            d.text((W - 150, y + 72), v, font=F("anton", 72), fill=mix(BG, COF, p), anchor="rm")
        d.text((W / 2, 1140), "Aavin toned milk: 59 kcal / 100 ml · 1 tsp sugar ≈ 4 g ≈ 16 kcal",
               font=F("med", 26), fill=mix(BG, MUTE, a * prog(t, s + 5.6)), anchor="mm")

    a, s = sa(t, 2)  # per cup, per day
    if a:
        n = 91 * prog(t, s + 0.2, 1.2)
        head(d, 640, f"≈ {n:.0f} kcal", a, COF, 170)
        d.text((W / 2, 700), "IN ONE CUP", font=F("bold", 40), fill=mix(BG, MUTE, a), anchor="mm")
        for k, dx in enumerate((-260, 0, 260)):
            tumbler(d, W / 2 + dx, 980, 0.6, prog(t, s + 2.1 + k * 0.2, 0.3) * a)
        p = prog(t, s + 3.0, 0.3) * a
        head(d, 1250, "≈ 270 kcal / DAY", p, TXT, 104)
        tag(d, W / 2, 1360, "BEFORE A SINGLE MEAL", prog(t, s + 5.5, 0.3) * a, COF, 34)

    a, s = sa(t, 3)  # 30 days
    if a:
        for i in range(30):
            r, c = divmod(i, 6); x = 165 + c * 128; y = 420 + r * 100
            p = prog(t, s + 0.2 + i * 0.05, 0.15) * a
            d.rounded_rectangle((x, y, x + 110, y + 84), 14, fill=mix(BG, COF if p > 0.5 else CARD, max(a * 0.9, p)))
            d.text((x + 55, y + 44), str(i + 1), font=F("bold", 30), fill=mix(BG, BG if p > 0.5 else MUTE, a), anchor="mm")
        n = 8190 * prog(t, s + 1.4, 1.6)
        head(d, 1110, f"{n:,.0f} kcal", a * prog(t, s + 1.2), COF, 150)
        d.text((W / 2, 1170), "IN 30 DAYS · JUST FROM COFFEE", font=F("bold", 38), fill=mix(BG, MUTE, a), anchor="mm")

    a, s = sa(t, 4)  # sugar
    if a:
        head(d, 520, "THE SUGAR ALONE", a, TXT, 100)
        n = 720 * prog(t, s + 1.0, 2.0)
        head(d, 760, f"{n:.0f} g", a * prog(t, s + 0.9), COF, 200)
        # 1 kg packet outline with fill level
        px0, px1, py0, py1 = W / 2 - 170, W / 2 + 170, 830, 1330
        d.rounded_rectangle((px0, py0, px1, py1), 24, outline=mix(BG, CREAM, a), width=6)
        lvl = 0.72 * prog(t, s + 1.0, 2.0)
        if lvl > 0:
            d.rounded_rectangle((px0 + 10, py1 - 10 - (py1 - py0 - 20) * lvl, px1 - 10, py1 - 10), 16, fill=mix(BG, (250, 246, 236), a))
        d.text((W / 2, py0 + 60), "SUGAR", font=F("anton", 56), fill=mix(BG, CREAM, a), anchor="mm")
        d.text((W / 2, py0 + 115), "1 kg", font=F("bold", 40), fill=mix(BG, MUTE, a), anchor="mm")
        tag(d, W / 2, 1400, "ALMOST A FULL 1-KG PACKET", prog(t, s + 3.5, 0.3) * a, COF, 34)

    a, s = sa(t, 5)  # don't quit
    if a:
        head(d, 560, "KEEP THE COFFEE.", a, TXT, 110)
        head(d, 690, "CUT THE SUGAR.", a * prog(t, s + 1.4), COF, 110)
        rows = [("1 SPOON", "SAVES ≈ 1,440 kcal / MONTH", 1.7), ("NO SUGAR", "SAVES ≈ 2,880 kcal / MONTH", 2.8)]
        for i, (k, v, dt) in enumerate(rows):
            p = prog(t, s + dt, 0.3) * a; y = 790 + i * 190
            if p <= 0: continue
            d.rounded_rectangle((110, y, W - 110, y + 150), 24, fill=mix(BG, CARD, p), outline=mix(BG, GREEN, p), width=4)
            d.text((150, y + 75), k, font=F("anton", 64), fill=mix(BG, TXT, p), anchor="lm")
            d.text((W - 150, y + 75), v, font=F("bold", 30), fill=mix(BG, GREEN, p), anchor="rm")

    a, s = sa(t, 6)  # CTA
    if a:
        head(d, 560, "EVERY MEAL", a, TXT, 110)
        head(d, 690, "HIGH IN PROTEIN.", a * prog(t, s + 0.8), COF, 104)
        p = prog(t, s + 1.6, 0.4) * a
        if p:
            fb = F("bold", 150); d.text((W / 2, 900), "FitEats", font=fb, fill=mix(BG, TXT, p), anchor="mm")
            tw = d.textlength("FitEats", font=fb); d.ellipse((W / 2 + tw / 2 + 4, 928, W / 2 + tw / 2 + 36, 960), fill=mix(BG, COF, p))
            d.text((W / 2, 1020), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 28), fill=mix(BG, MUTE, p), anchor="mm")
        tag(d, W / 2, 1160, "ORDER ON WHATSAPP · LINK IN BIO", prog(t, s + 3.0, 0.3) * a, COF, 42)

    # standing estimate note
    if 4.0 < t < 28.0:
        d.text((W / 2, 1830), "Estimate: 100 ml toned milk + 2 tsp sugar per cup", font=F("med", 24), fill=(96, 94, 90), anchor="mm")
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
