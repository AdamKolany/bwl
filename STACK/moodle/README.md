# Moodle (mathe-c10-mua, /moodle)

Installiert 2026-10-23: Moodle 4.5 LTS (`/srv/wwwservers/moodle/moodle`, Daten `/srv/wwwservers/moodledata`, DB postgres `moodle`),
STACK 4.14 + adaptivemultipart, dfexplicitvaildate, dfcbmexplicitvaildate, qbank_importasversion; Maxima 5.46 (linux-optimised).
Zugangsdaten: `/srv/wwwservers/moodle/ZUGANG.txt` (nur superuser). Kurs „bwl-STACK“, Testkonto `stacktest`.

## Dateien

- `apache-moodle.conf` → `/etc/apache2/conf-available/moodle.conf` (Alias /moodle; CORS-Header für /js, /css, /stackbwl,
  weil die STACK-iframe den Ursprung "null" hat und Schriften/Skripte sonst nicht lädt)
- `theme-boost.scss` → Website-Administration › Darstellung › Boost › Raw SCSS
  (`php admin/cli/cfg.php --component=theme_boost --name=scss --set="$(cat theme-boost.scss)"`):
  Tests in voller Breite, Aufgabentext in TeX Gyre Bonum 1.5rem, Formeln 112 %
- `bwlimport.php [xml]` – Kurs anlegen, XML importieren, je Thema ein Test mit 3 Zufallsfragen (einmalig)
- `updq.php [xml]` – Fragetexte vorhandener Fragen aus neuer XML übernehmen (statt neu importieren)
- `delatt.php` – Testversuche von `stacktest` löschen

Alle PHP-Skripte: `sudo -u www-data php <skript> <pfad/zu/bwl-stack.xml>` (XML muss für www-data lesbar sein).
