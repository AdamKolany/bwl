#!/bin/bash
# Vorschau des Intros mit der Figur aus Penrose-Dreieck.svg (im selben Ordner).
#   ./intro_vorschau.sh           → Intro-Vorschau.mp4  (ganzes Intro, 13,5 s; Rendern ca. 40 s)
#   ./intro_vorschau.sh bilder    → Intro-Vorschau.png  (Kontaktbogen mit 8 Zeitpunkten, schnell)
#   ./intro_vorschau.sh bilder 1 4.5 7   → Kontaktbogen mit eigenen Zeitpunkten (Sekunden)
#   PENROSE_SVG=/pfad/figur.svg OUT=Intro-Probe ./intro_vorschau.sh   → andere Figur, eigener Dateiname
#   PENROSE_FARBE=1 ./intro_vorschau.sh   → Füllfarben aus der SVG statt Grau
# Nur die Figur prüfen (ohne Animation): Penrose-Dreieck.svg im Browser/Inkscape öffnen.
set -e
cd "$(dirname "$0")"
if [ "$1" = bilder ]; then
  shift; T=${*:-0.8 2 4.2 5.2 6.2 7.5 9 11}
  D=$(mktemp -d); rm -f i_*.png; python3 intro.py 13.5 preview $T; mv i_*.png "$D"/
  python3 - "$D" <<'PY'
import sys, glob, cv2, numpy as np
fs = sorted(glob.glob(sys.argv[1] + "/i_*.png")); ims = [cv2.imread(f) for f in fs]
for im, f in zip(ims, fs): cv2.putText(im, f[-9:-4].lstrip("0") + " s", (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2, cv2.LINE_AA)
while len(ims) % 4: ims.append(np.zeros_like(ims[0]))
rows = [np.hstack(ims[i:i + 4]) for i in range(0, len(ims), 4)]
import os; cv2.imwrite(os.environ.get("OUT", "Intro-Vorschau") + ".png", np.vstack(rows))
PY
  rm -rf "$D"; echo "→ $(pwd)/${OUT:-Intro-Vorschau}.png"
else
  python3 intro.py 13.5 | ffmpeg -v error -y -f rawvideo -pix_fmt bgr24 -s 1920x1200 -r 30 -i - \
    -c:v libx264 -crf 18 -pix_fmt yuv420p "${OUT:-Intro-Vorschau}.tmp.mp4"
  mv -f "${OUT:-Intro-Vorschau}.tmp.mp4" "${OUT:-Intro-Vorschau}.mp4"; echo "→ $(pwd)/${OUT:-Intro-Vorschau}.mp4"
fi
