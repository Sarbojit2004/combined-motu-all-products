"""B10 — the network desk: CueMix Pro on the display, the AVB rig below it.

Every element is MOTU's own imagery, all shot on black, so they share one set:
  * the display running CueMix Pro   "MOTU 848 (24).jpg"
  * the 848, black hero              "MOTU 848 NEWLY ADDED (1).jpg"
  * the 16A, black hero              "MOTU 16A NEWLY ADDED.jpg"
  * the AVB Switch, studio photo     "MOTU AVB SWITCH (1).jpg" (matted off white)
The two rack units are from the same camera setup, so the 848 sits on the 16A
exactly; the 16A keeps its own reflection in the gloss desk. The switch sits on
the 848; its top face is foreshortened to the stack's viewing angle (it was
shot from higher up), and it is toned down into the display's light.
"""
import sys; sys.path.insert(0, '.')
from comp import *

AVB = '/home/user/high-end-video-motu-avb-series-16a-848-10pre-avb-switch-shivansh-electronics-kolkata'
disp = load(f'{AVB}/MOTU 848 (24).jpg')                 # 4000x2676
h848 = load(f'{AVB}/MOTU 848 NEWLY ADDED (1).jpg')      # 3839x1749
h16 = load(f'{AVB}/MOTU 16A NEWLY ADDED.jpg')           # 3839x1749
sw = load(f'{AVB}/MOTU AVB SWITCH (1).jpg')             # 2370x1218

CW, CH = 5400, 3040
canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 255))
dx, dy = 700, 60
canvas.paste(disp, (dx, dy))
# the display plate is black to its edges but not perfectly: feather its border into the canvas
m = Image.new('L', disp.size, 0); ImageDraw.Draw(m).rectangle([60, 40, disp.width - 60, disp.height - 20], fill=255)
m = m.filter(ImageFilter.GaussianBlur(30))
canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 255)); canvas.paste(disp, (dx, dy), m)

P848 = [(560, 622), (3245, 622), (3525, 845), (3687, 845), (3687, 1168), (122, 1168), (122, 845), (285, 845)]
P16 = [(545, 640), (3215, 640), (3515, 857), (3688, 857), (3688, 1181), (122, 1181), (122, 857), (282, 857)]
# the 16A with its reflection: the unit, then the gloss below it fading out
R16 = P16[:5] + [(3688, 1181), (3688, 1420), (122, 1420), (122, 1181)]
c16, o16 = cut(h16, [(545, 640), (3215, 640), (3515, 857), (3688, 857), (3688, 1420), (122, 1420), (122, 857), (282, 857)], feather=0.8)
a = np.array(c16).astype(np.float32)
ys = np.arange(a.shape[0])[:, None] + o16[1]
fade = np.clip(1 - (ys - 1182) / 238, 0, 1) ** 1.6 * 0.55
a[..., 3] = np.where(ys > 1182, a[..., 3] * fade, a[..., 3])
c16 = Image.fromarray(a.clip(0, 255).astype(np.uint8))
c848, o848 = cut(h848, P848, feather=0.8)

W = 2700
k = W / (3688 - 122)
c16 = scale(c16, k); c848 = scale(c848, k)
x0 = (CW - W) / 2 + 60
front_bottom = 2880
y16 = front_bottom - (1181 - o16[1]) * k
top16 = front_bottom - (1181 - 857) * k
y848 = top16 - (1168 - o848[1]) * k
top848 = top16 - (1168 - 845) * k

# the switch: matte, then foreshorten its top face to this viewing angle
PS = [(565, 300), (1835, 300), (2075, 570), (2072, 880), (2040, 902), (348, 902), (300, 880), (296, 570)]
csw, osw = cut(sw, PS, feather=0.8)
top_h = 570 - osw[1]; front_h = csw.height - top_h
top = csw.crop((0, 0, csw.width, top_h)).resize((csw.width, int(top_h * 0.62)), Image.LANCZOS)
front = csw.crop((0, top_h, csw.width, csw.height))
csw = Image.new('RGBA', (csw.width, top.height + front.height), (0, 0, 0, 0))
csw.paste(top, (0, 0)); csw.paste(front, (0, top.height))
ks = (W * 210 / 483) / (2075 - 296)
csw = scale(csw, ks)
g = match_region(sw, (700, 620, 1700, 860), h848, (900, 900, 1500, 1100), strength=0.9)
csw = tone(csw, gain=g, gamma=1.08)
xs = x0 + W * 0.50
ys_ = top848 - (845 - 622) * k * 0.30 - csw.height   # on the 848's lid, a third of the way back

out = canvas
out = paste(out, c16, (x0 + (o16[0] - 122) * k, y16))
out = shadow(out, [(x0 + 8, top16 - 3), (x0 + W - 8, top16 - 3), (x0 + W - 8, top16 + 5), (x0 + 8, top16 + 5)], blur=2.5, opacity=0.7)
out = paste(out, c848, (x0 + (o848[0] - 122) * k, y848))
out = shadow(out, [(xs + 10, ys_ + csw.height - 6), (xs + csw.width - 10, ys_ + csw.height - 6), (xs + csw.width + 10, ys_ + csw.height + 12), (xs - 10, ys_ + csw.height + 12)], blur=8, opacity=0.6)
out = paste(out, csw, (xs, ys_))
out = out.convert('RGB')
out.save('/tmp/claude-0/-home-user/fa82db52-803f-58e4-81e2-4e4805054d38/scratchpad/b10_full.jpg', quality=92)
f = out.resize((1920, round(1920 * CH / CW)), Image.LANCZOS)
f = f.crop((0, (f.height - 1080) // 2, 1920, (f.height - 1080) // 2 + 1080))
f = grain(f, 1.2, seed=10)
f.save('../start-frames/b10-network-desk.png')
print(f.size, 'switch gain', g)
