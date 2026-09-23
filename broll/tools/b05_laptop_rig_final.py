import sys; sys.path.insert(0, '.')
exec(open('b05_laptop_rig.py').read().split("out = out.convert('RGB')")[0])
Y0 = 110
out = out.convert('RGB').crop((0, Y0, 2509, 1935))
keep = [[(x, y - Y0) for x, y in pts] for pts in [
    [(60, 1170), (2460, 1170), (2460, 1860), (60, 1860)],
    [(p[0], p[1] - U1) for p in poly]]]
ext = extend_canvas(out, left=410, right=410, seed=3, keep=keep)
f = frame_16x9(ext, cx=ext.width / 2, cy=ext.height / 2, width=ext.width)
f.save('../start-frames/b05-laptop-rig.png')
