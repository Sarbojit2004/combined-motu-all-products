"""B07 — the gig, recorded: an M6 sitting on an 828 at the side of the stage.

Plate: MOTU's own photograph of an acoustic duo performing, an M6 on a crate at
stage right ("MOTU M6 (7).jpg", M-Series repo). The 828 is MOTU's black hero
photograph ("MOTU 828 (6).jpg", UltraLite-mk5/828 repo) — frontal, from a camera
a few degrees above, like this one — cut from its black sweep, sized from the
M6 by the two chassis' real widths, set on the crate, and the M6 lifted one rack
unit onto it. The plate is shot wide open, so the 828 is given the same softness
and the same warm, low stage light.
"""
import sys; sys.path.insert(0, '.')
from comp import *

UL = '/home/user/motu-ultralitemk5-828'
MS = '/home/user/motu-m-series-m2-m4-m6-high-end-video-shivansh-electronics-kolkata'
plate = load(f'{MS}/MOTU M6 (7).jpg')            # 3000x1740
hero = load(f'{UL}/MOTU 828 (6).jpg')             # 3839x1749

P828 = [(570, 628), (3280, 628), (3600, 850), (3722, 850), (3722, 1172), (128, 1172), (128, 850), (250, 850)]
c828, o = cut(hero, P828, feather=0.8)
m6_px_per_mm = (2742 - 2413) / 290 / np.cos(np.radians(33))   # M6 front, foreshortened ~33 deg
k = 483 * m6_px_per_mm * 0.96 / (3722 - 128)
c = scale(c828, k)
g = match_region(hero, (300, 870, 1900, 1160), plate, (2425, 1555, 2735, 1630), strength=0.85)
c = tone(c, gain=(g[0] * 1.10, g[1] * 0.97, g[2] * 0.82), gamma=1.12)   # warm, low stage light
c = c.filter(ImageFilter.GaussianBlur(2.2))
U1 = (1172 - 850) * k
front_w = (3722 - 128) * k
x828 = 2656 - front_w / 2 - (128 - o[0]) * k
y828 = 1642 - (1172 - o[1]) * k

# the M6, cut and lifted onto the 828
PM6 = [(2405, 1533), (2912, 1533), (2912, 1627), (2745, 1639), (2418, 1625), (2405, 1606)]
m6, om6 = cut(plate, PM6, feather=1.5)
out = plate.copy()
out = shadow(out, [(x828 + 10, 1636), (x828 + c.width - 10, 1636), (x828 + c.width + 20, 1660), (x828 - 20, 1660)], blur=8, opacity=0.5)
out = paste(out, c, (x828, y828))
out = shadow(out, [(2418, 1624 - U1), (2745, 1638 - U1), (2905, 1628 - U1), (2905, 1640 - U1), (2745, 1650 - U1), (2418, 1636 - U1)], blur=3, opacity=0.6)
out = paste(out, m6, (om6[0], om6[1] - U1))
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b07_full.jpg', quality=92)
f = frame_16x9(out, cx=1500, cy=870, width=3000)   # both performers and the rig: the camera move carries us to it
f = grain(f, 1.4, seed=7)
f.save('../start-frames/b07-live-duo.png')
print('k', k, 'U1', U1, 'front_w', front_w, 'gain', g)
