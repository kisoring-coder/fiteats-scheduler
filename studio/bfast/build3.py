"""FitEats - 'Let me guess' skipped-breakfast reel. Reality Check style (reuses b2 engine)."""
import math, os, subprocess, sys, random
from PIL import Image, ImageDraw
import b2
from b2 import (W, H, FPS, BG, TXT, GREY, DARK, LIME, CORAL, OUT, INK, F, clamp, ease, back, prog, sprite, vgrad,
                shape_mask, put, SP, bg, GLOW, headline_scaled)
TOTAL = 36.4

def plate_empty(w=520, h=260):
    def fn(d, k, im):
        d.ellipse((30*k, 70*k, (w-10)*k, (h-10)*k), fill=(0,0,0,100))
        box = (14*k, 40*k, (w-24)*k, (h-40)*k); m = shape_mask(im.size, lambda md: md.ellipse(box, fill=255))
        vgrad(im, box, (236,238,242), (190,194,204), m)
        d.ellipse((90*k, 76*k, (w-100)*k, (h-76)*k), outline=(170,174,184,255), width=int(4*k))
        d.ellipse(box, outline=OUT+(255,), width=int(5*k))
    return sprite(w, h, fn)

def rice_plate(w=420, h=260):
    def fn(d, k, im):
        d.ellipse((24*k, 120*k, (w-10)*k, (h-6)*k), fill=(0,0,0,100))
        box = (12*k, 110*k, (w-20)*k, (h-20)*k); m = shape_mask(im.size, lambda md: md.ellipse(box, fill=255))
        vgrad(im, box, (230,232,238), (186,190,200), m)
        mound = (70*k, 30*k, (w-80)*k, 190*k); mm = shape_mask(im.size, lambda md: md.pieslice(mound, 180, 360, fill=255))
        vgrad(im, mound, (255,252,240), (232,222,196), mm)
        rnd = random.Random(4)
        for _ in range(60):
            x = rnd.uniform(90, w-100)*k; y = rnd.uniform(60, 108)*k
            if ((x/k-(w-10)/2)/((w-150)/2))**2 + ((y/k-110)/80)**2 < 1:
                d.ellipse((x-3*k, y-1.5*k, x+3*k, y+1.5*k), fill=(214,204,176,255))
        d.ellipse((260*k, 130*k, 340*k, 168*k), fill=(232,170,60,255), outline=OUT+(255,), width=int(3*k))
        d.ellipse((90*k, 128*k, 170*k, 166*k), fill=(120,170,80,255), outline=OUT+(255,), width=int(3*k))
        d.arc(mound, 180, 360, fill=OUT+(255,), width=int(5*k))
        d.ellipse(box, outline=OUT+(255,), width=int(5*k))
    return sprite(w, h, fn)

def chai(w=220, h=300):
    def fn(d, k, im):
        d.ellipse((30*k, 250*k, (w-20)*k, (h-6)*k), fill=(0,0,0,110))
        g = [(40*k, 60*k), ((w-40)*k, 60*k), ((w-60)*k, 270*k), (60*k, 270*k)]
        m = shape_mask(im.size, lambda md: md.polygon(g, fill=255))
        vgrad(im, (40*k, 60*k, (w-40)*k, 270*k), (206,150,92), (150,92,46), m)
        d.polygon([(40*k,60*k),((w-40)*k,60*k),((w-44)*k,90*k),(44*k,90*k)], fill=(236,214,180,255))
        for x in (70, 110, 150):
            d.line([(x*k, 110*k), ((x-6)*k, 250*k)], fill=(240,220,190,90), width=int(4*k))
        d.line(g+[g[0]], fill=OUT+(255,), width=int(5*k), joint="curve")
        for i,dx in enumerate((-30,0,30)):
            ph = i*0.4
            d.arc(((w/2+dx-14)*k, 10*k, (w/2+dx+14)*k, 50*k), 200, 340, fill=GREY+(255,), width=int(5*k))
    return sprite(w, h, fn)

def samosa(w=280, h=240):
    def fn(d, k, im):
        pts = [(w/2*k, 20*k), ((w-20)*k, (h-40)*k), (20*k, (h-40)*k)]
        d.polygon([(x+8*k, y+14*k) for x,y in pts], fill=(0,0,0,110))
        m = shape_mask(im.size, lambda md: md.polygon(pts, fill=255))
        vgrad(im, (0, 20*k, w*k, (h-40)*k), (244,196,96), (200,128,40), m)
        rnd = random.Random(2)
        for _ in range(30):
            x = rnd.uniform(60, w-60)*k; y = rnd.uniform(90, h-60)*k
            d.ellipse((x-3*k, y-3*k, x+3*k, y+3*k), fill=(176,104,32,255))
        d.line(pts+[pts[0]], fill=OUT+(255,), width=int(5*k), joint="curve")
    return sprite(w, h, fn)

def battery(level, w=360, h=180):
    def fn(d, k, im):
        d.rounded_rectangle((10*k, 20*k, (w-50)*k, (h-20)*k), int(24*k), fill=DARK+(255,), outline=OUT+(255,), width=int(8*k))
        d.rounded_rectangle(((w-50)*k, 65*k, (w-20)*k, (h-65)*k), int(8*k), fill=OUT+(255,))
        if level > 0:
            d.rounded_rectangle((30*k, 40*k, (30+(w-100)*level)*k, (h-40)*k), int(12*k), fill=(CORAL if level<0.3 else LIME)+(255,))
    return sprite(w, h, fn)

def scale_s(w=420, h=300):
    def fn(d, k, im):
        d.ellipse((30*k, (h-50)*k, (w-20)*k, (h-6)*k), fill=(0,0,0,110))
        body = (20*k, 40*k, (w-30)*k, (h-30)*k); m = shape_mask(im.size, lambda md: md.rounded_rectangle(body, int(50*k), fill=255))
        vgrad(im, body, (90,96,110), (58,62,74), m)
        d.rounded_rectangle(body, int(50*k), outline=OUT+(255,), width=int(6*k))
        d.rounded_rectangle((110*k, 80*k, (w-120)*k, 160*k), int(16*k), fill=(26,28,34,255), outline=OUT+(255,), width=int(4*k))
        d.text(((w-10)/2*k, 120*k), "? ? ?", font=F("anton", int(56*k)), fill=CORAL+(255,), anchor="mm")
    return sprite(w, h, fn)

def egg(w=170, h=210, half=False):
    def fn(d, k, im):
        d.ellipse((24*k, (h-40)*k, (w-14)*k, (h-6)*k), fill=(0,0,0,100))
        body = (14*k, 10*k, (w-20)*k, (h-24)*k); m = shape_mask(im.size, lambda md: md.ellipse(body, fill=255))
        vgrad(im, body, (255,255,252), (228,222,210), m)
        if half:
            d.ellipse((44*k, 70*k, (w-50)*k, (h-64)*k), fill=(255,196,40,255))
        d.ellipse((40*k, 30*k, 74*k, 80*k), fill=(255,255,255,255))
        d.ellipse(body, outline=OUT+(255,), width=int(5*k))
    return sprite(w, h, fn)

def pill_x(text, size=70):
    im = b2.pill(text, DARK, fg=GREY, size=size)
    d = ImageDraw.Draw(im)
    d.line([(20, im.height*0.55), (im.width-30, im.height*0.4)], fill=CORAL, width=10)
    return im

def build():
    b2.build_sprites()
    SP.update(plate=plate_empty(), rice=rice_plate(), chai=chai(), samosa=samosa(), bat_lo=battery(0.12), bat_hi=battery(0.9),
              scale=scale_s(), egg=egg(), egg_half=egg(half=True), b12=b2.badge("~12g", LIME), x2=b2.badge("2X", CORAL),
              will=pill_x("WILLPOWER"), carbs=b2.pill("LESS CARBS", DARK, fg=TXT, size=56), prot=b2.pill("MORE PROTEIN", LIME, size=56))

SC = [
 (0.00, "LET ME {GUESS}", "neutral", "guess"),
 (0.90, "YOU [SKIP] BREAKFAST", "red", "skip"),
 (3.10, "BY 1 PM YOU'RE [STARVING]", "warm", "one"),
 (4.80, "SO LUNCH IS [DOUBLE]", "red", "double"),
 (6.40, "BY 4 PM YOU'RE [CRASHING]", "red", "crash"),
 (8.05, "CHAI AND [SNACKS]", "warm", "snack"),
 (9.90, "WHY ISN'T THE [WEIGHT] MOVING?", "red", "scale"),
 (12.70, "IT'S NOT YOUR WILLPOWER", "neutral", "will"),
 (14.20, "IT'S YOUR {FIRST MEAL}", "lime", "first"),
 (15.65, "NO PROTEIN AT BREAKFAST = [A FAILED DAY]", "red", "fail"),
 (19.40, "HERE'S WHAT {NOBODY TELLS YOU}", "lime", "fix"),
 (21.30, "DON'T EAT [LESS] IN THE MORNING", "red", "less"),
 (23.65, "EAT {MORE PROTEIN} AND LESS CARBS", "lime", "more"),
 (26.50, "2 BOILED EGGS = {~12 g PROTEIN}", "lime", "eggs"),
 (29.30, "NO TIME TO COOK?", "neutral", "clock"),
 (30.45, "FITEATS PLANS EVERY MEAL {HIGH IN PROTEIN}", "lime", "cta"),
]
CY = 1180

def clock_at(hour, size=360):
    key = f"clk{hour}"
    if key not in SP:
        def fn(d, k, im):
            c = size*k/2; r = (size/2-20)*k
            d.ellipse((c-r+10*k, c-r+16*k, c+r+10*k, c+r+16*k), fill=(0,0,0,100))
            d.ellipse((c-r, c-r, c+r, c+r), fill=DARK+(255,), outline=OUT+(255,), width=int(8*k))
            for i in range(12):
                a = i*math.pi/6
                d.line([(c+math.cos(a)*r*0.78, c+math.sin(a)*r*0.78), (c+math.cos(a)*r*0.9, c+math.sin(a)*r*0.9)], fill=GREY+(255,), width=int(6*k))
            ah = (hour % 12)/12*2*math.pi - math.pi/2
            d.line([(c, c), (c, c-r*0.68)], fill=OUT+(255,), width=int(10*k))
            d.line([(c, c), (c+math.cos(ah)*r*0.45, c+math.sin(ah)*r*0.45)], fill=CORAL+(255,), width=int(14*k))
            d.ellipse((c-14*k, c-14*k, c+14*k, c+14*k), fill=OUT+(255,))
        SP[key] = sprite(size, size, fn)
    return key

def draw(cv, d, key, t, t0):
    p = back((t - t0)/0.45) if t0 > 0 else 1.0
    bob = math.sin(t*2.2)*6
    if key == "guess":
        put(cv, clock_at(7), W/2, CY, 1.0*p)
        d.text((W/2, CY+250), "7 AM", font=F("anton", 60), fill=GREY, anchor="mm")
    elif key == "skip":
        put(cv, "plate", W/2, CY, 1.25*p)
        put(cv, "cross", W/2, CY, 0.95*back((t-t0-0.6)/0.3))
        d.text((W/2, CY+230), "BREAKFAST", font=F("anton", 60), fill=GREY, anchor="mm")
    elif key == "one":
        put(cv, clock_at(1), W/2, CY, 1.0*p)
        d.text((W/2, CY+250), "1 PM", font=F("anton", 60), fill=CORAL, anchor="mm")
    elif key == "double":
        put(cv, "rice", W/2-200, CY+bob, 0.95*p)
        put(cv, "rice", W/2+200, CY-bob, 0.95*back((t-t0-0.2)/0.45))
        put(cv, "x2", W/2, CY-200, 0.8*back((t-t0-0.5)/0.4))
    elif key == "crash":
        put(cv, clock_at(4), W/2-210, CY, 0.8*p)
        put(cv, "bat_lo", W/2+190, CY, 0.95*back((t-t0-0.2)/0.45) * (0.9 + 0.1*(math.sin(t*9) > 0)))
        d.text((W/2-210, CY+200), "4 PM", font=F("anton", 56), fill=GREY, anchor="mm")
        d.text((W/2+190, CY+150), "ENERGY", font=F("anton", 56), fill=CORAL, anchor="mm")
    elif key == "snack":
        put(cv, "chai", W/2-170, CY+bob, 1.0*p)
        put(cv, "samosa", W/2+170, CY+20-bob, 1.0*back((t-t0-0.2)/0.45))
    elif key == "scale":
        put(cv, "scale", W/2, CY, 1.2*p)
        d.text((W/2, CY+240), "NIGHT", font=F("anton", 60), fill=GREY, anchor="mm")
    elif key == "will":
        put(cv, "will", W/2, CY, 1.15*p)
    elif key == "first":
        put(cv, clock_at(7), W/2, CY - 30, 0.9*p)
        d.text((W/2, CY+220), "BREAKFAST DECIDES THE DAY", font=F("anton", 56), fill=LIME, anchor="mm")
    elif key == "fail":
        put(cv, "plate", W/2, CY-80, 1.0*p)
        put(cv, "meter_low", W/2, CY+170, 1.0*p)
        d.text((W/2-370, CY+70), "PROTEIN", font=F("anton", 52), fill=GREY, anchor="lm")
        d.text((W/2+370, CY+70), "0 g", font=F("anton", 52), fill=CORAL, anchor="rm")
    elif key == "fix":
        put(cv, "bfix", W/2, CY, 1.35*p)
        for i,(dx,dy,s) in enumerate(((-230,-160,0.9),(240,-120,0.6),(200,190,0.75),(-210,170,0.5))):
            put(cv, "spark", W/2+dx, CY+dy, s*back((t-t0-0.2-i*0.1)/0.4)*(0.85+0.15*math.sin(t*6+i)))
    elif key == "less":
        put(cv, "plate", W/2, CY, 1.1*p)
        put(cv, "check", W/2+240, CY-150, 0.8*back((t-t0-0.5)/0.4))
        d.text((W/2, CY+230), "EAT. JUST EAT RIGHT.", font=F("anton", 56), fill=GREY, anchor="mm")
    elif key == "more":
        put(cv, "prot", W/2, CY-90, 1.15*p)
        put(cv, "carbs", W/2, CY+80, 1.0*back((t-t0-0.3)/0.4))
        lv = ease((t-t0)/1.2)
        put(cv, "meter_hi" if lv > 0.5 else "meter_mid", W/2, CY+260, 1.0)
    elif key == "eggs":
        put(cv, "egg", W/2-120, CY+bob, 1.1*p)
        put(cv, "egg_half", W/2+120, CY-bob, 1.1*back((t-t0-0.2)/0.45))
        put(cv, "b12", W/2+300, CY-200, back((t-t0-0.8)/0.4))
    elif key == "clock":
        put(cv, "clock", W/2, CY, 1.1*p)
    elif key == "cta":
        a = clamp((t-t0)/0.3); fb = F("black", 150)
        tw = d.textlength("FitEats", font=fb)
        d.text((W/2+6, CY-210+8), "FitEats", font=fb, fill=(0,0,0), anchor="mm")
        d.text((W/2, CY-210), "FitEats", font=fb, fill=tuple(int(BG[i]+(TXT[i]-BG[i])*a) for i in range(3)), anchor="mm")
        d.ellipse((W/2+tw/2+6, CY-190, W/2+tw/2+40, CY-156), fill=LIME)
        d.text((W/2, CY-100), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 30), fill=GREY, anchor="mm")
        put(cv, "wa", W/2, CY+50, back((t-t0-0.3)/0.4)*(1+0.035*math.sin(t*6)))
        put(cv, "bio", W/2, CY+210, back((t-t0-0.8)/0.4))

def frame(t):
    i = max(j for j, s in enumerate(SC) if s[0] <= t); s0, markup, glow, key = SC[i]
    cv = bg(GLOW[glow]).copy(); d = ImageDraw.Draw(cv)
    d.rounded_rectangle((60, 214, W-60, 224), 5, fill=(49,53,57))
    d.rounded_rectangle((60, 214, 60+(W-120)*clamp(t/TOTAL), 224), 5, fill=LIME)
    d.rounded_rectangle((60, 254, 380, 312), 29, fill=LIME)
    d.text((220, 284), "REALITY CHECK", font=F("bold", 30), fill=INK, anchor="mm")
    sc = 0.9 + 0.1*back((t-s0)/0.22) if s0 > 0 else 1.0
    him = headline_scaled(markup, round(sc, 2))
    cv.alpha_composite(him, (int((W-him.width)/2), int(640-him.height/2+40)))
    draw(cv, d, key, t, s0)
    if 26.4 < t < 29.3:
        d.text((W/2, 1545), "Estimate: 2 large boiled eggs ≈ 12 g protein.", font=F("bold", 28), fill=GREY, anchor="mm")
    return cv.convert("RGB")

def main():
    build()
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(float(s)).save(f"s_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                          "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p","video_tmp.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait(); os.rename("video_tmp.mp4","video_only.mp4")

if __name__ == "__main__":
    main()
