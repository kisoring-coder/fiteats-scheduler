"""FitEats - '1 Hour vs 23 Hours' text reel. Cream paper theme, no voiceover.
python3 build.py stills t1 t2 ...   |   python3 build.py render
"""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, TOTAL = 1080, 1920, 30, 20.0
BG = (243, 237, 226); INK = (26, 23, 20); RED = (214, 69, 45); GREEN = (40, 138, 84)
GREY = (214, 206, 193); MUTE = (138, 128, 116)
GF = "/usr/share/fonts/truetype/google-fonts/ofl/"
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def F(kind, size):
    k = (kind, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype({"anton": GF + "anton/Anton-Regular.ttf", "bold": FD + "InterDisplay-Bold.otf",
                                     "med": FD + "InterDisplay-Medium.otf"}[kind], size)
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, t0, d=0.3): return ease((t - t0) / d)
def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

# scenes: (start, end)
SC = [(0, 2), (2, 4.5), (4.5, 9), (9, 11.5), (11.5, 14), (14, 16.5), (16.5, 20.0)]
def scene_alpha(t, i):
    s, e = SC[i]
    if t < s or t >= e: return 0.0
    out = 1.0 if i == len(SC) - 1 else clamp((e - t) / 0.22)
    return out

def line(d, y, parts, size, a, t0, t, center=True, x0=110):
    """parts: list of (text, color). slides up + fades in from t0."""
    p = prog(t, t0, 0.32) * a
    if p <= 0: return
    f = F("anton", size)
    total = sum(d.textlength(tx, font=f) for tx, _ in parts)
    x = (W - total) / 2 if center else x0
    yy = y + (1 - prog(t, t0, 0.32)) * 40
    for tx, col in parts:
        d.text((x, yy), tx, font=f, fill=mix(BG, col, p), anchor="ls")
        x += d.textlength(tx, font=f)

def small(d, xy, txt, col, size, a, anchor="mm", kind="bold"):
    if a <= 0: return
    d.text(xy, txt, font=F(kind, size), fill=mix(BG, col, a), anchor=anchor)

# ---- 24-hour blocks ----
BW, BG_ = 66, 12
X0 = (W - (12 * BW + 11 * BG_)) / 2
ROWY = [1250, 1390]
RED_HOURS = {11: 4.5, 16: 6.0, 20: 7.5}
def blocks(img, d, t, a, appear_t0, gym_t, red_on=True, pulse=False):
    if a <= 0: return
    for h in range(24):
        r, c = divmod(h, 12)
        x = X0 + c * (BW + BG_); y = ROWY[r]
        pa = prog(t, appear_t0 + h * 0.025, 0.25) * a
        if pa <= 0: continue
        col = GREY
        if pulse and h != 6:
            k = 0.5 + 0.5 * math.sin((t - 2.0) * 6 - h * 0.35)
            col = mix(GREY, (190, 180, 165), k)
        if h == 6:
            col = mix(GREY, GREEN, prog(t, gym_t, 0.3))
        if red_on and h in RED_HOURS:
            col = mix(col, RED, prog(t, RED_HOURS[h] + 0.1, 0.3))
        yy = y + (1 - prog(t, appear_t0 + h * 0.025, 0.25)) * 20
        d.rounded_rectangle((x, yy, x + BW, yy + 96), 12, fill=mix(BG, col, pa))
    # hour labels
    for h, lab in [(0, "12 AM"), (6, "6 AM"), (12, "12 PM"), (18, "6 PM")]:
        r, c = divmod(h, 12)
        small(d, (X0 + c * (BW + BG_), ROWY[r] + 128), lab, MUTE, 26, prog(t, appear_t0 + 0.4, 0.4) * a, "ls", "med")
    gp = prog(t, gym_t + 0.15, 0.3) * a
    if gp > 0:
        x = X0 + 6 * (BW + BG_) + BW / 2
        small(d, (x, ROWY[0] - 34), "GYM", GREEN, 30, gp)
    if red_on:
        for h, lab in [(11, "11 AM"), (16, "4 PM"), (20, "8:47")]:
            p = prog(t, RED_HOURS[h] + 0.2, 0.3) * a
            r, c = divmod(h, 12)
            x = X0 + c * (BW + BG_) + BW / 2
            small(d, (x, ROWY[r] - 34), lab, RED, 28, p)

def plate(d, cx, cy, a, s=1.0):
    if a <= 0: return
    R = 120 * s
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=mix(BG, GREEN, a), width=10)
    d.ellipse((cx - R * 0.66, cy - R * 0.66, cx + R * 0.66, cy + R * 0.66), outline=mix(BG, GREEN, a), width=6)
    # fork & knife
    d.rounded_rectangle((cx - R - 70, cy - R * 0.9, cx - R - 56, cy + R * 0.9), 6, fill=mix(BG, GREEN, a))
    d.rounded_rectangle((cx + R + 56, cy - R * 0.9, cx + R + 70, cy + R * 0.9), 6, fill=mix(BG, GREEN, a))

def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # brand header (persistent)
    small(d, (W / 2, 250), "F I T E A T S", MUTE, 30, 1.0)
    d.line([(W / 2 - 40, 285), (W / 2 + 40, 285)], fill=RED, width=4)

    # S1
    a = scene_alpha(t, 0)
    line(d, 760, [("THE GYM IS", INK)], 150, a, 0.05, t)
    line(d, 930, [("1 HOUR.", GREEN)], 170, a, 0.45, t)
    blocks(img, d, t, a if t < 2 else 0, 0.3, 1.2, red_on=False)

    # S2
    a = scene_alpha(t, 1)
    line(d, 680, [("THE OTHER ", INK), ("23", RED)], 150, a, 2.05, t)
    line(d, 850, [("ARE THE REAL", INK)], 150, a, 2.35, t)
    line(d, 1020, [("WORKOUT.", INK)], 150, a, 2.65, t)
    if 2 <= t < 4.5: blocks(img, d, t, a, -5, -5, red_on=False, pulse=True)

    # S3 list
    a = scene_alpha(t, 2)
    if a > 0:
        for i, (tm, txt, t0) in enumerate([("11 AM.", "OFFICE SAMOSA.", 4.55), ("4 PM.", "CHAI + BISCUITS.", 6.05), ("8:47 PM.", "“JUST ORDER SOMETHING.”", 7.55)]):
            y = 600 + i * 235
            line(d, y - 100, [(tm, RED)], 64, a, t0, t)
            line(d, y + 40, [(txt, INK)], 104 if i < 2 else 88, a, t0 + 0.1, t)
        blocks(img, d, t, a, -5, -5, red_on=True)

    # S4
    a = scene_alpha(t, 3)
    line(d, 820, [("DISCIPLINE ISN'T", INK)], 140, a, 9.05, t)
    line(d, 990, [("LIFTING ", INK), ("HEAVIER.", RED)], 140, a, 9.45, t)

    # S5
    a = scene_alpha(t, 4)
    line(d, 700, [("IT'S WHAT'S ON", INK)], 140, a, 11.55, t)
    line(d, 860, [("YOUR PLATE", INK)], 140, a, 11.85, t)
    line(d, 1060, [("WHEN NOBODY'S", RED)], 130, a, 12.5, t)
    line(d, 1210, [("WATCHING.", RED)], 130, a, 12.8, t)
    if a > 0:
        u = prog(t, 13.2, 0.5) * a
        if u > 0:
            w = 560 * prog(t, 13.2, 0.5)
            d.line([(W / 2 - 280, 1240), (W / 2 - 280 + w, 1240)], fill=RED, width=10)

    # S6
    a = scene_alpha(t, 5)
    if a > 0:
        if t < 14.9:
            line(d, 1000, [("OR…", INK)], 260, a, 14.02, t)
        else:
            line(d, 680, [("LET SOMEONE", INK)], 140, a, 14.95, t)
            line(d, 850, [("PLAN THE PLATE", GREEN)], 140, a, 15.25, t)
            line(d, 1010, [("FOR YOU.", INK)], 140, a, 15.55, t)
            plate(d, W / 2, 1300, prog(t, 15.6, 0.4) * a)

    # S7 CTA + loop
    a = scene_alpha(t, 6)
    if a > 0:
        p = prog(t, 16.55, 0.4)
        fb = F("bold", 170)
        d.text((W / 2, 700), "FitEats", font=fb, fill=mix(BG, INK, p), anchor="mm")
        tw = d.textlength("FitEats", font=fb)
        d.ellipse((W / 2 + tw / 2 + 4, 730, W / 2 + tw / 2 + 40, 766), fill=mix(BG, GREEN, p))
        small(d, (W / 2, 840), "HIGH-PROTEIN MEALS  ·  CALORIES COUNTED", MUTE, 32, prog(t, 16.9, 0.4))
        small(d, (W / 2, 890), "DELIVERED IN CHENNAI", MUTE, 32, prog(t, 17.0, 0.4))
        tp = prog(t, 17.3, 0.35)
        if tp > 0:
            f = F("anton", 84); txt = "COMMENT “MENU”"
            tw = d.textlength(txt, font=f)
            s = 0.9 + 0.1 * tp
            bx0, bx1 = W / 2 - tw / 2 - 40, W / 2 + tw / 2 + 40
            d.rounded_rectangle((bx0, 990, bx1, 1110), 60, fill=mix(BG, RED, tp))
            d.text((W / 2, 1082), txt, font=f, fill=mix(RED, BG, tp), anchor="ms")
        # loop back: blocks rebuild with gym green
        blocks(img, d, t, 1.0, 18.3, 19.2, red_on=False)
    return img

def main():
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            frame(float(s)).save(f"still_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "video_tmp.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    import os; os.rename("video_tmp.mp4", "video_only.mp4")

if __name__ == "__main__":
    main()
