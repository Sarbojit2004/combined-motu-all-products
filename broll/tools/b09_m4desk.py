"""B09 — two desktops, one producer: the M4 by the laptop, the UltraLite-mk5 up front.

Plate: MOTU's own photograph of the M4 beside a laptop on a light desk against
brick ("MOTU M4 (7).jpg", M-Series repo). The UltraLite-mk5 is MOTU's complete
transparent render ("MOTU UltraLite-mk5 (6).png" — frontal, nothing cropped),
set on the empty front of the desk, sized by the chassis' real widths (216 mm
against the M4's 190 mm, a little nearer the lens), and toned to black
anodising in this warm window light — sampled off the M4's own shadow side.
"""
import sys; sys.path.insert(0, '.')
from comp import *

UL = '/home/user/motu-ultralitemk5-828'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M4 (7).jpg')              # 2880x1516
ulr = load(f'{UL}/MOTU UltraLite-mk5 (6).png')      # 4938x2532

a = np.array(ulr); a[1812:, :, 3] = 0
ulr = Image.fromarray(a).crop((430, 430, 4500, 1814))
own = np.array(ulr.convert('RGB').crop((1400, 300, 3000, 700))).reshape(-1, 3).mean(0)
target = np.array([84.0, 84.0, 88.0])   # black anodising under this warm window light (the M4's panel reads cooler: it is dark blue)
m4_front = 1130 - 310
W = 720
ul = scale(ulr, W / ulr.width)
ul = tone(ul, gain=tuple(np.clip(target / own, 0.3, 1.6)), gamma=1.12)
ul = ul.filter(ImageFilter.GaussianBlur(0.9))      # a touch nearer than the focus plane
x, yb = 250, 1402
y = yb - ul.height
out = shadow(plate, [(x + 20, yb - 8), (x + ul.width - 20, yb - 8), (x + ul.width + 40, yb + 30), (x - 30, yb + 30)], blur=14, opacity=0.5)
out = paste(out, ul, (x, y)).convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b09_full.jpg', quality=92)
f = frame_16x9(out, cx=1440, cy=758, width=2880)
f = grain(f, 1.0, seed=9)
f.save('../start-frames/b09-two-desktops.png')
print(ul.size, own, target)
