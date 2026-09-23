#!/usr/bin/env python3
"""Packs a rendered 4K master into sequential, playable parts under 95 MB.

The film is rendered in 450-frame chunks (scripts/render.sh), each of which
starts on a keyframe. Consecutive chunks are grouped greedily so each group
stays under the limit; each group's video is STREAM-COPIED (never re-encoded)
and muxed with the matching slice of the mastered audio, so every part plays
on its own. Alongside the parts:

    <name>-audio.m4a      the whole mastered soundtrack (AAC 320k)
    <name>.concat.txt     rejoin list for ffmpeg's concat demuxer
    JOIN.md               the one-line rejoin command

Usage: package.py <chunks-dir> <mix.wav> <out-dir> <name> [max_mb]
"""
import glob, os, subprocess, sys

FF = "ffmpeg"
FPS = 30


def frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip()
    return int(out.split(",")[0])


def main():
    cdir, mix, outdir, name = sys.argv[1:5]
    limit = float(sys.argv[5] if len(sys.argv) > 5 else 95) * 1024 * 1024
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, f"{name}-part*.mp4")):
        os.remove(f)
    chunks = sorted(c for c in glob.glob(os.path.join(cdir, "*.mp4")) if ".tmp." not in c)
    info = [(c, os.path.getsize(c), frames(c)) for c in chunks]
    groups, cur, size = [], [], 0
    for c, s, n in info:
        if s > limit:
            raise SystemExit(f"{c} alone is {s / 1e6:.0f} MB — render with smaller chunks")
        if cur and size + s > limit * 0.985:
            groups.append(cur); cur, size = [], 0
        cur.append((c, s, n)); size += s
    groups.append(cur)

    t0 = 0
    parts = []
    for i, g in enumerate(groups, 1):
        n = sum(x[2] for x in g)
        lst = os.path.join(outdir, f".list{i}.txt")
        with open(lst, "w") as f:
            for c, _, _ in g:
                f.write(f"file '{os.path.abspath(c)}'\n")
        out = os.path.join(outdir, f"{name}-part{i:02d}.mp4")
        a, d = t0 / FPS, n / FPS
        subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-ss", f"{a:.6f}", "-t", f"{d:.6f}", "-i", mix,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                        "-movflags", "+faststart", out], check=True)
        os.remove(lst)
        parts.append((os.path.basename(out), a, d))
        print(f"  {os.path.basename(out)}  {a:7.2f} → {a + d:7.2f} s  {os.path.getsize(out) / 1e6:5.1f} MB")
        t0 += n

    audio = os.path.join(outdir, f"{name}-audio.m4a")
    subprocess.run([FF, "-v", "error", "-y", "-i", mix, "-c:a", "aac", "-b:a", "320k", audio], check=True)
    with open(os.path.join(outdir, f"{name}.concat.txt"), "w") as f:
        for p, _, _ in parts:
            f.write(f"file '{p}'\n")
    with open(os.path.join(outdir, "JOIN.md"), "w") as f:
        f.write(f"# {name}\n\n{len(parts)} sequential parts, each playable on its own, total {t0 / FPS:.3f} s.\n"
                f"The video in every part is the renderer's own encode, stream-copied — never re-encoded.\n\n"
                f"Rejoin into one master (video stream-copied, full soundtrack from `{name}-audio.m4a`):\n\n"
                f"```\nffmpeg -f concat -safe 0 -i {name}.concat.txt -i {name}-audio.m4a -map 0:v -map 1:a -c copy {name}.mp4\n```\n")
    print(f"{len(parts)} parts, {t0} frames = {t0 / FPS:.3f} s")


if __name__ == "__main__":
    main()
