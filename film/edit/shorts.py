#!/usr/bin/env python3
"""Vertical Shorts / Reels (1080x1920) cut from the finished film.

Usage: shorts.py <final.mp4> <timeline.json> <intro_s> <subs.hi.srt> <out_dir>

Layout: a hook line in the top band, the picture reframed to 3:4 in the middle (crop follows the
faces found in each shot; wide two-person shots are shown whole over a blurred copy), burned-in
Hindi captions in the bottom band (most Reels are watched muted), and a closing call to the full film.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

FILM, TL, INTRO, SRT, OUT = sys.argv[1], json.load(open(sys.argv[2])), float(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
OUT.mkdir(parents=True, exist_ok=True)
T = {c["clip"]: (c["start"] + INTRO, c["start"] + INTRO + c["dur"]) for c in TL}
BOLD = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
CHANNEL = "MAN KI TEH"

SHORTS = [
    ("short1_case", [4, 5, 6], "केस मेरे ख़िलाफ़…\nऔर केस किया भी मैंने?"),
    ("short2_khana", [11, 22, 25, 26], "माँ बस इतना ही पूछती थी…\n“खाना खाया?”"),
    ("short3_kyun", [27, 28, 29, 30], "हर बार मेरे साथ ही\nक्यों होता है?"),
    ("short4_kirdar", [9, 10, 17], "तुम्हारी कहानी में\nसिर्फ़ एक ही किरदार है…"),
    ("short5_maafi", [36, 37, 42, 43], "जिस दिन मैंने\nमाँ से माफ़ी माँगी…"),
]

def srt_cues(path):
    txt = Path(path).read_text(encoding="utf-8").strip().split("\n\n"); cues = []
    def sec(s):
        h, m, r = s.split(":"); s, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    for block in txt:
        lines = block.split("\n")
        a, b = lines[1].split(" --> "); cues.append((sec(a), sec(b), " ".join(lines[2:])))
    return cues

def text_png(path, text, size, color, box_h, wrap=22):
    img = Image.new("RGBA", (1080, box_h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(BOLD, size, layout_engine=ImageFont.Layout.RAQM)
    lines = []
    for para in text.split("\n"):  # simple word wrap
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > 980 and cur: lines.append(cur); cur = w
            else: cur = t
        lines.append(cur)
    lh = int(size * 1.45); y = (box_h - lh * len(lines)) // 2
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((1080 - w) / 2, y), ln, font=f, fill=color, stroke_width=max(4, size // 12), stroke_fill=(0, 0, 0))
        y += lh
    img.save(path)

def face_center(a, b):
    """Median x of faces (0..1) in the film between a and b, and how spread they are."""
    cap = cv2.VideoCapture(FILM); fr = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    pr = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml"); xs = []
    for t in np.linspace(a + 0.5, b - 0.5, 8):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, img = cap.read()
        if not ok: continue
        g = cv2.cvtColor(cv2.resize(img, (960, 540)), cv2.COLOR_BGR2GRAY); g = cv2.equalizeHist(g)
        found = list(fr.detectMultiScale(g, 1.1, 5, minSize=(50, 50))) + list(pr.detectMultiScale(g, 1.1, 5, minSize=(50, 50)))
        found += [(960 - x - w, y, w, h) for x, y, w, h in pr.detectMultiScale(cv2.flip(g, 1), 1.1, 5, minSize=(50, 50))]
        xs += [(x + w / 2) / 960 for x, y, w, h in found]
    cap.release()
    if not xs: return 0.5, 0.0
    xs = np.array(xs); return float(np.median(xs)), float(np.percentile(xs, 90) - np.percentile(xs, 10))

cues = srt_cues(SRT)
for name, clips, hook in SHORTS:
    tmp = Path(tempfile.mkdtemp())
    parts = []
    for c in clips:
        a, b = T[c]; cx, spread = face_center(a, b)
        if spread > 0.45:   # two people far apart: show the whole frame over a blurred copy
            vf = ("split[x][y];[y]scale=-2:1440,crop=1080:1440,gblur=sigma=30,eq=brightness=-0.15[bg];"
                  "[x]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2")
        else:               # 3:4 crop that follows the face
            sw = 2560; left = int(min(max(cx * sw - 540, 0), sw - 1080))
            vf = f"scale={sw}:1440:flags=lanczos,crop=1080:1440:{left}:0"
        vf += ",pad=1080:1920:0:240:black,setsar=1,fps=24,format=yuv420p"
        p = tmp / f"p{c}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", FILM,
                        "-vf", vf, "-threads", "2", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
                        "-c:a", "pcm_s16le", str(p)], check=True)
        parts.append(p); print(name, c, f"face x={cx:.2f} spread={spread:.2f}", flush=True)
    (tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-c", "copy", str(tmp / "body.mkv")], check=True)
    # overlays: hook (top, whole short except the last 3 s), captions (bottom), call to the full film
    s0 = T[clips[0]][0]; total = sum(T[c][1] - T[c][0] for c in clips)
    offs, acc = {}, 0.0
    for c in clips: offs[c] = acc; acc += T[c][1] - T[c][0]
    text_png(tmp / "hook.png", hook, 64, (255, 255, 255), 240)
    text_png(tmp / "cta.png", "पूरी फ़िल्म देखें —\n" + CHANNEL + " चैनल पर", 56, (255, 214, 0), 240)
    inputs, ov, k = ["-i", str(tmp / "body.mkv"), "-i", str(tmp / "hook.png"), "-i", str(tmp / "cta.png")], [], 3
    chain = f"[0:v][1:v]overlay=0:0:enable='lt(t,{total - 3:.2f})'[v1];[v1][2:v]overlay=0:0:enable='gte(t,{total - 3:.2f})'[v2]"
    last = "v2"
    for c in clips:
        a, b = T[c]
        for (cs, ce, txt) in cues:
            if ce <= a or cs >= b: continue
            st, en = offs[c] + max(cs, a) - a, offs[c] + min(ce, b) - a
            png = tmp / f"cap{k}.png"; text_png(png, txt, 50, (255, 255, 255), 240)
            inputs += ["-i", str(png)]
            chain += f";[{last}][{k}:v]overlay=0:1680:enable='between(t,{st:.2f},{en:.2f})'[v{k}]"; last = f"v{k}"; k += 1
    out = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", chain + f";[{last}]format=yuv420p[vo]",
                    "-map", "[vo]", "-map", "0:a", "-af", f"afade=t=in:d=0.3,afade=t=out:st={total - 1.0:.2f}:d=1.0",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out, round(total, 1), "s", flush=True)
