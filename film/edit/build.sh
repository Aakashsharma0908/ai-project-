#!/usr/bin/env bash
# Full build of "Riya - Andar Ki Adalat".
# Usage: film/edit/build.sh <clips_dir with c01..c48.mp4> <work_dir> <final.mp4>
# 1 render graded clips  2 score (MIDI -> FluidSynth, GM soundfont, MIT licence)
# 3 cold open: the judge's line over black  4 mix with ducking  5 master -14 LUFS  6 mux
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$1"; W="$2"; OUT="$3"; mkdir -p "$W"
OFF=7.0     # cold open length (s)
TAIL=1.5    # black after the last fade
SF2=/usr/share/sounds/sf2/FluidR3_GM.sf2

[[ -f "$W/timeline.json" ]] || python3 "$HERE/render_clips.py" "$SRC" "$W"

# --- picture: black cold open + 48 clips + black tail
ffmpeg -y -v error -f lavfi -i "color=black:s=1920x1080:r=24:d=$OFF" -c:v libx264 -crf 14 -pix_fmt yuv420p "$W/v00.mp4"
ffmpeg -y -v error -f lavfi -i "color=black:s=1920x1080:r=24:d=$TAIL" -c:v libx264 -crf 14 -pix_fmt yuv420p "$W/v49.mp4"
{ for i in $(seq -w 0 49); do echo "file '$W/v$i.mp4'"; done; } > "$W/vlist.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$W/vlist.txt" -c copy "$W/picture.mp4"

# --- dialogue bus: cold-open voice (clip 5's line, echoing in the dark) + 48 clips + tail
ffmpeg -y -v error -ss 0.6 -to 6.2 -i "$SRC/c05.mp4" -af \
  "aresample=48000,highpass=f=80,loudnorm=I=-19:TP=-3,aecho=0.8:0.75:90|200|340:0.35|0.22|0.12,adelay=600|600,apad,atrim=0:$OFF" \
  -ac 2 -c:a pcm_s16le "$W/a00.wav"
ffmpeg -y -v error -f lavfi -i "anullsrc=r=48000:cl=stereo" -t "$TAIL" -c:a pcm_s16le "$W/a49.wav"
{ for i in $(seq -w 0 49); do echo "file '$W/a$i.wav'"; done; } > "$W/alist.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$W/alist.txt" -c copy "$W/dialogue.wav"

# --- score
python3 "$HERE/score.py" "$W/timeline.json" "$OFF" "$W/score.mid"
fluidsynth -ni -q -r 48000 -g 0.55 -o synth.reverb.active=1 -o synth.reverb.room-size=0.85 \
  -o synth.reverb.damp=0.4 -o synth.reverb.width=0.9 -o synth.reverb.level=0.75 \
  -o synth.chorus.active=0 -F "$W/score_raw.wav" "$SF2" "$W/score.mid"
ffmpeg -y -v error -i "$W/score_raw.wav" -af \
  "aresample=48000,highpass=f=35,equalizer=f=3500:t=q:w=1:g=-2,aecho=0.8:0.5:70|130:0.12|0.08,loudnorm=I=-24:TP=-4:LRA=14" \
  -ac 2 -c:a pcm_s16le "$W/score.wav"

# --- mix: score ducks under speech, dialogue stays on top
ffmpeg -y -v error -i "$W/dialogue.wav" -i "$W/score.wav" -filter_complex \
  "[0:a]asplit=2[d][sc];[1:a][sc]sidechaincompress=threshold=0.015:ratio=4:attack=60:release=900:makeup=1[m];\
   [d]volume=1.0[dd];[dd][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[mix]" \
  -map "[mix]" -c:a pcm_s24le "$W/mix_raw.wav"

# --- master: two-pass loudnorm to -14 LUFS / -1.5 dBTP (streaming standard)
M=$(ffmpeg -hide_banner -i "$W/mix_raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i "$W/picture.mp4" -i "$W/mix_raw.wav" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -level 4.1 \
  -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart "$OUT"
echo "done: $OUT"
