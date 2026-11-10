#!/usr/bin/env python3
"""Soundtrack for the edit: original dialogue/foley + room tone + city ambience
+ a score synthesised from scratch (no third-party music, so no licensing).

Usage: make_audio.py <src_dir> <out.wav>
Timeline must match render_video.sh.
"""
import subprocess, sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
SRC, OUT = sys.argv[1], sys.argv[2]
TOTAL = 44.7
N = int(TOTAL * SR)
rng = np.random.default_rng(7)

def t2s(t): return int(round(t * SR))

def load(name, t0, t1):
    """Decode a clip's audio (cleaned: rumble cut, light denoise) as stereo float."""
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", f"{SRC}/{name}",
           "-af", "highpass=f=70,afftdn=nr=8:nf=-45,aresample=48000",
           "-ac", "2", "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def fades(x, fin, fout):
    n = len(x); e = np.ones(n)
    a, b = t2s(fin), t2s(fout)
    if a: e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if b: e[-b:] = np.cos(np.linspace(0, np.pi / 2, b)) ** 2
    return x * e[:, None]

def place(bus, x, start):
    s = t2s(start); e = min(len(bus), s + len(x))
    bus[s:e] += x[: e - s]

def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)

def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x, axis=0)

def env(points):
    """Piecewise-linear envelope over the whole timeline from (time, value) pairs."""
    ts, vs = zip(*points)
    return np.interp(np.arange(N) / SR, ts, vs)

def db(x): return 10 ** (x / 20)

# ---------------------------------------------------------------- dialogue/foley
# (clip, src in, src out, timeline start, fade in, fade out, gain dB)
SEGS = [("c1.mp4", 0.0, 10.0, 0.0,  0.8, 0.30, -2.0),
        ("c2.mp4", 1.25, 8.0, 9.75, 0.25, 0.15, 4.0),
        ("c3.mp4", 0.25, 8.25, 16.5, 0.10, 1.00, 3.0),
        ("c4.mp4", 0.0, 9.5, 23.5,  1.00, 0.80, 2.5),
        ("c5.mp4", 0.0, 10.0, 32.2, 0.80, 2.00, 0.0)]
dia = np.zeros((N, 2))
for name, a, b, start, fi, fo, g in SEGS:
    place(dia, fades(load(name, a, b), fi, fo) * db(g), start)

# Spoken lines on the timeline -> music ducks under them.
SPEECH = [(3.0, 9.2), (29.3, 31.8), (35.2, 36.0), (37.4, 38.8)]

# ---------------------------------------------------------------- reverb
def make_ir(sec=2.8, decay=3.2):
    n = t2s(sec); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-decay * t)[:, None]
    ir = lp(ir, 6000)
    ir[: t2s(0.012)] = 0          # pre-delay
    return ir / np.sqrt((ir ** 2).sum(axis=0))

IR = make_ir()
def verb(x, wet=0.35):
    w = np.stack([fftconvolve(x[:, c], IR[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + w * wet * 3.0

# ---------------------------------------------------------------- instruments
def hz(note):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6,
             "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)

def piano(f, dur=4.0, vel=0.5, pan=0.0):
    n = t2s(dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)          # slight string inharmonicity
        if fk > 12000: break
        y += (1 / k ** 1.3) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6)) * np.exp(-t * (0.9 + 0.55 * k))
    y *= np.minimum(1, t / 0.004)                         # hammer attack
    y += 0.02 * rng.standard_normal(n) * np.exp(-t * 60)  # felt thump
    y = lp(y[:, None], 4500)[:, 0] * vel
    return np.stack([y * (1 - pan) ** 0.5, y * (1 + pan) ** 0.5], 1) * 0.7

def pad(freqs, dur, att=2.0, rel=2.5, bright=900, vol=0.06):
    n = t2s(dur); t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for f in freqs:
        for c, det in enumerate((-0.0035, 0.0035)):        # detuned pair -> width
            ph = 2 * np.pi * f * (1 + det) * t
            saw = sum(np.sin(k * ph) / k for k in range(1, 7))
            out[:, c] += saw
    e = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0)
    out = sosfilt(butter(2, 110, btype='high', fs=SR, output='sos'), lp(out, bright), axis=0) * e[:, None]
    return out * vol / max(1, len(freqs) ** 0.5)

def sub(f, dur, vol=0.12):
    n = t2s(dur); t = np.arange(n) / SR
    e = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.5).clip(0)
    y = np.sin(2 * np.pi * f * t) * e * vol
    return np.stack([y, y], 1)

# ---------------------------------------------------------------- score
mus = np.zeros((N, 2))
# Harmony: (start, dur, pad voicing, bass) - D minor, resolving to D major.
CH = [
    (0.0,  6.0, ["D3", "A3", "E4", "F4"], "D2"),      # Dm(add9): alone, awake
    (5.5,  5.0, ["Bb2", "F3", "A3", "D4"], "Bb1"),    # Bbmaj7
    (10.0, 3.5, ["F3", "A3", "C4", "E4"], "F2"),      # Fmaj7: he gets up
    (13.2, 3.6, ["G3", "Bb3", "D4", "F4"], "G2"),     # Gm7
    (16.5, 4.6, ["A2", "D3", "E3", "A3"], "A1"),      # Asus4 -> tension at the window
    (20.9, 4.6, ["D3", "A3", "D4", "F4", "A4"], "D2"),# Dm: the street opens up
    (25.2, 2.8, ["Bb2", "F3", "D4", "A4"], "Bb1"),    # warmth as he smiles
    (27.8, 2.8, ["F3", "C4", "F4", "A4"], "F2"),
    (30.4, 2.8, ["C3", "G3", "E4", "G4"], "C2"),
    (33.0, 2.6, ["D3", "A3", "F4", "A4"], "D2"),
    (35.5, 2.7, ["Bb2", "F3", "D4", "G4"], "Bb1"),
    (38.0, 2.3, ["A2", "E3", "A3", "C#4"], "A1"),     # looks down: A major (dominant)
    (40.1, 4.6, ["D3", "A3", "D4", "F#4", "A4"], "D2"),  # Picardy D major: quiet resolution
]
for st, du, voice, bass in CH:
    bright = 700 if st < 20 else 1300
    place(mus, pad([hz(n) for n in voice], du + 1.5, att=1.4, rel=1.6, bright=bright), st)
    place(mus, sub(hz(bass), du + 1.0, vol=0.03 if st < 16 else 0.045), st)

# Piano: sparse at first, a small melody once he smiles, a last phrase to close.
MEL = [(1.2, "A4", .30), (2.8, "F4", .22), (4.6, "E4", .20), (7.0, "D4", .18),
       (10.2, "C5", .28), (11.7, "A4", .24), (13.4, "Bb4", .26), (15.0, "F4", .22),
       (17.0, "E4", .25), (18.4, "D4", .22), (19.6, "E4", .25),
       (21.0, "D5", .32), (21.0, "A4", .22), (22.6, "F5", .22), (24.0, "E5", .20),
       (25.3, "F5", .30), (26.1, "D5", .22), (26.9, "C5", .22), (27.9, "A4", .30),
       (28.8, "C5", .22), (30.5, "G4", .20), (32.0, "E4", .18),
       (33.1, "F4", .26), (34.4, "A4", .24), (35.6, "D5", .22), (36.8, "Bb4", .20),
       (38.1, "C#5", .24), (39.2, "E4", .2),
       (40.2, "D4", .30), (40.2, "F#4", .22), (40.9, "A4", .24), (41.8, "D5", .26)]
for i, (st, note, v) in enumerate(MEL):
    place(mus, piano(hz(note), dur=4.5, vel=v, pan=((i % 5) - 2) * 0.12), st)

# Riser into the street reveal (filtered noise + rising tone), then a soft low hit.
r0, r1 = 18.6, 20.9
n = t2s(r1 - r0); t = np.arange(n) / SR; p = t / (r1 - r0)
noise = rng.standard_normal((n, 2))
riser = np.zeros((n, 2))
for c in range(2):  # sweep a band-pass up through the noise in 8 chunks
    chunks = np.array_split(np.arange(n), 8)
    for j, idx in enumerate(chunks):
        lo = 300 * 2 ** (j * 0.5); riser[idx, c] = bp(noise[:, c], lo, lo * 2.5)[idx]
tone = np.sin(2 * np.pi * np.cumsum(220 + 220 * p ** 2) / SR)
riser = (riser * 0.05 + tone[:, None] * 0.015) * (p ** 2.2)[:, None]
place(mus, riser, r0)
n = t2s(3.0); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t * 3) + 38) / SR) * np.exp(-t * 2.2) * 0.22
boom += lp(rng.standard_normal(n)[:, None], 180)[:, 0] * np.exp(-t * 8) * 0.15
place(mus, np.stack([boom, boom], 1), 20.9)

mus = verb(mus, wet=0.45)

# Music level: present in the gaps, ducked ~10 dB under dialogue, swells for the smile.
base = env([(0, -8), (9.7, -8), (16.5, -6), (21, -4), (25, -3), (33, -4), (38, -5), (44.7, -5)])
duck = np.zeros(N); tt = np.arange(N) / SR
for a, b in SPEECH:
    duck = np.minimum(duck, np.interp(tt, [a - 0.4, a, b, b + 0.6], [0, -15, -15, 0], left=0, right=0))
mus *= db(base + duck)[:, None]

# ---------------------------------------------------------------- ambience
amb = np.zeros((N, 2))
room = lp(rng.standard_normal((N, 2)), 220, 4) * 0.05          # quiet bedroom air
amb += room * env([(0, 0), (1.5, 1), (16.5, 1), (20, 0.5), (44.7, 0.5)])[:, None]
city = bp(rng.standard_normal((N, 2)), 60, 700) * 0.05          # distant city at the window
amb += city * env([(0, 0.15), (15.5, 0.2), (19.5, 0.8), (22.5, 1.0), (33, 0.8), (40, 0.6), (44.7, 0)])[:, None]
for c0, dur, d in [(21.5, 6.0, 1), (34.0, 5.5, -1)]:            # far-off cars passing by
    n = t2s(dur); t = np.arange(n) / SR; x = bp(rng.standard_normal(n), 120, 1400)
    bell = np.sin(np.pi * t / dur) ** 3 * 0.05
    pan = np.linspace(-0.8, 0.8, n) * d
    place(amb, np.stack([x * bell * (1 - pan) / 2, x * bell * (1 + pan) / 2], 1) * 1.6, c0)

# ---------------------------------------------------------------- mix
mix = dia + mus + amb
mix *= env([(0, 0), (0.05, 1), (42.2, 1), (44.7, 0)])[:, None]   # tail fades with the picture
mix /= max(1e-9, np.abs(mix).max()) / 0.7
pcm = np.clip(mix, -1, 1).astype(np.float32)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-c:a", "pcm_f32le", OUT], input=pcm.tobytes(), check=True)
print("wrote", OUT, f"{len(pcm)/SR:.2f}s")
