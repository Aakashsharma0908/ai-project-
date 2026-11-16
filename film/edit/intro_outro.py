#!/usr/bin/env python3
"""Title card (after the cold open) and YouTube end screen.

Usage: intro_outro.py <clips_dir> <work_dir> <title_s> <outro_s>
Writes work_dir/vT.mp4 (title card) and work_dir/vZ.mp4 (end screen), silent; the score plays under both.

Title: the film's name glowing out of a dark, blurred courtroom (the world we are about to enter).
End screen: the last sunset, slowed and softened, with one closing line at the top. The middle and
lower part of the frame is left clear for YouTube's end-screen elements (subscribe + next video).
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, W = Path(sys.argv[1]), Path(sys.argv[2]); TD, OD = float(sys.argv[3]), float(sys.argv[4])
SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf"
CREAM, GOLD = (238, 230, 214), (214, 176, 110)

def text_png(path, lines, glow, ornament=None):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for text, font, size, y, col in lines:
        f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
        w = d.textlength(text, font=f)
        d.text(((1920 - w) / 2, y), text, font=f, fill=col + (255,))
    if ornament:  # thin gold rule with a small diamond under the title
        y = ornament; d.line([(760, y), (935, y)], fill=GOLD + (255,), width=2)
        d.line([(985, y), (1160, y)], fill=GOLD + (255,), width=2)
        d.polygon([(960, y - 9), (969, y), (960, y + 9), (951, y)], fill=GOLD + (255,))
    halo = img.filter(ImageFilter.GaussianBlur(glow))
    out = Image.alpha_composite(halo, img)
    out.save(path)

def frame(src, t, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(src), "-frames:v", "1",
                    "-vf", "scale=1920:1080", str(out)], check=True)

# ---- title card
text_png(W / "title.png", [
    ("अंदर की अदालत", SERIF, 150, 400, CREAM),
], glow=14, ornament=640)
frame(SRC / "c30.mp4", 8.5, W / "title_bg.png")
subprocess.run(["ffmpeg", "-y", "-v", "error",
    "-loop", "1", "-t", str(TD), "-i", str(W / "title_bg.png"),
    "-loop", "1", "-t", str(TD), "-i", str(W / "title.png"),
    "-filter_complex",
    f"[0]gblur=sigma=18,eq=brightness=-0.22:saturation=0.6,colorbalance=bs=0.08,"
    f"zoompan=z='1.05+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,"
    f"fade=t=in:st=0:d=0.6,fade=t=out:st={TD-0.9}:d=0.9[bg];"
    f"[1]format=rgba,fade=t=in:st=0.5:d=1.2:alpha=1,fade=t=out:st={TD-1.0}:d=0.8:alpha=1[tx];"
    f"[bg][tx]overlay=0:0,noise=alls=5:allf=t,"
    f"drawbox=x=0:y=0:w=iw:h=64:color=black:t=fill,drawbox=x=0:y=ih-64:w=iw:h=64:color=black:t=fill,"
    f"format=yuv420p",
    "-r", "24", "-t", str(TD), "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", str(W / "vT.mp4")], check=True)

# ---- end screen
text_png(W / "outro.png", [
    ("माफ़ी माँगना हार नहीं है…", SERIF_R, 64, 120, CREAM),
    ("ख़ुद को माफ़ करना ही असली आज़ादी है।", SERIF, 70, 215, (245, 222, 170)),
], glow=10)
frame(SRC / "c48.mp4", 9.0, W / "outro_bg.png")
subprocess.run(["ffmpeg", "-y", "-v", "error",
    "-loop", "1", "-t", str(OD), "-i", str(W / "outro_bg.png"),
    "-loop", "1", "-t", str(OD), "-i", str(W / "outro.png"),
    "-filter_complex",
    f"[0]gblur=sigma=10,eq=brightness=-0.18:saturation=0.85,colortemperature=temperature=4700:mix=0.3,"
    f"zoompan=z='1.04+0.0002*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,"
    f"fade=t=in:st=0:d=1.5,fade=t=out:st={OD-2.5}:d=2.5[bg];"
    f"[1]format=rgba,fade=t=in:st=1.5:d=1.5:alpha=1,fade=t=out:st={OD-2.5}:d=2.0:alpha=1[tx];"
    f"[bg][tx]overlay=0:0,noise=alls=4:allf=t,format=yuv420p",
    "-r", "24", "-t", str(OD), "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", str(W / "vZ.mp4")], check=True)
print("intro/outro done")
