#!/usr/bin/env bash
# VO 17 was generated with its last word ("देखिए") clipped at the 10 s mark.
# Keep everything up to 9.80 s, stretch the final syllable, let it decay naturally, and give the clip
# a little extra picture so the full word fits. Usage: fix_vo17.sh <vo17.mp4> <out c99.mp4>
set -euo pipefail
IN="$1"; OUT="$2"; T="$(mktemp -d)"
ffmpeg -y -v error -i "$IN" -filter_complex "[0:a]aresample=48000,asplit=2[a][b];[a]atrim=0:9.80,asetpts=PTS-STARTPTS[p1];\
[b]atrim=9.80:10.03,asetpts=PTS-STARTPTS,atempo=0.62,afade=t=out:st=0.18:d=0.2,aecho=0.8:0.5:60|120:0.25|0.15[p2];\
[p1][p2]concat=n=2:v=0:a=1,apad=pad_dur=0.4[ao]" -map "[ao]" -c:a pcm_s16le "$T/a.wav"
ffmpeg -y -v error -i "$IN" -i "$T/a.wav" -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=0.6[v]" \
  -map "[v]" -map 1:a -c:v libx264 -crf 14 -preset veryfast -c:a aac -b:a 256k -shortest "$OUT"
