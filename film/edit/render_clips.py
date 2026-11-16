#!/usr/bin/env python3
"""Stage 1: render each of the 48 clips (grade, fixes, transitions, cleaned audio).

Usage: render_clips.py <clips_dir with c01.mp4..c48.mp4> <work_dir> [trims.json]
trims.json maps clip number -> [in, out] seconds (dead air removed for pace).
Writes work_dir/vNN.mp4 (picture, 1920x1080, 24 fps) and work_dir/aNN.wav (dialogue/foley),
plus work_dir/timeline.json with each clip's start time and duration.

Director's rules applied here
- Two worlds: the courtroom inside Riya's mind is shown letterboxed (scope bars) with a cold
  teal grade and a reverberant "inside the head" sound; real life is full frame, dry and warm.
  The bars slide in when she wakes in the courtroom (clip 4) and slide away when she wakes up
  for real (clip 41) - the frame itself "opens up" when she forgives herself.
- Courtroom cuts are hard cuts; Maa's scenes breathe with slow fades (editing note 6).
- Clip 17 plays as a courtroom flashback: drained colour, heavy vignette, white flash in/out,
  echo on the voice (editing note 2).
- Clip 30's English line is muted (editing note 3); clip 37's unscripted mumble is pulled down.
- Clip 35 is a 1990s sepia memory with grain and gate weave.
- Clip 40 burns to white and clip 41 rises out of white: the verdict becomes the morning.
"""
import json, os, subprocess, sys
from pathlib import Path

SRC, W = Path(sys.argv[1]), Path(sys.argv[2])
DUST = Path(__file__).with_name("dust.mp4")  # VFX plate, made by dust.py if missing
# Dust motes were tried and dropped after review: on phone screens they read as white specks.
USE_DUST = os.environ.get("DUST") == "1"
if USE_DUST and not DUST.exists():
    subprocess.run([sys.executable, str(Path(__file__).with_name("dust.py")), str(DUST), "10.5"], check=True)
TRIM = {int(k): v for k, v in json.loads(Path(sys.argv[3]).read_text()).items()} if len(sys.argv) > 3 else {}
W.mkdir(parents=True, exist_ok=True)

COURT = {4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20, 21, 23, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40}
WARM = {1, 2, 3, 7, 9, 11, 13, 19, 22, 24, 25, 26}
GOLD = set(range(41, 49))

LOOK = {
    "court": "colorbalance=rs=-0.05:gs=-0.01:bs=0.05:rm=-0.02:bm=0.02:rh=0.02:bh=-0.02,"
             "eq=saturation=0.86:contrast=1.06:gamma=0.98",
    "warm": "colortemperature=temperature=5200:mix=0.30,eq=saturation=1.05:contrast=1.04",
    "gold": "colortemperature=temperature=4700:mix=0.35,eq=saturation=1.08:contrast=1.03:gamma=1.03",
    "flash": "hue=s=0.40,colorbalance=bs=0.07:bm=0.03,eq=contrast=1.10:brightness=-0.03,vignette=PI/3.2",
    "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,"
             "eq=contrast=1.06:brightness=-0.02,vignette=PI/3.4,"
             "crop=iw-12:ih-12:6+3*sin(t*7):6+3*cos(t*5),scale=1920:1080,noise=alls=16:allf=t",
}
BAR = 64  # px top and bottom in the mind-courtroom (about 2:1 framing)

# clip: (fade_in s, fade_in colour, fade_out s, fade_out colour)
FADES = {
    1: (2.5, "black", 0, None), 3: (0, None, 1.5, "black"), 4: (1.5, "black", 0, None),
    11: (0.8, "black", 0.8, "black"), 17: (0.3, "white", 0.3, "white"),
    19: (0.8, "black", 0.8, "black"), 22: (0.8, "black", 0.8, "black"),
    25: (0.8, "black", 0.8, "black"), 26: (0.8, "black", 0.8, "black"),
    35: (0.8, "black", 0.8, "black"), 40: (0, None, 1.2, "white"), 41: (1.5, "white", 0, None),
    43: (0.8, "black", 0.8, "black"), 48: (0, None, 3.0, "black"),
}

def dur(f):  # picture length (some sources carry audio that runs past the last frame)
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)

def run(cmd):
    subprocess.run(cmd, check=True)

timeline, t0 = [], 0.0
ONLY = {int(x) for x in os.environ.get("ONLY", "").split(",") if x}  # re-render just these clips
old = {c["clip"]: c for c in json.loads((W / "timeline.json").read_text())} if ONLY and (W / "timeline.json").exists() else {}
for i in range(1, 49):
    if ONLY and i not in ONLY and i in old:
        timeline.append(old[i]); continue
    f = SRC / f"c{i:02d}.mp4"
    full = round(dur(f), 3)
    tin, tout = TRIM.get(i, [0.0, full])
    tout = min(tout, full); d = round(tout - tin, 3)
    cut = ["-ss", f"{tin:.3f}", "-t", f"{d:.3f}"]
    look = ("court" if i in COURT else "flash" if i == 17 else "sepia" if i == 35
            else "gold" if i in GOLD else "warm")
    v = ["scale=1920:1080:flags=lanczos", "fps=24", LOOK[look]]
    if look != "sepia":
        v.append("noise=alls=5:allf=t")
    v.append("unsharp=5:5:0.3:5:5:0")
    # VFX: dust motes drifting in the courtroom light; soft bloom on the golden morning
    if i in COURT and USE_DUST:
        pre = ",".join(v) + "[base];[1:v]format=gbrp[dust];[base]format=gbrp[b];" \
              "[b][dust]blend=all_mode=screen:all_opacity=0.40:shortest=1"
        v = [pre]
    elif i in GOLD:
        pre = ",".join(v) + ",format=gbrp,split[b][g];[g]gblur=sigma=28,eq=brightness=-0.06[gl];" \
              "[b][gl]blend=all_mode=screen:all_opacity=0.22"
        v = [pre]
    if i in COURT:
        h = f"'max(1,min(1,t/2)*{BAR})'" if i == 4 else str(BAR)  # drawbox h=0 means full frame
        v += [f"drawbox=x=0:y=0:w=iw:h={h}:color=black:t=fill",
              f"drawbox=x=0:y=ih-{BAR}:w=iw:h={BAR}:color=black:t=fill"]
    if i == 41:  # bars open up as she wakes
        h = f"'max(1,(1-t/2.5)*{BAR})'"  # drawbox h=0 would mean full frame, so clamp and switch off
        v += [f"drawbox=x=0:y=0:w=iw:h={h}:color=black:t=fill:enable='lt(t,2.5)'",
              f"drawbox=x=0:y=ih-{h}:w=iw:h={h}:color=black:t=fill:enable='lt(t,2.5)'"]
    fi, fic, fo, foc = FADES.get(i, (0, None, 0, None))
    if fi: v.append(f"fade=t=in:st=0:d={fi}:color={fic}")
    if fo: v.append(f"fade=t=out:st={d - fo:.3f}:d={fo}:color={foc}")
    v.append("format=yuv420p")
    dust_in = ["-stream_loop", "-1", "-i", str(DUST)] if i in COURT and USE_DUST else []
    run(["ffmpeg", "-y", "-v", "error", *cut, "-i", str(f), *dust_in, "-filter_complex", "[0:v]" + ",".join(v), "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-t", str(d), str(W / f"v{i:02d}.mp4")])

    a = ["aresample=48000", "highpass=f=60", "loudnorm=I=-20:TP=-3:LRA=9", "aresample=48000"]
    if i in COURT:
        a.append("aecho=0.85:0.6:45|90:0.18|0.10")
    if i == 17:
        a += ["highpass=f=180", "lowpass=f=6000", "aecho=0.8:0.7:110|230:0.30|0.18"]
    if i == 30:
        a.append("volume=0")
    if i == 37:
        a.append("volume=-9dB")
    if fi: a.append(f"afade=t=in:st=0:d={min(fi, 1.0)}")
    if fo: a.append(f"afade=t=out:st={d - fo:.3f}:d={fo}")
    a += ["apad", f"atrim=0:{d}"]
    run(["ffmpeg", "-y", "-v", "error", *cut, "-i", str(f), "-af", ",".join(a), "-ac", "2",
         "-c:a", "pcm_s16le", str(W / f"a{i:02d}.wav")])
    timeline.append({"clip": i, "start": round(t0, 3), "dur": d, "in": tin, "look": look})
    t0 += d
    print(f"clip {i:02d} {look:6s} start {timeline[-1]['start']:7.2f}", flush=True)

(W / "timeline.json").write_text(json.dumps(timeline, indent=1))
print("total", round(t0, 2))
