-- Einmalig einspielen (als postgres):
--   sudo -u postgres psql -d bwl -f Modules/event_log.sql
CREATE TABLE IF NOT EXISTS event_log(
  id bigserial PRIMARY KEY, sessionid character(18), page_id varchar(24),
  action varchar(12), nr smallint, seq integer, client_ts timestamptz,
  server_ts timestamptz DEFAULT now(), typ varchar(24) NOT NULL, data jsonb);
CREATE INDEX IF NOT EXISTS event_log_sid_ts ON event_log (sessionid, client_ts);
CREATE INDEX IF NOT EXISTS event_log_server_ts ON event_log (server_ts);
GRANT SELECT, INSERT, DELETE ON event_log TO drak;
GRANT USAGE ON SEQUENCE event_log_id_seq TO drak;
