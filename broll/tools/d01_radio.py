"""D01 — radio broadcast booth: a MOTU 848 with an UltraLite-mk5 beside it."""
from scene import *
c = gradient((0.035, 0.03, 0.04), (0.06, 0.045, 0.05))
glow(c, 3150, 520, 700, 420, (1.0, 0.08, 0.05), 0.55)     # the ON AIR lamp, far out of focus
glow(c, 700, 700, 900, 500, (0.10, 0.35, 0.95), 0.35)     # the producer's screens behind the glass
glow(c, 1950, 900, 1300, 500, (1.0, 0.62, 0.30), 0.12)    # warm desk lamp
bokeh(c, 26, [(255, 60, 40), (80, 150, 255), (255, 170, 90), (230, 230, 255)], 40, 170, 180, 1250, 0.12, 0.45, seed=3)
surface(c, 1330, (0.07, 0.065, 0.07), (0.018, 0.017, 0.02), spec=0.07, seed=1)
img = to_img(c)
p848 = product(f'{AVB}/MOTU 848 NEWLY ADDED (4).png')
pul = product(f'{UL}/MOTU UltraLite-mk5 (7).png', floor_cut=2482)
img = place(img, p848, 2250, 1640, 1640, tint=(0.95, 0.90, 0.92), reflect=0.18, shadow_op=0.55)
img = place(img, pul, 1180, 2980, 1930, tint=(0.92, 0.88, 0.90), reflect=0.14, shadow_op=0.6)
finish(img, 'd01-radio-onair')
