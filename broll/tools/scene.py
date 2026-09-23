"""Start frames for the deployment B-rolls: real MOTU product images, nothing else.

Each frame is a tight, shallow-depth product shot: MOTU's own studio renders
and hero photographs (untouched pixels, tone-matched to the scene's key light)
standing on a desk surface, with the room behind them thrown fully out of
focus. No MOTU lifestyle photograph is used anywhere — the room is only colour
and out-of-focus light, and Kling builds the actual deployment around the
products as its camera pulls back.
"""
import sys
sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
UL = '/home/user/motu-ultralitemk5-828'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
W, H = 3840, 2160
rng = np.random.default_rng(7)


def gradient(top, bottom, h=H, w=W):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return np.repeat(a, w, axis=1)


def glow(canvas, cx, cy, rx, ry, color, strength):
    y, x = np.ogrid[:H, :W]
    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    g = np.exp(-d * 2.2)[..., None] * strength
    canvas += g * np.array(color)[None, None, :]


def bokeh(canvas, n, colors, rmin, rmax, ymin, ymax, amin, amax, xmin=0, xmax=W, seed=0):
    r_ = np.random.default_rng(seed)
    layer = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        r = r_.uniform(rmin, rmax); x = r_.uniform(xmin, xmax); y = r_.uniform(ymin, ymax)
        c = np.array(colors[r_.integers(len(colors))]) * r_.uniform(amin, amax)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v) for v in c))
        # the bright rim a real lens gives an out-of-focus highlight
        d.ellipse([x - r, y - r, x + r, y + r], outline=tuple(int(min(255, v * 1.35)) for v in c), width=max(2, int(r * 0.06)))
    layer = layer.filter(ImageFilter.GaussianBlur(16))
    canvas += np.array(layer).astype(np.float32) / 255.0 * 0.8


def surface(canvas, y0, top_col, front_col, spec=0.0, grain_amt=0.012, wood=False, seed=0):
    """A desk surface from y0 to the bottom edge, receding into soft focus."""
    h = H - y0
    t = np.linspace(0, 1, h)[:, None, None]
    s = np.array(top_col)[None, None, :] * (1 - t) + np.array(front_col)[None, None, :] * t
    s = np.repeat(s, W, axis=1).astype(np.float32)
    r_ = np.random.default_rng(seed)
    if wood:
        # grain: long horizontal streaks, compressed toward the back by perspective
        g = r_.normal(0, 1, (h, W // 8)).astype(np.float32)
        g = np.array(Image.fromarray(((g - g.min()) / (g.max() - g.min()) * 255).astype(np.uint8)).resize((W, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255 - 0.5
        s *= (1 + 0.16 * g[..., None])
    n = r_.normal(0, grain_amt, (h, W, 1)).astype(np.float32)
    s += n
    if spec:
        # a soft specular band: the room's light caught in the finish
        band = np.exp(-((t[..., 0] - 0.18) / 0.10) ** 2)[..., None] * spec
        s += band
    # depth of field: the back of the surface is out of focus
    img = Image.fromarray((np.clip(s, 0, 1) * 255).astype(np.uint8))
    back = img.filter(ImageFilter.GaussianBlur(10))
    m = Image.fromarray((np.clip(1 - np.linspace(0, 1, h) * 2.2, 0, 1)[:, None] * 255 * np.ones((1, W))).astype(np.uint8))
    img = Image.composite(back, img, m)
    canvas[y0:] = np.array(img).astype(np.float32) / 255.0
    # the edge where the desk meets the room
    canvas[y0 - 3:y0 + 3] *= 0.85


def to_img(canvas):
    return Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)).convert('RGBA')


def product(path, crop_alpha=True, floor_cut=None):
    im = load(path)
    a = np.array(im)
    if floor_cut is not None:
        a[floor_cut:, :, 3] = 0
    ys, xs = np.where(a[..., 3] > 16)
    return Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def place(base, prod, width, cx, bottom, tint=(1, 1, 1), gamma=1.0, reflect=0.0, shadow_op=0.6, soft=0.0):
    p = scale(prod, width / prod.width)
    p = tone(p, gain=tint, gamma=gamma)
    if soft:
        p = p.filter(ImageFilter.GaussianBlur(soft))
    x = cx - p.width / 2; y = bottom - p.height
    out = base
    # contact shadow under the chassis
    out = shadow(out, [(x + p.width * 0.03, bottom - 6), (x + p.width * 0.97, bottom - 6), (x + p.width * 1.02, bottom + 26), (x - p.width * 0.02, bottom + 26)], blur=18, opacity=shadow_op)
    if reflect:
        r = p.transpose(Image.FLIP_TOP_BOTTOM)
        ra = np.array(r).astype(np.float32)
        fade = np.clip(1 - np.arange(r.height) / (r.height * 0.45), 0, 1)[:, None] ** 1.8 * reflect
        ra[..., 3] *= fade
        r = Image.fromarray(ra.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
        out = paste(out, r, (x, bottom + 2))
    return paste(out, p, (x, y))


def finish(img, name, vignette=0.35):
    a = np.array(img.convert('RGB')).astype(np.float32) / 255
    y, x = np.ogrid[:H, :W]
    v = 1 - vignette * (((x - W / 2) / (W * 0.62)) ** 2 + ((y - H * 0.52) / (H * 0.70)) ** 2)
    a *= np.clip(v, 0, 1)[..., None]
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS)
    out = grain(out, 1.3, seed=hash(name) % 1000)
    out.save(f'../deploy-frames/{name}.png')
    return out


def keyed(path, crop=None, tol=115, soft=25):
    """A studio photograph on a white sweep, matted: white connected to the border
    goes, and the sweep's shadow under the feet is cut at the chassis' last row."""
    im = load(path)
    if crop:
        im = im.crop(crop)
    rgb = np.array(im.convert('RGB')).astype(np.float32)
    dark = (rgb.mean(-1) < 110).mean(1)
    rows = np.where(dark > 0.25)[0]
    bottom = rows.max() + 1 if len(rows) else im.height
    im = im.crop((0, 0, im.width, bottom))
    k = key_bg(im, bg=(250, 250, 250), tol=tol, soft=soft)
    a = np.array(k); ys, xs = np.where(a[..., 3] > 200)
    return k.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def m6_cut():
    """The M6, cut from MOTU's frontal studio photograph along its measured outline."""
    src = load(f'{MS}/MOTU M6 (10).jpg')
    poly = [(880, 1084), (2650, 1084), (2702, 1112), (2745, 1290), (2745, 1600), (2708, 1640),
            (830, 1640), (790, 1600), (790, 1290), (832, 1112)]
    c, _ = cut(src, poly, feather=1.0)
    return c
