# Liest das Penrose-Dreieck aus Penrose-Dreieck.svg: Flächen (polygon/path/rect…) mit Füllfarbe (Grau oder Farbe, inkl. Deckkraft),
# in Dokumentreihenfolge, sowie den Drehpunkt der Rosette (Element mit id="drehpunkt").
# Verträgt die von Inkscape erzeugten Pfade (absolute/relative Befehle, transform an Gruppen).
import os, re, numpy as np, xml.etree.ElementTree as ET
NAMED = {"black": (0, 0, 0), "white": (255, 255, 255), "gray": (128, 128, 128), "grey": (128, 128, 128),
         "silver": (192, 192, 192), "red": (255, 0, 0)}
def _color(s):
    s = (s or "").strip().lower()
    if s.startswith("#"):
        h = s[1:]; h = "".join(c * 2 for c in h) if len(h) == 3 else h[:6]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"rgb\(([^)]*)\)", s)
    if m: return tuple(int(float(v.strip().rstrip("%"))) for v in m.group(1).split(","))
    return NAMED.get(s)
def _style(el, name):
    m = re.search(r"(?<![\w-])" + name + r"\s*:\s*([^;]+)", el.get("style", ""))
    return m.group(1) if m else el.get(name)
def _tf(s):
    M = np.eye(3)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        a = [float(v) for v in re.split(r"[\s,]+", args.strip()) if v]
        T = np.eye(3)
        if name == "matrix": T[:2, :] = np.array(a).reshape(3, 2).T
        elif name == "translate": T[0, 2], T[1, 2] = a[0], (a[1] if len(a) > 1 else 0)
        elif name == "scale": T[0, 0], T[1, 1] = a[0], (a[1] if len(a) > 1 else a[0])
        elif name == "rotate":
            r = np.radians(a[0]); c, s_ = np.cos(r), np.sin(r); R = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])
            if len(a) == 3: R = np.array([[1, 0, a[1]], [0, 1, a[2]], [0, 0, 1]]) @ R @ np.array([[1, 0, -a[1]], [0, 1, -a[2]], [0, 0, 1]])
            T = R
        M = M @ T
    return M
def _path(d):
    """Eckpunkte eines Pfads (Kurven werden durch ihre Endpunkte ersetzt – die Figur besteht aus Geraden)."""
    toks = re.findall(r"[MmLlHhVvZzCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", d)
    polys, cur, pos, start, i, cmd = [], [], np.zeros(2), np.zeros(2), 0, None
    n = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]): cmd = toks[i]; i += 1
        U, rel = cmd.upper(), cmd.islower()
        if U == "Z":
            if cur: polys.append(cur); cur = []
            pos = start.copy(); continue
        a = [float(v) for v in toks[i:i + n[U]]]; i += n[U]
        if U == "H": p = np.array([a[0] + (pos[0] if rel else 0), pos[1]])
        elif U == "V": p = np.array([pos[0], a[0] + (pos[1] if rel else 0)])
        else: p = np.array(a[-2:]) + (pos if rel else 0)
        if U == "M":
            if cur: polys.append(cur)
            cur = [p]; start = p.copy(); cmd = "l" if rel else "L"
        else: cur.append(p)
        pos = p
    if cur: polys.append(cur)
    return [np.array(q) for q in polys if len(q) >= 3]
def load(fn):
    root = ET.parse(fn).getroot(); polys, piv = [], None
    def walk(el, M):
        nonlocal piv
        M = M @ _tf(el.get("transform")); tag = el.tag.split("}")[-1]
        app = lambda pts: (M @ np.c_[pts, np.ones(len(pts))].T).T[:, :2]
        if el.get("id") == "drehpunkt":
            if tag in ("circle", "ellipse"): piv = app(np.array([[float(el.get("cx", 0)), float(el.get("cy", 0))]]))[0]
            elif tag == "path": piv = np.concatenate([app(q) for q in _path(el.get("d", ""))]).mean(0)
            return
        if tag in ("defs", "metadata", "namedview", "title", "desc"): return
        geo = []
        if tag in ("polygon", "polyline"):
            v = [float(x) for x in re.split(r"[\s,]+", el.get("points", "").strip()) if x]; geo = [np.array(v).reshape(-1, 2)]
        elif tag == "path": geo = _path(el.get("d", ""))
        elif tag == "rect":
            x, y, w, h = (float(el.get(k, 0)) for k in ("x", "y", "width", "height")); geo = [np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])]
        if geo:
            c = _color(_style(el, "fill"))
            if c is None: c = (128, 128, 128)
            if not os.environ.get("PENROSE_FARBE"):   # Standard: Grau = Mittelwert der Füllfarbe (Adam: grau ist schöner)
                for q in geo: polys.append((int(round(sum(c) / 3)), app(q)))
                for ch in el: walk(ch, M)
                return
            op = 1.0                           # PENROSE_FARBE=1: echte Farben, Deckkraft wie in Inkscape über Weiß gemischt
            for k in ("opacity", "fill-opacity"):
                v = _style(el, k)
                if v: op *= float(v)
            c = tuple(x * op + 255 * (1 - op) for x in c)
            g = int(round(c[0])) if c[0] == c[1] == c[2] else (c[2], c[1], c[0])   # Grau → Zahl, Farbe → BGR
            for q in geo: polys.append((g, app(q)))
        for ch in el: walk(ch, M)
    walk(root, np.eye(3))
    return polys, piv
