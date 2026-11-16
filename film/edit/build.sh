#!/usr/bin/env bash
# Full build of "Riya - Andar Ki Adalat" for YouTube.
# Usage: film/edit/build.sh <clips_dir with c01..c48.mp4> <work_dir> <final.mp4> [trims.json] [timing.json]
#  0-7 s     cold open: the judge's line echoing over black (hook)
#  7-11.5 s  title card
#  then the 48 clips in script order (dead air trimmed by trims.json)
#  then a 20 s end screen (closing line, room for YouTube end-screen elements)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$1"; W="$2"; OUT="$3"; TRIMS="${4:-}"; TIMING="${5:-}"; mkdir -p "$W"
COLD=7.0; TITLE=4.5; INTRO=11.5; OUTRO=20.0
SF2=/usr/share/sounds/sf2/FluidR3_GM.sf2

# set RERENDER=1 to force re-grading the clips; otherwise a finished stage-1 render is reused
if [[ -n "${RERENDER:-}${ONLY:-}" || ! -f "$W/timeline.json" ]]; then python3 "$HERE/render_clips.py" "$SRC" "$W" $TRIMS; fi
python3 "$HERE/sync_av.py" "$W"   # picture is master: lock each clip's audio to its video length
python3 "$HERE/intro_outro.py" "$SRC" "$W" "$TITLE" "$OUTRO"

# --- picture
ffmpeg -y -v error -f lavfi -i "color=black:s=1920x1080:r=24:d=$COLD" -c:v libx264 -crf 14 -pix_fmt yuv420p "$W/v00.mp4"
{ echo "file '$W/v00.mp4'"; echo "file '$W/vT.mp4'"
  for i in $(seq -w 1 48); do echo "file '$W/v$i.mp4'"; done; echo "file '$W/vZ.mp4'"; } > "$W/vlist.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$W/vlist.txt" -c copy "$W/picture.mp4"

# --- dialogue bus: cold-open voice + silence under the title + 48 clips + silence under the end screen
ffmpeg -y -v error -ss 0.6 -to 6.2 -i "$SRC/c05.mp4" -af \
  "aresample=48000,highpass=f=80,loudnorm=I=-19:TP=-3,aecho=0.8:0.75:90|200|340:0.35|0.22|0.12,adelay=600|600,aresample=48000,apad" \
  -t "$COLD" -ar 48000 -ac 2 -c:a pcm_s16le "$W/a00.wav"
ffmpeg -y -v error -f lavfi -i "anullsrc=r=48000:cl=stereo" -t "$TITLE" -c:a pcm_s16le "$W/aT.wav"
ffmpeg -y -v error -f lavfi -i "anullsrc=r=48000:cl=stereo" -t "$OUTRO" -c:a pcm_s16le "$W/aZ.wav"
{ echo "file '$W/a00.wav'"; echo "file '$W/aT.wav'"
  for i in $(seq -w 1 48); do echo "file '$W/a$i.wav'"; done; echo "file '$W/aZ.wav'"; } > "$W/alist.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$W/alist.txt" -c copy "$W/dialogue.wav"

# --- score
python3 "$HERE/score.py" "$W/timeline.json" "$INTRO" "$OUTRO" "$W/score.mid"
fluidsynth -ni -q -r 48000 -g 0.55 -o synth.reverb.active=1 -o synth.reverb.room-size=0.85 \
  -o synth.reverb.damp=0.4 -o synth.reverb.width=0.9 -o synth.reverb.level=0.75 \
  -o synth.chorus.active=0 -F "$W/score_raw.wav" "$SF2" "$W/score.mid"
ffmpeg -y -v error -i "$W/score_raw.wav" -af \
  "aresample=48000,highpass=f=35,equalizer=f=3500:t=q:w=1:g=-2,aecho=0.8:0.5:70|130:0.12|0.08,loudnorm=I=-27:TP=-4:LRA=14,aresample=48000" \
  -ar 48000 -ac 2 -c:a pcm_s16le "$W/score.wav"

# --- mix: score ducks under speech, dialogue stays on top
ffmpeg -y -v error -i "$W/dialogue.wav" -i "$W/score.wav" -filter_complex \
  "[0:a]asplit=2[d][sc];[1:a][sc]sidechaincompress=threshold=0.015:ratio=4:attack=60:release=900:makeup=1[m];\
   [d][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[mix]" \
  -map "[mix]" -ar 48000 -c:a pcm_s24le "$W/mix_raw.wav"
# guard: the soundtrack must cover the whole picture
python3 - "$W/picture.mp4" "$W/mix_raw.wav" <<'PY'
import subprocess, sys
d = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                   capture_output=True, text=True).stdout)
v, a = d(sys.argv[1]), d(sys.argv[2])
assert abs(v - a) < 0.1, f"picture {v:.2f}s vs sound {a:.2f}s"
print(f"length check ok: picture {v:.2f}s, sound {a:.2f}s")
PY

# --- master: two-pass loudnorm to -14 LUFS / -1.5 dBTP (YouTube's reference loudness)
M=$(ffmpeg -hide_banner -i "$W/mix_raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i "$W/picture.mp4" -i "$W/mix_raw.wav" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -profile:v high -level 4.1 \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"

# --- subtitles (uploaded separately to YouTube, never burned in)
[[ -n "$TIMING" ]] && python3 "$HERE/subtitles.py" "$TIMING" "$W/timeline.json" "$INTRO" "${OUT%.mp4}"
echo "done: $OUT"
