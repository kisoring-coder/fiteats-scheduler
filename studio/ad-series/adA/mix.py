import json, subprocess, sys, numpy as np, os
ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 44100
sys.argv += []
DUR = 24.3

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def save(a, path):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", path], input=a.astype(np.float32).tobytes())

# ---- music: loop 4 beats of the drop so the final hit lands after the CTA, shift +0.10s
m = load(f"{ROOT}/music_raw.mp3")
def S(t): return int(t * SR)
DROP, BEAT = 17.15, 0.55
a = m[:S(DROP + 4 * BEAT)]; b = m[S(DROP):]
xf = S(0.02); ramp = np.linspace(0, 1, xf)[:, None]
a[-xf:] = a[-xf:] * (1 - ramp) + b[:xf] * ramp
mus = np.concatenate([np.zeros((S(0.10), 2), np.float32), a, b[xf:]])
mus = mus[:S(DUR)]
if len(mus) < S(DUR): mus = np.concatenate([mus, np.zeros((S(DUR) - len(mus), 2), np.float32)])

# ---- sfx (synthesised): whoosh on graphic cuts, pop on chips, low boom on section changes
rng = np.random.default_rng(7)
sfx = np.zeros((S(DUR), 2), np.float32)
def place(sig, t, g):
    i = S(t); n = min(len(sig), len(sfx) - i)
    if n > 0: sfx[i:i + n] += g * np.repeat(sig[:n, None], 2, 1)
def whoosh(d=0.32):
    n = S(d); x = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    # crude band sweep: mix of two lowpassed versions
    y = np.convolve(x, np.ones(18) / 18, 'same') - np.convolve(x, np.ones(90) / 90, 'same')
    return (y * env * 3.0).astype(np.float32)
def pop(f=900, d=0.09):
    t = np.arange(S(d)) / SR; fr = f * (1 + 1.5 * np.exp(-t * 40))
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 38)).astype(np.float32)
def boom(d=0.6):
    t = np.arange(S(d)) / SR; fr = 70 * np.exp(-t * 3) + 40
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 6)).astype(np.float32)

sys.path.insert(0, ROOT)
cuts = json.loads(subprocess.run([sys.executable, f"{ROOT}/build.py", "cuts"], capture_output=True, text=True).stdout)
for t0, prop, punch in cuts:
    if punch and t0 > 0 and prop not in (97, 98): place(whoosh(), max(0, t0 - 0.12), 0.35)
words = [w for w in json.load(open(f"{ROOT}/words.json"))['words'] if w.get('type', 'word') == 'word']
WS = [w['start'] for w in words]
for i in (5, 10, 15, 23, 48, 50, 53): place(pop(1100 if i >= 48 else 760), WS[i], 0.28)
place(boom(), 7.15, 0.55); place(boom(), 11.85, 0.4)
save(sfx, f"{ROOT}/sfx.wav"); save(mus, f"{ROOT}/mus.wav")
