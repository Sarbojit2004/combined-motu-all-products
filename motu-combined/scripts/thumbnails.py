#!/usr/bin/env python3
"""Portrait (1080x1920) and landscape (1920x1080) thumbnails.

Composited from the REAL product renders only — no generated imagery, no
Shivansh or MOTU logo overlaid. A dark studio lit by the three series colours
(ember = M-Series, teal = UltraLite-mk5 / 828, indigo = AVB), the AVB rack
stack with the 828 behind, the UltraLite-mk5 and the M-Series in front, each
with a contact shadow and a floor reflection. Built at 2x and downsampled.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUB = os.path.join(ROOT, "public")
OUT = os.path.join(os.path.dirname(ROOT), "thumbnails")
os.makedirs(OUT, exist_ok=True)

EMBER, TEAL, INDIGO, GOLD = (255, 138, 76), (63, 227, 210), (139, 151, 255), (255, 194, 74)


def img(slug):
    im = Image.open(os.path.join(PUB, "img", slug + ".png")).convert("RGBA")
    return im.crop(im.getbbox())


def backdrop(W, H, floor_y):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base += np.array([10, 10, 14], np.float32)
    # Three coloured light beams from above, one per series.
    for cx, col, spread in ((0.2, EMBER, 0.22), (0.5, TEAL, 0.2), (0.8, INDIGO, 0.22)):
        dx = (x / W - cx - (y / H - 0.0) * (cx - 0.5) * 0.5) / (spread * (0.4 + y / H))
        beam = np.exp(-dx ** 2) * np.clip(1.15 - y / floor_y, 0, 1) ** 1.4 * 0.42
        base += beam[..., None] * np.array(col, np.float32)
    # A warm pool of light on the floor under the products.
    pool = np.exp(-(((x - W / 2) / (W * 0.42)) ** 2 + ((y - floor_y) / (H * 0.12)) ** 2))
    base += pool[..., None] * np.array([70, 60, 55], np.float32)
    # The floor is darker and glossier than the wall.
    fl = y > floor_y
    base[fl] *= 0.55
    # Vignette
    v = 1 - 0.55 * (((x - W / 2) / (W * 0.7)) ** 2 + ((y - H / 2) / (H * 0.75)) ** 2)
    base *= np.clip(v, 0.2, 1)[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")


def place(canvas, im, cx, bottom, width, refl=0.22, shadow=0.75):
    h = int(im.height * width / im.width)
    p = im.resize((int(width), h), Image.LANCZOS)
    x, y = int(cx - width / 2), int(bottom - h)
    # Contact shadow: a blurred dark ellipse under the unit.
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x + width * 0.04, bottom - h * 0.06, x + width * 0.96, bottom + h * 0.1], fill=(0, 0, 0, int(255 * shadow)))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(6, h * 0.08))))
    # Reflection: flipped, faded, softened.
    if refl:
        r = p.transpose(Image.FLIP_TOP_BOTTOM)
        a = np.array(r).astype(np.float32)
        fade = np.linspace(refl, 0, a.shape[0]) ** 1.3
        a[..., 3] *= fade[:, None]
        r = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        canvas.alpha_composite(r, (x, bottom))
    canvas.alpha_composite(p, (x, y))


def rim(canvas, col, strength=0.35):
    """A coloured rim light across the whole frame edge to tie the lighting together."""
    W, H = canvas.size
    g = Image.new("RGBA", canvas.size, col + (0,))
    a = np.zeros((H, W), np.float32)
    y, x = np.mgrid[0:H, 0:W]
    a = np.clip(1 - np.minimum(np.minimum(x, W - x), np.minimum(y, H - y)) / (min(W, H) * 0.08), 0, 1) * strength * 255
    g.putalpha(Image.fromarray(a.astype(np.uint8)))
    canvas.alpha_composite(g)


def text(canvas, xy, s, font, fill, shadow=8, anchor="la"):
    d = ImageDraw.Draw(canvas)
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + shadow * 0.4, xy[1] + shadow), s, font=font, fill=(0, 0, 0, 230), anchor=anchor)
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow * 0.8)))
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def chips(canvas, x, y, items, size, gap, anchor_center=False):
    f = ImageFont.truetype(os.path.join(PUB, "fonts", "display.ttf"), size)
    d = ImageDraw.Draw(canvas)
    widths = [d.textlength(t, font=f) + size * 1.2 for t, _ in items]
    total = sum(widths) + gap * (len(items) - 1)
    cx = x - total / 2 if anchor_center else x
    for (t, col), w in zip(items, widths):
        h = size * 1.9
        d.rounded_rectangle([cx, y, cx + w, y + h], radius=h / 2, fill=col + (235,))
        d.text((cx + w / 2, y + h / 2), t, font=f, fill=(255, 255, 255), anchor="mm")
        cx += w + gap


def landscape():
    S = 2
    W, H = 1920 * S, 1080 * S
    floor = int(H * 0.8)
    c = backdrop(W, H, floor)
    # Back: the AVB rack stack (16A, 848, 10pre) with the 828 on top, angled units.
    stack = [("render-16a-newly-added-3-png", 0), ("render-848-newly-added-3-png", 1), ("render-10pre-newly-added-3-png", 2), ("render-828-2-png", 3)]
    sw = int(W * 0.46)
    for slug, k in stack:
        place(c, img(slug), W * 0.33, floor - int(H * 0.012) - k * int(H * 0.118), sw, refl=0.18 if k == 0 else 0, shadow=0.55 if k == 0 else 0.25)
    # Front: UltraLite-mk5 and the M-Series.
    place(c, img("render-ultralite-mk5-6-png"), W * 0.64, floor + int(H * 0.06), int(W * 0.25))
    place(c, img("panel-m6-1-png"), W * 0.855, floor + int(H * 0.035), int(W * 0.22), refl=0.2)
    place(c, img("panel-m4-1-png"), W * 0.2, floor + int(H * 0.14), int(W * 0.2))
    place(c, img("panel-m2-2-png"), W * 0.44, floor + int(H * 0.15), int(W * 0.16))
    rim(c, INDIGO, 0.18)
    script = ImageFont.truetype(os.path.join(PUB, "fonts", "script.ttf"), 150 * S)
    disp = ImageFont.truetype(os.path.join(PUB, "fonts", "display.ttf"), 62 * S)
    small = ImageFont.truetype(os.path.join(PUB, "fonts", "display.ttf"), 34 * S)
    text(c, (int(W * 0.62), int(H * 0.08)), "THREE SERIES", disp, (251, 250, 247), anchor="la")
    text(c, (int(W * 0.6), int(H * 0.15)), "One Family", script, GOLD + (255,), shadow=12, anchor="la")
    text(c, (int(W * 0.625), int(H * 0.4)), "8 INTERFACES · 2 DSP ENGINES", small, (215, 212, 205), anchor="la")
    chips(c, int(W * 0.625), int(H * 0.47), [("M-SERIES", (194, 65, 12)), ("ULTRALITE-mk5 · 828", (14, 124, 123)), ("AVB", (52, 70, 201))], 28 * S, 14 * S)
    out = c.convert("RGB").resize((1920, 1080), Image.LANCZOS)
    out.save(os.path.join(OUT, "thumbnail-landscape-1920x1080.jpg"), quality=94)
    out.save(os.path.join(OUT, "thumbnail-landscape-1920x1080.png"))


def portrait():
    S = 2
    W, H = 1080 * S, 1920 * S
    floor = int(H * 0.74)
    c = backdrop(W, H, floor)
    stack = [("render-16a-newly-added-3-png", 0), ("render-848-newly-added-3-png", 1), ("render-10pre-newly-added-3-png", 2), ("render-828-2-png", 3)]
    sw = int(W * 0.9)
    for slug, k in stack:
        place(c, img(slug), W * 0.5, floor - int(H * 0.075) - k * int(H * 0.062), sw, refl=0, shadow=0.55 if k == 0 else 0.25)
    place(c, img("render-ultralite-mk5-6-png"), W * 0.3, floor + int(H * 0.025), int(W * 0.5))
    place(c, img("panel-m6-1-png"), W * 0.76, floor - int(H * 0.004), int(W * 0.43), refl=0.2)
    place(c, img("panel-m4-1-png"), W * 0.3, floor + int(H * 0.105), int(W * 0.44))
    place(c, img("panel-m2-2-png"), W * 0.75, floor + int(H * 0.105), int(W * 0.36))
    rim(c, INDIGO, 0.18)
    script = ImageFont.truetype(os.path.join(PUB, "fonts", "script.ttf"), 190 * S)
    disp = ImageFont.truetype(os.path.join(PUB, "fonts", "display.ttf"), 76 * S)
    small = ImageFont.truetype(os.path.join(PUB, "fonts", "display.ttf"), 36 * S)
    text(c, (W // 2, int(H * 0.075)), "THREE SERIES", disp, (251, 250, 247), anchor="ma")
    text(c, (W // 2, int(H * 0.115)), "One Family", script, GOLD + (255,), shadow=14, anchor="ma")
    text(c, (W // 2, int(H * 0.268)), "8 INTERFACES · 2 DSP ENGINES", small, (215, 212, 205), anchor="ma")
    chips(c, W // 2, int(H * 0.305), [("M-SERIES", (194, 65, 12)), ("ULTRALITE · 828", (14, 124, 123)), ("AVB", (52, 70, 201))], 30 * S, 14 * S, anchor_center=True)
    out = c.convert("RGB").resize((1080, 1920), Image.LANCZOS)
    out.save(os.path.join(OUT, "thumbnail-portrait-1080x1920.jpg"), quality=94)
    out.save(os.path.join(OUT, "thumbnail-portrait-1080x1920.png"))


if __name__ == "__main__":
    landscape()
    portrait()
    print(sorted(os.listdir(OUT)))
