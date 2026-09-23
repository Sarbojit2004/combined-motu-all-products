"""Compositing helpers for the B-roll start frames.

Every start frame is built from the REAL product photography in the three MOTU
repositories — no generated imagery. Boxy hardware is cut out along a
hand-measured polygon (supersampled for an anti-aliased edge), matched to the
light of the plate it lands in, and given a contact shadow. Nothing here
redraws a product: pixels are only moved, scaled and tone-matched.
"""
from __future__ import annotations
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling for polygon masks


def load(path: str) -> Image.Image:
    im = Image.open(path)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    return im.convert("RGBA")


def poly_mask(size, pts, feather: float = 0.8) -> Image.Image:
    """Anti-aliased polygon mask at `size`, points in pixel coords."""
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return m


def cut(img: Image.Image, pts, feather: float = 0.8) -> tuple[Image.Image, tuple[int, int]]:
    """Cut `img` along polygon `pts`; returns the RGBA cutout cropped to its box and the box origin."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = int(max(0, min(xs) - 4)), int(max(0, min(ys) - 4))
    x1, y1 = int(min(img.width, max(xs) + 4)), int(min(img.height, max(ys) + 4))
    sub = img.crop((x0, y0, x1, y1)).convert("RGBA")
    m = poly_mask(sub.size, [(x - x0, y - y0) for x, y in pts], feather)
    a = np.array(sub)
    a[..., 3] = (a[..., 3].astype(np.float32) * (np.array(m).astype(np.float32) / 255)).astype(np.uint8)
    return Image.fromarray(a), (x0, y0)


def key_bg(img: Image.Image, bg=None, tol: float = 18.0, soft: float = 14.0, flood=True) -> Image.Image:
    """Matte a product off a uniform studio background (white / grey sweep).

    The background colour is estimated from the border when not given. Pixels
    within `tol` of it become transparent, ramping to opaque over `soft`. With
    `flood`, only background CONNECTED to the border is removed, so a grey
    panel inside the product can never be keyed out.
    """
    a = np.array(img.convert("RGB")).astype(np.float32)
    h, w, _ = a.shape
    if bg is None:
        border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
        bg = np.median(border, axis=0)
    d = np.sqrt(((a - np.array(bg)) ** 2).sum(-1))
    alpha = np.clip((d - tol) / soft, 0, 1)
    if flood:
        from scipy import ndimage
        near = d < tol + soft
        lab, n = ndimage.label(near)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        conn = np.isin(lab, list(edge))
        alpha = np.where(conn, alpha, 1.0)
    out = np.dstack([a, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def tone(img: Image.Image, gain=(1, 1, 1), lift=0.0, gamma=1.0, sat=1.0) -> Image.Image:
    """Per-channel gain, black lift, gamma and saturation — alpha untouched."""
    a = np.array(img).astype(np.float32)
    rgb = a[..., :3] / 255.0
    rgb = np.clip(rgb * np.array(gain), 0, 1)
    if gamma != 1.0:
        rgb = rgb ** gamma
    if sat != 1.0:
        l = (rgb * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
        rgb = np.clip(l + (rgb - l) * sat, 0, 1)
    rgb = lift + rgb * (1 - lift)
    a[..., :3] = rgb * 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def match_region(src: Image.Image, src_box, ref: Image.Image, ref_box, strength=1.0):
    """Channel gains that bring src_box's mean colour to ref_box's mean colour."""
    s = np.array(src.convert("RGB").crop(src_box)).reshape(-1, 3).mean(0) + 1e-3
    r = np.array(ref.convert("RGB").crop(ref_box)).reshape(-1, 3).mean(0)
    g = r / s
    return tuple(1 + (g - 1) * strength)


def scale(img: Image.Image, f: float) -> Image.Image:
    return img.resize((max(1, round(img.width * f)), max(1, round(img.height * f))), Image.LANCZOS)


def shadow(base: Image.Image, pts, blur: float, opacity: float, offset=(0, 0)) -> Image.Image:
    """Darken the plate under a polygon (contact shadow / occlusion)."""
    m = poly_mask(base.size, [(x + offset[0], y + offset[1]) for x, y in pts], 0).filter(ImageFilter.GaussianBlur(blur))
    a = np.array(base).astype(np.float32)
    k = 1 - (np.array(m).astype(np.float32) / 255 * opacity)[..., None]
    a[..., :3] *= k
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), base.mode)


def paste(base: Image.Image, cut_img: Image.Image, xy) -> Image.Image:
    out = base.convert("RGBA").copy()
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(cut_img, (round(xy[0]), round(xy[1])), cut_img)
    return Image.alpha_composite(out, layer)


def perspective_coeffs(src, dst):
    """Coefficients for Image.transform(PERSPECTIVE) mapping dst quad -> src quad."""
    A = []; B = []
    for (xs, ys), (xd, yd) in zip(src, dst):
        A.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd]); B.append(xs)
        A.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd]); B.append(ys)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp_onto(base: Image.Image, src_img: Image.Image, src_quad, dst_quad) -> Image.Image:
    """Perspective-warp src_img so src_quad lands on dst_quad of base, then composite."""
    c = perspective_coeffs(src_quad, dst_quad)
    w = src_img.convert("RGBA").transform(base.size, Image.PERSPECTIVE, c, Image.BICUBIC)
    return Image.alpha_composite(base.convert("RGBA"), w)


def grain(img: Image.Image, amount=2.0, seed=0) -> Image.Image:
    rng = np.random.default_rng(seed)
    a = np.array(img.convert("RGB")).astype(np.float32)
    a += rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def frame_16x9(img: Image.Image, cx: float, cy: float, width: float, out=(1920, 1080)) -> Image.Image:
    """Crop a 16:9 window of `width` px centred at (cx, cy) and resize to `out`."""
    width = min(width, img.width, img.height * 16 / 9)   # never sample outside the plate
    h = width * 9 / 16
    x0 = max(0, min(img.width - width, cx - width / 2))
    y0 = max(0, min(img.height - h, cy - h / 2))
    return img.crop((round(x0), round(y0), round(x0 + width), round(y0 + h))).resize(out, Image.LANCZOS)


def extend_canvas(img: Image.Image, left: int, right: int, top: int = 0, bottom: int = 0, blur: float = 40, seed: int = 0, keep=None) -> Image.Image:
    """Widen a plate whose edges are plain backdrop (seamless-studio walls, dark desks).

    Each new column is the plate's own edge band, heavily blurred vertically so
    no detail is duplicated, with matched grain. Only ever used where the edge
    of the photograph is empty backdrop — never through a product.
    """
    rgb = img.convert("RGB")
    W, H = rgb.size
    out = Image.new("RGB", (W + left + right, H + top + bottom))
    out.paste(rgb, (left, top))
    a = np.array(out).astype(np.float32)
    band0, band1 = 40, 160   # sample inside the photo's own edge vignette
    if left:
        edge = np.array(rgb.crop((band0, 0, band1, H))).astype(np.float32).mean(1)  # H x 3
        a[top:top + H, :left] = edge[:, None, :]
    if right:
        edge = np.array(rgb.crop((W - band1, 0, W - band0, H))).astype(np.float32).mean(1)
        a[top:top + H, left + W:] = edge[:, None, :]
    if top:
        a[:top] = a[top:top + 1]
    if bottom:
        a[top + H:] = a[top + H - 1:top + H]
    ext = Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    # keep the original pixels exactly; feather the join over 60 px
    m = Image.new("L", out.size, 0)
    ImageDraw.Draw(m).rectangle([left + 110, top + (60 if top else 0), left + W - 110, top + H - (60 if bottom else 0) - 1], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(45))
    if keep:  # product silhouettes keep their exact pixels, whatever the feather says
        k = Image.new("L", out.size, 0)
        for poly in keep:
            ImageDraw.Draw(k).polygon([(x + left, y + top) for x, y in poly], fill=255)
        m = Image.fromarray(np.maximum(np.array(m), np.array(k.filter(ImageFilter.GaussianBlur(1.5)))))
    res = Image.composite(out, ext, m)
    return grain(res, 1.6, seed)


def clone(base: Image.Image, dst_box, dx: int, dy: int = 0, feather: float = 6) -> Image.Image:
    """Heal a small patch by cloning plate texture from (dx, dy) away, feathered."""
    x0, y0, x1, y1 = dst_box
    src = base.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rectangle([feather, feather, x1 - x0 - feather, y1 - y0 - feather], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather / 2))
    out = base.copy()
    out.paste(src, (x0, y0), m)
    return out
