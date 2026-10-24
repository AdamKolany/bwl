# Trójkąt Penrose'a wektorowo: trzy belki wzdłuż x, y, z w rzucie izometrycznym ((1,1,1) → 0)
import numpy as np, cv2
L, Wd = 4.5, 1.0
C30, S30 = np.cos(np.pi/6), 0.5
def proj(p): x, y, z = p; return np.array([(x - y) * C30, (x + y) * S30 - z])
GRAY = {"z": 229, "x": 151, "y": 94}
def box_faces(lo, hi):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    return [("z", [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]),
            ("x", [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)]),
            ("y", [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)])]
BX = ((0,0,0),(L,Wd,Wd)); BY = ((L-Wd,0,0),(L,L,Wd)); BZ = ((L-Wd,L-Wd,0),(L,L,L))
BXs = ((0,0,0),(Wd,Wd,Wd))              # Anfang von X, nochmal obenauf → unmögliche Verbindung
POLYS = []
for b in (BX, BY, BZ, BXs):
    for k, q in box_faces(*b):
        if b is BXs and k == "x": continue      # Schnittfläche nicht zeichnen
        POLYS.append((GRAY[k], np.array([proj(p) for p in q])))
PIVOT = None                            # Drehpunkt der Rosette; None → best.npy
import os
_SVG = os.environ.get("PENROSE_SVG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "Penrose-Dreieck.svg")   # PENROSE_SVG=…: andere Figur probieren
if os.path.exists(_SVG) and not os.environ.get("PENROSE_INTERN"):   # Figur aus der SVG-Datei (zum Nachbearbeiten)
    import penrose_svg; POLYS, PIVOT = penrose_svg.load(_SVG)
allp = np.concatenate([p for _, p in POLYS]); CEN = (allp.max(0) + allp.min(0)) / 2; EXT = (allp.max(0) - allp.min(0)).max()
def bgr(g): return tuple(g) if isinstance(g, tuple) else (g,) * 3     # Grauwert oder (B, G, R)
def draw(img, cx, cy, size, ang, alpha_img=None, shade=1.0):
    """zeichnet in img (float BGR) bei Mittelpunkt (cx,cy), Größe = Ausdehnung in px, Drehung ang (Grad)"""
    a = np.radians(ang); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    for g, p in POLYS:
        q = ((p - CEN) / EXT * size) @ R.T + (cx, cy)
        cv2.fillPoly(img, [np.round(q * 16).astype(np.int32)], tuple(c * shade for c in bgr(g)), cv2.LINE_AA, shift=4)
        if alpha_img is not None: cv2.fillPoly(alpha_img, [np.round(q * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
if __name__ == "__main__":
    im = np.zeros((600, 600, 3), np.float32); draw(im, 300, 300, 500, 0); cv2.imwrite("pen_test.png", im)
