#!/bin/bash
# Alle Formel-Aufgaben (genau eine Antwort, richtig, mit LaTeX) aus allen bwl-Datenbanken → all.tsv
# Spalten: db, frage_id, kapitel, thema, th_kürzel, antwort_latex, hint, frage
set -e
: > all.tsv
for d in ${DBS:-bwl abitur julia henning drak}; do
  H="''"; sudo -u postgres psql -d "$d" -tAc "select 1 from information_schema.columns where table_name='antworte' and column_name='hint'" | grep -q 1 && H="coalesce(a.hint, '')"
  sudo -u postgres psql -d "$d" -tA -F $'\t' >> all.tsv <<SQL
select '$d', f.frage_id, k.kapitel, t.thema, f.th_kürzel, a.antwort_latex, $H,
       replace(replace(f.frage, E'\n', ' '), E'\t', ' ')
from fragen f join antworte a using (frage_id)
left join themen t on t.th_kürzel = f.th_kürzel
left join kapitel k on k.kap_kürzel = t.kapitel
where a.richtig = 'J' and coalesce(a.antwort_latex, '') <> ''
  and f.frage_id in (select frage_id from antworte group by 1 having count(*) = 1)
order by f.frage_id;
SQL
done
wc -l all.tsv
