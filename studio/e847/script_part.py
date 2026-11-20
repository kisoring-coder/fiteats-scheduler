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
