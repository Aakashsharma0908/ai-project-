#!/usr/bin/env python3
"""Pace pass: decide in/out points for every clip from measured speech timing.

Usage: make_trims.py <timing.json> <clips_dir> <out trims.json>

Retention rule of thumb: never let the screen sit idle. But a reaction after a line is often the
real moment (Maa's silence, Riya's nod), so tails are only shortened, never removed:
 - head: if speech starts after 3.0 s, start 1.5 s before it
 - tail: keep 2.5 s after the last word (4.0 s where the script asks for a reaction)
 - never shorter than 6 s; silent / purely visual clips stay whole
"""
import json, subprocess, sys

SEG = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
SRC, OUT = sys.argv[2], sys.argv[3]
WHOLE = {1, 2, 3, 4, 6, 13, 15, 19, 22, 25, 27, 29, 30, 31, 32, 35, 37, 38, 40, 41, 44, 45, 46, 47, 48}  # key visual beats
REACTION = {8, 12, 16, 17, 19, 20, 24, 25, 26, 27, 28, 32, 33, 36, 38, 39, 42, 43}  # script: a beat after the line

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)

trims, saved = {}, 0.0
for i in range(1, 49):
    full = dur(f"{SRC}/c{i:02d}.mp4"); segs = SEG.get(i, [])
    if i in WHOLE or not segs:
        trims[i] = [0.0, round(full, 3)]; continue
    first, last = segs[0][0], segs[-1][1]
    tin = first - 1.5 if first > 3.0 else 0.0
    tout = min(full, last + (4.0 if i in REACTION else 2.5))
    if tout - tin < 6.0:
        tout = min(full, tin + 6.0); tin = max(0.0, tout - 6.0)
    trims[i] = [round(tin, 3), round(tout, 3)]
    saved += full - (tout - tin)
    print(f"clip {i:02d}: {tin:5.2f} -> {tout:5.2f}  (cut {full - (tout - tin):4.1f} s)")
json.dump(trims, open(OUT, "w"), indent=1)
print(f"total cut {saved:.1f} s")
