#!/usr/bin/env python3
"""The soundtrack: "On & On" re-cut on its own beat grid + synthesized SFX.

For each film (plan from scripts/plan.py):
  1. MUSIC — the source is cut into whole-beat blocks listed in plan.audio and
     re-joined with 12 ms equal-power crossfades, so every join lands exactly
     on a downbeat and the output beat grid matches the picture's.
  2. SFX — every transition cue in plan.sfx is synthesized (sfxlib.py) and
     placed at its time; cues closer than 0.55 s are thinned so fast drop cuts
     don't turn into a machine-gun.
  3. MASTER — music and SFX are summed, mastered to -14 LUFS integrated (the
     loudness Instagram/YouTube normalise to) with a -1 dBFS peak ceiling.

Writes public/audio/mix-{reel,video}.wav and a transition-SFX-only stem
public/audio/sfx-{reel,video}.wav (delivered alongside the masters).
"""
import json, os, subprocess, wave
import numpy as np
import sfxlib as L

SR = L.SR
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "public", "audio")
os.makedirs(OUT, exist_ok=True)


def read_wav(p):
    with wave.open(p, "rb") as w:
        assert w.getframerate() == SR and w.getsampwidth() == 2
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768.0
        return x.reshape(-1, w.getnchannels())


def write(p, x):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


SRC = read_wav(os.path.join(ROOT, "audio-src", "on-and-on.wav"))


def cut(a, b):
    a, b = int(round(a * SR)), int(round(b * SR))
    seg = SRC[max(0, a):min(len(SRC), b)]
    if b > len(SRC):
        seg = np.concatenate([seg, np.zeros((b - max(a, len(SRC)), 2))])
    return seg


def music(plan):
    au = plan["audio"]
    beat, off = plan["beat"], au["srcOffset"]
    xf = int(0.012 * SR)
    out = np.zeros((0, 2))
    for i, (b0, b1) in enumerate(au["blocks"]):
        s0 = off + b0 * beat
        if i == 0 and au.get("leadIn"):
            s0 = 0.0  # the pickup before the song's first beat
        # Each block carries xf extra samples so the crossfade centres on the join.
        seg = cut(s0 - (xf / 2 / SR if i else 0), off + b1 * beat + xf / 2 / SR)
        if len(out) == 0:
            out = seg
            continue
        w = np.linspace(0, np.pi / 2, xf)[:, None]
        tail = out[-xf:] * np.cos(w) + seg[:xf] * np.sin(w)
        out = np.concatenate([out[:-xf], tail, seg[xf:]])
    n = int(round(au["duration"] * SR))
    out = out[:n] if len(out) >= n else np.concatenate([out, np.zeros((n - len(out), 2))])
    # The last 1.2 s fades so the film never ends on a truncated sample.
    f = int(1.2 * SR)
    out[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
    return out


_cache = {}


def sound(cue):
    if cue not in _cache:
        x = np.asarray(L.SOUNDS[cue](), dtype=np.float64)
        x = L.declick(x / (np.abs(x).max() + 1e-9))
        g = 10 ** (L.RELATIVE[cue] / 20)
        _cache[cue] = L.stereo(x * g, width=0.3)
    return _cache[cue]


def sfx(plan, n):
    out = np.zeros((n, 2))
    last = -9.0
    kept = 0
    for c in plan["sfx"]:
        trans = c["cue"] not in ("riser-short", "impact-deep", "tick-glass", "outro-bloom")
        if trans and c["at"] - last < 0.55:
            continue
        if trans:
            last = c["at"]
        s = sound(c["cue"])
        a = int(c["at"] * SR)
        b = min(n, a + len(s))
        if a < n:
            out[a:b] += s[:b - a]
            kept += 1
    print(f"  {plan['name']}: {kept} of {len(plan['sfx'])} SFX cues placed")
    return out


def lufs(x):
    kw = np.stack([L._k_weight(x[:, c]) for c in range(2)], 1)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = np.array([np.sum(np.mean(kw[i:i + blk] ** 2, 0)) for i in range(0, len(kw) - blk, hop)])
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-20))
    k = lk > -70
    rel = -0.691 + 10 * np.log10(ms[k].mean()) - 10
    k2 = k & (lk > rel)
    return -0.691 + 10 * np.log10(ms[k2].mean())


def soft_clip(x, ceil):
    # Transparent below 0.8·ceil, tanh knee above — catches SFX peaks on top of a
    # mastered commercial track without pumping.
    k = 0.8 * ceil
    y = x.copy()
    m = np.abs(x) > k
    y[m] = np.sign(x[m]) * (k + (ceil - k) * np.tanh((np.abs(x[m]) - k) / (ceil - k)))
    return y


def master(x, target=-14.0, ceil_db=-1.0):
    ceil = 10 ** (ceil_db / 20)
    for _ in range(3):
        x = x * 10 ** ((target - lufs(x)) / 20)
        x = soft_clip(x, ceil)
    return x


if __name__ == "__main__":
    for name in ("reel", "video"):
        plan = json.load(open(os.path.join(ROOT, "src", f"plan-{name}.json")))
        m = music(plan)
        fx = sfx(plan, len(m))
        # SFX sit under the music: the track is the star, the cues mark the cuts.
        mix = m + fx * 10 ** (-9 / 20) * np.abs(m).max()
        mix = master(mix)
        write(os.path.join(OUT, f"mix-{name}.wav"), mix)
        write(os.path.join(OUT, f"sfx-{name}.wav"), master(fx + 1e-7, target=-20.0))
        print(f"  {name}: {len(mix) / SR:.3f} s  {lufs(mix):.1f} LUFS  peak {20 * np.log10(np.abs(mix).max()):.2f} dBFS")
