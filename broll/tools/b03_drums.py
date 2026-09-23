"""B03 — the drum room: the M6 set on a 10pre, beside the kit.

Plate: MOTU's own drum-room photograph ("MOTU M6 (4).jpg", M-Series repo). The
10pre is MOTU's hero render ("MOTU 10PRE NEWLY ADDED.jpg"), whose camera sits
within a couple of degrees of this one (top-surface depth 0.12 of the unit's
depth against 0.16 for the M6 here). It is scaled from the M6's measured width
by the real ratio of the two chassis (483 mm rack width / 283 mm), set on the
side table, and the M6 is lifted one rack unit onto it.
"""
import sys; sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M6 (4).jpg')           # 2830x2737
src10 = load(f'{AVB}/MOTU 10PRE NEWLY ADDED.jpg')

# the M6 as it sits on the table (measured on a 2x zoom)
PM6 = [(345, 1564), (697, 1564), (705, 1600), (705, 1665), (324, 1665), (324, 1600)]
m6, om6 = cut(plate, PM6, feather=0.7)
m6_w = 700 - 327
k10 = m6_w * (483 / 283) / (3687 - 122)          # 10pre front width in this plate
P10 = [(560, 622), (3245, 622), (3525, 845), (3687, 845), (3687, 1168), (122, 1168), (122, 845), (285, 845)]
c10, o10 = cut(src10, P10, feather=0.6)
c10 = scale(c10, k10)
U1 = (1168 - 845) * k10                          # one rack unit here
# tone: bring the render's front panel to the M6's front panel as lit in this room
g = match_region(src10, (2700, 870, 2900, 1150), plate, (560, 1605, 610, 1655), strength=0.85)
c10 = tone(c10, gain=g)
c10 = c10.filter(ImageFilter.GaussianBlur(0.55))   # match the plate's softer lens

x10 = 262                                        # sits inside the table's edge
y10_front_bottom = 1664
y10 = y10_front_bottom - (1168 - o10[1]) * k10

out = plate.copy()
# the jack cable's loop on the table belongs to the M6's old height: heal it out
out = clone(out, (690, 1660, 800, 1700), dx=115)
# soften the M6's LED reflections: that face is one unit higher now
out = shadow(out, [(300, 1668), (720, 1668), (720, 1712), (300, 1712)], blur=10, opacity=0.35)
# contact shadow of the 10pre on the table
out = shadow(out, [(x10 + 6, 1660), (x10 + (3687 - 122) * k10 - 6, 1660), (x10 + (3687 - 122) * k10 + 10, 1676), (x10 - 10, 1676)], blur=6, opacity=0.45)
out = paste(out, c10, (x10 + (o10[0] - 122) * k10, y10))
# the M6, lifted onto the 10pre, with its own seam shadow
out = shadow(out, [(326, 1664 - U1 - 1), (704, 1664 - U1 - 1), (704, 1664 - U1 + 6), (326, 1664 - U1 + 6)], blur=2.5, opacity=0.6)
out = paste(out, m6, (om6[0], om6[1] - U1))
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b03_full.jpg', quality=92)
f = frame_16x9(out, cx=1060, cy=1330, width=2000)   # tighter on the rig: kit to the right, table and laptop left
f = grain(f, 1.0, seed=3)
f.save('../start-frames/b03-drum-room.png')
print('k10', k10, 'U1', U1, 'gain', g)
