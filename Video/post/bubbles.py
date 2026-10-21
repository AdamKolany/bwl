# Speech-bubble subtitles placed just above the answer field.
import sys, re, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont

SRC = "/tmp/claude-1000/-home-adamkolany-------Claude--Codex---etc--MuA-mathe-C10-mathe-c10-mua-www-tests-html-cgi-bin-teste-bwl/9c1ed67d-ca4d-4254-89ec-3e65bf6dc921/scratchpad/v2dtake.mp4"
W, H, FPS = 1920, 1200, 30
SIZE = 40
FONTS = ["/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf"]
FILL, TEXT, ACCENT = (22, 34, 64, 235), (255, 255, 255, 255), (255, 209, 102, 255)
MAXW, PADX, PADY, LINE = 1040, 34, 14, 54
INTRO_Y = 324   # "[ Aufgabenauswahl / Ableitungen ] Menu" line while the page is unscrolled
FADE = 0.2

fonts = [(ImageFont.truetype(f, SIZE), TTFont(f)["cmap"].getBestCmap()) for f in FONTS]
def font_for(ch):
    for f, cm in fonts:
        if ord(ch) in cm: return f
    return fonts[0][0]

def runs(text):
    """Split into (string, font, colour) runs; quoted words and key symbols get the accent colour."""
    out, quoted = [], False
    for ch in text:
        if ch == "„": quoted = True
        f = font_for(ch)
        col = ACCENT if (quoted or f is not fonts[0][0]) and not ch.isspace() else TEXT
        if ch == "“": quoted = False
        if out and out[-1][1] is f and out[-1][2] == col: out[-1][0] += ch
        else: out.append([ch, f, col])
    return out

def width(s): return sum(f.getlength(t) for t, f, _ in runs(s))

def wrap(text, maxw=MAXW):
    words, lines = text.split(" "), [""]
    for w in words:
        cand = (lines[-1] + " " + w).strip()
        if width(cand) <= maxw or not lines[-1]: lines[-1] = cand
        else: lines.append(w)
    if len(lines) == 2:  # balance two lines
        best = min(range(1, len(words)), key=lambda k: max(width(" ".join(words[:k])), width(" ".join(words[k:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    return lines

def bubble(text, maxw=MAXW):
    lines = wrap(text, maxw)
    tw = max(width(l) for l in lines)
    bw, bh = int(tw + 2 * PADX), int(len(lines) * LINE + 2 * PADY)
    m = 18  # room for shadow
    img = Image.new("RGBA", (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([m, m + 4, m + bw, m + bh + 4], radius=min(bh // 2, 40), fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m, m, m + bw, m + bh], radius=min(bh // 2, 40), fill=FILL, outline=(255, 255, 255, 60), width=2)
    for i, l in enumerate(lines):
        x = m + (bw - width(l)) / 2
        y = m + PADY + i * LINE + LINE / 2
        for t, f, col in runs(l):
            d.text((x, y), t, font=f, fill=col, anchor="lm")
            x += f.getlength(t)
    return img

def srt(path):
    ts = lambda s: (lambda h, m, r: int(h) * 3600 + int(m) * 60 + float(r.replace(",", ".")))(*s.split(":"))
    cues = []
    for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
        l = b.split("\n"); a, c = l[1].split(" --> ")
        cues.append((ts(a), ts(c), " ".join(l[2:])))
    return cues

def field_track():
    """Field top per 0.25 s, with detection glitches (1054 = black pad) and blips < 0.5 s removed."""
    r = np.load("/tmp/mb/field.npy")
    ys = [int(y) for _, y in r]
    for i, y in enumerate(ys):
        if y in (-1, 1054): ys[i] = ys[i - 1] if i else 924
    segs = []
    for y in ys:
        if segs and segs[-1][0] == y: segs[-1][1] += 1
        else: segs.append([y, 1])
    out = []
    for y, n in segs:
        if n < 2 and out: out[-1][1] += n
        elif out and out[-1][0] == y: out[-1][1] += n
        else: out.append([y, n])
    track = []
    for y, n in out: track += [y] * n
    return track

TRACK = field_track()
def field_top(t): return TRACK[min(int(t * 4), len(TRACK) - 1)]

def intro(t): return field_top(t) > 800   # page not yet scrolled to the answer field
CUES = [(a, c, bubble(s, 1800 if intro(a) else MAXW)) for a, c, s in srt("/tmp/mb/subs.srt")]

def place(img, t):
    x = W // 2 - img.width // 2
    if intro(t): return x, INTRO_Y - img.height // 2
    return x, field_top(t) - 40 - (img.height - 18)

def composite(frame, t):
    for a, c, img in CUES:
        if a <= t < c:
            al = min(1, (t - a) / FADE, (c - t) / FADE)
            x, y = place(img, t)
            arr = np.asarray(img, dtype=np.float32)
            y0, x0 = max(y, 0), max(x, 0)
            sub = arr[y0 - y: min(H - y, arr.shape[0]), x0 - x: min(W - x, arr.shape[1])]
            reg = frame[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]].astype(np.float32)
            A = sub[..., 3:4] / 255 * al
            frame[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = (reg * (1 - A) + sub[..., :3] * A).astype(np.uint8)
    return frame

def decode(ss=0, n=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(12.85 + ss), "-i", SRC, "-vf", f"crop=1920:1054:0:58,pad=1920:1200:0:0:black,fps={FPS}", "-pix_fmt", "rgb24", "-f", "rawvideo"]
    if n: cmd += ["-frames:v", str(n)]
    return subprocess.Popen(cmd + ["-"], stdout=subprocess.PIPE)

if sys.argv[1] == "preview":
    for t in map(float, sys.argv[2:]):
        p = decode(t, 1); f = np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).copy()
        Image.fromarray(composite(f, t)).resize((1280, 800)).save(f"/tmp/mb/prev_{int(t)}.png")
else:
    out = sys.argv[2]
    p = decode()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    i = 0
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        enc.stdin.write(composite(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(), i / FPS).tobytes()); i += 1
    enc.stdin.close(); enc.wait(); print("frames", i)
