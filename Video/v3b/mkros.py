# Rosette (ROSETTE_N Kopien um den Drehpunkt) aus der Intro-Figur als RGBA-PNG (Endkarte, Favicon).
# Zyklisches Geflecht: jede Kopie liegt über der vorigen, die letzte aber UNTER der ersten (sonst liegt sie oben auf).
import sys, os, numpy as np, cv2
sys.path.insert(0, os.environ["Q"]); import penrose as P
NR = int(os.environ.get("ROSETTE_N", "6"))   # Zahl der Arme
S = 2400; R60 = lambda k: (lambda a: np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]))(np.radians(360 / NR * k))
C = np.asarray(P.PIVOT, float)
pts = [((p - C) @ R60(k).T) for k in range(NR) for _, p in P.POLYS]; ext = max(np.abs(np.concatenate(pts)).max(0)) * 2
u = (S - 40) / ext
layers = []                                                       # je Kopie: Bild + Maske
for k in range(NR):
    li = np.zeros((S, S, 3), np.float32); lm = np.zeros((S, S), np.float32)
    for g, p in P.POLYS:
        q = [np.round((((p - C) @ R60(k).T) * u + S / 2) * 16).astype(np.int32)]
        cv2.fillPoly(li, q, P.bgr(g), cv2.LINE_AA, shift=4); cv2.fillPoly(lm, q, 1.0, cv2.LINE_AA, shift=4)
        cv2.polylines(li, q, True, (25, 25, 25), 3, cv2.LINE_AA, shift=4)
    layers.append((li, lm))
img = np.zeros((S, S, 3), np.float32); a = np.zeros((S, S), np.float32)
for li, lm in layers:                                             # Malerreihenfolge 0, 1, …, N-1
    img = img * (1 - lm[..., None]) + li * lm[..., None]; a = np.maximum(a, lm)
# Schluss des Geflechts: wo Kopie 0 und Kopie N-1 sich überlappen, liegt Kopie 0 oben – außer unter Kopien 1 … N-2
if os.environ.get("WEAVE", "1") == "1" and NR > 2:
    others = np.maximum.reduce([lm for _, lm in layers[1:NR - 1]])
    r = (layers[0][1] * layers[NR - 1][1] * (1 - others))[..., None]
    img = img * (1 - r) + layers[0][0] * r
print("Grauwerte", sorted({g if not isinstance(g, tuple) else g[0] for g, _ in P.POLYS}))
cv2.imwrite(sys.argv[1], np.dstack([img, a * 255]).clip(0, 255).astype(np.uint8))
