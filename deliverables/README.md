# MOTU combined films — 4K deliverables

| Film | Canvas | Length | Parts |
|---|---|---|---|
| `reel-4k/` | 2160 × 3840 (9:16), 30 fps | 180.000 s (no end screen) | 4 |
| `video-4k/` | 3840 × 2160 (16:9), 30 fps | 300.000 s (end screen 289.9–300 s) | 14 |

Each part is a normal MP4 that plays on its own, in order (`part01`, `part02`, …).
The video in every part is the renderer's own H.264 encode, stream-copied, never
re-encoded. Each folder's `JOIN.md` has the one-line ffmpeg command that rejoins the
parts with the full soundtrack; the rejoined video has been verified bit-identical
to the rendered master.

Music: "On & On" (Cartoon, Jéja feat. Daniel Levi), NCS, re-cut on its own beat grid.
Transition SFX are synthesized (motu-combined/scripts/sfxlib.py). Mixed to −14 LUFS.

Thumbnails: `../thumbnails/` (portrait 1080 × 1920, landscape 1920 × 1080).
