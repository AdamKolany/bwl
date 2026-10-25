# ILIAS – Test auf mathe-c10-mua (Okt. 2026): **funktioniert**

Ergebnis: Dieselbe `bwl-stack.xml` (117 Aufgaben, verbindlicher Satz aus DB `bwl`) läuft in ILIAS 10 mit dem
STACK-Plugin genauso wie in Moodle: bwl-Tastatur im Fragetext, Eingabe landet als Maxima im STACK-Feld, Bewertung
durch Maxima (getestet: Ableitung, unbestimmtes Integral mit +C, Teilpunkte bei nicht ausmultipliziert).
Keine Änderung am gemeinsamen Teil nötig.

## Installation

- ILIAS 10.12 (`release_10`, git) in `/srv/wwwservers/ilias/ilias`, Webroot `public/`, URL `/ilias`
  (`apache-ilias.conf`), Daten `/srv/wwwservers/iliasdata`, Konfiguration `/srv/wwwservers/iliasconfig/ilias.json`
  (Vorlage ohne Passwörter: `ilias.json.vorlage`), Client `mathe`.
- MariaDB 10.11 (ILIAS kann kein PostgreSQL), klein eingestellt: `mariadb-90-ilias.cnf`.
- Node 22 nur für `npm clean-install` unter `/opt/node22` (System-Node 18 zu alt), dann `composer install --no-dev`,
  `php cli/setup.php build`, `php cli/setup.php install <config>`; MathJax 2 über `mathjax` im Config (`update`).
- Admin: wie Moodle (`mua`), Zugangsdaten in `/srv/wwwservers/moodle/ZUGANG.txt`.
- STACK-Plugin `surlabs/STACKForILIAS` (`release_10`, v10.3.8, STACK-Kern 4.5) in
  `public/Customizing/global/plugins/Modules/TestQuestionPool/Questions/assStackQuestion`; Installieren/Aktivieren
  in Administration › Plugins (die CLI registriert es nicht). Maxima lokal: Plattform `linux`, 5.46.

## Stolpersteine (lokale Maxima, ILIAS unter /ilias)

1. Healthcheck las `maximacommandserver` (nur bei Plattform „server“ gesetzt) → Fatal. Einzeiler in
   `classes/ui/admin/class.PluginConfigurationHealthcheckUI.php` (`?? maximacommand`, kommentiert).
2. `maximalocal.mac` sucht die STACK-Maxima-Bibliotheken unter `…/question/type/stack/stack/maxima` (Moodle-Layout).
   Lösung ohne Codeänderung: Symlink `assStackQuestion/question/type/stack/stack → ../../../classes/stack`.
3. Links auf die CORS-Skripte (stack_js) werden als `/Customizing/…` gebaut – ohne `/ilias`-Präfix. Lösung:
   Apache-Alias `/Customizing` → `public/Customizing` (in `apache-ilias.conf`). Danach verbindet sich das Relais.
4. Import: In einem Fragenpool eine STACK-Frage anlegen → „Import question from MoodleXML“; die Datei darf keine
   `category`-Einträge enthalten, die aktuelle Frage wird durch die erste der Datei ersetzt.
5. Fehlerprotokolle: `error_path` in `ilias.ini.php` war leer → `/srv/wwwservers/iliasdata/errors`.

6. Breite: Plugin-CSS `templates/css/styles.css` (wird nur auf Seiten mit STACK-Fragen geladen) um einen Block
   ergänzt: linke Hauptleiste aus, Innenränder der Frage klein (`ilias-wide.css`). Tests laufen zusätzlich in der
   Prüfungsansicht (Kiosk, ohne Menü).
7. Zufallstests: Pools müssen online sein (`object_data.offline = 0`), sonst bietet der Test sie nicht an; nach dem
   Anlegen der Regel „Synchronize Questions from Pool“, erst danach lässt sich der Test online schalten.

## Inhalt

- Kategorie „bwl-STACK (Formeleditor)“ (ref_id 87): 8 Fragenpools „Pool: <Thema>“ (je 15 bzw. 12 Fragen) und
  8 Tests „<Thema>“: je 5 Zufallsfragen aus dem Themenpool, online, Prüfungsansicht, sofortiges Feedback
  (Punkte, Rückmeldung, beste Lösung) per „Check“ – wie die Moodle-Tests.
- Zusätzlich der Gesamtpool „bwl-Aufgabenauswahl (STACK)“ (ref_id 86, 117 Fragen) im Wurzelverzeichnis.

## Anmeldung

- Sitzung 7 Tage: `[session] expire = "604800"` in `public/data/mathe/client.ini.php`, dazu `session.gc_maxlifetime = 604800` in `/etc/php/8.3/apache2/conf.d/91-ilias.ini`.
- Admin `mua` wie in Moodle.
- Erlaubte Hostnamen: ILIAS kennt nur den Host aus `http_path` (voller Name) und weist `http://mathe-c10-mua/…` mit
  „not in the allowed_hosts list“ ab. Zusätzlich eingetragen (Tabelle `settings`, `common/allowed_hosts`):
  `mathe-c10-mua,149.205.23.140,149.205.132.24,100.109.86.39`.
- Favicon: `public/assets/images/logo/favicon.ico` durch das Penrose-Dreieck (PTR1, 16–128 px) ersetzt, Original als
  `favicon.ico.ilias-orig`; nach einem ILIAS-Update (`build`/`npm`) prüfen.
  Damit Browser es neu laden: in `components/ILIAS/GlobalScreen/src/Scope/Layout/Provider/PagePart/StandardPagePartProvider.php`
  `getFaviconPath()` hängt `?v=ptr1-2` an (Einzeiler, kommentiert; Original `/srv/wwwservers/ilias/StandardPagePartProvider.php.orig`).
