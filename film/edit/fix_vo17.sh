#!/usr/bin/env bash
# VO 17 was generated with its last word ("देखिए") clipped at the 10 s mark.
# Keep the voice exactly as generated (no time-stretch or echo: on so short a piece they ring like a beep),
# fade the last 0.15 s, and give the clip a little extra picture for the tail. Usage: fix_vo17.sh <vo17.mp4> <out c99.mp4>
set -euo pipefail
IN="$1"; OUT="$2"; T="$(mktemp -d)"
D=$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$IN")
ffmpeg -y -v error -i "$IN" -filter_complex "[0:a]aresample=48000,afade=t=out:st=$(python3 -c "print($D-0.15)"):d=0.15,apad=pad_dur=0.6[ao]" \
  -map "[ao]" -c:a pcm_s16le "$T/a.wav"
ffmpeg -y -v error -i "$IN" -i "$T/a.wav" -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=0.6[v]" \
  -map "[v]" -map 1:a -c:v libx264 -crf 14 -preset veryfast -c:a aac -b:a 256k -shortest "$OUT"
