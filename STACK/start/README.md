# Startseite dispatch.cgi (main, `cgi-bin/teste/`)

Kopien der Dateien aus `/srv/wwwservers/www/main/html/cgi-bin/teste/` (dort nicht versioniert):

- `dispatch.cgi` – Auswahl Direct / Moodle / Ilias (blaue Links ohne Unterstreichung, Hover-Effekt).
- `run-moodle.cgi` → `/moodle/course/view.php?id=2` (Kurs bwl-STACK), `run-ilias.cgi` → `/ilias/goto.php?target=cat_87`
  (Kategorie bwl-STACK (Formeleditor)). `run-direct.cgi` ist dort ein Symlink auf `doit.cgi`.
- `apple-touch-icon.png` (180 px, Penrose-Dreieck auf Weiß) liegt im Wurzelverzeichnis von main
  (`/srv/wwwservers/www/main/html/`, zusätzlich als `apple-touch-icon-precomposed.png`): Safari holt diese Datei
  bevorzugt vor dem Favicon – ohne sie zeigte Safari weiter die alte Rosette aus dem Cache.
