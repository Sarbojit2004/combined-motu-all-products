"""B08 — songwriting on the couch: an M6 and an UltraLite-mk5 side by side.

Plate: MOTU's own photograph of an M6 on a grey couch with a guitar, a mic and
an iPad ("MOTU M6 (9).jpg", M-Series repo). The UltraLite-mk5 is MOTU's
complete transparent 3/4 render ("MOTU UltraLite-mk5 (7).png"), turned the same
way as the M6, set on the cushion to its right, sized by the two chassis' real
widths (the UltraLite's 216 mm against the M6's 283 mm), and given the couch's
soft window light and a contact shadow in the fabric.
"""
import sys; sys.path.insert(0, '.')
from comp import *

UL = '/home/user/motu-ultralitemk5-828'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M6 (9).jpg')                  # 2830x2737
ulr = load(f'{UL}/MOTU UltraLite-mk5 (7).png')          # 5000x3127

a = np.array(ulr)
# keep the product, drop the render's floor reflection (below the chassis' bottom edge)
ys, xs = np.where(a[..., 3] > 200)
ulr = Image.fromarray(a).crop((432, 614, 4542, 2481))
# front width of the M6 as seen here (1253..2120 on the front face, turned ~20 deg)
m6_front = 2120 - 1253
W = m6_front * (216 / 283) * 1.22                        # whole render width incl. the receding side
ul = scale(ulr, W / ulr.width)
ref = np.array(plate.convert('RGB').crop((1450, 1450, 1900, 1560))).reshape(-1, 3).mean(0)   # the M6's lit top
own = np.array(ulr.convert('RGB').crop((1500, 300, 3000, 700))).reshape(-1, 3).mean(0)
ul = tone(ul, gain=tuple(np.clip(ref / own, 0.4, 1.8)))
ul = ul.filter(ImageFilter.GaussianBlur(0.9))
x, yb = 2012, 1985
y = yb - ul.height
out = shadow(plate, [(x + 40, yb - 40), (x + ul.width - 80, yb - 150), (x + ul.width + 20, yb - 110), (x + 60, yb + 20)], blur=22, opacity=0.5)
out = paste(out, ul, (x, y)).convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b08_full.jpg', quality=92)
f = frame_16x9(out, cx=1415, cy=1560, width=2830)
f = grain(f, 1.0, seed=8)
f.save('../start-frames/b08-couch-writing.png')
print(ul.size, ref, own)
