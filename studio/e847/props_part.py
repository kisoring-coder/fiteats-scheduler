
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
