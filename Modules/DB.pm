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
# Das DDL der Session-/Verlaufstabellen steht jetzt in Modules/schema.sql
# und wird einmalig pro Datenbank eingespielt:
#
#   psql -d bwl -f Modules/schema.sql
#
# Es lief früher hier bei jedem CGI-Aufruf (7x CREATE TABLE IF NOT EXISTS
# pro Request) - unnötiger Overhead auf einem kleinen Server.


1;
