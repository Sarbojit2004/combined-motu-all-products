"""Synthesis primitives, transition SFX and a BS.1770 loudness meter.

Adapted from the MOTU AVB Series film (scripts/gen_audio.py): every SFX is
generated from scratch here — no samples. impact_deep is new for this film.
"""
import json
import math
import os
import subprocess
import wave

import numpy as np
from scipy.signal import lfilter
SR = 48000
rng = np.random.default_rng(0xC0B1)
# ─────────────────────────────────────────────────────────── primitives ──
def t(n):
    return np.arange(n) / SR


def tsec(dur):
    return np.arange(int(dur * SR)) / SR


def expd(n, tau):
    return np.exp(-t(n) / tau)


def noise(n):
    return rng.standard_normal(n)


def _bq(fc, q, kind, gain_db=0.0):
    fc = float(np.clip(fc, 20.0, SR / 2 * 0.97))
    w = 2 * math.pi * fc / SR
    al = math.sin(w) / (2 * q)
    c = math.cos(w)
    if kind == "peak":
        A = 10 ** (gain_db / 40)
        a0 = 1 + al / A
        b = [(1 + al * A) / a0, (-2 * c) / a0, (1 - al * A) / a0]
        a = [1.0, (-2 * c) / a0, (1 - al / A) / a0]
        return b, a
    a0 = 1 + al
    if kind == "lp":
        b = [(1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0]
    else:
        b = [(1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0]
    return b, [1.0, -2 * c / a0, (1 - al) / a0]


def lpf(x, fc, q=0.707):
    b, a = _bq(fc, q, "lp")
    return lfilter(b, a, x)


def hpf(x, fc, q=0.707):
    b, a = _bq(fc, q, "hp")
    return lfilter(b, a, x)


def peak(x, fc, gain_db, q=0.9):
    b, a = _bq(fc, q, "peak", gain_db)
    return lfilter(b, a, x)


def lpf_tv(x, fc_curve, q=0.707, blk=2048):
    x = np.asarray(x, dtype=np.float64)
    fc_curve = np.asarray(fc_curve, dtype=np.float64)
    out = np.zeros_like(x)
    zi = np.zeros(2)
    for i in range(0, len(x), blk):
        j = min(i + blk, len(x))
        b, a = _bq(float(fc_curve[i]), q, "lp")
        out[i:j], zi = lfilter(b, a, x[i:j], zi=zi)
    return out


def sine(f, n):
    return np.sin(2 * np.pi * np.cumsum(np.full(n, f / SR)))


def stereo(x, width=0.25, pre=0.012):
    d = int(pre * SR)
    r = np.concatenate([np.zeros(d), x[:-d]]) if d else x.copy()
    return np.stack([x * (1 - width * 0.5) + r * width * 0.5, r * (1 - width * 0.5) + x * width * 0.5], 1)


def verb(x, taps=((0.029, 0.33), (0.043, 0.25), (0.067, 0.18), (0.097, 0.12)), mix=0.26):
    y = np.zeros_like(x)
    for dt, g in taps:
        d = int(dt * SR)
        if d < len(x):
            y[d:] += x[:-d] * g
    return x * (1 - mix) + y * mix


def declick(x, ms=4.0):
    k = max(2, int(ms / 1000 * SR))
    if len(x) < 2 * k:
        return x
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, k))
    x[:k] *= w
    x[-k:] *= w[::-1]
    return x


def speech_pocket(x):
    x = peak(x, 1600, -7.0, q=0.55)
    x = peak(x, 500, -3.2, q=0.8)
    return x


def write_wav(path, x, peak_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    m = np.abs(x).max()
    if m > 0:
        x = x * (10 ** (peak_db / 20)) / m
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(d.tobytes())
    return x

# ═════════════════════════════════════════════════════════════════ SFX ══
def band_pass_sweep(n, f_lo, f_hi, curve=1.0, blk=512):
    s = noise(n)
    out = np.zeros(n)
    p = np.linspace(0, 1, n) ** curve
    for i in range(0, n, blk):
        j = min(i + blk, n)
        fc = f_lo + (f_hi - f_lo) * p[i]
        out[i:j] = hpf(lpf(s[i:j], min(fc * 2.2, 19000)), fc)
    return out


def air_pass():
    d = 0.36; n = int(d * SR)
    s = band_pass_sweep(n, 1100, 4800, 1.2)
    return s * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.3 * 0.55


def slide_air():
    d = 0.5; n = int(d * SR); x = tsec(d)
    s = band_pass_sweep(n, 700, 8000, 0.8) * 0.7
    f = np.linspace(1800, 600, n)
    s += np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.18 * np.exp(-5.5 * x)
    return hpf(s * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.9, 500)


def gate_snap():
    d = 0.14; n = int(d * SR); x = tsec(d)
    s = hpf(noise(n), 3000) * 0.9
    g = np.where(x < 0.016, 1.0, np.exp(-95 * (x - 0.016)))
    s = s * g + (sine(2400, n) * 0.22 + sine(3600, n) * 0.12) * expd(n, 0.011)
    return hpf(s, 1500)


def impact_soft():
    d = 0.42; n = int(d * SR); x = tsec(d)
    f = np.linspace(100, 50, n)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-6.5 * x)
    click = hpf(noise(n), 4200) * 0.10 * np.exp(-70 * x)
    return lpf(body, 220) * 0.9 + click


def riser_short():
    d = 0.58; n = int(d * SR); x = tsec(d)
    s = band_pass_sweep(n, 800, 7000, 1.5) * 0.6
    f = np.linspace(330, 1320, n)
    s += np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.2
    s *= (x / d) ** 1.7
    s *= np.minimum((d - x) / 0.06, 1.0)
    return hpf(s, 400)


def chime_lift():
    d = 0.85; n = int(d * SR); x = tsec(d)
    s = np.zeros(n)
    for f, a, tau in ((1318.5, 0.34, 0.30), (1975.5, 0.26, 0.24), (2637.0, 0.14, 0.16), (3951.0, 0.08, 0.10), (5274.0, 0.05, 0.07)):
        s += a * np.sin(2 * np.pi * f * x) * np.exp(-x / tau)
    s += hpf(noise(n), 7000) * 0.05 * np.exp(-40 * x)
    return verb(hpf(s, 800), mix=0.26)


def tick_glass():
    d = 0.06; n = int(d * SR)
    s = sine(4800, n) * 0.40 + sine(7200, n) * 0.20 + sine(9600, n) * 0.08
    return hpf(s * expd(n, 0.011), 3000)


def count_blip():
    d = 0.05; n = int(d * SR)
    s = sine(5600, n) * 0.45 + sine(8400, n) * 0.16
    return hpf(s * expd(n, 0.009), 3500)


def net_lock():
    """An AVB stream locking — two quick rising tones then a settled third."""
    d = 0.42; n = int(d * SR); x = tsec(d)
    s = np.zeros(n)
    for k, (f, at) in enumerate(((1975.5, 0.0), (2637.0, 0.09), (3951.0, 0.18))):
        m = x >= at
        s[m] += 0.3 * np.sin(2 * np.pi * f * (x[m] - at)) * np.exp(-(x[m] - at) / (0.05 if k < 2 else 0.18))
    s += hpf(noise(n), 6000) * 0.04 * np.exp(-30 * x)
    return hpf(s, 1200)


def outro_bloom():
    d = 2.6; n = int(d * SR); x = tsec(d)
    s = np.zeros(n)
    for f, a in ((329.63, 0.30), (415.30, 0.22), (493.88, 0.20), (659.26, 0.12), (987.77, 0.06)):
        s += a * np.sin(2 * np.pi * f * x)
    s += hpf(noise(n), 5200) * 0.035
    env = np.minimum(x / 0.35, 1.0) * np.exp(-1.0 * np.maximum(x - 0.35, 0))
    return verb(hpf(s * env, 120), mix=0.34)


SOUNDS = {
    "air-pass": air_pass,
    "slide-air": slide_air,
    "gate-snap": gate_snap,
    "impact-soft": impact_soft,
    "riser-short": riser_short,
    "chime-lift": chime_lift,
    "tick-glass": tick_glass,
    "count-blip": count_blip,
    "net-lock": net_lock,
    "outro-bloom": outro_bloom,
}
RELATIVE = {
    "riser-short": 0.0,
    "chime-lift": -1.5,
    "outro-bloom": -2.0,
    "net-lock": -2.5,
    "slide-air": -3.0,
    "impact-soft": -3.5,
    "gate-snap": -4.0,
    "air-pass": -6.0,
    "tick-glass": -11.0,
    "count-blip": -13.0,
}
# ════════════════════════════════════════════════ LOUDNESS MASTERING ══
def _k_weight(x):
    """ITU-R BS.1770 K-weighting: a high-shelf then a high-pass, at 48 kHz."""
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
    a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]
    a2 = [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x))


def measure_lufs(path):
    """Integrated loudness (LUFS), BS.1770-4 with absolute and relative gating.

    The ffmpeg build in this container ships without the ebur128 filter, so the
    meter is implemented here directly: K-weighting per channel, 400 ms blocks
    at 75% overlap, -70 LUFS absolute gate, then a -10 LU relative gate.
    """
    with wave.open(path, "rb") as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64) / 32768.0
    x = x.reshape(-1, ch)
    if sr != SR:
        return None
    blk = int(0.4 * SR)
    hop = int(0.1 * SR)
    if len(x) < blk + hop:
        x = np.concatenate([x, np.zeros((blk + hop - len(x), ch))])
    kw = np.stack([_k_weight(x[:, c]) for c in range(ch)], 1)
    ms = []
    for i in range(0, len(kw) - blk + 1, hop):
        seg = kw[i:i + blk]
        ms.append(float(np.sum(np.mean(seg ** 2, axis=0))))
    ms = np.asarray(ms)
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-20))
    keep = lk > -70.0
    if not keep.any():
        return None
    rel = -0.691 + 10 * np.log10(np.mean(ms[keep])) - 10.0
    keep2 = keep & (lk > rel)
    if not keep2.any():
        return None
    return float(-0.691 + 10 * np.log10(np.mean(ms[keep2])))



def impact_deep():
    """A drop downbeat: a pitched sub thump under a short noise burst."""
    d = 0.9; n = int(d * SR); x = tsec(d)
    f = 38 + 90 * np.exp(-x / 0.045)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-3.6 * x)
    burst = lpf(noise(n), 2400) * 0.25 * np.exp(-28 * x)
    return lpf(body, 180) + burst


SOUNDS["impact-deep"] = impact_deep
RELATIVE["impact-deep"] = -1.0
