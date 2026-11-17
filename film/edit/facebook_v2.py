#!/usr/bin/env python3
"""Facebook cut of the finished film: 4:5 (1080x1350) for the mobile feed.

Usage: facebook_v2.py <final.mp4> <hi.srt> <cold_s> <intro_s> <outro_s> <work> <out.mp4> <cold_still.png>

What changes from the YouTube cut (Facebook viewers scroll fast, mostly on phones, often muted):
  * 4:5 frame: the film sits full-width in the middle over a blurred, darkened copy of itself,
    so nothing in the picture is cropped away.
  * Top band: the hook question for the first seconds, then the film's name and the channel.
  * Bottom band: Hindi captions burned in, below the picture (never over faces).
  * Intro: the cold open plays straight away over a slow push-in on the judge (never a black first frame); the slow title card is dropped (the name lives in the top band).
  * Outro: the 20 s YouTube end screen is replaced by a 7 s card asking viewers to comment and follow
    on Facebook (no YouTube mention).
"""
import re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, SRT = sys.argv[1], sys.argv[2]
COLD, INTRO, OUTRO = map(float, sys.argv[3:6])
W, OUT, STILL = Path(sys.argv[6]), sys.argv[7], sys.argv[8]
W.mkdir(parents=True, exist_ok=True)
FW, FH, PH = 1080, 1350, 608          # frame and picture height (16:9 at full width)
PY = (FH - PH) // 2                   # picture top
SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf"
LATIN = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
CREAM, GOLD = (238, 230, 214), (214, 176, 110)
OUTRO_FB = 7.0

def run(cmd): subprocess.run(cmd, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

def card(path, lines, size=(FW, FH), glow=8):
    img = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for text, font, fs, y, col in lines:
        f = ImageFont.truetype(font, fs, layout_engine=ImageFont.Layout.RAQM)
        d.text(((size[0] - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col + (255,),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
    Image.alpha_composite(img.filter(ImageFilter.GaussianBlur(glow)), img).save(path)

TOTAL = dur(SRC); BODY_END = TOTAL - OUTRO
SHIFT = INTRO - COLD                  # seconds removed by dropping the title card

# ---- top band texts
card(W / "hook.png", [("मेरे ख़िलाफ़ केस…", SERIF, 70, 95, (245, 222, 170)),
                      ("मैंने ही किया?", SERIF, 70, 200, (245, 222, 170))], size=(FW, PY))
card(W / "name.png", [("अंदर की अदालत", SERIF, 64, 120, CREAM),
                      ("M A N   K I   T E H", LATIN, 26, 240, GOLD)], size=(FW, PY))

# ---- captions: shift to the new timeline, write ASS placed in the bottom band
def sec(s): h, m, x = s.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(x)
def ass_t(x): x = max(0.0, x); return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
events = []
for blk in open(SRT, encoding="utf-8").read().strip().split("\n\n"):
    ln = blk.split("\n"); a, b = [sec(t.strip()) for t in ln[1].split("-->")]; text = " ".join(ln[2:])
    if a >= INTRO: a, b = a - SHIFT, b - SHIFT
    elif a >= COLD: continue
    else: b = min(b, COLD)
    events.append(f"Dialogue: 0,{ass_t(a)},{ass_t(b)},Cap,,0,0,0,,{text}")
(W / "caps.ass").write_text(
    "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1350\nWrapStyle: 0\n\n"
    "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
    "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
    "Alignment, MarginL, MarginR, MarginV, Encoding\n"
    "Style: Cap,Noto Sans Devanagari,50,&H00D6E6EE,&H00D6E6EE,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,"
    f"8,70,70,{PY + PH + 50},1\n\n"
    "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    + "\n".join(events) + "\n", encoding="utf-8")

# ---- main part: cold open + film body, laid out in 4:5
HOOK_END = COLD + 6.0
fc = (
    f"[3:v]scale=1920:1080,zoompan=z='1.0+0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,"
    f"eq=brightness=-0.08:saturation=0.75,vignette=PI/4,trim=0:{COLD},fade=t=in:d=0.4,setpts=PTS-STARTPTS[c];[0:v]trim={INTRO}:{BODY_END},setpts=PTS-STARTPTS[b];"
    f"[c][b]concat=n=2:v=1:a=0,split[m1][m2];"
    f"[m1]scale=-2:{FH},crop={FW}:{FH},gblur=sigma=40,eq=brightness=-0.28:saturation=0.7[bg];"
    f"[m2]scale={FW}:{PH}[fg];"
    f"[bg][fg]overlay=0:{PY}[l];"
    f"[1:v]format=rgba,fade=t=out:st={HOOK_END - 0.5}:d=0.5:alpha=1[hk];"
    f"[2:v]format=rgba,fade=t=in:st={HOOK_END}:d=0.8:alpha=1[nm];"
    f"[l][hk]overlay=0:0:enable='lt(t,{HOOK_END})'[l2];[l2][nm]overlay=0:0:enable='gte(t,{HOOK_END})',"
    f"subtitles=filename={W / 'caps.ass'},format=yuv420p[v];"
    f"[0:a]atrim=0:{COLD},asetpts=PTS-STARTPTS,afade=t=out:st={COLD - 0.3}:d=0.3[ca];"
    f"[0:a]atrim={INTRO}:{BODY_END},asetpts=PTS-STARTPTS,afade=t=in:d=0.3[ba];"
    f"[ca][ba]concat=n=2:v=0:a=1[a]")
run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-loop", "1", "-i", str(W / "hook.png"), "-loop", "1", "-i", str(W / "name.png"), "-loop", "1", "-i", STILL,
     "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(COLD + BODY_END - INTRO), "-r", "24",
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-c:a", "pcm_s16le", "-ar", "48000", str(W / "main.mkv")])

# ---- Facebook outro: last picture, blurred, with the comment question and a follow line
run(["ffmpeg", "-y", "-v", "error", "-ss", str(BODY_END - 0.1), "-i", SRC, "-frames:v", "1", str(W / "last.png")])
card(W / "outro.png", [
    ("आपके मन की अदालत में…", SERIF_R, 58, 380, CREAM),
    ("आज किसका केस चल रहा है?", SERIF, 66, 470, (245, 222, 170)),
    ("कमेंट में ज़रूर बताइए", SERIF_R, 40, 600, CREAM),
    ("ऐसी और कहानियों के लिए", SERIF_R, 40, 800, CREAM),
    ("फ़ॉलो करें — मन की तह", SERIF, 58, 870, (245, 222, 170)),
    ("M A N   K I   T E H", LATIN, 28, 990, GOLD)])
O = OUTRO_FB
run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(O), "-i", str(W / "last.png"),
     "-loop", "1", "-t", str(O), "-i", str(W / "outro.png"), "-ss", str(BODY_END), "-t", str(O), "-i", SRC,
     "-filter_complex",
     f"[0:v]scale=-2:{FH},crop={FW}:{FH},gblur=sigma=14,eq=brightness=-0.3:saturation=0.8,fade=t=in:d=0.8[bg];"
     f"[1:v]format=rgba,fade=t=in:st=0.6:d=1.0:alpha=1[tx];[bg][tx]overlay=0:0,fade=t=out:st={O - 1.2}:d=1.2,format=yuv420p[v];"
     f"[2:a]afade=t=out:st={O - 2.0}:d=2.0[a]",
     "-map", "[v]", "-map", "[a]", "-t", str(O), "-r", "24", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
     "-c:a", "pcm_s16le", "-ar", "48000", str(W / "outro.mkv")])

(W / "list.txt").write_text(f"file '{W / 'main.mkv'}'\nfile '{W / 'outro.mkv'}'\n")
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(W / "list.txt"),
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
print("facebook cut:", OUT, round(dur(OUT), 1), "s")
