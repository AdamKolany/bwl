# Moodle (mathe-c10-mua, /moodle)

Installiert 2026-10-23: Moodle 4.5 LTS (`/srv/wwwservers/moodle/moodle`, Daten `/srv/wwwservers/moodledata`, DB postgres `moodle`),
STACK 4.14 + adaptivemultipart, dfexplicitvaildate, dfcbmexplicitvaildate, qbank_importasversion; Maxima 5.46 (linux-optimised).
Zugangsdaten: `/srv/wwwservers/moodle/ZUGANG.txt` (nur superuser). Kurs „bwl-STACK“, Testkonto `stacktest`.

## Dateien

- `apache-moodle.conf` → `/etc/apache2/conf-available/moodle.conf` (Alias /moodle; CORS-Header für /js, /css, /stackbwl,
  weil die STACK-iframe den Ursprung "null" hat und Schriften/Skripte sonst nicht lädt)
- `theme-boost.scss` → Website-Administration › Darstellung › Boost › Raw SCSS
  (`php admin/cli/cfg.php --component=theme_boost --name=scss --set="$(cat theme-boost.scss)"`):
  Tests in voller Breite, Aufgabentext in TeX Gyre Bonum 1.5rem, Formeln 112 %; beim Lösen/in der Vorschau alles an den Seiten weg
  (Drawer, Fragen-Infokasten, Brotkrumen), damit der Editor auch auf dem iPad passt
- `kurs.php <kurzname> "<Name>" <xml> [lehrende] [teilnehmende]` – Kurs anlegen, XML importieren, Tests anlegen, einschreiben
- `tests.php <kurzname> [N]` – alle Tests eines Kurses neu: je Thema N Zufallsfragen (Standard 5; löscht Versuche)
- `bwlimport.php [xml]` – erste Version für den Kurs bwl-STACK (heute durch kurs.php ersetzt)
- `updq.php [xml]` – Fragetext, Musterlösung und Feedback vorhandener Fragen (per idnumber) aus neuer XML übernehmen
- `delatt.php` – Testversuche von `stacktest` löschen

Alle PHP-Skripte: `sudo -u www-data php <skript> <pfad/zu/bwl-stack.xml>` (XML muss für www-data lesbar sein).

Kurse: `bwl-STACK` (verbindlich, 117 Fragen, 8 Tests) und `bwl-STACK-alt` (Testmaterial, 268 Fragen, 22 Tests), je 5 Zufallsfragen pro Test.

## Ereignisprotokoll (bwl event_log) aus Moodle

Der Editor schreibt wie bwl in die Tabelle `event_log` der DB **bwl**, Seite `action = 'moodle'`.
Erstes Ereignis jeder Seite: `typ = 'moodle'` mit `q` (idnumber der Frage) und `ctx` = `q<usage>:<slot>_-quid_log`
(usage = Moodle-Frageverwendung des Versuchs). Dazu `stack.answer` (LaTeX → Maxima bzw. Fehler) und `stack.restore`.

    -- letzte Moodle-Seiten mit Frage und Kontext (DB bwl)
    select page_id, min(server_ts), max(data->>'q') q, max(data->>'ctx') ctx, count(*)
      from event_log where action = 'moodle' group by page_id order by 2 desc limit 20;
    -- alle Ereignisse einer Seite
    select client_ts::time(3), typ, data from event_log where page_id = '<page_id>' order by seq;
    -- Kontext → Benutzer (DB moodle): usage-Nummer aus ctx einsetzen
    select u.username, a.id attempt, a.quiz from mdl_quiz_attempts a join mdl_user u on u.id = a.userid where a.uniqueid = <usage>;

- `logo.php` – Rosette (6 Arme, hell) als Favicon, kompaktes Logo (Kopfzeile, 28 px) und Logo (Anmeldeseite, 90 px); Bilder vorher nach /tmp/rosette-6B-192.png und -512.png (aus Filme/_Quellen/favicon)
