"""FitEats emotional reels: 'Stay locked in' (s1) and 'Do you have the health?' (s2). Reality Check style."""
import math, os, subprocess, sys, random
from PIL import Image, ImageDraw
import b2
from b2 import (W, H, FPS, BG, TXT, GREY, DARK, LIME, CORAL, OUT, INK, F, clamp, ease, back, sprite, vgrad,
                shape_mask, put, SP, bg, GLOW, headline_scaled)

def shadow(d, k, box): d.ellipse(box, fill=(0,0,0,110))

def briefcase(w=300, h=240):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-40)*k, (w-20)*k, (h-6)*k))
        d.rounded_rectangle((100*k, 20*k, (w-100)*k, 70*k), int(16*k), outline=OUT+(255,), width=int(10*k))
        body = (20*k, 55*k, (w-20)*k, (h-25)*k); m = shape_mask(im.size, lambda md: md.rounded_rectangle(body, int(24*k), fill=255))
        vgrad(im, body, (150,104,64), (104,68,40), m)
        d.line([(20*k, 120*k), ((w-20)*k, 120*k)], fill=(80,50,28,255), width=int(6*k))
        d.rounded_rectangle(((w/2-22)*k, 106*k, (w/2+22)*k, 138*k), int(6*k), fill=(232,190,90,255))
        d.rounded_rectangle(body, int(24*k), outline=OUT+(255,), width=int(6*k))
    return sprite(w, h, fn)

def house(w=300, h=280, col=(240,236,226)):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-40)*k, (w-20)*k, (h-6)*k))
        body = (50*k, 120*k, (w-50)*k, (h-25)*k); m = shape_mask(im.size, lambda md: md.rectangle(body, fill=255))
        vgrad(im, body, col, tuple(int(c*0.82) for c in col), m)
        roof = [(20*k, 130*k), (w/2*k, 20*k), ((w-20)*k, 130*k)]
        d.polygon(roof, fill=CORAL+(255,)); d.line(roof+[roof[0]], fill=OUT+(255,), width=int(6*k), joint="curve")
        d.rounded_rectangle(((w/2-30)*k, 180*k, (w/2+30)*k, (h-25)*k), int(8*k), fill=(120,80,50,255))
        d.rectangle((80*k, 160*k, 120*k, 200*k), fill=(140,200,240,255)); d.rectangle(((w-120)*k, 160*k, (w-80)*k, 200*k), fill=(140,200,240,255))
        d.rectangle(body, outline=OUT+(255,), width=int(6*k))
    return sprite(w, h, fn)

def coins(w=300, h=260):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-40)*k, (w-20)*k, (h-6)*k))
        for i in range(5):
            y = (h-60-i*30)*k
            d.ellipse((60*k, y-26*k, (w-60)*k, y+26*k), fill=(214,160,40,255), outline=OUT+(255,), width=int(5*k))
        top = (h-60-4*30)*k
        d.ellipse((60*k, top-26*k, (w-60)*k, top+26*k), fill=(250,206,80,255), outline=OUT+(255,), width=int(5*k))
        d.text((w/2*k, top), "₹", font=F("bold", int(44*k)), fill=(150,100,20,255), anchor="mm")
    return sprite(w, h, fn)

def storm(w=320, h=280):
    def fn(d, k, im):
        for cx, cy, r in ((110,110,70),(180,90,80),(240,120,60),(160,140,70)):
            d.ellipse(((cx-r)*k, (cy-r)*k, (cx+r)*k, (cy+r)*k), fill=(110,116,130,255))
        for cx, cy, r in ((110,110,70),(180,90,80),(240,120,60)):
            d.arc(((cx-r)*k, (cy-r)*k, (cx+r)*k, (cy+r)*k), 180, 360, fill=OUT+(255,), width=int(5*k))
        bolt = [(170,170),(130,240),(165,240),(140,300),(215,215),(178,215),(205,170)]
        d.polygon([(x*k, (y-30)*k) for x,y in bolt], fill=(255,214,60,255), outline=OUT+(255,))
    return sprite(w, h, fn)

def plate_drop(w=420, h=240):
    def fn(d, k, im):
        box = (14*k, 40*k, (w-24)*k, (h-40)*k); m = shape_mask(im.size, lambda md: md.ellipse(box, fill=255))
        vgrad(im, box, (236,238,242), (190,194,204), m)
        rnd = random.Random(7)
        for _ in range(14):
            x = rnd.uniform(90, w-110)*k; y = rnd.uniform(80, h-90)*k; r = rnd.uniform(14, 26)*k
            col = rnd.choice([(120,180,80),(232,170,60),(244,236,220),(214,80,60)])
            d.ellipse((x-r, y-r*0.7, x+r, y+r*0.7), fill=col+(255,))
        d.ellipse(box, outline=OUT+(255,), width=int(5*k))
    return sprite(w, h, fn)

def padlock(locked=True, w=260, h=320):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-40)*k, (w-20)*k, (h-6)*k))
        if locked: d.arc((60*k, 20*k, (w-60)*k, 200*k), 180, 360, fill=OUT+(255,), width=int(22*k)); d.line([(60*k,110*k),(60*k,150*k)], fill=OUT+(255,), width=int(22*k)); d.line([((w-60)*k,110*k),((w-60)*k,150*k)], fill=OUT+(255,), width=int(22*k))
        body = (30*k, 140*k, (w-30)*k, (h-30)*k); m = shape_mask(im.size, lambda md: md.rounded_rectangle(body, int(30*k), fill=255))
        vgrad(im, body, LIME, (150,190,40), m)
        d.ellipse(((w/2-20)*k, 190*k, (w/2+20)*k, 230*k), fill=INK+(255,)); d.rectangle(((w/2-8)*k, 220*k, (w/2+8)*k, 260*k), fill=INK+(255,))
        d.rounded_rectangle(body, int(30*k), outline=OUT+(255,), width=int(6*k))
    return sprite(w, h, fn)

def idcard(w=340, h=240):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-30)*k, (w-20)*k, (h-4)*k))
        body = (14*k, 14*k, (w-24)*k, (h-30)*k); m = shape_mask(im.size, lambda md: md.rounded_rectangle(body, int(22*k), fill=255))
        vgrad(im, body, (240,240,246), (200,204,214), m)
        d.rectangle((14*k, 14*k, (w-24)*k, 60*k), fill=(60,90,160,255))
        d.ellipse((40*k, 80*k, 130*k, 170*k), fill=(160,166,180,255)); d.ellipse((66*k, 92*k, 104*k, 130*k), fill=(230,232,238,255))
        for i, wd in enumerate((150, 120, 90)):
            d.rounded_rectangle((150*k, (90+i*28)*k, (150+wd)*k, (104+i*28)*k), int(6*k), fill=(150,156,170,255))
        d.text((w/2*k, 37*k), "MANAGER", font=F("anton", int(30*k)), fill=(255,255,255,255), anchor="mm")
        d.rounded_rectangle(body, int(22*k), outline=OUT+(255,), width=int(6*k))
    return sprite(w, h, fn)

def notes(w=320, h=220):
    def fn(d, k, im):
        shadow(d, k, (30*k, (h-30)*k, (w-20)*k, (h-4)*k))
        for i, (dx, dy, a) in enumerate(((0,30,-8),(12,14,4),(24,0,0))):
            n = Image.new("RGBA", (int(260*k), int(140*k)), (0,0,0,0)); nd = ImageDraw.Draw(n)
            nd.rounded_rectangle((0,0,n.width-1,n.height-1), int(14*k), fill=(132,196,120,255), outline=OUT+(255,), width=int(5*k))
            nd.ellipse((n.width/2-40*k, n.height/2-40*k, n.width/2+40*k, n.height/2+40*k), outline=(80,140,70,255), width=int(5*k))
            nd.text((n.width/2, n.height/2), "₹", font=F("bold", int(56*k)), fill=(60,110,50,255), anchor="mm")
            n = n.rotate(a, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(n, (int((20+dx)*k), int((20+dy)*k)))
    return sprite(w, h, fn)

def heart(col=CORAL, cracked=False, w=300, h=280):
    def fn(d, k, im):
        shadow(d, k, (40*k, (h-36)*k, (w-30)*k, (h-6)*k))
        pts = []
        for i in range(120):
            t = i/120*2*math.pi
            x = 16*math.sin(t)**3; y = -(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
            pts.append(((w/2 + x*8.2)*k, (h/2 - 6 + y*8.2)*k))
        m = shape_mask(im.size, lambda md: md.polygon(pts, fill=255))
        vgrad(im, (0, 0, w*k, h*k), col, tuple(int(c*0.75) for c in col), m)
        d.line(pts+[pts[0]], fill=OUT+(255,), width=int(6*k), joint="curve")
        if cracked:
            c = [(w/2+6, 60), (w/2-14, 110), (w/2+12, 150), (w/2-10, 195), (w/2+4, 235)]
            d.line([(x*k, y*k) for x,y in c], fill=BG+(255,), width=int(12*k), joint="curve")
    return sprite(w, h, fn)

def dumbbell(w=380, h=200):
    def fn(d, k, im):
        shadow(d, k, (40*k, (h-40)*k, (w-30)*k, (h-8)*k))
        d.rounded_rectangle((90*k, 85*k, (w-90)*k, 115*k), int(10*k), fill=(200,204,214,255), outline=OUT+(255,), width=int(4*k))
        for x0 in (40, w-90):
            d.rounded_rectangle((x0*k, 30*k, (x0+50)*k, 170*k), int(14*k), fill=(60,64,74,255), outline=OUT+(255,), width=int(5*k))
        for x0 in (20, w-40):
            d.rounded_rectangle((x0*k, 60*k, (x0+20)*k, 140*k), int(8*k), fill=(60,64,74,255), outline=OUT+(255,), width=int(4*k))
    return sprite(w, h, fn)

def salad_bowl():
    return b2.bowl((120,190,90), (80,150,60), [((232,90,70), 10, 9), ((250,210,90), 10, 8), ((244,240,230), 8, 9)])

def build():
    b2.build_sprites()
    SP.update(brief=briefcase(), house=house(), coins=coins(), storm=storm(), dish=plate_drop(), lock=padlock(),
              idcard=idcard(), notes=notes(), heart=heart(), heart_x=heart(cracked=True), heart_g=heart(col=LIME),
              dumbbell=dumbbell(), salad=salad_bowl(), quit=b2.pill("QUIT FIRST", CORAL, size=56),
              diet_x=b2.pill("DIET", DARK, fg=GREY, size=70))

S1 = dict(total=18.6, tag="REALITY CHECK", voice="v1.mp3", sc=[
 (0.00, "YOU'VE TRIED [EVERY DIET]", "red", "diets"),
 (1.60, "STILL IN THE [SAME BODY]", "red", "body"),
 (3.30, "DO YOU KNOW {WHY?}", "neutral", "why"),
 (4.55, "IT'S THE [FRICTION]", "red", "friction"),
 (9.00, "THE FIRST THING YOU QUIT", "warm", "quit"),
 (10.25, "IS [YOUR DIET]", "red", "dietx"),
 (11.50, "NO MORE {SKIPPING YOUR DIET}", "lime", "dish"),
 (14.15, "STAY {LOCKED IN}", "lime", "lock"),
 (15.40, "ORDER FROM {FITEATS}", "lime", "cta"),
])
S2 = dict(total=18.3, tag="REALITY CHECK", voice="v2.mp3", sc=[
 (0.00, "YOU HAVE {THE TITLE}", "neutral", "title"),
 (1.08, "{THE SALARY}", "lime", "salary"),
 (1.95, "AND {THE STABILITY}", "lime", "stable"),
 (3.35, "BUT DO YOU HAVE [THE HEALTH?]", "red", "health"),
 (4.95, "IT MATTERS {MORE THAN MONEY}", "lime", "more"),
 (7.65, "WITHOUT HEALTH", "red", "without"),
 (8.65, "EVERYTHING [FALLS APART]", "red", "apart"),
 (10.30, "GO TO {THE GYM}", "lime", "gym"),
 (11.45, "{EAT HEALTHY}", "lime", "eat"),
 (12.30, "NO TIME TO {COOK HEALTHY?}", "neutral", "cook"),
 (14.95, "ORDER FROM {FITEATS}", "lime", "cta"),
])
CY = 1180

def draw(cv, d, key, t, t0):
    p = back((t-t0)/0.45) if t0 > 0 else 1.0
    bob = math.sin(t*2.2)*6
    def pop(dt): return back((t-t0-dt)/0.4)
    if key == "diets":
        for i, (dx, lab) in enumerate(((-280,"KETO"),(0,"FASTING"),(280,"LOW CARB"))):
            pi = pop(i*0.15)
            if pi > 0.02:
                im = b2.pill(lab, DARK, fg=TXT, size=64)
                s = round(pi, 2); im2 = im.resize((max(1,int(im.width*s)), max(1,int(im.height*s))))
                cv.alpha_composite(im2, (int(W/2+dx-im2.width/2), int(CY-60+(i%2)*120-im2.height/2)))
        for i, dx in enumerate((-280, 0, 280)):
            if t > t0 + 0.9 + i*0.15: put(cv, "cross", W/2+dx, CY-60+(i%2)*120, 0.55)
    elif key == "body":
        put(cv, "b2_mirror" if "b2_mirror" in SP else "meter_low", W/2, CY+40, 1.0*p)
        d.text((W/2-370, CY-60), "PROGRESS", font=F("anton", 52), fill=GREY, anchor="lm")
        d.text((W/2+370, CY-60), "0%", font=F("anton", 52), fill=CORAL, anchor="rm")
    elif key == "why":
        d.text((W/2+8, CY+10), "?", font=F("anton", 360), fill=(0,0,0), anchor="mm")
        d.text((W/2, CY), "?", font=F("anton", 360), fill=tuple(int(LIME[i]*clamp(p)) for i in range(3)), anchor="mm")
    elif key == "friction":
        items = (("brief", "JOB", 6.0), ("house", "FAMILY", 6.75), ("coins", "MONEY", 7.45), ("storm", "STRESS", 8.0))
        for i, (sp, lab, ts) in enumerate(items):
            x = W/2 + (-195 if i % 2 == 0 else 195); y = CY - 170 + (i//2)*340
            a = back((t-ts+0.35)/0.35)
            put(cv, sp, x, y, 0.9*a)
            if a > 0.5: d.text((x, y+165), lab, font=F("anton", 48), fill=GREY, anchor="mm")
    elif key == "quit":
        put(cv, "dish", W/2, CY+bob, 1.15*p)
        put(cv, "quit", W/2, CY+220, pop(0.3))
    elif key == "dietx":
        put(cv, "diet_x", W/2, CY, 2.0*p)
        put(cv, "cross", W/2, CY, 1.3*pop(0.25))
    elif key == "dish":
        put(cv, "dish", W/2, CY+bob, 1.2*p)
        put(cv, "check", W/2+250, CY-150, 0.85*pop(0.4))
        d.text((W/2, CY+220), "MEALS PLANNED FOR YOU", font=F("anton", 56), fill=LIME, anchor="mm")
    elif key == "lock":
        put(cv, "lock", W/2, CY, 1.1*p*(1+0.03*math.sin(t*7)))
    elif key == "title":
        put(cv, "idcard", W/2, CY+bob, 1.25*p)
    elif key == "salary":
        put(cv, "notes", W/2, CY+bob, 1.3*p)
    elif key == "stable":
        put(cv, "house", W/2, CY+bob, 1.2*p)
    elif key == "health":
        put(cv, "heart", W/2, CY, 1.2*p*(1+0.05*abs(math.sin(t*4))))
        d.text((W/2+200, CY-190), "?", font=F("anton", 140), fill=CORAL, anchor="mm")
    elif key == "more":
        put(cv, "heart_g", W/2-170, CY-20, 1.0*p*(1+0.05*abs(math.sin(t*4))))
        put(cv, "coins", W/2+190, CY+20, 0.7*pop(0.2))
        d.text((W/2+15, CY), ">", font=F("anton", 150), fill=LIME, anchor="mm")
    elif key == "without":
        put(cv, "heart_x", W/2, CY, 1.2*p)
    elif key == "apart":
        fall = clamp((t-t0)/1.4)
        for i, (sp, dx) in enumerate((("idcard",-230),("notes",230),("house",0))):
            y = CY - 120 + (i==2)*200 + fall**2*500*(0.6+0.25*i)
            ang_a = 1 - clamp(fall*1.2)
            put(cv, sp, W/2+dx, y, 0.6, max(0.0, ang_a))
    elif key == "gym":
        put(cv, "dumbbell", W/2, CY+bob, 1.2*p)
    elif key == "eat":
        put(cv, "salad", W/2, CY+bob, 1.5*p)
    elif key == "cook":
        put(cv, "clock", W/2, CY, 1.05*p)
    elif key == "cta":
        a = clamp((t-t0)/0.3); fb = F("black", 150)
        tw = d.textlength("FitEats", font=fb)
        d.text((W/2+6, CY-210+8), "FitEats", font=fb, fill=(0,0,0), anchor="mm")
        d.text((W/2, CY-210), "FitEats", font=fb, fill=tuple(int(BG[i]+(TXT[i]-BG[i])*a) for i in range(3)), anchor="mm")
        d.ellipse((W/2+tw/2+6, CY-190, W/2+tw/2+40, CY-156), fill=LIME)
        d.text((W/2, CY-100), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 30), fill=GREY, anchor="mm")
        put(cv, "wa", W/2, CY+50, back((t-t0-0.3)/0.4)*(1+0.035*math.sin(t*6)))
        put(cv, "bio", W/2, CY+210, back((t-t0-0.6)/0.4))

def frame(cfg, t):
    SC = cfg["sc"]; TOTAL = cfg["total"]
    i = max(j for j, s in enumerate(SC) if s[0] <= t); s0, markup, glow, key = SC[i]
    cv = bg(GLOW[glow]).copy(); d = ImageDraw.Draw(cv)
    d.rounded_rectangle((60, 214, W-60, 224), 5, fill=(49,53,57))
    d.rounded_rectangle((60, 214, 60+(W-120)*clamp(t/TOTAL), 224), 5, fill=LIME)
    d.rounded_rectangle((60, 254, 380, 312), 29, fill=LIME)
    d.text((220, 284), cfg["tag"], font=F("bold", 30), fill=INK, anchor="mm")
    sc = 0.9 + 0.1*back((t-s0)/0.22) if s0 > 0 else 1.0
    him = headline_scaled(markup, round(sc, 2))
    cv.alpha_composite(him, (int((W-him.width)/2), int(640-him.height/2+40)))
    draw(cv, d, key, t, s0)
    return cv.convert("RGB")

def main():
    cfg = S1 if sys.argv[1] == "s1" else S2
    build()
    if sys.argv[2] == "stills":
        for s in sys.argv[3:]: frame(cfg, float(s)).save(f"{sys.argv[1]}_{s}.png")
        return
    out = f"{sys.argv[1]}_video.mp4"
    p = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                          "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p",out], stdin=subprocess.PIPE)
    for i in range(int(cfg["total"]*FPS)): p.stdin.write(frame(cfg, i/FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
