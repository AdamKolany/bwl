package event_log;

# Nimmt das Ereignisprotokoll aus JS/eventLog.js entgegen (POST, JSON als
# text/plain) und schreibt es in die Tabelle event_log (DDL in
# Modules/schema.sql). Antwortet immer mit 204 — Fehler (z. B. Tabelle
# fehlt) werden geschluckt, die Seite soll davon nie etwas merken.

use strict;
use JSON::PP ();

my $MAX_BODY   = 256 * 1024;
my $MAX_EVENTS = 500;

sub run {
  eval { store(); 1; };
  print $Common::cgi->header(-status => '204 No Content', -Cache_Control => 'no-store');
  exit;
}

sub store {
  my $raw = $Common::cgi->param('POSTDATA') // '';
  return if $raw eq '' || length($raw) > $MAX_BODY;

  my $json = JSON::PP->new;
  $json->utf8 unless utf8::is_utf8($raw);
  my $in = $json->decode($raw);
  return unless ref $in eq 'HASH' && ref $in->{ev} eq 'ARRAY';

  my $out = JSON::PP->new->canonical;
  my $page_id = substr($in->{p} // '', 0, 24);
  my $action  = substr($in->{a} // '', 0, 12);
  my $nr      = (($in->{nr} // '') =~ /^(\d{1,4})$/) ? $1 : undef;

  my $ins = $DB::dbh->prepare(q{
    INSERT INTO event_log (sessionid, page_id, action, nr, seq, client_ts, typ, data)
    VALUES (?, ?, ?, ?, ?, to_timestamp(? / 1000.0), ?, ?::jsonb)
  });

  my @ev = @{ $in->{ev} };
  splice(@ev, $MAX_EVENTS) if @ev > $MAX_EVENTS;

  $DB::dbh->begin_work;
  for my $e (@ev) {
    next unless ref $e eq 'HASH';
    my $typ = substr($e->{y} // '', 0, 24); next if $typ eq '';
    my $seq = (($e->{s} // '') =~ /^(\d{1,9})$/) ? $1 : undef;
    my $ts  = (($e->{t} // '') =~ /^(\d{10,16})$/) ? $1 : undef;
    my $data = defined $e->{d} ? $out->encode($e->{d}) : undef;
    $ins->execute($Common::sid, $page_id, $action, $nr, $seq, $ts, $typ, $data);
  }
  $DB::dbh->commit;

  # Gelegentlich Altes wegräumen (Einträge älter als 90 Tage).
  $DB::dbh->do(q{DELETE FROM event_log WHERE server_ts < now() - interval '90 days'}) if rand() < 0.005;
}

1;
