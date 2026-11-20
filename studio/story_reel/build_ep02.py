"""FitEats EP01 - Protein for desk workers. 30s 1080x1920 kinetic-typography reel."""
import math, os, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- palette & fonts ----------
BG = (11, 11, 12)
CARD = (24, 24, 27)
BORDER = (48, 48, 54)
TXT = (242, 242, 240)
MUTED = (110, 110, 118)
ACC = (184, 240, 64)
DARK = (11, 11, 12)

FD = "/usr/share/fonts/opentype/inter/"
GF = "/usr/share/fonts/truetype/google-fonts/ofl/"
_fc = {}
def font(kind, size):
    key = (kind, size)
    if key not in _fc:
        path = {
            "sans": FD + "InterDisplay-Medium.otf",
            "bold": FD + "InterDisplay-Bold.otf",
            "serif": GF + "crimsontext/CrimsonText-Italic.ttf",
            "mono": GF + "anonymouspro/AnonymousPro-Bold.ttf",
        }[kind]
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]

# ---------- script ----------
# token syntax: *word = serif italic accent, ^word = highlight box, ~word = spoken only (not shown)
# word|spoken_text overrides spoken length for timing
SCENES = [
    ("lunch",  "You eat *less at lunch, hoping to lose weight."),
    ("crash",  "By ^4pm,|four_pee_em your energy *crashes."),
    ("snacks", "So you grab chips, a sugary chai, maybe a cold drink."),
    ("math",   "That's over ^400|four_hundred calories. Your lunch savings? *Gone."),
    ("plate",  "The problem isn't willpower. It's your *plate."),
    ("checks", "A ^low-calorie, high-protein meal keeps you full for hours, with steady energy and no 4pm|four_pee_em craving."),
    ("steady", "Eat *smarter. Not less."),
    ("outro",  "Want meals built this way? Follow ^FitEats."),
]
TOTAL = 30.0
NARR_END = 28.7

def parse():
    words = []
    for si, (prop, text) in enumerate(SCENES):
        for tok in text.split(" "):
            style = "n"
            if tok[0] in "*^~":
                style = {"*": "s", "^": "h", "~": "x"}[tok[0]]
                tok = tok[1:]
            disp, spoken = (tok.split("|") + [None])[:2]
            spoken = (spoken or disp).replace("_", " ")
            words.append(dict(scene=si, text=disp, style=style, spoken=spoken))
    # raw durations
    t = 0.35
    for i, w in enumerate(words):
        letters = sum(c.isalnum() for c in w["spoken"])
        nsyl_ish = max(1, len(w["spoken"].split()))
        d = 0.09 + 0.052 * letters + 0.03 * (nsyl_ish - 1)
        w["start"], w["dur"] = t, d
        t += d
        last = w["text"][-1]
        if last == ",": t += 0.12
        elif last in ".?": t += 0.34
        if i + 1 < len(words) and words[i + 1]["scene"] != w["scene"]:
            t += 0.12
    # scale to fit
    k = (NARR_END - 0.35) / (t - 0.35 - 0.34)
    for w in words:
        w["start"] = 0.35 + (w["start"] - 0.35) * k
        w["dur"] *= k
        w["end"] = w["start"] + w["dur"]
    return words

WORDS = parse()

# ---- override with real voiceover word timings when available ----
_TJ = os.path.join(OUT, "dl", "words.json")
if os.path.exists(_TJ):
    TOTAL = 29.4
    tw = []
    for w in json.load(open(_TJ))["words"]:
        if w["type"] != "word": continue
        if "—" in w["text"]:
            a_, b_ = w["text"].split("—"); mid = w["start"] + (w["end"] - w["start"]) * len(a_) / (len(a_) + len(b_))
            tw += [dict(text=a_, start=w["start"], end=mid), dict(text=b_, start=mid + 0.05, end=w["end"])]
        else:
            tw.append(w)
    span = {"4pm,": 2, "400": 2, "4pm": 2}
    k = 0
    for w in WORDS:
        n = span.get(w["text"], 1)
        grp = tw[k:k + n]; k += n
        w["start"], w["end"] = grp[0]["start"], grp[-1]["end"]
        w["dur"] = w["end"] - w["start"]
    assert k == len(tw), (k, len(tw))
def scene_bounds():
    b = []
    for si in range(len(SCENES)):
        ws = [w for w in WORDS if w["scene"] == si]
        b.append(0.0 if si == 0 else ws[0]["start"] - 0.18)
    b.append(TOTAL)
    return b
BOUNDS = scene_bounds()

def wt(si, text_prefix):
    """start time of first word in scene si whose text starts with prefix"""
    for w in WORDS:
        if w["scene"] == si and w["text"].lower().startswith(text_prefix.lower()):
            return w["start"]
    raise KeyError(text_prefix)

# ---------- easing helpers ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, t0, dur): return ease((t - t0) / dur)
def mix(c1, c2, a): return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

# ---------- drawing primitives ----------
def text_w(f, s):
    return f.getlength(s)

def rrect(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def dashed_rrect(d, box, color, dash=14, gap=10, width=3):
    x0, y0, x1, y1 = box
    for (ax, ay, bx, by) in [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]:
        L = math.hypot(bx - ax, by - ay); n = int(L // (dash + gap)) + 1
        for i in range(n):
            s = i * (dash + gap); e = min(L, s + dash)
            if s >= L: break
            d.line([(ax + (bx - ax) * s / L, ay + (by - ay) * s / L), (ax + (bx - ax) * e / L, ay + (by - ay) * e / L)], fill=color, width=width)

def mono_label(d, xy, s, color=MUTED, size=30, anchor="la"):
    d.text(xy, s, font=font("mono", size), fill=color, anchor=anchor)

def tag(d, cx, cy, s, a=1.0, size=34, fill=ACC, fg=DARK, pad=(18, 10), anchor_center=True):
    f = font("mono", size)
    tw = text_w(f, s)
    x0 = cx - tw / 2 - pad[0] if anchor_center else cx
    box = (x0, cy - size / 2 - pad[1], x0 + tw + 2 * pad[0], cy + size / 2 + pad[1])
    rrect(d, box, 6, fill=mix(BG, fill, a))
    d.text(((box[0] + box[2]) / 2, cy + 1), s, font=f, fill=mix(BG, fg, a) if fg != DARK else DARK, anchor="mm")
    return box

def aa_ellipse_img(size, ring_w, frac, ring_color, track_color, fill=None):
    """supersampled ring with progress arc, returns RGBA image"""
    S = 4; n = size * S
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if fill: d.ellipse((0, 0, n - 1, n - 1), fill=fill)
    d.ellipse((ring_w * S / 2, ring_w * S / 2, n - ring_w * S / 2, n - ring_w * S / 2), outline=track_color, width=ring_w * S)
    if frac > 0:
        d.arc((ring_w * S / 2, ring_w * S / 2, n - ring_w * S / 2, n - ring_w * S / 2), -90, -90 + 360 * frac, fill=ring_color, width=ring_w * S)
    return im.resize((size, size), Image.LANCZOS)

def aa_circle_img(size, color, outline=None, ow=0):
    S = 4; n = size * S
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, n - 1, n - 1), fill=color, outline=outline, width=ow * S)
    return im.resize((size, size), Image.LANCZOS)

def paste_a(base, im, xy, a=1.0):
    if a < 1:
        im = im.copy(); al = im.split()[3].point(lambda v: int(v * a)); im.putalpha(al)
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))

# ---------- kinetic caption ----------
CAP_Y = 560      # top of caption block
CAP_W = 940
SANS_SZ, SERIF_SZ = 66, 84
LINE_H = 96

def word_font(w):
    return font("serif", SERIF_SZ) if w["style"] == "s" else font("bold" if w["style"] == "h" else "sans", SANS_SZ)

def layout_caption(si):
    ws = [w for w in WORDS if w["scene"] == si and w["style"] != "x"]
    space = text_w(font("sans", SANS_SZ), " ")
    lines, cur, cw = [], [], 0
    for w in ws:
        ww = text_w(word_font(w), w["text"]) + (24 if w["style"] == "h" else 0)
        if cur and cw + space + ww > CAP_W:
            lines.append((cur, cw)); cur, cw = [], 0
        cur.append((w, ww)); cw += (space if len(cur) > 1 else 0) + ww
    if cur: lines.append((cur, cw))
    placed = []
    n = len(lines)
    y0 = CAP_Y + (2 - n) * LINE_H / 2 if n < 3 else CAP_Y - (n - 2) * LINE_H / 2
    for li, (ln, lw) in enumerate(lines):
        x = (W - lw) / 2; y = y0 + li * LINE_H
        for w, ww in ln:
            placed.append((w, x, y, ww)); x += ww + space
    return placed

LAYOUT = {si: layout_caption(si) for si in range(len(SCENES))}

def draw_caption(img, d, si, t):
    for w, x, y, ww in LAYOUT[si]:
        p = prog(t, w["start"] - 0.04, 0.2)
        if p <= 0: continue
        dy = (1 - p) * 22
        base = y + LINE_H / 2 + dy
        if w["style"] == "h":
            hp = prog(t, w["start"], 0.22)
            rrect(d, (x, base - 46, x + ww * hp, base + 40), 6, fill=mix(BG, ACC, p))
            d.text((x + 12, base), w["text"], font=word_font(w), fill=mix(BG, DARK if hp > 0.5 else TXT, p), anchor="lm")
        elif w["style"] == "s":
            d.text((x, base + 4), w["text"], font=word_font(w), fill=mix(BG, ACC, p), anchor="lm")
        else:
            d.text((x, base), w["text"], font=word_font(w), fill=mix(BG, TXT, p), anchor="lm")

# ---------- props (y range ~ 820..1420) ----------
PY = 860

def prop_clock(img, d, si, t):
    t_in = BOUNDS[si] + 0.1; t9 = wt(si, "nine")
    a = prog(t, t_in, 0.3)
    box = (80, PY, W - 80, PY + 470)
    rrect(d, box, 22, fill=mix(BG, CARD, a), outline=mix(BG, BORDER, a), width=3)
    mono_label(d, (120, PY + 50), "HOURS SITTING · TODAY", mix(BG, MUTED, a), 30)
    n = 9; bw, gap = 80, 14; x0 = (W - (n * bw + (n - 1) * gap)) / 2
    fill_p = clamp((t - (t_in + 0.2)) / (t9 + 0.55 - t_in - 0.2))
    filled = fill_p * n
    hours = ["9", "10", "11", "12", "1", "2", "3", "4", "5"]
    for i in range(n):
        x = x0 + i * (bw + gap); y = PY + 170
        f = clamp(filled - i)
        rrect(d, (x, y, x + bw, y + 150), 10, fill=mix(BG, (36, 36, 40), a), outline=mix(BG, BORDER, a), width=2)
        if f > 0:
            hh = 150 * f
            rrect(d, (x, y + 150 - hh, x + bw, y + 150), 10, fill=ACC)
        mono_label(d, (x + bw / 2, y + 190), hours[i], mix(BG, MUTED, a), 28, "mm")
    cnt = int(round(filled))
    d.text((W - 120, PY + 62), f"{cnt}H", font=font("mono", 64), fill=mix(BG, ACC if cnt == 9 else TXT, a), anchor="rm")
    mono_label(d, (W / 2, PY + 420), "9AM ───────────── 6PM", mix(BG, MUTED, a), 28, "mm")

def prop_muscle(img, d, si, t):
    t_in = BOUNDS[si] + 0.05; tq = wt(si, "quietly")
    a = prog(t, t_in, 0.25)
    box = (80, PY, W - 80, PY + 470)
    rrect(d, box, 22, fill=mix(BG, CARD, a), outline=mix(BG, BORDER, a), width=3)
    mono_label(d, (120, PY + 50), "MUSCLE MASS", mix(BG, MUTED, a), 30)
    bx0, bx1, by = 130, W - 130, PY + 190
    full = bx1 - bx0
    shrink = prog(t, tq, BOUNDS[si + 1] - tq - 0.1)
    cur = full * (1 - 0.30 * shrink)
    dashed_rrect(d, (bx0, by, bx1, by + 120), mix(BG, MUTED, a), width=3)
    rrect(d, (bx0, by, bx0 + cur, by + 120), 14, fill=mix(BG, mix(ACC, (200, 90, 70), shrink), a))
    pct = 100 - int(30 * shrink)
    d.text((W - 120, PY + 62), f"{pct}%", font=font("mono", 64), fill=mix(BG, TXT, a), anchor="rm")
    mono_label(d, (bx0, by + 170), "WHERE YOU WERE", mix(BG, MUTED, a), 26)
    mono_label(d, (bx1, by + 170), "WHERE SITTING TAKES YOU", mix(BG, MUTED, a * shrink), 26, "ra")

def prop_chart(img, d, si, t):
    t_in = BOUNDS[si] + 0.05
    a = prog(t, t_in, 0.25)
    box = (80, PY, W - 80, PY + 520)
    rrect(d, box, 22, fill=mix(BG, CARD, a), outline=mix(BG, BORDER, a), width=3)
    mono_label(d, (120, PY + 50), "MUSCLE BY AGE · INACTIVE", mix(BG, MUTED, a), 30)
    ages = ["30", "40", "50", "60"]; vals = [1.0, 0.92, 0.85, 0.78]
    base = PY + 430; maxh = 280; bw = 150; gap = 50
    x0 = (W - (4 * bw + 3 * gap)) / 2
    t8 = wt(si, "8%")
    for i in range(4):
        p = prog(t, t_in + 0.25 + i * 0.35, 0.45)
        h = maxh * vals[i] * p
        x = x0 + i * (bw + gap)
        col = ACC if i == 0 else mix(ACC, (90, 90, 96), min(1, i / 3 + 0.2))
        if h > 2: rrect(d, (x, base - h, x + bw, base), 10, fill=col)
        mono_label(d, (x + bw / 2, base + 36), ages[i], mix(BG, MUTED, a), 30, "mm")
    tp = prog(t, t8, 0.25)
    if tp > 0:
        tag(d, W - 250, PY + 62, "-8% / DECADE", tp, 30)

def prop_cards(img, d, si, t):
    rows = [("METABOLISM", "↓ SLOWER", wt(si, "slower")), ("BELLY FAT", "↑ MORE", wt(si, "belly")), ("ENERGY AT 3PM", "↓ CRASH", wt(si, "3pm"))]
    for i, (lab, val, ts) in enumerate(rows):
        p = prog(t, ts - 0.05, 0.3)
        if p <= 0:
            dashed_rrect(d, (80, PY + i * 160, W - 80, PY + i * 160 + 130), (40, 40, 44), width=3)
            continue
        y = PY + i * 160 + (1 - p) * 30
        rrect(d, (80, y, W - 80, y + 130), 18, fill=mix(BG, CARD, p), outline=mix(BG, BORDER, p), width=3)
        mono_label(d, (125, y + 65), lab, mix(BG, TXT, p), 38, "lm")
        d.text((W - 125, y + 65), val, font=font("bold", 44), fill=mix(BG, ACC if i != 1 else (240, 120, 90), p), anchor="rm")

def prop_big(img, d, si, t):
    tp = wt(si, "protein")
    p = prog(t, tp - 0.05, 0.35)
    if p <= 0: return
    f = font("serif", int(230 * (0.88 + 0.12 * p)))
    d.text((W / 2, PY + 260), "Protein.", font=f, fill=mix(BG, ACC, p), anchor="mm")
    lp = prog(t, tp + 0.25, 0.4)
    if lp > 0:
        w = 520 * lp
        d.line([(W / 2 - w / 2, PY + 430), (W / 2 + w / 2, PY + 430)], fill=ACC, width=6)

def prop_checks(img, d, si, t):
    rows = [("STAYS FULL LONGER", wt(si, "full")), ("PROTECTS MUSCLE", wt(si, "protects")), ("BURNS MORE TO DIGEST", wt(si, "burns"))]
    a = prog(t, BOUNDS[si] + 0.05, 0.25)
    for i, (lab, ts) in enumerate(rows):
        y = PY + i * 160
        p = prog(t, ts, 0.3)
        if p > 0:
            rrect(d, (80, y, W - 80, y + 130), 18, fill=mix(BG, CARD, p), outline=mix(ACC, BORDER, 1 - p * 0.0) if False else mix(BG, ACC, p), width=3)
        else:
            dashed_rrect(d, (80, y, W - 80, y + 130), mix(BG, (60, 60, 66), a), width=3)
        # check circle
        cs = 74
        if p > 0:
            ci = aa_circle_img(cs, ACC + (255,))
            paste_a(img, ci, (120, y + 65 - cs / 2), p)
            d.line([(120 + 20, y + 66), (120 + 33, y + 80), (120 + 56, y + 50)], fill=DARK, width=8, joint="curve")
        else:
            ci = aa_circle_img(cs, (0, 0, 0, 0), mix(BG, (70, 70, 76), a) + (255,), 3)
            paste_a(img, ci, (120, y + 65 - cs / 2), 1)
        mono_label(d, (230, y + 65), lab, mix(BG, TXT if p > 0 else (80, 80, 86), max(p, a * 0.9)), 38, "lm")

def prop_plates(img, d, si, t):
    t20 = wt(si, "20"); a = prog(t, BOUNDS[si] + 0.05, 0.25)
    meals = ["BREAKFAST", "LUNCH", "DINNER"]
    size = 270; gap = 50; x0 = (W - (3 * size + 2 * gap)) / 2; y = PY + 40
    for i, m in enumerate(meals):
        p = prog(t, t20 + i * 0.28, 0.7)
        ring = aa_ellipse_img(size, 16, 0.83 * p, ACC + (255,), mix(BG, (44, 44, 50), a) + (255,), fill=mix(BG, CARD, a) + (255,))
        x = x0 + i * (size + gap)
        paste_a(img, ring, (x, y), 1)
        g = int(round(25 * p))
        d.text((x + size / 2, y + size / 2 - 6), f"{g}g", font=font("bold", 72), fill=mix(BG, TXT, a), anchor="mm")
        mono_label(d, (x + size / 2, y + size / 2 + 50), "PROTEIN", mix(BG, MUTED, a), 24, "mm")
        mono_label(d, (x + size / 2, y + size + 50), m, mix(BG, TXT, a), 30, "mm")
    te = wt(si, "every"); tp = prog(t, te, 0.25)
    if tp > 0: tag(d, W / 2, y + size + 150, "20–30G · EVERY MEAL", tp, 32)

def prop_outro(img, d, si, t):
    tf = wt(si, "follow"); p = prog(t, tf - 0.1, 0.4)
    a0 = prog(t, BOUNDS[si] + 0.05, 0.3)
    # plate icon line
    if p <= 0:
        mono_label(d, (W / 2, PY + 200), "DESK BODY · EP 02", mix(BG, MUTED, a0), 32, "mm")
        return
    fb = font("bold", 150)
    tw = text_w(fb, "FitEats")
    y = PY + 210 + (1 - p) * 30
    d.text((W / 2 - 18, y), "FitEats", font=fb, fill=mix(BG, TXT, p), anchor="mm")
    dot = aa_circle_img(34, ACC + (255,))
    paste_a(img, dot, (W / 2 + tw / 2 - 6, y + 22), p)
    mono_label(d, (W / 2, y + 120), "HIGH-PROTEIN DIET MEALS", mix(BG, MUTED, p), 32, "mm")
    tp = prog(t, tf + 0.5, 0.3)
    if tp > 0: tag(d, W / 2, y + 230, "FOLLOW FOR EP 03", tp, 34)


CORAL = (240, 120, 90)

def card(d, box, a, outline=None):
    rrect(d, box, 22, fill=mix(BG, CARD, a), outline=mix(BG, outline or BORDER, a), width=3)

def prop_lunch(img, d, si, t):
    a = prog(t, BOUNDS[si] + 0.05, 0.3)
    card(d, (80, PY, W - 80, PY + 470), a)
    mono_label(d, (120, PY + 50), "LUNCH · CALORIES", mix(BG, MUTED, a), 30)
    tl = wt(si, "less"); p = prog(t, tl, 1.6)
    kcal = int(round(650 - 300 * p))
    size = 260
    ring = aa_ellipse_img(size, 18, 0.95 * (1 - 0.46 * p), ACC + (255,), mix(BG, (44, 44, 50), a) + (255,), fill=mix(BG, CARD, a) + (255,))
    paste_a(img, ring, (140, PY + 140), 1)
    d.text((140 + size / 2, PY + 140 + size / 2 - 8), f"{kcal}", font=font("bold", 76), fill=mix(BG, TXT, a), anchor="mm")
    mono_label(d, (140 + size / 2, PY + 140 + size / 2 + 48), "KCAL", mix(BG, MUTED, a), 26, "mm")
    tw_ = wt(si, "lose"); tp = prog(t, tw_, 0.3)
    mono_label(d, (480, PY + 200), "BEFORE   650", mix(BG, MUTED, a), 34, "lm")
    mono_label(d, (480, PY + 260), "TODAY    350", mix(BG, TXT, a * p), 34, "lm")
    if tp > 0: tag(d, 480, PY + 340, "-300 KCAL", tp, 34, anchor_center=False)

def energy_curve(kind, n=160):
    xs = np.linspace(0, 1, n)
    if kind == "crash":
        ys = 0.72 + 0.06 * np.sin(xs * 6) - 0.62 / (1 + np.exp(-(xs - 0.78) * 40)) + 0.25 / (1 + np.exp(-(xs - 0.9) * 40))
    else:
        ys = 0.66 + 0.05 * np.sin(xs * 5.0)
    return xs, ys

def draw_energy(img, d, si, t, kind):
    a = prog(t, BOUNDS[si] + 0.05, 0.3)
    card(d, (80, PY, W - 80, PY + 500), a)
    mono_label(d, (120, PY + 50), "ENERGY · YOUR DAY" if kind == "crash" else "ENERGY · WITH PROTEIN", mix(BG, MUTED, a), 30)
    gx0, gx1, gy0, gy1 = 130, W - 130, PY + 120, PY + 400
    for i, lab in enumerate(["9AM", "12PM", "3PM", "6PM"]):
        x = gx0 + (gx1 - gx0) * i / 3
        d.line([(x, gy0), (x, gy1)], fill=mix(BG, (34, 34, 38), a), width=2)
        mono_label(d, (x, gy1 + 40), lab, mix(BG, MUTED, a), 26, "mm")
    xs, ys = energy_curve(kind)
    t0 = BOUNDS[si] + 0.2
    reveal = prog(t, t0, (BOUNDS[si + 1] - t0) * 0.8)
    m = max(2, int(len(xs) * reveal))
    pts = [(gx0 + (gx1 - gx0) * x, gy1 - (gy1 - gy0) * y) for x, y in zip(xs[:m], ys[:m])]
    col = ACC if kind == "steady" else ACC
    if kind == "crash":
        # colour segments after the drop coral
        cut = int(len(xs) * 0.74)
        if len(pts) > 1: d.line(pts[:min(cut, m)], fill=ACC, width=7, joint="curve")
        if m > cut: d.line(pts[cut - 1:m], fill=CORAL, width=7, joint="curve")
        tc = wt(si, "crashes"); tp = prog(t, tc, 0.3)
        if tp > 0:
            x4 = gx0 + (gx1 - gx0) * 0.82; y4 = gy1 - (gy1 - gy0) * ys[int(len(xs) * 0.82)]
            dot = aa_circle_img(30, CORAL + (255,)); paste_a(img, dot, (x4 - 15, y4 - 15), tp)
            tag(d, W - 250, PY + 62, "4PM CRASH", tp, 30, fill=CORAL)
    else:
        if len(pts) > 1: d.line(pts, fill=col, width=7, joint="curve")
        ts_ = wt(si, "smarter"); tp = prog(t, ts_, 0.3)
        if tp > 0: tag(d, W - 230, PY + 62, "NO CRASH", tp, 30)

def prop_crash(img, d, si, t): draw_energy(img, d, si, t, "crash")
def prop_steady(img, d, si, t): draw_energy(img, d, si, t, "steady")

def prop_snacks(img, d, si, t):
    rows = [("CHIPS", "+150 KCAL", wt(si, "chips")), ("SUGARY CHAI", "+120 KCAL", wt(si, "sugary")), ("COLD DRINK", "+140 KCAL", wt(si, "cold"))]
    for i, (lab, val, ts) in enumerate(rows):
        p = prog(t, ts - 0.05, 0.3)
        if p <= 0:
            dashed_rrect(d, (80, PY + i * 160, W - 80, PY + i * 160 + 130), (40, 40, 44), width=3); continue
        y = PY + i * 160 + (1 - p) * 30
        rrect(d, (80, y, W - 80, y + 130), 18, fill=mix(BG, CARD, p), outline=mix(BG, BORDER, p), width=3)
        mono_label(d, (125, y + 65), lab, mix(BG, TXT, p), 38, "lm")
        d.text((W - 125, y + 65), val, font=font("bold", 44), fill=mix(BG, CORAL, p), anchor="rm")

def prop_math(img, d, si, t):
    a = prog(t, BOUNDS[si] + 0.05, 0.3)
    card(d, (80, PY, W - 80, PY + 470), a)
    t4 = wt(si, "400"); tg = wt(si, "gone")
    rows = [("SAVED AT LUNCH", "-300", ACC, BOUNDS[si] + 0.1), ("4PM SNACKS", "+410", CORAL, t4)]
    for i, (lab, val, col, ts) in enumerate(rows):
        p = prog(t, ts, 0.3)
        y = PY + 110 + i * 100
        mono_label(d, (125, y), lab, mix(BG, TXT, p), 36, "lm")
        d.text((W - 125, y), val, font=font("bold", 56), fill=mix(BG, col, p), anchor="rm")
    lp = prog(t, t4 + 0.4, 0.3)
    d.line([(125, PY + 300), (125 + (W - 250) * lp, PY + 300)], fill=mix(BG, BORDER, a), width=3)
    p = prog(t, tg - 0.05, 0.3)
    mono_label(d, (125, PY + 385), "NET", mix(BG, TXT, p), 40, "lm")
    if p > 0:
        f = font("bold", int(70 * (0.9 + 0.1 * p)))
        d.text((W - 125, PY + 385), "+110 KCAL", font=f, fill=mix(BG, CORAL, p), anchor="rm")

def prop_plate(img, d, si, t):
    tw_ = wt(si, "willpower"); tp_ = wt(si, "plate")
    p1 = prog(t, tw_, 0.3)
    if p1 > 0:
        y = PY + 20
        dashed_rrect(d, (80, y, W - 80, y + 170), mix(BG, (90, 90, 96), p1), width=3)
        d.text((W / 2, y + 85), "WILLPOWER", font=font("mono", 64), fill=mix(BG, MUTED, p1), anchor="mm")
        sp = prog(t, tw_ + 0.35, 0.35)
        if sp > 0:
            tw2 = text_w(font("mono", 64), "WILLPOWER")
            d.line([(W / 2 - tw2 / 2 - 20, y + 88), (W / 2 - tw2 / 2 - 20 + (tw2 + 40) * sp, y + 88)], fill=CORAL, width=8)
    p2 = prog(t, tp_ - 0.05, 0.35)
    if p2 > 0:
        y = PY + 240 + (1 - p2) * 30
        rrect(d, (80, y, W - 80, y + 220), 22, fill=mix(BG, ACC, p2))
        d.text((W / 2, y + 110), "Your plate.", font=font("serif", 120), fill=DARK, anchor="mm")

def prop_checks2(img, d, si, t):
    rows = [("FULL FOR HOURS", wt(si, "full")), ("STEADY ENERGY", wt(si, "steady")), ("NO 4PM CRAVING", wt(si, "craving"))]
    a = prog(t, BOUNDS[si] + 0.05, 0.25)
    for i, (lab, ts) in enumerate(rows):
        y = PY + 60 + i * 160
        p = prog(t, ts, 0.3)
        if p > 0:
            rrect(d, (80, y, W - 80, y + 130), 18, fill=mix(BG, CARD, p), outline=mix(BG, ACC, p), width=3)
            ci = aa_circle_img(74, ACC + (255,)); paste_a(img, ci, (120, y + 65 - 37), p)
            d.line([(140, y + 66), (153, y + 80), (176, y + 50)], fill=DARK, width=8, joint="curve")
        else:
            dashed_rrect(d, (80, y, W - 80, y + 130), mix(BG, (60, 60, 66), a), width=3)
            ci = aa_circle_img(74, (0, 0, 0, 0), mix(BG, (70, 70, 76), a) + (255,), 3); paste_a(img, ci, (120, y + 65 - 37), 1)
        mono_label(d, (230, y + 65), lab, mix(BG, TXT if p > 0 else (80, 80, 86), max(p, a * 0.9)), 38, "lm")

PROPS = dict(lunch=prop_lunch, crash=prop_crash, snacks=prop_snacks, math=prop_math, plate=prop_plate,
             checks=prop_checks2, steady=prop_steady, outro=prop_outro)

# ---------- persistent chrome ----------
def draw_chrome(img, d, t):
    tag(d, W / 2, 330, "DESK BODY · EP 02", 1.0, 32)
    # progress dots (episode-ish tracker of scenes)
    n = len(SCENES); r = 9; gap = 34; x0 = W / 2 - (n - 1) * gap / 2; y = 1560
    cur = max(i for i in range(n) if BOUNDS[i] <= t + 1e-6)
    for i in range(n):
        c = ACC if i <= cur else (60, 60, 66)
        d.ellipse((x0 + i * gap - r, y - r, x0 + i * gap + r, y + r), fill=c if i <= cur else None, outline=c, width=3)

def frame(t):
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    si = max(i for i in range(len(SCENES)) if BOUNDS[i] <= t + 1e-6)
    PROPS[SCENES[si][0]](img, d, si, t)
    draw_caption(img, d, si, t)
    # scene out-fade (except last)
    te = BOUNDS[si + 1]
    if si < len(SCENES) - 1 and t > te - 0.16:
        f = clamp((t - (te - 0.16)) / 0.16)
        img = Image.blend(img, Image.new("RGBA", (W, H), BG + (255,)), f * 0.9)
        d = ImageDraw.Draw(img)
    if si == len(SCENES) - 1 and t > TOTAL - 0.4:
        pass
    draw_chrome(img, d, t)
    return img.convert("RGB")

# ---------- render ----------
def render_scene(si):
    f0 = round(BOUNDS[si] * FPS); f1 = round(BOUNDS[si + 1] * FPS)
    tmp = os.path.join(OUT, f"scene_{si:02d}.tmp.mp4"); dst = os.path.join(OUT, f"scene_{si:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, dst)
    else: sys.exit(f"scene {si} failed")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    if mode == "timing":
        for si, (prop, _) in enumerate(SCENES):
            ws = [w for w in WORDS if w["scene"] == si]
            print(f"{BOUNDS[si]:5.2f}-{BOUNDS[si+1]:5.2f}  " + " ".join(f'{w["text"]}@{w["start"]:.2f}' for w in ws))
    elif mode == "stills":
        for t in sys.argv[2:]:
            frame(float(t)).save(os.path.join(OUT, f"still_{t}.png"))
    elif mode == "render":
        which = [int(x) for x in sys.argv[2:]] or range(len(SCENES))
        for si in which: render_scene(si)
        with open(os.path.join(OUT, "words.json"), "w") as fh: json.dump(WORDS, fh, indent=1)
