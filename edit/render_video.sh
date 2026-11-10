#!/usr/bin/env bash
# Picture edit + grade. Usage: render_video.sh <src_dir> <work_dir> <out.mp4>
# Expects src_dir/c1.mp4 .. c5.mp4 (1280x720, 24fps).
# Stage 1 renders each shot (trim, per-shot exposure/white-balance match,
# optional slow dolly-in) to a near-lossless intermediate.
# Stage 2 assembles shots with the transitions and applies the shared look.
set -euo pipefail
S="$1"; W="$2"; OUT="$3"; mkdir -p "$W"
ENC="-c:v libx264 -preset fast -crf 8 -pix_fmt yuv420p -an"
# Slow dolly-in on a 2x upscale so the motion stays sub-pixel smooth.
push() { echo "scale=2560:1440:flags=lanczos,zoompan=z='1+$1*on/$2':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1280x720:fps=24,"; }

shot() { # name src in out filters
  ffmpeg -y -v error -ss "$3" -to "$4" -i "$S/$2" -vf "${5}fps=24,format=yuv420p" $ENC "$W/$1.mp4"
}
# A: in bed on the phone (already has its own slow push-in)
shot a c1.mp4 0    10   "colortemperature=temperature=6200:mix=0.25,"
# B: gets up and walks to the window (skip the opening that repeats shot A)
shot b c2.mp4 1.25 8.0  "colortemperature=temperature=6000:mix=0.2,eq=brightness=-0.015,"
# C: leans to the window -> the street (match cut on the sit/lean)
shot c c3.mp4 0.25 8.25 "$(push 0.04 192)eq=saturation=0.95,"
# D: reaction - he smiles (lifted ~1 stop to match the rest)
shot d c4.mp4 0    9.5  "eq=gamma=1.18:brightness=0.015,colortemperature=temperature=6000:mix=0.2,"
# E: smile fades, looks down (slow push-in to let the moment breathe)
shot e c5.mp4 0    10   "$(push 0.05 240)eq=gamma=1.16:brightness=0.012,colortemperature=temperature=6000:mix=0.2,"

# Shared night look: soft S-curve, teal shadows / warm highlights, gentle desat,
# light denoise, mild sharpen, vignette, fine luma grain.
LOOK="hqdn3d=1.5:1.5:3:3,curves=all='0/0.02 0.25/0.21 0.5/0.5 0.75/0.79 1/0.97',colorbalance=rs=-0.03:bs=0.04:rh=0.03:bh=-0.03,eq=saturation=0.92,unsharp=5:5:0.35:5:5:0,vignette=angle=PI/5"

ffmpeg -y -v error -stats \
  -i "$W/a.mp4" -i "$W/b.mp4" -i "$W/c.mp4" -i "$W/d.mp4" -i "$W/e.mp4" \
  -filter_complex "
  [0:v]settb=AVTB[a];[1:v]settb=AVTB[b];[2:v]settb=AVTB[c];[3:v]settb=AVTB[d];[4:v]settb=AVTB[e];
  [a][b]xfade=transition=fade:duration=0.25:offset=9.75[ab];
  [ab][c]concat=n=2:v=1:a=0[abc];
  [abc][d]xfade=transition=fade:duration=1.0:offset=23.5[abcd];
  [abcd][e]xfade=transition=fade:duration=0.8:offset=32.2[all];
  [all]$LOOK,tpad=stop_mode=add:stop_duration=2.5:color=black,
       fade=t=in:st=0:d=1.5,fade=t=out:st=40.2:d=2.0,
       noise=c0s=5:c0f=t,format=yuv420p,setsar=1[v]" \
  -map "[v]" -r 24 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -an "$OUT"
