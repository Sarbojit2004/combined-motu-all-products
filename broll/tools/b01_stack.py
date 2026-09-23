"""B01 — the control-room stack.

Plate: MOTU's own studio shot of the 828 on a dark desk (UltraLite-mk5/828 repo,
"MOTU 828 (21).jpg"). The 16A comes from the SAME shoot ("MOTU 16A (1).jpg" in
the AVB repo: identical desk, camera, laptop and headphones), so stacking it on
the 828 is exact in light and perspective. The 10pre comes from MOTU's black
hero render ("MOTU 10PRE NEWLY ADDED.jpg"), whose 3/4 view matches to within a
pixel once scaled to the 16A's width (top-surface depth 178 px vs 179 px).
"""
import sys; sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
UL = '/home/user/motu-ultralitemk5-828'

plate = load(f'{UL}/MOTU 828 (21).jpg')          # 828 on the desk, 4000x1845
src16 = load(f'{AVB}/MOTU 16A (1).jpg')          # 16A, same desk
src10 = load(f'{AVB}/MOTU 10PRE NEWLY ADDED.jpg')  # 10pre, black hero

# ── the 16A, cut along its measured outline, lifted one rack unit ──
P16 = [(835, 921), (2982, 921), (3210, 1100), (3335, 1100), (3335, 1361), (486, 1361), (486, 1100), (608, 1100)]
c16, o16 = cut(src16, P16, feather=0.7)
U1 = 1361 - 1099            # one rack unit, measured: 16A front bottom -> 828 front top
x16, y16 = o16[0] + 4, o16[1] - U1

# ── the 10pre, cut, scaled to the 16A's front width, lifted two units ──
P10 = [(560, 622), (3245, 622), (3525, 845), (3687, 845), (3687, 1168), (122, 1168), (122, 845), (285, 845)]
c10, o10 = cut(src10, P10, feather=0.7)
k = (3335 - 486) / (3687 - 122)
c10 = scale(c10, k)
# tone-match the render to the desk shoot: top surface and front panel means
g_top = match_region(src10, (1500, 690, 1800, 790), src16, (1500, 960, 1800, 1060))
g_front = match_region(src10, (2700, 870, 2900, 1150), src16, (2700, 1120, 2900, 1340))
g = tuple((a + b) / 2 for a, b in zip(g_top, g_front))
c10 = tone(c10, gain=g)
x10 = 486 + (o10[0] - 122) * k + 4
y10 = (y16 + (1100 - o16[1])) - (1168 - o10[1]) * k   # 10pre front-bottom on 16A front-top

out = plate.copy()
# contact shadow where each unit sits on the one below (the thin dark seam)
out = shadow(out, [(490, 1097), (3334, 1097), (3334, 1104), (490, 1104)], blur=2.0, opacity=0.55)
out = paste(out, c16, (x16, y16))
top16 = y16 + (1100 - o16[1])
out = shadow(out, [(490, top16 - 3), (3334, top16 - 3), (3334, top16 + 4), (490, top16 + 4)], blur=2.0, opacity=0.55)
out = paste(out, c10, (x10, y10))
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b01_full.jpg', quality=92)
f = frame_16x9(out, cx=1910, cy=920, width=3280)
f = grain(f, 1.2, seed=1)
f.save('../start-frames/b01-control-room-stack.png')
print('gain', g, 'placed 16A', (x16, y16), '10pre', (x10, y10))
