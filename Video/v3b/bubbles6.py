# v03_07: Owal um die Zielformel bei Blase 2
# v03_06: Aufnahme per Umgebung (TAKE, SS), Vorführ-Umrandungen relativ zu Blase 3
# v03_04: neue Aufnahme v5take (Überblick an der fertigen Formel)
# v03_03: + Vorführ-Umrandungen bei Blase 3, weitere Hilfetext-Beispiele bei Blase 5, Untertitel-Datei per Umgebungsvariable SRT
# v03: Untertitel-Sprechblasen über dem Antwortfeld + Zielformel oben (aus dem Anfang
# der Aufnahme ausgeschnitten) + Sondertasten-Legende im schwarzen Streifen unten.
import sys, os, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont

D = "/tmp/mb4"; TAKE = os.environ.get("TAKE", "v6take"); SRT = os.environ.get("SRT", f"{D}/{TAKE}.srt"); SRC = f"{D}/{TAKE}.mp4"; SS = float(os.environ["SS"])
W, H, FPS = 1920, 1200, 30
LAY = json.load(open(f"{D}/{TAKE}.layout.json"))
SIZE = 40
FONTS = ["/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf"]
FILL, TEXT, ACCENT = (22, 34, 64, 235), (255, 255, 255, 255), (255, 209, 102, 255)
MAXW, PADX, PADY, LINE = 1040, 34, 14, 54
INTRO_Y = 324
FADE = 0.2
VF = "crop=1920:1054:0:58,pad=1920:1200:0:0:black"

fonts = [(ImageFont.truetype(f, SIZE), TTFont(f)["cmap"].getBestCmap()) for f in FONTS]
def font_for(ch, fl=fonts):
    for f, cm in fl:
        if ord(ch) in cm: return f
    return fl[0][0]
def runs(text, fl=fonts):
    out, quoted = [], False
    for ch in text:
        if ch == "„": quoted = True
        f = font_for(ch, fl)
        col = ACCENT if (quoted or f is not fl[0][0]) and not ch.isspace() else TEXT
        if ch == "“": quoted = False
        if out and out[-1][1] is f and out[-1][2] == col: out[-1][0] += ch
        else: out.append([ch, f, col])
    return out
def width(s, fl=fonts): return sum(f.getlength(t) for t, f, _ in runs(s, fl))
def wrap(text, maxw=MAXW):
    words, lines = text.split(" "), [""]
    for w in words:
        cand = (lines[-1] + " " + w).strip()
        if width(cand) <= maxw or not lines[-1]: lines[-1] = cand
        else: lines.append(w)
    if len(lines) == 2:
        best = min(range(1, len(words)), key=lambda k: max(width(" ".join(words[:k])), width(" ".join(words[k:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    return lines
def panel(bw, bh, fill=FILL, outline=(255, 255, 255, 60), radius=None, m=18):
    img = Image.new("RGBA", (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); r = radius if radius is not None else min(bh // 2, 40)
    ImageDraw.Draw(sh).rounded_rectangle([m, m + 4, m + bw, m + bh + 4], radius=r, fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(img).rounded_rectangle([m, m, m + bw, m + bh], radius=r, fill=fill, outline=outline, width=2)
    return img
def bubble(text, maxw=MAXW, lines=None):
    lines = lines or wrap(text, maxw)
    tw = max(width(l) for l in lines)
    bw, bh = int(tw + 2 * PADX), int(len(lines) * LINE + 2 * PADY); m = 18
    img = panel(bw, bh); d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = m + (bw - width(l)) / 2; y = m + PADY + i * LINE + LINE / 2
        for t, f, col in runs(l):
            d.text((x, y), t, font=f, fill=col, anchor="lm"); x += f.getlength(t)
    return img, len(lines)

def srt(path):
    ts = lambda s: (lambda h, m, r: int(h) * 3600 + int(m) * 60 + float(r.replace(",", ".")))(*s.split(":"))
    cues = []
    for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
        l = b.split("\n"); a, c = l[1].split(" --> "); cues.append((ts(a), ts(c), " ".join(l[2:])))
    return cues

def field_track():
    r = np.load(f"{D}/field.npy"); ys = [int(y) for _, y in r]
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
def intro(t): return field_top(t) > 800

def frame(t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(SS + t), "-i", SRC, "-frames:v", "1", "-vf", VF, "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
    return Image.fromarray(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy())

# --- Zielformel oben -------------------------------------------------------
def goal_panel():
    fx = frame(3.0).crop(tuple(LAY["formula"])).convert("RGBA")
    fh = 100; fx = fx.resize((int(fx.width * fh / fx.height), fh), Image.LANCZOS)
    lf = ImageFont.truetype(FONTS[0], 30); lab = "Ziel:"; lw = int(lf.getlength(lab))
    bw, bh = 22 + lw + 18 + fx.width + 22, fh + 16; m = 12
    img = panel(bw, bh, fill=(255, 251, 230, 250), outline=(217, 164, 0, 255), radius=18, m=m)
    d = ImageDraw.Draw(img); d.text((m + 22, m + bh / 2), lab, font=lf, fill=(120, 90, 0, 255), anchor="lm")
    img.alpha_composite(fx, (m + 22 + lw + 18, m + 8))
    return img
# --- Legende unten ---------------------------------------------------------
def legend_panel():
    src = frame(LAY["scrolled_at"] + 2.0); K = LAY["keys"]
    ITEMS = [(["capsCycle"], "Großbuchstaben"), (["exitCtx"], "heraus"), (["bs"], "links löschen"),
             (["del"], "rechts löschen"), (["clear"], "Auswahl löschen"), (["selL", "selR"], "Auswahl erweitern"),
             (["selectAll"], "alles auswählen"), (["move_L", "move_R"], "Cursor bewegen"), (["copy"], "kopieren"),
             (["paste"], "einfügen"), (["undo"], "rückgängig"), (["redo"], "wiederholen")]
    F = ImageFont.truetype(FONTS[0], 24); KH, ROWH, PAD, GAP, CG, COLS = 34, 52, 14, 10, 22, 6
    def keys_img(cs):
        ims = [src.crop(tuple(K[c])) for c in cs]
        ims = [i.resize((int(i.width * KH / i.height), KH), Image.LANCZOS) for i in ims]
        out = Image.new("RGBA", (sum(i.width for i in ims) + 5 * (len(ims) - 1), KH), (0, 0, 0, 0)); x = 0
        for i in ims: out.paste(i, (x, 0)); x += i.width + 5
        return out
    cells = [(keys_img(k), t) for k, t in ITEMS]
    cols = [cells[c::COLS] for c in range(COLS)]                     # zeilenweise füllen
    kw = [max(c[0].width for c in col) for col in cols]
    tw = [max(int(F.getlength(c[1])) for c in col) for col in cols]
    bw = PAD * 2 + sum(kw) + sum(tw) + COLS * GAP + (COLS - 1) * CG; bh = PAD * 2 + 2 * ROWH - 8; m = 10
    img = panel(bw, bh, radius=18, m=m); d = ImageDraw.Draw(img)
    x = m + PAD
    for ci, col in enumerate(cols):
        for ri, (k, t) in enumerate(col):
            y = m + PAD - 4 + ri * ROWH
            img.alpha_composite(k, (x + (kw[ci] - k.width) // 2, y + (ROWH - KH) // 2))
            d.text((x + kw[ci] + GAP, y + ROWH / 2), t, font=F, fill=(255, 255, 255, 255), anchor="lm")
        x += kw[ci] + GAP + tw[ci] + CG
    if img.width > W - 12: img = img.resize((W - 12, int(img.height * (W - 12) / img.width)), Image.LANCZOS)
    return img

GOAL = goal_panel(); LEG = legend_panel()
GOAL_XY = ((W - GOAL.width) // 2, -4)
LEG_XY = ((W - LEG.width) // 2, 984 - 10)   # v03_02: höher, verdeckt die (kaum genutzte) Leertaste
OVERLAYS = [(GOAL, GOAL_XY, LAY["scrolled_at"] + 0.8), (LEG, LEG_XY, LAY["legend_at"])]

# Zeilenumbrüche von Hand: Blasen.txt (### Nr Zeit, dann die Zeilen der Blase)
def manual_lines(path):
    out, cur = {}, None
    for l in open(path, encoding="utf-8").read().split("\n"):
        if l.startswith("# "): continue
        if l.startswith("###"): cur = int(l.split()[1]); out[cur] = []
        elif cur is not None and l.strip(): out[cur].append(" ".join(l.split()))   # Mehrfach-Leerzeichen → eines
    return out
MANUAL = manual_lines(sys.argv[3]) if len(sys.argv) > 3 else {}
CUES = []
for i, (a, c, s) in enumerate(srt(SRT), 1):
    mw = 1800 if intro(a) else MAXW
    ls = MANUAL.get(i)
    if ls:
        if " ".join(ls).split() != s.split(): print(f"Hinweis Blase {i:02d}: Text weicht vom Untertitel ab", file=sys.stderr)
        for l in ls:
            if width(l) > W - 120: print(f"WARNUNG Blase {i:02d}: Zeile zu breit ({int(width(l))} px): {l}", file=sys.stderr)
    img, n = bubble(s, mw, ls); CUES.append((a, c, img, n))

# Vorführung zu „… farbig umrandet“: einige Tasten nacheinander umranden wie in der App
# (Rand 7 px außerhalb der Taste, 6 px Magenta, weicher Schein).  (x, y, w, h) im Videobild
DEMO = [(314, 681, 49, 55), (1184, 596, 41, 64), (369, 681, 82, 55), (130, 681, 39, 55), (1378, 596, 40, 64)]   # v03_04: neue Tastenlage
DEMO_T0, DEMO_DT = srt(SRT)[2][0] + 0.6, 1.25            # ab Beginn von Blase 3
def ring(x, y, w, h, o=7, sw=6, g=14):
    bw, bh = w + 2 * (o + g), h + 2 * (o + g)
    glow = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([g, g, bw - g - 1, bh - g - 1], radius=12, outline=(225, 0, 123, 200), width=sw + 6)
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(glow).rounded_rectangle([g, g, bw - g - 1, bh - g - 1], radius=12, outline=(225, 0, 123, 255), width=sw)
    return glow, (x - o - g, y - o - g)
RINGS = [ring(*b) for b in DEMO]
# Weitere Beispiele zu „Tipp: … länger gedrückt“ (Blase 5): Umrandung, dann gehaltene Taste (grün) mit
# Hilfetext wie in paletteHelp.js (#333, 14px/1.3 sans-serif, max 18em; im Video Faktor 1,5)
TIPS = []   # v03_04: echte Hilfetexte in der Aufnahme
TIPS_T0, TIPS_DT, TIPS_RING = 36.7, 1.55, 0.45
TFL = [(ImageFont.truetype(f, 21), TTFont(f)["cmap"].getBestCmap()) for f in
       ["/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]]
class _TF:                                  # Roboto, fehlende Zeichen (→ …) aus DejaVu wie Androids Fallback
    def getlength(self, s): return width(s, TFL)
TF = _TF()
def tip_img(text):
    words, lines = text.split(), [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if TF.getlength(t) <= 378 or not lines[-1]: lines[-1] = t
        else: lines.append(w)
    bw = int(max(TF.getlength(l) for l in lines)) + 25; bh = int(len(lines) * 27.3) + 13; m = 10
    img = Image.new("RGBA", (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([m, m + 3, m + bw, m + bh + 3], radius=9, fill=(0, 0, 0, 80))
    img = img.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([m, m, m + bw, m + bh], radius=9, fill=(51, 51, 51, 255))
    for i, l in enumerate(lines):
        x = m + 12.5
        for t, f, _ in runs(l, TFL): d.text((x, m + 6.5 + 27.3 * i + 13.65), t, font=f, fill=(255, 255, 255, 255), anchor="lm"); x += f.getlength(t)
    return img, m
TIPIMGS = []
for (x, y, w, h), text in TIPS:
    img, m = tip_img(text); bw = img.width - 2 * m
    tx = max(4, min(int(x + w / 2 - bw / 2), W - bw - 4)); ty = y - (img.height - 2 * m) - 9
    TIPIMGS.append((ring(x, y, w, h), (img, (tx - m, ty - m)), (x, y, w, h)))
TINT = np.array([220 / 233, 237 / 231, 199 / 227])
def tips(frame, t):
    for k, (rg, (img, xy), (x, y, w, h)) in enumerate(TIPIMGS):
        a = TIPS_T0 + k * TIPS_DT; b = a + TIPS_RING; c = a + TIPS_DT - 0.15
        if a <= t < b: blend(frame, rg[0], *rg[1], min(1, (t - a) / 0.12, (b - t) / 0.12 + 0.3))
        elif b <= t < c:
            al = min(1, (t - b) / 0.12, (c - t) / 0.12)
            reg = frame[y + 2:y + h - 2, x + 2:x + w - 2].astype(np.float32)
            frame[y + 2:y + h - 2, x + 2:x + w - 2] = np.clip(reg * (1 - al + al * TINT), 0, 255).astype(np.uint8)
            blend(frame, img, *xy, al)

# Owal um die Zielformel in der Aufgabe (Blase 2, „Die Aufgabe: …“): wird gezeichnet, bleibt kurz, verblasst
OVAL_BOX = LAY["formula"]; OVAL_T0 = srt(SRT)[1][0] + 0.2; OVAL_DRAW, OVAL_FADE = 0.6, 0.3
OVAL_HOLD = min(2.5, LAY["scrolled_at"] - 0.05 - OVAL_T0 - OVAL_DRAW - OVAL_FADE)   # weg, bevor die Seite scrollt
_oval_cache = {}
def oval_img(p):
    k = round(p, 2)
    if k not in _oval_cache:
        x0, y0, x1, y1 = OVAL_BOX; mx, my, g = 70, 38, 16
        bw, bh = x1 - x0 + 2 * (mx + g), y1 - y0 + 2 * (my + g)
        img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); box = [g, g, bw - g - 1, bh - g - 1]
        ImageDraw.Draw(img).arc(box, 200, 200 + 360 * k, fill=(225, 0, 123, 200), width=12)
        img = img.filter(ImageFilter.GaussianBlur(6))
        ImageDraw.Draw(img).arc(box, 200, 200 + 360 * k, fill=(225, 0, 123, 255), width=6)
        _oval_cache[k] = (img, (x0 - mx - g, y0 - my - g))
    return _oval_cache[k]
def oval(frame, t):
    u = t - OVAL_T0
    if 0 <= u < OVAL_DRAW + OVAL_HOLD + OVAL_FADE:
        p = min(1.0, u / OVAL_DRAW); p = 1 - (1 - p) ** 2
        img, (x, y) = oval_img(p); blend(frame, img, x, y, min(1, (OVAL_DRAW + OVAL_HOLD + OVAL_FADE - u) / OVAL_FADE))

def demo(frame, t):
    oval(frame, t)
    tips(frame, t)
    for k, (img, (x, y)) in enumerate(RINGS):
        a, c = DEMO_T0 + k * DEMO_DT, DEMO_T0 + (k + 1) * DEMO_DT
        if a <= t < c: blend(frame, img, x, y, min(1, (t - a) / 0.12, (c - t) / 0.12))

def place(img, n, t):
    x = W // 2 - img.width // 2
    if intro(t): return x, INTRO_Y - img.height // 2
    gap = 40 if n == 1 else 8          # zweizeilige Blasen tiefer, damit sie die Zielformel nicht berühren
    return x, field_top(t) - gap - (img.height - 18)

def blend(frame, img, x, y, al):
    arr = np.asarray(img, dtype=np.float32)
    y0, x0 = max(y, 0), max(x, 0)
    sub = arr[y0 - y: min(H - y, arr.shape[0]), x0 - x: min(W - x, arr.shape[1])]
    reg = frame[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]].astype(np.float32)
    A = sub[..., 3:4] / 255 * al
    frame[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = (reg * (1 - A) + sub[..., :3] * A).astype(np.uint8)

def composite(frame, t):
    demo(frame, t)
    for img, (x, y), t0 in OVERLAYS:
        if t >= t0: blend(frame, img, x, y, min(1, (t - t0) / 0.5))
    for a, c, img, n in CUES:
        if a <= t < c:
            x, y = place(img, n, t); blend(frame, img, x, y, min(1, (t - a) / FADE, (c - t) / FADE))
    return frame

def decode(ss=0, n=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(SS + ss), "-i", SRC, "-vf", f"{VF},fps={FPS}", "-pix_fmt", "rgb24", "-f", "rawvideo"]
    if n: cmd += ["-frames:v", str(n)]
    return subprocess.Popen(cmd + ["-"], stdout=subprocess.PIPE)

if sys.argv[1] == "blasen":                # nur Blasen (+Legende) auf grauem Grund, 10 fps, schnell
    out = sys.argv[2]; n = int(9694 / FPS * 10)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "10", "-i", "-",
                            "-i", sys.argv[4], "-map", "0:v", "-map", "1:a", "-vf", "scale=960:600", "-c:v", "libx264", "-crf", "23",
                            "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    bgf = np.full((H, W, 3), 70, np.uint8)
    for i in range(n): enc.stdin.write(composite(bgf.copy(), i / 10).tobytes())
    enc.stdin.close(); enc.wait(); print("frames", n)
elif sys.argv[1] == "preview":
    for t in map(float, sys.argv[2:]):
        p = decode(t, 1); f = np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).copy()
        Image.fromarray(composite(f, t)).resize((960, 600)).save(f"{D}/p3b_{int(t)}.png")
else:
    out = sys.argv[2]; p = decode()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    i = 0
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        enc.stdin.write(composite(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(), i / FPS).tobytes()); i += 1
    enc.stdin.close(); enc.wait(); print("frames", i)
