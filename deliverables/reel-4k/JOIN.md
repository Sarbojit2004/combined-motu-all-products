# motu-combined-reel-4k

4 sequential parts, each playable on its own, total 180.000 s.
The video in every part is the renderer's own encode, stream-copied — never re-encoded.

Rejoin into one master (video stream-copied, full soundtrack from `motu-combined-reel-4k-audio.m4a`):

```
ffmpeg -f concat -safe 0 -i motu-combined-reel-4k.concat.txt -i motu-combined-reel-4k-audio.m4a -map 0:v -map 1:a -c copy motu-combined-reel-4k.mp4
```
