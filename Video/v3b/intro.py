# Figur: Penrose-Dreieck.svg (über penrose.py); Vorschau/Film: intro_vorschau.sh
# Intro: Penrose-Dreieck wächst aus einem Punkt, wirbelt, spaltet sich (1→2→…→6) zur Rosette,
# Rosette wächst, man fliegt in den Sechseck-Durchbruch, darin schwillt der Titel an.
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import penrose as P
W, H, FPS = 1920, 1200, 30
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 13.5
L, cx, cy, flip, A0 = np.load("best.npy"); CEN = np.array([cx, cy])   # Drehpunkt der Rosette (gefittet an ros6_hi)
if P.PIVOT is not None: CEN = np.asarray(P.PIVOT, float)          # aus Penrose-Dreieck.svg (id="drehpunkt")
POLYS = P.POLYS
import os; NR = int(os.environ.get("ROSETTE_N", "6"))     # Zahl der Arme der Rosette (6, 7, 8 …)
m = np.zeros((800, 800), np.float32); P.draw(np.zeros((800, 800, 3), np.float32), 400, 400, 600, 0, m)
ys, xs = np.nonzero(m > 0.5); G = np.array([xs.mean() - 400, ys.mean() - 400]) / 600 * P.EXT + P.CEN   # Schwerpunkt
U1 = 470 / P.EXT                                   # px pro Einheit: Dreieck ≈ 470 px
cl = lambda x: min(1.0, max(0.0, x))
eo = lambda x: 1 - (1 - cl(x)) ** 3
eio = lambda x: (lambda u: 3 * u * u - 2 * u ** 3)(cl(x))
def rot(a): a = np.radians(a); return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
# --- Titel
FB, FS = "/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf", "/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf"
FB, FS = "Platypi-700.ttf", "Platypi-600.ttf"      # Schrift und Farben wie auf der Startseite (bwl.css)
LINES = [("Mathematisieren und Abstrahieren", FB, 96, (0, 0, 255)), None,
         ("Kurzes Schulungsvideo zur Benutzung", FS, 62, (0, 51, 170)),
         ("der Formeleingabe-Tastatur", FS, 62, (0, 51, 170))]
TI = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(TI)
hs = [40 if l is None else int(l[2] * 1.35) for l in LINES]; y = (H - sum(hs)) // 2
for l, h in zip(LINES, hs):
    if l:
        f = ImageFont.truetype(l[1], l[2]); w = d.textlength(l[0], font=f); d.text(((W - w) / 2, y), l[0], font=f, fill=l[3] + (255,))
    y += h
TI = np.asarray(TI, np.float32)
# helle Aura hinter dem Text, damit er auf dem Foto lesbar bleibt
_g = cv2.GaussianBlur(cv2.dilate(TI[..., 3], np.ones((9, 9), np.uint8)), (0, 0), 14); _g = np.clip(_g / max(_g.max(), 1) * 1.6, 0, 1) * 0.55   # dezente helle Aura – Blau auf Grau sonst kontrastarm
_tc = TI[..., :3] * (TI[..., 3:] / 255) + 255 * (1 - TI[..., 3:] / 255)
TI = np.dstack([_tc, np.maximum(TI[..., 3] / 255, _g) * 255]).astype(np.float32)
# Hintergrund: Startseitenbild (Schulgebäude mit Laternen), auf 16:10 beschnitten
_b = cv2.imread("HoMe.png", cv2.IMREAD_UNCHANGED).astype(np.float32)
_b = (_b[..., :3] * _b[..., 3:] / 255 + 128 * (1 - _b[..., 3:] / 255)).astype(np.uint8)   # wie im Browser: Alpha über Grau 128
_s = H / _b.shape[0]; _b = cv2.resize(_b, (int(_b.shape[1] * _s), H), interpolation=cv2.INTER_CUBIC)
_x = (_b.shape[1] - W) // 2; BG = _b[:, _x:_x + W].astype(np.float32)
VS = 1100 / (2.6 * P.EXT)                          # virtuelle Leinwand für die Innen-Maske der Figur
def inside_mask(phi, anc, u, Rt):
    """Bereich innerhalb der Figur, der nicht von Balken bedeckt ist (Löcher), in Bildschirmkoordinaten"""
    S = 1400; m = np.zeros((S, S), np.uint8)
    for k in range(NR):
        Rk = rot(phi[k])
        for g, p in POLYS:
            q = ((p - CEN) @ Rk.T + CEN - anc) * VS + S / 2
            cv2.fillPoly(m, [np.round(q * 16).astype(np.int32)], 255, cv2.LINE_8, shift=4)
    ff = cv2.dilate(m, np.ones((7, 7), np.uint8)); cv2.floodFill(ff, None, (0, 0), 128)   # dicht machen: feine Spalten nicht nach außen „lecken“ lassen
    inner = cv2.erode((ff != 128).astype(np.uint8), np.ones((9, 9), np.uint8))        # Umriss der Figur (Dichtung zurücknehmen)
    hole = cv2.dilate((inner & (m == 0)).astype(np.uint8), np.ones((5, 5), np.uint8)) & inner
    hole = hole * 255
    A = np.zeros((2, 3), np.float32); A[:, :2] = Rt * (u / VS); A[:, 2] = (W / 2, H / 2) - (Rt * (u / VS)) @ (S / 2, S / 2)
    return cv2.warpAffine(hole, A, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)[..., None] / 255
def draw_woven(img, copies, lw=2):
    """copies: je Kopie eine Liste (grau, Punkte in px). Malt 0…N-1 übereinander, dann Kopie 0 wieder über Kopie N-1
    (nur wo keine der Kopien 1…N-2 darüber liegt) – geschlossenes Geflecht statt „letzte liegt oben“."""
    for polys in copies:
        for g, q in polys:
            pq = [np.round(q * 16).astype(np.int32)]
            cv2.fillPoly(img, pq, P.bgr(g), cv2.LINE_AA, shift=4)
            cv2.polylines(img, pq, True, (25, 25, 25), lw, cv2.LINE_AA, shift=4)
    if len(copies) < 3: return img
    def mask(groups):
        m = np.zeros(img.shape[:2], np.float32)
        for polys in groups:
            for _, q in polys: cv2.fillPoly(m, [np.round(q * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
        return m
    k3 = np.ones((5, 5), np.uint8)                   # Kontur der unteren Kopie reicht ~1 px über ihre Fläche
    r = mask([copies[0]]) * cv2.dilate(mask([copies[-1]]), k3) * (1 - mask(copies[1:-1]))
    if r.max() <= 0: return img
    top = img.copy()
    for g, q in copies[0]:
        pq = [np.round(q * 16).astype(np.int32)]
        cv2.fillPoly(top, pq, P.bgr(g), cv2.LINE_AA, shift=4)
        cv2.polylines(top, pq, True, (25, 25, 25), lw, cv2.LINE_AA, shift=4)
    r = r[..., None]
    img[:] = img * (1 - r) + top * r
    return img
def frame(t):
    # Größe: Wachsen aus dem Punkt, später exponentieller Zoom in die Rosette
    u = U1 * eo(t / 1.6) * np.exp(np.log(32) * eio((t - 6.6) / 3.8))
    # Drehung: 3 Umdrehungen bis 4 s (auslaufend), danach langsam weiter
    th = -1080 * (1 - (1 - cl(t / 4.2)) ** 2) - 12 * max(0, t - 4.2)
    # Aufspalten: Kopie k löst sich von Kopie k-1 um 60°
    phi = [0.0]
    for k in range(1, NR): phi.append(phi[-1] + 360 / NR * eio((t - 4.0 - 2.1 / (NR - 1) * (k - 1)) / 0.8))
    anc = G + (CEN - G) * eio((t - 4.0) / 2.4)       # Ankerpunkt wandert vom Schwerpunkt zum Rosettenmittelpunkt
    Rt = rot(th + A0)
    # Schulgebäude nur in den Löchern der Figur sichtbar, sonst schwarz; langsamer Zoom
    z = 1 + 0.06 * t / DUR; M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]])
    img = cv2.warpAffine(BG, M, (W, H), flags=cv2.INTER_LINEAR) * inside_mask(phi, anc, u, Rt) if u > 0 else np.zeros((H, W, 3), np.float32)
    copies = [[(g, ((p - CEN) @ rot(phi[k]).T + CEN - anc) * u @ Rt.T + (W / 2, H / 2)) for g, p in POLYS] for k in range(NR)]
    draw_woven(img, copies)                          # Kontur gegen das Hintergrundbild; letzte Kopie unter der ersten
    # Titel schwillt an
    s = eo((t - 8.3) / 2.4)
    if s > 0:
        sz = max(2, int(W * (0.03 + 0.97 * s))), max(2, int(H * (0.03 + 0.97 * s)))
        ti = cv2.resize(TI, sz, interpolation=cv2.INTER_AREA); x0, y0 = (W - sz[0]) // 2, (H - sz[1]) // 2
        a = ti[..., 3:] / 255 * cl((t - 8.3) / 0.8)
        reg = img[y0:y0 + sz[1], x0:x0 + sz[0]]; img[y0:y0 + sz[1], x0:x0 + sz[0]] = reg * (1 - a) + ti[..., :3][..., ::-1] * a
    return np.clip(img, 0, 255).astype(np.uint8)
if __name__ == "__main__":
    if sys.argv[2:3] == ["preview"]:
        for t in map(float, sys.argv[3:]): cv2.imwrite(f"i_{t:05.2f}.png", cv2.resize(frame(t), (960, 600), interpolation=cv2.INTER_AREA))
    else:
        out = sys.stdout.buffer
        for i in range(int(DUR * FPS)): out.write(frame(i / FPS).tobytes())
