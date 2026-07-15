# BWL Quiz

Perl-CGI-Quizmodul für das Fach BWL (Betriebswirtschaftslehre), Teil des
Mathe_C10-Werkstatt-Projekts (HS Merseburg).

## Funktionsweise

- `doit.cgi` steuert den Ablauf (Menü → Quizstart → Fragen → Auswertung),
  die Logik liegt in `Modules/*.pm`.
- Fragen werden nach Kapitel/Thema aus einer PostgreSQL-Datenbank (`bwl`)
  gezogen; die Anzahl der Fragen ist im Menü frei wählbar (begrenzt durch
  die Anzahl verfügbarer Fragen zum gewählten Thema).
- Unterstützte Fragetypen: Einzelauswahl, Mehrfachauswahl, Freitext und
  Formeleingabe (MathLive, ausgewertet über MathJSON).
- Mathematische Inhalte werden mit KaTeX/MathJax gerendert.

## Struktur

- `Modules/` – Perl-Module (DB-Zugriff, Menü, Fragenanzeige, Auswertung)
- `CSS/`, `JS/` – Styling und Frontend-Logik (inkl. KaTeX-Fonts)
- `showDB.cgi` – einfache Datenbank-/Themenübersicht
