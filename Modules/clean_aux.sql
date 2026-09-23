-- Leert die Hilfstabellen des BWL-Quiz (Sessions, Verlauf, Ereignisprotokoll).
-- Fragen/Antworten/Kapitel/Themen bleiben unberührt. Unumkehrbar!
--
-- Aufruf auf dem Server:
--   sudo -u postgres psql -d bwl -f /srv/wwwservers/www/tests/html/cgi-bin/teste/bwl/Modules/clean_aux.sql
-- oder von außen:
--   ssh superuser@mathe-c10-mua 'sudo -u postgres psql -d bwl -f /srv/wwwservers/www/tests/html/cgi-bin/teste/bwl/Modules/clean_aux.sql'

\set ON_ERROR_STOP 1

\echo 'Vorher:'
SELECT 'session_quiz' AS tabelle, count(*) FROM session_quiz
UNION ALL SELECT 'session_questions', count(*) FROM session_questions
UNION ALL SELECT 'sessions',          count(*) FROM sessions
UNION ALL SELECT 'geschichte',        count(*) FROM geschichte
UNION ALL SELECT 'geschichte_text',   count(*) FROM geschichte_text
UNION ALL SELECT 'geschichte_wahl',   count(*) FROM geschichte_wahl
UNION ALL SELECT 'event_log',         count(*) FROM event_log;

TRUNCATE session_quiz, session_questions, sessions,
         geschichte, geschichte_text, geschichte_wahl,
         event_log RESTART IDENTITY;

\echo 'Geleert. Fragen/Antworten:'
SELECT 'fragen' AS tabelle, count(*) FROM fragen
UNION ALL SELECT 'antworte', count(*) FROM antworte;
