# Cheat-sheet box of the special keys, built from key images cropped out of the recording.
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/tmp/claude-1000/-home-adamkolany-------Claude--Codex---etc--MuA-mathe-C10-mathe-c10-mua-www-tests-html-cgi-bin-teste-bwl/9c1ed67d-ca4d-4254-89ec-3e65bf6dc921/scratchpad/v2dtake.mp4"
W, H = 1920, 1200
def frame(t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(12.85 + t), "-i", SRC, "-frames:v", "1", "-vf", "crop=1920:1054:0:58,pad=1920:1200:0:0:black", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
    return Image.fromarray(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy())

src = frame(45)  # no special key highlighted here
# key boxes in the 1280-wide preview, scaled by 1.5 to full resolution
K = lambda x0, y0, x1, y1: src.crop(tuple(int(v * 1.5) for v in (x0, y0, x1, y1)))
row = (484, 516)
ITEMS = [
    ([K(38, *row[:1], 96, row[1])],                 "Großbuchstaben"),
    ([K(254, row[0], 291, row[1])],                 "heraus (eine Ebene)"),
    ([K(450, row[0], 480, row[1])],                 "links löschen"),
    ([K(489, row[0], 519, row[1])],                 "rechts löschen"),
    ([K(529, row[0], 559, row[1])],                 "Auswahl löschen"),
    ([K(720, row[0], 750, row[1]), K(760, row[0], 790, row[1])], "Auswahl erweitern"),
    ([K(800, row[0], 830, row[1])],                 "alles auswählen"),
    ([K(1110, 426, 1149, 459), K(1163, 426, 1202, 459)], "Cursor bewegen"),
    ([K(1085, 341, 1152, 374)],                     "kopieren"),
    ([K(1159, 341, 1228, 374)],                     "einfügen"),
    ([K(991, row[0], 1021, row[1])],                "rückgängig"),
    ([K(1031, row[0], 1061, row[1])],               "wiederholen"),
]
F = ImageFont.truetype("/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf", 26)
FT = ImageFont.truetype("/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf", 28)
KH, ROWH, PAD, GAP, COLS = 40, 52, 22, 12, 2
def keys_img(ims):
    ims = [im.resize((int(im.width * KH / im.height), KH), Image.LANCZOS) for im in ims]
    out = Image.new("RGBA", (sum(i.width for i in ims) + 6 * (len(ims) - 1), KH), (0, 0, 0, 0))
    x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + 6
    return out
cells = [(keys_img(k), t) for k, t in ITEMS]
keyw = max(c[0].width for c in cells)
colw = keyw + GAP + max(int(F.getlength(t)) for _, t in cells)
rows = (len(cells) + COLS - 1) // COLS
bw = PAD * 2 + COLS * colw + (COLS - 1) * 28
bh = PAD * 2 + 44 + rows * ROWH
m = 16
img = Image.new("RGBA", (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([m, m + 4, m + bw, m + bh + 4], radius=22, fill=(0, 0, 0, 90))
img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
d = ImageDraw.Draw(img)
d.rounded_rectangle([m, m, m + bw, m + bh], radius=22, fill=(22, 34, 64, 235), outline=(255, 255, 255, 60), width=2)
d.text((m + PAD, m + PAD + 18), "Sondertasten", font=FT, fill=(255, 209, 102, 255), anchor="lm")
for i, (k, t) in enumerate(cells):
    c, r = i // rows, i % rows   # fill column by column
    x = m + PAD + c * (colw + 28); y = m + PAD + 44 + r * ROWH
    img.alpha_composite(k, (x + (keyw - k.width) // 2, y + (ROWH - KH) // 2))
    d.text((x + keyw + GAP, y + ROWH / 2), t, font=F, fill=(255, 255, 255, 255), anchor="lm")
img.save("legend.png")
f = frame(62).convert("RGBA")
f.alpha_composite(img, (W - img.width - 8, 150))
f.convert("RGB").resize((1280, 800)).save("legend_prev.png")
print(img.size)
