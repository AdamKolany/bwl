# Erklärungsvideo „Tastatur-Schulung“

Werkzeuge, mit denen das Video *Formeln eingeben mit der Bildschirmtastatur* entsteht.
Die Skripte stammen aus Arbeitssitzungen und enthalten teils feste Pfade
(Scratchpad unter `/tmp/claude-1000/…`); vor erneuter Benutzung anpassen.

Große Mediendateien sind **nicht** im Repo, sondern liegen auf *byczysko* in
`MuA/mathe-C10/Filme/_Quellen/`: Rohaufnahme `v2dtake.mp4`, Sprechtext-Audio
`vo/voice.wav` und `vo/NN.wav`, `field.npy`.
Fertige Videos: `MuA/mathe-C10/Filme/Tastatur-Schulung, v MM_mm.mp4`.

## Ablauf

1. **Aufnahme** (`tablet/`): Lenovo-Tablet (adb `HA27SS17`) per USB, Chrome mit
   Remote-Debugging (CDP, Port 9222). `drv.py` findet Tasten per CDP und tippt
   per adb echte Touches; `edit_steps.py` = Ablauf der Eingabe; `record2.py`
   nimmt mit scrcpy auf. Eine 1-s-Schwarzmarke dient zur Synchronisation
   (`blackdetect`).
2. **Bildausschnitt** 16:10: `crop=1920:1054:0:58,pad=1920:1200`, Start bei `-ss 12.85`.
3. **Sprechtext** (`voice/`): `lines.txt` = ein Satz pro Untertitel. `synth.py`
   (XTTS-v2 über das Projekt *Szeptucha*, eigene Stimmprobe) erzeugt `NN.wav`;
   `regen.py` erzeugt Kandidaten für misslungene Sätze (Prüfung mit Whisper);
   `mix.py` legt die Sätze auf die Untertitelzeiten (+0,25 s, ggf. atempo ≤ 1,3).
4. **Untertitel als Sprechblasen** (`post/`): `field.py` misst die Oberkante des
   Antwortfelds über die Zeit (`field.npy`), `bubbles.py` zeichnet die Untertitel
   als abgerundete Blasen knapp darüber (folgt dem Scrollen; am Anfang auf der
   Menüzeile, einzeilig). `legend.py` baut die Sondertasten-Legende aus echten
   Tastenbildern.
5. **Abspann**: `xfade` auf `Ende.png`, dann Ton (`voice.wav`) dazumischen.

`start-page/` enthält Kopien von `cgi-bin/teste/doit.cgi` (main/tests), die
selbst nicht unter Versionskontrolle stehen.

## Version 3 (`v3/`, ab v03_02)

Neue Tabletaufnahme (Testserver :8080, 100 % Zoom), Arbeitsverzeichnis `/tmp/mb3`
auf *byczysko* (flüchtig; Kopien in `Filme/_Quellen/`). Feste Pfade in den Skripten
zeigen dorthin.

- **Aufnahme**: `record3.py` (CDP über `adb forward`, Tablet an *mientus*);
  `field3.py` misst die Antwortfeld-Oberkante (`field.npy`).
- **Sprechblasen**: `bubbles3b.py render out.mp4 Blasen.txt` – Blasen mit den
  Zeilenumbrüchen aus `Blasen.txt` (ein `### NN`-Block pro Untertitel; warnt bei zu
  breiten Zeilen und abweichendem Text). Legende unten etwas höher.
  `blasen_vorschau.sh` = schnelle Vorschau nur der Blasen mit Ton (10 fps).
- **Intro** (`intro.py`, 13,5 s): vektorielles Penrose-Dreieck (`penrose.py`,
  isometrische Projektion dreier Balken) wächst aus einem Punkt, wirbelt, spaltet
  sich 1→6 zur Rosette; Flug in das Sechseck-Loch. Das Startseitenbild `HoMe.png`
  (Alpha über Grau 128 wie im Browser) ist nur in den Löchern der Figur sichtbar.
  Titel in Platypi, Farben wie `bwl.css`. `fit.py` hat Balkenbreite und Drehpunkt
  an `ros6_hi.png` angepasst (`best.npy`).
- **Endkarte** (`endcard.py`, 12 s): `Ende.png` wächst rosettenförmig aus der
  Mitte (`ros6_hi.png` mit 3D-Schattierung), dann SDF-Morphing zur vollen Karte.
- **Stimme**: `Sprechtext.txt` = gesprochene Sätze (Symbole ausgeschrieben).
  `hybrid.py`/`blend.py`: XTTS-v2, GPT-Latent gemischt aus dem deutschen
  Piper-Sprecher *Thorsten* (Sprachmelodie) und Adams Probe (Anteil `alpha`),
  Speaker-Embedding aus Adams entrauschter Probe. Mehrere Kandidaten pro Satz,
  Auswahl mit `check.py pick` (Whisper). `mix2.py` legt die Sätze ohne
  Beschleunigung auf die Untertitelzeiten.
- **Zusammenbau**: `build0302.sh` (Intro + Blasenvideo mit 1 s Überblendung,
  Endkarte, Ton nachbearbeitet: Entrauschen, Declick, Kompressor, loudnorm;
  `mksrt.py` erzeugt die verschobenen Untertitel). `SKIPBUB=1` überspringt das
  Rendern der Blasen.

## Version 3b (`v3b/`, v03_06 – v03_14)

Escher-Dreieck statt Penrose, Rosette mit 8 Armen (geflochten), neue Endkarte (Ente als Ellipse → Rechteck), Favicon. Details: `v3b/README.md`.
