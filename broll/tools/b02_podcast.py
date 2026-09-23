"""B02 — the podcast table: the M6 records, the 848 sits behind it on the table.

Plate: MOTU's own four-seat podcast photograph ("MOTU M6 (5).jpg", M-Series repo).
The 848 is MOTU's transparent render ("MOTU 848 NEWLY ADDED (3).png"), turned
the same way as the M6 on the table. It is set down behind the laptop and the
right-hand microphone, and both are restored OVER it from the plate — so the
laptop screen hides its left end and the mic hides its right end, exactly as a
unit placed there would be hidden. What stays in view is its middle: the four
gain knobs, the talkback buttons, the display.
"""
import sys; sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M6 (5).jpg')            # 3000x2223
r848 = load(f'{AVB}/MOTU 848 NEWLY ADDED (3).png')  # 3000x771 RGBA

k = 0.226
u = scale(r848, k)
# tone the neutral render into the room's tungsten light, matched on the M6's own top surface
g = match_region(r848.convert('RGBA'), (900, 60, 1500, 160), plate, (1600, 1400, 1760, 1460), strength=0.8)
u = tone(u, gain=g, gamma=1.08)
u = u.filter(ImageFilter.GaussianBlur(0.9))          # this depth is slightly behind the focus plane
x0, y0 = 1285, 976

out = plate.copy()
# a soft occlusion shadow on the table under the unit
fb = lambda rx: y0 + (410 + rx / 2330 * 350) * k   # front-bottom edge of the unit, plate y
out = shadow(out, [(x0 + 200 * k, fb(200) - 4), (x0 + 2330 * k, fb(2330) - 4), (x0 + 2330 * k + 30, fb(2330) + 14), (x0 + 200 * k - 20, fb(200) + 12)], blur=8, opacity=0.5)
out = paste(out, u, (x0, y0))
# restore the occluders from the plate: the laptop screen, the mic, the mic's cable
occ = [
    [(0, 700), (1383, 785), (1371, 1100), (1359, 1362), (0, 1362)],
    [(1760, 1008), (1772, 996), (2030, 975), (2100, 958), (2400, 944), (2400, 1131), (2100, 1148), (1778, 1166), (1762, 1152)],
    [(1712, 898), (1742, 898), (1778, 1000), (1756, 1006)],
]
for poly in occ:
    m = poly_mask(out.size, poly, 0.8)
    out.paste(plate, (0, 0), m)
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b02_full.jpg', quality=92)
f = frame_16x9(out, cx=1500, cy=1150, width=3000)
f = grain(f, 1.0, seed=2)
f.save('../start-frames/b02-podcast-table.png')
print('gain', g)
