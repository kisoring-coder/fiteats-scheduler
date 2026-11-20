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
SCENES = [
    ("hook",    "Karthik knew ^everything about protein. And he still *gained four kilos."),
    ("notmeal", "It wasn't his breakfast. It wasn't his *lunch."),
    ("moment",  "It was one exact moment. ^8:47 PM."),
    ("morning", "Every morning, he was *perfect. Eggs. Paneer at lunch."),
    ("reel",    "He'd even watched ^this reel."),
    ("night",   "Then ^8:47 hits. Last call ends. Fridge is empty. Brain is *empty."),
    ("swiggy",  "And Swiggy is... *right there."),
    ("order",   "Two parottas. Extra salna. *Just this once."),
    ("week",    "^Four nights out of seven."),
    ("twist",   "Here's what ^nobody tells you."),
    ("gym",     "Diets don't fail at the *gym."),
    ("fail",    "They fail at ^8:47 PM, when you're too tired to *decide."),
    ("battery", "Willpower runs out by night. A plan ^doesn't."),
    ("stopped", "So Karthik *stopped deciding. Dinner was ^already planned."),
    ("box",     "High protein, calories counted, and at his door *before the hunger hit."),
    ("same",    "Same Karthik. *Different 8:47."),
    ("cta",     "Comment ^MENU, and we'll send you this week's plan."),
    ("outro",   "Because your 8:47 is *coming tonight."),
]
TOTAL = 55.0
NARR_END = 53.0
SPAN = {}

def parse():
    words = []
    for si, (prop, text) in enumerate(SCENES):
        for tok in text.split(" "):
            style = "n"
            if tok[0] in "*^~":
                style = {"*": "s", "^": "h", "~": "x"}[tok[0]]
                tok = tok[1:]
            words.append(dict(scene=si, text=tok, style=style, spoken=tok))
    t = 0.35
    for i, w in enumerate(words):
        d = 0.09 + 0.052 * sum(c.isalnum() for c in w["spoken"])
        w["start"], w["dur"] = t, d
        t += d
        if w["text"][-1] in ".?": t += 0.34
        elif w["text"][-1] == ",": t += 0.12
    k = (NARR_END - 0.35) / (t - 0.35)
    for w in words:
        w["start"] = 0.35 + (w["start"] - 0.35) * k; w["dur"] *= k; w["end"] = w["start"] + w["dur"]
    return words

WORDS = parse()

_TJ = os.path.join(OUT, "dl", "words.json")
if os.path.exists(_TJ):
    _j = json.load(open(_TJ))
    tw = [w for w in _j["words"] if w["type"] == "word"]
    k = 0
    for w in WORDS:
        n = SPAN.get(w["text"].strip(".,"), 1)
        grp = tw[k:k + n]; k += n
        w["start"], w["end"] = grp[0]["start"], grp[-1]["end"]
        w["dur"] = w["end"] - w["start"]
    assert k == len(tw), (k, len(tw))
    TOTAL = round(tw[-1]["end"] + 1.4, 2)

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

CORAL = (240, 120, 90)

def card(d, box, a, outline=None):
    rrect(d, box, 22, fill=mix(BG, CARD, a), outline=mix(BG, outline or BORDER, a), width=3)

_SPR = {}
def spr(name):
    if name not in _SPR:
        im = Image.open(os.path.join(OUT, "sprites", name + ".png")).convert("RGBA")
        _SPR[name] = im.crop(im.getbbox())
    return _SPR[name]

def put_sprite(img, name, cx, bottom, h, a=1.0):
    if a <= 0: return
    im = spr(name); w = int(im.width * h / im.height)
    im = im.resize((w, int(h)), Image.LANCZOS)
    paste_a(img, im, (cx - w / 2, bottom - h), a)

def wt_any(si, pref):
    try: return wt(si, pref)
    except KeyError: return BOUNDS[si] + 0.3


# ---------- props for 8:47 PM ----------
def a_in(si, t, dl=0.05, dur=0.3): return prog(t, BOUNDS[si] + dl, dur)

def big_clock(img, d, cy, txt, col, a, size=230, label=None, blink_t=None):
    box = (130, cy - 170, W - 130, cy + 170)
    rrect(d, box, 28, fill=mix(BG, CARD, a), outline=mix(BG, col, a), width=4)
    f = font("bold", size)
    hh, mm = txt.split(":")
    show_colon = True if blink_t is None else (int(blink_t * 2) % 2 == 0)
    tw_ = text_w(f, hh + ":" + mm)
    x = W / 2 - tw_ / 2 - 50
    d.text((x, cy + 6), hh, font=f, fill=mix(BG, col, a), anchor="lm")
    x2 = x + text_w(f, hh)
    d.text((x2, cy + 6), ":", font=f, fill=mix(BG, col, a if show_colon else a * 0.25), anchor="lm")
    x3 = x2 + text_w(f, ":")
    d.text((x3, cy + 6), mm, font=f, fill=mix(BG, col, a), anchor="lm")
    d.text((x3 + text_w(f, mm) + 24, cy + 50), "PM", font=font("mono", 70), fill=mix(BG, col, a), anchor="ls")
    if label: mono_label(d, (W / 2, cy - 130), label, mix(BG, MUTED, a), 28, "mm")

def phone(d, cx, top, w, h, a):
    rrect(d, (cx - w / 2, top, cx + w / 2, top + h), 46, fill=mix(BG, (20, 20, 23), a), outline=mix(BG, (90, 90, 98), a), width=5)
    rrect(d, (cx - 60, top + 18, cx + 60, top + 34), 8, fill=mix(BG, (60, 60, 66), a))

def rows(img, d, si, t, items, y0=880, h=130, gap=160, good=True):
    for i, (lab, val, ts, col) in enumerate(items):
        p = prog(t, ts - 0.05, 0.3)
        yy = y0 + i * gap
        if p <= 0:
            dashed_rrect(d, (80, yy, W - 80, yy + h), (44, 44, 50), width=3); continue
        y = yy + (1 - p) * 30
        rrect(d, (80, y, W - 80, y + h), 18, fill=mix(BG, CARD, p), outline=mix(BG, BORDER, p), width=3)
        mono_label(d, (125, y + h / 2), lab, mix(BG, TXT, p), 38, "lm")
        d.text((W - 125, y + h / 2), val, font=font("bold", 46), fill=mix(BG, col, p), anchor="rm")

def prop_hook(img, d, si, t):
    a = a_in(si, t, 0.0, 0.45)
    put_sprite(img, "karthik_before", W / 2 + (1 - a) * 120, 1500, 520, a)
    te = wt_any(si, "everything"); tg = wt_any(si, "gained")
    p1 = prog(t, te, 0.3); p2 = prog(t, tg, 0.3)
    if p2 > 0:
        tag(d, W / 2, 900, "+4 KG", p2, 48, fill=CORAL, pad=(26, 14))
    elif p1 > 0:
        tag(d, W / 2, 900, "PROTEIN KNOWLEDGE: 100%", p1, 34)

def prop_notmeal(img, d, si, t):
    rows(img, d, si, t, [("BREAKFAST", "FINE", wt_any(si, "breakfast"), ACC), ("LUNCH", "FINE", wt_any(si, "lunch"), ACC)], y0=940)
    mono_label(d, (W / 2, 1300), "SO WHAT WENT WRONG?", mix(BG, MUTED, prog(t, wt_any(si, "lunch") + 0.3, 0.3)), 32, "mm")

def prop_moment(img, d, si, t):
    a = a_in(si, t)
    t8 = wt_any(si, "8:47")
    p = prog(t, t8 - 0.05, 0.3)
    if p <= 0:
        rrect(d, (130, 1000, W - 130, 1340), 28, outline=mix(BG, BORDER, a), width=3)
        d.text((W / 2, 1176), "--:--", font=font("bold", 200), fill=mix(BG, (60, 60, 66), a), anchor="mm")
    else:
        s = 0.9 + 0.1 * p
        big_clock(img, d, 1170, "8:47", CORAL, p, int(230 * s), "THE MOMENT", blink_t=t)

def prop_morning(img, d, si, t):
    rows(img, d, si, t, [("8 AM · EGGS", "✓", wt_any(si, "eggs"), ACC), ("1 PM · PANEER", "✓", wt_any(si, "paneer"), ACC)], y0=940)
    tp = prog(t, wt_any(si, "perfect"), 0.3)
    if tp > 0: tag(d, W / 2, 870, "DAY MODE: PERFECT", tp, 32)

def prop_reel(img, d, si, t):
    a = a_in(si, t, 0.0, 0.35)
    cx, top, pw, ph = W / 2, 860 + (1 - a) * 40, 380, 640
    phone(d, cx, top, pw, ph, a)
    # mini reel inside
    mono_label(d, (cx, top + 90), "FITEATS · 8:47 PM", mix(BG, ACC, a), 20, "mm")
    d.text((cx, top + 190), "Karthik knew", font=font("sans", 34), fill=mix(BG, TXT, a), anchor="mm")
    d.text((cx, top + 236), "everything...", font=font("serif", 40), fill=mix(BG, ACC, a), anchor="mm")
    put_sprite(img, "karthik_before", cx, top + ph - 70, 300, a)
    # play progress bar
    pp = clamp((t - BOUNDS[si]) / max(0.1, BOUNDS[si + 1] - BOUNDS[si]))
    d.line([(cx - pw / 2 + 40, top + ph - 40), (cx + pw / 2 - 40, top + ph - 40)], fill=mix(BG, (60, 60, 66), a), width=6)
    d.line([(cx - pw / 2 + 40, top + ph - 40), (cx - pw / 2 + 40 + (pw - 80) * pp, top + ph - 40)], fill=ACC, width=6)
    tp = prog(t, wt_any(si, "this"), 0.3)
    if tp > 0: tag(d, cx + 300, top + 120, "YES, THIS ONE", tp, 26, fill=CORAL)

def small_clock(d, cx, cy, txt, col, a, size=96):
    f = font("bold", size)
    tw_ = text_w(f, txt) + text_w(font("mono", 40), " PM") + 60
    rrect(d, (cx - tw_ / 2, cy - size * 0.75, cx + tw_ / 2, cy + size * 0.75), 20, fill=mix(BG, CARD, a), outline=mix(BG, col, a), width=3)
    x = cx - tw_ / 2 + 30
    d.text((x, cy + 4), txt, font=f, fill=mix(BG, col, a), anchor="lm")
    d.text((x + text_w(f, txt) + 14, cy + 30), "PM", font=font("mono", 40), fill=mix(BG, col, a), anchor="ls")

def prop_night(img, d, si, t):
    a = prog(t, wt_any(si, "8:47") - 0.05, 0.3)
    if a > 0: small_clock(d, W / 2, 900, "8:47", CORAL, a)
    rows(img, d, si, t, [("LAST CALL", "ENDED", wt_any(si, "call"), MUTED), ("FRIDGE", "EMPTY", wt_any(si, "fridge"), CORAL), ("BRAIN", "EMPTY", wt_any(si, "brain"), CORAL)], y0=1030, h=120, gap=150)

def prop_swiggy(img, d, si, t):
    a = a_in(si, t, 0.0, 0.35)
    cx, top, pw, ph = W / 2, 860, 420, 640
    phone(d, cx, top, pw, ph, a)
    mono_label(d, (cx, top + 80), "FOOD DELIVERY", mix(BG, MUTED, a), 22, "mm")
    for i in range(3):
        y = top + 120 + i * 120
        p = prog(t, BOUNDS[si] + 0.1 + i * 0.15, 0.3)
        rrect(d, (cx - pw / 2 + 30, y, cx + pw / 2 - 30, y + 100), 14, fill=mix(BG, (36, 36, 40), p))
        rrect(d, (cx - pw / 2 + 45, y + 15, cx - pw / 2 + 115, y + 85), 10, fill=mix(BG, (90, 70, 50), p))
        rrect(d, (cx - pw / 2 + 135, y + 28, cx + 60, y + 44), 6, fill=mix(BG, (70, 70, 76), p))
        rrect(d, (cx - pw / 2 + 135, y + 58, cx + 10, y + 70), 6, fill=mix(BG, (55, 55, 60), p))
    tr = wt_any(si, "right")
    p = prog(t, tr - 0.1, 0.3)
    if p > 0:
        pulse = 1 + 0.04 * math.sin((t - tr) * 9)
        bw, bh = 300 * pulse, 90 * pulse; by = top + ph - 110
        rrect(d, (cx - bw / 2, by - bh / 2, cx + bw / 2, by + bh / 2), 45, fill=mix(BG, CORAL, p))
        d.text((cx, by), "ORDER NOW", font=font("bold", 40), fill=DARK, anchor="mm")

def prop_order(img, d, si, t):
    rows(img, d, si, t, [("2 x PAROTTA", "ADDED", wt_any(si, "parottas"), CORAL), ("EXTRA SALNA", "ADDED", wt_any(si, "salna"), CORAL)], y0=930)
    tp = prog(t, wt_any(si, "once"), 0.3)
    if tp > 0:
        d.text((W / 2, 1310), "“just this once”", font=font("serif", 76), fill=mix(BG, MUTED, tp), anchor="mm")

def prop_week(img, d, si, t):
    a = a_in(si, t)
    days = "MTWTFSS"; bad = [0, 1, 3, 5]
    bw, gap = 112, 16; x0 = (W - (7 * bw + 6 * gap)) / 2; y = 960
    tf = wt_any(si, "four")
    k = 0
    for i, ch in enumerate(days):
        x = x0 + i * (bw + gap)
        col = (36, 36, 40)
        if i in bad:
            p = prog(t, tf + 0.18 * k, 0.25); k += 1
            col = mix((36, 36, 40), CORAL, p)
        rrect(d, (x, y, x + bw, y + 150), 14, fill=mix(BG, col, a), outline=mix(BG, BORDER, a), width=2)
        mono_label(d, (x + bw / 2, y + 75), ch, mix(BG, DARK if i in bad and t > tf + 0.18 * bad.index(i) + 0.12 else TXT, a), 44, "mm")
    tp = prog(t, wt_any(si, "seven"), 0.3)
    if tp > 0: tag(d, W / 2, 1230, "4 / 7 NIGHTS · SAME MINUTE", tp, 32, fill=CORAL)

def prop_twist(img, d, si, t):
    p = prog(t, BOUNDS[si] + 0.1, (BOUNDS[si + 1] - BOUNDS[si]) * 0.85)
    w = 700 * p
    d.line([(W / 2 - w / 2, 960), (W / 2 + w / 2, 960)], fill=ACC, width=6)
    mono_label(d, (W / 2, 1040), "THE REAL REASON", mix(BG, MUTED, prog(t, BOUNDS[si] + 0.2, 0.4)), 32, "mm")

def dumbbell(d, cx, cy, s, col):
    rrect(d, (cx - 110 * s, cy - 12 * s, cx + 110 * s, cy + 12 * s), 6, fill=col)
    for sx in (-1, 1):
        rrect(d, (cx + sx * 110 * s - 28 * s, cy - 75 * s, cx + sx * 110 * s + 28 * s, cy + 75 * s), 10, fill=col)
        rrect(d, (cx + sx * 160 * s - 20 * s, cy - 50 * s, cx + sx * 160 * s + 20 * s, cy + 50 * s), 8, fill=col)

def prop_gym(img, d, si, t):
    a = a_in(si, t)
    card(d, (80, 900, W - 80, 1360), a)
    dumbbell(d, W / 2, 1090, 1.1, mix(BG, TXT, a))
    tp = prog(t, wt_any(si, "gym"), 0.3)
    if tp > 0: tag(d, W / 2, 1270, "NOT HERE", tp, 36)

def prop_fail(img, d, si, t):
    a = prog(t, wt_any(si, "8:47") - 0.05, 0.3)
    if a > 0: big_clock(img, d, 1110, "8:47", CORAL, a, 210, blink_t=t)
    tp = prog(t, wt_any(si, "decide"), 0.3)
    if tp > 0: tag(d, W / 2, 1360, "TOO TIRED TO DECIDE", tp, 34, fill=CORAL)

def battery(d, y, label, frac, col, a, right=""):
    mono_label(d, (110, y - 40), label, mix(BG, MUTED, a), 30, "lm")
    if right: mono_label(d, (W - 110, y - 40), right, mix(BG, col, a), 30, "rm")
    x0, x1 = 110, W - 150
    rrect(d, (x0, y, x1, y + 120), 18, outline=mix(BG, (90, 90, 98), a), width=4)
    rrect(d, (x1 + 6, y + 35, x1 + 30, y + 85), 6, fill=mix(BG, (90, 90, 98), a))
    if frac > 0.01: rrect(d, (x0 + 12, y + 12, x0 + 12 + (x1 - x0 - 24) * frac, y + 108), 12, fill=mix(BG, col, a))

def prop_battery(img, d, si, t):
    a = a_in(si, t)
    tw_ = wt_any(si, "willpower"); tn = wt_any(si, "night")
    dr = prog(t, tw_, max(0.6, tn - tw_ + 0.4))
    clock = int(9 + 12 * dr); ampm = "AM" if clock < 12 else "PM"; hh = clock if clock <= 12 else clock - 12
    battery(d, 960, "WILLPOWER", 1 - 0.88 * dr, mix(ACC, CORAL, dr), a, f"{hh}{ampm}")
    tp = prog(t, wt_any(si, "plan") - 0.05, 0.35)
    if tp > 0: battery(d, 1220, "A PLAN", 1.0, ACC, tp, "ALWAYS FULL")

def prop_stopped(img, d, si, t):
    a = a_in(si, t)
    days = "MTWTFSS"
    bw, gap = 112, 16; x0 = (W - (7 * bw + 6 * gap)) / 2; y = 880
    ta = wt_any(si, "already")
    for i, ch in enumerate(days):
        x = x0 + i * (bw + gap)
        p = prog(t, ta + 0.08 * i, 0.25)
        rrect(d, (x, y, x + bw, y + 130), 14, fill=mix(mix(BG, (36, 36, 40), a), ACC, p), outline=mix(BG, BORDER, a), width=2)
        mono_label(d, (x + bw / 2, y + 65), ch, DARK if p > 0.5 else mix(BG, TXT, a), 42, "mm")
    mono_label(d, (W / 2, y + 175), "DINNER PLANNED", mix(BG, MUTED, prog(t, ta, 0.3)), 28, "mm")
    pa = prog(t, wt_any(si, "stopped") - 0.1, 0.4)
    put_sprite(img, "karthik_after", W / 2, 1520, 420, pa)

def prop_box(img, d, si, t):
    a = a_in(si, t, 0.0, 0.35)
    cx, cy = W / 2, 1180
    # meal box
    rrect(d, (cx - 230, cy - 110, cx + 230, cy + 150), 26, fill=mix(BG, (44, 44, 50), a), outline=mix(BG, ACC, a), width=4)
    rrect(d, (cx - 250, cy - 150, cx + 250, cy - 100), 18, fill=mix(BG, ACC, a))
    d.text((cx, cy + 20), "FitEats", font=font("bold", 80), fill=mix(BG, TXT, a), anchor="mm")
    mono_label(d, (cx, cy + 95), "DINNER", mix(BG, MUTED, a), 28, "mm")
    tags = [("HIGH PROTEIN", "protein", 230, 900), ("CALORIES COUNTED", "calories", W - 290, 960), ("AT YOUR DOOR", "door", 250, 1440), ("BEFORE 8:47", "before", W - 260, 1440)]
    for lab, k, x, y in tags:
        p = prog(t, wt_any(si, k) - 0.05, 0.3)
        if p > 0: tag(d, x, y, lab, p, 30, fill=CORAL if "8:47" in lab else ACC)

def prop_same(img, d, si, t):
    a = a_in(si, t, 0.0, 0.4)
    put_sprite(img, "karthik_after", W / 2, 1520, 440, a)
    td = wt_any(si, "different")
    c = prog(t, td, 0.4)
    small_clock(d, W / 2, 930, "8:47", mix(CORAL, ACC, c), a)
    if c > 0: tag(d, W / 2, 1040, "NOTHING TO DECIDE", c, 28)

def prop_cta(img, d, si, t):
    a0 = a_in(si, t, 0.05, 0.4)
    fb = font("bold", 150); tw_ = text_w(fb, "FitEats"); y = 1000
    d.text((W / 2 - 18, y), "FitEats", font=fb, fill=mix(BG, TXT, a0), anchor="mm")
    dot = aa_circle_img(34, ACC + (255,)); paste_a(img, dot, (W / 2 + tw_ / 2 - 6, y + 22), a0)
    mono_label(d, (W / 2, y + 120), "HIGH-PROTEIN DIET MEALS · CHENNAI", mix(BG, MUTED, a0), 28, "mm")
    tp = prog(t, wt_any(si, "comment") - 0.05, 0.3)
    if tp > 0: tag(d, W / 2, y + 250, "COMMENT “MENU”", tp, 44, pad=(26, 14))
    tp2 = prog(t, wt_any(si, "plan"), 0.3)
    if tp2 > 0: mono_label(d, (W / 2, y + 350), "GET THIS WEEK'S PLAN IN YOUR DMS", mix(BG, TXT, tp2), 28, "mm")

def prop_outro(img, d, si, t):
    a = a_in(si, t, 0.0, 0.4)
    big_clock(img, d, 1110, "8:46", CORAL, a, 210, "TONIGHT", blink_t=t)
    tp = prog(t, wt_any(si, "coming"), 0.3)
    if tp > 0: tag(d, W / 2, 1360, "COMMENT “MENU” BEFORE IT HITS", tp, 30)

PROPS = {name: globals()["prop_" + name] for name, _ in SCENES}

# ---------- persistent chrome ----------
def draw_chrome(img, d, t):
    tag(d, W / 2, 330, "FITEATS · 8:47 PM", 1.0, 32)
    # progress dots (episode-ish tracker of scenes)
    n = len(SCENES); r = 8; gap = 30; x0 = W / 2 - (n - 1) * gap / 2; y = 1560
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
    _grp = lambda k: k
    if si < len(SCENES) - 1 and t > te - 0.16 and _grp(SCENES[si][0]) != _grp(SCENES[si + 1][0]):
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
