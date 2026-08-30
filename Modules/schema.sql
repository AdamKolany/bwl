-- Hilfstabellen für das BWL-Quiz (Session- und Verlaufsdaten).
--
-- Einmalig pro Datenbank einspielen, z. B.:
--   psql -d bwl -f Modules/schema.sql
--
-- Früher stand dieses DDL in Modules/DB.pm und lief bei JEDEM CGI-Aufruf
-- (7 CREATE TABLE IF NOT EXISTS pro Request). Das ist reiner Overhead und
-- wurde hier herausgezogen.

CREATE TABLE IF NOT EXISTS session_quiz(
  sessionid   character(18) PRIMARY KEY,
  kapitel     character varying(5) NOT NULL,
  thema       character varying(5) NOT NULL,
  n_questions integer NOT NULL,
  last_seen   timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session_questions(
  sessionid  character(18) NOT NULL,
  nr         integer NOT NULL,
  frage_id   smallint NOT NULL,
  PRIMARY KEY(sessionid, nr)
);

CREATE TABLE IF NOT EXISTS geschichte_wahl(
  sessionid   character(18) NOT NULL,
  frage       smallint NOT NULL,
  antwort_ID  smallint NOT NULL
);

CREATE TABLE IF NOT EXISTS geschichte_text(
  sessionid     character(18) NOT NULL,
  frage         smallint NOT NULL,
  typ           character(1) NOT NULL, -- 'O' oder 'F'
  user_text     text,
  user_latex    text,
  user_mathjson jsonb,
  created_at    timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS geschichte(
  sessionid character(18),
  kapitel varchar(5),
  thema varchar(5),
  frage varchar(5),
  antwort varchar(5),
  richtig char(1)
);

CREATE TABLE IF NOT EXISTS sessions (sessionid character(18));
