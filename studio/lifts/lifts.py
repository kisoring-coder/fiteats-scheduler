"""Blueprint-style anatomical lifter rig (side view, facing right). Drawn in code, no image credits."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

S = 2                      # supersampling of the figure layer
Z = 1.0                    # output zoom (set by the reel)
FW, FH = 1080, 1120        # figure layer size (final px)
GROUND = 1050              # ground y inside the layer
WHITE = (226, 230, 238); FAINT = (104, 112, 126); BODY = (13, 14, 18); LIME = (201, 236, 74)
LEN = dict(torso=252, ua=146, fa=134, th=198, sh=192, foot=72, neck=30)
PLATE_R = 96

def lerp(a, b, t): return a + (b - a) * t
def add(p, q, s=1.0): return (p[0] + q[0] * s, p[1] + q[1] * s)
def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def norm(p): d = math.hypot(*p) or 1e-6; return (p[0] / d, p[1] / d)
def vdir(a):  # angle from straight UP, + = forward (right)
    r = math.radians(a); return (math.sin(r), -math.cos(r))

def ik(root, target, a, b, prefer):
    dx, dy = target[0] - root[0], target[1] - root[1]; d = math.hypot(dx, dy)
    d = max(1.0, min(d, a + b - 0.01)); base = math.atan2(dy, dx)
    A = math.acos(max(-1, min(1, (a * a + d * d - b * b) / (2 * a * d))))
    best = None
    for s in (1, -1):
        ang = base + s * A; mid = (root[0] + a * math.cos(ang), root[1] + a * math.sin(ang))
        sc = prefer(mid)
        if best is None or sc > best[0]: best = (sc, mid)
    mid = best[1]; e = norm(sub(target, mid))
    return mid, add(mid, e, b)

# ---------------------------------------------------------------- body profiles (half-widths, front / back)
PROF = {
 "thigh": ([(0, 34), (0.3, 41), (0.7, 33), (1, 21)], [(0, 36), (0.35, 39), (0.8, 27), (1, 21)]),
 "shin": ([(0, 19), (0.5, 15), (1, 11)], [(0, 21), (0.25, 31), (0.55, 24), (1, 12)]),
 "ua": ([(0, 27), (0.5, 23), (1, 16)], [(0, 29), (0.45, 27), (1, 16)]),
 "fa": ([(0, 17), (0.3, 19), (1, 11)], [(0, 17), (0.3, 18), (1, 11)]),
 "neck": ([(0, 19), (1, 16)], [(0, 21), (1, 16)]),
 "torso": ([(-0.12, 28), (0, 46), (0.3, 45), (0.55, 46), (0.78, 57), (0.93, 46), (1, 30)],
           [(-0.12, 34), (0, 60), (0.15, 52), (0.35, 41), (0.6, 49), (0.8, 55), (0.95, 46), (1, 32)]),
}
def prof(pts, t):
    if t <= pts[0][0]: return pts[0][1]
    for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0); u = (1 - math.cos(u * math.pi)) / 2
            return lerp(w0, w1, u)
    return pts[-1][1]

class Seg:
    def __init__(self, name, a, b, flip=False, t0=0.0, t1=1.0):
        self.name, self.a, self.b, self.t0, self.t1 = name, a, b, t0, t1
        d = norm(sub(b, a)); self.d = d
        n = (d[1], -d[0]); self.n = (-n[0], -n[1]) if flip else n   # anterior normal
        self.L = math.hypot(*sub(b, a))
    def pt(self, t, side, frac=1.0):
        fp, bp = PROF[self.name]
        base = add(self.a, self.d, self.L * t)
        if side > 0: return add(base, self.n, prof(fp, t) * frac)
        return add(base, self.n, -prof(bp, t) * frac)
    def outline(self, n=28):
        ts = [lerp(self.t0, self.t1, i / n) for i in range(n + 1)]
        return [self.pt(t, 1) for t in ts] + [self.pt(t, -1) for t in reversed(ts)]
    def muscle(self, side, t0, t1, depth, n=18):
        ts = [lerp(t0, t1, i / n) for i in range(n + 1)]
        if side == 0:  # centre band
            outer = [self.pt(t, 1, 0.42 * math.sin(math.pi * i / n)) for i, t in enumerate(ts)]
            inner = [self.pt(t, -1, 0.42 * math.sin(math.pi * i / n)) for i, t in enumerate(ts)]
            return outer + inner[::-1]
        edge = [self.pt(t, side, 0.96) for t in ts]
        inner = [self.pt(t, side, 1 - depth * math.sin(math.pi * i / n) ** 0.7) for i, t in enumerate(ts)]
        return edge + inner[::-1]

# muscle key -> list of (segment, side, t0, t1, depth)
MUSCLES = {
 "traps": [("torso", -1, 0.8, 1.0, 0.9), ("neck", -1, -0.05, 0.9, 0.85)],
 "shoulders": [("ua", 1, -0.06, 0.34, 1.0), ("ua", -1, -0.06, 0.34, 1.0)],
 "triceps": [("ua", -1, 0.22, 0.9, 0.8)],
 "biceps": [("ua", 1, 0.3, 0.88, 0.7)],
 "forearms": [("fa", 1, 0.02, 0.68, 0.95), ("fa", -1, 0.02, 0.68, 0.95)],
 "upperback": [("torso", -1, 0.6, 0.86, 0.75)],
 "lats": [("torso", -1, 0.36, 0.7, 0.55)],
 "lowerback": [("torso", -1, 0.1, 0.42, 0.6)],
 "glutes": [("torso", -1, -0.12, 0.17, 1.0)],
 "core": [("torso", 1, 0.08, 0.6, 0.55)],
 "chest": [("torso", 1, 0.68, 0.95, 0.7)],
 "quads": [("thigh", 1, 0.05, 0.95, 0.85)],
 "hamstrings": [("thigh", -1, 0.12, 0.92, 0.85)],
 "innerthigh": [("thigh", 0, 0.04, 0.62, 1.0)],
 "calves": [("shin", -1, 0.06, 0.58, 0.92)],
}
LEGS = ("quads", "hamstrings", "calves")

# ---------------------------------------------------------------- pose
def solve(pose, cx):
    """pose: hip(x,y) rel to ankle, lean, wrist(x,y) rel to ankle, head."""
    ank = (cx, GROUND - 12)
    hip = add(ank, pose["hip"])
    sh = add(hip, vdir(pose["lean"]), LEN["torso"])
    knee, ank2 = ik(hip, ank, LEN["th"], LEN["sh"], lambda m: m[0])
    wr = add(ank, pose["wrist"])
    pe = pose.get("elbow", "low")
    pref = (lambda m: m[1]) if pe == "low" else (lambda m: m[0]) if pe == "fwd" else (lambda m: -m[0] * 0.4 + m[1])
    elb, wr2 = ik(sh, wr, LEN["ua"], LEN["fa"], pref)
    neck_top = add(sh, vdir(pose["lean"] * 0.55 + pose.get("head", 0)), LEN["neck"])
    head = add(neck_top, vdir(pose["lean"] * 0.4 + pose.get("head", 0)), 40)
    return dict(ank=ank, hip=hip, sh=sh, knee=knee, elb=elb, wr=wr2, neck=neck_top, head=head,
                bar=(wr2 if ("bar" not in pose or math.hypot(pose["bar"][0] - pose["wrist"][0], pose["bar"][1] - pose["wrist"][1]) < 1) else add(ank, pose["bar"])), lean=pose["lean"], ph=pose.get("head", 0))

def interp(keys, u):
    """keys: list of (u, pose); u in [0,1)."""
    for (u0, p0), (u1, p1) in zip(keys, keys[1:]):
        if u0 <= u <= u1:
            t = (u - u0) / max(1e-6, u1 - u0); t = t * t * (3 - 2 * t)
            out = {}
            for k in p0:
                a, b = p0[k], p1.get(k, p0[k])
                if isinstance(a, tuple): out[k] = (lerp(a[0], b[0], t), lerp(a[1], b[1], t))
                elif isinstance(a, str): out[k] = a if t < 0.5 else b
                else: out[k] = lerp(a, b, t)
            return out
    return dict(keys[-1][1])

# Bar positions relative to the ankle (x forward, y up negative)
def dl_pose(h, lean):  # h = bar height above ground; arms straight, shoulder slightly ahead of bar
    bar = (14, -h)
    arm = LEN["ua"] + LEN["fa"] - 4
    sh = (bar[0] + 10 + lean * 0.25, bar[1] - arm)
    v = vdir(lean); hip = (sh[0] - v[0] * LEN["torso"], sh[1] - v[1] * LEN["torso"])
    return dict(hip=hip, lean=lean, wrist=bar, bar=bar, head=-lean * 0.35, elbow="low")

DEADLIFT = [(0.0, dl_pose(PLATE_R + 2, 72)), (0.42, dl_pose(PLATE_R + 2 + 262, 0)), (0.6, dl_pose(PLATE_R + 2 + 262, 0)),
            (1.0, dl_pose(PLATE_R + 2, 72))]

def sq_pose(hip, lean):
    v = vdir(lean); sh = (hip[0] + v[0] * LEN["torso"], hip[1] + v[1] * LEN["torso"])
    bar = (sh[0] - 22, sh[1] + 8)
    return dict(hip=hip, lean=lean, wrist=(bar[0] + 14, bar[1] + 4), bar=bar, head=-lean * 0.45, elbow="back")

SQUAT = [(0.0, sq_pose((-36, -372), 8)), (0.45, sq_pose((-150, -205), 42)), (0.55, sq_pose((-150, -205), 42)),
         (1.0, sq_pose((-36, -372), 8))]

def cp_pose(hip, lean, wrist, elbow, head=0):
    return dict(hip=hip, lean=lean, wrist=wrist, bar=wrist, head=head, elbow=elbow)

CLEAN = [
 (0.00, cp_pose((-46, -362), 18, (34, -335), "low", -6)),        # hang: bar mid-thigh
 (0.12, cp_pose((-28, -382), 2, (26, -540), "fwd", 0)),           # pull (elbows high)
 (0.24, cp_pose((-40, -352), 6, (44, -632), "fwd", 0)),           # catch in front rack
 (0.34, cp_pose((-30, -378), 2, (40, -640), "fwd", 0)),           # stand
 (0.52, cp_pose((-26, -384), -2, (-8, -900), "fwd", -4)),         # press lockout
 (0.62, cp_pose((-26, -384), -2, (-8, -900), "fwd", -4)),
 (0.78, cp_pose((-30, -378), 2, (40, -640), "fwd", 0)),           # back to rack
 (1.00, cp_pose((-46, -362), 18, (34, -335), "low", -6)),         # back to hang
]
STAND = [(0.0, dict(hip=(-22, -386), lean=0, wrist=(-4, -372), head=0, elbow="back")),
         (1.0, dict(hip=(-22, -386), lean=0, wrist=(-4, -372), head=0, elbow="back"))]

# ---------------------------------------------------------------- drawing
def P(p): return (p[0] * S * Z, p[1] * S * Z)
def poly(pts): return [P(p) for p in pts]

def _edge(M, o):
    bb = M.getbbox()
    out = Image.new("L", M.size, 0)
    if not bb: return out
    pad = o + 2; bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(M.width, bb[2] + pad), min(M.height, bb[3] + pad))
    c = M.crop(bb); e = ImageChops.subtract(c.filter(ImageFilter.MaxFilter(o)), c)
    out.paste(e, bb[:2]); return out

def draw_figure(J, hl, plate=True, show_bar=True, dim=1.0):
    """Clean silhouettes (one continuous outline per body layer), anatomy contours, lime highlights."""
    big = Image.new("RGBA", (int(FW * S * Z), int(FH * S * Z)), (0, 0, 0, 0))
    glowL = Image.new("RGBA", big.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glowL)
    cents = {}
    fw = max(1, int(1.2 * S * Z)); OE = 5 if S * Z < 2.6 else 7
    def segs(off=(0, 0)):
        o = lambda p: add(p, off)
        return {"thigh": Seg("thigh", o(J["hip"]), o(J["knee"])), "shin": Seg("shin", o(J["knee"]), o(J["ank"])),
                "ua": Seg("ua", o(J["sh"]), o(J["elb"])), "fa": Seg("fa", o(J["elb"]), o(J["wr"])),
                "torso": Seg("torso", o(J["hip"]), o(J["sh"]), flip=True, t0=-0.12, t1=1.0),
                "neck": Seg("neck", o(add(J["sh"], norm(sub(J["neck"], J["sh"])), -6)), o(J["neck"]), flip=True)}
    def endr(sg, t):
        fp, bp = PROF[sg.name]; return (prof(fp, t) + prof(bp, t)) / 2
    def circ(md, p, r): md.ellipse(P((p[0] - r, p[1] - r)) + P((p[0] + r, p[1] + r)), fill=255)
    def shoe_pts(off):
        a = add(J["ank"], off)
        return [add(a, (-24, -18)), add(a, (12, -24)), add(a, (54, -8)), add(a, (LEN["foot"], 2)), add(a, (LEN["foot"] - 4, 12)), add(a, (-26, 12))]
    def head_pts():
        hc = J["head"]; ang = math.radians(J["lean"] * 0.4 + J["ph"])
        ca, sa = math.cos(ang), math.sin(ang)
        rot = lambda x, y: (hc[0] + x * ca - y * sa, hc[1] + x * sa + y * ca)
        ell = [rot(38 * math.cos(t), 45 * math.sin(t) - 2 * math.cos(t)) for t in [i * math.pi / 30 for i in range(60)]]
        nose = [rot(32, -6), rot(45, 10), rot(32, 16)]
        jaw = [rot(20, 40), rot(34, 30), rot(36, 18)]
        return ell, nose, jaw, rot
    def layer(sg, parts, extra, near, muscles=True):
        M = Image.new("L", big.size, 0); md = ImageDraw.Draw(M)
        for name in parts:
            md.polygon(poly(sg[name].outline()), fill=255)
        for fn in extra: fn(md)
        lay = Image.new("RGBA", big.size, BODY + (0,)); lay.putalpha(M)
        tmp = Image.new("RGBA", big.size, (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
        if muscles:
            for key, lst in MUSCLES.items():
                for (sn, side, t0, t1, dp) in lst:
                    if sn not in parts: continue
                    s = sg[sn]; mp = poly(s.muscle(side, t0, t1, dp))
                    h = hl.get(key, 0) * (1.0 if near else 0.5)
                    if key in LEGS and hl.get("legs", 0) > 0: h = max(h, hl["legs"] * (1.0 if near else 0.5))
                    fib = lambda f, a, b: [P(s.pt(lerp(t0, t1, i / 10), side if side else 1, (1 - f * dp * 0.9) if side else f * 0.4)) for i in range(a, b)]
                    if h > 0.01:
                        c = tuple(int(lerp(BODY[i], LIME[i], h)) for i in range(3))
                        d.polygon(mp, fill=c + (255,)); gd.polygon(mp, fill=LIME + (int(190 * h),))
                        for k in range(1, 5):
                            d.line(fib(k / 5.0, 1, 10), fill=tuple(int(lerp(c[i], 255, 0.4)) for i in range(3)) + (int(170 * h),), width=fw)
                        if near:
                            cents.setdefault(key, (sum(p[0] for p in mp) / len(mp) / S, sum(p[1] for p in mp) / len(mp) / S))
                    else:
                        for k in (1, 2, 3): d.line(fib(k / 4.0, 2, 9), fill=(46, 50, 60, 255), width=fw)
                    d.line(mp + [mp[0]], fill=((FAINT if near else (60, 64, 74)) if h < 0.5 else (232, 250, 170)) + (255,), width=fw)
        clip = Image.new("RGBA", big.size, (0, 0, 0, 0)); clip.paste(tmp, (0, 0), M)
        lay.alpha_composite(clip)
        E = _edge(M, OE); col = WHITE if near else (132, 138, 150)
        edge = Image.new("RGBA", big.size, col + (0,)); edge.putalpha(E)
        lay.alpha_composite(edge)
        big.alpha_composite(lay)
    far = (-10, -6)
    sgf, sgn = segs(far), segs()
    # far leg + far arm
    layer(sgf, ["thigh", "shin"], [lambda md: circ(md, add(J["knee"], far), endr(sgf["thigh"], 1) + 1),
                                    lambda md: md.polygon(poly(shoe_pts(far)), fill=255)], False)
    def arm_extra(off, sg):
        w = add(J["wr"], off)
        return [lambda md: circ(md, add(J["elb"], off), endr(sg["ua"], 1)),
                lambda md: circ(md, add(J["sh"], off), endr(sg["ua"], 0)),
                lambda md: md.rounded_rectangle(P((w[0] - 16, w[1] - 16)) + P((w[0] + 16, w[1] + 18)), int(9 * S * Z), fill=255)]
    layer(sgf, ["ua", "fa"], arm_extra(far, sgf), False)
    # main body: torso + neck + head + near leg + foot
    ell, nose, jaw, rot = head_pts()
    layer(sgn, ["torso", "neck", "thigh", "shin"],
          [lambda md: md.polygon(poly(ell), fill=255), lambda md: md.polygon(poly(nose), fill=255),
           lambda md: circ(md, J["knee"], endr(sgn["thigh"], 1) + 1), lambda md: circ(md, J["hip"], 42),
           lambda md: md.polygon(poly(shoe_pts((0, 0))), fill=255)], True)
    bd = ImageDraw.Draw(big)
    bd.ellipse(poly([rot(-14, -6)]) [0] + poly([rot(-2, 14)])[0], outline=FAINT + (255,), width=fw)  # ear
    bd.line(poly([rot(20, -4), rot(30, -4)]), fill=WHITE + (255,), width=fw)                        # eye
    bd.line(poly([rot(-36, -20), rot(-10, -40), rot(20, -42)]), fill=FAINT + (255,), width=fw)       # hairline
    bd.line(poly(jaw), fill=FAINT + (255,), width=fw)
    sa = shoe_pts((0, 0)); bd.line(poly([sa[-1], add(sa[3], (-4, 4))]), fill=FAINT + (255,), width=fw)
    # plate (own layer so the body shows through)
    if show_bar:
        b = J["bar"]; lw = int(2.4 * S * Z)
        PL = Image.new("RGBA", big.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(PL)
        if plate:
            r = PLATE_R
            pd.ellipse(P((b[0] - r, b[1] - r)) + P((b[0] + r, b[1] + r)), fill=(12, 13, 16, 80), outline=WHITE + (255,), width=lw)
            for rr, c in ((r - 9, FAINT), (r - 38, (70, 76, 88)), (r - 62, (110, 116, 128))):
                pd.ellipse(P((b[0] - rr, b[1] - rr)) + P((b[0] + rr, b[1] + rr)), outline=c + (255,), width=fw)
        pd.ellipse(P((b[0] - 15, b[1] - 15)) + P((b[0] + 15, b[1] + 15)), fill=(30, 32, 38, 255), outline=WHITE + (255,), width=lw)
        big.alpha_composite(PL)
    # near arm on top
    layer(sgn, ["ua", "fa"], arm_extra((0, 0), sgn), True)
    w = J["wr"]
    if hl.get("grip", 0) > 0.01:
        h = hl["grip"]; c = tuple(int(lerp(BODY[i], LIME[i], h)) for i in range(3))
        bd.rounded_rectangle(P((w[0] - 13, w[1] - 13)) + P((w[0] + 13, w[1] + 15)), int(7 * S * Z), fill=c + (255,))
        gd.ellipse(P((w[0] - 28, w[1] - 28)) + P((w[0] + 28, w[1] + 28)), fill=LIME + (int(200 * h),))
        cents.setdefault("grip", (w[0] * S * Z / S, w[1] * S * Z / S))
    for k in (-6, 0, 6): bd.line(P((w[0] + 8, w[1] + k)) + P((w[0] + 15, w[1] + k)), fill=FAINT + (255,), width=fw)  # knuckles
    small = glowL.resize((glowL.width // 8, glowL.height // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0)); out.alpha_composite(small.resize(big.size, Image.BILINEAR)); out.alpha_composite(big)
    out = out.resize((int(FW * Z), int(FH * Z)), Image.LANCZOS)
    if dim < 0.99:
        a = out.getchannel("A").point(lambda v: int(v * dim)); out.putalpha(a)
    return out, cents

def floor(layer, cx, w=420):
    d = ImageDraw.Draw(layer)
    d.line([(cx - w, GROUND), (cx + w, GROUND)], fill=(120, 126, 138, 255), width=2)
    for i in range(-6, 7):
        d.line([(cx + i * 60, GROUND), (cx + i * 90, GROUND + 60)], fill=(40, 44, 52, 255), width=1)
    for j, y in enumerate((GROUND + 18, GROUND + 40)):
        d.line([(cx - w - j * 40, y), (cx + w + j * 40, y)], fill=(34, 37, 44, 255), width=1)
