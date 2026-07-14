package DB;

use DBI;


# ============================================================
# DB
# ============================================================

our $DSN  = "dbi:Pg:dbname=".($Common::DB).";host=127.0.0.1;port=5432";
our $USER = $Common::user;
our $PASS = $Common::passwd;

our $dbh =
    DBI->connect($DSN, $USER, $PASS,
       { RaiseError     => 1, PrintError     => 0, AutoCommit     => 1, pg_enable_utf8 => 1, });
eval { $dbh->do("SET client_encoding TO 'UTF8'"); 1; };

# ============================================================
# Hilfstabellen
# ============================================================
$dbh->do(q{
  CREATE TABLE IF NOT EXISTS session_quiz(
    sessionid   character(18) PRIMARY KEY,
    kapitel     character varying(5) NOT NULL,
    thema       character varying(5) NOT NULL,
    n_questions integer NOT NULL,
    last_seen   timestamp without time zone DEFAULT now()
  )
});
$dbh->do(q{
  CREATE TABLE IF NOT EXISTS session_questions(
    sessionid  character(18) NOT NULL,
    nr         integer NOT NULL,
    frage_id   smallint NOT NULL,
    PRIMARY KEY(sessionid, nr)
  )
});
$dbh->do(q{
  CREATE TABLE IF NOT EXISTS geschichte_wahl(
    sessionid   character(18) NOT NULL,
    frage       smallint NOT NULL,
    antwort_ID  smallint NOT NULL
  )
});
$dbh->do(q{
  CREATE TABLE IF NOT EXISTS geschichte_text(
    sessionid     character(18) NOT NULL,
    frage         smallint NOT NULL,
    typ           character(1) NOT NULL, -- 'O' oder 'F'
    user_text     text,
    user_latex    text,
    user_mathjson jsonb,
    created_at    timestamp without time zone DEFAULT now()
  )
});

$dbh->do(q{
  CREATE TABLE IF NOT EXISTS geschichte(
   sessionid character(18), 
   kapitel varchar(5), 
   thema varchar(5), 
   frage varchar(5), 
   antwort varchar(5), 
   richtig char(1)
  )
});

$dbh->do(q{ CREATE TABLE IF NOT EXISTS sessions (sessionid character(18)) });


1;
