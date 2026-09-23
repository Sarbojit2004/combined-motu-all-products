"""B04 — the guitar rig: the 828 on the bench, an M4 on the shelf below.

Plate: MOTU's own photograph of the 828 beside a VOX AC30 ("MOTU 828 (18).jpg",
UltraLite-mk5/828 repo). The M4 is MOTU's studio photograph ("MOTU M4 (4).jpg",
M-Series repo), matted off its white sweep (only white connected to the border
is removed), sized from the 828's measured front width by the two chassis' real
widths (483 mm / 190 mm), toned into the warm shade under the bench top, and
set on the lower shelf. The coiled cable that hangs in front of the shelf is
restored over it.
"""
import sys; sys.path.insert(0, '.')
from comp import *

UL = '/home/user/motu-ultralitemk5-828'
plate = load(f'{UL}/MOTU 828 (18).jpg')             # 2500x1732
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
m4src = load(f'{MS}/MOTU M4 (4).jpg')                # 2102x1061, on white
ulr = key_bg(m4src.crop((60, 60, 2040, 667)), bg=(250, 250, 250), tol=115, soft=25)   # stop at the feet: below is the sweep's shadow
a = np.array(ulr); ys, xs = np.where(a[..., 3] > 200)
ulr = ulr.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
w828 = 1513 - 543                                    # 828 front width in the plate
k = (w828 * 190 / 483 * 1.06) / ulr.width            # the shelf sits a touch nearer the lens
ul = scale(ulr, k)
# the chassis' underside chamfer caught the white sweep; on a dark shelf it sits in shade
_a = np.array(ul).astype(np.float32); _n = _a.shape[0]; _r = np.clip((np.arange(_n) - _n * 0.90) / (_n * 0.10), 0, 1)[:, None, None]
_a[..., :3] *= 1 - 0.7 * _r; ul = Image.fromarray(_a.clip(0, 255).astype(np.uint8))
ul = tone(ul, gain=(0.93, 0.89, 0.85), gamma=1.18, lift=-0.07)   # warm bench light, deep blacks like the plate
ul = ul.filter(ImageFilter.GaussianBlur(0.6))

x_ul, y_front = 815, 882
y_ul = y_front - ul.height
base = plate.convert('RGBA')
out = shadow(base, [(x_ul + 10, y_front - 6), (x_ul + ul.width - 6, y_front - 6), (x_ul + ul.width + 30, y_front + 16), (x_ul - 14, y_front + 16)], blur=9, opacity=0.55)
out = shadow(out, [(x_ul + 40, y_ul + 10), (x_ul + ul.width + 60, y_ul + 10), (x_ul + ul.width + 70, y_front), (x_ul + ul.width, y_front)], blur=18, opacity=0.35)
out = paste(out, ul, (x_ul, y_ul))
# the coiled cable hangs in front of the shelf: put it back over the unit
reg = (770, 700, 840, 1000)
pa = np.array(plate.convert('RGB').crop(reg)).astype(np.float32)
luma = pa @ np.array([0.299, 0.587, 0.114])
m = np.clip((58 - luma) / 18, 0, 1)
m = (np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))))
patch = plate.convert('RGBA').crop(reg)
out.paste(patch, reg[:2], Image.fromarray(m))
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b04_full.jpg', quality=92)
f = frame_16x9(out, cx=1250, cy=720, width=2500)
f = grain(f, 1.0, seed=4)
f.save('../start-frames/b04-guitar-rig.png')
print('k', k, ul.size)
