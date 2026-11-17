#!/usr/bin/env python3
"""Build "Andar Ki Adalat" V2 from the EDL: review preview or full-quality master.

Usage: build_v2.py preview|final <clips_dir> <uploads_dir> <trims.json> <timing.json> <timing_extra.json> <work_dir> <out.mp4>

Both modes produce the whole film: cold open (judge's voice over black), title card, every shot with
its grade, fixes, transitions and burned Hindi subtitles, chapter cards, the score and sound design,
the end screen. "preview" is 960x540 and fast; "final" is 1920x1080 at YouTube quality.
"""
import glob, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from v2_edl import SHOTS

MODE, CLIPS, UPL = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
TRIM = {int(k): v for k, v in json.load(open(sys.argv[4])).items()}
TIM = {**{f"old:{k}": v for k, v in json.load(open(sys.argv[5])).items()},
       **{f"up:{k}": v for k, v in json.load(open(sys.argv[6])).items()}}
WK, OUT = Path(sys.argv[7]), sys.argv[8]; WK.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).parent
FINAL = MODE == "final"
W, H = (1920, 1080) if FINAL else (960, 540)
K = W / 960  # scale factor for text/bars
ENC = ["-c:v", "libx264", "-preset", "medium" if FINAL else "ultrafast", "-crf", "16" if FINAL else "28"]
FONT = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf"
COLD, TITLE, OUTRO = 7.0, 4.5, 20.0
BAR = int(32 * K)
GRAIN = ",noise=alls=4:allf=t" if FINAL else ""
LOOK = {
 "W": "colortemperature=temperature=5200:mix=0.3,eq=saturation=1.05:contrast=1.04" + GRAIN,
 "C": "colorbalance=rs=-0.05:bs=0.05:rh=0.02:bh=-0.02,eq=saturation=0.86:contrast=1.06" + GRAIN +
      f",drawbox=x=0:y=0:w=iw:h={BAR}:color=black:t=fill,drawbox=x=0:y=ih-{BAR}:w=iw:h={BAR}:color=black:t=fill",
 "M": "hue=s=0.35,colorbalance=bs=0.09:bm=0.04,eq=contrast=1.08:brightness=-0.02,vignette=PI/3.3" + GRAIN,
 "S": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.06,vignette=PI/3.4,noise=alls=12:allf=t",
 "G": "colortemperature=temperature=4700:mix=0.35,eq=saturation=1.08:contrast=1.03" + GRAIN,
}

def run(cmd): subprocess.run(cmd, check=True)
def vdur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                                 "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
def frames(f):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                               "stream=nb_read_frames", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip())
def fix_len(path, d):
    """pad or cut a wav to exactly d seconds (sample-accurate)"""
    import numpy as np
    from scipy.io import wavfile
    sr, x = wavfile.read(str(path)); n = int(round(d * sr))
    x = x[:n] if len(x) >= n else np.concatenate([x, np.zeros((n - len(x),) + x.shape[1:], x.dtype)])
    wavfile.write(str(path), sr, x)
def silence(path, d):
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d:.6f}",
         "-c:a", "pcm_s16le", str(path)])
    fix_len(path, d)
def src_of(s):
    if s.startswith("old:"): return CLIPS / f"c{int(s[4:]):02d}.mp4"
    return Path(glob.glob(str(UPL / f"{s[3:]}-*.mp4"))[0])

def png(path, lines, glow=0):
    """lines: (text, font, size, y, colour, box)"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for text, font, size, y, col, box in lines:
        size = int(size * K); f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
        rows, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > W * 0.86 and cur: rows.append(cur); cur = w
            else: cur = t
        rows.append(cur)
        for k, r in enumerate(rows):
            tw = d.textlength(r, font=f); x = (W - tw) / 2; yy = int(y * K) + k * int(size * 1.35)
            if box: d.rectangle([x - 12 * K, yy - 2 * K, x + tw + 12 * K, yy + size * 1.32], fill=(0, 0, 0, 140))
            d.text((x, yy), r, font=f, fill=col + (255,), stroke_width=max(2, int(3 * K)), stroke_fill=(0, 0, 0))
    img.save(path)

REAL, MIND = set("WGS"), set("CM")
for idx, sh in enumerate(SHOTS):
    o_ = sh[7] if len(sh) > 7 else {}
    if len(sh) == 7: SHOTS[idx] = tuple(sh) + (o_,)
    if idx + 1 < len(SHOTS):
        nxt = SHOTS[idx + 1]; on = nxt[7] if len(nxt) > 7 else {}
        if (sh[4] in REAL) != (nxt[4] in REAL) and sh[1] != "card" and nxt[1] != "card":
            o_.setdefault("fout", (0.25, "black"))
            if len(nxt) == 7: SHOTS[idx + 1] = tuple(nxt) + (on,)
            on.setdefault("fin", (0.25, "black"))
parts, timeline, t_acc = [], [], 0.0
for n, shot in enumerate(SHOTS):
    label, src, tin, tout, look, subs, _card = shot[:7]; o = shot[7] if len(shot) > 7 else {}
    out = WK / f"s{n:03d}.mkv"
    if src == "card":
        d = o["dur"]; p = WK / f"card{n}.png"
        png(p, [(o["text"], SERIF, 46, 215, (240, 228, 205), False)] +
               ([(o["sub"], FONT, 24, 290, (214, 176, 110), False)] if o.get("sub") else []))
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r=24:d={d}",
             "-loop", "1", "-t", str(d), "-i", str(p),
             "-filter_complex", f"[1]format=rgba,fade=t=in:st=0.15:d=0.5:alpha=1,fade=t=out:st={d-0.55}:d=0.5:alpha=1[t];"
                                f"[0][t]overlay,format=yuv420p[v]",
             "-map", "[v]", "-an", "-t", str(d), *ENC, str(out)])
        if o.get("vo") and not FINAL:
            pv = WK / f"vo{n}.png"; png(pv, [("रिया (मन में): " + o["vo"], FONT, 23, 540 - 140, (255, 225, 120), True)])
            tmpc = out.with_name(out.stem + "_t.mkv"); out.rename(tmpc)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(tmpc), "-i", str(pv), "-filter_complex",
                 "[0][1]overlay=0:0:enable='gte(t,0.6)',format=yuv420p", "-an", *ENC, str(out)])
        d = frames(out) / 24; silence(out.with_suffix(".wav"), d)
    else:
        f = src_of(src); full = vdur(f)
        if tin is None and tout is None and src.startswith("old:"):
            tin, tout = TRIM.get(int(src[4:]), [0, full])
        tin = tin or 0.0; tout = min(tout or full, full)
        slow = o.get("slow", 1.0)
        d = round((tout - tin) * slow * 24) / 24
        inputs = ["-ss", f"{tin:.3f}", "-t", f"{d / slow:.3f}", "-i", str(f)]; vin = "0:v"
        if "pic" in o:
            ps, pin = o["pic"]; inputs += ["-ss", f"{pin:.3f}", "-t", f"{d:.3f}", "-i", str(src_of(ps))]; vin = "1:v"
        v = []
        if "split" in o:  # handled below as a two-strip composition
            pass
        elif "crop" in o:
            cx, cy, cw = o["crop"]
            v.append(f"crop=iw*{cw}:ih*{cw}:iw*{cx}:min(ih*{cy}\\,ih-ih*{cw})")
        if slow != 1.0: v.append(f"setpts={slow}*PTS,minterpolate=fps=24:mi_mode=blend")
        v += [f"scale={W}:{H}:flags=lanczos", "fps=24"]
        if "push" in o:
            z = o["push"]; nf = int(d * 24)
            v.append(f"zoompan=z='1+({z}-1)*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=24")
        v.append(LOOK[look])
        if "fin" in o: v.append(f"fade=t=in:st=0:d={o['fin'][0]}:color={o['fin'][1]}")
        if "fout" in o: v.append(f"fade=t=out:st={d - o['fout'][0]:.3f}:d={o['fout'][0]}:color={o['fout'][1]}")
        if "split" in o:
            (x0, w0), (x1, w1) = o["split"]; (a0, b0), (a1, b1) = o["speak"]; hw = W // 2 - 3
            side = lambda x, w, a_, b_, tag: (f"crop=iw*{w}:ih:iw*{x}:0,scale={hw}:{H}:force_original_aspect_ratio=increase,"
                                              f"crop={hw}:{H},{LOOK[look]},eq=brightness=-0.22:enable='not(between(t,{a_},{b_}))'[{tag}]")
            chain = (f"[{vin}]fps=24,split[l][r];[l]{side(x0, w0, a0, b0, 'L')};[r]{side(x1, w1, a1, b1, 'R')};"
                     f"color=c=0xd8c8a8:s=6x{H}:r=24:d={d}[bar];[L][bar][R]hstack=3")
            if "fin" in o: chain += f",fade=t=in:st=0:d={o['fin'][0]}:color={o['fin'][1]}"
            chain += "[v0]"; k = 1 + (1 if "pic" in o else 0)
        else:
            chain, k = f"[{vin}]" + ",".join(v) + "[v0]", 1 + (1 if "pic" in o else 0)
        last = "v0"; ov = 0
        # burned subtitles: spread the script lines across the measured speech inside the shot
        segs = [(s, e) for s, e, *_ in TIM.get(src, []) if e > tin and s < tout]
        if subs:
            a = max(segs[0][0], tin) - tin if segs else 0.4; b = min(segs[-1][1], tout) - tin if segs else d - 0.4
            if len(segs) == len(subs): spans = [(max(s, tin) - tin, min(e, tout) - tin) for s, e in segs]
            else:
                tot = sum(len(s) for s in subs); spans, t = [], a
                for s_ in subs: L = (b - a) * len(s_) / tot; spans.append((t, t + L)); t += L
            ends = [min(d, max(e0, s0 + 1.2) + 0.3) for s0, e0 in spans]
            for j in range(len(spans) - 1): ends[j] = min(ends[j], spans[j + 1][0] - 0.05)
            for ((s0, e0), text), e1 in zip(zip(spans, subs), ends):
                col = (255, 225, 120) if o.get("narr") else (255, 255, 255)
                p = WK / f"sub{n}_{ov}.png"; png(p, [(text, FONT, 25, 540 - 88, col, True)])
                inputs += ["-i", str(p)]
                chain += f";[{last}][{k}:v]overlay=0:0:enable='between(t,{s0:.2f},{e1:.2f})'[o{ov}]"
                last = f"o{ov}"; k += 1; ov += 1
        if o.get("vo") and FINAL is False:  # narration placeholder until the voice clip is delivered
            p = WK / f"vo{n}.png"; png(p, [("रिया (मन में): " + o["vo"], FONT, 23, 540 - 140, (255, 225, 120), True)])
            inputs += ["-i", str(p)]
            chain += f";[{last}][{k}:v]overlay=0:0:enable='between(t,0.1,{d - 0.1:.2f})'[o{ov}]"; last = f"o{ov}"; k += 1; ov += 1
        if o.get("title"):
            tt, ts_ = o["title"]; p = WK / f"title{n}.png"
            png(p, [(tt, SERIF, 46, 200, (240, 228, 205), False)] + ([(ts_, FONT, 24, 275, (214, 176, 110), False)] if ts_ else []))
            inputs += ["-loop", "1", "-t", f"{d:.3f}", "-i", str(p)]
            chain += (f";[{k}:v]format=rgba,fade=t=in:st=0.1:d=0.5:alpha=1,fade=t=out:st=3.0:d=0.6:alpha=1[tt{ov}];"
                      f"[{last}][tt{ov}]overlay=0:0[o{ov}]"); last = f"o{ov}"; k += 1; ov += 1
        if o.get("tag"):
            p = WK / f"tag{n}.png"; png(p, [(o["tag"], FONT, 20, 44, (190, 215, 255), True)])
            inputs += ["-i", str(p)]
            chain += f";[{last}][{k}:v]overlay=0:0:enable='between(t,0.3,2.8)'[o{ov}]"; last = f"o{ov}"; k += 1; ov += 1
        af = "asetpts=PTS-STARTPTS,aresample=48000,highpass=f=60,loudnorm=I=-19:TP=-3:LRA=9,aresample=48000"
        if look == "C": af += ",aecho=0.85:0.6:45|90:0.16|0.09"
        for a0, b0 in o.get("mute", []):
            af += f",volume=enable='between(t,{max(0, a0 - tin):.2f},{max(0, b0 - tin):.2f})':volume=0"
        for a0, b0 in o.get("phone", []):  # telephone voice: narrow band
            w = f"enable='between(t,{max(0, a0 - tin):.2f},{max(0, b0 - tin):.2f})'"
            af += f",highpass=f=380:{w},lowpass=f=3000:{w},volume=1.6:{w}"
        if o.get("gain"): af += f",volume={o['gain']}dB"
        af += f",afade=t=in:st=0:d={min(o['fin'][0], 0.8) if 'fin' in o else 0.015}"
        af += f",afade=t=out:st={d - (o['fout'][0] if 'fout' in o else 0.015):.3f}:d={o['fout'][0] if 'fout' in o else 0.015}"
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", chain + f";[{last}]format=yuv420p[vo]",
             "-map", "[vo]", "-an", "-t", f"{d:.4f}", *ENC, str(out)])
        d = frames(out) / 24  # picture is master
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{tin:.3f}", "-i", str(f), "-vn",
             "-af", af + ",apad", "-t", f"{d:.6f}", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out.with_suffix(".wav"))])
        fix_len(out.with_suffix(".wav"), d)
    timeline.append({"label": label, "start": round(t_acc, 6), "dur": d}); t_acc += d
    parts.append(out); print(label, src, f"{d:.2f}s", flush=True)
json.dump(timeline, open(WK / "timeline_v2.json", "w"), indent=0)

# --- intro (cold open over black + title card) and end screen
run([sys.executable, str(HERE / "intro_outro.py"), str(CLIPS), str(WK), str(TITLE), str(OUTRO)])
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r=24:d={COLD}", "-an", "-t", str(COLD),
     *ENC, str(WK / "x_cold.mkv")])
run(["ffmpeg", "-y", "-v", "error", "-ss", "0.6", "-to", "6.2", "-i", str(CLIPS / "c05.mp4"), "-vn", "-af",
     f"aresample=48000,highpass=f=80,loudnorm=I=-18:TP=-3,aecho=0.8:0.75:90|200|340:0.35|0.22|0.12,"
     f"adelay=600|600,aresample=48000,apad", "-t", str(COLD), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(WK / "x_cold.wav")])
fix_len(WK / "x_cold.wav", frames(WK / "x_cold.mkv") / 24)
for name, srcf, dur in (("x_title", "vT.mp4", TITLE), ("x_end", "vZ.mp4", OUTRO)):
    run(["ffmpeg", "-y", "-v", "error", "-i", str(WK / srcf), "-vf", f"scale={W}:{H},format=yuv420p", "-an",
         "-t", str(dur), *ENC, str(WK / f"{name}.mkv")])
    silence(WK / f"{name}.wav", frames(WK / f"{name}.mkv") / 24)
seq = [WK / "x_cold.mkv", WK / "x_title.mkv", *parts, WK / "x_end.mkv"]
(WK / "list.txt").write_text("".join(f"file '{p}'\n" for p in seq))
(WK / "alist.txt").write_text("".join(f"file '{p.with_suffix('.wav')}'\n" for p in seq))
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(WK / "list.txt"), "-c", "copy", str(WK / "body.mkv")])
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(WK / "alist.txt"), "-c", "copy", str(WK / "dialogue.wav")])
vlen, alen = frames(WK / "body.mkv") / 24, float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(WK / "dialogue.wav")], capture_output=True, text=True).stdout)
assert abs(vlen - alen) < 0.05, f"sync check failed: picture {vlen:.3f}s vs sound {alen:.3f}s"
print(f"sync check ok: picture {vlen:.3f}s, sound {alen:.3f}s")

# --- score + rain under the opening night, mix with ducking, master to -14 LUFS
INTRO = COLD + TITLE
run([sys.executable, str(HERE / "score_v2.py"), str(WK / "timeline_v2.json"), str(INTRO), str(OUTRO), str(WK / "score.mid")])
run(["fluidsynth", "-ni", "-q", "-r", "48000", "-g", "0.55", "-o", "synth.reverb.active=1", "-o", "synth.reverb.room-size=0.85",
     "-o", "synth.reverb.level=0.75", "-o", "synth.chorus.active=0", "-F", str(WK / "score_raw.wav"),
     "/usr/share/sounds/sf2/FluidR3_GM.sf2", str(WK / "score.mid")])
night_end = INTRO + sum(c["dur"] for c in timeline[:4])
total = vlen
run(["ffmpeg", "-y", "-v", "error", "-i", str(WK / "score_raw.wav"),
     "-f", "lavfi", "-t", f"{night_end + 1:.2f}", "-i", "anoisesrc=color=pink:amplitude=0.25:r=48000",
     "-filter_complex",
     f"[0:a]aresample=48000,highpass=f=35,loudnorm=I=-27:TP=-4:LRA=14,aresample=48000[m];"
     f"[1:a]lowpass=f=3500,highpass=f=300,volume=0.35,afade=t=in:st={INTRO - 0.5:.2f}:d=2,"
     f"afade=t=out:st={night_end - 1.5:.2f}:d=2.5,adelay=0|0,apad[r];"
     f"[m][r]amix=inputs=2:normalize=0:duration=first,aresample=48000[a]",
     "-map", "[a]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(WK / "music.wav")])
run(["ffmpeg", "-y", "-v", "error", "-i", str(WK / "dialogue.wav"), "-i", str(WK / "music.wav"), "-filter_complex",
     "[0:a]aresample=48000,asplit=2[d][sc];[1:a][sc]sidechaincompress=threshold=0.015:ratio=4:attack=60:release=900[m];"
     f"[d][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,apad,atrim=0:{total:.3f}[mix]",
     "-map", "[mix]", "-ar", "48000", "-c:a", "pcm_s24le", str(WK / "mix_raw.wav")])
M = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(WK / "mix_raw.wav"), "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(M[M.rindex("{"):M.rindex("}") + 1])
vopts = ["-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-profile:v", "high",
         "-level", "4.1"] if FINAL else ["-c:v", "copy"]
run(["ffmpeg", "-y", "-v", "error", "-i", str(WK / "body.mkv"), "-i", str(WK / "mix_raw.wav"),
     "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000",
     "-map", "0:v", "-map", "1:a", *vopts, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k" if FINAL else "128k",
     "-ar", "48000", "-movflags", "+faststart", OUT])
print("done:", OUT, round(total, 1), "s")
