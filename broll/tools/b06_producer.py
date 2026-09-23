"""B06 — the producer's desk: the M2 up front, the UltraLite-mk5 beside the laptop.

Plate: MOTU's own photograph of the M2 in front of a laptop on a wooden desk
("MOTU M2 (1).jpg", M-Series repo). The UltraLite-mk5 is MOTU's complete
transparent render ("MOTU UltraLite-mk5 (6).png" — frontal, nothing cropped),
set down on the empty right half of the desk, a little further from the lens
than the M2 and in front of the laptop, toned to black anodising in daylight.
"""
import sys; sys.path.insert(0, '.')
from comp import *

UL = '/home/user/motu-ultralitemk5-828'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M2 (1).jpg')              # 2880x1396
ulr = load(f'{UL}/MOTU UltraLite-mk5 (6).png')      # 4938x2532

a = np.array(ulr); a[1812:, :, 3] = 0               # drop the render's floor reflection
ulr = Image.fromarray(a).crop((430, 430, 4500, 1814))
top = np.array(ulr.convert('RGB').crop((1400, 300, 3000, 700))).reshape(-1, 3).mean(0)
target = np.array([88, 92, 102])                     # black anodising in this light (the laptop hinge, the M2's shadow side)
W = 960
ul = scale(ulr, W / ulr.width)
ul = tone(ul, gain=tuple(target / top), gamma=1.0)
ul = ul.filter(ImageFilter.GaussianBlur(0.8))        # a touch behind the M2's focus plane
x, yb = 1548, 1150
y = yb - ul.height
out = shadow(plate, [(x + 30, yb - 10), (x + W - 30, yb - 10), (x + W + 50, yb + 30), (x - 40, yb + 30)], blur=16, opacity=0.5)
out = shadow(out, [(x + W - 60, y + 60), (x + W + 90, y + 90), (x + W + 90, yb + 20), (x + W - 40, yb)], blur=30, opacity=0.25)
out = paste(out, ul, (x, y)).convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b06_full.jpg', quality=92)
f = frame_16x9(out, cx=1291, cy=698, width=2880)
f = grain(f, 1.0, seed=6)
f.save('../start-frames/b06-producer-desk.png')
print('gain', target / top, ul.size)
