# Datenbank-Snapshots der `bwl`-Datenbank

Backups des Quiz-Inhalts (PostgreSQL, DB `bwl`), damit der Dienst nach einem
Serverausfall auf einer anderen Maschine wiederherstellbar ist. Der Server
`mathe-c10-mua` ist eine kleine VM ohne separates DB-Backup.

## Dateien

- `bwl_content_<Datum>.sql` – **eigenständiger Inhalts-Dump**: Schema + Daten
  der Tabellen `fragen`, `antworte`, `kapitel`, `themen` **plus die beiden
  Views** `kapitel_themen` und `kapitel_themen_fragen`. Kein `--data-only`,
  also allein wiederherstellbar. Enthält KEINE Session-/Verlaufsdaten
  (`session_quiz`, `session_questions`, `geschichte*`, `sessions`) – dort
  stehen u. a. von Studierenden eingegebene Freitexte.
- `bwl_full_<Datum>.sql` – (nur in `~/bwl-db-backup/` auf dem Arbeitsrechner,
  bewusst NICHT im Repo) kompletter `pg_dump`: alle Tabellen inkl.
  Session-/Verlaufsdaten.

Snapshot-Stand siehe Dateiname; Zeilenzahlen zum jeweiligen Zeitpunkt:
`fragen` 117, `antworte` 117, `themen` 8, `kapitel` 7.

## Wiederherstellen auf einer frischen Maschine

```sh
createdb bwl

# Quiz-Inhalt (Tabellen fragen/antworte/kapitel/themen + Views):
psql -d bwl -f db/bwl_content_<Datum>.sql

# Session-/Verlaufstabellen (leer, aus dem Repo):
psql -d bwl -f Modules/schema.sql

# DB-Zugang: Modules/Common.pm ($DB / $user / $passwd),
# Verbindung in Modules/DB.pm (host 127.0.0.1:5432).
```

Für eine 1:1-Kopie inkl. bisheriger Auswertungen stattdessen den Full-Dump
einspielen: `psql -d bwl -f bwl_full_<Datum>.sql`.

## Neuen Snapshot ziehen

```sh
# Inhalt (kommt ins Repo):
ssh <server> 'sudo -u postgres pg_dump -d bwl --no-owner --no-privileges \
  -t fragen -t antworte -t kapitel -t themen \
  -t kapitel_themen -t kapitel_themen_fragen' > db/bwl_content_$(date +%F).sql

# Full-Dump (nicht ins Repo):
ssh <server> 'sudo -u postgres pg_dump -d bwl --no-owner --no-privileges' \
  > ~/bwl-db-backup/bwl_full_$(date +%F).sql
```
