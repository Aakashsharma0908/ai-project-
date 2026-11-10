#!/usr/bin/env bash
# Full build: picture, soundtrack, mastering, mux.
# Usage: edit/build.sh <src_dir with c1..c5.mp4> <work_dir> <final.mp4>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$1"; W="$2"; OUT="$3"; mkdir -p "$W"
bash "$HERE/render_video.sh" "$S" "$W" "$W/video.mp4"
python3 "$HERE/make_audio.py" "$S" "$W/mix_raw.wav"
# Master to -14 LUFS (streaming standard), -1 dBTP ceiling, two-pass loudnorm.
M=$(ffmpeg -hide_banner -i "$W/mix_raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i "$W/video.mp4" -i "$W/mix_raw.wav" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000,alimiter=limit=0.89:level=false" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart "$OUT"
echo "done: $OUT"
