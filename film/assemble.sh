#!/usr/bin/env bash
# Assemble the 48 generated clips into one film, keeping each clip's audio.
# Usage: film/assemble.sh <clips_dir with c01.mp4..c48.mp4> <out.mp4>
# Normalises every clip to 1920x1080 / 24 fps / 48 kHz stereo, adds short
# fades at the scene changes into and out of the courtroom, then concatenates.
set -euo pipefail
SRC="$1"; OUT="$2"; W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT

# Clips that start a new scene get a 0.4 s fade-in from black.
FADE_IN=" 01 04 05 07 09 13 14 18 19 21 22 25 28 32 36 37 38 40 41 44 47 "

: > "$W/list.txt"
for i in $(seq -w 1 48); do
  f="$SRC/c$i.mp4"; [[ -f "$f" ]] || { echo "missing $f" >&2; exit 1; }
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,setsar=1,format=yuv420p"
  af="aresample=48000"
  if [[ "$FADE_IN" == *" $i "* ]]; then vf+=",fade=t=in:st=0:d=0.4"; af+=",afade=t=in:st=0:d=0.3"; fi
  [[ "$i" == 48 ]] && { vf+=",fade=t=out:st=$(echo "$d-2" | bc):d=2"; af+=",afade=t=out:st=$(echo "$d-2" | bc):d=2"; }
  # Add a silent track if the clip has no audio so concat stays in sync.
  if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$f" | grep -q .; then
    ffmpeg -y -v error -i "$f" -vf "$vf" -af "$af" -ac 2 -c:v libx264 -crf 16 -preset fast -c:a aac -b:a 256k "$W/$i.mp4"
  else
    ffmpeg -y -v error -i "$f" -f lavfi -i anullsrc=r=48000:cl=stereo -vf "$vf" -shortest -c:v libx264 -crf 16 -preset fast -c:a aac -b:a 256k "$W/$i.mp4"
  fi
  echo "file '$W/$i.mp4'" >> "$W/list.txt"
done
ffmpeg -y -v error -f concat -safe 0 -i "$W/list.txt" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 256k -movflags +faststart "$OUT"
echo "done: $OUT"
