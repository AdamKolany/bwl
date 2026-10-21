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
