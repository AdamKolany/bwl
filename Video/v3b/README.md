# Version 3b (v03_06 – v03_14)

Werkzeuge der späteren Fassungen (Arbeitsverzeichnis `/tmp/mb4` auf *byczysko*, flüchtig; Kopien in
`Filme/_Quellen/`). Feste Pfade zeigen dorthin.

- **Aufnahme**: `record6.py` (Tablet, CDP), Synchronisation `sync.py`, Feldkante `field6.py`,
  Sprechblasen `bubbles6.py` + `bubble.py`, Blasen-/Sprechtext-Datei `mk0306.py`.
- **Intro**: `intro.py` (Dreieck wächst, wirbelt, spaltet sich zur Rosette, Flug ins Loch, Titel),
  Figur aus SVG über `penrose.py`/`penrose_svg.py` (`PENROSE_SVG=…`), Vorschau `intro_vorschau.sh`.
  Figur: Escher-Dreieck `escher-Drehpunkt-A, v 01_01.svg` (aus eszer.psf, `mkescher.py`, Balkendicke b = 0,55,
  roter Kreis = Drehpunkt). `ROSETTE_N` = Zahl der Arme (Film: 8; 6 erinnerte an den Davidstern, 5 an den Sowjetstern).
- **Rosette geflochten** (`draw_woven` in intro.py/endcard5.py, `mkros.py`): jede Kopie über der vorigen,
  die letzte unter der ersten.
- **Endkarte** `endcard5.py`: Rosette entsteht wie im Intro, Seitenhintergrund verlischt, Ente wächst als
  Ellipse → bildschirmfüllendes Rechteck (weich überblendet), Stehen, Ausblenden nach Schwarz.
- **Favicon** `fav.py` aus `mkros.py`-Rosette (8 Arme, helle Variante B → `JS/favicon-ros8.png`).
- **Bau**: `build0314.sh` (Intro + Inhalt + Endkarte + Ton + Untertitel).
