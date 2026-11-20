"""FitEats - 2 eggs a day for 14 days. Charcoal + yolk theme, voice + music.
Sentence timings come from timing.json (built from the voice's pauses).
python3 build.py stills t...   |   python3 build.py render
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (16, 16, 18); CARD = (30, 30, 34); TXT = (244, 241, 234); MUTE = (150, 146, 138)
YOLK = (255, 192, 40); WHITE = (250, 248, 242); RED = (232, 84, 62); GREEN = (88, 196, 120)
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

SENT = [
 "What happens if you eat two eggs every day, for fourteen days?",
 "First, the protein. Two eggs give you about twelve grams, with all nine essential amino acids.",
 "Then the part most people miss. Choline, for your brain and liver. Plus B12, selenium and vitamin D.",
 "Have them at breakfast, and most people stay fuller for longer. Fewer cravings before lunch.",
 "But here's the catch. Fried in oil or butter, you're adding calories you never planned for. Boiled or poached is the smart way.",
 "And if you have high cholesterol or a heart condition, check with your doctor first.",
 "Two eggs are a strong start. Not the whole plan. Want every meal high in protein, with calories counted? Comment MENU.",
]
_J = json.load(open("timing.json")); TM = _J["tm"]; CHUNKS = _J["chunks"]
TOTAL = TM[-1][1] + 1.3

# ---- word timeline for captions (spread by length inside each sentence) ----
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
    # chunk into lines of ~22 chars, show the chunk group (max 3 lines) containing the current word
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
            hl = any(k in w.lower() for k in ("twelve", "choline", "fuller", "catch", "boiled", "poached", "doctor", "menu"))
            col = YOLK if hl else TXT
            d.text((x, y), w, font=f, fill=mix(BG, col, 0.25 + 0.75 * p) if p > 0 else mix(BG, TXT, 0.18), anchor="ls")
            x += d.textlength(w + " ", font=f)
        y += 74

def egg(d, cx, cy, s, a, halved=False):
    if a <= 0: return
    rx, ry = 95 * s, 125 * s
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=mix(BG, WHITE, a))
    if halved:
        r = 58 * s; d.ellipse((cx - r, cy - r + 10 * s, cx + r, cy + r + 10 * s), fill=mix(BG, YOLK, a))

def tag(d, cx, cy, txt, a, col=YOLK, size=34, fg=None):
    if a <= 0: return
    f = F("bold", size); w = d.textlength(txt, font=f)
    d.rounded_rectangle((cx - w / 2 - 26, cy - size * 0.95, cx + w / 2 + 26, cy + size * 0.95), int(size * 0.95), fill=mix(BG, col, a))
    d.text((cx, cy + 2), txt, font=f, fill=mix(col, fg or BG, a), anchor="mm")

def head(d, y, txt, a, col=TXT, size=120):
    if a <= 0: return
    d.text((W / 2, y + (1 - a) * 30), txt, font=F("anton", size), fill=mix(BG, col, a), anchor="ms")

def sa(t, i):  # scene alpha from sentence timing
    s = TM[i][0] - 0.2; e = TM[i + 1][0] - 0.2 if i + 1 < len(TM) else 999
    if t < s or t >= e: return 0, s
    return min(prog(t, s, 0.3), clamp((e - t) / 0.2)), s

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((W / 2, 250), "F I T E A T S  ·  E G G   F A C T S", font=F("bold", 28), fill=MUTE, anchor="mm")
    d.line([(W / 2 - 40, 285), (W / 2 + 40, 285)], fill=YOLK, width=4)

    a, s = sa(t, 0)
    if a:
        egg(d, W / 2 - 120, 620, 1.0, prog(t, s + 0.1, 0.3) * a)
        egg(d, W / 2 + 120, 620, 1.0, prog(t, s + 0.4, 0.3) * a)
        head(d, 880, "2 EGGS A DAY", a * prog(t, s + 0.6), YOLK, 110)
        for i in range(14):
            r, c = divmod(i, 7); x = 160 + c * 110; y = 960 + r * 120
            p = prog(t, s + 1.4 + i * 0.12, 0.2) * a
            d.rounded_rectangle((x, y, x + 90, y + 95), 14, fill=mix(BG, YOLK if p > 0.5 else CARD, max(a * 0.9, p)))
            d.text((x + 45, y + 50), str(i + 1), font=F("bold", 34), fill=mix(BG, BG if p > 0.5 else MUTE, a), anchor="mm")
        head(d, 1290 + 60, "× 14 DAYS", a * prog(t, s + 1.4), TXT, 90)

    a, s = sa(t, 1)
    if a:
        egg(d, W / 2, 600, 1.1, a, halved=True)
        n = 12 * prog(t, s + 1.0, 2.2)
        head(d, 1020, f"{n:.0f} g", a, YOLK, 230)
        d.text((W / 2, 1080), "PROTEIN FROM 2 EGGS", font=F("bold", 40), fill=mix(BG, MUTE, a), anchor="mm")
        tag(d, W / 2, 1190, "ALL 9 ESSENTIAL AMINO ACIDS", prog(t, s + 3.2, 0.3) * a, GREEN, 32)

    a, s = sa(t, 2)
    if a:
        head(d, 560, "THE PART MOST", a, TXT, 100); head(d, 680, "PEOPLE MISS", a, YOLK, 100)
        items = [("CHOLINE", "BRAIN + LIVER", 1.8), ("B12", "ENERGY + NERVES", 4.3), ("SELENIUM", "ANTIOXIDANT", 5.2), ("VITAMIN D", "BONES + IMMUNITY", 6.1)]
        for i, (k, v, dt) in enumerate(items):
            p = prog(t, s + dt, 0.3) * a; y = 790 + i * 150
            if p <= 0: continue
            d.rounded_rectangle((110, y, W - 110, y + 120), 20, fill=mix(BG, CARD, p))
            d.text((150, y + 62), k, font=F("anton", 64), fill=mix(BG, YOLK, p), anchor="lm")
            d.text((W - 150, y + 62), v, font=F("bold", 32), fill=mix(BG, TXT, p), anchor="rm")

    a, s = sa(t, 3)
    if a:
        head(d, 560, "FULLER FOR LONGER", a, YOLK, 104)
        x0, x1, yb, yt = 140, W - 140, 1240, 760
        d.line([(x0, yb), (x1, yb)], fill=mix(BG, MUTE, a), width=3)
        for i, lab in enumerate(["8 AM", "10 AM", "12 PM", "1 PM"]):
            d.text((x0 + i * (x1 - x0) / 3, yb + 40), lab, font=F("med", 28), fill=mix(BG, MUTE, a), anchor="mm")
        pr = prog(t, s + 0.8, 3.0)
        pts_e = [(x0 + (x1 - x0) * k / 40, yt + 60 + 80 * (k / 40) ** 2) for k in range(int(40 * pr) + 1)]
        pts_l = [(x0 + (x1 - x0) * k / 40, yt + 60 + 300 * min(1, (k / 40) * 1.4)) for k in range(int(40 * pr) + 1)]
        if len(pts_l) > 1: d.line(pts_l, fill=mix(BG, (110, 106, 100), a), width=8)
        if len(pts_e) > 1: d.line(pts_e, fill=mix(BG, YOLK, a), width=10)
        d.text((x1, yt + 10), "EGG BREAKFAST", font=F("bold", 28), fill=mix(BG, YOLK, a * pr), anchor="rm")
        d.text((x0, yt - 10), "FULLNESS (ILLUSTRATIVE)", font=F("med", 26), fill=mix(BG, MUTE, a), anchor="lm")
        d.text((x1, yt + 410), "LIGHT BREAKFAST", font=F("bold", 28), fill=mix(BG, MUTE, a * pr), anchor="rm")
        tag(d, W / 2, 1390, "FEWER CRAVINGS BEFORE LUNCH", prog(t, s + 3.6, 0.3) * a, YOLK, 32)

    a, s = sa(t, 4)
    if a:
        head(d, 560, "THE CATCH", a, RED, 130)
        for i, (lab, sub, col, ok, dt) in enumerate([("FRIED", "+ OIL / BUTTER", RED, False, 1.3), ("BOILED / POACHED", "SMART WAY", GREEN, True, 5.0)]):
            p = prog(t, s + dt, 0.3) * a; y = 720 + i * 300
            if p <= 0: continue
            d.rounded_rectangle((110, y, W - 110, y + 240), 26, fill=mix(BG, CARD, p), outline=mix(BG, col, p), width=4)
            d.text((160, y + 95), lab, font=F("anton", 70), fill=mix(BG, TXT, p), anchor="lm")
            d.text((160, y + 170), sub, font=F("bold", 34), fill=mix(BG, col, p), anchor="lm")
            cx, cy = W - 210, y + 120
            d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), fill=mix(BG, col, p))
            if ok: d.line([(cx - 28, cy), (cx - 6, cy + 24), (cx + 30, cy - 22)], fill=BG, width=12)
            else:
                d.line([(cx - 24, cy - 24), (cx + 24, cy + 24)], fill=BG, width=12); d.line([(cx - 24, cy + 24), (cx + 24, cy - 24)], fill=BG, width=12)

    a, s = sa(t, 5)
    if a:
        cx, cy = W / 2, 820
        d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline=mix(BG, YOLK, a), width=10)
        d.rectangle((cx - 22, cy - 80, cx + 22, cy + 80), fill=mix(BG, YOLK, a)); d.rectangle((cx - 80, cy - 22, cx + 80, cy + 22), fill=mix(BG, YOLK, a))
        head(d, 1110, "HIGH CHOLESTEROL", a * prog(t, s + 0.6), TXT, 96)
        head(d, 1220, "OR HEART CONDITION?", a * prog(t, s + 1.2), TXT, 96)
        tag(d, W / 2, 1330, "ASK YOUR DOCTOR FIRST", prog(t, s + 2.6, 0.3) * a, YOLK, 34)

    a, s = sa(t, 6)
    if a:
        head(d, 560, "A STRONG START.", a, TXT, 110)
        head(d, 690, "NOT THE WHOLE PLAN.", a * prog(t, s + 1.6), YOLK, 96)
        p = prog(t, s + 3.0, 0.4) * a
        if p:
            fb = F("bold", 150); d.text((W / 2, 900), "FitEats", font=fb, fill=mix(BG, TXT, p), anchor="mm")
            tw = d.textlength("FitEats", font=fb); d.ellipse((W / 2 + tw / 2 + 4, 928, W / 2 + tw / 2 + 36, 960), fill=mix(BG, YOLK, p))
            d.text((W / 2, 1020), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 28), fill=mix(BG, MUTE, p), anchor="mm")
        tag(d, W / 2, 1160, "COMMENT “MENU”", prog(t, TM[6][1] - 1.0, 0.3) * a, YOLK, 50)

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
