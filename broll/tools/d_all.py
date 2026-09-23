"""D02-D08 — the other seven deployment start frames (see scene.py)."""
from scene import *

P = {
    '10pre_L': lambda: product(f'{AVB}/MOTU 10PRE NEWLY ADDED.png'),
    '10pre_R': lambda: product(f'{AVB}/MOTU 10PRE NEWLY ADDED (3).png'),
    '16a_L': lambda: product(f'{AVB}/MOTU 16A NEWLY ADDED (4).png'),
    '16a_R': lambda: product(f'{AVB}/MOTU 16A NEWLY ADDED (3).png'),
    '848_R': lambda: product(f'{AVB}/MOTU 848 NEWLY ADDED (3).png'),
    '828_L': lambda: product(f'{UL}/MOTU 828 (1).png'),
    '828_R': lambda: product(f'{UL}/MOTU 828 (2).png'),
    'ul_F': lambda: product(f'{UL}/MOTU UltraLite-mk5 (6).png', floor_cut=1812),
    'ul_L': lambda: product(f'{UL}/MOTU UltraLite-mk5 (7).png', floor_cut=2482),
    'm2': lambda: keyed(f'{MS}/MOTU M2 (8).jpg'),
    'm4': lambda: keyed(f'{MS}/MOTU M4 (4).jpg', crop=(0, 0, 2102, 700)),
    'm6': m6_cut,
    'switch_F': lambda: keyed(f'{AVB}/MOTU AVB SWITCH (1).jpg', crop=(150, 150, 2250, 960)),
    'switch_3q': lambda: keyed(f'{AVB}/MOTU AVB SWITCH (2).jpg'),
}

def d02():
    # Indian classical session — tabla and sitar, evening, warm lamps
    c = gradient((0.07, 0.035, 0.015), (0.10, 0.05, 0.02))
    glow(c, 1900, 650, 1700, 700, (1.0, 0.55, 0.18), 0.35)
    glow(c, 400, 400, 700, 500, (1.0, 0.75, 0.35), 0.25)
    bokeh(c, 15, [(255, 170, 70), (255, 200, 120), (255, 120, 50), (255, 225, 170)], 40, 180, 150, 1200, 0.12, 0.45, seed=21)
    surface(c, 1320, (0.22, 0.12, 0.06), (0.09, 0.045, 0.02), spec=0.05, wood=True, seed=2)
    img = to_img(c)
    img = place(img, P['10pre_L'](), 2150, 1520, 1600, tint=(0.92, 0.84, 0.76), gamma=1.12, reflect=0.10, shadow_op=0.6, soft=0.8)
    img = place(img, P['m6'](), 1500, 2560, 1990, tint=(1.02, 0.92, 0.80), gamma=1.10, reflect=0.08, shadow_op=0.65)
    finish(img, 'd02-classical-session')

def d03():
    # House of worship — FOH desk, livestream of the service
    c = gradient((0.03, 0.025, 0.05), (0.05, 0.04, 0.06))
    glow(c, 1900, 520, 1800, 520, (0.55, 0.25, 0.95), 0.30)
    glow(c, 1900, 300, 2200, 300, (1.0, 0.80, 0.50), 0.18)
    bokeh(c, 17, [(255, 214, 150), (190, 110, 255), (120, 150, 255), (255, 240, 210)], 30, 150, 120, 1150, 0.12, 0.48, seed=31)
    surface(c, 1300, (0.06, 0.055, 0.07), (0.015, 0.014, 0.018), spec=0.06, seed=3)
    img = to_img(c)
    img = place(img, P['16a_L'](), 2200, 1500, 1580, tint=(0.93, 0.90, 1.0), reflect=0.12, shadow_op=0.55, soft=0.6)
    sw = P['switch_3q']()
    img = place(img, sw, 780, 1350, 1250, tint=(0.80, 0.78, 0.86), shadow_op=0.5, soft=0.6)
    img = place(img, P['m4'](), 1350, 2750, 1960, tint=(0.95, 0.92, 1.0), reflect=0.10, shadow_op=0.6)
    finish(img, 'd03-worship-livestream')

def d04():
    # Music school lab — bright daylight classroom
    c = gradient((0.78, 0.80, 0.82), (0.70, 0.71, 0.72))
    glow(c, 2800, 450, 1600, 700, (1.0, 1.0, 1.0), 0.25)
    bokeh(c, 13, [(255, 255, 255), (220, 235, 255), (255, 245, 225)], 60, 220, 100, 1150, 0.10, 0.28, seed=41)
    surface(c, 1320, (0.86, 0.86, 0.85), (0.70, 0.70, 0.69), spec=0.03, grain_amt=0.008, seed=4)
    img = to_img(c)
    img = place(img, P['828_L'](), 2150, 1560, 1600, tint=(1.0, 1.0, 1.0), shadow_op=0.35, soft=0.8)
    img = place(img, P['m2'](), 1300, 2700, 1980, tint=(1.0, 1.0, 1.0), shadow_op=0.4)
    finish(img, 'd04-music-school', vignette=0.2)

def d05():
    # Outdoor festival — front of house at dusk
    c = gradient((0.05, 0.07, 0.18), (0.03, 0.03, 0.06))
    glow(c, 1900, 700, 2200, 600, (0.95, 0.20, 0.75), 0.30)
    glow(c, 3300, 400, 800, 500, (0.15, 0.85, 1.0), 0.28)
    glow(c, 500, 450, 800, 500, (1.0, 0.65, 0.20), 0.22)
    bokeh(c, 20, [(255, 60, 200), (60, 220, 255), (255, 180, 60), (255, 255, 255), (150, 80, 255)], 30, 160, 100, 1150, 0.12, 0.55, seed=51)
    surface(c, 1320, (0.05, 0.05, 0.06), (0.012, 0.012, 0.014), spec=0.05, seed=5)
    img = to_img(c)
    img = place(img, P['10pre_R'](), 2150, 1600, 1600, tint=(0.95, 0.88, 1.0), reflect=0.12, shadow_op=0.55, soft=0.6)
    img = place(img, P['switch_F'](), 900, 1050, 1985, tint=(0.80, 0.78, 0.88), reflect=0.10, shadow_op=0.6)
    img = place(img, P['ul_L'](), 1250, 2950, 1960, tint=(0.95, 0.88, 1.0), reflect=0.1, shadow_op=0.6)
    finish(img, 'd05-festival-foh')

def d06():
    # Film location — sound cart at golden hour
    c = gradient((0.42, 0.30, 0.14), (0.20, 0.16, 0.08))
    glow(c, 3200, 350, 1100, 700, (1.0, 0.80, 0.40), 0.55)
    glow(c, 700, 800, 1200, 600, (0.35, 0.55, 0.25), 0.25)
    bokeh(c, 17, [(255, 220, 140), (255, 190, 90), (190, 220, 130), (255, 245, 210)], 40, 200, 80, 1150, 0.12, 0.45, seed=61)
    surface(c, 1330, (0.10, 0.09, 0.08), (0.03, 0.028, 0.025), spec=0.07, seed=6)
    img = to_img(c)
    img = place(img, P['ul_F'](), 1500, 1500, 1720, tint=(0.92, 0.86, 0.78), gamma=1.12, reflect=0.08, shadow_op=0.65)
    img = place(img, P['m2'](), 1250, 2800, 1960, tint=(1.0, 0.94, 0.86), gamma=1.05, reflect=0.08, shadow_op=0.65)
    finish(img, 'd06-film-set')

def d07():
    # Creator studio — streaming room, RGB practicals
    c = gradient((0.05, 0.02, 0.08), (0.03, 0.02, 0.05))
    glow(c, 600, 600, 1000, 700, (0.65, 0.15, 1.0), 0.40)
    glow(c, 3300, 600, 1000, 700, (0.05, 0.85, 0.85), 0.35)
    bokeh(c, 16, [(190, 70, 255), (40, 230, 220), (255, 70, 170), (255, 255, 255)], 30, 150, 120, 1150, 0.12, 0.5, seed=71)
    surface(c, 1320, (0.07, 0.05, 0.09), (0.015, 0.012, 0.02), spec=0.08, seed=7)
    img = to_img(c)
    img = place(img, P['828_R'](), 2150, 1650, 1600, tint=(0.95, 0.90, 1.02), reflect=0.12, shadow_op=0.55, soft=0.6)
    img = place(img, P['m4'](), 1350, 2750, 1970, tint=(0.95, 0.92, 1.02), reflect=0.1, shadow_op=0.6)
    finish(img, 'd07-creator-studio')

def d08():
    # Film post — Dolby Atmos mix stage, projection screen glow
    c = gradient((0.02, 0.04, 0.10), (0.02, 0.025, 0.05))
    glow(c, 1900, 450, 2300, 520, (0.20, 0.45, 1.0), 0.45)
    bokeh(c, 13, [(80, 140, 255), (40, 200, 255), (255, 190, 110), (200, 220, 255)], 30, 140, 150, 1150, 0.10, 0.42, seed=81)
    surface(c, 1320, (0.05, 0.06, 0.08), (0.012, 0.014, 0.02), spec=0.07, seed=8)
    img = to_img(c)
    img = place(img, P['848_R'](), 2200, 1520, 1600, tint=(0.88, 0.93, 1.05), reflect=0.14, shadow_op=0.55, soft=0.6)
    img = place(img, P['m6'](), 1500, 2650, 1990, tint=(0.90, 0.95, 1.08), gamma=1.05, shadow_op=0.6)
    finish(img, 'd08-atmos-post')

for f in (d02, d03, d04, d05, d06, d07, d08):
    f(); print(f.__name__)
