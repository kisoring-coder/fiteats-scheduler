"""FitEats reel: 'Wake up tired, back hurts' (27 Nov). Reality Check style, b2 engine."""
import math, subprocess, sys
from PIL import Image, ImageDraw
import b2
from b2 import (W, H, FPS, BG, TXT, GREY, DARK, LIME, CORAL, OUT, INK, F, clamp, ease, back, sprite, vgrad,
                shape_mask, put, SP, bg, GLOW, headline_scaled)
import build_emo as E
import bf3

TOTAL = 21.6
SC = [
 (0.00, "YOU WAKE UP [TIRED]", "red", "tired"),
 (1.31, "AND YOUR [BACK HURTS]", "red", "back"),
 (2.40, "AFTER [HOURS OF SITTING]", "red", "sit"),
 (3.95, "{RIGHT?}", "neutral", "why"),
 (4.84, "YOU CAN'T FIX [YOUR JOB]", "red", "job"),
 (6.46, "BUT YOU CAN FIX {YOUR BODY}", "lime", "body"),
 (8.60, "{STRENGTH TRAINING}", "lime", "train"),
 (9.40, "+ A {PROTEIN-RICH DIET}", "lime", "protein"),
 (11.30, "EASE {STIFFNESS & PAIN}", "lime", "ease"),
 (14.08, "YOU {TRAIN}", "lime", "youtrain"),
 (15.88, "WE BRING {HIGH-PROTEIN MEALS}", "lime", "meals"),
 (19.04, "TAP {LINK IN BIO}", "lime", "cta"),
]
CY = 1180

def spine(col, w=220, h=560):
    def fn(d, k, im):
        d.line([(w/2*k, 20*k), (w/2*k, (h-20)*k)], fill=(70,74,84,255), width=int(14*k))
        n = 9
        for i in range(n):
            y = 40 + i*(h-80)/n; vw = 110 + i*8
            box = ((w/2-vw/2)*k, y*k, (w/2+vw/2)*k, (y+(h-80)/n-16)*k)
            m = shape_mask(im.size, lambda md, b=box: md.rounded_rectangle(b, int(16*k), fill=255))
            vgrad(im, box, (244,238,226), (206,196,178), m)
            d.rounded_rectangle(box, int(16*k), outline=OUT+(255,), width=int(5*k))
            if i < n-1:
                dy = y + (h-80)/n - 13
                d.rounded_rectangle(((w/2-vw/2+14)*k, dy*k, (w/2+vw/2-14)*k, (dy+10)*k), int(5*k), fill=col+(255,))
    return sprite(w, h, fn)

def desk_person(w=640, h=520):
    def fn(d, k, im):
        d.ellipse((40*k, (h-50)*k, (w-40)*k, (h-8)*k), fill=(0,0,0,110))
        # desk + laptop
        d.rounded_rectangle((330*k, 250*k, 620*k, 280*k), int(8*k), fill=(150,104,64,255), outline=OUT+(255,), width=int(5*k))
        d.rectangle((580*k, 280*k, 600*k, (h-30)*k), fill=(110,76,46,255))
        d.polygon([(420*k, 250*k), (470*k, 130*k), (560*k, 130*k), (520*k, 250*k)], fill=(170,176,190,255), outline=OUT+(255,))
        d.ellipse((498*k, 178*k, 518*k, 198*k), fill=(230,232,238,255))
        # chair
        d.rounded_rectangle((70*k, 300*k, 280*k, 336*k), int(12*k), fill=(52,56,66,255), outline=OUT+(255,), width=int(5*k))
        d.rounded_rectangle((60*k, 120*k, 96*k, 330*k), int(14*k), fill=(52,56,66,255), outline=OUT+(255,), width=int(5*k))
        d.line([(175*k, 336*k), (175*k, (h-50)*k)], fill=(52,56,66,255), width=int(14*k))
        d.line([(100*k, (h-46)*k), (250*k, (h-46)*k)], fill=(52,56,66,255), width=int(12*k))
        # hunched person
        skin = (214,160,120,255); shirt = (90,120,180,255)
        d.line([(160*k, 300*k), (150*k, 200*k), (200*k, 130*k), (270*k, 110*k)], fill=shirt, width=int(54*k), joint="curve")
        d.line([(225*k, 150*k), (330*k, 210*k), (440*k, 240*k)], fill=shirt, width=int(30*k), joint="curve")
        d.line([(160*k, 310*k), (330*k, 310*k), (340*k, (h-60)*k)], fill=(50,54,70,255), width=int(40*k), joint="curve")
        d.ellipse((262*k, 52*k, 352*k, 142*k), fill=skin, outline=OUT+(255,), width=int(5*k))
    return sprite(w, h, fn)

def pain(size=260):
    def fn(d, k, im):
        c = size/2
        for r, a in ((120, 60), (90, 110), (60, 180)):
            d.ellipse(((c-r)*k, (c-r)*k, (c+r)*k, (c+r)*k), fill=CORAL+(a,))
        for ang in range(0, 360, 45):
            x1 = c + 70*math.cos(math.radians(ang)); y1 = c + 70*math.sin(math.radians(ang))
            x2 = c + 118*math.cos(math.radians(ang)); y2 = c + 118*math.sin(math.radians(ang))
            d.line([(x1*k, y1*k), (x2*k, y2*k)], fill=(255,214,60,255), width=int(9*k))
    return sprite(size, size, fn)

def protein_bowl():
    return b2.bowl((238,214,170), (206,176,126), [((176,104,48), 22, 9), ((120,180,80), 12, 8), ((250,210,90), 10, 5)])

def build():
    b2.build_sprites()
    E.build()
    SP.update(spine_r=spine(CORAL), spine_g=spine(LIME), desk=desk_person(), pain=pain(), pbowl=protein_bowl(),
              bat_low=bf3.battery(0.12), egg=bf3.egg(half=True), you=b2.pill("YOU", DARK, fg=TXT, size=64),
              we=b2.pill("WE", LIME, size=64))

def draw(cv, d, key, t, t0):
    p = back((t-t0)/0.45) if t0 > 0 else back(t/0.35)
    bob = math.sin(t*2.2)*6
    def pop(dt): return back((t-t0-dt)/0.4)
    if key == "tired":
        put(cv, "bat_low", W/2, CY+bob, 1.4*p)
        for i in range(3):
            a = clamp((t - 0.3 - i*0.25)/0.3)
            if a > 0: d.text((W/2+230+i*60, CY-150-i*70), "Z", font=F("anton", 70+i*24), fill=tuple(int(GREY[j]*a) for j in range(3)), anchor="mm")
    elif key == "back":
        pulse = 1 + 0.06*abs(math.sin(t*5))
        put(cv, "pain", W/2, CY+120, 1.3*pulse*pop(0.15))
        put(cv, "spine_r", W/2, CY, 0.95*p)
    elif key == "sit":
        put(cv, "desk", W/2, CY+30, 1.15*p)
        put(cv, "pain", W/2-200, CY-20, 0.8*(1+0.08*abs(math.sin(t*5)))*pop(0.3))
        hrs = min(9, int(1 + (t-t0)*6))
        d.rounded_rectangle((W/2-150, CY+300, W/2+150, CY+400), 24, fill=DARK)
        d.text((W/2, CY+350), f"{hrs} HRS", font=F("anton", 70), fill=CORAL, anchor="mm")
    elif key == "why":
        d.text((W/2+8, CY+10), "?", font=F("anton", 360), fill=(0,0,0), anchor="mm")
        d.text((W/2, CY), "?", font=F("anton", 360), fill=tuple(int(LIME[i]*clamp(p)) for i in range(3)), anchor="mm")
    elif key == "job":
        put(cv, "brief", W/2, CY+bob, 1.3*p)
        put(cv, "cross", W/2, CY, 1.0*pop(0.35))
    elif key == "body":
        put(cv, "spine_g", W/2, CY, 0.95*p)
        put(cv, "check", W/2+230, CY-180, 0.8*pop(0.4))
    elif key == "train":
        put(cv, "dumbbell", W/2, CY+bob, 1.4*p)
    elif key == "protein":
        put(cv, "dumbbell", W/2-200, CY-170, 0.75)
        d.text((W/2, CY-40), "+", font=F("anton", 120), fill=LIME, anchor="mm")
        put(cv, "pbowl", W/2+60, CY+170+bob, 1.25*p)
        put(cv, "egg", W/2-230, CY+200, 0.8*pop(0.25))
    elif key == "ease":
        fade = clamp((t-t0)/1.6)
        put(cv, "spine_r", W/2, CY, 0.95, 1-fade)
        put(cv, "spine_g", W/2, CY, 0.95, fade)
        for i, (dx, dy) in enumerate(((-230,-200),(240,-60),(-200,200))):
            put(cv, "spark", W/2+dx, CY+dy, 0.8*pop(1.0+i*0.25)*(1+0.1*math.sin(t*6+i)))
    elif key == "youtrain":
        put(cv, "dumbbell", W/2, CY+60+bob, 1.25*p)
        put(cv, "you", W/2, CY-170, pop(0.2))
    elif key == "meals":
        put(cv, "pbowl", W/2, CY-60+bob, 1.35*p)
        put(cv, "we", W/2-260, CY-260, pop(0.15))
        days = ("MON","TUE","WED","THU","FRI","SAT")
        for i, dname in enumerate(days):
            x = W/2 - 400 + i*160; y = CY + 250
            a = clamp((t - t0 - 0.6 - i*0.28)/0.25)
            d.rounded_rectangle((x-66, y-50, x+66, y+70), 18, fill=DARK)
            d.text((x, y-20), dname, font=F("anton", 38), fill=GREY, anchor="mm")
            if a > 0: put(cv, "check", x, y+30, 0.3*back(a))
    elif key == "cta":
        a = clamp((t-t0)/0.3); fb = F("black", 150)
        tw = d.textlength("FitEats", font=fb)
        d.text((W/2+6, CY-210+8), "FitEats", font=fb, fill=(0,0,0), anchor="mm")
        d.text((W/2, CY-210), "FitEats", font=fb, fill=tuple(int(BG[i]+(TXT[i]-BG[i])*a) for i in range(3)), anchor="mm")
        d.ellipse((W/2+tw/2+6, CY-190, W/2+tw/2+40, CY-156), fill=LIME)
        d.text((W/2, CY-100), "HIGH-PROTEIN MEALS · CALORIES COUNTED · CHENNAI", font=F("bold", 30), fill=GREY, anchor="mm")
        put(cv, "bio", W/2, CY+60, back((t-t0-0.3)/0.4)*(1+0.035*math.sin(t*6)))
        put(cv, "wa", W/2, CY+240, back((t-t0-0.6)/0.4))

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
    return cv.convert("RGB")

def main():
    build()
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]: frame(float(s)).save(f"st_{s}.png")
        return
    p = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                          "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p","video.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
