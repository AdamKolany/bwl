# Favicon aus der Rosette (mkros.py, z. B. ROSETTE_N=8): A = Grau wie im Film, B = heller; dazu Vergleichsbild
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
src = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED)
lut = np.interp(np.arange(256), [0, 25, 82, 170, 255], [0, 70, 125, 225, 255]).astype(np.uint8)
srcB = src.copy(); srcB[..., :3] = cv2.LUT(src[..., :3], lut)
def prep(s):
    ys, xs = np.nonzero(s[..., 3] > 10); c = s[ys.min():ys.max()+1, xs.min():xs.max()+1]
    n = max(c.shape[:2]); pad = np.zeros((n, n, 4), np.uint8); oy, ox = (n - c.shape[0]) // 2, (n - c.shape[1]) // 2
    pad[oy:oy+c.shape[0], ox:ox+c.shape[1]] = c; m = int(n * 0.03)
    return cv2.copyMakeBorder(pad, m, m, m, m, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
def down(pad, n):
    im = pad
    while im.shape[0] > 2 * n: im = cv2.resize(im, (im.shape[1] // 2, im.shape[0] // 2), interpolation=cv2.INTER_AREA)
    return cv2.resize(im, (n, n), interpolation=cv2.INTER_AREA)
A, B = prep(src), prep(srcB)
cv2.imwrite("favicon-ros8.png", down(A, 192)); cv2.imwrite("favicon-ros8-B.png", down(B, 192))
old = cv2.imread("ros6.png", cv2.IMREAD_UNCHANGED)
def comp(icon, bgcol):
    a = icon[..., 3:] / 255.0; return (icon[..., :3] * a + np.array(bgcol, float) * (1 - a)).astype(np.uint8)
canvas = Image.new("RGB", (1120, 620), (255, 255, 255)); d = ImageDraw.Draw(canvas)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15); y = 20
for label, ic, i192 in (("jetzt (6 Arme, Penrose)", lambda n: cv2.resize(old, (n, n), interpolation=cv2.INTER_AREA), old),
                        ("neu A (8 Arme, Escher, Grau wie im Film)", lambda n: down(A, n), down(A, 192)),
                        ("neu B (8 Arme, Escher, heller)", lambda n: down(B, n), down(B, 192))):
    d.text((20, y), label, fill=(0, 0, 0), font=f); y += 24; x = 20
    for bg, txt in (((222, 225, 230), (30, 30, 30)), ((53, 54, 58), (230, 230, 230))):
        d.rounded_rectangle((x, y, x + 230, y + 34), 8, fill=bg)
        canvas.paste(Image.fromarray(cv2.cvtColor(comp(ic(16), bg[::-1]), cv2.COLOR_BGR2RGB)), (x + 10, y + 9))
        d.text((x + 34, y + 8), "Mathematisieren …", fill=txt, font=f); x += 245
    for n, k in ((16, 7), (32, 3)):
        big = cv2.resize(comp(ic(n), (255, 255, 255)), (n * k,) * 2, interpolation=cv2.INTER_NEAREST)
        canvas.paste(Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)), (x, y - 6)); x += n * k + 25
    canvas.paste(Image.fromarray(cv2.cvtColor(cv2.resize(comp(i192, (255, 255, 255)), (130, 130), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)), (x, y - 10))
    y += 175
canvas.save("favicon-vergleich.png")
