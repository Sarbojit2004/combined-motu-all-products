#!/usr/bin/env python3
"""Exports each film's two soundtrack stems as WAV, at mix level.

    <film>-music-bed.wav        the "On & On" beat-grid edit alone
    <film>-transition-sfx.wav   the synthesized transition SFX alone

Both stems carry the exact gain the final mix received, so for each film
music-bed + transition-sfx sums back to the delivered soundtrack (the mix's
only extra step is a transparent peak-safety clip above -2.9 dBFS).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as AU

OUT = os.path.join(os.path.dirname(AU.ROOT), "deliverables", "audio-stems")
os.makedirs(OUT, exist_ok=True)

for name in ("reel", "video"):
    plan = json.load(open(os.path.join(AU.ROOT, "src", f"plan-{name}.json")))
    m = AU.music(plan)
    fx = AU.sfx(plan, len(m)) * 10 ** (-9 / 20) * np.abs(m).max()
    mix = m + fx
    g = 10 ** ((-14.0 - AU.lufs(mix)) / 20)
    for stem, x in (("music-bed", m * g), ("transition-sfx", fx * g)):
        p = os.path.join(OUT, f"motu-combined-{name}-{stem}.wav")
        AU.write(p, x)
        pk = 20 * np.log10(np.abs(x).max() + 1e-12)
        print(f"  {os.path.basename(p):42s} {len(x) / AU.SR:7.3f} s  peak {pk:6.2f} dBFS")
