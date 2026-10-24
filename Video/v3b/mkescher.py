# Escher-Dreieck aus eszer.psf (/escher a b, gleichseitig) mit wählbarer Balkendicke b; Stile aus Adams escher.svg,
# Drehpunkt A wie bisher: gleiche baryzentrische Lage im äußeren Dreieck (Seite a + 2b).
import sys, re, numpy as np
src, a, b, out, outp = sys.argv[1], 3.0, float(sys.argv[2]), sys.argv[3], sys.argv[4]
h = np.sqrt(3) / 2
def segment():
    cx = a / 2; cy = (cx + b) / np.sqrt(3); p = [np.array([-cx, -cy])]
    for d in [((a - b) / 2, (a - b) * h), ((a - 3 * b) / 2, -(a - 3 * b) * h), (b, 0), (-(a - b) / 2, (a - b) * h), (-a / 2, -a * h)]:
        p.append(p[-1] + d)
    return np.array(p)
R = lambda d: (lambda r: np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]]))(np.radians(d))
segs = [segment() @ R(120 * k).T for k in range(3)]
side = a + 2 * b; top = side / np.sqrt(3); bot = -side / (2 * np.sqrt(3))       # äußeres Dreieck um den Ursprung
corners = {"ap": np.array([0, top]), "rt": np.array([side / 2, bot]), "lf": np.array([-side / 2, bot])}
# genaue Baryzentrik aus der alten Rechnung
A_, C_, B_ = np.array([50, -0.2]), np.array([613.3, 325]), np.array([50, 650.2]); piv = np.array([486.62, 141.67])
l = np.linalg.solve(np.c_[A_ - B_, C_ - B_], piv - B_); bary = (l[0], l[1], 1 - l.sum())
pv = bary[0] * corners["ap"] + bary[1] * corners["rt"] + bary[2] * corners["lf"]
allp = np.vstack(segs); lo, hi = allp.min(0), allp.max(0)
S, M = 100, 20
tx = lambda p: (M + (p[0] - lo[0]) * S, M + (hi[1] - p[1]) * S)
vw, vh = (hi - lo) * S + 2 * M
text = open(src, encoding="utf-8").read()
text = re.sub(r'width="[^"]*"\s+height="[^"]*"\s+viewBox="[^"]*"', f'width="{vw:.0f}"\n   height="{vh:.0f}"\n   viewBox="0 0 {vw:.2f} {vh:.2f}"', text, 1)
text = re.sub(r'mit a=3\.0, b=[0-9.]+\)', f'mit a=3.0, b={b:g})', text)
pts = iter([" ".join("%.2f,%.2f" % tx(q) for q in s) for s in segs])
text = re.sub(r'points="[^"]*"', lambda m: f'points="{next(pts)}"', text)
open(out, "w", encoding="utf-8").write(text)
x, y = tx(pv); open(outp, "w", encoding="utf-8").write(text.replace("</svg>", f'  <circle id="drehpunkt" cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#ff0000"/>\n</svg>'))
print("Drehpunkt", x, y)
