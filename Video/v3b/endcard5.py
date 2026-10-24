# Endkarte: Rosette entsteht wie im Intro – ein Dreieck wächst aus einem Punkt, wirbelt und spaltet sich in ROSETTE_N
# Kopien (Anker wandert vom Schwerpunkt zum Drehpunkt), dabei verlischt der Seitenhintergrund; dann wächst aus der Mitte das
# Entenbild – erst als winzige Ellipse, die sich beim Wachsen in ein bildschirmfüllendes Rechteck verwandelt (Superellipse,
# Exponent 2 → 22). Weiche Überblendung: innen wiegt die Ente immer mehr, Rosette und Hintergrund werden schwächer.
# Am Ende Stehen und Ausblenden nach Schwarz.
import sys, os, numpy as np, cv2
sys.path.insert(0, os.environ["Q"]); import penrose as P          # Figur: PENROSE_SVG (Escher A)
W, H, FPS = 1920, 1200, 30
NR = int(os.environ.get("ROSETTE_N", "8"))
G1 = 210; G2 = G1 + 10; B1 = G2 + 135; S1 = B1 + 60; F1 = S1 + 45; N = F1 + 15
#  Rosette entsteht 7 s | Pause | Ente wächst und wird zum Rechteck 4,5 s | Stehen 2 s | Ausblenden 1,5 s | schwarz 0,5 s
bg = cv2.imread(sys.argv[1]).astype(np.float32)                   # letzte Inhaltsklatke
# Ente: fast bildschirmfüllend, 20 % breiter gestreckt, weißer Grund (wie v03_09ff.)
ende = cv2.imread("Ende.png", cv2.IMREAD_UNCHANGED)
ys, xs = np.nonzero(ende[..., 3] > 10); ende = ende[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
eh = int(H * 0.95); ew = min(W, int(eh * ende.shape[1] / ende.shape[0] * 1.2)); ex, ey = (W - ew) // 2, (H - eh) // 2
e = cv2.resize(ende, (ew, eh), interpolation=cv2.INTER_AREA).astype(np.float32); a = e[..., 3:] / 255
card = np.full((H, W, 3), 255, np.float32); card[ey:ey+eh, ex:ex+ew] = e[..., :3] * a + 255 * (1 - a)
# Rosette: NR Kopien um den Drehpunkt, normiert auf Außenradius 1
C = np.asarray(P.PIVOT, float)
def rot(d): r = np.radians(d); return np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]])
ROS = [(g, (p - C) @ rot(360 / NR * k).T) for k in range(NR) for g, p in P.POLYS]
RMAX = max(np.linalg.norm(q, axis=1).max() for _, q in ROS); ROS = [(g, q / RMAX) for g, q in ROS]
TRI = [(g, (p - C) / RMAX) for g, p in P.POLYS]                   # ein Dreieck, relativ zum Drehpunkt
_m = np.zeros((1000, 1000), np.uint8)
for _, q in TRI: cv2.fillPoly(_m, [np.round(q * 400 + 500).astype(np.int32)], 255)
_y, _x = np.nonzero(_m); GC = np.array([_x.mean() - 500, _y.mean() - 500]) / 400   # Schwerpunkt, relativ zum Drehpunkt
R0 = 560                                                          # Außenradius der fertigen Rosette in px
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
ease_io = lambda t: 3 * t * t - 2 * t ** 3
cl = lambda v: min(1.0, max(0.0, v))
def build(img, t):
    # wie intro.py: Wachsen aus dem Punkt, 3 Umdrehungen bis 4,2 s, ab 4,0 s Aufspalten, Anker → Drehpunkt bis 6,4 s
    u = R0 * (1 - (1 - cl(t / 1.6)) ** 3)
    th = -1080 * (1 - (1 - cl(t / 4.2)) ** 2)
    phi = [0.0]
    for k in range(1, NR): phi.append(phi[-1] + 360 / NR * ease_io(cl((t - 4.0 - 2.1 / (NR - 1) * (k - 1)) / 0.8)))
    anc = GC * (1 - ease_io(cl((t - 4.0) / 2.4)))                # 0 = Drehpunkt in der Bildmitte
    draw_woven(img, [[(g, ((q @ rot(phi[k]).T) - anc) * u @ rot(th).T + (W / 2, H / 2)) for g, q in TRI] for k in range(NR)])
def rosette(img, rad, ang):
    draw_woven(img, [[(g, q * rad @ rot(ang).T + (W / 2, H / 2)) for g, q in ROS[k * len(TRI):(k + 1) * len(TRI)]] for k in range(NR)])
# Koordinaten relativ zur Mitte, in Halbbreite/Halbhöhe des Bildschirms (Ellipse/Rechteck im Bildschirmformat)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
UX = np.abs(xx - W / 2) / (W / 2) + 1e-6; UY = np.abs(yy - H / 2) / (H / 2) + 1e-6
ease_out = lambda t: 1 - (1 - t) ** 3
ease_io = lambda t: 3 * t * t - 2 * t ** 3
ease_in = lambda t: t ** 1.8
def scaled(img, s):
    M = np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
out = sys.stdout.buffer
for f in range(N):
    img = bg * (1 - ease_io(min(1.0, f / G1)))                  # Seitenhintergrund verlischt, während die Rosette entsteht
    if f < G1:                                                    # Rosette entsteht wie im Intro
        build(img, (f + 1) / FPS)
    else:
        rosette(img, R0, 0)
    if f >= G2:                                                   # Ente wächst: Ellipse → Rechteck, weich überblendet
        t = min(1.0, (f - G2 + 1) / (B1 - G2)); u = ease_io(t)
        sc = 0.015 + (1.12 - 0.015) * u                             # Größe (am Ende etwas über den Rand, damit die Ecken voll sind)
        pw = 2 + 20 * u ** 2                                        # Superellipsen-Exponent: 2 = Ellipse, groß = Rechteck
        r = (UX ** pw + UY ** pw) ** (1 / pw) / sc                  # < 1: innerhalb der Form
        feather = 0.55 * (1 - u) + 0.01                             # breite, weiche Kante am Anfang, scharf am Ende
        g = 0.35 + 0.65 * u                                         # Gesamtgewicht der Ente
        k = (g * np.clip((1 - r) / feather, 0, 1))[..., None]
        k = np.where(u >= 0.999, (r < 1)[..., None].astype(np.float32), k)
        img = img * (1 - k) + scaled(card, min(1.0, sc)) * k
    if f >= S1:                                                   # Ausblenden nach Schwarz
        img = img * (1 - min(1.0, (f - S1) / (F1 - S1)))
    out.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
