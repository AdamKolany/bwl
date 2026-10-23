# Plansza końcowa: Ende.png wyrasta ze środka w kształcie rozety, potem morfing (SDF) do pełnej planszy.
import sys, numpy as np, cv2
W, H, FPS, N = 1920, 1200, 30, 360
G1, HOLD, M0, M1 = 120, 150, 150, 270           # klatki: wzrost 4 s, pauza 1 s, morfing 4 s, potem 3 s stoi
bg = cv2.imread(sys.argv[1]).astype(np.float32)          # ostatnia klatka treści (BGR)
ende = cv2.imread("Ende.png", cv2.IMREAD_UNCHANGED)
ew, eh = 1510, 1200; ex = (W - ew) // 2
e = cv2.resize(ende, (ew, eh), interpolation=cv2.INTER_AREA).astype(np.float32)
card = np.zeros((H, W, 3), np.float32); fa = np.zeros((H, W), np.float32)
a = e[..., 3:] / 255; card[:, ex:ex+ew] = e[..., :3] * a; fa[:, ex:ex+ew] = a[..., 0]
final = card                                              # plansza na czarnym tle
# rozeta: wysoka rozdzielczość z PTR1 (ros6_hi.png), alfa = kształt z otworami, szarość = cieniowanie
ros = cv2.imread("ros6_hi.png", cv2.IMREAD_UNCHANGED).astype(np.float32)
R = 1000                                                  # szerokość rozety w pełnej skali
rh = int(R * ros.shape[0] / ros.shape[1])
ros = cv2.resize(ros, (R, rh), interpolation=cv2.INTER_AREA)
rm = (ros[..., 3] > 128).astype(np.float32)
rs = ros[..., :3].mean(2) / 229.0                         # 1 = jasna ściana, ~0.4 = ciemna
def place(m, s, ang):
    sw, sh = max(2, int(R * s)), max(2, int(rh * s))
    mm = cv2.resize(m, (sw, sh), interpolation=cv2.INTER_LINEAR)
    M = cv2.getRotationMatrix2D((sw / 2, sh / 2), ang, 1); M[0, 2] += W / 2 - sw / 2; M[1, 2] += H / 2 - sh / 2
    return cv2.warpAffine(mm, M, (W, H), flags=cv2.INTER_LINEAR)
def sdf(m):
    b = (m > 0.5).astype(np.uint8)
    return cv2.distanceTransform(1 - b, cv2.DIST_L2, 5) - cv2.distanceTransform(b, cv2.DIST_L2, 5)
ease_out = lambda t: 1 - (1 - t) ** 3
ease_io = lambda t: 3 * t * t - 2 * t ** 3
d_ros = sdf(place(rm, 1.0, 0)); d_fin = sdf((fa > 0.5).astype(np.float32))
def scaled_card(s):
    # cała plansza przeskalowana wokół środka ekranu
    M = np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]])
    return cv2.warpAffine(card, M, (W, H), flags=cv2.INTER_LINEAR)
out = sys.stdout.buffer
for f in range(N):
    if f < G1:                                            # wzrost + obrót
        t = ease_out((f + 1) / G1); s = 0.02 + 0.98 * t
        ang = -120 * (1 - t); m = place(rm, s, ang); sh = place(rs, s, ang); img = scaled_card(s); dark = 0.0; shade = 1.0
    elif f < M0:
        m = place(rm, 1.0, 0); sh = place(rs, 1.0, 0); img = card; dark = 0.0; shade = 1.0
    else:                                                 # morfing SDF
        t = ease_io(min(1.0, (f - M0) / (M1 - M0)))
        d = (1 - t) * d_ros + t * d_fin
        m = np.clip(0.5 - d, 0, 1); sh = place(rs, 1.0, 0); img = card; dark = t; shade = 1 - t
    if f >= M1: m = fa; shade = 0.0
    k = (0.45 + 0.55 * np.clip(sh, 0, 1.1))[..., None]     # mnożnik cieniowania
    img = img * (1 - shade + shade * k)
    # cienki ciemny kontur, żeby rozeta odcinała się od jasnego tła (znika z morfingiem)
    edge = np.clip(cv2.dilate(m, np.ones((5, 5), np.uint8)) - m, 0, 1)[..., None] * (1 - dark) * 0.6
    back = bg * (1 - dark)
    back = back * (1 - edge) + 40 * edge
    frame = back * (1 - m[..., None]) + img * m[..., None]
    out.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
