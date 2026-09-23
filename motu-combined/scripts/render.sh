#!/bin/sh
# Render a composition in chunks (resumable), join losslessly, mux the master audio.
#   sh scripts/render.sh <Composition> <outname> <frames> <chunk>
set -e
COMP=$1; NAME=$2; FRAMES=$3; CHUNK=$4
MIX=public/audio/mix-$(echo "$COMP" | tr 'A-Z' 'a-z').wav
D=out/$NAME-chunks; mkdir -p $D
i=0
while [ $i -lt $FRAMES ]; do
  e=$((i + CHUNK - 1)); [ $e -ge $FRAMES ] && e=$((FRAMES - 1))
  f=$D/$(printf '%05d' $i).mp4
  if [ ! -s "$f" ]; then
    npx remotion render $COMP "$f.tmp.mp4" --frames=$i-$e --muted --concurrency=${CONC:-4} --crf=${CRF:-16} --jpeg-quality=92 --log=error
    mv "$f.tmp.mp4" "$f"
  fi
  echo "chunk $i-$e done"
  i=$((e + 1))
done
ls $D/*.mp4 | grep -v tmp | sed "s#^#file '$PWD/#; s#\$#'#" > $D/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $D/list.txt -i $MIX -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart out/$NAME.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 out/$NAME.mp4
