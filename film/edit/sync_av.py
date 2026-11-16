#!/usr/bin/env python3
"""Lock every clip's audio to its picture length (frame-accurate) and rewrite timeline.json.

Usage: sync_av.py <work_dir>
Some generated clips carry a video stream of 10.00 s but audio of 10.24 s; over 48 clips that
difference would add up to more than a second of lip-sync drift. The picture is the master:
each aNN.wav is padded/cut to exactly the duration of vNN.mp4, and the timeline (used by the
score and the subtitles) is rebuilt from the real picture lengths.
"""
import json, subprocess, sys
from pathlib import Path

W = Path(sys.argv[1])

def vdur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                          "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True).stdout
    return int(out.strip().split(",")[0]) / 24.0

tl = json.loads((W / "timeline.json").read_text()); t0 = 0.0
for c in tl:
    i = c["clip"]; d = vdur(W / f"v{i:02d}.mp4")
    a, tmp = W / f"a{i:02d}.wav", W / f"a{i:02d}.sync.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(a), "-af", "apad", "-t", f"{d:.6f}",
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(tmp)], check=True)
    tmp.replace(a)
    if abs(d - c["dur"]) > 0.02:
        print(f"clip {i:02d}: {c['dur']:.3f} -> {d:.3f}")
    c["dur"], c["start"] = round(d, 6), round(t0, 6); t0 += d
(W / "timeline.json").write_text(json.dumps(tl, indent=1))
print("picture-locked timeline:", round(t0, 3), "s")
