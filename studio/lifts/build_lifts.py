"""FitEats reel: 'No time for the gym? 3 compound lifts' — PrimeFit-style blueprint anatomy, lime accent."""
import math, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import b2
from b2 import W, H, FPS, LIME, GREY, TXT, F, clamp, back, ease, put, SP
import lifts as Lf
Lf.Z = 1.3
Z = Lf.Z

TOTAL = 33.4
BGC = (9, 10, 12)
MONO = "/usr/share/fonts/truetype/google-fonts/ofl/anonymouspro/AnonymousPro-Bold.ttf"
def M(s): return ImageFont.truetype(MONO, s)

SC = [  # start, kicker, headline, mode, counter
 (0.00, "NO TIME FOR THE GYM?", "Only {3 lifts}", "intro", ""),
 (3.45, "COMPOUND LIFTS", "Almost {every muscle}", "sweep", ""),
 (7.24, "01 / HANG CLEAN & PRESS", "Arms, {shoulders} , back", "clean", "01 / 03"),
 (17.21, "02 / DEADLIFT", "Hamstrings, {glutes} , back", "dead", "02 / 03"),
 (24.07, "03 / BACK SQUAT", "{Quads} , glutes, core", "squat", "03 / 03"),
 (31.04, "MORE LIKE THIS", "Follow for {more}", "cta", ""),
]
HL = {
 "clean": [("forearms", 10.85), ("traps", 11.6), ("shoulders", 12.2), ("triceps", 13.0), ("upperback", 13.6), ("glutes", 15.2), ("legs", 15.7)],
 "dead": [("hamstrings", 19.6), ("glutes", 20.3), ("lowerback", 21.0), ("lats", 21.8), ("traps", 22.5), ("grip", 23.1)],
 "squat": [("quads", 27.1), ("glutes", 27.7), ("innerthigh", 28.45), ("hamstrings", 29.3), ("core", 30.0)],
}
NAMES = {"forearms": "FOREARMS", "traps": "TRAPS", "shoulders": "SHOULDERS", "triceps": "TRICEPS", "upperback": "UPPER BACK",
         "glutes": "GLUTES", "legs": "LEGS", "hamstrings": "HAMSTRINGS", "lowerback": "LOWER BACK", "lats": "LATS",
         "grip": "GRIP", "quads": "QUADS", "innerthigh": "INNER THIGHS", "core": "CORE"}
FRONT = {"forearms", "grip", "quads", "core", "legs", "innerthigh", "shoulders"}
CENT_KEY = {"legs": "quads"}
CYCLE = {"clean": 3.3, "dead": 2.7, "squat": 2.7}
KEYS = {"clean": Lf.CLEAN, "dead": Lf.DEADLIFT, "squat": Lf.SQUAT}
GROUND_Y = 1800
FIG_Y = GROUND_Y - int(Lf.GROUND * Z)
FIG_X = int(W / 2 - 540 * Z)

@lru_cache(1)
def background():
    im = Image.new("RGBA", (W, H), BGC + (255,)); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(15, 16, 20, 255))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(15, 16, 20, 255))
    return im

@lru_cache(16)
def headline(markup, size=88):
    f = F("bold", size); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    words = []; col = TXT
    for tok in markup.replace("{", " { ").replace("}", " } ").split():
        if tok == "{": col = LIME
        elif tok == "}": col = TXT
        elif tok in (",", ".", "?") and words: words[-1] = (words[-1][0] + tok, words[-1][1])
        else: words.append((tok, col))
    lines, cur = [], []
    for w, c in words:
        if cur and d0.textlength(" ".join(x for x, _ in cur + [(w, c)]), font=f) > 920: lines.append(cur); cur = []
        cur.append((w, c))
    if cur: lines.append(cur)
    if len(lines) > 1 and size > 70 and len(words) <= 4: return headline(markup, size - 6)
    lh = int(size * 1.1); im = Image.new("RGBA", (W, lh * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sp = d0.textlength(" ", font=f)
    for li, ln in enumerate(lines):
        x = 80
        for w, c in ln:
            d.text((x, li * lh), w, font=f, fill=c + (255,)); x += d0.textlength(w, font=f) + sp
    return im

def kicker(d, text, a=1.0):
    x = 82; f = M(30)
    for ch in text:
        d.text((x, 330), ch, font=f, fill=tuple(int(c * a) for c in (150, 156, 168)))
        x += d.textlength(ch, font=f) + 3

@lru_cache(8)
def mini(which):
    pose = {"p": (Lf.CLEAN, 0.56), "d": (Lf.DEADLIFT, 0.5), "s": (Lf.SQUAT, 0.5)}[which]
    J = Lf.solve(Lf.interp(pose[0], pose[1]), 540)
    hl = {"p": {"shoulders": 1, "triceps": 1, "traps": 1}, "d": {"hamstrings": 1, "glutes": 1, "lowerback": 1},
          "s": {"quads": 1, "glutes": 1}}[which]
    lay, _ = Lf.draw_figure(J, hl)
    bg = Image.new("RGBA", lay.size, (0, 0, 0, 0)); bd_ = ImageDraw.Draw(bg); g = int(Lf.GROUND * Z); bd_.line([(int(330 * Z), g), (int(750 * Z), g)], fill=(120, 126, 138, 255), width=2); bg.alpha_composite(lay)
    return bg.crop((int(200 * Z), 0, int(880 * Z), int(Lf.FH * Z)))

def place_fig(cv, lay):
    bgf = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(bgf)
    dd.line([(80, GROUND_Y), (W - 80, GROUND_Y)], fill=(120, 126, 138, 255), width=2)
    for i in range(-8, 9): dd.line([(W / 2 + i * 70, GROUND_Y), (W / 2 + i * 105, GROUND_Y + 80)], fill=(36, 40, 48, 255), width=1)
    for j, y in enumerate((GROUND_Y + 24, GROUND_Y + 54)): dd.line([(80 - j * 40, y), (W - 80 + j * 40, y)], fill=(30, 33, 40, 255), width=1)
    cv.alpha_composite(bgf)
    cv.alpha_composite(lay, (FIG_X, FIG_Y))

def labels(d, on, cents):
    for side in (0, 1):
        items = []
        for k, v in on:
            if (k in FRONT) != bool(side): continue
            c = cents.get(CENT_KEY.get(k, k))
            if c is None: continue
            cx, cy = FIG_X + c[0], FIG_Y + c[1]
            items.append([k, v, cx, cy, cy])
        items.sort(key=lambda it: it[3])
        for n in range(1, len(items)):
            items[n][4] = max(items[n][4], items[n - 1][4] + 46)
        for k, v, cx, cy, ly in items:
            name = NAMES[k]; f = M(32); tw = d.textlength(name, font=f)
            col = tuple(int(LIME[i] * v + BGC[i] * (1 - v)) for i in range(3))
            if side: tx = min(W - 60 - tw, max(cx + 150, 640)); lx = tx - 12
            else: tx = max(60, min(cx - 150 - tw, 440 - tw)); lx = tx + tw + 12
            d.line([(lx, ly + 16), (cx, cy)], fill=col, width=2)
            d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=col)
            d.text((tx, ly), name, font=f, fill=col)

def label(cv, d, key, cent, slot, a):
    if cent is None or a <= 0.01: return
    name = NAMES[key]; f = M(32)
    tw = d.textlength(name, font=f)
    front = key in FRONT
    ty = 760 + slot * 66
    if front: tx = W - 70 - tw; lx = tx - 14
    else: tx = 70; lx = tx + tw + 14
    cx, cy = cent[0], cent[1] + FIG_Y
    col = tuple(int(LIME[i] * a + BGC[i] * (1 - a)) for i in range(3))
    mid = (lx + (24 if not front else -24), ty + 16)
    d.line([(lx, ty + 16), mid, (cx, cy)], fill=col, width=2)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=col)
    d.text((tx, ty), name, font=f, fill=col)

def frame(t):
    i = max(j for j, s in enumerate(SC) if s[0] <= t); s0, kick, head, mode, counter = SC[i]
    cv = background().copy(); d = ImageDraw.Draw(cv)
    d.rounded_rectangle((80, 214, W - 80, 222), 4, fill=(40, 43, 50))
    d.rounded_rectangle((80, 214, 80 + (W - 160) * clamp(t / TOTAL), 222), 4, fill=LIME)
    if counter: d.text((W - 82, 334), counter, font=M(30), fill=(150, 156, 168), anchor="ra")
    a = clamp((t - s0) / 0.25) if s0 > 0 else 1.0
    kicker(d, kick, a)
    him = headline(head)
    if a < 1:
        him = him.copy(); al = him.getchannel("A").point(lambda v: int(v * a)); him.putalpha(al)
    cv.alpha_composite(him, (0, int(380 + (1 - ease(a)) * 30)))
    if mode == "intro":
        for k, (w, x, tin) in enumerate((("p", 200, 1.4), ("d", 540, 1.95), ("s", 880, 2.5))):
            p = back((t - tin) / 0.4)
            if p <= 0.02: continue
            im = mini(w); s = 0.6 * p / Z
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
            cv.alpha_composite(im, (int(x - im.width / 2), int(1700 - im.height + 40 * s)))
            d.text((x, 1760), f"0{k+1}", font=M(44), fill=LIME, anchor="mm")
    elif mode == "sweep":
        J = Lf.solve(Lf.interp(Lf.STAND, 0), 540)
        order = ["calves", "hamstrings", "quads", "innerthigh", "glutes", "core", "lowerback", "lats", "upperback", "chest",
                 "traps", "shoulders", "triceps", "biceps", "forearms"]
        hl = {k: clamp((t - s0 - 0.2 - n * 0.17) / 0.3) for n, k in enumerate(order)}
        hl["grip"] = clamp((t - s0 - 2.8) / 0.3)
        lay, _ = Lf.draw_figure(J, hl, show_bar=False)
        place_fig(cv, lay)
    elif mode in KEYS:
        u = ((t - s0) / CYCLE[mode]) % 1.0
        J = Lf.solve(Lf.interp(KEYS[mode], u), 540)
        hl = {}; on = []
        for k, ton in HL[mode]:
            v = clamp((t - ton) / 0.25)
            if v > 0: hl[k] = max(hl.get(k, 0), v); on.append((k, v))
        lay, cents = Lf.draw_figure(J, hl)
        place_fig(cv, lay)
        labels(ImageDraw.Draw(cv), on, cents)
    elif mode == "cta":
        for k, (w, x) in enumerate((("p", 200), ("d", 540), ("s", 880))):
            im = mini(w); s = 0.42 / Z
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            al = im.getchannel("A").point(lambda v: int(v * 0.5)); im.putalpha(al)
            cv.alpha_composite(im, (int(x - im.width / 2), int(1180 - im.height)))
        put(cv, "follow", W / 2, 1450, back((t - s0 - 0.2) / 0.4))
    return cv.convert("RGB")

def main():
    b2.build_sprites()
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(float(s)).save(f"st_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
