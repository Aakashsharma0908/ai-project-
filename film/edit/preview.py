#!/usr/bin/env python3
"""Fast low-res review cut of an EDL (story check before the full-quality build).

Usage: preview.py <clips_dir> <uploads_dir> <trims.json> <timing.json> <timing_extra.json> <out.mp4>
960x540, quick encode, dialogue only (no score), burned Hindi subtitles, name cards,
and a labelled black card for every clip that has not been delivered yet.
"""
import glob, json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from v2_edl import SHOTS, TODO_TITLES

CLIPS, UPL, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[6]
TRIM = {int(k): v for k, v in json.load(open(sys.argv[3])).items()}
TIM = {**{f"old:{k}": v for k, v in json.load(open(sys.argv[4])).items()},
       **{f"up:{k}": v for k, v in json.load(open(sys.argv[5])).items()}}
FONT = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
W, H = 960, 540
LOOK = {"W": "colortemperature=temperature=5200:mix=0.3",
        "C": "colorbalance=rs=-0.05:bs=0.05,eq=saturation=0.86:contrast=1.06,"
             "drawbox=x=0:y=0:w=iw:h=32:color=black:t=fill,drawbox=x=0:y=ih-32:w=iw:h=32:color=black:t=fill",
        "M": "hue=s=0.35,colorbalance=bs=0.08:bm=0.04,eq=contrast=1.08,vignette=PI/3.5",
        "S": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,vignette=PI/3.5",
        "G": "colortemperature=temperature=4700:mix=0.35,eq=saturation=1.08"}
tmp = Path(tempfile.mkdtemp())

def png(path, text, size, y, box=False, color=(255, 255, 255)):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > W - 80 and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    for k, ln in enumerate(lines):
        tw = d.textlength(ln, font=f); x = (W - tw) / 2; yy = y + k * int(size * 1.35)
        if box: d.rectangle([x - 14, yy - 4, x + tw + 14, yy + size * 1.3], fill=(0, 0, 0, 150))
        d.text((x, yy), ln, font=f, fill=color + (255,), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(path)

def src_of(s):
    if s.startswith("old:"): return CLIPS / f"c{int(s[4:]):02d}.mp4"
    return Path(glob.glob(str(UPL / f"{s[3:]}-*.mp4"))[0])

def vdur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                                 "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)

parts = []
for n, shot in enumerate(SHOTS):
    label, src, tin, tout, look, subs, card = shot[:7]; audio = shot[7] if len(shot) > 7 else {}
    out = tmp / f"s{n:03d}.mkv"
    if src.startswith("todo:"):
        x = src[5:]
        png(tmp / "todo.png", f"[ नई क्लिप {x} — {TODO_TITLES[x]} ]", 34, 210, color=(255, 214, 0))
        png(tmp / "todo2.png", "  /  ".join(subs), 26, 300)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r=24:d=4",
                        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-i", str(tmp / "todo.png"), "-i", str(tmp / "todo2.png"),
                        "-filter_complex", "[0][2]overlay[a];[a][3]overlay,format=yuv420p[v]", "-map", "[v]", "-map", "1:a",
                        "-t", "4", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-c:a", "pcm_s16le", str(out)], check=True)
        parts.append(out); continue
    f = src_of(src); full = vdur(f)
    if tin is None and tout is None and src.startswith("old:"):
        tin, tout = TRIM.get(int(src[4:]), [0, full])
    tin = tin or 0.0; tout = min(tout or full, full); d = tout - tin
    # subtitles: spread the script lines over the measured speech span inside [tin, tout]
    segs = [(s, e) for s, e, _ in TIM.get(src, []) if e > tin and s < tout]
    inputs, chain, k = ["-ss", f"{tin:.3f}", "-t", f"{d:.3f}", "-i", str(f)], f"[0:v]scale={W}:{H},fps=24,{LOOK[look]}[v0]", 1
    if subs:
        a = max(segs[0][0], tin) - tin if segs else 0.5; b = min(segs[-1][1], tout) - tin if segs else d - 0.5
        if len(segs) == len(subs): spans = [(max(s, tin) - tin, min(e, tout) - tin) for s, e in segs]
        else:
            tot = sum(len(s) for s in subs); spans, t = [], a
            for s in subs: L = (b - a) * len(s) / tot; spans.append((t, t + L)); t += L
        for (s0, e0), text in zip(spans, subs):
            p = tmp / f"sub{n}_{k}.png"; png(p, text, 26, H - 92, box=True)
            inputs += ["-i", str(p)]
            chain += f";[v{k-1}][{k}:v]overlay=0:0:enable='between(t,{s0:.2f},{max(e0, s0 + 1.2) + 0.3:.2f})'[v{k}]"; k += 1
    if card:
        p = tmp / f"card{n}.png"; png(p, card, 28, 44, box=True, color=(255, 214, 0)); inputs += ["-i", str(p)]
        chain += f";[v{k-1}][{k}:v]overlay=0:0:enable='between(t,0.3,3.8)'[v{k}]"; k += 1
    af = "aresample=48000,loudnorm=I=-18:TP=-2"
    if audio.get("mute"): af += ",volume=0"
    if audio.get("gain"): af += f",volume={audio['gain']}dB"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", chain + f";[v{k-1}]format=yuv420p[vo]",
                    "-map", "[vo]", "-map", "0:a", "-af", af + ",aresample=48000,apad", "-t", f"{d:.3f}",
                    "-ar", "48000", "-ac", "2", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                    "-c:a", "pcm_s16le", str(out)], check=True)
    parts.append(out); print(label, src, f"{d:.1f}s", flush=True)

(tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", OUT], check=True)
print("preview:", OUT)
