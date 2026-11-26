"""Composite rendered 3D frames with background, karaoke captions, kicker, muscle labels and bloom; pipe to ffmpeg."""
import sys, json, glob, subprocess, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.path.insert(0, "/home/claude/back")
import b2
from b2 import W, H, LIME, F, put

FPS = 30; TOTAL = 36.4; FIG_Y = 470
BGC = (9, 10, 12)
MONO = "/usr/share/fonts/truetype/google-fonts/ofl/anonymouspro/AnonymousPro-Bold.ttf"
def M(s): return ImageFont.truetype(MONO, s)

KICK = {"intro": "NO TIME FOR THE GYM?", "sweep": "COMPOUND LIFTS", "clean": "01 / HANG CLEAN & PRESS", "dead": "02 / DEADLIFT",
        "squat": "03 / BACK SQUAT", "push": "+5 MIN / PUSH-UPS", "cta": "MORE LIKE THIS"}
COUNT = {"clean": "01 / 03", "dead": "02 / 03", "squat": "03 / 03", "push": "BONUS"}
CHUNKS = [
 (0.00, 0.92, "No time for the gym?"), (1.38, 3.11, "You only need these three lifts."),
 (3.45, 4.94, "Together, they work almost"), (5.07, 6.61, "every major muscle in your body."),
 (7.24, 7.55, "One:"), (7.98, 9.82, "the barbell hang clean and press."),
 (10.29, 12.05, "It works your forearms, traps,"), (12.20, 14.32, "shoulders, triceps and upper back,"),
 (14.76, 16.54, "and your glutes and legs drive the bar up."),
 (17.21, 17.46, "Two:"), (17.89, 18.53, "the deadlift."),
 (19.00, 20.78, "It works your hamstrings, glutes,"), (20.96, 23.55, "lower back, lats, traps and grip."),
 (24.07, 24.40, "Three:"), (24.85, 26.03, "the barbell back squat."),
 (26.51, 28.19, "It works your quads, glutes,"), (28.43, 30.48, "inner thighs, hamstrings and core."),
 (31.03, 32.10, "Got five more minutes?"), (32.51, 33.83, "Add push-ups for your chest."),
 (34.38, 35.90, "Follow for more videos like this."),
]
KEY = {"three", "every", "muscle", "forearms", "traps", "shoulders", "triceps", "upper", "back", "glutes", "legs", "hamstrings",
       "lower", "lats", "grip", "quads", "inner", "thighs", "core", "five", "push-ups", "chest", "follow", "clean", "press",
       "deadlift", "squat", "one", "two", "three:"}
NAMES = {"forearms": "FOREARMS", "traps": "TRAPS", "shoulders": "SHOULDERS", "triceps": "TRICEPS", "upperback": "UPPER BACK",
         "glutes": "GLUTES", "quads": "QUADS", "hamstrings": "HAMSTRINGS", "lowerback": "LOWER BACK", "lats": "LATS", "grip": "GRIP",
         "innerthigh": "INNER THIGHS", "core": "CORE", "chest": "CHEST", "calves": "CALVES"}
LABELS = {"clean": {"forearms", "traps", "shoulders", "triceps", "upperback", "glutes", "quads"},
          "dead": {"hamstrings", "glutes", "lowerback", "lats", "traps", "grip"},
          "squat": {"quads", "glutes", "innerthigh", "hamstrings", "core"},
          "push": {"chest", "triceps", "shoulders", "core"}}
RENAME = {("clean", "quads"): "LEGS"}

@lru_cache(1)
def background():
    im = Image.new("RGBA", (W, H), BGC + (255,)); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(14, 15, 19, 255))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(14, 15, 19, 255))
    return im

def caption(d, t):
    cur = None
    for c in CHUNKS:
        if c[0] - 0.05 <= t <= c[1] + 0.45: cur = c
    if cur is None:
        prev = [c for c in CHUNKS if c[1] < t]
        if prev and t - prev[-1][1] < 0.9: cur = prev[-1]
    if cur is None: return
    t0, t1, text = cur
    words = text.split(); tot = sum(len(w) + 1 for w in words); acc = 0; times = []
    for w in words: times.append(t0 + (t1 - t0) * acc / tot); acc += len(w) + 1
    f = F("bold", 84); x, y = 80, 380; lh = 96
    for w, ws in zip(words, times):
        tw = d.textlength(w, font=f)
        if x + tw > W - 80: x = 80; y += lh
        spoken = t >= ws
        key = w.lower().strip(",.?:") in KEY
        col = (LIME if key else (244, 241, 234)) if spoken else (52, 56, 66)
        d.text((x, y), w, font=f, fill=col)
        x += tw + d.textlength(" ", font=f)

def labels(d, mode, anchors):
    want = LABELS.get(mode, set()); items = []
    for k, (ax, ay, v) in anchors.items():
        if k not in want or v <= 0.02: continue
        items.append([k, ax, ay + FIG_Y, v])
    for side in (0, 1):
        if mode == "push": col = sorted(items, key=lambda it: it[1]) if side else []
        else: col = sorted([it for it in items if (it[1] >= W / 2) == bool(side)], key=lambda it: it[2])
        ly = []
        for n, it in enumerate(col):
            if mode == "push": ly.append(800 + n * 52); continue
            y = max(it[2], (ly[-1] + 46) if ly else 0); ly.append(y)
        for it, y in zip(col, ly):
            k, ax, ay, v = it; name = RENAME.get((mode, k), NAMES[k]); f = M(32); tw = d.textlength(name, font=f)
            c = tuple(int(LIME[i] * v + BGC[i] * (1 - v)) for i in range(3))
            if side: tx = min(W - 50 - tw, max(ax + 120, 760)); lx = tx - 12
            else: tx = max(50, min(ax - 120 - tw, 320 - tw)); lx = tx + tw + 12
            d.line([(lx, y + 16), (ax, ay)], fill=c, width=2)
            d.ellipse((ax - 6, ay - 6, ax + 6, ay + 6), fill=c, outline=(9, 10, 12))
            d.text((tx, y), name, font=f, fill=c)

def bloom(fr):
    r, g, b, a = fr.split()
    mask = ImageChops.subtract(g, b).point(lambda v: 255 if v > 60 else int(v * 3))
    glow = Image.merge("RGBA", (r, g, b, ImageChops.multiply(mask, a)))
    small = glow.resize((fr.width // 6, fr.height // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    return small.resize(fr.size, Image.BILINEAR)

def frame(i, meta):
    t = i / FPS; m = meta.get(str(i)) or {"mode": "cta", "anchors": {}}
    mode = m["mode"]
    cv = background().copy(); d = ImageDraw.Draw(cv)
    d.rounded_rectangle((80, 214, W - 80, 222), 4, fill=(40, 43, 50))
    d.rounded_rectangle((80, 214, 80 + (W - 160) * min(1, t / TOTAL), 222), 4, fill=LIME)
    x = 82; fk = M(30)
    for ch in KICK[mode]:
        d.text((x, 330), ch, font=fk, fill=(150, 156, 168)); x += d.textlength(ch, font=fk) + 3
    if mode in COUNT: d.text((W - 82, 330), COUNT[mode], font=fk, fill=(150, 156, 168), anchor="ra")
    try:
        fr = Image.open(f"/home/claude/b3d/frames/f_{i:04d}.png").convert("RGBA")
    except FileNotFoundError:
        fr = None
    if fr is not None:
        g = bloom(fr); cv.alpha_composite(g, (0, FIG_Y)); cv.alpha_composite(fr, (0, FIG_Y))
    d = ImageDraw.Draw(cv)
    caption(d, t)
    labels(d, mode, m.get("anchors", {}))
    if mode == "cta":
        put(cv, "follow", W / 2, 1730, b2.back((t - 34.4) / 0.4))
    return cv.convert("RGB")

def main():
    b2.build_sprites()
    meta = {}
    for p in glob.glob("/home/claude/b3d/frames/meta_*.json"): meta.update(json.load(open(p)))
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(int(float(s) * FPS), meta).save(f"/home/claude/b3d/c_{s}.png")
        return
    out = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/b3d/video.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i, meta).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
