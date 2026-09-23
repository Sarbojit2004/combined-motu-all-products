"""B05 — the laptop rig: a laptop on a 16A on an 828.

Both plates are from one MOTU shoot ("MOTU 16A (18).jpg" in the AVB repo and
"MOTU 828 (28).jpg" in the UltraLite-mk5/828 repo): same backdrop, same camera,
the same laptop. The laptop-on-16A block is cut from the first and set down one
rack unit higher on the second, so the 828 carries the 16A and the laptop.
"""
import sys; sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
UL = '/home/user/motu-ultralitemk5-828'
plate = load(f'{UL}/MOTU 828 (28).jpg')     # 2509x2166
src = load(f'{AVB}/MOTU 16A (18).jpg')

sc = 1250 / 2509
D = lambda x, y: (x / sc, y / sc + 300)     # measured on the 1250-wide grid view
poly = [D(*p) for p in [
    (272, 57), (970, 57), (976, 524), (1058, 598), (1168, 597), (1190, 656), (1219, 656), (1219, 769),
    (34, 769), (34, 656), (58, 656), (124, 597), (126, 574), (200, 545), (265, 524)]]
blk, o = cut(src, poly, feather=1.0)
U1 = (769 - 657) / sc                         # one rack unit in this shoot
out = plate.copy()
out = shadow(out, [D(36, 655), D(1218, 655), D(1218, 660), D(36, 660)], blur=2.5, opacity=0.6)
out = paste(out, blk, (o[0], o[1] - U1))
out = out.convert('RGB')
# the block now reaches higher: frame it with headroom above the screen
f = frame_16x9(out, cx=1254, cy=1150, width=2509)
f = grain(f, 1.0, seed=5)
f.save('../start-frames/b05-laptop-rig.png')
print('U1', U1)
