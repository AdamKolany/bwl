#!/bin/bash
# Richtige Antworten der Aufgabenauswahl (DB bwl) als answers.tsv ins aktuelle Verzeichnis exportieren.
# Achtung: enthält Musterlösungen – nur im Arbeitsverzeichnis (z. B. ~/stackbwl), nie ins (öffentliche) Repo.
set -e
sudo -u postgres psql -d "${DB:-bwl}" -tA -F $'\t' -c "select f.frage_id, f.th_kürzel, a.antwort_latex, a.hint,
  replace(replace(f.frage, E'\n', ' '), E'\t', ' ') from fragen f join antworte a using(frage_id) where a.richtig = 'J' order by 1" > answers.tsv
wc -l answers.tsv
